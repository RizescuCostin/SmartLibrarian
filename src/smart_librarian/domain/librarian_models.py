from pydantic import BaseModel, ConfigDict, Field


class LibrarianAnswer(BaseModel):
    """Represents the final Smart Librarian response."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1)
    reason: str = Field(min_length=1)
    summary: str = Field(min_length=1)
