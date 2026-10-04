import logging

from smart_librarian.config import get_settings
from smart_librarian.data.book_repository import BookRepository
from smart_librarian.exceptions import SmartLibrarianError
from smart_librarian.logging_config import configure_logging
from smart_librarian.rag.indexer import BookIndexer
from smart_librarian.rag.vector_store import ChromaVectorStore

logger = logging.getLogger(__name__)


def main() -> int:
    """Build or update the persistent Chroma book index."""

    try:
        settings = get_settings()
        configure_logging(settings.log_level)

        repository = BookRepository()

        vector_store = ChromaVectorStore(
            persist_directory=settings.chroma_persist_directory,
            collection_name=settings.chroma_collection_name,
        )

        indexer = BookIndexer(
            repository=repository,
            vector_store=vector_store,
        )

        result = indexer.index_all()

    except SmartLibrarianError as exc:
        logger.exception("Book indexing failed.")
        print(f"Indexing error: {exc}")
        return 1

    print(
        f"Indexed {result.indexed_count} books into collection "
        f"'{settings.chroma_collection_name}'."
    )
    print(f"The collection now contains {result.collection_count} records.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
