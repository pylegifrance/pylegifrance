"""Filter models for JURI search."""

from pydantic import Field

from pylegifrance.models.base import PyLegifranceBaseModel
from pylegifrance.models.juri.constants import (
    CoursAppel,
    FilterTypes,
    FormationsJudiciaires,
    JuridictionJudiciaire,
    PublicationStatus,
)


class BaseFilter(PyLegifranceBaseModel):
    """Base filter with common structure."""

    facette: FilterTypes
    valeurs: list[str]


class JurisdictionFilter(BaseFilter):
    """Filter for judicial jurisdictions."""

    facette: FilterTypes = FilterTypes.JURIDICTION_JUDICIAIRE
    valeurs: list[JuridictionJudiciaire]


class FormationFilter(BaseFilter):
    """Filter for judicial formations."""

    facette: FilterTypes = FilterTypes.FORMATION
    valeurs: list[FormationsJudiciaires]


class CourAppelFilter(BaseFilter):
    """Filter for appeal courts."""

    facette: FilterTypes = FilterTypes.COUR_APPEL
    valeurs: list[CoursAppel]


class PublicationFilter(BaseFilter):
    """Filter for publication status."""

    facette: FilterTypes = FilterTypes.PUBLICATION_BULLETIN
    valeurs: list[PublicationStatus] = Field(default=[PublicationStatus.PUBLISHED])
