from pydantic import BaseModel, ConfigDict, Field


class BookCandidate(BaseModel):
    """Represents one book returned by semantic retrieval."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1)
    document: str = Field(min_length=1)
    distance: float | None = None
