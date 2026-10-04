import sys

from smart_librarian.config import get_settings
from smart_librarian.exceptions import SmartLibrarianError
from smart_librarian.rag.retriever import BookRetriever
from smart_librarian.rag.vector_store import ChromaVectorStore


def main() -> int:
    """Run a semantic book search from the command line."""

    if len(sys.argv) < 2:
        print('Usage: python scripts/search_books.py "your search query"')
        return 1

    query = " ".join(sys.argv[1:])

    try:
        settings = get_settings()

        vector_store = ChromaVectorStore(
            persist_directory=settings.chroma_persist_directory,
            collection_name=settings.chroma_collection_name,
        )

        retriever = BookRetriever(vector_store)

        results = retriever.retrieve(
            query=query,
            limit=3,
        )

    except (SmartLibrarianError, ValueError) as exc:
        print(f"Search error: {exc}")
        return 1

    if not results:
        print("No books found.")
        return 0

    print()
    print(f"Search: {query}")
    print()

    for position, candidate in enumerate(results, start=1):
        print(f"{position}. {candidate.title}")

        if candidate.distance is not None:
            print(f"   Distance: {candidate.distance:.4f}")

        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
