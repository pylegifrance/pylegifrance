from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field, field_validator

from pylegifrance.models.base import PyLegifranceBaseModel
from pylegifrance.models.generated.model import (
    ConsultArticle,
    ConsultSection,
    ConsultTextResponse,
)


def _first_of(data: dict, *keys: str) -> Any:
    """Return first non-None value found for the given keys.

    Args:
        data: Dictionary to search in.
        *keys: Keys to look up in priority order.

    Returns:
        The first non-None value, or None if all are missing/None.
    """
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None


def _to_dict(data: Any) -> dict:
    """Normalize any input to a plain dict.

    Args:
        data: A dict, Pydantic model, or arbitrary object.

    Returns:
        A plain dictionary representation of the input.
    """
    if isinstance(data, dict):
        return data
    if hasattr(data, "model_dump"):
        return data.model_dump()
    return vars(data) if hasattr(data, "__dict__") else {}


def _extract_code_name(
    article_data: dict,
    raw_data: dict,
) -> str | None:
    """Extract the code name from article or raw response data.

    Tries multiple locations in priority order to find the code name,
    covering both consult and search response shapes.

    Args:
        article_data: Normalized article-level dict (nested or top-level).
        raw_data: The full top-level response dict.

    Returns:
        The code name string, or None if not found.
    """
    # 1. consult: textTitles list
    text_titles = article_data.get("textTitles")
    if isinstance(text_titles, list):
        for title in text_titles:
            titre = title.get("titre") if isinstance(title, dict) else None
            if titre is not None:
                return titre

    # 2-4. consult: context block inside article_data
    context = article_data.get("context")
    if isinstance(context, dict):
        titre_txt_list = context.get("titreTxt")
        if isinstance(titre_txt_list, list) and titre_txt_list:
            first = titre_txt_list[0]
            if isinstance(first, dict) and first.get("titre") is not None:
                return first["titre"]
        if context.get("titreCode") is not None:
            return context["titreCode"]
        if context.get("titre") is not None:
            return context["titre"]

    # 5. top-level contexte fallback
    contexte = raw_data.get("contexte")
    if isinstance(contexte, dict):
        if contexte.get("titreCode") is not None:
            return contexte["titreCode"]
        if contexte.get("titre") is not None:
            return contexte["titre"]

    # 6. direct top-level keys
    for key in ("titreCode", "codeTitle", "nomCode"):
        if raw_data.get(key) is not None:
            return raw_data[key]

    # 7. top-level context.titreTxt
    top_context = raw_data.get("context")
    if isinstance(top_context, dict):
        titre_txt_list = top_context.get("titreTxt")
        if isinstance(titre_txt_list, list) and titre_txt_list:
            first = titre_txt_list[0]
            if isinstance(first, dict) and first.get("titre") is not None:
                return first["titre"]

    # 8. search: titles list with nature == "CODE"
    titles = raw_data.get("titles")
    if isinstance(titles, list):
        for t in titles:
            if (
                isinstance(t, dict)
                and t.get("nature") == "CODE"
                and t.get("title") is not None
            ):
                return t["title"]

    return None


class Code(PyLegifranceBaseModel):
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

    id: str | None = Field(
        default=None,
        description="Identifiant unique LEGITEXT du code",
        examples=["LEGITEXT000006070721"],
    )
    cid: str | None = Field(
        default=None,
        description="Identifiant chronologique du code",
        examples=["LEGITEXT000006070721"],
    )
    title: str | None = Field(
        default=None,
        description="Titre officiel du code",
        examples=["Code civil", "Code pénal"],
    )
    etat: str | None = Field(
        default=None,
        description="Statut juridique actuel du code",
        examples=["VIGUEUR", "ABROGE"],
    )
    sections: list[ConsultSection] | None = Field(
        default=None,
        description="Liste des sections de premier niveau du code",
    )
    articles: list[ConsultArticle] | None = Field(
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
            for title in data_dict.titles:
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


class Article(PyLegifranceBaseModel):
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
    title: str | None = Field(
        None,
        alias="titre",
        description="Titre ou intitulé de l'article",
        examples=["Des lois en général"],
    )
    content: str | None = Field(
        None, alias="texte", description="Contenu textuel brut de l'article"
    )
    content_html: str | None = Field(
        None, alias="texteHtml", description="Contenu HTML formaté avec balises légales"
    )
    cid: str | None = Field(
        None,
        description="Identifiant LEGITEXT du code parent",
        examples=["LEGITEXT000006070721"],
    )
    code_name: str | None = Field(
        None,
        description="Nom officiel du code juridique parent",
        examples=["Code civil", "Code pénal"],
    )
    version_date: datetime | None = Field(
        None,
        alias="dateVersion",
        description="Date de version de l'article (auto-parsée depuis timestamp ou ISO)",
    )
    legal_status: str | None = Field(
        None,
        alias="etatJuridique",
        description="Statut juridique actuel de l'article",
        examples=["VIGUEUR", "ABROGE", "TRANSFERE"],
    )
    url: str | None = Field(
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

        Gère les réponses de consultation (clé ``article`` imbriquée) et les
        réponses de recherche (dict plat) de manière transparente.

        Args:
            data: Dictionnaire, modèle Pydantic ou réponse API.

        Returns:
            Une nouvelle instance d'Article.
        """
        raw_data = _to_dict(data)

        # Consult shape: nested "article" dict; Search shape: flat top-level
        nested = raw_data.get("article")
        if nested and isinstance(nested, dict):
            article_data = nested
        else:
            article_data = raw_data

        # --- Declarative field extraction ---
        num = _first_of(article_data, "num", "numero")
        titre = _first_of(
            article_data, "titre", "sectionParentTitre", "fullSectionsTitre"
        )
        texte = _first_of(article_data, "texte", "contenu", "content")
        if texte is None:
            values = article_data.get("values") or raw_data.get("values")
            if isinstance(values, list) and values:
                texte = " ".join(values)

        texte_html = article_data.get("texteHtml")
        cid = article_data.get("cid") or raw_data.get("cid")

        etat = _first_of(
            article_data,
            "etatJuridique",
            "etatText",
            "etat",
            "legalStatus",
        ) or _first_of(raw_data, "etatJuridique", "etatText", "etat", "legalStatus")

        date_version = _first_of(
            article_data, "dateVersion", "dateDebut", "date"
        ) or _first_of(raw_data, "dateVersion", "date")

        code_name = _extract_code_name(article_data, raw_data)

        # --- Build mapped dict using model field names ---
        article_id = article_data.get("id") or raw_data.get("id") or "unknown"

        mapped_data: dict[str, Any] = {
            "id": article_id,
            "number": num or "unknown",
        }
        if titre is not None:
            mapped_data["title"] = titre
        if texte is not None:
            mapped_data["content"] = texte
        if texte_html is not None:
            mapped_data["content_html"] = texte_html
        if cid is not None:
            mapped_data["cid"] = cid
        if code_name is not None:
            mapped_data["code_name"] = code_name
        if date_version is not None:
            mapped_data["version_date"] = date_version
        if etat is not None:
            mapped_data["legal_status"] = etat

        # --- URL generation ---
        url = article_data.get("url") or raw_data.get("url")
        if url is None and article_id != "unknown":
            url = f"https://www.legifrance.gouv.fr/codes/article_lc/{article_id}"
        elif url is None and cid is not None:
            url = f"https://www.legifrance.gouv.fr/codes/section_lc/{cid}"
        if url is not None:
            mapped_data["url"] = url

        return cls(**mapped_data)
