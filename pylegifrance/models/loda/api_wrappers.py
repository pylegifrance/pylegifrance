from typing import Any

from pylegifrance.models.base import PyLegifranceBaseModel
from pylegifrance.models.generated.model import (
    ConsultDateRequest as GeneratedConsultVersionRequest,
)
from pylegifrance.models.generated.model import (
    LawDecreeConsultRequest as GeneratedConsultRequest,
)


class ConsultRequest(PyLegifranceBaseModel):
    """
    Request model for consulting a LODA text.

    This model is compatible with LawDecreeConsultRequest from the generated model.
    """

    text_id: str
    searched_string: str | None = None
    date: str | None = None
    from_suggest: bool | None = None

    def to_api_model(self) -> GeneratedConsultRequest:
        """Convert to API model format.

        Returns:
            The API model.
        """
        # Use the current date if not provided
        date = self.date or "2023-01-01"  # Default date

        return GeneratedConsultRequest(
            textId=self.text_id,
            searchedString=self.searched_string,
            date=date,
            fromSuggest=self.from_suggest,
        )


class ConsultResponse(PyLegifranceBaseModel):
    """
    Response model for consulting a LODA text.

    This model is compatible with ConsultTextResponse from the generated model.
    """

    text: dict[str, Any] | None = None
    execution_time: int | None = None
    dereferenced: bool | None = None

    @classmethod
    def from_api_model(cls, data: dict[str, Any]) -> "ConsultResponse":
        """Create a ConsultResponse from API response data.

        Args:
            data: The API response data.

        Returns:
            The ConsultResponse object.
        """
        # Handle old API format (with 'texte' field)
        if "texte" in data:
            return cls(
                text=data.get("texte"),
                executionTime=data.get("executionTime"),
                dereferenced=data.get("dereferenced"),
            )

        # Handle new API format (fields at top level)
        # For backward compatibility, we'll create a dictionary with the expected structure
        if "id" in data:
            from pylegifrance.models.loda.models import TexteLoda

            text_model = TexteLoda.model_validate(data)
            return cls(
                text=text_model.model_dump(),
                executionTime=data.get("executionTime"),
                dereferenced=data.get("dereferenced"),
            )

        # Default case
        return cls(
            text=None,
            executionTime=data.get("executionTime"),
            dereferenced=data.get("dereferenced"),
        )


class ConsultVersionRequest(PyLegifranceBaseModel):
    """
    Request model for consulting a specific version of a LODA text.

    This model is compatible with ConsultDateRequest from the generated model.
    """

    text_id: str
    date: str

    def to_api_model(self) -> dict[str, Any]:
        """Convert to API model format.

        Returns:
            The API model as a dictionary.
        """
        # Parse the date string to extract year, month, and day
        from datetime import datetime

        date_obj = datetime.strptime(self.date, "%Y-%m-%d")

        # Create a ConsultDateRequest with the correct parameters
        request = GeneratedConsultVersionRequest(
            year=date_obj.year, month=date_obj.month, dayOfMonth=date_obj.day
        )

        # Add textId to the dictionary manually since it's not a parameter of ConsultDateRequest
        result = request.model_dump(by_alias=True)
        result["textId"] = self.text_id

        # Convert to dictionary
        return result


class ListVersionsRequest(PyLegifranceBaseModel):
    """
    Request model for listing versions of a LODA text.
    """

    text_id: str

    def to_api_model(self) -> dict[str, Any]:
        """Convert to API model format.

        Returns:
            The API model as a dictionary.
        """
        return {"textId": self.text_id}
