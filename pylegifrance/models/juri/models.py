"""Core domain models for JURI."""

from pydantic import Field

from pylegifrance.models.generated.model import TexteLien, TexteSimple


class Decision(TexteSimple):
    """
    Judicial decision domain model.

    Extends the generated TexteSimple model with JURI-specific fields.
    """

    siege_appel: str | None = Field(alias="siegeAppel", default=None)
    avocat_general: str | None = Field(alias="avocatGl", default=None)
    liens: list[TexteLien] = Field(default=[])
