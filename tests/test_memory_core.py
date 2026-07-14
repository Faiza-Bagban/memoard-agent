from src.memory.schema import MemoryItem, MemoryType
from src.memory.stores import EpisodicStore, SemanticStore, ProceduralStore


def test_write_and_retrieve_episodic():
    """Verify an episodic memory can be written and retrieved.

    Args:
        None

    Returns:
        None
    """
    store = EpisodicStore(persist_path="./chroma_db_test")
    item = MemoryItem(
        id="",
        content="User asked how to name test files for payments module.",
        memory_type=MemoryType.EPISODIC,
        source_session="session_1",
        convention_tag="test_naming",
    )
    item_id = store.write(item)
    results = store.retrieve("test file naming", k=3)
    assert len(results) > 0
    assert item_id in [r["id"] for r in results]


def test_semantic_store_all():
    """Verify semantic store returns all written items.

    Args:
        None

    Returns:
        None
    """
    store = SemanticStore(persist_path="./chroma_db_test")
    item = MemoryItem(
        id="",
        content="Convention: test files must be named test_<module>_spec.py",
        memory_type=MemoryType.SEMANTIC,
        convention_tag="test_naming",
    )
    store.write(item)
    all_items = store.all()
    assert len(all_items) > 0


def test_procedural_store_write():
    """Verify procedural store can write and read back a skill.

    Args:
        None

    Returns:
        None
    """
    store = ProceduralStore(persist_path="./chroma_db_test")
    item = MemoryItem(
        id="",
        content="When raising errors, always use AppError(message, code).",
        memory_type=MemoryType.PROCEDURAL,
        convention_tag="error_handling",
    )
    item_id = store.write(item)
    all_items = store.all()
    assert any(i["id"] == item_id for i in all_items)