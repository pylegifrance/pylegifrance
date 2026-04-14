import json
import logging
import re
from datetime import date, datetime
from typing import Any, Optional

from pylegifrance.client import LegifranceClient
from pylegifrance.models.generated.model import (
    ChampDTO,
    CritereDTO,
    DatePeriod,
    FiltreDTO,
    Fond,
    Operateur,
    RechercheSpecifiqueDTO,
    SearchRequestDTO,
    TypeChamp,
    TypePagination,
    TypeRecherche,
)
from pylegifrance.models.identifier import Cid, Eli, Nor
from pylegifrance.models.juri.api_wrappers import (
    ConsultByAncienIdRequest,
    ConsultRequest,
    ConsultResponse,
)
from pylegifrance.models.juri.constants import FacettesJURI
from pylegifrance.models.juri.models import Decision
from pylegifrance.models.juri.search import SearchRequest
from pylegifrance.utils import EnumEncoder

HTTP_OK = 200
CITATION_TYPE = "CITATION"

# Canonical CASSATION_FORMATION filter values accepted by the Legifrance
# search endpoint for fond JURI. These are the French human-readable labels
# used natively by the API on the ``CASSATION_FORMATION`` facet (see
# ``description-des-tris-et-filtres-de-l-api.xlsx``, JURI sheet). The existing
# :class:`pylegifrance.models.juri.search.SearchRequest` documents and
# forwards these strings verbatim, so we stay consistent with that contract.
CASSATION_FORMATIONS: tuple[str, ...] = (
    "Chambre sociale",
    "Première chambre civile",
    "Deuxième chambre civile",
    "Troisième chambre civile",
    "Chambre commerciale",
    "Chambre criminelle",
    "Chambre mixte",
    "Assemblée plénière",
    "Chambres réunies",
)

# Convenience aliases mapping short codes (as used in prose citations such as
# "Cass. Soc." or "Cass. Civ. 1") to the canonical Legifrance labels above.
# Matching is case-insensitive on keys. Unknown keys are passed through
# unchanged so callers can always supply the canonical label directly.
CASSATION_FORMATION_ALIASES: dict[str, str] = {
    "soc": "Chambre sociale",
    "soci": "Chambre sociale",
    "social": "Chambre sociale",
    "civ1": "Première chambre civile",
    "civi1": "Première chambre civile",
    "civ2": "Deuxième chambre civile",
    "civi2": "Deuxième chambre civile",
    "civ3": "Troisième chambre civile",
    "civi3": "Troisième chambre civile",
    "com": "Chambre commerciale",
    "comm": "Chambre commerciale",
    "crim": "Chambre criminelle",
    "mixte": "Chambre mixte",
    "chmixte": "Chambre mixte",
    "pleniere": "Assemblée plénière",
    "plen": "Assemblée plénière",
    "ap": "Assemblée plénière",
}


def _normalize_formation(formation: str) -> str:
    """Resolve a formation alias (e.g. ``"Soc"``) to its canonical label.

    Args:
        formation: The user-supplied formation string. May be a short alias
            (``"Soc"``, ``"Civ1"``, ``"Com"``, ``"Crim"``...) or the canonical
            Legifrance label (``"Chambre sociale"``...).

    Returns:
        The canonical Legifrance label if the alias is known, otherwise the
        input unchanged (so callers can pass exotic formations directly).
    """
    key = formation.strip().lower().replace(" ", "").replace(".", "")
    return CASSATION_FORMATION_ALIASES.get(key, formation)


# Supported Legifrance case law identifier prefixes. JURITEXT is used for
# judicial decisions (Cour de cassation, cours d'appel, tribunaux judiciaires)
# and CETATEXT for administrative case law (Conseil d'Etat, tribunaux
# administratifs). Both resolve under the same /juri/id/ path on
# legifrance.gouv.fr.
JURI_URL_ID_PREFIXES: tuple[str, ...] = ("JURITEXT", "CETATEXT")
JURI_URL_TEMPLATE = "https://www.legifrance.gouv.fr/juri/id/{decision_id}"

# Canonical Legifrance case-law textId format. A valid JURITEXT or CETATEXT
# identifier is the literal prefix followed by exactly 12 numeric digits
# (for example ``JURITEXT000037999394``). This regex is used by
# :meth:`JuriAPI.fetch_by_id` to reject obviously malformed identifiers
# client-side so callers receive a precise :class:`ValueError` before any
# network round-trip.
JURI_TEXT_ID_PATTERN: re.Pattern[str] = re.compile(r"^(?:JURITEXT|CETATEXT)\d{12}$")

# Marker substring used to recognise the distinctive HTTP 400 response that
# Legifrance's ``/consult/juri`` endpoint returns when asked about a
# well-formed textId that does not resolve to an existing decision. Probed
# against the live API on 2026-04-13: both all-zero and all-nine JURITEXT ids
# (e.g. ``JURITEXT000000000000``, ``JURITEXT999999999999``) trigger this
# exact message, while valid ids (e.g. ``JURITEXT000037999394``) return 200
# with a populated ``text`` payload. The endpoint does NOT return 200 with
# an empty text for unknown ids — it returns 400, so we have to interpret
# this specific error as "decision does not exist" rather than as a real
# transport failure.
_UNKNOWN_TEXT_ID_MARKER: str = "L'expression à valider est fausse"

logger = logging.getLogger(__name__)


class JuriDecision:
    """
    Objet de domaine de haut niveau représentant une décision de justice.

    Cette classe encapsule le modèle Decision et fournit des comportements riches comme
    .latest(), .citations(), .versions(), et .at(date).
    """

    def __init__(self, decision: Decision, client: LegifranceClient):
        """Initialise une instance de JuriDecision.

        Args:
            decision: Le modèle Decision sous-jacent.
            client: Le client pour interagir avec l'API Legifrance.
        """
        self._decision = decision
        self._client = client

    @property
    def id(self) -> str | None:
        """Récupère l'identifiant de la décision."""
        return self._decision.id

    @property
    def url(self) -> str | None:
        """Construit l'URL Legifrance officielle de la décision.

        L'URL est dérivée de l'identifiant de la décision en suivant le
        schéma canonique ``https://www.legifrance.gouv.fr/juri/id/{id}``.
        Ce même chemin résout les décisions judiciaires (``JURITEXT...``)
        et les décisions administratives (``CETATEXT...``).

        Reflète le comportement d'auto-génération d'URL déjà présent sur
        :class:`pylegifrance.models.code.models.Article`, afin que les
        consommateurs (notamment les agents LLM) disposent toujours d'une
        URL vérifiable et puissent distinguer les citations authentiques
        des fabrications.

        Returns:
            L'URL canonique de consultation sur legifrance.gouv.fr, ou
            ``None`` si l'identifiant est manquant ou ne correspond pas à
            un préfixe reconnu (JURITEXT ou CETATEXT). Retourne ``None``
            plutôt qu'une URL malformée afin de ne pas induire les
            consommateurs en erreur.

        Examples:
            >>> decision.url
            'https://www.legifrance.gouv.fr/juri/id/JURITEXT000027546700'
        """
        decision_id = self._decision.id
        if not decision_id:
            return None
        if not decision_id.startswith(JURI_URL_ID_PREFIXES):
            return None
        return JURI_URL_TEMPLATE.format(decision_id=decision_id)

    @property
    def cid(self) -> Cid | None:
        """Récupère le CID de la décision avec validation."""
        if not hasattr(self._decision, "cid") or not self._decision.cid:
            return None
        return Cid(self._decision.cid)

    @property
    def eli(self) -> Eli | None:
        """Récupère l'ELI de la décision avec validation."""
        if not self._decision.id_eli:
            return None
        return Eli(self._decision.id_eli)

    @property
    def nor(self) -> Nor | None:
        """Récupère le NOR de la décision avec validation."""
        if not self._decision.nor:
            return None
        return Nor(self._decision.nor)

    @property
    def ecli(self) -> str | None:
        """Récupère l'ECLI de la décision."""
        return getattr(self._decision, "ecli", None)

    @property
    def date(self) -> datetime | None:
        """Récupère la date de la décision."""
        if not self._decision.date_texte:
            return None

        try:
            # Gère à la fois les types chaîne et datetime
            if isinstance(self._decision.date_texte, str):
                return datetime.fromisoformat(self._decision.date_texte)
            elif isinstance(self._decision.date_texte, datetime):
                return self._decision.date_texte
        except (ValueError, TypeError):
            # Gère le cas où dateTexte n'est pas un format ISO valide
            return None
        return None

    @property
    def title(self) -> str | None:
        """Récupère le titre de la décision."""
        return self._decision.titre

    @property
    def long_title(self) -> str | None:
        """Récupère le titre long de la décision."""
        return self._decision.titre_long

    @property
    def text(self) -> str | None:
        """Récupère le texte de la décision."""
        return self._decision.texte

    @property
    def text_html(self) -> str | None:
        """Récupère le texte HTML de la décision."""
        return self._decision.texte_html

    @property
    def formation(self) -> str | None:
        """Récupère la formation de la décision."""
        return self._decision.formation

    @property
    def numero(self) -> str | None:
        """Récupère le numéro de la décision."""
        return getattr(self._decision, "num", None)

    @property
    def jurisdiction(self) -> str | None:
        """Récupère la juridiction de la décision."""
        return getattr(self._decision, "juridiction", None)

    @property
    def solution(self) -> str | None:
        """Récupère la solution de la décision."""
        return getattr(self._decision, "solution", None)

    def citations(self) -> list["JuriDecision"]:
        """Récupère les citations de la décision.

        Returns:
            Une liste d'objets JuriDecision représentant les citations.
        """
        citations = []
        for lien in self._decision.liens:
            if lien.type_lien != CITATION_TYPE:
                continue
            if not lien.cid_texte or lien.cid_texte == "":
                continue

            try:
                decision = JuriAPI(self._client).fetch(lien.cid_texte)
                if decision:
                    citations.append(decision)
            except Exception:
                # Skip citations that can't be fetched
                # We use a generic exception here because we want to continue processing
                # other citations even if one fails for any reason
                pass
        return citations

    def at(self, date: datetime | str) -> Optional["JuriDecision"]:
        """Récupère la version de la décision à la date spécifiée.

        Args:
            date: La date à laquelle récupérer la version.

        Returns:
            La version de la décision à la date spécifiée, ou None si non trouvée.
        """
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date)
            except ValueError:
                raise ValueError(f"Format de date invalide: {date}") from None

        # Convert date to ISO format string for the API
        date_str = date.isoformat()

        # Use the JuriAPI to fetch the version at the specified date
        try:
            if self.id is None:
                return None
            return JuriAPI(self._client).fetch_version_at(self.id, date_str)
        except Exception:
            return None

    def latest(self) -> Optional["JuriDecision"]:
        """Récupère la dernière version de la décision.

        Returns:
            La dernière version de la décision, ou None si non trouvée.
        """
        if self.id is None:
            return None

        try:
            return JuriAPI(self._client).fetch(self.id)
        except Exception:
            return None

    def versions(self) -> list["JuriDecision"]:
        """Récupère toutes les versions de la décision.

        Returns:
            Une liste d'objets JuriDecision représentant toutes les versions.
        """
        if self.id is None:
            return []

        try:
            return JuriAPI(self._client).fetch_versions(self.id)
        except Exception:
            return []

    def to_dict(self) -> dict[str, Any]:
        """Convertit la décision en dictionnaire.

        Returns:
            Une représentation sous forme de dictionnaire de la décision.
        """
        return self._decision.model_dump()

    def __repr__(self) -> str:
        """Récupère une représentation sous forme de chaîne de la décision."""
        return f"JuriDecision(id={self.id}, date={self.date}, title={self.title})"


class JuriAPI:
    """
    API de haut niveau pour interagir avec les données JURI de l'API Legifrance.
    """

    def __init__(self, client: LegifranceClient):
        """Initialise une instance de JuriAPI.

        Args:
            client: Le client pour interagir avec l'API Legifrance.
        """
        self._client = client

    def _process_consult_response(
        self, response_data: ConsultResponse
    ) -> Decision | None:
        """Traite une réponse de consultation et extrait la Décision.

        Args:
            response_data: Les données de réponse JSON de l'API.

        Returns:
            L'objet Decision, ou None si non trouvé.
        """
        consult_response = ConsultResponse.from_api_model(response_data)

        if not consult_response.text:
            return None

        # Fix: Use the text data directly since it's already a dict
        if isinstance(consult_response.text, dict):
            decision_data = consult_response.text
        else:
            decision_data = consult_response.text.model_dump()

        return Decision.model_validate(decision_data)

    def fetch(self, text_id: str) -> JuriDecision | None:
        """Récupère une décision par son identifiant.

        Args:
            text_id: L'identifiant de la décision à récupérer.

        Returns:
            La décision, ou None si non trouvée.

        Raises:
            ValueError: Si l'identifiant du texte est invalide.
            Exception: Si l'appel à l'API échoue.
        """
        if not text_id:
            raise ValueError("L'identifiant du texte ne peut pas être vide")

        request = ConsultRequest(textId=text_id, searchedString="")

        response = self._client.call_api(
            "consult/juri", request.to_api_model().model_dump(by_alias=True)
        )

        if response.status_code != HTTP_OK:
            return None

        response_data = response.json()
        decision = self._process_consult_response(response_data)

        if not decision:
            return None

        return JuriDecision(decision, self._client)

    def fetch_with_ancien_id(self, ancien_id: str) -> JuriDecision | None:
        """Récupère une décision par son ancien identifiant.

        Args:
            ancien_id: L'ancien identifiant de la décision à récupérer.

        Returns:
            La décision, ou None si non trouvée.
        """
        if not ancien_id:
            raise ValueError("L'ancien identifiant ne peut pas être vide")

        request = ConsultByAncienIdRequest(ancienId=ancien_id)

        response = self._client.call_api(
            "consult/juri/ancienId",
            request.to_api_model().model_dump(by_alias=True),
        )

        if response.status_code != HTTP_OK:
            return None

        response_data = response.json()
        decision = self._process_consult_response(response_data)

        if not decision:
            return None

        return JuriDecision(decision, self._client)

    def fetch_version_at(self, text_id: str, date: str) -> JuriDecision | None:
        """Récupère la version d'une décision à une date spécifique.

        Args:
            text_id: L'identifiant de la décision à récupérer.
            date: La date à laquelle récupérer la version, au format ISO.

        Returns:
            La version de la décision à la date spécifiée, ou None si non trouvée.
        """
        if not text_id:
            raise ValueError("L'identifiant du texte ne peut pas être vide")

        try:
            datetime.fromisoformat(date)
        except ValueError:
            raise ValueError(f"Format de date invalide: {date}") from None

        request = {"textId": text_id, "date": date}
        response = self._client.call_api("consult/juri/version", request)

        if response.status_code != HTTP_OK:
            return None

        response_data = response.json()
        decision = self._process_consult_response(response_data)

        if not decision:
            return None

        return JuriDecision(decision, self._client)

    def fetch_versions(self, text_id: str) -> list[JuriDecision]:
        """Récupère toutes les versions d'une décision.

        Args:
            text_id: L'identifiant de la décision dont on veut récupérer les versions.

        Returns:
            Une liste d'objets JuriDecision représentant toutes les versions.
        """
        if not text_id:
            raise ValueError("L'identifiant du texte ne peut pas être vide")

        request = {"textId": text_id}
        response = self._client.call_api("consult/juri/versions", request)

        if response.status_code != HTTP_OK:
            return []

        response_data = response.json()

        if not isinstance(response_data, list):
            return []

        versions = []
        for version_data in response_data:
            decision = self._process_consult_response(version_data)
            if decision:
                versions.append(JuriDecision(decision, self._client))

        return versions

    def search(self, query: str | SearchRequest) -> list[JuriDecision]:
        """Recherche des décisions correspondant à la requête.

        Args:
            query: La requête de recherche, soit sous forme de chaîne, soit sous forme d'objet SearchRequest.

        Returns:
            Une liste d'objets JuriDecision correspondant à la requête.
        """
        if isinstance(query, str):
            search_query = SearchRequest(search=query)
        else:
            search_query = query

        request_dto = search_query.to_api_model()

        request = request_dto.model_dump(by_alias=True)
        request = json.loads(json.dumps(request, cls=EnumEncoder))

        response = self._client.call_api("search", request)

        if response.status_code != HTTP_OK:
            return []

        response_data = response.json()

        if "results" not in response_data or not isinstance(
            response_data["results"], list
        ):
            return []

        results = []
        for result in response_data["results"]:
            if (
                "titles" not in result
                or not isinstance(result["titles"], list)
                or len(result["titles"]) == 0
            ):
                continue

            title = result["titles"][0]

            if "id" not in title:
                continue

            text_id = title["id"]

            try:
                decision = self.fetch(text_id)
                if decision:
                    results.append(decision)
                    logger.debug(f"Décision {text_id} récupérée et ajoutée avec succès")
                else:
                    logger.warning(
                        f"Échec de récupération de la décision {text_id} (a retourné None)"
                    )
            except Exception as e:
                logger.error(
                    f"Exception lors de la récupération de la décision {text_id}: {e}"
                )

        return results

    def fetch_by_id(self, text_id: str) -> JuriDecision | None:
        """Verify and fetch a decision by its canonical Legifrance identifier.

        Wraps ``POST /consult/juri`` with body ``{"textId": text_id}``. This
        is the canonical verifier for "does this decision actually exist on
        Legifrance?" — the primary use case is hardening LLM agents that
        fabricate case-law citations with plausible-looking but invented
        JURITEXT/CETATEXT identifiers.

        Unlike :meth:`fetch`, this method is documented as a verification
        primitive. The resolution order is:

        1. Validate the identifier format client-side against
           :data:`JURI_TEXT_ID_PATTERN` (``^(JURITEXT|CETATEXT)\\d{12}$``).
           Malformed inputs raise :class:`ValueError` with no network
           round-trip.
        2. Call ``POST /consult/juri``. A populated 200 response is wrapped
           in a :class:`JuriDecision`.
        3. The Legifrance ``/consult/juri`` endpoint does NOT return an
           empty 200 response for unknown well-formed ids — it answers HTTP
           400 with the body ``"L'expression à valider est fausse"``
           (probed live on 2026-04-13 against ``JURITEXT000000000000``,
           ``JURITEXT999999999999``, and ``JURITEXT000037999394``). When we
           observe that exact signature AFTER passing client-side format
           validation, we interpret it as "decision does not exist" and
           return ``None``. Every other error (transport, auth, other 4xx,
           5xx) propagates so callers can distinguish "decision does not
           exist" from "we could not check".

        Args:
            text_id: The Legifrance text identifier (e.g.
                ``"JURITEXT000037999394"`` for a Cour de cassation decision
                or ``"CETATEXT000007422435"`` for a Conseil d'État decision).
                Must match ``^(JURITEXT|CETATEXT)\\d{12}$``.

        Returns:
            A :class:`JuriDecision` if Legifrance returns a populated text
            for the given identifier, ``None`` if the identifier is well
            formed but does not resolve to any decision on Legifrance.

        Raises:
            ValueError: If ``text_id`` is empty, only whitespace, or does
                not match the canonical ``JURITEXT``/``CETATEXT`` format.
            Exception: If the HTTP call fails for any reason other than the
                recognised "unknown textId" 400 signature (transport, auth,
                other 4xx, 5xx). The caller MUST treat these as
                "verification impossible", not as "decision does not exist".

        Examples:
            >>> juri = JuriAPI(client)
            >>> decision = juri.fetch_by_id("JURITEXT000037999394")
            >>> if decision is None:
            ...     raise ValueError("Decision does not exist on Legifrance")
        """
        if not text_id or not text_id.strip():
            raise ValueError("L'identifiant du texte ne peut pas être vide")

        normalized = text_id.strip()
        if not JURI_TEXT_ID_PATTERN.match(normalized):
            raise ValueError(
                "Invalid text_id format: expected JURITEXT<12 digits> or "
                f"CETATEXT<12 digits>, got {text_id!r}"
            )

        request = ConsultRequest(textId=normalized, searchedString=None)

        # Match the DILA API cookbook example for POST /consult/juri which
        # sends only ``{"textId": ...}``. Excluding None keeps the body
        # minimal and avoids transmitting a dangling ``"searchedString":
        # null`` that is not part of the documented contract.
        try:
            response = self._client.call_api(
                "consult/juri",
                request.to_api_model().model_dump(by_alias=True, exclude_none=True),
            )
        except Exception as exc:
            # LegifranceClient wraps 4xx/5xx responses into plain
            # ``Exception("API client error <code> - <body>")``. We only
            # translate the very specific "unknown textId" 400 signature
            # into ``None``; every other failure propagates so the caller
            # can distinguish "not found" from "could not verify".
            message = str(exc)
            if "400" in message and _UNKNOWN_TEXT_ID_MARKER in message:
                logger.debug(
                    "fetch_by_id: Legifrance reported unknown textId %s "
                    "(HTTP 400 'L'expression à valider est fausse'); "
                    "returning None.",
                    normalized,
                )
                return None
            raise

        if response.status_code != HTTP_OK:
            return None

        response_data = response.json()
        decision = self._process_consult_response(response_data)

        if decision is None:
            return None

        return JuriDecision(decision, self._client)

    def search_by_ecli(self, ecli: str, *, fond: str = "JURI") -> list[JuriDecision]:
        """Resolve a European Case Law Identifier (ECLI) to Legifrance decisions.

        Wraps ``POST /search`` with a field search on ``typeChamp=ECLI``
        using ``typeRecherche=EXACTE``. An ECLI typically resolves to zero
        or one match, but a list is returned for API consistency with
        :meth:`search`.

        Args:
            ecli: The European Case Law Identifier. Any documented format is
                accepted (for example ``"ECLI:FR:CCASS:2018:CO00579"``,
                ``"ECLI:FR:CC:2023:123.QPC"``, or
                ``"ECLI:FR:CE:2024:123456.20240101"``). Only a non-empty
                check is performed locally; format validation is delegated
                to the Legifrance API.
            fond: The Legifrance fond to search. Defaults to ``"JURI"``
                (judicial case law — Cour de cassation, cours d'appel,
                tribunaux judiciaires). Use ``"CETAT"`` to search the
                administrative case law corpus (Conseil d'État) instead.

        Returns:
            A list of matching :class:`JuriDecision` objects. Empty list if
            no decision matches the ECLI on the given fond.

        Raises:
            ValueError: If ``ecli`` is empty or ``fond`` is not one of
                ``"JURI"`` or ``"CETAT"``.
            Exception: If the HTTP call fails (transport, auth, 4xx, 5xx).

        Examples:
            >>> matches = juri.search_by_ecli("ECLI:FR:CCASS:2018:CO00579")
            >>> if not matches:
            ...     raise ValueError("ECLI does not resolve on Legifrance")
        """
        if not ecli or not ecli.strip():
            raise ValueError("L'ECLI ne peut pas être vide")

        fond_normalized = fond.strip().upper()
        if fond_normalized == "JURI":
            fond_dto = Fond.juri
        elif fond_normalized == "CETAT":
            fond_dto = Fond.cetat
        else:
            raise ValueError(
                f"Fond non supporté pour une recherche par ECLI: {fond}. "
                "Valeurs acceptées: 'JURI', 'CETAT'."
            )

        request_dto = self._build_field_search_dto(
            value=ecli,
            type_champ=TypeChamp.ecli,
            fond=fond_dto,
        )

        return self._run_search_dto(request_dto)

    def search_by_affaire(
        self,
        num_affaire: str,
        *,
        formation: str | None = None,
        date_decision: date | None = None,
        date_range: tuple[date, date] | None = None,
    ) -> list[JuriDecision]:
        """Exact-tuple lookup for Cassation-style case citations.

        Wraps ``POST /search`` on fond ``JURI`` combining:

        - a field search on ``typeChamp=NUM_AFFAIRE`` (``typeRecherche=EXACTE``),
        - an optional ``CASSATION_FORMATION`` filter,
        - an optional ``DATE_DECISION`` filter (either an exact day or an
          inclusive date range).

        This is designed to verify canonical French case citations of the
        form ``Cass. Soc. 4 mars 2020 n° 18-26.218``: the caller supplies
        the formation, the date, and the case number, and this method
        returns the matching JURITEXT — or an empty list if no decision
        matches the tuple exactly.

        Args:
            num_affaire: The case number (``"18-26.218"``,
                ``"20-80.000"``...). Exact match is used.
            formation: Optional Cassation formation. Accepts either a short
                alias (``"Soc"``, ``"Civ1"``, ``"Civ2"``, ``"Civ3"``,
                ``"Com"``, ``"Crim"``, ``"Mixte"``, ``"Pleniere"``) or the
                canonical Legifrance label (``"Chambre sociale"``,
                ``"Première chambre civile"``...). Aliases are resolved via
                :data:`CASSATION_FORMATION_ALIASES`; unknown strings are
                forwarded to the API unchanged.
            date_decision: Optional exact decision date. Mutually exclusive
                with ``date_range``.
            date_range: Optional ``(start, end)`` inclusive date range for
                the decision date. Mutually exclusive with ``date_decision``.

        Returns:
            A list of matching :class:`JuriDecision` objects. Empty list if
            no decision matches the tuple.

        Raises:
            ValueError: If ``num_affaire`` is empty, if both
                ``date_decision`` and ``date_range`` are provided, or if
                ``date_range`` is not a 2-tuple with start <= end.
            Exception: If the HTTP call fails.

        Examples:
            >>> from datetime import date
            >>> juri.search_by_affaire(
            ...     num_affaire="18-26.218",
            ...     formation="Soc",
            ...     date_decision=date(2020, 3, 4),
            ... )
        """
        if not num_affaire or not num_affaire.strip():
            raise ValueError("Le numéro d'affaire ne peut pas être vide")

        if date_decision is not None and date_range is not None:
            raise ValueError(
                "Paramètres incompatibles: utilisez soit 'date_decision', "
                "soit 'date_range', mais pas les deux."
            )

        filters: list[FiltreDTO] = []

        if formation is not None:
            canonical_formation = _normalize_formation(formation)
            filters.append(
                FiltreDTO(
                    facette=FacettesJURI.CASSATION_FORMATION.value,
                    valeurs=[canonical_formation],
                    dates=None,
                    singleDate=None,
                    multiValeurs=None,
                )
            )

        if date_decision is not None:
            start = datetime.combine(date_decision, datetime.min.time())
            end = datetime.combine(date_decision, datetime.min.time())
            filters.append(
                FiltreDTO(
                    facette="DATE_DECISION",
                    valeurs=None,
                    dates=DatePeriod(start=start, end=end),
                    singleDate=None,
                    multiValeurs=None,
                )
            )
        elif date_range is not None:
            if len(date_range) != 2:
                raise ValueError("date_range doit être un tuple (start_date, end_date)")
            start_date, end_date = date_range
            if end_date < start_date:
                raise ValueError(
                    "date_range: la date de fin doit être >= date de début"
                )
            filters.append(
                FiltreDTO(
                    facette="DATE_DECISION",
                    valeurs=None,
                    dates=DatePeriod(
                        start=datetime.combine(start_date, datetime.min.time()),
                        end=datetime.combine(end_date, datetime.min.time()),
                    ),
                    singleDate=None,
                    multiValeurs=None,
                )
            )

        request_dto = self._build_field_search_dto(
            value=num_affaire,
            type_champ=TypeChamp.num_affaire,
            fond=Fond.juri,
            filters=filters,
        )

        return self._run_search_dto(request_dto)

    def _build_field_search_dto(
        self,
        *,
        value: str,
        type_champ: TypeChamp,
        fond: Fond,
        filters: list[FiltreDTO] | None = None,
    ) -> SearchRequestDTO:
        """Build a :class:`SearchRequestDTO` for a single exact field search.

        Mirrors the helpers on
        :class:`pylegifrance.models.juri.search.SearchRequest` but operates
        directly on DTOs so we can target fonds other than JURI and field
        types (ECLI, NUM_AFFAIRE...) that the higher-level ``SearchRequest``
        wrapper does not currently expose.
        """
        criteria = CritereDTO(
            valeur=value,
            operateur=Operateur.et,
            typeRecherche=TypeRecherche.exacte,
            proximite=None,
            criteres=None,
        )
        champ = ChampDTO(
            criteres=[criteria],
            operateur=Operateur.et,
            typeChamp=type_champ,
        )
        recherche = RechercheSpecifiqueDTO(
            champs=[champ],
            filtres=filters or [],
            pageNumber=1,
            pageSize=10,
            sort="PERTINENCE",
            fromAdvancedRecherche=False,
            secondSort="ID",
            typePagination=TypePagination.defaut,
            operateur=Operateur.et,
        )
        return SearchRequestDTO(recherche=recherche, fond=fond)

    def _run_search_dto(self, request_dto: SearchRequestDTO) -> list[JuriDecision]:
        """Execute a prepared search DTO and hydrate matches into JuriDecisions.

        Mirrors the post-processing loop of :meth:`search`: walks the
        ``results[].titles[0].id`` path and calls :meth:`fetch` for each
        hit so callers uniformly receive rich :class:`JuriDecision`
        instances. Matches the behaviour of :meth:`search` for parity.
        """
        request = request_dto.model_dump(by_alias=True)
        request = json.loads(json.dumps(request, cls=EnumEncoder))

        response = self._client.call_api("search", request)

        if response.status_code != HTTP_OK:
            return []

        response_data = response.json()

        if "results" not in response_data or not isinstance(
            response_data["results"], list
        ):
            return []

        results: list[JuriDecision] = []
        for result in response_data["results"]:
            if (
                "titles" not in result
                or not isinstance(result["titles"], list)
                or len(result["titles"]) == 0
            ):
                continue

            title = result["titles"][0]
            if "id" not in title:
                continue

            text_id = title["id"]
            try:
                decision = self.fetch(text_id)
                if decision is not None:
                    results.append(decision)
            except Exception as exc:
                logger.error(
                    f"Exception lors de la récupération de la décision {text_id}: {exc}"
                )

        return results
