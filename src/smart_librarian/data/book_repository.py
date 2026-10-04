import json
from pathlib import Path

from pydantic import ValidationError

from smart_librarian.domain.models import Book
from smart_librarian.exceptions import DataFileError, DuplicateBookTitleError

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATA_FILE = PROJECT_ROOT / "data" / "book_summaries.json"


class BookRepository:
    """Loads and provides access to books stored in a local JSON file."""

    def __init__(self, data_file: Path = DEFAULT_DATA_FILE) -> None:
        self._data_file = data_file
        self._books = self._load_books()
        self._books_by_normalized_title = self._build_title_index(self._books)

    def get_all(self) -> list[Book]:
        """Return all books in the dataset."""

        return list(self._books)

    def get_by_title(self, title: str) -> Book | None:
        """Find a book by title, ignoring case and surrounding whitespace."""

        normalized_title = self._normalize_title(title)
        return self._books_by_normalized_title.get(normalized_title)

    def _load_books(self) -> list[Book]:
        """Load and validate books from the JSON dataset."""

        try:
            raw_content = self._data_file.read_text(encoding="utf-8")
        except OSError as exc:
            raise DataFileError(
                f"Could not read book dataset: {self._data_file}"
            ) from exc

        try:
            raw_books = json.loads(raw_content)
        except json.JSONDecodeError as exc:
            raise DataFileError(
                f"Book dataset contains invalid JSON: {self._data_file}"
            ) from exc

        if not isinstance(raw_books, list):
            raise DataFileError("Book dataset must contain a JSON array of books.")

        try:
            return [Book.model_validate(raw_book) for raw_book in raw_books]
        except ValidationError as exc:
            raise DataFileError(
                f"Book dataset contains invalid book data: {exc}"
            ) from exc

    def _build_title_index(self, books: list[Book]) -> dict[str, Book]:
        """Build a case-insensitive lookup table and reject duplicates."""

        title_index: dict[str, Book] = {}

        for book in books:
            normalized_title = self._normalize_title(book.title)

            if normalized_title in title_index:
                raise DuplicateBookTitleError(f"Duplicate book title: {book.title}")

            title_index[normalized_title] = book

        return title_index

    @staticmethod
    def _normalize_title(title: str) -> str:
        """Normalize a title for reliable lookup."""

        return title.strip().casefold()
