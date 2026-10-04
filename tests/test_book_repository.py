import json
from pathlib import Path

import pytest

from smart_librarian.data.book_repository import BookRepository
from smart_librarian.exceptions import DataFileError, DuplicateBookTitleError

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"
SAMPLE_BOOKS_FILE = FIXTURES_DIRECTORY / "sample_books.json"


def test_repository_loads_all_books() -> None:
    repository = BookRepository(SAMPLE_BOOKS_FILE)

    books = repository.get_all()

    assert len(books) == 2
    assert books[0].title == "Test Book One"
    assert books[1].title == "Test Book Two"


def test_repository_finds_book_by_exact_title() -> None:
    repository = BookRepository(SAMPLE_BOOKS_FILE)

    book = repository.get_by_title("Test Book One")

    assert book is not None
    assert book.title == "Test Book One"


def test_repository_lookup_ignores_case_and_whitespace() -> None:
    repository = BookRepository(SAMPLE_BOOKS_FILE)

    book = repository.get_by_title("  TEST BOOK ONE  ")

    assert book is not None
    assert book.title == "Test Book One"


def test_repository_returns_none_for_unknown_title() -> None:
    repository = BookRepository(SAMPLE_BOOKS_FILE)

    book = repository.get_by_title("Unknown Book")

    assert book is None


def test_repository_raises_error_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.json"

    with pytest.raises(DataFileError, match="Could not read book dataset"):
        BookRepository(missing_file)


def test_repository_raises_error_for_invalid_json(
    tmp_path: Path,
) -> None:
    invalid_file = tmp_path / "invalid.json"
    invalid_file.write_text("{invalid json", encoding="utf-8")

    with pytest.raises(DataFileError, match="invalid JSON"):
        BookRepository(invalid_file)


def test_repository_raises_error_for_duplicate_titles(
    tmp_path: Path,
) -> None:
    duplicate_file = tmp_path / "duplicates.json"

    duplicate_books = [
        {
            "title": "Duplicate Book",
            "short_summary": "First short summary.",
            "full_summary": "First full summary.",
        },
        {
            "title": " duplicate book ",
            "short_summary": "Second short summary.",
            "full_summary": "Second full summary.",
        },
    ]

    duplicate_file.write_text(
        json.dumps(duplicate_books),
        encoding="utf-8",
    )

    with pytest.raises(
        DuplicateBookTitleError,
        match="Duplicate book title",
    ):
        BookRepository(duplicate_file)
