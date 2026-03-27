#!/usr/bin/env python3
"""Generate before/after comparison charts for the driver-comparison experiment."""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


BEFORE = {
    "connect": {"mean_ms": 2.244, "cv_pct": 13.2},
    "insert_execute": {"mean_ms": 7.811},
    "insert_commit": {"mean_ms": 49.825},
    "insert_total": {"mean_ms": 57.636},
    "select_pk_execute": {"mean_ms": 1.082},
    "select_pk_fetch": {"mean_ms": 0.002},
    "select_pk_total": {"mean_ms": 1.084},
    "select_full_execute": {"mean_ms": 14.894},
    "select_full_fetch": {"mean_ms": 96.047},
    "select_full_total": {"mean_ms": 110.940},
    "update_execute": {"mean_ms": 4.516},
    "update_commit": {"mean_ms": 47.082},
    "update_total": {"mean_ms": 51.598},
    "delete_execute": {"mean_ms": 4.364},
    "delete_commit": {"mean_ms": 48.343},
    "delete_total": {"mean_ms": 52.707},
}


def load_after(path: Path) -> dict:
    data = json.loads(path.read_text())
    return data["results"]


def pct_change(before: float, after: float) -> float:
    if before == 0:
        return 0.0
    return (after - before) / before * 100


def chart_phase_comparison(before: dict, after: dict, output: Path) -> None:
    phases = [
        ("Connect", "connect"),
        ("INSERT\nexecute", "insert_execute"),
        ("INSERT\ncommit", "insert_commit"),
        ("SELECT PK\ntotal", "select_pk_total"),
        ("SELECT 10K\nexecute", "select_full_execute"),
        ("SELECT 10K\nfetch", "select_full_fetch"),
        ("UPDATE\nexecute", "update_execute"),
        ("DELETE\nexecute", "delete_execute"),
    ]

    labels = [p[0] for p in phases]
    before_vals = [before[p[1]]["mean_ms"] for p in phases]
    after_vals = [after[p[1]]["mean_ms"] for p in phases]

    x = np.arange(len(labels))
    width = 0.35

    fig, ax = plt.subplots(figsize=(14, 6))
    bars_before = ax.bar(x - width / 2, before_vals, width, label="Before (bb687dc)",
                         color="#e74c3c", alpha=0.85)
    bars_after = ax.bar(x + width / 2, after_vals, width, label="After (16a8634)",
                        color="#2ecc71", alpha=0.85)

    for i, (bv, av) in enumerate(zip(before_vals, after_vals)):
        pct = pct_change(bv, av)
        color = "#2ecc71" if pct < 0 else "#e74c3c"
        ax.annotate(f"{pct:+.1f}%", xy=(x[i] + width / 2, av),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", fontsize=8, fontweight="bold", color=color)

    ax.set_ylabel("Latency (ms)")
    ax.set_title("pycubrid Phase-Decomposed: Before vs After Optimization")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output}")


def chart_select_10k_breakdown(before: dict, after: dict, output: Path) -> None:
    categories = ["Execute", "Fetch", "Total"]
    before_keys = ["select_full_execute", "select_full_fetch", "select_full_total"]

    before_vals = [before[k]["mean_ms"] for k in before_keys]
    after_vals = [after[k]["mean_ms"] for k in before_keys]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, before_vals, width, label="Before (bb687dc)",
           color="#e74c3c", alpha=0.85)
    ax.bar(x + width / 2, after_vals, width, label="After (16a8634)",
           color="#2ecc71", alpha=0.85)

    for i, (bv, av) in enumerate(zip(before_vals, after_vals)):
        pct = pct_change(bv, av)
        ax.annotate(f"{pct:+.1f}%", xy=(x[i] + width / 2, av),
                    xytext=(0, 5), textcoords="offset points",
                    ha="center", fontsize=10, fontweight="bold", color="#2ecc71")

    ax.set_ylabel("Latency (ms)")
    ax.set_title("SELECT 10K Rows: Before vs After (Primary Optimization Target)")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output}")


def chart_speedup_waterfall(before: dict, after: dict, output: Path) -> None:
    optimizations = [
        ("Baseline\n(before)", "select_full_fetch", True),
        ("After\noptimization", "select_full_fetch", False),
    ]

    fetch_before = before["select_full_fetch"]["mean_ms"]
    fetch_after = after["select_full_fetch"]["mean_ms"]
    saved = fetch_before - fetch_after
    pct_saved = saved / fetch_before * 100

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.bar(["Before", "After"], [fetch_before, fetch_after],
            color=["#e74c3c", "#2ecc71"], alpha=0.85, width=0.5)
    ax1.annotate(f"−{saved:.1f}ms\n({pct_saved:.1f}% faster)",
                 xy=(1, fetch_after), xytext=(0, 10), textcoords="offset points",
                 ha="center", fontsize=11, fontweight="bold", color="#2ecc71")
    ax1.set_ylabel("Fetch Latency (ms)")
    ax1.set_title("SELECT 10K Fetch Time")
    ax1.grid(axis="y", alpha=0.3)

    total_before = before["select_full_total"]["mean_ms"]
    total_after = after["select_full_total"]["mean_ms"]
    cubriddb_total = 39.364

    ax2.barh(["CUBRIDdb (C ext)", "pycubrid After", "pycubrid Before"],
             [cubriddb_total, total_after, total_before],
             color=["#3498db", "#2ecc71", "#e74c3c"], alpha=0.85, height=0.5)

    ratio_before = total_before / cubriddb_total
    ratio_after = total_after / cubriddb_total
    ax2.annotate(f"{ratio_before:.2f}×", xy=(total_before, 2),
                 xytext=(5, 0), textcoords="offset points",
                 va="center", fontsize=10, fontweight="bold")
    ax2.annotate(f"{ratio_after:.2f}×", xy=(total_after, 1),
                 xytext=(5, 0), textcoords="offset points",
                 va="center", fontsize=10, fontweight="bold", color="#2ecc71")

    ax2.set_xlabel("Total Latency (ms)")
    ax2.set_title("SELECT 10K Total: pycubrid vs CUBRIDdb")
    ax2.grid(axis="x", alpha=0.3)

    fig.suptitle("Optimization Impact: Dispatch Table + Pre-compiled Structs + Slice Fetch",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(output, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {output}")


def main() -> None:
    after_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "experiments/driver-comparison/runs/2026-03-27_after-parse-optimization/raw/phase_decomposed.json"
    )
    figures_dir = Path(
        "experiments/driver-comparison/runs/2026-03-27_after-parse-optimization/figures"
    )
    figures_dir.mkdir(parents=True, exist_ok=True)

    after = load_after(after_path)

    print("Generating charts...")
    chart_phase_comparison(BEFORE, after, figures_dir / "before_after_phases.png")
    chart_select_10k_breakdown(BEFORE, after, figures_dir / "select_10k_before_after.png")
    chart_speedup_waterfall(BEFORE, after, figures_dir / "optimization_impact.png")
    print("Done.")


if __name__ == "__main__":
    main()
