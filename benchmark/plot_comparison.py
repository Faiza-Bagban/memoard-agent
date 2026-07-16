import csv
from collections import defaultdict

import matplotlib.pyplot as plt


def _load_session_rates(csv_path: str) -> tuple:
    """Compute pass rate per session from a results CSV.

    Args:
        csv_path: Path to the results CSV file.

    Returns:
        A tuple of (sorted session numbers, corresponding pass rates as percentages).
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
    return sessions, rates


def plot_comparison(
    with_memory_csv: str = "benchmark/results.csv",
    no_memory_csv: str = "benchmark/results_no_memory.csv",
    output_path: str = "benchmark/comparison_graph.png",
) -> None:
    """Plot memory-enabled vs memory-disabled pass rates side by side.

    Args:
        with_memory_csv: Path to the memory-enabled results CSV.
        no_memory_csv: Path to the memory-disabled (ablation) results CSV.
        output_path: Path to save the output graph image.

    Returns:
        None
    """
    sessions_mem, rates_mem = _load_session_rates(with_memory_csv)
    sessions_nomem, rates_nomem = _load_session_rates(no_memory_csv)

    labels = ["Session 0\n(baseline)", "Session 1\n(teach)", "Session 2\n(recall)",
              "Session 3\n(recall)", "Session 4\n(recall)", "Session 5\n(recall)"]

    plt.figure(figsize=(10, 6))

    plt.plot(sessions_mem, rates_mem, marker="o", linewidth=2.5, markersize=9,
              color="#2563eb", label="With Memory")
    plt.plot(sessions_nomem, rates_nomem, marker="s", linewidth=2.5, markersize=8,
              color="#dc2626", label="Without Memory (ablation)", linestyle="--")

    for s, r in zip(sessions_mem, rates_mem):
        plt.annotate(f"{r:.0f}%", (s, r), textcoords="offset points", xytext=(0, 12),
                      ha="center", fontweight="bold", color="#2563eb")
    for s, r in zip(sessions_nomem, rates_nomem):
        plt.annotate(f"{r:.0f}%", (s, r), textcoords="offset points", xytext=(0, -18),
                      ha="center", fontweight="bold", color="#dc2626")

    plt.xticks(sessions_mem, labels)
    plt.ylim(0, 110)
    plt.ylabel("Convention Match Rate (%)")
    plt.title("Memory vs No Memory: Convention Recall Across Sessions", fontsize=13, fontweight="bold")
    plt.legend(loc="center right")
    plt.grid(True, alpha=0.3)
    plt.axvline(x=0.5, color="gray", linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Comparison graph saved to {output_path}")


if __name__ == "__main__":
    plot_comparison()