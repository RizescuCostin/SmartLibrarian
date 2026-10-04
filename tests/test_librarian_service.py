import pytest

from smart_librarian.domain.librarian_models import LibrarianAnswer
from smart_librarian.domain.search_models import BookCandidate
from smart_librarian.services.librarian_service import LibrarianService


class FakeRetriever:
    def retrieve(
        self,
        query: str,
        limit: int = 3,
    ) -> list[BookCandidate]:
        return [
            BookCandidate(
                title="1984",
                document="Title: 1984",
                distance=0.2,
            ),
            BookCandidate(
                title="Fahrenheit 451",
                document="Title: Fahrenheit 451",
                distance=0.4,
            ),
        ]


class FakeToolExecutor:
    pass


class FakeRecommendationClient:
    def recommend_with_summary(
        self,
        *,
        user_query: str,
        candidates: list[BookCandidate],
        tool_executor: FakeToolExecutor,
    ) -> LibrarianAnswer:
        return LibrarianAnswer(
            title="1984",
            reason="It best matches the user's interest.",
            summary="Test summary.",
        )


def test_service_returns_recommendation() -> None:
    service = LibrarianService(
        retriever=FakeRetriever(),
        recommendation_client=FakeRecommendationClient(),
        tool_executor=FakeToolExecutor(),
    )

    answer = service.answer(
        "surveillance and social control"
    )

    assert answer.title == "1984"
    assert answer.reason == "It best matches the user's interest."
    assert answer.summary == "Test summary."


def test_service_rejects_empty_query() -> None:
    service = LibrarianService(
        retriever=FakeRetriever(),
        recommendation_client=FakeRecommendationClient(),
        tool_executor=FakeToolExecutor(),
    )

    with pytest.raises(
        ValueError,
        match="must not be empty",
    ):
        service.answer("   ")