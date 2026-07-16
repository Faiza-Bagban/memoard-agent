from src.memory.schema import MemoryItem, MemoryType
from src.memory.stores import EpisodicStore
from src.consolidation.consolidator import Consolidator


def test_consolidation_extracts_facts():
    """Verify consolidation distills raw episodes into semantic facts.

    Args:
        None

    Returns:
        None
    """
    persist_path = "./chroma_db_test_consolidation"
    episodic = EpisodicStore(persist_path)

    episodic.write(MemoryItem(
        id="",
        content="Q: What should I name a test file for payments.py?\nA: In this codebase, test files must be named test_<module>_spec.py, so it should be test_payments_spec.py.",
        memory_type=MemoryType.EPISODIC,
        convention_tag="test_naming",
    ))
    episodic.write(MemoryItem(
        id="",
        content="Q: How do I raise an error for invalid input?\nA: In this codebase, errors must always use AppError(message, code), never a bare Exception.",
        memory_type=MemoryType.EPISODIC,
        convention_tag="error_handling",
    ))

    consolidator = Consolidator(persist_path)
    result = consolidator.consolidate()

    assert result["episodes_processed"] == 2
    assert result["facts_extracted"] > 0 or result["skills_extracted"] > 0

    remaining_unconsolidated = episodic.get_unconsolidated()
    assert len(remaining_unconsolidated) == 0