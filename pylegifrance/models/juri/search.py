"""Search models and functionality for JURI."""

from typing import List, Optional
from pydantic import Field, validator
from datetime import datetime

from pylegifrance.models.base import PyLegifranceBaseModel
from pylegifrance.models.juri.constants import (
    SortOptions,
    PublicationStatus,
    FacettesJURI,
)
from pylegifrance.models.generated.model import (
    SearchRequestDTO,
    RechercheSpecifiqueDTO,
    ChampDTO,
    CritereDTO,
    FiltreDTO,
    TypePagination,
    Operateur,
    TypeChamp,
    TypeRecherche,
    Fond,
    DatePeriod
)


class SearchRequest(PyLegifranceBaseModel):
    """JURI search request model."""

    search: str = Field("", description="Search text or keywords")
    publication_bulletin: Optional[List[PublicationStatus]] = Field(
        default=None, description="Publication status filter"
    )
    sort: SortOptions = Field(default=SortOptions.RELEVANCE)
    field: TypeChamp = Field(default=TypeChamp.all)
    search_type: TypeRecherche = Field(default=TypeRecherche.un_des_mots)
    page_size: int = Field(default=5, ge=1, le=100)
    page_number: int = Field(default=1, ge=1)

    # Advanced options
    formatter: bool = Field(default=True, description="Extract only specific fields")
    fetch_all: bool = Field(default=False, description="Fetch all results")
    keys: Optional[List[str]] = Field(
        default=None, description="Specific field extraction keys"
    )
    juridiction_judiciaire: Optional[List[str]] = Field(default=None)
    
    date_start: Optional[str] = Field(
        default=None, 
        description="Start date for decision filtering (ISO format: YYYY-MM-DD)"
    )
    date_end: Optional[str] = Field(
        default=None, 
        description="End date for decision filtering (ISO format: YYYY-MM-DD)"
    )
    date_facet: str = Field(
        default="DATE_DECISION", 
        description="Date facet to filter on (DATE_DECISION, DATE_PUBLI, etc.)"
    )
    
    formation: Optional[List[str]] = Field(
        default=None, 
        description="Formation filter (e.g., 'Chambre sociale', 'Première chambre civile', 'Chambre criminelle')"
    )
    
    cour_appel: Optional[List[str]] = Field(
        default=None, 
        description="Court of appeal location filter (only for 'Juridictions d'appel')"
    )
    
    @validator('date_start', 'date_end')
    def validate_date_format(cls, v):
        """Validate date format is ISO YYYY-MM-DD."""
        if v is not None:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError(f"Date must be in ISO format (YYYY-MM-DD), got: {v}")
        return v

    @validator('date_end')
    def validate_date_range(cls, v, values):
        """Validate that end date is after start date."""
        if v is not None and 'date_start' in values and values['date_start'] is not None:
            start_date = datetime.fromisoformat(values['date_start'])
            end_date = datetime.fromisoformat(v)
            if end_date < start_date:
                raise ValueError("End date must be after start date")
        return v

    def to_api_model(self) -> SearchRequestDTO:
        """Convert to generated model for API calls."""
        criteria = self._create_criteria()
        field = self._create_field(criteria)
        filters = self._create_filters()
        search_spec = self._create_search_specification(field, filters)

        return SearchRequestDTO(recherche=search_spec, fond=Fond.juri)

    def _create_criteria(self) -> CritereDTO:
        """Create search criteria from the search text."""
        return CritereDTO(
            valeur=self.search,
            operateur=Operateur.et,
            typeRecherche=self.search_type,
            proximite=None,
            criteres=None,
        )

    def _create_field(self, criteria: CritereDTO) -> ChampDTO:
        """Create search field with the given criteria."""
        return ChampDTO(
            criteres=[criteria], operateur=Operateur.et, typeChamp=self.field
        )

    def _create_filters(self) -> List[FiltreDTO]:
        """Create filters based on search parameters."""
        filters = []

        # Add publication bulletin filter if specified
        if self.publication_bulletin:
            filters.append(self._create_publication_filter())

        # Add jurisdiction judiciaire filter if specified
        if self.juridiction_judiciaire:
            filters.append(self._create_jurisdiction_filter())
            
        # Add date filter if specified
        if self.date_start and self.date_end:
            filters.append(self._create_date_filter())
            
        # Add formation filter if specified
        if self.formation:
            filters.append(self._create_formation_filter())
        
        # Add court of appeal filter if specified  
        if self.cour_appel and self.juridiction_judiciaire and "Juridictions d'appel" in self.juridiction_judiciaire:
            filters.append(self._create_cour_appel_filter())

        return filters

    def _create_publication_filter(self) -> FiltreDTO:
        """Create publication bulletin filter."""
        # Ensure publication_bulletin is not None before using it as an iterable
        pub_values = []
        if self.publication_bulletin:
            pub_values = [p.value for p in self.publication_bulletin]

        return FiltreDTO(
            facette=FacettesJURI.CASSATION_TYPE_PUBLICATION_BULLETIN.value,
            valeurs=pub_values,
            dates=None,
            singleDate=None,
            multiValeurs=None,
        )

    def _create_jurisdiction_filter(self) -> FiltreDTO:
        """Create jurisdiction filter."""
        return FiltreDTO(
            facette=FacettesJURI.JURIDICTION_JUDICIAIRE.value,
            valeurs=self.juridiction_judiciaire,
            dates=None,
            singleDate=None,
            multiValeurs=None,
        )
    
    def _create_date_filter(self) -> FiltreDTO:
        """Create date range filter."""
        return FiltreDTO(
            facette=self.date_facet,
            valeurs=None,
            dates=DatePeriod(
                start=datetime.fromisoformat(self.date_start),
                end=datetime.fromisoformat(self.date_end)
            ),
            singleDate=None,
            multiValeurs=None,
        )
    
    def _create_formation_filter(self) -> FiltreDTO:
        """Create formation filter."""
        return FiltreDTO(
            facette=FacettesJURI.CASSATION_FORMATION.value,
            valeurs=self.formation,
            dates=None,
            singleDate=None,
            multiValeurs=None,
        )
    
    def _create_cour_appel_filter(self) -> FiltreDTO:
        return FiltreDTO(
            facette=FacettesJURI.APPEL_SIEGE_APPEL.value,
            valeurs=self.cour_appel,
            dates=None,
            singleDate=None,
            multiValeurs=None,
        )

    def _create_search_specification(
        self, field: ChampDTO, filters: List[FiltreDTO]
    ) -> RechercheSpecifiqueDTO:
        """Create search specification with fields and filters."""
        return RechercheSpecifiqueDTO(
            champs=[field],
            filtres=filters,
            pageNumber=self.page_number,
            pageSize=self.page_size,
            sort=self.sort.value,
            fromAdvancedRecherche=False,
            secondSort="ID",
            typePagination=TypePagination.defaut,
            operateur=Operateur.et,
        )


class SearchResponse(PyLegifranceBaseModel):
    """JURI search response model."""

    total_results: int = Field(alias="totalNbResult")
    execution_time: int = Field(alias="executionTime")
    results: List[dict] = Field(default=[])
    page_number: int = Field(alias="pageNumber")
    page_size: int = Field(alias="pageSize")
