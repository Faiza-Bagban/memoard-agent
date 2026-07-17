import json

from src.agent.llm_client import OllamaClient
from src.memory.schema import MemoryItem, MemoryType
from src.memory.stores import EpisodicStore, SemanticStore, ProceduralStore


class Consolidator:
    """Distills raw episodic memories into durable semantic facts and procedural skills.

    Uses convention-tag-based supersession: when a new fact is extracted for a
    tag that already has a stored fact, the old one is replaced rather than
    duplicated, preventing memory drift and contradiction buildup.

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
        """Run one consolidation pass, grouped by convention tag with supersession.

        Args:
            None

        Returns:
            A dict summarizing how many episodes were processed and what was extracted.
        """
        unconsolidated = self.episodic.get_unconsolidated()

        if not unconsolidated:
            return {"episodes_processed": 0, "facts_extracted": 0, "skills_extracted": 0, "facts_superseded": 0}

        by_tag = {}
        for item in unconsolidated:
            tag = item["metadata"].get("convention_tag", "") or "untagged"
            by_tag.setdefault(tag, []).append(item)

        total_facts = 0
        total_skills = 0
        total_superseded = 0

        for tag, items in by_tag.items():
            episodes_text = "\n\n".join(f"- {item['content']}" for item in items)

            prompt = (
                "You are reviewing raw conversation logs from a coding assistant agent, "
                f"all related to the same topic/convention: '{tag}'.\n\n"
                f"Logs:\n{episodes_text}\n\n"
                "Return ONLY a JSON object with this exact structure, no other text:\n"
                '{"facts": ["fact 1"], "skills": ["skill 1"]}\n\n'
                "Extract at most ONE durable fact and ONE reusable skill that best represents "
                "the correct, consistent rule across these logs. If logs disagree, prefer the "
                "most specific and most repeated version. Keep each item short (one sentence)."
            )

            raw_response = self.llm.generate(prompt)
            extracted = self._parse_response(raw_response)

            if tag != "untagged":
                for existing in self.semantic.get_by_convention_tag(tag):
                    self.semantic.delete(existing["id"])
                    total_superseded += 1
                for existing in self.procedural.get_by_convention_tag(tag):
                    self.procedural.delete(existing["id"])
                    total_superseded += 1

            for fact in extracted.get("facts", []):
                self.semantic.write(MemoryItem(
                    id="",
                    content=fact,
                    memory_type=MemoryType.SEMANTIC,
                    importance=0.8,
                    convention_tag=tag if tag != "untagged" else None,
                ))
                total_facts += 1

            for skill in extracted.get("skills", []):
                self.procedural.write(MemoryItem(
                    id="",
                    content=skill,
                    memory_type=MemoryType.PROCEDURAL,
                    importance=0.8,
                    convention_tag=tag if tag != "untagged" else None,
                ))
                total_skills += 1

        for item in unconsolidated:
            self.episodic.mark_consolidated(item["id"])

        return {
            "episodes_processed": len(unconsolidated),
            "facts_extracted": total_facts,
            "skills_extracted": total_skills,
            "facts_superseded": total_superseded,
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