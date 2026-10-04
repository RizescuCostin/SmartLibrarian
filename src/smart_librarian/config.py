from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, ConfigDict, Field

from smart_librarian.exceptions import ConfigurationError

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseModel):
    """Validated application configuration."""

    model_config = ConfigDict(frozen=True)

    openai_api_key: str = Field(repr=False)
    openai_chat_model: str
    openai_embedding_model: str = "text-embedding-3-small"

    chroma_persist_directory: Path = Path("storage/chroma")
    chroma_collection_name: str = "book_summaries"

    app_env: str = "development"
    log_level: str = "INFO"


def _optional_environment_value(name: str) -> str | None:
    """Return a stripped environment value, or None when it is empty."""

    import os

    value = os.getenv(name)

    if value is None:
        return None

    value = value.strip()
    return value or None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and validate settings once for the current process."""

    import os

    load_dotenv(ENV_FILE)

    api_key = _optional_environment_value("OPENAI_API_KEY")

    chat_model = _optional_environment_value("OPENAI_CHAT_MODEL")

    if chat_model is None:
        raise ConfigurationError(
            "OPENAI_CHAT_MODEL is missing. Add a chat model to your .env file."
        )

    if api_key is None:
        raise ConfigurationError(
            "OPENAI_API_KEY is missing. Copy .env.example to .env and add your API key."
        )

    persist_directory_value = os.getenv(
        "CHROMA_PERSIST_DIRECTORY",
        "storage/chroma",
    ).strip()

    persist_directory = Path(persist_directory_value)

    if not persist_directory.is_absolute():
        persist_directory = PROJECT_ROOT / persist_directory

    return Settings(
        openai_api_key=api_key,
        openai_chat_model=chat_model,
        openai_embedding_model=os.getenv(
            "OPENAI_EMBEDDING_MODEL",
            "text-embedding-3-small",
        ).strip(),
        chroma_persist_directory=persist_directory,
        chroma_collection_name=os.getenv(
            "CHROMA_COLLECTION_NAME",
            "book_summaries",
        ).strip(),
        app_env=os.getenv("APP_ENV", "development").strip(),
        log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
    )
