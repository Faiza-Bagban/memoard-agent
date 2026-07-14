from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """The three types of memory a MemoryItem can belong to."""
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryItem(BaseModel):
    """A single unit of memory stored by the agent.

    Args:
        None

    Returns:
        None
    """
    id: str
    content: str
    memory_type: MemoryType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    importance: float = 0.5
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    source_session: Optional[str] = None
    convention_tag: Optional[str] = None