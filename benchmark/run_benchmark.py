import json
import csv

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
    """Run every question through the agent in order and score each answer.

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
        print(f"[{i}/{len(questions)}] {q['session_type']} - {q['convention']}")
        answer = agent.answer(q["question"], convention_tag=q["convention"])
        passed = score_answer(answer, q["convention"], q["expected_pattern"])
        print(f"  -> {'PASS' if passed else 'FAIL'}")
        rows.append({
            "order": i,
            "id": q["id"],
            "session_type": q["session_type"],
            "convention": q["convention"],
            "passed": passed,
            "answer": answer.replace("\n", " ")[:200],
        })

    with open(output_csv, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["order", "id", "session_type", "convention", "passed", "answer"])
        writer.writeheader()
        writer.writerows(rows)

    recall_rows = [r for r in rows if r["session_type"] == "test_recall"]
    recall_pass_rate = sum(r["passed"] for r in recall_rows) / len(recall_rows) if recall_rows else 0
    print(f"\nRecall pass rate: {recall_pass_rate:.0%}")


if __name__ == "__main__":
    run_benchmark()