from src.memory.base_store import BaseMemoryStore
from src.memory.schema import MemoryType


class EpisodicStore(BaseMemoryStore):
    """Stores raw session events - what happened, turn by turn.

    Args:
        None

    Returns:
        None
    """

    def __init__(self, persist_path: str = "./chroma_db"):
        super().__init__(MemoryType.EPISODIC, persist_path)


class SemanticStore(BaseMemoryStore):
    """Stores distilled facts learned from past sessions.

    Args:
        None

    Returns:
        None
    """

    def __init__(self, persist_path: str = "./chroma_db"):
        super().__init__(MemoryType.SEMANTIC, persist_path)


class ProceduralStore(BaseMemoryStore):
    """Stores reusable skills/how-to patterns that worked before.

    Args:
        None

    Returns:
        None
    """

    def __init__(self, persist_path: str = "./chroma_db"):
        super().__init__(MemoryType.PROCEDURAL, persist_path)