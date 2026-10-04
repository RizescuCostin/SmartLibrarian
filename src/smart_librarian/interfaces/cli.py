import logging

from smart_librarian.config import get_settings
from smart_librarian.data.book_repository import BookRepository
from smart_librarian.exceptions import ConfigurationError, SmartLibrarianError
from smart_librarian.llm.openai_client import OpenAIRecommendationClient
from smart_librarian.logging_config import configure_logging
from smart_librarian.rag.retriever import BookRetriever
from smart_librarian.rag.vector_store import ChromaVectorStore
from smart_librarian.services.librarian_service import LibrarianService
from smart_librarian.tools.tool_executor import ToolExecutor

logger = logging.getLogger(__name__)


def main() -> int:
    """Start the Smart Librarian command-line interface."""

    try:
        settings = get_settings()
    except ConfigurationError as exc:
        print(f"Configuration error: {exc}")
        return 1

    configure_logging(settings.log_level)

    try:
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

    except SmartLibrarianError as exc:
        logger.exception("Application startup failed.")
        print(f"Startup error: {exc}")
        return 1

    print()
    print("Smart Librarian")
    print("================")
    print("Type 'exit' to stop.")
    print()

    while True:
        user_query = input("You: ").strip()

        if user_query.casefold() == "exit":
            print("Goodbye!")
            break

        if not user_query:
            print("Please enter a book preference.")
            continue

        try:
            answer = service.answer(user_query)
        except (SmartLibrarianError, ValueError) as exc:
            print(f"Error: {exc}")
            continue

        print()
        print(f"Librarian: I recommend {answer.title}.")
        print(f"Why: {answer.reason}")
        print()
        print("Summary:")
        print(answer.summary)
        print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
