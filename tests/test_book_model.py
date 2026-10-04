import pytest
from pydantic import ValidationError

from smart_librarian.domain.models import Book


def test_book_strips_required_text() -> None:
    book = Book(
        title="  Test Book  ",
        short_summary="  Short summary  ",
        full_summary="  Full summary  ",
    )

    assert book.title == "Test Book"
    assert book.short_summary == "Short summary"
    assert book.full_summary == "Full summary"


def test_book_rejects_blank_title() -> None:
    with pytest.raises(ValidationError):
        Book(
            title="   ",
            short_summary="Short summary",
            full_summary="Full summary",
        )


def test_book_cleans_themes_and_genres() -> None:
    book = Book(
        title="Test Book",
        short_summary="Short summary",
        full_summary="Full summary",
        themes=[" friendship ", "", " courage "],
        genres=[" fantasy ", "  "],
    )

    assert book.themes == ["friendship", "courage"]
    assert book.genres == ["fantasy"]
