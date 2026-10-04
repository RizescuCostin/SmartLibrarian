import sys

from smart_librarian.config import get_settings
from smart_librarian.data.book_repository import BookRepository
from smart_librarian.exceptions import SmartLibrarianError
from smart_librarian.llm.openai_client import OpenAIRecommendationClient
from smart_librarian.rag.retriever import BookRetriever
from smart_librarian.rag.vector_store import ChromaVectorStore
from smart_librarian.services.librarian_service import LibrarianService
from smart_librarian.tools.tool_executor import ToolExecutor


def main() -> int:
    """Recommend one book and return its complete local summary."""

    if len(sys.argv) < 2:
        print('Usage: python scripts/recommend_book.py "your request"')
        return 1

    user_query = " ".join(sys.argv[1:])

    try:
        settings = get_settings()

        repository = BookRepository()

        vector_store = ChromaVectorStore(
            persist_directory=settings.chroma_persist_directory,
            collection_name=settings.chroma_collection_name,
        )

        retriever = BookRetriever(vector_store)

        recommendation_client = OpenAIRecommendationClient(
            api_key=settings.openai_api_key,
            model=settings.openai_chat_model,
        )

        tool_executor = ToolExecutor(repository)

        service = LibrarianService(
            retriever=retriever,
            recommendation_client=recommendation_client,
            tool_executor=tool_executor,
        )

        answer = service.answer(user_query)

    except (SmartLibrarianError, ValueError) as exc:
        print(f"Recommendation error: {exc}")
        return 1

    print()
    print(f"Recommendation: {answer.title}")
    print()
    print(f"Why: {answer.reason}")
    print()
    print("Summary:")
    print(answer.summary)
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
