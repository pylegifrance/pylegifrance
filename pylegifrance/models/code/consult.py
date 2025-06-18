from pylegifrance.models.generated.model import (
    CodeConsultRequest as _CodeConsultRequest,
)
from pylegifrance.models.generated.model import (
    ConsultTextResponse as _ConsultTextResponse,
)


class CodeConsultRequest(_CodeConsultRequest):
    """Requête de consultation d'un texte de code juridique français.

    Permet de récupérer le contenu complet d'un texte de code à partir de son
    identifiant technique et de sa date de version. Utilisée avec l'endpoint
    POST /consult/code de l'API Légifrance.

    Args:
        textid: Identifiant technique chronique du texte (LEGITEXT).
        date: Date de consultation au format ISO (YYYY-MM-DD).
        abrogated: Inclure les textes abrogés dans la consultation.
        searchedstring: Texte de recherche pour mise en évidence dans le résultat.
        fromsuggest: Indique si la requête provient d'une suggestion.
        setcid: Identifiant chronique de section spécifique à consulter.

    Examples:
        Consultation d'un code complet:
            >>> request = CodeConsultRequest(
            ...     textId="LEGITEXT000006075116",  # Code civil
            ...     date="2021-04-15"
            ... )

        Consultation avec recherche mise en évidence:
            >>> request = CodeConsultRequest(
            ...     textId="LEGITEXT000006075116",
            ...     date="2021-04-15",
            ...     searchedstring="constitution 1958"
            ... )

        Consultation d'une section spécifique:
            >>> request = CodeConsultRequest(
            ...     textId="LEGITEXT000006075116",
            ...     date="2021-04-15",
            ...     setcid="LEGISCTA000006112861"
            ... )

        Inclure les textes abrogés:
            >>> request = CodeConsultRequest(
            ...     textId="LEGITEXT000006075116",
            ...     date="2021-04-15",
            ...     abrogated=True
            ... )

    Note:
        - textid et date sont obligatoires pour toute consultation
        - setcid est optionnel et permet de cibler une section précise
        - searchedstring permet la mise en évidence de termes dans le résultat
        - abrogated=True inclut les parties abrogées du code

    See Also:
        Article: Modèle pour les articles retournés par la consultation
        SearchRequestDTO: Pour les recherches avant consultation
    """


class CodeConsultResponse(_ConsultTextResponse):
    pass
