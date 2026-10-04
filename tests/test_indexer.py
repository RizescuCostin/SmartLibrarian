from pathlib import Path
from typing import Any

from smart_librarian.data.book_repository import BookRepository
from smart_librarian.rag.indexer import BookIndexer

FIXTURES_DIRECTORY = Path(__file__).parent / "fixtures"
SAMPLE_BOOKS_FILE = FIXTURES_DIRECTORY / "sample_books.json"


class FakeVectorStore:
    """Test double that records data passed to upsert."""

    def __init__(self) -> None:
        self.ids: list[str] = []
        self.documents: list[str] = []
        self.metadatas: list[dict[str, Any]] = []

    def upsert(
        self,
        *,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.ids = ids
        self.documents = documents
        self.metadatas = metadatas

    def count(self) -> int:
        return len(self.ids)


def test_indexer_indexes_all_repository_books() -> None:
    repository = BookRepository(SAMPLE_BOOKS_FILE)
    vector_store = FakeVectorStore()

    indexer = BookIndexer(
        repository=repository,
        vector_store=vector_store,
    )

    result = indexer.index_all()

    assert result.indexed_count == 2
    assert result.collection_count == 2

    assert vector_store.ids == [
        "test-book-one",
        "test-book-two",
    ]


def test_indexer_builds_documents_and_metadata() -> None:
    repository = BookRepository(SAMPLE_BOOKS_FILE)
    vector_store = FakeVectorStore()

    indexer = BookIndexer(
        repository=repository,
        vector_store=vector_store,
    )

    indexer.index_all()

    first_document = vector_store.documents[0]
    first_metadata = vector_store.metadatas[0]

    assert "Title: Test Book One" in first_document
    assert "Themes: friendship" in first_document
    assert "Genres: fantasy" in first_document

    assert first_metadata == {
        "title": "Test Book One",
        "genres": "fantasy",
    }
