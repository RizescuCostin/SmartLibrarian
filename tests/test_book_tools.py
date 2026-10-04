from pathlib import Path

import pytest

from smart_librarian.data.book_repository import BookRepository
from smart_librarian.exceptions import BookNotFoundError
from smart_librarian.tools.book_tools import get_summary_by_title

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"
SAMPLE_BOOKS_FILE = FIXTURES_DIRECTORY / "sample_books.json"


@pytest.fixture
def repository() -> BookRepository:
    return BookRepository(SAMPLE_BOOKS_FILE)


def test_get_summary_by_title_returns_full_summary(
    repository: BookRepository,
) -> None:
    summary = get_summary_by_title(
        "Test Book One",
        repository,
    )

    assert summary == "A complete summary for the first test book."


def test_get_summary_by_title_ignores_case(
    repository: BookRepository,
) -> None:
    summary = get_summary_by_title(
        "TEST BOOK ONE",
        repository,
    )

    assert summary == "A complete summary for the first test book."


def test_get_summary_by_title_ignores_surrounding_whitespace(
    repository: BookRepository,
) -> None:
    summary = get_summary_by_title(
        "  Test Book One  ",
        repository,
    )

    assert summary == "A complete summary for the first test book."


def test_get_summary_by_title_rejects_empty_title(
    repository: BookRepository,
) -> None:
    with pytest.raises(
        ValueError,
        match="Book title must not be empty",
    ):
        get_summary_by_title(
            "   ",
            repository,
        )


def test_get_summary_by_title_raises_for_unknown_book(
    repository: BookRepository,
) -> None:
    with pytest.raises(
        BookNotFoundError,
        match="Book not found: Unknown Book",
    ):
        get_summary_by_title(
            "Unknown Book",
            repository,
        )
