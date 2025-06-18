from typing import Optional, Any, List
from datetime import datetime
from pydantic import Field, field_validator, ConfigDict, BaseModel

from pylegifrance.models.generated.model import (
    ConsultTextResponse,
    ConsultSection,
    ConsultArticle,
)


class Code(BaseModel):
    """Code juridique français avec contenu complet et métadonnées.

    Représente un code juridique français tel que retourné par l'API Légifrance.
    Un code est une collection de tous les textes (lois + décrets) dans un domaine juridique.

    Args:
        id: Identifiant unique LEGITEXT du code dans la base Légifrance.
        cid: Identifiant chronologique du code.
        title: Titre officiel du code (ex: "Code civil").
        etat: Statut juridique actuel (ex: "VIGUEUR", "ABROGE").
        sections: Liste des sections de premier niveau du code.
        articles: Liste des articles racine du code.

    Class Methods:
        from_orm: Crée une instance de Code à partir d'une réponse de l'API.

    Examples:
        Code civil:
            >>> code = Code(
            ...     id="LEGITEXT000006070721",
            ...     title="Code civil",
            ...     etat="VIGUEUR"
            ... )

    Note:
        - Un code est structuré hiérarchiquement en sections et articles
        - Les sections peuvent contenir d'autres sections (sous-sections) et des articles
        - Les articles sont les unités de base contenant le texte juridique
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    id: Optional[str] = Field(
        default=None,
        description="Identifiant unique LEGITEXT du code",
        examples=["LEGITEXT000006070721"],
    )
    cid: Optional[str] = Field(
        default=None,
        description="Identifiant chronologique du code",
        examples=["LEGITEXT000006070721"],
    )
    title: Optional[str] = Field(
        default=None,
        description="Titre officiel du code",
        examples=["Code civil", "Code pénal"],
    )
    etat: Optional[str] = Field(
        default=None,
        description="Statut juridique actuel du code",
        examples=["VIGUEUR", "ABROGE"],
    )
    sections: Optional[List[ConsultSection]] = Field(
        default=None,
        description="Liste des sections de premier niveau du code",
    )
    articles: Optional[List[ConsultArticle]] = Field(
        default=None,
        description="Liste des articles racine du code",
    )

    @classmethod
    def from_orm(cls, data: ConsultTextResponse) -> "Code":
        """Crée une instance de Code à partir d'une réponse de l'API.

        Args:
            data: Réponse de l'API contenant les données du code.

        Returns:
            Code: Une nouvelle instance de Code.
        """
        # Handle both Pydantic model and dictionary inputs
        if hasattr(data, "model_dump"):
            data_dict = data.model_dump()
        elif isinstance(data, dict):
            data_dict = data
        else:
            # Try to convert to dict if it's a JSON response
            try:
                data_dict = data.model_dump_json()
            except (AttributeError, ValueError):
                # If all else fails, try to access attributes directly
                return cls(
                    id=getattr(data, "id", None),
                    cid=getattr(data, "cid", None),
                    title=getattr(data, "title", None),
                    etat=getattr(data, "etat", None),
                    sections=getattr(data, "sections", None),
                    articles=getattr(data, "articles", None),
                )

        code_data = {
            "id": getattr(data_dict, "id", None),
            "cid": getattr(data_dict, "cid", None),
            "title": getattr(data_dict, "title", None),
            "etat": getattr(data_dict, "etat", None),
            "sections": getattr(data_dict, "sections", None),
            "articles": getattr(data_dict, "articles", None),
        }

        if "titles" in data_dict and getattr(data_dict, "titles", None):
            for title in getattr(data_dict, "titles"):
                title_cid = (
                    getattr(title, "cid", None)
                    if hasattr(title, "cid")
                    else title.get("cid")
                    if isinstance(title, dict)
                    else None
                )
                if title_cid and title_cid.startswith("LEGITEXT"):
                    code_data["cid"] = title_cid
                    break

        # Create and return the Code instance
        return cls(**code_data)


class Article(BaseModel):
    """Article juridique français avec contenu complet et métadonnées.

    Représente un article de loi, de code ou de règlement français tel que retourné
    par l'API Légifrance. Inclut le contenu textuel, les métadonnées de versioning
    et les informations de rattachement au code parent.

    Args:
        id: Identifiant unique LEGIARTI de l'article dans la base Légifrance.
        number: Numéro officiel de l'article (ex: "L36-11", "R123-4").
        title: Titre ou intitulé de l'article (optionnel).
        content: Contenu textuel brut de l'article.
        content_html: Contenu HTML formaté de l'article.
        cid: Identifiant LEGITEXT du code parent (optionnel).
        code_name: Nom officiel du code parent (ex: "Code civil").
        version_date: Date de version de l'article (timestamp Unix ou ISO).
        legal_status: Statut juridique actuel (ex: "VIGUEUR", "ABROGE").
        url: URL de consultation sur le site Légifrance.

    Class Methods:
        from_orm: Crée une instance d'Article à partir d'un dictionnaire.

    Examples:
        Article du Code civil:
            >>> article = Article(
            ...     id="LEGIARTI000006419292",
            ...     number="1",
            ...     title="Des lois en général",
            ...     content="Les lois et, lorsqu'ils sont publiés...",
            ...     code_name="Code civil",
            ...     version_date=1577836800000,  # timestamp
            ...     legal_status="VIGUEUR"
            ... )
            >>> article.format_citation()
            'Code civil, art. 1 (version du 01/01/2020)'

        Parsing automatique des dates:
            >>> # Timestamp Unix (millisecondes)
            >>> article = Article(id="123", number="L1", version_date=1577836800000)
            >>> # String ISO
            >>> article = Article(id="123", number="L1", version_date="2020-01-01T00:00:00")
            >>> # Les deux sont automatiquement converties en datetime

        Citation formatée:
            >>> citation = article.format_citation()
            >>> print(citation)  # "Code civil, art. 1 (version du 01/01/2020)"

    Note:
        - Les alias permettent la compatibilité avec l'API Légifrance (num→number, etc.)
        - Les dates sont automatiquement parsées depuis timestamp Unix ou format ISO
        - Le champ legal_status indique si l'article est en vigueur, abrogé, etc.
        - L'URL pointe vers la consultation officielle sur legifrance.gouv.fr

    See Also:
        Code: Classe représentant un code juridique complet
        SearchResult: Résultat de recherche contenant des références d'articles
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    id: str = Field(
        description="Identifiant unique LEGIARTI de l'article",
        examples=["LEGIARTI000006419292"],
    )
    number: str = Field(
        alias="num",
        description="Numéro officiel de l'article",
        examples=["1", "L36-11", "R123-4"],
    )
    title: Optional[str] = Field(
        None,
        alias="titre",
        description="Titre ou intitulé de l'article",
        examples=["Des lois en général"],
    )
    content: Optional[str] = Field(
        None, alias="texte", description="Contenu textuel brut de l'article"
    )
    content_html: Optional[str] = Field(
        None, alias="texteHtml", description="Contenu HTML formaté avec balises légales"
    )
    cid: Optional[str] = Field(
        None,
        alias="cid",
        description="Identifiant LEGITEXT du code parent",
        examples=["LEGITEXT000006070721"],
    )
    code_name: Optional[str] = Field(
        None,
        alias="codeName",
        description="Nom officiel du code juridique parent",
        examples=["Code civil", "Code pénal"],
    )
    version_date: Optional[datetime] = Field(
        None,
        alias="dateVersion",
        description="Date de version de l'article (auto-parsée depuis timestamp ou ISO)",
    )
    legal_status: Optional[str] = Field(
        None,
        alias="etatJuridique",
        description="Statut juridique actuel de l'article",
        examples=["VIGUEUR", "ABROGE", "TRANSFERE"],
    )
    url: Optional[str] = Field(
        None,
        description="URL de consultation officielle sur Légifrance",
        examples=[
            "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006419292"
        ],
    )

    @classmethod
    @field_validator("version_date", mode="before")
    def parse_date(cls, v):
        """Parse date depuis divers formats (timestamp Unix, ISO string, datetime).

        Args:
            v: Date au format timestamp Unix (ms), string ISO, ou datetime.

        Returns:
            datetime: Date parsée ou None si valeur vide.

        Note:
            Les timestamps Unix sont attendus en millisecondes (format API Légifrance).
        """
        if v is None:
            return None
        if isinstance(v, str):
            return datetime.fromisoformat(v)
        if isinstance(v, (int, float)):
            # Timestamp en millisecondes (format API Légifrance)
            return datetime.fromtimestamp(v / 1000)
        return v

    def format_citation(self) -> str:
        """Formate une citation juridique standardisée de l'article.

        Returns:
            str: Citation au format "Code, art. numéro (version du JJ/MM/AAAA)".

        Examples:
            >>> article.format_citation()
            'Code civil, art. L36-11 (version du 01/01/2020)'

            >>> # Article sans code parent
            >>> article.format_citation()
            'art. 123'
        """
        parts = []
        if self.code_name:
            parts.append(self.code_name)
        if self.number:
            parts.append(f"art. {self.number}")
        if self.version_date:
            parts.append(f"(version du {self.version_date.strftime('%d/%m/%Y')})")
        return ", ".join(parts)

    @classmethod
    def from_orm(cls, data: Any) -> "Article":
        """Crée une instance d'Article à partir d'un dictionnaire ou d'une réponse API.

        Cette méthode permet de convertir les données brutes de l'API en objet Article
        en gérant les différences de nommage entre l'API et le modèle, ainsi que les
        différentes structures de réponse possibles.

        Args:
            data: Dictionnaire, objet Pydantic ou réponse API contenant les données de l'article.

        Returns:
            Article: Une nouvelle instance d'Article.
        """
        # Convert to dictionary if needed
        if hasattr(data, "model_dump"):
            data_dict = data.model_dump()
        elif isinstance(data, dict):
            data_dict = data
        else:
            # Try to convert to dict if it's a JSON response
            try:
                data_dict = data.json()
            except (AttributeError, ValueError):
                # If all else fails, try to access attributes directly
                data_dict = {}
                for attr in [
                    "id",
                    "num",
                    "titre",
                    "texte",
                    "texteHtml",
                    "cid",
                    "codeName",
                    "dateVersion",
                    "etatJuridique",
                    "url",
                ]:
                    if hasattr(data, attr):
                        data_dict[attr] = getattr(data, attr)

        # Extract article data from nested structures if needed
        article_data = {}

        # Check if we have a response with an 'article' field
        if "article" in data_dict and data_dict["article"]:
            article_obj = data_dict["article"]

            # Extract article number
            if "num" in article_obj:
                article_data["num"] = article_obj["num"]
            elif "numero" in article_obj:
                article_data["num"] = article_obj["numero"]

            # Extract article title
            if "titre" in article_obj:
                article_data["titre"] = article_obj["titre"]
            elif (
                "sectionParentTitre" in article_obj
                and article_obj["sectionParentTitre"]
            ):
                article_data["titre"] = article_obj["sectionParentTitre"]
            elif (
                "fullSectionsTitre" in article_obj and article_obj["fullSectionsTitre"]
            ):
                article_data["titre"] = article_obj["fullSectionsTitre"]

            # Extract article content
            if "texte" in article_obj:
                article_data["texte"] = article_obj["texte"]
            elif "contenu" in article_obj:
                article_data["texte"] = article_obj["contenu"]
            elif "content" in article_obj:
                article_data["texte"] = article_obj["content"]

            # Extract HTML content
            if "texteHtml" in article_obj:
                article_data["texteHtml"] = article_obj["texteHtml"]

            # Extract code information
            if "cid" in article_obj:
                article_data["cid"] = article_obj["cid"]

            # Extract legal status
            if "etatJuridique" in article_obj:
                article_data["etatJuridique"] = article_obj["etatJuridique"]
            elif "etatText" in article_obj:
                article_data["etatJuridique"] = article_obj["etatText"]
            elif "etat" in article_obj:
                article_data["etatJuridique"] = article_obj["etat"]

            # Extract version date
            if "dateVersion" in article_obj:
                article_data["dateVersion"] = article_obj["dateVersion"]
            elif "date" in article_obj:
                article_data["dateVersion"] = article_obj["date"]

            # Check for textTitles field to extract code name
            if "textTitles" in article_obj and article_obj["textTitles"]:
                text_titles = article_obj["textTitles"]
                if isinstance(text_titles, list) and len(text_titles) > 0:
                    for title in text_titles:
                        # Handle both dictionary and Pydantic model access
                        if hasattr(title, "titre"):
                            article_data["codeName"] = title.titre
                            break
                        elif isinstance(title, dict) and "titre" in title:
                            article_data["codeName"] = title["titre"]
                            break

            # Check for context field in article to extract code name
            if "context" in article_obj and article_obj["context"]:
                context = article_obj["context"]
                # Handle both dictionary and Pydantic model access
                if hasattr(context, "titreCode") and context.titreCode is not None:
                    article_data["codeName"] = context.titreCode
                elif (
                    isinstance(context, dict)
                    and "titreCode" in context
                    and context["titreCode"] is not None
                ):
                    article_data["codeName"] = context["titreCode"]
                elif (
                    hasattr(context, "titre")
                    and getattr(context, "titre", None) is not None
                ):
                    article_data["codeName"] = getattr(context, "titre")
                elif (
                    isinstance(context, dict)
                    and "titre" in context
                    and context["titre"] is not None
                ):
                    article_data["codeName"] = context["titre"]
        else:
            # Use the top-level data if no 'article' field
            article_data = data_dict

        # Extract code name from context if available
        if (
            "codeName" not in article_data
            and "contexte" in data_dict
            and data_dict["contexte"]
        ):
            context = data_dict["contexte"]

            # Extract code name from title - handle both dictionary and Pydantic model access
            if hasattr(context, "titreCode") and context.titreCode is not None:
                article_data["codeName"] = context.titreCode
            elif (
                isinstance(context, dict)
                and "titreCode" in context
                and context["titreCode"] is not None
            ):
                article_data["codeName"] = context["titreCode"]
            elif (
                hasattr(context, "titre")
                and getattr(context, "titre", None) is not None
            ):
                article_data["codeName"] = getattr(context, "titre")
            elif (
                isinstance(context, dict)
                and "titre" in context
                and context["titre"] is not None
            ):
                article_data["codeName"] = context["titre"]

        if "codeName" not in article_data:
            if "titreCode" in data_dict:
                article_data["codeName"] = data_dict["titreCode"]
            elif "codeTitle" in data_dict:
                article_data["codeName"] = data_dict["codeTitle"]
            elif "nomCode" in data_dict:
                article_data["codeName"] = data_dict["nomCode"]

        # Extract code_name from context.titreTxt if available (original logic)
        if (
            "codeName" not in article_data
            and "context" in data_dict
            and data_dict["context"] is not None
        ):
            context = data_dict["context"]
            # Handle both dictionary and Pydantic model access for titreTxt
            titre_txt_list = None
            if hasattr(context, "titreTxt") and context.titreTxt:
                titre_txt_list = context.titreTxt
            elif (
                isinstance(context, dict)
                and "titreTxt" in context
                and context["titreTxt"]
            ):
                titre_txt_list = context["titreTxt"]

            if titre_txt_list and len(titre_txt_list) > 0:
                titre_txt = titre_txt_list[0]
                # Handle both dictionary and Pydantic model access
                if hasattr(titre_txt, "titre") and titre_txt.titre is not None:
                    article_data["codeName"] = titre_txt.titre
                elif (
                    isinstance(titre_txt, dict)
                    and "titre" in titre_txt
                    and titre_txt["titre"] is not None
                ):
                    article_data["codeName"] = titre_txt["titre"]

        # Extract legal status from top-level if not found in article
        if "etatJuridique" not in article_data:
            if "etatJuridique" in data_dict:
                article_data["etatJuridique"] = data_dict["etatJuridique"]
            elif "etatText" in data_dict:
                article_data["etatJuridique"] = data_dict["etatText"]
            elif "etat" in data_dict:
                article_data["etatJuridique"] = data_dict["etat"]

        # Extract version date from top-level if not found in article
        if "dateVersion" not in article_data:
            if "dateVersion" in data_dict:
                article_data["dateVersion"] = data_dict["dateVersion"]
            elif "date" in data_dict:
                article_data["dateVersion"] = data_dict["date"]

        # Map API field names to model field names
        field_mapping = {
            "id": "id",
            "num": "number",
            "titre": "title",
            "texte": "content",
            "texteHtml": "content_html",
            "cid": "cid",
            "codeName": "code_name",
            "dateVersion": "version_date",
            "etatJuridique": "legal_status",
            "url": "url",
            "etat": "legal_status",  # Some API responses use etat instead of etatJuridique
            "legalStatus": "legal_status",  # Some API responses use legalStatus instead of etatJuridique
            "numero": "number",  # Some API responses use numero instead of num
            "sectionParentTitre": "title",  # Use section title if article title is missing
        }

        # Create a new dict with mapped field names
        mapped_data = {}
        for api_field, model_field in field_mapping.items():
            if api_field in article_data and article_data[api_field] is not None:
                mapped_data[model_field] = article_data[api_field]

        # Add URL if we have an ID but no URL
        if (
            "id" in mapped_data
            and "url" not in mapped_data
            and mapped_data["id"] != "unknown"
        ):
            mapped_data["url"] = (
                f"https://www.legifrance.gouv.fr/codes/article_lc/{mapped_data['id']}"
            )

        # Add URL based on CID if we have a CID but no URL
        elif (
            "cid" in mapped_data
            and "url" not in mapped_data
            and mapped_data["cid"] is not None
        ):
            mapped_data["url"] = (
                f"https://www.legifrance.gouv.fr/codes/section_lc/{mapped_data['cid']}"
            )

        # Ensure required fields have default values if missing
        if "id" not in mapped_data:
            mapped_data["id"] = "unknown"
        if "number" not in mapped_data:
            mapped_data["number"] = "unknown"

        # Create and return the Article instance
        return cls(**mapped_data)
