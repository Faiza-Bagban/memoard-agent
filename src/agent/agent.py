from src.agent.llm_client import OllamaClient
from src.memory.retriever import MemoryRetriever
from src.memory.schema import MemoryItem, MemoryType


class MemoardAgent:
    """An agent that answers coding questions using retrieved memory context.

    Args:
        None

    Returns:
        None
    """

    def __init__(self, persist_path: str = "./chroma_db", session_id: str = "default_session"):
        self.retriever = MemoryRetriever(persist_path)
        self.llm = OllamaClient()
        self.session_id = session_id

    def answer(self, question: str, convention_tag: str = "") -> str:
        """Answer a question using retrieved memory as context.

        Args:
            question: The user's coding question.
            convention_tag: Optional tag identifying which convention this question tests.

        Returns:
            The agent's text answer.
        """
        memories = self.retriever.retrieve(question, top_n=5)
        context_block = "\n".join(f"- {m['content']}" for m in memories) if memories else "No prior memory."

        prompt = (
            "You are a coding assistant for a specific codebase. "
            "Use the following remembered facts and conventions if relevant:\n"
            f"{context_block}\n\n"
            f"Question: {question}\n"
            "Answer with code or a direct explanation, following any remembered conventions exactly."
        )

        answer_text = self.llm.generate(prompt)

        self.retriever.episodic.write(MemoryItem(
            id="",
            content=f"Q: {question}\nA: {answer_text}",
            memory_type=MemoryType.EPISODIC,
            source_session=self.session_id,
            convention_tag=convention_tag,
        ))

        return answer_text