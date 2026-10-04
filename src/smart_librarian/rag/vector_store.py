from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from smart_librarian.exceptions import VectorStoreError


class ChromaVectorStore:
    """Provides access to the persistent Chroma book collection."""

    def __init__(
        self,
        persist_directory: Path,
        collection_name: str,
    ) -> None:
        self._persist_directory = persist_directory
        self._collection_name = collection_name

        try:
            self._persist_directory.mkdir(parents=True, exist_ok=True)

            self._client = chromadb.PersistentClient(path=str(self._persist_directory))

            self._collection = self._client.get_or_create_collection(
                name=self._collection_name,
                metadata={
                    "description": ("Semantic search index for Smart Librarian books.")
                },
            )
        except Exception as exc:
            raise VectorStoreError(
                "Could not initialize the Chroma vector store."
            ) from exc

    @property
    def collection(self) -> Collection:
        """Return the underlying Chroma collection."""

        return self._collection

    def upsert(
        self,
        *,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict[str, Any]],
    ) -> None:
        """Insert new records or update records with existing IDs."""

        if not ids:
            return

        if not (len(ids) == len(documents) == len(metadatas)):
            raise ValueError("IDs, documents, and metadata must have equal lengths.")

        try:
            self._collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas,
            )
        except Exception as exc:
            raise VectorStoreError("Could not upsert books into ChromaDB.") from exc

    def count(self) -> int:
        """Return the number of records in the collection."""

        try:
            return self._collection.count()
        except Exception as exc:
            raise VectorStoreError("Could not count records in ChromaDB.") from exc

    def query(
        self,
        query_text: str,
        limit: int = 3,
    ) -> dict[str, Any]:
        """Search the collection using semantic similarity."""

        if not query_text.strip():
            raise ValueError("Query text must not be empty.")

        if limit <= 0:
            raise ValueError("Query limit must be greater than zero.")

        try:
            return self._collection.query(
                query_texts=[query_text],
                n_results=limit,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as exc:
            raise VectorStoreError("Could not query ChromaDB.") from exc
