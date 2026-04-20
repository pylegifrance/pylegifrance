"""Search request model for the KALI fond."""

from datetime import datetime

from pydantic import Field, ValidationInfo, field_validator

from pylegifrance.models.base import PyLegifranceBaseModel
from pylegifrance.models.generated.model import (
    ChampDTO,
    CritereDTO,
    DatePeriod,
    FiltreDTO,
    Fond,
    Operateur,
    RechercheSpecifiqueDTO,
    SearchRequestDTO,
    TypeChamp,
    TypePagination,
    TypeRecherche,
)
from pylegifrance.models.kali.enum import FacettesKALI, SortKali, TypeChampKali

EN_VIGUEUR_STATUSES: list[str] = [
    "VIGUEUR",
    "VIGUEUR_ETEN",
    "VIGUEUR_NON_ETEN",
]


class SearchRequest(PyLegifranceBaseModel):
    """Requête de recherche dans le fond KALI (conventions collectives)."""

    search: str = Field("", description="Texte ou mots-clés à rechercher")
    field: TypeChampKali = Field(default=TypeChampKali.ALL)
    search_type: TypeRecherche = Field(
        default=TypeRecherche.tous_les_mots_dans_un_champ
    )
    sort: SortKali = Field(default=SortKali.PERTINENCE)
    page_size: int = Field(default=10, ge=1, le=100)
    page_number: int = Field(default=1, ge=1)

    idcc: str | None = Field(
        default=None,
        description="Filtre par numéro IDCC (ex: '1261').",
    )
    legal_status: list[str] | None = Field(
        default_factory=lambda: list(EN_VIGUEUR_STATUSES),
        description=(
            "Filtre par état juridique du texte. Par défaut restreint aux "
            "conventions 'en vigueur' (VIGUEUR, VIGUEUR_ETEN, "
            "VIGUEUR_NON_ETEN). Passer une liste vide ou ``None`` pour "
            "désactiver le filtre."
        ),
    )
    date_signature_start: str | None = Field(
        default=None, description="Début de plage — date de signature (YYYY-MM-DD)."
    )
    date_signature_end: str | None = Field(
        default=None, description="Fin de plage — date de signature (YYYY-MM-DD)."
    )

    @field_validator("date_signature_start", "date_signature_end")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        if v is not None:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError(
                    f"Date must be in ISO format (YYYY-MM-DD), got: {v}"
                ) from None
        return v

    @field_validator("date_signature_end")
    @classmethod
    def validate_date_range(cls, v: str | None, info: ValidationInfo) -> str | None:
        start = info.data.get("date_signature_start")
        if v is not None and start is not None:
            if datetime.fromisoformat(v) < datetime.fromisoformat(start):
                raise ValueError("date_signature_end must be >= date_signature_start")
        return v

    def to_api_model(self) -> SearchRequestDTO:
        """Convert to the generated API DTO."""
        criteria = CritereDTO(
            valeur=self.search,
            operateur=Operateur.et,
            typeRecherche=self.search_type,
            proximite=None,
            criteres=None,
        )
        champ = ChampDTO(
            criteres=[criteria],
            operateur=Operateur.et,
            typeChamp=TypeChamp(self.field.value),
        )

        filtres: list[FiltreDTO] = []
        if self.idcc is not None:
            filtres.append(
                FiltreDTO(
                    facette=FacettesKALI.IDCC.value,
                    valeurs=[self.idcc],
                    dates=None,
                    singleDate=None,
                    multiValeurs=None,
                )
            )
        if self.legal_status:
            filtres.append(
                FiltreDTO(
                    facette=FacettesKALI.LEGAL_STATUS.value,
                    valeurs=self.legal_status,
                    dates=None,
                    singleDate=None,
                    multiValeurs=None,
                )
            )
        if self.date_signature_start and self.date_signature_end:
            filtres.append(
                FiltreDTO(
                    facette=FacettesKALI.DATE_SIGNATURE.value,
                    valeurs=None,
                    dates=DatePeriod(
                        start=datetime.fromisoformat(self.date_signature_start),
                        end=datetime.fromisoformat(self.date_signature_end),
                    ),
                    singleDate=None,
                    multiValeurs=None,
                )
            )

        recherche = RechercheSpecifiqueDTO(
            champs=[champ],
            filtres=filtres,
            pageNumber=self.page_number,
            pageSize=self.page_size,
            sort=self.sort.value,
            fromAdvancedRecherche=False,
            secondSort="ID",
            typePagination=TypePagination.defaut,
            operateur=Operateur.et,
        )
        return SearchRequestDTO(recherche=recherche, fond=Fond.kali)
