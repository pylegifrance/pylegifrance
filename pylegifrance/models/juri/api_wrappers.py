"""API wrapper models for JURI."""

from pydantic import Field

from pylegifrance.models.base import PyLegifranceBaseModel
from pylegifrance.models.generated.model import (
    JuriConsultRequest,
    JuriConsultWithAncienId,
    TexteSimple,
)


class ConsultRequest(PyLegifranceBaseModel):
    """Request to consult a JURI text."""

    searched_string: str | None = Field(
        None, alias="searchedString", description="Search text that led to consultation"
    )
    text_id: str = Field(..., alias="textId", description="Text identifier")

    def to_api_model(self) -> JuriConsultRequest:
        """Convert to generated model for API calls."""
        return JuriConsultRequest(**self.model_dump(by_alias=True))


class ConsultByAncienIdRequest(PyLegifranceBaseModel):
    """Request to consult by ancien ID."""

    ancien_id: str | None = Field(
        None, alias="ancienId", description="Legacy ID for JURI text consultation"
    )

    def to_api_model(self) -> JuriConsultWithAncienId:
        """Convert to generated model for API calls."""
        return JuriConsultWithAncienId(**self.model_dump(by_alias=True))


class ConsultResponse(PyLegifranceBaseModel):
    """Response from text consultation."""

    text: TexteSimple | None = Field(None, description="Text content")
    execution_time: int | None = Field(None, alias="executionTime")
    dereferenced: bool | None = Field(None, description="Indexable by robots")

    @classmethod
    def from_api_model(cls, model) -> "ConsultResponse":
        """Create from generated model or dictionary.

        Args:
            model: The model or dictionary to convert from.

        Returns:
            The converted response.
        """
        if isinstance(model, dict):
            return cls(**model)
        else:
            return cls(**model.model_dump())
