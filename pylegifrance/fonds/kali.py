"""Façade KALI — conventions collectives nationales.

Le fond KALI regroupe les conventions collectives étendues et leurs
accords. Les objets sont organisés en deux niveaux :

- le **conteneur** (``KALICONT...``) qui représente une convention
  collective au sens large, identifiée par un numéro IDCC ;
- les **textes** (``KALITEXT...``) — texte de base, avenants, accords —
  qui sont les unités réellement consultables, avec sections et
  articles.

Cette façade expose un :class:`KaliAPI` mince (inspiré de
:class:`pylegifrance.fonds.juri.JuriAPI`) et deux wrappers de domaine,
:class:`ConventionCollective` et :class:`TexteKali`. KALI n'exposant pas
d'endpoint ``versions`` / ``version/at``, aucun équivalent à
``.at(date)`` ou ``.versions()`` n'est fourni.

Endpoints de consultation couverts (voir
``docs/raw/legifrance/description-des-tris-et-filtres-de-l-api.md``
section *Présentation du Consult*) :

- ``POST /consult/kaliCont`` — conteneur par identifiant ``KALICONT``.
- ``POST /consult/kaliContIdcc`` — conteneur par numéro IDCC.
- ``POST /consult/kaliText`` — texte par identifiant ``KALITEXT``.
- ``POST /consult/kaliSection`` — texte parent d'une section.
- ``POST /consult/kaliArticle`` — texte parent d'un article.
"""

import json
import logging
import re
from typing import Any

from pylegifrance.client import LegifranceClient
from pylegifrance.models.generated.model import (
    ConsultKaliContResponse,
    ConsultKaliTextResponse,
    KaliContConsultIdccRequest,
    KaliContConsultRequest,
    KaliTextConsultArticleRequest,
    KaliTextConsultRequest,
    KaliTextConsultSectionRequest,
)
from pylegifrance.models.kali.search import SearchRequest
from pylegifrance.utils import EnumEncoder

HTTP_OK = 200

KALI_CONT_PREFIX = "KALICONT"
KALI_TEXT_PREFIX = "KALITEXT"
KALI_ARTI_PREFIX = "KALIARTI"
KALI_SCTA_PREFIX = "KALISCTA"
KALI_PREFIXES: tuple[str, ...] = (
    KALI_CONT_PREFIX,
    KALI_TEXT_PREFIX,
    KALI_ARTI_PREFIX,
    KALI_SCTA_PREFIX,
)

_IDCC_PATTERN: re.Pattern[str] = re.compile(r"^\d{1,5}$")

logger = logging.getLogger(__name__)


class ConventionCollective:
    """Conteneur d'une convention collective (niveau IDCC)."""

    def __init__(self, data: ConsultKaliContResponse, client: LegifranceClient):
        self._data = data
        self._client = client

    @property
    def id(self) -> str | None:
        """Identifiant ``KALICONT...`` du conteneur."""
        return self._data.id

    @property
    def titre(self) -> str | None:
        return self._data.titre

    @property
    def idcc(self) -> str | None:
        """Numéro IDCC (ex: ``"1261"``), si présent dans la réponse."""
        return self._data.num

    @property
    def nature(self) -> str | None:
        return self._data.nature

    @property
    def numero_texte(self) -> str | None:
        """Libellé ``"IDCC <n>"`` utilisé par la DILA."""
        return self._data.numero_texte

    @property
    def activites_pro(self) -> list[str] | None:
        return self._data.activite_pro

    @property
    def categorisation(self) -> list[str] | None:
        return self._data.categorisation

    @property
    def texte_base_ids(self) -> list[str] | None:
        """Identifiants ``KALITEXT...`` des textes de base associés."""
        return self._data.texte_base_id

    @property
    def sections(self) -> list:
        return self._data.sections or []

    def to_dict(self) -> dict[str, Any]:
        return self._data.model_dump(by_alias=True)

    def to_markdown(self) -> str:
        parts: list[str] = [
            f"## {self.titre or self.id or 'Convention collective'}",
            "",
        ]
        if self.idcc:
            parts.append(f"**IDCC**: {self.idcc}")
        if self.numero_texte:
            parts.append(f"**Numéro**: {self.numero_texte}")
        if self.nature:
            parts.append(f"**Nature**: {self.nature}")
        if self.activites_pro:
            parts.append(f"**Activités**: {', '.join(self.activites_pro)}")
        if self.id:
            parts.append(f"**Référence**: {self.id}")
        return "\n".join(parts)

    def __repr__(self) -> str:
        return (
            f"ConventionCollective(id={self.id}, idcc={self.idcc}, titre={self.titre})"
        )


class TexteKali:
    """Texte individuel du fond KALI (texte de base, avenant, accord)."""

    def __init__(self, data: ConsultKaliTextResponse, client: LegifranceClient):
        self._data = data
        self._client = client

    @property
    def container_id(self) -> str | None:
        """Identifiant ``KALICONT`` du conteneur parent, si disponible.

        Priorité de lecture :

        1. ``id_conteneur`` (``idConteneur`` côté API) — présent pour
           les textes de base (``typeTexte = "TEXTE_BASE"``).
        2. ``conteneurs[0].cid`` — présent pour les textes dérivés
           (avenants, accords). Les avenants retournés par
           ``/consult/kaliText`` n'ont pas d'``idConteneur`` au niveau
           racine mais listent leurs conventions parentes dans
           ``conteneurs`` ; le champ ``cid`` de chaque entrée est
           l'identifiant ``KALICONT`` canonique.

        Sans ce fallback, ``KaliAPI.search`` (qui navigue texte →
        conteneur) dropperait tous les avenants retournés par
        ``/search``, ce qui correspond au cas commun des recherches
        par secteur puisque la majorité des hits sont des avenants.
        """
        if self._data.id_conteneur:
            return self._data.id_conteneur
        conteneurs = self._data.conteneurs
        if conteneurs:
            first = conteneurs[0]
            if first is not None and first.cid:
                return first.cid
        return None

    @property
    def titre(self) -> str | None:
        return self._data.title

    @property
    def nor(self) -> str | None:
        return self._data.nor

    @property
    def etat(self) -> str | None:
        return self._data.etat

    @property
    def type_texte(self) -> str | None:
        """Type de texte (``TEXTE_BASE``, ``AVENANT``...)."""
        return self._data.type_texte

    @property
    def nature(self) -> str | None:
        return self._data.nature

    @property
    def date_signature(self):
        return self._data.date_texte

    @property
    def date_parution(self):
        return self._data.date_parution

    @property
    def texte_numero(self) -> str | None:
        return self._data.text_number

    @property
    def signataires(self):
        return self._data.signataires

    @property
    def articles(self) -> list:
        return self._data.articles or []

    @property
    def sections(self) -> list:
        return self._data.sections or []

    @property
    def visas_html(self) -> str | None:
        return self._data.visas_html

    def to_dict(self) -> dict[str, Any]:
        return self._data.model_dump(by_alias=True)

    def to_markdown(self) -> str:
        parts: list[str] = [f"## {self.titre or 'Texte KALI'}", ""]
        if self.etat:
            parts.append(f"**Statut**: {self.etat}")
        if self.type_texte:
            parts.append(f"**Type**: {self.type_texte}")
        if self.nor:
            parts.append(f"**NOR**: {self.nor}")
        if self.texte_numero:
            parts.append(f"**Numéro**: {self.texte_numero}")
        if self.date_signature:
            parts.append(f"**Signé le**: {self.date_signature}")
        if self.date_parution:
            parts.append(f"**Paru le**: {self.date_parution}")
        if self.container_id:
            parts.append(f"**Conteneur**: {self.container_id}")
        return "\n".join(parts)

    def __repr__(self) -> str:
        return (
            "TexteKali("
            f"titre={self.titre}, etat={self.etat}, "
            f"conteneur={self.container_id})"
        )


class KaliAPI:
    """API haut niveau pour le fond KALI."""

    def __init__(self, client: LegifranceClient):
        self._client = client

    def fetch_container(self, kali_id: str) -> ConventionCollective | None:
        """Récupère un conteneur par son identifiant ``KALICONT``.

        Wraps ``POST /consult/kaliCont``.
        """
        if not kali_id or not kali_id.strip():
            raise ValueError("kali_id ne peut pas être vide")
        payload = KaliContConsultRequest(id=kali_id.strip()).model_dump(
            by_alias=True, exclude_none=True
        )
        response = self._client.call_api("consult/kaliCont", payload)
        return self._wrap_container(response.json())

    def fetch_by_idcc(self, idcc: str | int) -> ConventionCollective | None:
        """Récupère un conteneur par son numéro IDCC.

        Wraps ``POST /consult/kaliContIdcc``. ``idcc`` doit être un
        entier ou une chaîne de chiffres (ex: ``"1261"``).
        """
        idcc_str = str(idcc).strip()
        if not _IDCC_PATTERN.match(idcc_str):
            raise ValueError(
                f"IDCC invalide: {idcc!r}. Attendu: 1 à 5 chiffres (ex: '1261')."
            )
        payload = KaliContConsultIdccRequest(id=idcc_str).model_dump(by_alias=True)
        response = self._client.call_api("consult/kaliContIdcc", payload)
        return self._wrap_container(response.json())

    def fetch_text(self, kali_id: str) -> TexteKali | None:
        """Récupère un texte KALI par son identifiant ``KALITEXT``.

        Wraps ``POST /consult/kaliText``.
        """
        if not kali_id or not kali_id.strip():
            raise ValueError("kali_id ne peut pas être vide")
        payload = KaliTextConsultRequest(id=kali_id.strip()).model_dump(
            by_alias=True, exclude_none=True
        )
        response = self._client.call_api("consult/kaliText", payload)
        return self._wrap_text(response.json())

    def fetch_article(self, article_id: str) -> TexteKali | None:
        """Récupère le texte parent contenant un article ``KALIARTI``.

        Wraps ``POST /consult/kaliArticle``. Le endpoint retourne le
        texte entier contextualisé autour de l'article demandé.
        """
        if not article_id or not article_id.strip():
            raise ValueError("article_id ne peut pas être vide")
        payload = KaliTextConsultArticleRequest(id=article_id.strip()).model_dump(
            by_alias=True
        )
        response = self._client.call_api("consult/kaliArticle", payload)
        return self._wrap_text(response.json())

    def fetch_section(self, section_id: str) -> TexteKali | None:
        """Récupère le texte parent contenant une section ``KALISCTA``.

        Wraps ``POST /consult/kaliSection``.
        """
        if not section_id or not section_id.strip():
            raise ValueError("section_id ne peut pas être vide")
        payload = KaliTextConsultSectionRequest(id=section_id.strip()).model_dump(
            by_alias=True
        )
        response = self._client.call_api("consult/kaliSection", payload)
        return self._wrap_text(response.json())

    def fetch(self, kali_id: str) -> ConventionCollective | TexteKali | None:
        """Dispatcher basé sur le préfixe de l'identifiant.

        - ``KALICONT`` → :meth:`fetch_container`
        - ``KALITEXT`` → :meth:`fetch_text`
        - ``KALIARTI`` → :meth:`fetch_article`
        - ``KALISCTA`` → :meth:`fetch_section`
        """
        if not kali_id or not kali_id.strip():
            raise ValueError("kali_id ne peut pas être vide")
        normalized = kali_id.strip()
        if normalized.startswith(KALI_CONT_PREFIX):
            return self.fetch_container(normalized)
        if normalized.startswith(KALI_TEXT_PREFIX):
            return self.fetch_text(normalized)
        if normalized.startswith(KALI_ARTI_PREFIX):
            return self.fetch_article(normalized)
        if normalized.startswith(KALI_SCTA_PREFIX):
            return self.fetch_section(normalized)
        raise ValueError(
            f"Préfixe KALI inconnu dans {kali_id!r}. "
            f"Attendu un des: {', '.join(KALI_PREFIXES)}."
        )

    def search(self, query: str | SearchRequest) -> list[ConventionCollective]:
        """Recherche dans le fond KALI.

        Le endpoint ``/search`` peut renvoyer différents types
        d'identifiants — typiquement des ``KALITEXT...`` (texte : une
        convention spécifique, un avenant…), parfois des
        ``KALICONT...`` (conteneur : la convention collective
        parente). Chaque identifiant est dispatché par préfixe via
        :meth:`fetch` pour charger l'entité correcte, puis ramené à un
        :class:`ConventionCollective` (conteneur) : pour un hit texte,
        on navigue vers le conteneur parent via
        :attr:`TexteKali.container_id`.

        Args:
            query: texte libre ou :class:`SearchRequest` pré-construit.

        Returns:
            Liste de :class:`ConventionCollective` déduplicée par
            identifiant conteneur. Vide si aucun résultat n'a pu être
            résolu vers un conteneur.

        Note:
            Limitation connue — un hit ``KALITEXT...`` dont la charge
            utile ne contient pas ``idConteneur`` est ignoré silen-
            cieusement (il n'y a pas d'autre chemin pour remonter au
            conteneur parent sans API additionnelle). Les avenants
            isolés peuvent donc être absents des résultats même après
            ce correctif ; une résolution complète nécessiterait un
            complément côté API Legifrance.
        """
        if isinstance(query, str):
            search_query = SearchRequest(search=query)
        else:
            search_query = query

        request_dto = search_query.to_api_model()
        payload = json.loads(
            json.dumps(request_dto.model_dump(by_alias=True), cls=EnumEncoder)
        )
        response = self._client.call_api("search", payload)

        if response.status_code != HTTP_OK:
            return []

        response_data = response.json()
        raw_results = response_data.get("results")
        if not isinstance(raw_results, list):
            return []

        containers: list[ConventionCollective] = []
        seen_container_ids: set[str] = set()
        for result in raw_results:
            result_id = self._extract_result_id(result)
            if result_id is None:
                continue
            try:
                entity = self.fetch(result_id)
            except Exception as exc:
                logger.warning("Échec de récupération KALI %s: %s", result_id, exc)
                continue
            if entity is None:
                continue

            container: ConventionCollective | None
            if isinstance(entity, ConventionCollective):
                cont_id = entity.id
                if not cont_id or cont_id in seen_container_ids:
                    continue
                seen_container_ids.add(cont_id)
                container = entity
            elif isinstance(entity, TexteKali):
                parent_id = entity.container_id
                # Dedupe BEFORE issuing the /consult/kaliCont call so
                # N text hits under the same convention cost 1 extra
                # fetch, not N.
                if not parent_id or parent_id in seen_container_ids:
                    continue
                seen_container_ids.add(parent_id)
                try:
                    container = self.fetch_container(parent_id)
                except Exception as exc:
                    logger.warning(
                        "Échec de récupération du conteneur KALI %s: %s",
                        parent_id,
                        exc,
                    )
                    continue
            else:
                # KALIARTI / KALISCTA hits are not search-level
                # convention sources — skip.
                continue

            if container is not None:
                containers.append(container)
        return containers

    @staticmethod
    def _extract_result_id(result: dict[str, Any]) -> str | None:
        titles = result.get("titles")
        if not isinstance(titles, list) or not titles:
            return None
        first = titles[0]
        if not isinstance(first, dict):
            return None
        text_id = first.get("id")
        return text_id if isinstance(text_id, str) and text_id else None

    def _wrap_container(
        self, response_data: dict[str, Any] | None
    ) -> ConventionCollective | None:
        if not response_data:
            return None
        try:
            model = ConsultKaliContResponse.model_validate(response_data)
        except Exception as exc:
            logger.error("Échec de validation ConsultKaliContResponse: %s", exc)
            return None
        return ConventionCollective(model, self._client)

    def _wrap_text(self, response_data: dict[str, Any] | None) -> TexteKali | None:
        if not response_data:
            return None
        try:
            model = ConsultKaliTextResponse.model_validate(response_data)
        except Exception as exc:
            logger.error("Échec de validation ConsultKaliTextResponse: %s", exc)
            return None
        return TexteKali(model, self._client)
