from dataclasses import dataclass

from smart_librarian.data.book_repository import BookRepository
from smart_librarian.rag.book_ids import create_book_id
from smart_librarian.rag.document_builder import build_book_document
from smart_librarian.rag.vector_store import ChromaVectorStore


@dataclass(frozen=True)
class IndexingResult:
    """Describes the outcome of one indexing operation."""

    indexed_count: int
    collection_count: int


class BookIndexer:
    """Indexes books from the repository into ChromaDB."""

    def __init__(
        self,
        repository: BookRepository,
        vector_store: ChromaVectorStore,
    ) -> None:
        self._repository = repository
        self._vector_store = vector_store

    def index_all(self) -> IndexingResult:
        """Insert or update every local book in ChromaDB."""

        books = self._repository.get_all()

        ids = [create_book_id(book.title) for book in books]
        documents = [build_book_document(book) for book in books]
        metadatas = [
            {
                "title": book.title,
                "genres": ", ".join(book.genres),
            }
            for book in books
        ]

        self._vector_store.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        return IndexingResult(
            indexed_count=len(books),
            collection_count=self._vector_store.count(),
        )
