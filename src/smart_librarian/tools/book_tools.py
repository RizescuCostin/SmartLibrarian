from smart_librarian.data.book_repository import BookRepository
from smart_librarian.exceptions import BookNotFoundError


def get_summary_by_title(
    title: str,
    repository: BookRepository,
) -> str:
    """Return the complete local summary for an exact book title."""

    normalized_title = title.strip()

    if not normalized_title:
        raise ValueError("Book title must not be empty.")

    book = repository.get_by_title(normalized_title)

    if book is None:
        raise BookNotFoundError(f"Book not found: {normalized_title}")

    return book.full_summary
