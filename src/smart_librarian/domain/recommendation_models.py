from pydantic import BaseModel, ConfigDict, Field


class BookRecommendation(BaseModel):
    """Represents one model-selected book recommendation."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1)
    reason: str = Field(min_length=1)
