from datetime import datetime, timezone
from typing import List

from src.memory.stores import EpisodicStore, SemanticStore, ProceduralStore


class MemoryRetriever:
    """Retrieves and ranks relevant memories across all three memory types.

    Args:
        None

    Returns:
        None
    """

    def __init__(self, persist_path: str = "./chroma_db"):
        self.episodic = EpisodicStore(persist_path)
        self.semantic = SemanticStore(persist_path)
        self.procedural = ProceduralStore(persist_path)

    def retrieve(self, query: str, k_per_store: int = 3, top_n: int = 5) -> List[dict]:
        """Retrieve and rank the most relevant memories across all stores.

        Args:
            query: The text to search for.
            k_per_store: How many results to pull from each store before ranking.
            top_n: How many top-ranked results to return overall.

        Returns:
            A list of dicts sorted by combined relevance score, highest first.
        """
        candidates = []
        for store in (self.episodic, self.semantic, self.procedural):
            results = store.retrieve(query, k=k_per_store)
            for r in results:
                r["memory_type"] = store.memory_type.value
                store.touch(r["id"])
                candidates.append(r)

        for c in candidates:
            c["score"] = self._score(c)

        candidates.sort(key=lambda c: c["score"], reverse=True)
        return candidates[:top_n]

    def _score(self, candidate: dict) -> float:
        """Compute a combined relevance score for a single candidate memory.

        Args:
            candidate: A dict with distance and metadata fields.

        Returns:
            A float score - higher is more relevant.
        """
        distance = candidate.get("distance")
        similarity = 1.0 - distance if distance is not None else 0.5

        importance = float(candidate["metadata"].get("importance", 0.5))

        timestamp_str = candidate["metadata"].get("timestamp")
        recency = 0.5
        if timestamp_str:
            try:
                ts = datetime.fromisoformat(timestamp_str)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
                recency = 1.0 / (1.0 + age_hours / 24)
            except ValueError:
                pass

        return (0.5 * similarity) + (0.3 * importance) + (0.2 * recency)