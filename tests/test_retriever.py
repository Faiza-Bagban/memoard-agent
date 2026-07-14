from src.memory.schema import MemoryItem, MemoryType
from src.memory.stores import EpisodicStore, SemanticStore, ProceduralStore
from src.memory.retriever import MemoryRetriever


def _seed_memories(persist_path: str) -> None:
    """Write one memory item into each store for testing retrieval.

    Args:
        persist_path: The path to use for the test ChromaDB instance.

    Returns:
        None
    """
    episodic = EpisodicStore(persist_path)
    semantic = SemanticStore(persist_path)
    procedural = ProceduralStore(persist_path)

    episodic.write(MemoryItem(
        id="",
        content="Session event: user asked about test file naming for shipping module.",
        memory_type=MemoryType.EPISODIC,
        importance=0.4,
        convention_tag="test_naming",
    ))
    semantic.write(MemoryItem(
        id="",
        content="Fact: test files must be named test_<module>_spec.py in this codebase.",
        memory_type=MemoryType.SEMANTIC,
        importance=0.9,
        convention_tag="test_naming",
    ))
    procedural.write(MemoryItem(
        id="",
        content="Skill: when naming a test file, take the module name and wrap it as test_<module>_spec.py.",
        memory_type=MemoryType.PROCEDURAL,
        importance=0.8,
        convention_tag="test_naming",
    ))


def test_retriever_pulls_across_all_stores():
    """Verify the retriever returns results spanning multiple memory types.

    Args:
        None

    Returns:
        None
    """
    persist_path = "./chroma_db_test_retriever"
    _seed_memories(persist_path)

    retriever = MemoryRetriever(persist_path)
    results = retriever.retrieve("How should I name a test file?", top_n=5)

    assert len(results) > 0
    memory_types_found = {r["memory_type"] for r in results}
    assert len(memory_types_found) >= 2


def test_retriever_ranks_by_score():
    """Verify results are sorted by descending score.

    Args:
        None

    Returns:
        None
    """
    persist_path = "./chroma_db_test_retriever"
    retriever = MemoryRetriever(persist_path)
    results = retriever.retrieve("test file naming convention", top_n=5)

    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True)