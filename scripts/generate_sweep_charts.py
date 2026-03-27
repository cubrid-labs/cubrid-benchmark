#!/usr/bin/env python3
"""Generate charts for the row-count sweep experiment."""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main() -> None:
    sweep_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "experiments/row-count-sweep/runs/2026-03-27_initial/raw/sweep.json"
    )
    figures_dir = Path(
        "experiments/row-count-sweep/runs/2026-03-27_initial/figures"
    )
    figures_dir.mkdir(parents=True, exist_ok=True)

    data = json.loads(sweep_path.read_text())
    sweep = data["sweep"]

    row_counts = [int(k) for k in sweep.keys()]
    execute_ms = [sweep[str(rc)]["execute"]["mean_ms"] for rc in row_counts]
    fetch_ms = [sweep[str(rc)]["fetch"]["mean_ms"] for rc in row_counts]
    total_ms = [sweep[str(rc)]["total"]["mean_ms"] for rc in row_counts]
    per_row_us = [fetch_ms[i] / row_counts[i] * 1000 for i in range(len(row_counts))]

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    ax1 = axes[0]
    ax1.plot(row_counts, total_ms, "o-", color="#2c3e50", linewidth=2, markersize=8, label="Total")
    ax1.plot(row_counts, fetch_ms, "s--", color="#e74c3c", linewidth=2, markersize=7, label="Fetch")
    ax1.plot(row_counts, execute_ms, "^--", color="#3498db", linewidth=2, markersize=7, label="Execute")
    ax1.set_xlabel("Row Count")
    ax1.set_ylabel("Latency (ms)")
    ax1.set_title("SELECT Latency vs Row Count")
    ax1.legend()
    ax1.grid(alpha=0.3)
    ax1.set_xscale("log")

    ax2 = axes[1]
    width = 0.35
    x = np.arange(len(row_counts))
    ax2.bar(x - width / 2, execute_ms, width, label="Execute", color="#3498db", alpha=0.85)
    ax2.bar(x + width / 2, fetch_ms, width, label="Fetch", color="#e74c3c", alpha=0.85)
    ax2.set_xlabel("Row Count")
    ax2.set_ylabel("Latency (ms)")
    ax2.set_title("Execute vs Fetch by Row Count")
    ax2.set_xticks(x)
    ax2.set_xticklabels([str(rc) for rc in row_counts])
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    for i, (e, f) in enumerate(zip(execute_ms, fetch_ms)):
        total = e + f
        fetch_pct = f / total * 100 if total > 0 else 0
        ax2.annotate(f"{fetch_pct:.0f}%", xy=(x[i] + width / 2, f),
                     xytext=(0, 3), textcoords="offset points",
                     ha="center", fontsize=8, fontweight="bold", color="#e74c3c")

    ax3 = axes[2]
    ax3.bar(range(len(row_counts)), per_row_us, color="#9b59b6", alpha=0.85, width=0.6)
    ax3.set_xlabel("Row Count")
    ax3.set_ylabel("Per-Row Fetch Cost (µs)")
    ax3.set_title("Amortized Per-Row Cost")
    ax3.set_xticks(range(len(row_counts)))
    ax3.set_xticklabels([str(rc) for rc in row_counts])
    ax3.grid(axis="y", alpha=0.3)

    for i, v in enumerate(per_row_us):
        ax3.annotate(f"{v:.1f}µs", xy=(i, v), xytext=(0, 3), textcoords="offset points",
                     ha="center", fontsize=9, fontweight="bold")

    fig.suptitle("pycubrid SELECT Fetch Scaling (200 iter, optimized build 16a8634)", y=1.02)
    fig.tight_layout()
    fig.savefig(figures_dir / "row_count_scaling.png", dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {figures_dir / 'row_count_scaling.png'}")


if __name__ == "__main__":
    main()
