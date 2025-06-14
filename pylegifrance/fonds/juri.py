import json
import logging
from datetime import datetime
from typing import List, Optional, Union, Dict, Any

from pylegifrance.client import LegifranceClient
from pylegifrance.models.identifier import Cid, Eli, Nor
from pylegifrance.utils import EnumEncoder

from pylegifrance.models.juri.models import Decision
from pylegifrance.models.juri.search import SearchRequest
from pylegifrance.models.juri.api_wrappers import (
    ConsultRequest,
    ConsultByAncienIdRequest,
    ConsultResponse,
)

HTTP_OK = 200
CITATION_TYPE = "CITATION"

logger = logging.getLogger(__name__)


class JuriDecision:
    """
    Objet de domaine de haut niveau représentant une décision de justice.

    Cette classe encapsule le modèle Decision et fournit des comportements riches comme
    .latest(), .citations(), .versions(), et .at(date).
    """

    def __init__(self, decision: Decision, client: LegifranceClient):
        """
        Initialise une instance de JuriDecision.

        Parameters
        ----------
        decision : Decision
            Le modèle Decision sous-jacent.
        client : LegifranceClient
            Le client pour interagir avec l'API Legifrance.
        """
        self._decision = decision
        self._client = client

    @property
    def id(self) -> Optional[str]:
        """Récupère l'identifiant de la décision."""
        return self._decision.id

    @property
    def cid(self) -> Optional[Cid]:
        """Récupère le CID de la décision avec validation."""
        if not hasattr(self._decision, "cid") or not self._decision.cid:
            return None
        return Cid(self._decision.cid)

    @property
    def eli(self) -> Optional[Eli]:
        """Récupère l'ELI de la décision avec validation."""
        if not self._decision.id_eli:
            return None
        return Eli(self._decision.id_eli)

    @property
    def nor(self) -> Optional[Nor]:
        """Récupère le NOR de la décision avec validation."""
        if not self._decision.nor:
            return None
        return Nor(self._decision.nor)

    @property
    def ecli(self) -> Optional[str]:
        """Récupère l'ECLI de la décision."""
        return getattr(self._decision, "ecli", None)

    @property
    def date(self) -> Optional[datetime]:
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
    def title(self) -> Optional[str]:
        """Récupère le titre de la décision."""
        return self._decision.titre

    @property
    def long_title(self) -> Optional[str]:
        """Récupère le titre long de la décision."""
        return self._decision.titre_long

    @property
    def text(self) -> Optional[str]:
        """Récupère le texte de la décision."""
        return self._decision.texte

    @property
    def text_html(self) -> Optional[str]:
        """Récupère le texte HTML de la décision."""
        return self._decision.texte_html

    @property
    def formation(self) -> Optional[str]:
        """Récupère la formation de la décision."""
        return self._decision.formation

    @property
    def numero(self) -> Optional[str]:
        """Récupère le numéro de la décision."""
        return getattr(self._decision, "num", None)

    @property
    def jurisdiction(self) -> Optional[str]:
        """Récupère la juridiction de la décision."""
        return getattr(self._decision, "juridiction", None)

    @property
    def solution(self) -> Optional[str]:
        """Récupère la solution de la décision."""
        return getattr(self._decision, "solution", None)

    def citations(self) -> List["JuriDecision"]:
        """
        Récupère les citations de la décision.

        Returns
        -------
        List[JuriDecision]
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

    def at(self, date: Union[datetime, str]) -> Optional["JuriDecision"]:
        """
        Récupère la version de la décision à la date spécifiée.

        Parameters
        ----------
        date : Union[datetime, str]
            La date à laquelle récupérer la version.

        Returns
        -------
        Optional[JuriDecision]
            La version de la décision à la date spécifiée, ou None si non trouvée.
        """
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date)
            except ValueError:
                raise ValueError(f"Format de date invalide: {date}")

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
        """
        Récupère la dernière version de la décision.

        Returns
        -------
        Optional[JuriDecision]
            La dernière version de la décision, ou None si non trouvée.
        """
        if self.id is None:
            return None

        try:
            return JuriAPI(self._client).fetch(self.id)
        except Exception:
            return None

    def versions(self) -> List["JuriDecision"]:
        """
        Récupère toutes les versions de la décision.

        Returns
        -------
        List[JuriDecision]
            Une liste d'objets JuriDecision représentant toutes les versions.
        """
        if self.id is None:
            return []

        try:
            return JuriAPI(self._client).fetch_versions(self.id)
        except Exception:
            return []

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit la décision en dictionnaire.

        Returns
        -------
        Dict[str, Any]
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
        """
        Initialise une instance de JuriAPI.

        Parameters
        ----------
        client : LegifranceClient
            Le client pour interagir avec l'API Legifrance.
        """
        self._client = client

    def _process_consult_response(
        self, response_data: ConsultResponse
    ) -> Optional[Decision]:
        """
        Traite une réponse de consultation et extrait la Décision.

        Parameters
        ----------
        response_data : dict
            Les données de réponse JSON de l'API.

        Returns
        -------
        Optional[Decision]
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

    def fetch(self, text_id: str) -> Optional[JuriDecision]:
        """
        Récupère une décision par son identifiant.

        Parameters
        ----------
        text_id : str
            L'identifiant de la décision à récupérer.

        Returns
        -------
        Optional[JuriDecision]
            La décision, ou None si non trouvée.

        Raises
        ------
        ValueError
            Si l'identifiant du texte est invalide.
        Exception
            Si l'appel à l'API échoue.
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

    def fetch_with_ancien_id(self, ancien_id: str) -> Optional[JuriDecision]:
        """
        Récupère une décision par son ancien identifiant.

        Parameters
        ----------
        ancien_id : str
            L'ancien identifiant de la décision à récupérer.

        Returns
        -------
        Optional[JuriDecision]
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

    def fetch_version_at(self, text_id: str, date: str) -> Optional[JuriDecision]:
        """
        Récupère la version d'une décision à une date spécifique.

        Parameters
        ----------
        text_id : str
            L'identifiant de la décision à récupérer.
        date : str
            La date à laquelle récupérer la version, au format ISO.

        Returns
        -------
        Optional[JuriDecision]
            La version de la décision à la date spécifiée, ou None si non trouvée.
        """
        if not text_id:
            raise ValueError("L'identifiant du texte ne peut pas être vide")

        try:
            datetime.fromisoformat(date)
        except ValueError:
            raise ValueError(f"Format de date invalide: {date}")

        request = {"textId": text_id, "date": date}
        response = self._client.call_api("consult/juri/version", request)

        if response.status_code != HTTP_OK:
            return None

        response_data = response.json()
        decision = self._process_consult_response(response_data)

        if not decision:
            return None

        return JuriDecision(decision, self._client)

    def fetch_versions(self, text_id: str) -> List[JuriDecision]:
        """
        Récupère toutes les versions d'une décision.

        Parameters
        ----------
        text_id : str
            L'identifiant de la décision dont on veut récupérer les versions.

        Returns
        -------
        List[JuriDecision]
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

    def search(self, query: Union[str, SearchRequest]) -> List[JuriDecision]:
        """
        Recherche des décisions correspondant à la requête.

        Parameters
        ----------
        query : Union[str, SearchRequest]
            La requête de recherche, soit sous forme de chaîne, soit sous forme d'objet SearchRequest.

        Returns
        -------
        List[JuriDecision]
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
