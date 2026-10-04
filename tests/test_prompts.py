from smart_librarian.domain.search_models import BookCandidate
from smart_librarian.llm.prompts import build_recommendation_prompt


def test_recommendation_prompt_contains_query_and_candidates() -> None:
    candidates = [
        BookCandidate(
            title="1984",
            document=("Title: 1984\nThemes: surveillance, freedom"),
            distance=0.2,
        ),
        BookCandidate(
            title="Fahrenheit 451",
            document=("Title: Fahrenheit 451\nThemes: censorship, freedom"),
            distance=0.4,
        ),
    ]

    prompt = build_recommendation_prompt(
        user_query="I want a book about social control.",
        candidates=candidates,
    )

    assert "I want a book about social control." in prompt
    assert "1984" in prompt
    assert "Fahrenheit 451" in prompt
