import json
from datetime import datetime, timezone
from pathlib import Path

from src.consolidation.consolidator import Consolidator
from src.consolidation.forgetting import ForgettingPolicy


def run_sleep_cycle(
    persist_path: str = "./chroma_db",
    forget_threshold: float = 0.3,
    log_path: str = "benchmark/sleep_log.json",
) -> dict:
    """Run one full sleep cycle: consolidate raw episodes, then apply forgetting, then log it.

    Args:
        persist_path: Path to the ChromaDB store to operate on.
        forget_threshold: Minimum retention score for a memory to survive forgetting.
        log_path: Path to the JSON file where sleep-cycle history is appended.

    Returns:
        A dict with consolidation and forgetting summaries.
    """
    consolidator = Consolidator(persist_path)
    consolidation_summary = consolidator.consolidate()

    forgetting_policy = ForgettingPolicy(persist_path, forget_threshold=forget_threshold)
    forgetting_summary = forgetting_policy.run()

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "persist_path": persist_path,
        "consolidation": consolidation_summary,
        "forgetting": forgetting_summary,
    }
    _append_log(log_path, entry)

    return {
        "consolidation": consolidation_summary,
        "forgetting": forgetting_summary,
    }


def _append_log(log_path: str, entry: dict) -> None:
    """Append one sleep-cycle log entry to the JSON log file.

    Args:
        log_path: Path to the JSON log file.
        entry: The log entry dict to append.

    Returns:
        None
    """
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    log = []
    if path.exists():
        try:
            log = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            log = []

    log.append(entry)
    path.write_text(json.dumps(log, indent=2), encoding="utf-8")