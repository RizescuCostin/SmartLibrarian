from smart_librarian.domain.librarian_models import LibrarianAnswer
from smart_librarian.llm.openai_client import OpenAIRecommendationClient
from smart_librarian.rag.retriever import BookRetriever
from smart_librarian.tools.tool_executor import ToolExecutor


class LibrarianService:
    """Coordinates retrieval, recommendation, and local tool execution."""

    def __init__(
        self,
        *,
        retriever: BookRetriever,
        recommendation_client: OpenAIRecommendationClient,
        tool_executor: ToolExecutor,
    ) -> None:
        self._retriever = retriever
        self._recommendation_client = recommendation_client
        self._tool_executor = tool_executor

    def answer(
        self,
        user_query: str,
    ) -> LibrarianAnswer:
        """Return a recommendation with its complete local summary."""

        normalized_query = user_query.strip()

        if not normalized_query:
            raise ValueError("User query must not be empty.")

        candidates = self._retriever.retrieve(
            query=normalized_query,
            limit=3,
        )

        if not candidates:
            raise ValueError("No candidate books were found.")

        return self._recommendation_client.recommend_with_summary(
            user_query=normalized_query,
            candidates=candidates,
            tool_executor=self._tool_executor,
        )
