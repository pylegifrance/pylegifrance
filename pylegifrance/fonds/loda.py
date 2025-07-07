import json
import logging
import re
from datetime import datetime
from typing import List, Optional, Union, Dict, Any, Tuple

from pylegifrance.client import LegifranceClient
from pylegifrance.models.identifier import Cid, Nor
from pylegifrance.utils import EnumEncoder
from pylegifrance.models.loda.models import TexteLoda as TexteLodaModel
from pylegifrance.models.generated.model import ConsultSection, ConsultArticle
from pylegifrance.models.loda.search import SearchRequest
from pylegifrance.models.loda.api_wrappers import (
    ConsultRequest,
    ConsultVersionRequest,
    ListVersionsRequest,
)
from pylegifrance.models.code.models import Article

# Constantes
HTTP_OK = 200
DATE_SEPARATOR = "_"
DATE_FORMAT_SEPARATOR = "-"
FRENCH_DATE_FORMAT_LENGTH = 10
FRENCH_DATE_DAY_POSITION = 0
FRENCH_DATE_MONTH_POSITION = 1
FRENCH_DATE_YEAR_POSITION = 2

logger = logging.getLogger(__name__)


class TexteLoda:
    """
    Objet de domaine de haut niveau représentant un texte LODA (Lois, Ordonnances, Décrets, Arrêtés).

    Cette classe encapsule le modèle TexteLoda et fournit des comportements riches comme
    .latest(), .versions(), et .at(date).
    """

    def __init__(self, texte: TexteLodaModel, client: LegifranceClient):
        """
        Initialise une instance de TexteLoda.

        Parameters
        ----------
        texte : TexteLodaModel
            Le modèle TexteLoda sous-jacent.
        client : LegifranceClient
            Le client pour interagir avec l'API Legifrance.
        """
        self._texte = texte
        self._client = client
        self._code_client = None

    @property
    def id(self) -> Optional[str]:
        """Récupère l'identifiant du texte."""
        if not self._texte.id:
            return None
        return self._texte.id

    @property
    def cid(self) -> Optional[Cid]:
        """Récupère le CID du texte avec validation."""
        if not self._texte.cid:
            return None
        return Cid(self._texte.cid)

    @property
    def nor(self) -> Optional[Nor]:
        """Récupère le NOR du texte avec validation."""
        if not self._texte.nor:
            return None
        return Nor(self._texte.nor)

    @property
    def titre(self) -> Optional[str]:
        """Récupère le titre du texte."""
        return self._texte.titre

    @property
    def titre_long(self) -> Optional[str]:
        """Récupère le titre long du texte."""
        return self._texte.titre_long

    @property
    def date_debut(self) -> Optional[datetime]:
        """Récupère la date de début du texte."""
        return self._texte.date_debut_dt

    @property
    def date_fin(self) -> Optional[datetime]:
        """Récupère la date de fin du texte."""
        return self._texte.date_fin_dt

    @property
    def etat(self) -> Optional[str]:
        """Récupère l'état juridique du texte."""
        return self._texte.etat

    @property
    def last_update(self) -> Optional[datetime]:
        """Récupère la date de dernière mise à jour du texte."""
        return self._texte.last_update_dt

    @property
    def date_publication(self) -> Optional[datetime]:
        """Récupère la date de publication du texte."""
        return (
            self._texte.consult_response.date_parution
            if self._texte.consult_response
            else None
        )

    @property
    def texte_html(self) -> Optional[str]:
        """
        Récupère le contenu HTML du texte.

        Si texte_html est None, tente d'extraire le contenu des sections et articles.
        Cette propriété est maintenue pour la compatibilité, mais il est recommandé
        d'accéder directement aux sections et articles pour un traitement plus précis.
        """
        if self._texte.texte_html is not None:
            return self._texte.texte_html

        # Si texte_html est None, tenter d'extraire le contenu des sections et articles
        content_parts = []

        # Extraire le contenu des articles racine
        if self._texte.articles:
            for article in self._texte.articles:
                if article.content:
                    content_parts.append(article.content)

        # Extraire le contenu des sections
        if self._texte.sections:
            for section in self._texte.sections:
                # Ajouter le titre de la section
                if section.title:
                    content_parts.append(f"<h2>{section.title}</h2>")

                # Extraire le contenu des articles de la section
                if section.articles:
                    for article in section.articles:
                        if article.content:
                            content_parts.append(article.content)

        if content_parts:
            return " ".join(content_parts)

        return None

    @property
    def texte_brut(self) -> Optional[str]:
        """
        Récupère le contenu du texte nettoyé des balises HTML avec formatage préservé.

        Utilise BeautifulSoup (recommandé 2025) avec fallback regex.

        Returns
        -------
        Optional[str]
            Le contenu du texte sans balises HTML mais avec formatage lisible.
        """
        html_content = self.texte_html
        if not html_content:
            return None

        try:
            # Méthode recommandée 2025: BeautifulSoup (optional dependency)
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, "html.parser")

            # Ajouter des retours à la ligne avant les balises de structure
            for br in soup.find_all("br"):
                br.replace_with(soup.new_string("\n"))
            for p in soup.find_all(["p", "div"]):
                p.insert_before(soup.new_string("\n"))
                p.insert_after(soup.new_string("\n"))
            for blockquote in soup.find_all("blockquote"):
                blockquote.insert_before(soup.new_string("\n"))
                blockquote.insert_after(soup.new_string("\n"))
            for h in soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                h.insert_before(soup.new_string("\n"))
                h.insert_after(soup.new_string("\n"))

            text = soup.get_text()

            # Nettoyer les espaces multiples et retours à la ligne excessifs
            text = re.sub(r"\n\s*\n", "\n\n", text)
            text = re.sub(r" +", " ", text)

            return text.strip() or None

        except ImportError:
            # Fallback: regex (built-in) avec amélioration du formatage

            # Remplacer certaines balises par des retours à la ligne
            text = re.sub(r"<br/?>", "\n", html_content)
            text = re.sub(r"<p[^>]*>", "\n", text)
            text = re.sub(r"</p>", "\n", text)
            text = re.sub(r"<BLOCKQUOTE[^>]*>", "\n", text)
            text = re.sub(r"</BLOCKQUOTE>", "\n", text)
            text = re.sub(r"<h[1-6][^>]*>", "\n", text)
            text = re.sub(r"</h[1-6]>", "\n", text)

            # Supprimer toutes les autres balises HTML
            text = re.sub(r"<[^>]+>", "", text)

            # Nettoyer les espaces multiples et retours à la ligne excessifs
            text = re.sub(r"\n\s*\n", "\n\n", text)
            text = re.sub(r" +", " ", text)

            return text.strip() or None

    @property
    def sections(self) -> Optional[List[ConsultSection]]:
        """Récupère les sections du texte."""
        return self._texte.sections

    @property
    def articles(self) -> Optional[List[ConsultArticle]]:
        """Récupère les articles racine du texte."""
        return self._texte.articles

    def at(self, date: Union[datetime, str]) -> Optional["TexteLoda"]:
        """
        Récupère la version du texte à la date spécifiée.

        Parameters
        ----------
        date : Union[datetime, str]
            La date à laquelle récupérer la version, soit comme objet datetime, soit comme chaîne au format ISO.

        Returns
        -------
        Optional[TexteLoda]
            La version du texte à la date spécifiée, ou None si non trouvée.

        Raises
        ------
        ValueError
            Si la date est invalide.
        """
        # Convertir datetime en chaîne si nécessaire
        if isinstance(date, datetime):
            date_str = date.isoformat()
        else:
            date_str = date
            # Valider le format de la date
            try:
                datetime.fromisoformat(date_str)
            except ValueError:
                raise ValueError(f"Format de date invalide: {date_str}")

        # Créer une instance Loda pour utiliser sa méthode fetch_version_at
        loda = Loda(self._client)
        if self.id is None:
            raise ValueError("TexteLoda.id is None; cannot fetch version at.")
        return loda.fetch_version_at(self.id, date_str)

    def latest(self) -> Optional["TexteLoda"]:
        """
        Récupère la dernière version du texte.

        Returns
        -------
        Optional[TexteLoda]
            La dernière version du texte, ou None si non trouvée.
        """
        # Créer une instance Loda pour utiliser sa méthode fetch
        if self.id is None:
            raise ValueError("TexteLoda.id is None, cannot fetch Loda.")
        loda = Loda(self._client)
        return loda.fetch(self.id)

    def versions(self) -> List["TexteLoda"]:
        """
        Récupère toutes les versions du texte.

        Returns
        -------
        List[TexteLoda]
            Une liste de toutes les versions du texte.
        """
        # Créer une instance Loda pour utiliser sa méthode fetch_versions
        loda = Loda(self._client)
        if self.id is None:
            return []
        return loda.fetch_versions(self.id)

    def get_modified_articles(self) -> List[Article]:
        """
        Récupère les articles qui sont modifiés par cette loi.

        Returns
        -------
        List[Article]
            Une liste des articles modifiés par cette loi.
        """
        from pylegifrance.fonds.code import Code

        logger.debug(f"Recherche des articles modifiés par la loi {self.id}")
        modified_articles = []

        if not self.articles:
            return modified_articles

        for article in self.articles:
            logger.debug(
                f"Analyse de l'article {article.id} pour les liens de modification"
            )

            if not (
                hasattr(article, "lst_lien_modification")
                and article.lst_lien_modification
            ):
                logger.debug(
                    f"Aucun lien de modification trouvé pour l'article {article.id}"
                )
                continue

            logger.debug(
                f"Trouvé {len(article.lst_lien_modification)} liens de modification pour l'article {article.id}"
            )

            for lien in article.lst_lien_modification:
                logger.debug(
                    f"Lien de modification: type={lien.link_type}, article_id={lien.article_id}, date_debut_cible={lien.date_debut_cible}"
                )

                if not self._is_outgoing_modification_link(lien):
                    continue

                try:
                    modified_article = self._fetch_modified_article(
                        lien, Code(self._client)
                    )
                    modified_articles.append(modified_article)
                    logger.debug(
                        f"Article modifié {lien.article_id} récupéré avec succès"
                    )
                except Exception as e:
                    logger.warning(
                        f"Impossible de récupérer l'article {lien.article_id}: {e}"
                    )
                    continue

        logger.debug(f"Total des articles modifiés récupérés: {len(modified_articles)}")
        return modified_articles

    def _is_outgoing_modification_link(self, lien: Any) -> bool:
        """
        Vérifie si le lien représente une modification sortante (cette loi modifie d'autres textes).

        Parameters
        ----------
        lien : Any
            Le lien de modification à vérifier.

        Returns
        -------
        bool
            True si c'est une modification sortante valide.
        """
        return lien.link_type == "MODIFIE" and lien.article_id and lien.date_debut_cible

    def _fetch_modified_article(self, lien: Any, code_api: Any) -> Article:
        """
        Récupère un article modifié à partir d'un lien de modification.

        Parameters
        ----------
        lien : Any
            Le lien de modification contenant l'ID et la date.
        code_api : Any
            L'instance de l'API Code pour récupérer l'article.

        Returns
        -------
        Article
            L'article modifié.

        Raises
        ------
        Exception
            Si la récupération échoue.
        """
        logger.debug(
            f"Récupération de l'article modifié {lien.article_id} à la date {lien.date_debut_cible}"
        )
        return code_api.fetch_article(lien.article_id).at(lien.date_debut_cible)

    def format_modifications_report(self) -> str:
        """
        Formate un rapport des modifications avec citations, contenu et URLs.

        Returns
        -------
        str
            Un rapport markdown des modifications apportées par cette loi.
        """
        if not self.articles:
            return "Aucune modification disponible."

        # En-tête du rapport
        rapport = "# Modifications apportées par cette loi\n\n"
        rapport += f"**Titre**: {self.titre or 'Non spécifié'}\n"
        rapport += f"**Statut**: {self.etat or 'Non spécifié'}\n"
        rapport += f"**Date d'entrée en vigueur**: {self.date_debut.strftime('%d/%m/%Y') if self.date_debut else 'Non spécifiée'}\n\n"
        rapport += "---\n\n"

        modifications_found = False

        for article in self.articles:
            if (
                hasattr(article, "lst_lien_modification")
                and article.lst_lien_modification
            ):
                modifications_found = True
                rapport += f"## Article {article.num}\n\n"

                for i, lien in enumerate(article.lst_lien_modification, 1):
                    if lien.link_type == "MODIFIE" and lien.article_id:
                        try:
                            logger.debug(
                                f"Formatage du rapport - récupération de l'article {lien.article_id}"
                            )
                            # Récupérer l'article modifié
                            from pylegifrance.fonds.code import Code

                            code_api = Code(self._client)
                            article_modifie = (
                                code_api.fetch_article(lien.article_id).at(
                                    lien.date_debut_cible
                                )
                                if lien.date_debut_cible
                                else None
                            )

                            rapport += f"### Modification {i}: {lien.text_title}\n\n"

                            # Citation juridique
                            citation = (
                                article_modifie.format_citation()
                                if article_modifie
                                else f"Article {lien.article_num}"
                            )
                            rapport += f"**Citation**: {citation}\n\n"

                            # URL de consultation - utiliser directement l'articleId du lien
                            article_url = f"https://www.legifrance.gouv.fr/codes/article_lc/{lien.article_id}"
                            rapport += f"**Consulter**: [{lien.article_num}]({article_url})\n\n"

                            # Contenu de l'article modifié
                            if article_modifie and article_modifie.content:
                                # Nettoyer le contenu HTML pour l'affichage markdown
                                contenu_nettoye = self._clean_html_for_markdown(
                                    article_modifie.content
                                )
                                rapport += f"**Nouveau contenu**:\n\n```\n{contenu_nettoye}\n```\n\n"
                            else:
                                rapport += (
                                    "**Nouveau contenu**: Contenu non disponible\n\n"
                                )

                            # Métadonnées
                            rapport += f"**Date d'entrée en vigueur**: {lien.date_debut_cible}\n"
                            rapport += f"**Code source**: {lien.text_cid}\n\n"

                        except Exception as e:
                            logger.warning(
                                f"Erreur lors du formatage de l'article {lien.article_id}: {e}"
                            )
                            rapport += f"### Modification {i}: {lien.text_title}\n\n"
                            rapport += f"**Article**: {lien.article_num}\n"
                            rapport += (
                                "**Erreur**: Impossible de récupérer le contenu\n\n"
                            )

                        rapport += "---\n\n"

        if not modifications_found:
            rapport += "Aucune modification d'articles trouvée dans cette loi.\n"

        return rapport

    def _clean_html_for_markdown(self, html_content: str) -> str:
        """
        Nettoie le contenu HTML pour un affichage propre en markdown.

        Parameters
        ----------
        html_content : str
            Le contenu HTML à nettoyer.

        Returns
        -------
        str
            Le contenu nettoyé pour markdown.
        """
        if not html_content:
            return ""

        try:
            # Méthode recommandée 2025: BeautifulSoup (optional dependency)
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html_content, "html.parser")

            # Remplacer les éléments HTML par leur équivalent markdown
            for br in soup.find_all("br"):
                br.replace_with(soup.new_string("\n"))

            for p in soup.find_all("p"):
                p.insert_after(soup.new_string("\n\n"))

            for blockquote in soup.find_all("blockquote"):
                blockquote.insert_before(soup.new_string("> "))
                blockquote.insert_after(soup.new_string("\n\n"))

            # Gérer les liens
            from bs4 import Tag

            for a in soup.find_all("a"):
                if isinstance(a, Tag) and a.get("href"):
                    link_text = a.get_text()
                    href = a.get("href")
                    # Convertir en lien markdown
                    a.replace_with(soup.new_string(f"[{link_text}]({href})"))

            text = soup.get_text()

            # Nettoyer les espaces multiples et retours à la ligne excessifs
            import re

            text = re.sub(
                r"\n\s*\n\s*\n", "\n\n", text
            )  # Max 2 retours à la ligne consécutifs
            text = re.sub(r" +", " ", text)  # Espaces multiples -> espace simple

            return text.strip()

        except ImportError:
            # Fallback: regex simple
            import re

            # Remplacer les balises par des équivalents markdown
            text = re.sub(r"<br\s*/?>\s*", "\n", html_content)
            text = re.sub(r"<p[^>]*>\s*", "\n", text)
            text = re.sub(r"</p>\s*", "\n\n", text)
            text = re.sub(r"<blockquote[^>]*>\s*", "\n> ", text)
            text = re.sub(r"</blockquote>\s*", "\n\n", text)

            # Extraire les liens
            text = re.sub(r'<a[^>]*href="([^"]*)"[^>]*>([^<]*)</a>', r"[\2](\1)", text)

            # Supprimer les autres balises HTML
            text = re.sub(r"<[^>]+>", "", text)

            # Nettoyer
            text = re.sub(r"\n\s*\n\s*\n", "\n\n", text)
            text = re.sub(r" +", " ", text)

            return text.strip()

    def to_dict(self) -> Dict[str, Any]:
        """
        Convertit le texte en dictionnaire.

        Returns
        -------
        Dict[str, Any]
            Une représentation du texte sous forme de dictionnaire.
        """
        return self._texte.model_dump()

    def __repr__(self) -> str:
        """Récupère une représentation sous forme de chaîne du texte."""
        return f"TexteLoda(id={self.id}, titre={self.titre})"


class Loda:
    """
    API de haut niveau pour interagir avec les données LODA de l'API Legifrance.
    """

    def __init__(self, client: LegifranceClient):
        """
        Initialise une instance de Loda.

        Parameters
        ----------
        client : LegifranceClient
            Le client pour interagir avec l'API Legifrance.
        """
        self._client = client

    def _extract_date_from_id(self, text_id: str) -> Tuple[str, Optional[str]]:
        """
        Extrait la date d'un identifiant de texte s'il en contient une.

        Parameters
        ----------
        text_id : str
            L'identifiant du texte, potentiellement avec une date (format: LEGITEXT000043987391_01-01-2023).

        Returns
        -------
        Tuple[str, Optional[str]]
            Un tuple contenant l'identifiant de base et la date extraite (ou None si aucune date n'est présente).
        """
        # Guard clause: vérifier si l'ID contient un séparateur de date
        if DATE_SEPARATOR not in text_id:
            return text_id, None

        parts = text_id.split(DATE_SEPARATOR)

        # Guard clause: vérifier si le format est valide (exactement deux parties)
        if len(parts) != 2:
            return text_id, None

        # Extraire l'ID de base et la date
        base_id, date_str = parts

        # Vérifier si la date est au format français (DD-MM-YYYY)
        is_french_date_format = (
            len(date_str) == FRENCH_DATE_FORMAT_LENGTH
            and date_str[2] == DATE_FORMAT_SEPARATOR
            and date_str[5] == DATE_FORMAT_SEPARATOR
        )

        # Si ce n'est pas au format français, utiliser la date telle quelle
        if not is_french_date_format:
            logger.debug(f"Utilisation de la date telle quelle: {date_str}")
            return base_id, date_str

        # Convertir la date du format français (DD-MM-YYYY) au format ISO (YYYY-MM-DD)
        try:
            date_parts = date_str.split(DATE_FORMAT_SEPARATOR)
            day = date_parts[FRENCH_DATE_DAY_POSITION].zfill(2)
            month = date_parts[FRENCH_DATE_MONTH_POSITION].zfill(2)
            year = date_parts[FRENCH_DATE_YEAR_POSITION]

            iso_date = f"{year}-{month}-{day}"
            logger.debug(f"Date convertie de {date_str} à {iso_date}")
            return base_id, iso_date
        except ValueError as e:
            # Si la date n'est pas au format attendu, journaliser l'erreur et l'utiliser telle quelle
            logger.warning(f"Échec d'analyse de la date {date_str}: {e}")
            return base_id, date_str

    def _process_consult_response(
        self, response_data: Dict[str, Any]
    ) -> Optional[TexteLodaModel]:
        """
        Traite une réponse de consultation et extrait le modèle TexteLoda.

        Parameters
        ----------
        response_data : Dict[str, Any]
            Les données JSON de la réponse de l'API.

        Returns
        -------
        Optional[TexteLodaModel]
            Le modèle TexteLoda, ou None si non trouvé.
        """
        # Cas 1: Format d'API ancien avec champ 'texte'
        if "texte" in response_data:
            return self._extract_texte_from_old_format(response_data)

        # Cas 2: Nouveau format d'API (champs au niveau supérieur)
        return self._extract_texte_from_new_format(response_data)

    def _extract_texte_from_old_format(
        self, response_data: Dict[str, Any]
    ) -> Optional[TexteLodaModel]:
        """
        Extrait le modèle TexteLoda à partir du format ancien de l'API (avec champ 'texte').

        Parameters
        ----------
        response_data : Dict[str, Any]
            Les données JSON de la réponse de l'API.

        Returns
        -------
        Optional[TexteLodaModel]
            Le modèle TexteLoda, ou None si non trouvé.
        """

    def _extract_texte_from_new_format(
        self, response_data: Dict[str, Any]
    ) -> Optional[TexteLodaModel]:
        """
        Extrait le modèle TexteLoda à partir du nouveau format de l'API (champs au niveau supérieur).

        Parameters
        ----------
        response_data : Dict[str, Any]
            Les données JSON de la réponse de l'API.

        Returns
        -------
        Optional[TexteLodaModel]
            Le modèle TexteLoda, ou None si non trouvé.
        """
        if "id" not in response_data:
            logger.warning("La réponse ne contient pas le champ 'id' requis")
            return None

        try:
            logger.debug(
                f"Création de TexteLodaModel directement à partir de la réponse avec ID: {response_data['id']}"
            )
            # Create the TexteLodaModel
            texte_model = TexteLodaModel.model_validate(response_data)

            # Create a ConsultTextResponse from the response data and set it as the consult_response
            from pylegifrance.models.generated.model import ConsultTextResponse

            consult_response = ConsultTextResponse.model_validate(response_data)
            texte_model.consult_response = consult_response

            return texte_model
        except Exception as e:
            logger.error(
                f"Échec de création de TexteLodaModel à partir de la réponse: {e}"
            )
            return None

    def fetch(self, text_id: str) -> Optional[TexteLoda]:
        """
        Récupère un texte par son identifiant.

        Parameters
        ----------
        text_id : str
            L'identifiant du texte à récupérer.

        Returns
        -------
        Optional[TexteLoda]
            Le texte, ou None si non trouvé.

        Raises
        ------
        ValueError
            Si text_id est invalide.
        Exception
            Si l'appel API échoue.
        """
        if not text_id:
            raise ValueError("text_id ne peut pas être vide")

        base_id, date = self._extract_date_from_id(text_id)
        logger.debug(
            f"Récupération du texte avec ID: {text_id}, ID de base: {base_id}, date: {date}"
        )

        request = ConsultRequest(textId=base_id, date=date)
        api_model = request.to_api_model().model_dump(by_alias=True)

        # Debug log the consult request
        logger.debug(
            f"Payload de requête de consultation: {json.dumps(api_model, indent=2)}"
        )

        response = self._client.call_api("consult/lawDecree", api_model)

        response_data = response.json()
        logger.debug(
            f"Données de réponse de consultation: {json.dumps(response_data, indent=2, default=str)}"
        )

        texte_model = self._process_consult_response(response_data)

        if not texte_model:
            logger.warning(f"Impossible de traiter la réponse pour le texte {text_id}")
            return None

        logger.debug(
            f"Texte {text_id} récupéré avec succès, titre: {texte_model.titre}"
        )
        return TexteLoda(texte_model, self._client)

    def fetch_version_at(self, text_id: str, date: str) -> Optional[TexteLoda]:
        """
        Récupère une version d'un texte à une date spécifique.

        Parameters
        ----------
        text_id : str
            L'identifiant du texte à récupérer.
        date : str
            La date à laquelle récupérer la version, au format ISO.

        Returns
        -------
        Optional[TexteLoda]
            La version du texte à la date spécifiée, ou None si non trouvée.

        Raises
        ------
        ValueError
            Si text_id ou date est invalide.
        Exception
            Si l'appel API échoue.
        """
        if not text_id:
            raise ValueError("text_id ne peut pas être vide")

        try:
            datetime.fromisoformat(date)
        except ValueError:
            raise ValueError(f"Format de date invalide: {date}")

        request = ConsultVersionRequest(textId=text_id, date=date)
        api_model = request.to_api_model()

        response = self._client.call_api("consult/loda/version", api_model)

        if response.status_code != HTTP_OK:
            return None

        response_data = response.json()
        texte_model = self._process_consult_response(response_data)

        if not texte_model:
            return None

        return TexteLoda(texte_model, self._client)

    def fetch_versions(self, text_id: str) -> List[TexteLoda]:
        """
        Récupère toutes les versions d'un texte.

        Parameters
        ----------
        text_id : str
            L'identifiant du texte dont on veut récupérer les versions.

        Returns
        -------
        List[TexteLoda]
            Une liste d'objets TexteLoda représentant toutes les versions.

        Raises
        ------
        ValueError
            Si text_id est invalide.
        Exception
            Si l'appel API échoue.
        """
        if not text_id:
            raise ValueError("text_id ne peut pas être vide")

        request = ListVersionsRequest(textId=text_id)
        api_model = request.to_api_model()

        response = self._client.call_api("consult/loda/versions", api_model)

        if response.status_code != HTTP_OK:
            return []

        response_data = response.json()

        is_valid_response_format = isinstance(response_data, list)
        if not is_valid_response_format:
            return []

        versions = [
            TexteLoda(texte_model, self._client)
            for version_data in response_data
            if (texte_model := self._process_consult_response(version_data)) is not None
        ]

        return versions

    def _process_search_results(self, response_data: Dict[str, Any]) -> List[TexteLoda]:
        """
        Traite les résultats de recherche de la réponse de l'API.

        Parameters
        ----------
        response_data : Dict[str, Any]
            Les données JSON de la réponse de l'API.

        Returns
        -------
        List[TexteLoda]
            Une liste d'objets TexteLoda extraits de la réponse.
        """
        results_list = self._normalize_search_results_structure(response_data)

        if not results_list:
            return []

        processed_results = [
            texte
            for result in results_list
            if (title_info := self._extract_title_info(result)) is not None
            if (
                texte := self._fetch_and_enrich_text(
                    title_info[0], title_info[1], result
                )
            )
            is not None
        ]

        return processed_results

    def _normalize_search_results_structure(
        self, response_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Normalise la structure des résultats de recherche pour gérer différents formats d'API.

        Parameters
        ----------
        response_data : Dict[str, Any]
            Les données JSON de la réponse de l'API.

        Returns
        -------
        List[Dict[str, Any]]
            Liste normalisée des résultats de recherche.
        """
        # Vérifier si la structure attendue est présente
        has_valid_results = "results" in response_data and isinstance(
            response_data["results"], list
        )

        # Si la structure attendue n'est pas présente, chercher une structure alternative
        if not has_valid_results:
            has_alternative_results = "hits" in response_data and isinstance(
                response_data["hits"], list
            )

            if has_alternative_results:
                logger.debug(
                    "Utilisation de 'hits' au lieu de 'results' pour les résultats de recherche"
                )
                return response_data["hits"]
            else:
                logger.warning(
                    "Aucun résultat valide trouvé dans la réponse de recherche"
                )
                return []

        return response_data["results"]

    def _extract_title_info(self, result: Dict[str, Any]) -> Optional[Tuple[str, str]]:
        """
        Extrait l'ID et le titre d'un résultat de recherche.

        Parameters
        ----------
        result : Dict[str, Any]
            Un résultat de recherche individuel.

        Returns
        -------
        Optional[Tuple[str, str]]
            Un tuple contenant l'ID du texte et son titre, ou None si non trouvé.
        """
        # Vérifier si le résultat a un champ 'titles' valide
        has_valid_titles = (
            "titles" in result
            and result["titles"]
            and isinstance(result["titles"], list)
        )

        if not has_valid_titles:
            return None

        # Chercher le premier titre avec un ID en utilisant next() et une generator expression
        try:
            valid_title = next(
                title for title in result["titles"] if "id" in title and title["id"]
            )
            return valid_title["id"], valid_title.get("title", "")
        except StopIteration:
            return None

    def _fetch_and_enrich_text(
        self, text_id: str, title_text: str, result: Dict[str, Any]
    ) -> Optional[TexteLoda]:
        """
        Récupère un texte par son ID et l'enrichit avec des informations supplémentaires.

        Parameters
        ----------
        text_id : str
            L'ID du texte à récupérer.
        title_text : str
            Le titre du texte extrait des résultats de recherche.
        result : Dict[str, Any]
            Le résultat de recherche complet contenant des informations supplémentaires.

        Returns
        -------
        Optional[TexteLoda]
            Le texte enrichi, ou None en cas d'erreur.
        """
        try:
            texte = self.fetch(text_id)

            # Guard clause: retourner None si le texte n'a pas pu être récupéré
            if not texte:
                logger.warning(
                    f"Échec de récupération du texte {text_id} (a retourné None)"
                )
                return None

            # Enrichir le texte avec le titre si nécessaire
            if texte.titre is None and title_text:
                if texte._texte.consult_response:
                    texte._texte.consult_response.title = title_text

            # Enrichir le texte avec le contenu HTML si nécessaire
            self._enrich_text_with_html_content(texte, result)

            logger.debug(f"Texte {text_id} récupéré et enrichi avec succès")
            return texte

        except Exception as e:
            logger.error(f"Exception lors de la récupération du texte {text_id}: {e}")
            return None

    def _enrich_text_with_html_content(
        self, texte: TexteLoda, result: Dict[str, Any]
    ) -> None:
        """
        Enrichit un texte avec du contenu HTML extrait des sections du résultat de recherche.

        Parameters
        ----------
        texte : TexteLoda
            Le texte à enrichir.
        result : Dict[str, Any]
            Le résultat de recherche contenant les sections avec du contenu HTML.
        """
        needs_html_content = (
            texte.texte_html is None
            and "sections" in result
            and isinstance(result["sections"], list)
        )

        if not needs_html_content:
            return

        extracts = [
            value
            for section in result["sections"]
            if "extracts" in section and isinstance(section["extracts"], list)
            for extract in section["extracts"]
            if "values" in extract and isinstance(extract["values"], list)
            for value in extract["values"]
        ]

        if extracts:
            html_content = " ".join(extracts)
            texte._texte.texte_html = html_content

    def search(self, query: SearchRequest | str) -> List[TexteLoda]:
        """
        Recherche des textes correspondant à la requête.

        Parameters
        ----------
        query : Union[str, SearchRequest]
            La requête de recherche, soit sous forme de chaîne, soit sous forme d'objet SearchRequest.

        Returns
        -------
        List[TexteLoda]
            Une liste d'objets TexteLoda correspondant à la requête.

        Raises
        ------
        ValueError
            Si la requête contient des valeurs invalides (comme une nature non reconnue).
        """
        try:
            search_query = self._normalize_search_query(query)

            # Use the new to_generated_model method
            generated_model = search_query.to_generated_model()

            # If it's a dictionary, use it directly
            if isinstance(generated_model, dict):
                serialized_request = generated_model
            else:
                # Convert the model to a dictionary
                if hasattr(generated_model, "model_dump"):
                    serialized_request = generated_model.model_dump(by_alias=True)
                else:
                    # Fallback for objects without model_dump
                    serialized_request = dict(generated_model)

            # Ensure proper JSON serialization
            serialized_request = json.loads(
                json.dumps(serialized_request, cls=EnumEncoder)
            )

            # Debug log the request
            logger.debug(
                f"Payload de requête de recherche: {json.dumps(serialized_request, indent=2)}"
            )

            # Appeler l'API
            response = self._client.call_api("search", serialized_request)

            if response.status_code != HTTP_OK:
                logger.warning(
                    f"L'API de recherche a retourné un code d'état non-OK: {response.status_code}"
                )
                return []

            response_data = response.json()
            logger.debug(
                f"Données de réponse de recherche: {json.dumps(response_data, indent=2, default=str)}"
            )

            results = self._process_search_results(response_data)
            logger.debug(
                f"Résultats de recherche traités: {len(results)} objets TexteLoda trouvés"
            )

            return results
        except Exception as e:
            # Convert Pydantic validation errors to ValueError for better error handling
            if "not a valid" in str(e):
                raise ValueError(str(e))
            raise

    def _normalize_search_query(
        self, query: Union[str, SearchRequest]
    ) -> SearchRequest:
        """
        Normalise une requête de recherche en objet SearchRequest.

        Parameters
        ----------
        query : Union[str, SearchRequest]
            La requête de recherche, soit sous forme de chaîne, soit sous forme d'objet SearchRequest.

        Returns
        -------
        SearchRequest
            L'objet SearchRequest normalisé.

        Raises
        ------
        ValueError
            Si la requête contient des valeurs invalides (comme une nature non reconnue).
        """
        is_string_query = isinstance(query, str)

        try:
            if is_string_query:
                return SearchRequest(search=query)
            else:
                return query
        except Exception as e:
            # Convert Pydantic validation errors to ValueError for better error handling
            if "not a valid" in str(e):
                raise ValueError(str(e))
            raise
