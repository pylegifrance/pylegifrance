from pydantic import BaseModel


class DecisionShort(BaseModel):
    """A Judilibre decision as returned by ``/search`` (summary fields only)."""

    id: str
    jurisdiction: str | None = None
    chamber: str | None = None
    number: str | None = None
    numbers: list[str] | None = None
    ecli: str | None = None
    formation: str | None = None
    publication: list[str] | None = None
    decision_date: str | None = None
    type: str | None = None
    solution: str | None = None
    summary: str | None = None
    themes: list[str] | None = None
    files: list[dict] | None = None


class DecisionFull(DecisionShort):
    """A Judilibre decision as returned by ``/decision`` (full content)."""

    text: str | None = None
    update_date: str | None = None
    visa: list[dict] | None = None
