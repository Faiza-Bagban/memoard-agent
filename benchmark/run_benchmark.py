import json
import csv
import argparse
from collections import defaultdict

from src.agent.agent import MemoardAgent
from benchmark.scorer import score_answer
from src.consolidation.sleep_cycle import run_sleep_cycle


def load_questions(path: str = "benchmark/questions.json") -> list:
    """Load the question bank from disk.

    Args:
        path: Path to the questions JSON file.

    Returns:
        A list of question dicts.
    """
    with open(path, "r") as f:
        return json.load(f)


def run_benchmark(persist_path: str, output_csv: str, memory_enabled: bool, sleep_enabled: bool = False) -> None:
    """Run every question through the agent in session order, optionally sleeping between sessions.

    Args:
        persist_path: Where to store the agent's memory for this run.
        output_csv: Where to write the per-question results.
        memory_enabled: Whether the agent uses memory retrieval and storage.
        sleep_enabled: Whether to run a consolidation+forgetting cycle after each session.

    Returns:
        None
    """
    questions = load_questions()
    agent = MemoardAgent(persist_path=persist_path, session_id="benchmark_run", memory_enabled=memory_enabled)

    rows = []
    current_session = None
    for i, q in enumerate(questions, start=1):
        if sleep_enabled and current_session is not None and q["session"] != current_session:
            print(f"  [sleeping after session {current_session}...]")
            summary = run_sleep_cycle(persist_path)
            print(f"  {summary}")
        current_session = q["session"]

        print(f"[{i}/{len(questions)}] session={q['session']} {q['session_type']} - {q['convention']}")
        try:
            answer = agent.answer(q["question"], convention_tag=q["convention"])
            passed = score_answer(answer, q["convention"], q["expected_pattern"])
            answer_text = answer.replace("\n", " ")[:200]
        except Exception as e:
            print(f"  -> ERROR: {e}")
            passed = False
            answer_text = f"ERROR: {e}"
        print(f"  -> {'PASS' if passed else 'FAIL'}")
        rows.append({
            "order": i,
            "id": q["id"],
            "session": q["session"],
            "session_type": q["session_type"],
            "convention": q["convention"],
            "passed": passed,
            "answer": answer_text,
        })

    if sleep_enabled:
        print("  [final sleep cycle...]")
        summary = run_sleep_cycle(persist_path)
        print(f"  {summary}")

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["order", "id", "session", "session_type", "convention", "passed", "answer"])
        writer.writeheader()
        writer.writerows(rows)

    print("\n=== Per-session pass rate ===")
    by_session = defaultdict(list)
    for r in rows:
        by_session[r["session"]].append(r["passed"])

    for session_num in sorted(by_session.keys()):
        passed_list = by_session[session_num]
        rate = sum(passed_list) / len(passed_list)
        print(f"Session {session_num}: {rate:.0%} ({sum(passed_list)}/{len(passed_list)})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-memory", action="store_true", help="Run without memory (ablation baseline)")
    parser.add_argument("--sleep", action="store_true", help="Run consolidation+forgetting after each session")
    args = parser.parse_args()

    if args.no_memory:
        run_benchmark(
            persist_path="./chroma_db_ablation",
            output_csv="benchmark/results_no_memory.csv",
            memory_enabled=False,
        )
    elif args.sleep:
        run_benchmark(
            persist_path="./chroma_db_sleep",
            output_csv="benchmark/results_sleep.csv",
            memory_enabled=True,
            sleep_enabled=True,
        )
    else:
        run_benchmark(
            persist_path="./chroma_db_benchmark",
            output_csv="benchmark/results.csv",
            memory_enabled=True,
        )