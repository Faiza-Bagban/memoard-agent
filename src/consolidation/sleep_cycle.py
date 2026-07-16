from src.consolidation.consolidator import Consolidator
from src.consolidation.forgetting import ForgettingPolicy


def run_sleep_cycle(persist_path: str = "./chroma_db", forget_threshold: float = 0.3) -> dict:
    """Run one full sleep cycle: consolidate raw episodes, then apply forgetting.

    Args:
        persist_path: Path to the ChromaDB store to operate on.
        forget_threshold: Minimum retention score for a memory to survive forgetting.

    Returns:
        A dict with consolidation and forgetting summaries.
    """
    consolidator = Consolidator(persist_path)
    consolidation_summary = consolidator.consolidate()

    forgetting_policy = ForgettingPolicy(persist_path, forget_threshold=forget_threshold)
    forgetting_summary = forgetting_policy.run()

    return {
        "consolidation": consolidation_summary,
        "forgetting": forgetting_summary,
    }