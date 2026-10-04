from smart_librarian.domain.search_models import BookCandidate
from smart_librarian.rag.vector_store import ChromaVectorStore


class BookRetriever:
    """Retrieves semantically relevant books from ChromaDB."""

    def __init__(self, vector_store: ChromaVectorStore) -> None:
        self._vector_store = vector_store

    def retrieve(
        self,
        query: str,
        limit: int = 3,
    ) -> list[BookCandidate]:
        """Return the most relevant books for a natural-language query."""

        normalized_query = query.strip()

        if not normalized_query:
            raise ValueError("Query must not be empty.")

        if limit <= 0:
            raise ValueError("Limit must be greater than zero.")

        raw_results = self._vector_store.query(
            query_text=normalized_query,
            limit=limit,
        )

        return self._to_candidates(raw_results)

    @staticmethod
    def _to_candidates(
        raw_results: dict,
    ) -> list[BookCandidate]:
        """Convert Chroma's nested result structure into domain models."""

        documents = raw_results.get("documents") or []
        metadatas = raw_results.get("metadatas") or []
        distances = raw_results.get("distances") or []

        if not documents or not metadatas:
            return []

        query_documents = documents[0]
        query_metadatas = metadatas[0]

        query_distances = distances[0] if distances else []

        candidates: list[BookCandidate] = []

        for index, document in enumerate(query_documents):
            metadata = query_metadatas[index]

            distance = query_distances[index] if index < len(query_distances) else None

            title = metadata.get("title")

            if not title or not document:
                continue

            candidates.append(
                BookCandidate(
                    title=title,
                    document=document,
                    distance=distance,
                )
            )

        return candidates
