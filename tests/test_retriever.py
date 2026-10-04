import pytest

from smart_librarian.rag.retriever import BookRetriever


class EmptyVectorStore:
    def query(
        self,
        query_text: str,
        limit: int = 3,
    ) -> dict:
        return {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]],
        }


class PartialVectorStore:
    def query(
        self,
        query_text: str,
        limit: int = 3,
    ) -> dict:
        return {
            "documents": [
                [
                    "Valid document",
                    "",
                ]
            ],
            "metadatas": [
                [
                    {"title": "Valid Book"},
                    {"title": "Invalid Book"},
                ]
            ],
            "distances": [
                [
                    0.2,
                    0.3,
                ]
            ],
        }


class FakeVectorStore:
    def query(
        self,
        query_text: str,
        limit: int = 3,
    ) -> dict:
        return {
            "documents": [
                [
                    "Title: 1984\nSummary: A dystopian novel.",
                    "Title: Fahrenheit 451\nSummary: A censored society.",
                ]
            ],
            "metadatas": [
                [
                    {"title": "1984"},
                    {"title": "Fahrenheit 451"},
                ]
            ],
            "distances": [
                [
                    0.2,
                    0.4,
                ]
            ],
        }


def test_retriever_converts_results_to_candidates() -> None:
    retriever = BookRetriever(FakeVectorStore())

    results = retriever.retrieve(
        "surveillance and censorship",
        limit=2,
    )

    assert len(results) == 2

    assert results[0].title == "1984"
    assert results[0].distance == 0.2

    assert results[1].title == "Fahrenheit 451"
    assert results[1].distance == 0.4


def test_retriever_rejects_empty_query() -> None:
    retriever = BookRetriever(FakeVectorStore())

    with pytest.raises(ValueError, match="must not be empty"):
        retriever.retrieve("   ")


def test_retriever_rejects_invalid_limit() -> None:
    retriever = BookRetriever(FakeVectorStore())

    with pytest.raises(ValueError, match="greater than zero"):
        retriever.retrieve(
            "fantasy",
            limit=0,
        )


def test_retriever_returns_empty_list_when_no_results() -> None:
    retriever = BookRetriever(EmptyVectorStore())

    results = retriever.retrieve("anything")

    assert results == []


def test_retriever_skips_invalid_entries() -> None:
    retriever = BookRetriever(PartialVectorStore())

    results = retriever.retrieve("test")

    assert len(results) == 1
    assert results[0].title == "Valid Book"
