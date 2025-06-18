import json
import logging
from datetime import datetime
from typing import List, Union, Self
from pylegifrance.models.code import models
from pylegifrance.models.code.search import (
    CodeSearchCriteria,
    CodeDateSearchRequest,
    CodeEtatSearchRequest,
    DateVersionFiltre,
    TextLegalStatusFiltre,
    ChampCode,
    CritereCode,
    NomCodeFiltre,
)
from pylegifrance.models.code.consult import CodeConsultRequest
from pylegifrance.models.code.enum import TypeChampCode, NomCode
from pylegifrance.models.constants import TypeRecherche, EtatJuridique
from pylegifrance import LegifranceClient

logger = logging.getLogger(__name__)


class CodeSearchBuilder:
    """Builder pour construire des requêtes de recherche de codes juridiques.

    Cette classe implémente le pattern Builder pour permettre la construction
    fluide de requêtes de recherche dans les codes juridiques français.

    Args:
        api_client: Client API Légifrance pour exécuter les requêtes.
        fond: Type de fond juridique (CODE_DATE ou CODE_ETAT).

    Attributes:
        api: Client API Légifrance.
        fond: Type de fond juridique.
        criteria: Critères de recherche en cours de construction.
    """

    def __init__(self, api_client: LegifranceClient, fond: str):
        self.api = api_client
        self.fond = fond
        self.criteria = CodeSearchCriteria()
        self._champs = []
        self._filtres = []
        self._formatter = False

    def in_code(self, code_name: NomCode) -> Self:
        """Filtre la recherche à un code juridique spécifique.

        Args:
            code_name: Nom du code (peut être une chaîne ou une valeur de l'énumération NomCode).

        Returns:
            Self: Le builder pour chaînage.

        Raises:
            ValueError: Si le nom du code n'est pas valide.
        """

        self._filtres.append(NomCodeFiltre(valeurs=[code_name]))
        return self

    def in_codes(self, code_names: List[Union[str, NomCode]]) -> Self:
        """Filtre la recherche à plusieurs codes juridiques.

        Args:
            code_names: Liste des noms de codes.

        Returns:
            Self: Le builder pour chaînage.
        """
        # Validation et conversion des noms de codes
        validated_codes = []
        for code in code_names:
            if isinstance(code, str):
                try:
                    # Tenter de convertir en NomCode si c'est une chaîne
                    validated_codes.append(getattr(NomCode, code))
                except AttributeError:
                    # Vérifier si c'est un nom de code valide
                    valid_codes = [c.value for c in NomCode]
                    if code in valid_codes:
                        validated_codes.append(code)
                    else:
                        raise ValueError(f"Nom de code invalide: {code}")
            else:
                validated_codes.append(code)

        # Ajouter le filtre de codes
        self._filtres.append(NomCodeFiltre(valeurs=validated_codes))
        return self

    def article_number(self, number: str) -> Self:
        """Recherche un article par son numéro.

        Args:
            number: Numéro de l'article (ex: "1234", "L123-4").

        Returns:
            Self: Le builder pour chaînage.
        """
        self._champs.append(
            ChampCode(
                typeChamp=TypeChampCode.NUM_ARTICLE,
                criteres=[
                    CritereCode(
                        typeRecherche=TypeRecherche.EXACTE,
                        valeur=number,
                        proximite=None,
                    )
                ],
            )
        )
        return self

    def text(
        self, search_text: str, in_field: TypeChampCode = TypeChampCode.ALL
    ) -> Self:
        """Recherche un texte dans les articles.

        Args:
            search_text: Texte à rechercher.
            in_field: Champ dans lequel rechercher (par défaut: ALL).

        Returns:
            Self: Le builder pour chaînage.
        """
        self._champs.append(
            ChampCode(
                typeChamp=in_field,
                criteres=[
                    CritereCode(
                        typeRecherche=TypeRecherche.TOUS_LES_MOTS_DANS_UN_CHAMP,
                        valeur=search_text,
                        proximite=None,
                    )
                ],
            )
        )
        return self

    def at_date(self, date_str: str) -> Self:
        """Filtre la recherche à une date spécifique.

        Args:
            date_str: Date au format YYYY-MM-DD.

        Returns:
            Self: Le builder pour chaînage.

        Raises:
            ValueError: Si le fond n'est pas CODE_DATE.
        """
        if self.fond != "CODE_DATE":
            raise ValueError(
                "Le filtre de date n'est utilisable qu'avec le fond CODE_DATE"
            )

        # Convertir la date en datetime
        try:
            date_obj = datetime.fromisoformat(date_str)
        except ValueError:
            raise ValueError(
                f"Format de date invalide: {date_str}. Utilisez YYYY-MM-DD"
            )

        # Ajouter le filtre de date
        self._filtres.append(DateVersionFiltre(singleDate=date_obj))
        return self

    def with_legal_status(
        self, status: List[EtatJuridique] = [EtatJuridique.VIGUEUR]
    ) -> Self:
        """Filtre la recherche par statut juridique.

        Args:
            status: Statut juridique (VIGUEUR, ABROGE, etc.).

        Returns:
            Self: Le builder pour chaînage.

        Raises:
            ValueError: Si le fond n'est pas CODE_ETAT.
        """
        if self.fond != "CODE_ETAT":
            raise ValueError(
                "Le filtre d'état juridique n'est utilisable qu'avec le fond CODE_ETAT"
            )

        self._filtres.append(TextLegalStatusFiltre(valeurs=status))
        return self

    def paginate(self, page_number: int = 1, page_size: int = 10) -> Self:
        """Configure la pagination des résultats.

        Args:
            page_number: Numéro de page (commence à 1).
            page_size: Nombre d'éléments par page (max 100).

        Returns:
            Self: Le builder pour chaînage.
        """
        if page_number < 1:
            raise ValueError("Le numéro de page doit être supérieur ou égal à 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("La taille de page doit être entre 1 et 100")

        self.criteria.page_number = page_number
        self.criteria.page_size = page_size
        return self

    def with_formatter(self) -> Self:
        """Active le formatage des résultats (génération d'URLs, etc.).

        Returns:
            Self: Le builder pour chaînage.
        """
        self._formatter = True
        return self

    def execute(self) -> List[models.Article]:
        """Exécute la recherche et retourne les résultats.

        Returns:
            List[models.Article]: Liste des articles correspondant aux critères.

        Raises:
            ValueError: Si les critères de recherche sont invalides.
        """
        # Finaliser les critères de recherche
        logger.debug(f"Champs: {self._champs}")
        logger.debug(f"Filtres: {self._filtres}")

        # Vérifier qu'au moins un filtre est spécifié ou qu'il y a des champs de recherche
        if not self._filtres and not self._champs:
            raise ValueError(
                "Au moins un filtre ou un champ de recherche doit être spécifié"
            )

        # Si aucun champ n'est spécifié mais qu'un filtre de code est présent,
        # on considère que c'est une recherche de code complet
        if not self._champs and any(
            isinstance(f, NomCodeFiltre) for f in self._filtres
        ):
            logger.debug("Recherche de code complet détectée")

        self.criteria.champs = self._champs
        self.criteria.filtres = self._filtres
        logger.debug(f"Criteria champs: {self.criteria.champs}")
        logger.debug(f"Criteria filtres: {self.criteria.filtres}")

        # Créer la requête selon le type de fond
        if self.fond == "CODE_DATE":
            # Vérifier qu'un filtre de date est présent
            has_date_filter = any(
                isinstance(f, DateVersionFiltre) for f in self._filtres
            )

            # Pour une recherche de code complet, on n'exige pas de filtre de date
            is_complete_code_search = not self._champs and any(
                isinstance(f, NomCodeFiltre) for f in self._filtres
            )

            if not has_date_filter and not is_complete_code_search:
                raise ValueError("CODE_DATE nécessite un filtre de date (at_date)")

            # Si c'est une recherche de code complet sans date, on ajoute la date du jour
            if not has_date_filter and is_complete_code_search:
                logger.debug(
                    "Ajout de la date du jour pour la recherche de code complet"
                )
                current_timestamp = datetime.now()
                self._filtres.append(DateVersionFiltre(singleDate=current_timestamp))

            request = CodeDateSearchRequest(recherche=self.criteria)
        elif self.fond == "CODE_ETAT":
            request = CodeEtatSearchRequest(recherche=self.criteria)
        else:
            raise ValueError(f"Type de fond non supporté: {self.fond}")

        # Exécuter la requête
        response = self.api.call_api(
            "search", request.model_dump(by_alias=True, mode="json")
        )

        results = []
        if response:
            response_json = json.loads(response.text)

            # Log pagination information
            page_number = response_json.get("pageNumber", 1)
            page_size = response_json.get("pageSize", 10)
            total_results = response_json.get("totalResults", 0)
            total_pages = (
                (total_results + page_size - 1) // page_size if page_size > 0 else 0
            )
            logger.debug(f"Page number: {page_number}, Page size: {page_size}")
            logger.debug(f"Total results: {total_results}, Total pages: {total_pages}")

            if "results" in response_json:
                logger.debug(
                    f"Results: {json.dumps(response_json['results'], indent=2, ensure_ascii=False)}"
                )

                # Process each result item
                for item in response_json["results"]:
                    # Process items with sections
                    if "sections" in item and item["sections"]:
                        for section in item["sections"]:
                            # If formatter is enabled, add CID from section to extracts
                            section_cid = None
                            if self._formatter and "id" in section and section["id"]:
                                section_cid = section["id"]

                            if "extracts" in section and section["extracts"]:
                                for extract in section["extracts"]:
                                    if extract.get("type") == "articles":
                                        # Add section CID to extract if formatter is enabled
                                        if self._formatter and section_cid:
                                            extract["cid"] = section_cid

                                        # Use enhanced models.Article.from_orm to process the extract
                                        article = models.Article.from_orm(
                                            {**extract, **item}
                                        )

                                        results.append(article)

                                        # Respect page size
                                        if len(results) >= self.criteria.page_size:
                                            break

                            # Respect page size
                            if len(results) >= self.criteria.page_size:
                                break

                        # Respect page size
                        if len(results) >= self.criteria.page_size:
                            break
                    else:
                        # Standard processing for results not structured in sections
                        article = models.Article.from_orm(item)
                        results.append(article)

                        # Respect page size
                        if len(results) >= self.criteria.page_size:
                            break

        return results


class CodeConsultFetcher:
    """Builder pour configurer et exécuter la consultation d'un code juridique.

    Cette classe implémente le pattern Builder pour permettre la configuration
    fluide de la consultation d'un code juridique français.

    Args:
        api_client: Client API Légifrance pour exécuter les requêtes.
        text_id: Identifiant LEGITEXT du code à consulter.

    Attributes:
        api: Client API Légifrance.
        text_id: Identifiant du code.
        date: Date de consultation (optionnelle).
        abrogated: Inclure les textes abrogés.
        searched_string: Texte de recherche pour mise en évidence.
        section_id: Identifiant de section spécifique à consulter.
    """

    def __init__(self, api_client: LegifranceClient, text_id: str):
        self.api = api_client
        self.text_id = text_id
        self.date = None
        self.abrogated = False
        self.searched_string = None
        self.section_id = None

    def at(self, date: str) -> models.Code:
        """Consulte le code à une date spécifique.

        Args:
            date: Date au format YYYY-MM-DD ou timestamp Unix en millisecondes.

        Returns:
            models.Article: L'article consulté.

        Raises:
            ValueError: Si le format de date est invalide.
        """
        logger.debug(f"CodeConsultFetcher.at called with date: {date}")
        # Essayer de traiter comme un timestamp Unix en millisecondes
        if date.isdigit() and len(date) >= 10:
            try:
                # Convertir le timestamp (millisecondes) en datetime
                timestamp = int(date) / 1000
                dt = datetime.fromtimestamp(timestamp)
                # Formater en YYYY-MM-DD
                self.date = dt.strftime("%Y-%m-%d")
                logger.debug(f"Date converted from timestamp to: {self.date}")
                return self._execute()
            except (ValueError, OverflowError):
                pass  # Continuer avec la validation du format YYYY-MM-DD

        # Valider le format de date YYYY-MM-DD
        try:
            datetime.fromisoformat(date)
            self.date = date
            logger.debug(f"Date set to: {self.date}")
            return self._execute()
        except ValueError:
            raise ValueError(
                f"Format de date invalide: {date}. Utilisez YYYY-MM-DD ou un timestamp Unix en millisecondes"
            )

    def include_abrogated(self, include: bool = True) -> Self:
        """Configure l'inclusion des textes abrogés.

        Args:
            include: True pour inclure les textes abrogés, False sinon.

        Returns:
            Self: Le builder pour chaînage.
        """
        self.abrogated = include
        return self

    def section(self, section_id: str) -> Self:
        """Configure la consultation d'une section spécifique.

        Args:
            section_id: Identifiant LEGISCTA de la section.

        Returns:
            Self: Le builder pour chaînage.
        """
        self.section_id = section_id
        return self

    def _execute(self) -> models.Code:
        """Exécute la consultation et retourne le résultat.

        Returns:
            Code: Code consulté.

        Raises:
            ValueError: Si les paramètres de consultation sont invalides.
        """
        logger.debug(f"CodeConsultFetcher._execute called with self.date: {self.date}")
        if not self.date:
            self.date = datetime.now().strftime("%Y-%m-%d")
            logger.debug(f"Date was None, set to current date: {self.date}")

        request = CodeConsultRequest(
            textId=self.text_id,
            date=self.date,
            abrogated=self.abrogated,
            searchedString=self.searched_string,
            sctCid=self.section_id,
            fromSuggest=None,
        )
        logger.debug(f"Created CodeConsultRequest with date: {request.date}")

        request_data = request.model_dump(by_alias=True, mode="json")
        logger.debug(f"Request data: {request_data}")
        response = self.api.call_api("consult/code", request_data)

        return models.Code.from_orm(response.json())


class ArticleFetcher:
    """Récupérateur d'articles utilisant le point de terminaison /consult/getArticle."""

    def __init__(self, api_client: LegifranceClient, article_id: str):
        self.api = api_client
        self.article_id = article_id
        self.date = None
        self.searched_string = None

    def at(self, date: Union[str, datetime, int]) -> models.Article:
        """Récupère un article à une date spécifique.

        Args:
            date: Date au format YYYY-MM-DD, datetime, ou timestamp (ms)

        Returns:
            models.Article: L'objet models.Article récupéré
        """
        # Convert date to string format
        if isinstance(date, datetime):
            date_str = date.strftime("%Y-%m-%d")
        elif isinstance(date, int):
            # Unix timestamp in milliseconds
            date_str = datetime.fromtimestamp(date / 1000).strftime("%Y-%m-%d")
        elif isinstance(date, str):
            # Validate format
            datetime.fromisoformat(date)
            date_str = date
        else:
            raise ValueError(f"Type de date invalide: {type(date)}")

        # Build request
        request_data = {"id": self.article_id, "date": date_str}

        # Execute request
        response = self.api.call_api("consult/getArticle", request_data)

        if not response:
            raise ValueError(f"Article {self.article_id} non trouvé")

        # Parse response and create models.Article using enhanced from_orm method
        return models.Article.from_orm(response.json())


class Code:
    """Interface pour rechercher et consulter les codes juridiques français.

    Permet de rechercher dans les codes juridiques français (Code civil, Code pénal, etc.)
    et de récupérer des articles spécifiques. Utilise l'API Légifrance en arrière-plan
    et propose une approche par étapes pour construire des recherches précises.

    Args:
        api_client: Client pour se connecter à l'API Légifrance.
        fond: Type de recherche. CODE_DATE pour chercher à une date précise,
            CODE_ETAT pour chercher dans la version actuelle (défaut).

    Examples:
        Initialisation basique:
            >>> from pylegifrance import LegifranceClient
            >>> client = LegifranceClient(client_id="...", client_secret="...")
            >>> code = Code(client)

        Recherche d'articles par numéro:
            >>> results = (code.search()
            ...                .in_code(NomCode.CC)  # Code civil
            ...                .article_number("1234")
            ...                .execute())

        Recherche textuelle avec filtres:
            >>> results = (code.search()
            ...                .in_codes([NomCode.CC, NomCode.CP])
            ...                .text("contrat de vente")
            ...                .at_date("2020-01-01")
            ...                .page_size(20)
            ...                .execute())

        Consultation d'un article spécifique:
            >>> article = code.fetch_code("LEGIARTI000006419292").at("2020-01-01")
            >>> print(article.format_citation())

        Recherche historique:
            >>> code_historique = Code(client, fond="CODE_DATE")
            >>> results = (code_historique.search()
            ...                .in_code(NomCode.CC)
            ...                .at_date("1990-01-01")
            ...                .execute())

    Note:
        - CODE_DATE: Permet les recherches historiques avec filtre de date obligatoire
        - CODE_ETAT: Recherche dans l'état juridique actuel (défaut recommandé)
        - Les recherches utilisent le pattern Builder pour une API fluide et lisible
        - L'authentification OAuth est gérée automatiquement par le client

    Attributes:
        api: Client API Légifrance configuré pour les appels REST.
        fond: Type de fond juridique utilisé pour les recherches.

    See Also:
        LegifranceClient: Client de base pour l'authentification et les appels API
        CodeSearchBuilder: Builder pour construire des requêtes de recherche complexes
        models.Article: Modèle représentant un article de code avec métadonnées
        NomCode: Énumération des codes juridiques français disponibles
    """

    def __init__(self, api_client: LegifranceClient, fond: str = "CODE_ETAT"):
        self.api = api_client
        self.fond = fond

    def search(self) -> CodeSearchBuilder:
        """Démarre la construction d'une requête de recherche.

        Returns:
            CodeSearchBuilder: Builder pour construire la requête de manière fluide.
        """
        return CodeSearchBuilder(self.api, self.fond)

    def fetch_code(self, text_id: str) -> "CodeConsultFetcher":
        """Récupère le contenu complet d'un code juridique.

        Args:
            text_id: Identifiant LEGITEXT du code à récupérer.

        Returns:
            CodeConsultFetcher: Builder pour configurer la consultation.

        Examples:
            >>> code.fetch_code("LEGITEXT000006070721").at("2020-01-01")
        """
        return CodeConsultFetcher(self.api, text_id)

    def fetch_article(self, article_id: str) -> ArticleFetcher:
        """Récupère un article en utilisant /consult/getArticle.

        Args:
            article_id: Identifiant LEGIARTI

        Returns:
            ArticleFetcher: Récupérateur pour la configuration de date
        """
        if not article_id or not article_id.startswith("LEGIARTI"):
            raise ValueError(f"Identifiant d'article invalide: {article_id}")
        return ArticleFetcher(self.api, article_id)
