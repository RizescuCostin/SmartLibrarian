import pytest

from smart_librarian.domain.recommendation_models import BookRecommendation
from smart_librarian.domain.search_models import BookCandidate
from smart_librarian.llm.openai_client import OpenAIRecommendationClient


def test_recommended_title_must_be_from_candidates() -> None:
    candidates = [
        BookCandidate(
            title="1984",
            document="Title: 1984",
            distance=0.2,
        )
    ]

    recommendation = BookRecommendation(
        title="The Hobbit",
        reason="Fantasy.",
    )

    with pytest.raises(
        ValueError,
        match="not.*retrieved candidates",
    ):
        OpenAIRecommendationClient._validate_recommended_title(
            recommendation=recommendation,
            candidates=candidates,
        )
