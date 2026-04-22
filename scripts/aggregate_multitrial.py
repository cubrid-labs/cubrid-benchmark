from __future__ import annotations

import json
import statistics
from pathlib import Path
from typing import TypedDict, cast


ROOT = Path(__file__).resolve().parent.parent
RUN_ID = "2026-04-22_multitrial-baseline"
RUN_DIR = ROOT / "experiments/orm-overhead/runs" / RUN_ID
RAW_DIR = RUN_DIR / "raw"
DERIVED_DIR = RUN_DIR / "derived"
BASELINE_SUMMARY = (
    ROOT / "experiments/orm-overhead/runs/2026-04-21_post-native-ping/derived/summary.json"
)
WORKERS = ["raw_pycubrid", "sqlalchemy_core", "sqlalchemy_orm"]
TRIALS = [1, 2, 3, 4, 5]


class LatencySummary(TypedDict):
    p95_ns: int


class WorkerStep(TypedDict):
    name: str
    ops: int
    errors: int
    latency_summary: LatencySummary
    throughput_ops_s: float


class WorkerOutput(TypedDict):
    status: str
    steps: list[WorkerStep]


class TrialMetricStats(TypedDict):
    trial_values: list[float]
    median: float
    min: float
    max: float
    mean: float
    iqr: float
    q25: float
    q75: float


class OperationAggregate(TypedDict):
    ops: TrialMetricStats
    errors: TrialMetricStats
    throughput_ops_s: TrialMetricStats
    p95_ns: TrialMetricStats


class WorkerAverageAggregate(TypedDict):
    throughput_ops_s: TrialMetricStats
    p95_ns: TrialMetricStats


class SummaryDocument(TypedDict):
    run_id: str
    compares_to: str
    trials: int
    quartile_method: str
    workers: dict[str, dict[str, OperationAggregate]]
    worker_averages: dict[str, WorkerAverageAggregate]


class BaselineOperation(TypedDict):
    throughput_ops_s: float
    p95_ms: float


class BaselineSummary(TypedDict):
    workers: dict[str, dict[str, BaselineOperation]]


def load_worker_output(path: Path) -> WorkerOutput:
    with path.open("r", encoding="utf-8") as handle:
        return cast(WorkerOutput, json.load(handle))


def load_baseline_summary(path: Path) -> BaselineSummary:
    with path.open("r", encoding="utf-8") as handle:
        return cast(BaselineSummary, json.load(handle))


def compute_stats(values: list[float]) -> TrialMetricStats:
    sorted_values = sorted(values)
    quartiles = statistics.quantiles(sorted_values, n=4, method="inclusive")
    q1 = quartiles[0]
    q3 = quartiles[2]
    return {
        "trial_values": values,
        "median": statistics.median(sorted_values),
        "min": min(sorted_values),
        "max": max(sorted_values),
        "mean": statistics.fmean(sorted_values),
        "iqr": q3 - q1,
        "q25": q1,
        "q75": q3,
    }


def fmt_float(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def fmt_ms_from_ns(value: float, digits: int = 2) -> str:
    return fmt_float(value / 1_000_000, digits)


def get_step(output: WorkerOutput, operation: str) -> WorkerStep:
    for step in output["steps"]:
        if step["name"] == operation:
            return step
    raise KeyError(f"operation not found: {operation}")


def build_summary(raw_payloads: dict[str, dict[int, WorkerOutput]]) -> SummaryDocument:
    workers_summary: dict[str, dict[str, OperationAggregate]] = {}
    worker_averages: dict[str, WorkerAverageAggregate] = {}

    for worker, trial_payloads in raw_payloads.items():
        operation_names = [step["name"] for step in trial_payloads[1]["steps"]]
        operations_summary: dict[str, OperationAggregate] = {}

        per_trial_worker_ops: list[float] = []
        per_trial_worker_p95: list[float] = []

        for operation in operation_names:
            throughput_values: list[float] = []
            p95_values: list[float] = []
            ops_values: list[float] = []
            errors_values: list[float] = []

            for trial in TRIALS:
                step = get_step(trial_payloads[trial], operation)
                throughput_values.append(step["throughput_ops_s"])
                p95_values.append(float(step["latency_summary"]["p95_ns"]))
                ops_values.append(float(step["ops"]))
                errors_values.append(float(step["errors"]))

            operations_summary[operation] = {
                "ops": compute_stats(ops_values),
                "errors": compute_stats(errors_values),
                "throughput_ops_s": compute_stats(throughput_values),
                "p95_ns": compute_stats(p95_values),
            }

        for trial in TRIALS:
            trial_steps = trial_payloads[trial]["steps"]
            per_trial_worker_ops.append(
                statistics.fmean(step["throughput_ops_s"] for step in trial_steps)
            )
            per_trial_worker_p95.append(
                statistics.fmean(float(step["latency_summary"]["p95_ns"]) for step in trial_steps)
            )

        workers_summary[worker] = operations_summary
        worker_averages[worker] = {
            "throughput_ops_s": compute_stats(per_trial_worker_ops),
            "p95_ns": compute_stats(per_trial_worker_p95),
        }

    return {
        "run_id": RUN_ID,
        "compares_to": "2026-04-21_post-native-ping",
        "trials": len(TRIALS),
        "quartile_method": "inclusive",
        "workers": workers_summary,
        "worker_averages": worker_averages,
    }


def write_summary_md(summary: SummaryDocument) -> None:
    lines = [
        f"# {RUN_ID}",
        "",
        "> Five serial trials per worker using the exact same WorkerInput as 2026-04-21.",
        "> Statistics summarize trial-level `throughput_ops_s` and trial-level `p95_ns` only;",
        "> they do not recompute p95 from pooled latency samples.",
        "",
        "| operation | worker | ops/s median | ops/s [min..max] | ops/s IQR | p95 ms median | p95 ms [min..max] | p95 ms IQR |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for worker in WORKERS:
        for operation, metrics in summary["workers"][worker].items():
            throughput = metrics["throughput_ops_s"]
            p95_ns = metrics["p95_ns"]
            lines.append(
                "| {operation} | {worker} | {ops_med} | {ops_band} | {ops_iqr} | {p95_med} | {p95_band} | {p95_iqr} |".format(
                    operation=operation,
                    worker=worker,
                    ops_med=fmt_float(throughput["median"]),
                    ops_band="[{0}..{1}]".format(
                        fmt_float(throughput["min"]),
                        fmt_float(throughput["max"]),
                    ),
                    ops_iqr=fmt_float(throughput["iqr"]),
                    p95_med=fmt_ms_from_ns(p95_ns["median"]),
                    p95_band="[{0}..{1}]".format(
                        fmt_ms_from_ns(p95_ns["min"]),
                        fmt_ms_from_ns(p95_ns["max"]),
                    ),
                    p95_iqr=fmt_ms_from_ns(p95_ns["iqr"]),
                )
            )

    lines.extend(
        [
            "",
            "## Per-worker averages",
            "",
            "> Simple arithmetic mean across the six operations within each trial, then summarized across 5 trials.",
            "",
            "| worker | avg ops/s median | avg ops/s [min..max] | avg ops/s IQR | avg p95 ms median | avg p95 ms [min..max] | avg p95 ms IQR |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for worker in WORKERS:
        throughput = summary["worker_averages"][worker]["throughput_ops_s"]
        p95_ns = summary["worker_averages"][worker]["p95_ns"]
        lines.append(
            "| {worker} | {ops_med} | {ops_band} | {ops_iqr} | {p95_med} | {p95_band} | {p95_iqr} |".format(
                worker=worker,
                ops_med=fmt_float(throughput["median"]),
                ops_band="[{0}..{1}]".format(
                    fmt_float(throughput["min"]),
                    fmt_float(throughput["max"]),
                ),
                ops_iqr=fmt_float(throughput["iqr"]),
                p95_med=fmt_ms_from_ns(p95_ns["median"]),
                p95_band="[{0}..{1}]".format(
                    fmt_ms_from_ns(p95_ns["min"]),
                    fmt_ms_from_ns(p95_ns["max"]),
                ),
                p95_iqr=fmt_ms_from_ns(p95_ns["iqr"]),
            )
        )

    _ = (DERIVED_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_comparison_md(summary: SummaryDocument, baseline: BaselineSummary) -> None:
    lines = [
        f"# {RUN_ID} vs 2026-04-21_post-native-ping",
        "",
        "> Side-by-side of 5-trial medians versus the 2026-04-21 single trial.",
        "> `outside_band` means the 2026-04-21 single-trial value falls outside the 2026-04-22",
        "> five-trial [min..max] band and is therefore not representative of the repeated-run band.",
        "",
        "| operation | worker | 04-21 ops/s | 04-22 median ops/s | 04-22 ops/s band | ops/s status | 04-21 p95 ms | 04-22 median p95 ms | 04-22 p95 band | p95 status |",
        "|---|---|---:|---:|---:|---|---:|---:|---:|---|",
    ]

    outside_band_lines: list[str] = []

    for worker in WORKERS:
        for operation, baseline_metrics in baseline["workers"][worker].items():
            baseline_ops = baseline_metrics["throughput_ops_s"]
            baseline_p95_ms = baseline_metrics["p95_ms"]
            current = summary["workers"][worker][operation]
            ops_band = current["throughput_ops_s"]
            p95_band = current["p95_ns"]
            baseline_p95_ns = baseline_p95_ms * 1_000_000
            ops_outside = baseline_ops < ops_band["min"] or baseline_ops > ops_band["max"]
            p95_outside = baseline_p95_ns < p95_band["min"] or baseline_p95_ns > p95_band["max"]
            ops_status = "outside_band" if ops_outside else "within_band"
            p95_status = "outside_band" if p95_outside else "within_band"

            if ops_outside:
                outside_band_lines.append(
                    "- {worker} / {operation}: 04-21 ops/s {baseline_value} vs 04-22 band [{band_min}..{band_max}]".format(
                        worker=worker,
                        operation=operation,
                        baseline_value=fmt_float(baseline_ops),
                        band_min=fmt_float(ops_band["min"]),
                        band_max=fmt_float(ops_band["max"]),
                    )
                )
            if p95_outside:
                outside_band_lines.append(
                    "- {worker} / {operation}: 04-21 p95 {baseline_value} ms vs 04-22 band [{band_min}..{band_max}] ms".format(
                        worker=worker,
                        operation=operation,
                        baseline_value=fmt_float(baseline_p95_ms),
                        band_min=fmt_ms_from_ns(p95_band["min"]),
                        band_max=fmt_ms_from_ns(p95_band["max"]),
                    )
                )

            lines.append(
                "| {operation} | {worker} | {base_ops} | {cur_ops} | {ops_band_text} | {ops_status} | {base_p95} | {cur_p95} | {p95_band_text} | {p95_status} |".format(
                    operation=operation,
                    worker=worker,
                    base_ops=fmt_float(baseline_ops),
                    cur_ops=fmt_float(current["throughput_ops_s"]["median"]),
                    ops_band_text="[{0}..{1}]".format(
                        fmt_float(current["throughput_ops_s"]["min"]),
                        fmt_float(current["throughput_ops_s"]["max"]),
                    ),
                    ops_status=ops_status,
                    base_p95=fmt_float(baseline_p95_ms),
                    cur_p95=fmt_ms_from_ns(current["p95_ns"]["median"]),
                    p95_band_text="[{0}..{1}]".format(
                        fmt_ms_from_ns(current["p95_ns"]["min"]),
                        fmt_ms_from_ns(current["p95_ns"]["max"]),
                    ),
                    p95_status=p95_status,
                )
            )

    lines.extend(["", "## 04-21 single-trial values outside the 04-22 five-trial band", ""])
    if outside_band_lines:
        lines.extend(outside_band_lines)
    else:
        lines.append("- None")

    _ = (DERIVED_DIR / "comparison_vs_2026-04-21.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def main() -> None:
    raw_payloads: dict[str, dict[int, WorkerOutput]] = {}
    for worker in WORKERS:
        raw_payloads[worker] = {}
        for trial in TRIALS:
            path = RAW_DIR / f"worker_{worker}_trial{trial}.json"
            payload = load_worker_output(path)
            if payload["status"] != "ok":
                raise SystemExit(f"{path} status != ok")
            raw_payloads[worker][trial] = payload

    summary = build_summary(raw_payloads)
    baseline = load_baseline_summary(BASELINE_SUMMARY)

    _ = (DERIVED_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    write_summary_md(summary)
    write_comparison_md(summary, baseline)


if __name__ == "__main__":
    main()
