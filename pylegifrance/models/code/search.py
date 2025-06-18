from typing import List, Literal, Union, Optional, Any, Dict
from datetime import datetime

from pydantic import Field, BaseModel, model_validator, ConfigDict

# Import from your existing modules
from pylegifrance.models.constants import (
    Facette,
    Fond,
    Operateur,
    TypeRecherche,
    EtatJuridique,
)
from pylegifrance.models.generated.model import (
    FiltreDTO,
    RechercheSpecifiqueDTO,
    SearchRequestDTO,
    ChampDTO,
    CritereDTO,
    TypePagination,
    TypeChamp,
)
from .enum import TypeChampCode, SortCode, NomCode


class DateVersionFiltre(BaseModel):
    """Filtre par date de version pour rechercher dans une version historique.

    Utilisé avec CODE_DATE pour récupérer des articles à une date spécifique.

    Args:
        facette: Facette DATE_VERSION (non modifiable)
        single_date: Date cible en timestamp Unix (millisecondes) ou datetime

    Examples:
        >>> # Recherche au 1er janvier 2018
        >>> filtre = DateVersionFiltre(single_date=1514802418000)

        >>> # Avec datetime
        >>> from datetime import datetime
        >>> filtre = DateVersionFiltre(
        ...     single_date=datetime(2018, 1, 1)
        ... )
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    facette: Literal[Facette.DATE_VERSION] = Field(
        default=Facette.DATE_VERSION,
        frozen=True,
        description="Facette de filtrage par date de version",
    )
    single_date: datetime = Field(
        ...,
        alias="singleDate",
        description="Date de version (timestamp Unix en ms ou datetime)",
    )

    def to_generated(self) -> FiltreDTO:
        """Convertit vers le DTO pour l'API."""
        return FiltreDTO(
            facette=self.facette.value,
            singleDate=self.single_date,
            dates=None,
            valeurs=None,
            multiValeurs=None,
        )


class NomCodeFiltre(BaseModel):
    """Filtre de recherche par nom de code juridique.

    Permet de restreindre une recherche à un ou plusieurs codes juridiques
    spécifiques en utilisant la facette NOM_CODE de l'API Légifrance.

    Attributes:
        facette: Type de facette utilisé (toujours NOM_CODE pour ce filtre).
        valeurs: Liste des codes juridiques à inclure dans la recherche.

    Methods:
        to_generated: Convertit le filtre vers un FiltreDTO pour l'API.

    Examples:
        >>> # Recherche dans le Code civil uniquement
        >>> filtre = NomCodeFiltre(valeurs=[NomCode.CC])

        >>> # Recherche dans plusieurs codes
        >>> filtre = NomCodeFiltre(
        ...     valeurs=[NomCode.CC, NomCode.CPD, NomCode.CDPEDCE]
        ... )

        >>> # Conversion pour l'API
        >>> filtre_dto = filtre.to_generated()
        >>> print(filtre_dto.facette)
        'NOM_CODE'
        >>> print(filtre_dto.valeurs)
        ['Code civil', 'Code pénal', 'Code des postes et des communications électroniques']

    Note:
        La facette est fixée à NOM_CODE et ne doit pas être modifiée.
        Les valeurs acceptées sont définies dans l'énumération NomCode
        qui contient tous les codes juridiques français reconnus.

    See Also:
        NomCode: Énumération des codes juridiques disponibles.
        FiltreDTO: Objet de transfert pour l'API Légifrance.
    """

    facette: Facette = Field(
        default=Facette.NOM_CODE,
        frozen=True,
        description="Facette de filtrage par nom de code (non modifiable)",
    )
    valeurs: List[NomCode] = Field(
        ...,
        description="Codes juridiques ciblés pour la recherche",
        examples=[[NomCode.CC], [NomCode.CC, NomCode.CPD, NomCode.CDPEDCE]],
        min_length=1,
    )

    def to_generated(self) -> FiltreDTO:
        """Convertit le filtre vers un objet DTO pour l'API.

        Returns:
            FiltreDTO: Objet de transfert avec les valeurs converties
                en chaînes de caractères pour l'API Légifrance.
        """
        return FiltreDTO(
            facette=self.facette.value,
            valeurs=[valeur.value for valeur in self.valeurs],
            dates=None,
            singleDate=None,
            multiValeurs=None,
        )


class TextLegalStatusFiltre(BaseModel):
    """Filtre par statut juridique pour CODE_ETAT.

    Permet de filtrer les textes selon leur statut juridique actuel
    (en vigueur, abrogé, etc.).

    Args:
        facette: Facette TEXT_LEGAL_STATUS (non modifiable)
        valeur: Statut juridique recherché

    Examples:
        >>> # Recherche des textes en vigueur
        >>> filtre = TextLegalStatusFiltre(valeur="VIGUEUR")

        >>> # Recherche des textes abrogés
        >>> filtre = TextLegalStatusFiltre(valeur="ABROGE")
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    facette: Facette = Field(
        default=Facette.TEXT_LEGAL_STATUS,
        frozen=True,
        description="Facette de filtrage par statut juridique",
    )
    valeurs: List[EtatJuridique] = Field(
        default=[EtatJuridique.VIGUEUR], description="Statut juridique du texte"
    )

    def to_generated(self) -> FiltreDTO:
        """Convertit vers le DTO pour l'API."""
        return FiltreDTO(
            facette=self.facette.value,
            valeurs=[valeur.value for valeur in self.valeurs],
            dates=None,
            singleDate=None,
            multiValeurs=None,
        )


class CritereCode(BaseModel):
    """Critère de recherche pour les codes juridiques.

    Définit un critère de recherche textuelle avec ses paramètres.

    Args:
        type_recherche: Type de recherche à effectuer
        valeur: Mot(s) ou expression à rechercher
        operateur: Opérateur logique (ET/OU)
        proximite: Distance maximale entre les mots (optionnel)
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    type_recherche: TypeRecherche = Field(
        ..., alias="typeRecherche", description="Type de recherche effectuée"
    )
    valeur: str = Field(..., description="Mot(s)/expression recherchés", min_length=1)
    operateur: Operateur = Field(default=Operateur.ET, description="Opérateur logique")
    proximite: Optional[int] = Field(
        None, ge=1, le=100, description="Distance maximale entre les mots"
    )

    def to_generated(self) -> CritereDTO:
        """Convertit vers le DTO pour l'API."""
        data = {
            "typeRecherche": TypeRecherche(self.type_recherche.value),
            "valeur": self.valeur,
            "operateur": self.operateur.value,
        }
        if self.proximite is not None:
            data["proximite"] = self.proximite
        return CritereDTO(**data)


class ChampCode(BaseModel):
    """Champ de recherche pour le fond CODE.

    Args:
        type_champ: Type de champ sur lequel effectuer la recherche
        criteres: Liste des critères de recherche
        operateur: Opérateur entre les critères
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    type_champ: TypeChampCode = Field(
        default=TypeChampCode.ALL,
        alias="typeChamp",
        description="Type de champ de recherche",
    )
    criteres: List[CritereCode] = Field(
        ..., min_length=1, description="Critères de recherche pour ce champ"
    )
    operateur: Operateur = Field(
        default=Operateur.ET, description="Opérateur entre les critères"
    )

    def to_generated(self) -> ChampDTO:
        """Convertit vers le DTO pour l'API."""
        return ChampDTO(
            typeChamp=TypeChamp(self.type_champ.value),
            criteres=[c.to_generated() for c in self.criteres],
            operateur=self.operateur.to_generated(),
        )


class CodeSearchCriteria(BaseModel):
    """Critères de recherche complets pour les codes juridiques.

    Regroupe tous les paramètres de recherche pour CODE_DATE et CODE_ETAT.
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    champs: List[ChampCode] = Field(
        default_factory=list, description="Champs de recherche avec leurs critères"
    )
    filtres: List[Union[NomCodeFiltre, DateVersionFiltre, TextLegalStatusFiltre]] = (
        Field(default_factory=list, description="Filtres à appliquer à la recherche")
    )
    page_number: int = Field(
        default=1, ge=1, alias="pageNumber", description="Numéro de page (commence à 1)"
    )
    page_size: int = Field(
        default=5,
        ge=1,
        le=100,
        alias="pageSize",
        description="Nombre d'éléments par page",
    )
    operateur: Operateur = Field(
        default=Operateur.ET, description="Opérateur logique global"
    )
    sort: SortCode = Field(
        default=SortCode.PERTINENCE, description="Critère de tri des résultats"
    )
    type_pagination: TypePagination = Field(
        default=TypePagination.defaut,
        alias="typePagination",
        description="Type de pagination à utiliser",
    )

    def to_generated(self) -> RechercheSpecifiqueDTO:
        """Convertit vers le DTO pour l'API."""
        return RechercheSpecifiqueDTO(
            champs=[c.to_generated() for c in self.champs],
            filtres=[f.to_generated() for f in self.filtres],
            pageNumber=self.page_number,
            pageSize=self.page_size,
            operateur=self.operateur.to_generated(),
            sort=self.sort.value,
            typePagination=self.type_pagination,
            fromAdvancedRecherche=None,
            secondSort=None,
        )


class CodeDateSearchRequest(SearchRequestDTO):
    """Requête de recherche dans CODE_DATE (versions historiques).

    Recherche des articles de codes à une date donnée.

    Examples:
        >>> # Article L36-11 du code des postes au 1er janvier 2018
        >>> request = CodeDateSearchRequest(
        ...     recherche=CodeSearchCriteria(
        ...         champs=[
        ...             ChampCode(
        ...                 type_champ=TypeChampCode.NUM_ARTICLE,
        ...                 criteres=[
        ...                     CritereCode(
        ...                         type_recherche=TypeRecherche.EXACTE,
        ...                         valeur="L36-11"
        ...                     )
        ...                 ]
        ...             )
        ...         ],
        ...         filtres=[
        ...             NomCodeFiltre(
        ...                 valeurs=[NomCode.CDPEDCE]
        ...             ),
        ...             DateVersionFiltre(
        ...                 single_date=datetime(2018, 1, 1)
        ...             )
        ...         ]
        ...     )
        ... )
    """

    fond: Literal[Fond.CODE_DATE] = Field(
        default=Fond.CODE_DATE,
        frozen=True,
        description="Recherche par date dans les codes",
    )
    recherche: CodeSearchCriteria = Field(..., description="Critères de recherche")

    @model_validator(mode="after")
    def validate_date_filter(self) -> "CodeDateSearchRequest":
        """Vérifie qu'un filtre de date est présent pour CODE_DATE."""
        has_date_filter = any(
            isinstance(f, DateVersionFiltre) for f in self.recherche.filtres
        )
        if not has_date_filter:
            raise ValueError("CODE_DATE nécessite un filtre DateVersionFiltre")
        return self


class CodeEtatSearchRequest(SearchRequestDTO):
    """Requête de recherche dans CODE_ETAT (état actuel).

    Recherche des articles de codes selon leur état juridique actuel.

    Examples:
        >>> # Articles en vigueur du Code civil
        >>> request = CodeEtatSearchRequest(
        ...     recherche=CodeSearchCriteria(
        ...         champs=[
        ...             ChampCode(
        ...                 type_champ=TypeChampCode.ALL,
        ...                 criteres=[
        ...                     CritereCode(
        ...                         type_recherche=TypeRecherche.UN_DES_MOTS,
        ...                         valeur="propriété possession"
        ...                     )
        ...                 ]
        ...             )
        ...         ],
        ...         filtres=[
        ...             NomCodeFiltre(valeurs=[NomCode.CC]),
        ...             TextLegalStatusFiltre(valeur="VIGUEUR")
        ...         ]
        ...     )
        ... )
    """

    fond: Literal[Fond.CODE_ETAT] = Field(
        default=Fond.CODE_ETAT,
        frozen=True,
        description="Recherche par état juridique dans les codes",
    )
    recherche: CodeSearchCriteria = Field(..., description="Critères de recherche")


class CodeSearchResponse(BaseModel):
    """Réponse de recherche dans les codes juridiques.

    Contient les résultats de recherche avec pagination et métadonnées.
    """

    model_config = ConfigDict(validate_by_name=True, validate_by_alias=True)

    results: List[Dict[str, Any]] = Field(
        default_factory=list, description="Liste des résultats de recherche"
    )
    total_results: int = Field(
        0, alias="totalResults", description="Nombre total de résultats"
    )
    page_number: int = Field(1, alias="pageNumber", description="Numéro de page actuel")
    page_size: int = Field(
        10, alias="pageSize", description="Nombre de résultats par page"
    )
    facets: Optional[Dict[str, List[Dict[str, Any]]]] = Field(
        None, description="Facettes de filtrage disponibles"
    )

    @property
    def total_pages(self) -> int:
        """Calcule le nombre total de pages."""
        if self.page_size == 0:
            return 0
        return (self.total_results + self.page_size - 1) // self.page_size

    @property
    def has_next_page(self) -> bool:
        """Indique s'il y a une page suivante."""
        return self.page_number < self.total_pages

    @property
    def has_previous_page(self) -> bool:
        """Indique s'il y a une page précédente."""
        return self.page_number > 1
