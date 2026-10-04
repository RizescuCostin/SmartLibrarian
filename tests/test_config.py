from pathlib import Path

import pytest

from smart_librarian.config import get_settings
from smart_librarian.exceptions import ConfigurationError


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    """Ensure each test reloads configuration independently."""

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_settings_are_loaded_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENAI_EMBEDDING_MODEL", "test-embedding-model")
    monkeypatch.setenv("CHROMA_COLLECTION_NAME", "test-books")
    monkeypatch.setenv("CHROMA_PERSIST_DIRECTORY", "storage/test-chroma")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv(
        "OPENAI_CHAT_MODEL",
        "test-chat-model",
    )

    settings = get_settings()

    assert settings.openai_api_key == "test-api-key"
    assert settings.openai_embedding_model == "test-embedding-model"
    assert settings.chroma_collection_name == "test-books"
    assert settings.app_env == "test"
    assert settings.log_level == "DEBUG"
    assert settings.chroma_persist_directory.is_absolute()
    assert settings.chroma_persist_directory == (
        Path(__file__).resolve().parents[1] / "storage/test-chroma"
    )
    assert settings.openai_chat_model == "test-chat-model"


def test_missing_api_key_raises_configuration_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv(
        "OPENAI_CHAT_MODEL",
        "test-chat-model",
    )

    import smart_librarian.config as config_module

    monkeypatch.setattr(
        config_module,
        "load_dotenv",
        lambda *args, **kwargs: False,
    )

    with pytest.raises(
        ConfigurationError,
        match="OPENAI_API_KEY is missing",
    ):
        get_settings()

    def test_missing_chat_model_raises_configuration_error(
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setenv(
            "OPENAI_API_KEY",
            "test-api-key",
        )
        monkeypatch.delenv(
            "OPENAI_CHAT_MODEL",
            raising=False,
        )

        import smart_librarian.config as config_module

        monkeypatch.setattr(
            config_module,
            "load_dotenv",
            lambda *args, **kwargs: False,
        )

        with pytest.raises(
            ConfigurationError,
            match="OPENAI_CHAT_MODEL is missing",
        ):
            get_settings()
