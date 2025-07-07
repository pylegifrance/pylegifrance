from datetime import datetime
from enum import Enum
from typing import List, Dict, Any

from pydantic import BaseModel

from pylegifrance.models.generated.model import (
    TypeRecherche,
    Operateur,
    Fond,
    CritereDTO,
    ChampDTO,
    FiltreDTO,
    TypeChamp,
    TypePagination,
    RechercheSpecifiqueDTO,
    SearchRequestDTO,
    DatePeriod,
    Nature2 as Nature,
    Sort1 as Sort,
)


class SearchRequest(BaseModel):
    """
    Model for constructing LODA search requests.
    """

    search: str | None = None
    text_id: str | None = None
    champ: TypeChamp | None = TypeChamp.all
    type_recherche: TypeRecherche | None = TypeRecherche.tous_les_mots_dans_un_champ
    fond: Fond = Fond.loda_date
    natures: List[Nature] | List[str] = []
    date_signature: DatePeriod | str | None = None
    date_publication: DatePeriod | str | None = None
    page_number: int = 1
    page_size: int = 10

    def __init__(self, **data):
        """
        Initialize the SearchRequest with validation for nature values.

        Raises
        ------
        ValueError
            If an invalid nature value is provided.
        """
        # Validate nature values before initializing
        if "natures" in data and data["natures"]:
            valid_values = [n.value for n in Nature]
            for nature in data["natures"]:
                if isinstance(nature, str) and nature not in valid_values:
                    raise ValueError(
                        f"'{nature}' is not a valid Nature. Valid values are: {valid_values}"
                    )

        super().__init__(**data)

    def to_generated_model(self) -> Dict[str, Any]:
        """
        Convert to the generated model format.

        Returns
        -------
        Dict[str, Any]
            A dictionary representation of the search request.
        """
        # Always use the SearchRequestDTO for consistency
        # Simple list requests don't work well with search terms

        # Create fields for search criteria
        fields = []

        # Add text_id field if provided
        if self.text_id:
            critere_text = [
                CritereDTO(
                    valeur=self.text_id,
                    typeRecherche=TypeRecherche.exacte,
                    operateur=Operateur.et,
                    proximite=None,
                    criteres=None,
                )
            ]
            fields.append(
                ChampDTO(
                    typeChamp=TypeChamp.num,
                    criteres=critere_text,
                    operateur=Operateur.et,
                )
            )

        # Add search field if provided
        if self.search:
            # For search terms, try different search types for better results
            # Create multiple search fields to increase chances of finding matches

            # Search in ALL fields with TOUS_LES_MOTS_DANS_UN_CHAMP
            fields.append(
                ChampDTO(
                    typeChamp=TypeChamp.all,
                    criteres=[
                        CritereDTO(
                            valeur=self.search,
                            typeRecherche=TypeRecherche.tous_les_mots_dans_un_champ,
                            operateur=Operateur.et,
                            proximite=None,
                            criteres=None,
                        )
                    ],
                    operateur=Operateur.et,
                )
            )

            # Also search in TEXTE field with UN_DES_MOTS
            fields.append(
                ChampDTO(
                    typeChamp=TypeChamp.texte,
                    criteres=[
                        CritereDTO(
                            valeur=self.search,
                            typeRecherche=TypeRecherche.un_des_mots,
                            operateur=Operateur.et,
                            proximite=None,
                            criteres=None,
                        )
                    ],
                    operateur=Operateur.ou,  # Use OR between this field and others
                )
            )

            # Also search in TITLE field with UN_DES_MOTS
            fields.append(
                ChampDTO(
                    typeChamp=TypeChamp.title,
                    criteres=[
                        CritereDTO(
                            valeur=self.search,
                            typeRecherche=TypeRecherche.un_des_mots,
                            operateur=Operateur.et,
                            proximite=None,
                            criteres=None,
                        )
                    ],
                    operateur=Operateur.ou,  # Use OR between this field and others
                )
            )

        # If no fields, create a default field that will match all
        if not fields:
            criteres = [
                CritereDTO(
                    valeur=" ",
                    typeRecherche=TypeRecherche.exacte,
                    operateur=Operateur.et,
                    proximite=None,
                    criteres=None,
                )
            ]
            fields.append(
                ChampDTO(
                    typeChamp=TypeChamp.title,
                    criteres=criteres,
                    operateur=Operateur.et,
                )
            )

        filters = []

        # Always add date version filter
        filters.append(
            FiltreDTO(
                facette="DATE_VERSION",
                singleDate=datetime.now(),
                dates=None,
                valeurs=None,
                multiValeurs=None,
            )
        )

        # Always add legal status filters
        filters.append(
            FiltreDTO(
                facette="TEXT_LEGAL_STATUS",
                valeurs=["VIGUEUR"],
                dates=None,
                singleDate=None,
                multiValeurs=None,
            )
        )
        filters.append(
            FiltreDTO(
                facette="ARTICLE_LEGAL_STATUS",
                valeurs=["VIGUEUR"],
                dates=None,
                singleDate=None,
                multiValeurs=None,
            )
        )

        # Add nature filter if specified
        if self.natures:
            nature_values = [
                n.value if isinstance(n, Enum) else str(n) for n in self.natures
            ]

            filters.append(
                FiltreDTO(
                    facette="NATURE",
                    valeurs=nature_values,
                    dates=None,
                    singleDate=None,
                    multiValeurs=None,
                )
            )

        # Add date signature filter if specified
        if self.date_signature:
            date_sig_period = self.date_signature
            if isinstance(date_sig_period, str):
                date_sig_period = DatePeriod(
                    start=datetime.fromisoformat(date_sig_period),
                    end=datetime.fromisoformat(date_sig_period),
                )
            filters.append(
                FiltreDTO(
                    facette="DATE_SIGNATURE",
                    dates=date_sig_period,
                    valeurs=None,
                    singleDate=None,
                    multiValeurs=None,
                )
            )

        # Add date publication filter if specified
        if self.date_publication:
            date_pub_period = self.date_publication
            if isinstance(date_pub_period, str):
                date_pub_period = DatePeriod(
                    start=datetime.fromisoformat(date_pub_period),
                    end=datetime.fromisoformat(date_pub_period),
                )
            filters.append(
                FiltreDTO(
                    facette="DATE_PUBLICATION",
                    dates=date_pub_period,
                    valeurs=None,
                    singleDate=None,
                    multiValeurs=None,
                )
            )

        # Create the RechercheSpecifiqueDTO
        recherche = RechercheSpecifiqueDTO(
            champs=fields,
            filtres=filters,
            pageNumber=self.page_number,
            pageSize=self.page_size,
            sort=Sort.publication_date_desc.value,
            operateur=Operateur.et,
            typePagination=TypePagination.defaut,
            fromAdvancedRecherche=None,
            secondSort=None,
        )

        # For LODA_ETAT, ensure we're using legal status filters
        if self.fond == Fond.loda_etat:
            # Make sure we have legal status filters
            has_legal_status_filter = any(
                f.facette == "TEXT_LEGAL_STATUS" for f in filters
            )
            if not has_legal_status_filter:
                filters.append(
                    FiltreDTO(
                        facette="TEXT_LEGAL_STATUS",
                        valeurs=["VIGUEUR"],
                        dates=None,
                        singleDate=None,
                        multiValeurs=None,
                    )
                )

        # Create the final SearchRequestDTO
        recherche_final = SearchRequestDTO(recherche=recherche, fond=self.fond)

        # Return as a dictionary
        return recherche_final.model_dump(by_alias=True)
