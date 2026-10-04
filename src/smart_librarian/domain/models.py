from pydantic import BaseModel, ConfigDict, Field, field_validator


class Book(BaseModel):
    """Represents one book in the local dataset."""

    model_config = ConfigDict(frozen=True)

    title: str = Field(min_length=1)
    short_summary: str = Field(min_length=1)
    full_summary: str = Field(min_length=1)
    themes: list[str] = Field(default_factory=list)
    genres: list[str] = Field(default_factory=list)

    @field_validator("title", "short_summary", "full_summary")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        """Reject empty text and remove surrounding whitespace."""

        cleaned_value = value.strip()

        if not cleaned_value:
            raise ValueError("must not be empty")

        return cleaned_value

    @field_validator("themes", "genres")
    @classmethod
    def clean_string_lists(cls, values: list[str]) -> list[str]:
        """Remove blank entries and surrounding whitespace."""

        cleaned_values = []

        for value in values:
            cleaned_value = value.strip()

            if cleaned_value:
                cleaned_values.append(cleaned_value)

        return cleaned_values
