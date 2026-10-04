from smart_librarian.domain.models import Book
from smart_librarian.rag.document_builder import build_book_document


def test_build_book_document_contains_retrieval_information() -> None:
    book = Book(
        title="Test Book",
        short_summary="A story about friendship and magic.",
        full_summary="A much longer summary.",
        themes=["friendship", "magic"],
        genres=["fantasy", "adventure"],
    )

    document = build_book_document(book)

    assert "Title: Test Book" in document
    assert "Genres: fantasy, adventure" in document
    assert "Themes: friendship, magic" in document
    assert "Summary: A story about friendship and magic." in document


def test_build_book_document_does_not_include_full_summary() -> None:
    book = Book(
        title="Test Book",
        short_summary="Short summary.",
        full_summary="Private full summary text.",
        themes=["friendship"],
        genres=["fantasy"],
    )

    document = build_book_document(book)

    assert "Private full summary text." not in document
