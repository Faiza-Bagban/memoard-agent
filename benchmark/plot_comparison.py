import csv
import os
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


def plot_three_way_comparison(
    with_memory_csv: str = "benchmark/results.csv",
    no_memory_csv: str = "benchmark/results_no_memory.csv",
    sleep_csv: str = "benchmark/results_sleep.csv",
    output_path: str = "benchmark/three_way_comparison.png",
) -> None:
    """Plot no-memory vs memory-only vs memory+sleep pass rates on one chart.

    Args:
        with_memory_csv: Path to the memory-only results CSV.
        no_memory_csv: Path to the memory-disabled (ablation) results CSV.
        sleep_csv: Path to the full sleep-cycle (consolidation+forgetting) results CSV.
        output_path: Path to save the output graph image.

    Returns:
        None
    """
    labels = ["Session 0\n(baseline)", "Session 1\n(teach)", "Session 2\n(recall)",
              "Session 3\n(recall)", "Session 4\n(recall)", "Session 5\n(recall)"]

    plt.figure(figsize=(11, 6.5))

    sessions_nomem, rates_nomem = _load_session_rates(no_memory_csv)
    plt.plot(sessions_nomem, rates_nomem, marker="s", linewidth=2, markersize=7,
              color="#dc2626", label="No Memory", linestyle="--", alpha=0.85)

    sessions_mem, rates_mem = _load_session_rates(with_memory_csv)
    plt.plot(sessions_mem, rates_mem, marker="o", linewidth=2, markersize=8,
              color="#f59e0b", label="Memory Only (no sleep)", linestyle="-.", alpha=0.9)

    if os.path.exists(sleep_csv):
        sessions_sleep, rates_sleep = _load_session_rates(sleep_csv)
        plt.plot(sessions_sleep, rates_sleep, marker="D", linewidth=2.8, markersize=8,
                  color="#16a34a", label="Memory + Sleep (consolidation+forgetting)")
        for s, r in zip(sessions_sleep, rates_sleep):
            plt.annotate(f"{r:.0f}%", (s, r), textcoords="offset points", xytext=(0, 12),
                          ha="center", fontweight="bold", color="#16a34a", fontsize=9)

    plt.xticks(sessions_mem, labels)
    plt.ylim(0, 115)
    plt.ylabel("Convention Match Rate (%)")
    plt.title("Memory Architecture Ablation: No Memory vs Memory vs Memory+Sleep", fontsize=12.5, fontweight="bold")
    plt.legend(loc="lower right")
    plt.grid(True, alpha=0.3)
    plt.axvline(x=0.5, color="gray", linestyle=":", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    print(f"Three-way comparison graph saved to {output_path}")


if __name__ == "__main__":
    plot_three_way_comparison()