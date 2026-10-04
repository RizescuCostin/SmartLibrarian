from pathlib import Path
from typing import Any

import pytest

from smart_librarian.rag.vector_store import ChromaVectorStore


class FakeCollection:
    def __init__(self) -> None:
        self.received: dict[str, Any] | None = None

    def upsert(
        self,
        *,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        self.received = {
            "ids": ids,
            "documents": documents,
            "metadatas": metadatas,
        }

    def query(
        self,
        *,
        query_texts: list[str],
        n_results: int,
        include: list[str],
    ) -> dict:
        return {
            "documents": [["Test document"]],
            "metadatas": [[{"title": "Test Book"}]],
            "distances": [[0.1]],
        }


def create_store_without_chroma() -> ChromaVectorStore:
    store = object.__new__(ChromaVectorStore)
    store._persist_directory = Path("unused")
    store._collection_name = "test"
    store._collection = FakeCollection()
    return store


def test_upsert_rejects_different_list_lengths() -> None:
    store = create_store_without_chroma()

    with pytest.raises(ValueError, match="equal lengths"):
        store.upsert(
            ids=["one"],
            documents=["document one", "document two"],
            metadatas=[{"title": "One"}],
        )


def test_upsert_passes_records_to_collection() -> None:
    store = create_store_without_chroma()

    store.upsert(
        ids=["test-book"],
        documents=["Title: Test Book"],
        metadatas=[{"title": "Test Book"}],
    )

    collection = store._collection

    assert collection.received == {
        "ids": ["test-book"],
        "documents": ["Title: Test Book"],
        "metadatas": [{"title": "Test Book"}],
    }


def test_query_rejects_empty_query() -> None:
    store = create_store_without_chroma()

    with pytest.raises(ValueError, match="must not be empty"):
        store.query("   ")


def test_query_rejects_invalid_limit() -> None:
    store = create_store_without_chroma()

    with pytest.raises(ValueError, match="greater than zero"):
        store.query(
            "fantasy",
            limit=0,
        )
