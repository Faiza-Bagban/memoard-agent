import json
import csv
from collections import defaultdict

from src.agent.agent import MemoardAgent
from benchmark.scorer import score_answer


def load_questions(path: str = "benchmark/questions.json") -> list:
    """Load the question bank from disk.

    Args:
        path: Path to the questions JSON file.

    Returns:
        A list of question dicts.
    """
    with open(path, "r") as f:
        return json.load(f)


def run_benchmark(persist_path: str = "./chroma_db_benchmark", output_csv: str = "benchmark/results.csv") -> None:
    """Run every question through the agent in session order and score each answer.

    Args:
        persist_path: Where to store the agent's memory for this run.
        output_csv: Where to write the per-question results.

    Returns:
        None
    """
    questions = load_questions()
    agent = MemoardAgent(persist_path=persist_path, session_id="benchmark_run")

    rows = []
   
    for i, q in enumerate(questions, start=1):
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
    run_benchmark()