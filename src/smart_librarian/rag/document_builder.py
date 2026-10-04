from smart_librarian.domain.models import Book


def build_book_document(book: Book) -> str:
    """Build the text that will be embedded for semantic retrieval."""

    genres = ", ".join(book.genres)
    themes = ", ".join(book.themes)

    return "\n".join(
        [
            f"Title: {book.title}",
            f"Genres: {genres}",
            f"Themes: {themes}",
            f"Summary: {book.short_summary}",
        ]
    )
