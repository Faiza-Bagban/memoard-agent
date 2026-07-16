from src.memory.schema import MemoryItem, MemoryType
from src.memory.stores import SemanticStore
from src.consolidation.forgetting import ForgettingPolicy


def test_forgetting_keeps_important_drops_unimportant():
    """Verify high-importance memories survive and low-importance ones get forgotten.

    Args:
        None

    Returns:
        None
    """
    persist_path = "./chroma_db_test_forgetting"
    semantic = SemanticStore(persist_path)

    important_id = semantic.write(MemoryItem(
        id="",
        content="Critical convention: always use AppError for exceptions.",
        memory_type=MemoryType.SEMANTIC,
        importance=0.95,
    ))
    unimportant_id = semantic.write(MemoryItem(
        id="",
        content="Minor one-off note that is not really useful long-term.",
        memory_type=MemoryType.SEMANTIC,
        importance=0.05,
    ))

    policy = ForgettingPolicy(persist_path, forget_threshold=0.3)
    summary = policy.run()

    assert summary["semantic"]["forgotten"] >= 1

    remaining = semantic.all()
    remaining_ids = [item["id"] for item in remaining]
    assert important_id in remaining_ids
    assert unimportant_id not in remaining_ids