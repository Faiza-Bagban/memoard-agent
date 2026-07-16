import json

from src.agent.llm_client import OllamaClient
from src.memory.schema import MemoryItem, MemoryType
from src.memory.stores import EpisodicStore, SemanticStore, ProceduralStore


class Consolidator:
    """Distills raw episodic memories into durable semantic facts and procedural skills.

    Args:
        None

    Returns:
        None
    """

    def __init__(self, persist_path: str = "./chroma_db"):
        self.episodic = EpisodicStore(persist_path)
        self.semantic = SemanticStore(persist_path)
        self.procedural = ProceduralStore(persist_path)
        self.llm = OllamaClient()

    def consolidate(self) -> dict:
        """Run one consolidation pass over all unconsolidated episodic memories.

        Args:
            None

        Returns:
            A dict summarizing how many episodes were processed and what was extracted.
        """
        unconsolidated = self.episodic.get_unconsolidated()

        if not unconsolidated:
            return {"episodes_processed": 0, "facts_extracted": 0, "skills_extracted": 0}

        episodes_text = "\n\n".join(f"- {item['content']}" for item in unconsolidated)

        prompt = (
            "You are reviewing raw conversation logs from a coding assistant agent. "
            "Extract durable, reusable knowledge from these logs.\n\n"
            f"Logs:\n{episodes_text}\n\n"
            "Return ONLY a JSON object with this exact structure, no other text:\n"
            '{"facts": ["fact 1", "fact 2"], "skills": ["skill 1", "skill 2"]}\n\n'
            "Facts = durable rules or conventions learned (e.g. naming rules, error patterns). "
            "Skills = reusable how-to steps for accomplishing a task type. "
            "Keep each item short (one sentence). Only include genuinely reusable knowledge."
        )

        raw_response = self.llm.generate(prompt)
        extracted = self._parse_response(raw_response)

        facts_written = 0
        for fact in extracted.get("facts", []):
            self.semantic.write(MemoryItem(
                id="",
                content=fact,
                memory_type=MemoryType.SEMANTIC,
                importance=0.8,
            ))
            facts_written += 1

        skills_written = 0
        for skill in extracted.get("skills", []):
            self.procedural.write(MemoryItem(
                id="",
                content=skill,
                memory_type=MemoryType.PROCEDURAL,
                importance=0.8,
            ))
            skills_written += 1

        for item in unconsolidated:
            self.episodic.mark_consolidated(item["id"])

        return {
            "episodes_processed": len(unconsolidated),
            "facts_extracted": facts_written,
            "skills_extracted": skills_written,
        }

    def _parse_response(self, raw_response: str) -> dict:
        """Parse the LLM's JSON response, handling markdown code fences if present.

        Args:
            raw_response: The raw text response from the LLM.

        Returns:
            A dict with "facts" and "skills" lists, empty lists if parsing fails.
        """
        text = raw_response.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {"facts": [], "skills": []}