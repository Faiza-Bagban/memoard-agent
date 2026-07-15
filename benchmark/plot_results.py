import csv
from collections import defaultdict

import matplotlib.pyplot as plt


def plot_session_scores(csv_path: str = "benchmark/results.csv", output_path: str = "benchmark/improvement_graph.png") -> None:
    """Plot pass rate per session from benchmark results.

    Args:
        csv_path: Path to the results CSV file.
        output_path: Path to save the output graph image.

    Returns:
        None
    """
    by_session = defaultdict(list)

    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            session = int(row["session"])
            passed = row["passed"] == "True"
            by_session[session].append(passed)

    sessions = sorted(by_session.keys())
    rates = [sum(by_session[s]) / len(by_session[s]) * 100 for s in sessions]

    labels = []
    for s in sessions:
        if s == 0:
            labels.append("Session 0\n(baseline)")
        elif s == 1:
            labels.append("Session 1\n(teach)")
        else:
            labels.append(f"Session {s}\n(recall)")

    plt.figure(figsize=(9, 5.5))
    plt.plot(sessions, rates, marker="o", linewidth=2.5, markersize=9, color="#2563eb")
    plt.fill_between(sessions, rates, alpha=0.1, color="#2563eb")

    for s, r in zip(sessions, rates):
        plt.annotate(f"{r:.0f}%", (s, r), textcoords="offset points", xytext=(0, 10), ha="center", fontweight="bold")

    plt.xticks(sessions, labels)
    plt.ylim(0, 110)
    plt.ylabel("Convention Match Rate (%)")
    plt.title("MemoardAgent: Convention Recall Across Sessions", fontsize=13, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.axvline(x=0.5, color="gray", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Graph saved to {output_path}")


if __name__ == "__main__":
    plot_session_scores()