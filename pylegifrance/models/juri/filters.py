"""Filter models for JURI search."""

from collections.abc import Sequence

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
    valeurs: Sequence[str]


class JurisdictionFilter(BaseFilter):
    """Filter for judicial jurisdictions."""

    facette: FilterTypes = FilterTypes.JURIDICTION_JUDICIAIRE
    # Narrower than BaseFilter.valeurs (Sequence[str]) by design — these
    # subclasses exist specifically to constrain which values are valid
    # per facette. pydantic validates this at construction time; nothing
    # in this codebase mutates .valeurs post-construction (only iterated).
    valeurs: Sequence[JuridictionJudiciaire]  # pyright: ignore[reportIncompatibleVariableOverride]  # ty: ignore[incompatible-mutable-override]


class FormationFilter(BaseFilter):
    """Filter for judicial formations."""

    facette: FilterTypes = FilterTypes.FORMATION
    valeurs: Sequence[FormationsJudiciaires]  # pyright: ignore[reportIncompatibleVariableOverride]  # ty: ignore[incompatible-mutable-override]


class CourAppelFilter(BaseFilter):
    """Filter for appeal courts."""

    facette: FilterTypes = FilterTypes.COUR_APPEL
    valeurs: Sequence[CoursAppel]  # pyright: ignore[reportIncompatibleVariableOverride]  # ty: ignore[incompatible-mutable-override]


class PublicationFilter(BaseFilter):
    """Filter for publication status."""

    facette: FilterTypes = FilterTypes.PUBLICATION_BULLETIN
    valeurs: Sequence[PublicationStatus] = Field(  # pyright: ignore[reportIncompatibleVariableOverride]  # ty: ignore[incompatible-mutable-override]
        default=[PublicationStatus.PUBLISHED]
    )
