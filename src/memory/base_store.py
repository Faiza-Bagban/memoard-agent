import uuid
from typing import List, Optional

import chromadb
from chromadb.utils import embedding_functions

from src.memory.schema import MemoryItem, MemoryType

_embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


class BaseMemoryStore:
    """A ChromaDB-backed store for a single type of memory.

    Args:
        None

    Returns:
        None
    """

    def __init__(self, memory_type: MemoryType, persist_path: str = "./chroma_db"):
        self.memory_type = memory_type
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name=f"memory_{memory_type.value}",
            embedding_function=_embedding_fn,
        )

    def write(self, item: MemoryItem) -> str:
        """Store a memory item in this collection.

        Args:
            item: The MemoryItem to store.

        Returns:
            The id of the stored item.
        """
        if not item.id:
            item.id = str(uuid.uuid4())
        self.collection.add(
            ids=[item.id],
            documents=[item.content],
            metadatas=[{
                "memory_type": item.memory_type.value,
                "timestamp": item.timestamp.isoformat(),
                "importance": item.importance,
                "access_count": item.access_count,
                "source_session": item.source_session or "",
                "convention_tag": item.convention_tag or "",
            }],
        )
        return item.id

    def retrieve(self, query: str, k: int = 5) -> List[dict]:
        """Retrieve the top-k most relevant memory items for a query.

        Args:
            query: The text to search for.
            k: Number of results to return.

        Returns:
            A list of dicts with document content, metadata, and distance.
        """
        results = self.collection.query(query_texts=[query], n_results=k)
        items = []
        if results["ids"] and results["ids"][0]:
            for i in range(len(results["ids"][0])):
                items.append({
                    "id": results["ids"][0][i],
                    "content": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i] if results.get("distances") else None,
                })
        return items

    def all(self) -> List[dict]:
        """Return all items in this store.

        Args:
            None

        Returns:
            A list of dicts with id, content, and metadata for every stored item.
        """
        results = self.collection.get()
        items = []
        for i in range(len(results["ids"])):
            items.append({
                "id": results["ids"][i],
                "content": results["documents"][i],
                "metadata": results["metadatas"][i],
            })
        return items

    def delete(self, item_id: str) -> None:
        """Delete a memory item by id.

        Args:
            item_id: The id of the item to delete.

        Returns:
            None
        """
        self.collection.delete(ids=[item_id])