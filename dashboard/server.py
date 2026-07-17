import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import csv
from collections import defaultdict

from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from src.memory.stores import EpisodicStore, SemanticStore, ProceduralStore

app = FastAPI(title="MemoardAgent Dashboard API")

STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/", response_class=HTMLResponse)
def serve_index():
    """Serve the dashboard's main HTML page.

    Args:
        None

    Returns:
        The dashboard HTML content as a string.
    """
    return (STATIC_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/stats")
def get_stats(path: str = Query("./chroma_db_sleep")):
    """Return memory counts for each store type.

    Args:
        path: Path to the ChromaDB persistence directory.

    Returns:
        A dict with counts for episodic, semantic, and procedural stores.
    """
    episodic = EpisodicStore(path)
    semantic = SemanticStore(path)
    procedural = ProceduralStore(path)
    return {
        "episodic": len(episodic.all()),
        "semantic": len(semantic.all()),
        "procedural": len(procedural.all()),
    }


@app.get("/api/memory/{kind}")
def get_memory(kind: str, path: str = Query("./chroma_db_sleep")):
    """Return all items from a given memory store type.

    Args:
        kind: One of "episodic", "semantic", "procedural".
        path: Path to the ChromaDB persistence directory.

    Returns:
        A list of memory item dicts, or an empty list for an unknown kind.
    """
    stores = {"episodic": EpisodicStore, "semantic": SemanticStore, "procedural": ProceduralStore}
    if kind not in stores:
        return []
    return stores[kind](path).all()


@app.get("/api/benchmark")
def get_benchmark(run: str = Query("sleep")):
    """Return per-session pass rates from a benchmark results CSV.

    Args:
        run: Which benchmark run to load - "sleep", "memory", or "no_memory".

    Returns:
        A list of dicts with session number and pass rate percentage.
    """
    file_map = {
        "sleep": "benchmark/results_sleep.csv",
        "memory": "benchmark/results.csv",
        "no_memory": "benchmark/results_no_memory.csv",
    }
    p = Path(file_map.get(run, file_map["sleep"]))
    if not p.exists():
        return []

    by_session = defaultdict(list)
    with open(p, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            by_session[int(row["session"])].append(row["passed"] == "True")

    return [
        {"session": s, "rate": sum(v) / len(v) * 100}
        for s, v in sorted(by_session.items())
    ]

@app.get("/api/sleep-log")
def get_sleep_log(log_path: str = Query("benchmark/sleep_log.json")):
    """Return the full sleep-cycle history log.

    Args:
        log_path: Path to the JSON sleep-cycle log file.

    Returns:
        A list of sleep-cycle log entries, or an empty list if the file doesn't exist.
    """
    p = Path(log_path)
    if not p.exists():
        return []
    import json
    return json.loads(p.read_text(encoding="utf-8"))


class ChatRequest(BaseModel):
    """Request body for the chat endpoint."""
    question: str
    persist_path: str = "./chroma_db_sleep"
    session_id: str = "dashboard_chat"


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Send a question to the agent and return its answer.

    Args:
        req: The chat request containing question, persist_path, and session_id.

    Returns:
        A dict with the agent's answer text.
    """
    from src.agent.agent import MemoardAgent
    agent = MemoardAgent(persist_path=req.persist_path, session_id=req.session_id)
    answer = agent.answer(req.question)
    return {"answer": answer}