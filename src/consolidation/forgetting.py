from datetime import datetime, timezone

from src.memory.stores import EpisodicStore, SemanticStore, ProceduralStore


class ForgettingPolicy:
    """Scores and prunes low-value memories to keep memory bounded.

    Args:
        None

    Returns:
        None
    """

    def __init__(self, persist_path: str = "./chroma_db", forget_threshold: float = 0.3):
        self.episodic = EpisodicStore(persist_path)
        self.semantic = SemanticStore(persist_path)
        self.procedural = ProceduralStore(persist_path)
        self.forget_threshold = forget_threshold

    def run(self) -> dict:
        """Score every memory and delete those below the forget threshold.

        Args:
            None

        Returns:
            A dict summarizing how many items were reviewed and forgotten per store.
        """
        summary = {}
        for store in (self.episodic, self.semantic, self.procedural):
            all_items = store.all()
            forgotten = 0
            for item in all_items:
                score = self._score(item["metadata"])
                if score < self.forget_threshold:
                    store.delete(item["id"])
                    forgotten += 1
            summary[store.memory_type.value] = {
                "reviewed": len(all_items),
                "forgotten": forgotten,
            }
        return summary

    def _score(self, metadata: dict) -> float:
        """Compute a retention score for a memory item - higher means keep it.

        Args:
            metadata: The stored metadata dict for a memory item.

        Returns:
            A float score combining importance, recency, and access frequency.
        """
        importance = float(metadata.get("importance", 0.5))

        access_count = int(metadata.get("access_count", 0))
        access_score = min(access_count / 5.0, 1.0)

        timestamp_str = metadata.get("timestamp")
        recency_score = 0.5
        if timestamp_str:
            try:
                ts = datetime.fromisoformat(timestamp_str)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                age_hours = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
                recency_score = 1.0 / (1.0 + age_hours / 24)
            except ValueError:
                pass

        return (0.5 * importance) + (0.3 * access_score) + (0.2 * recency_score)