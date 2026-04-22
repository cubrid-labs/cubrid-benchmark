from __future__ import annotations

import json
import random
import statistics
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
RUN_ID = "2026-04-22_native-ping-hotpath"
RUN_DIR = ROOT / "experiments/orm-overhead/runs" / RUN_ID
RAW_DIR = RUN_DIR / "raw"
DERIVED_DIR = RUN_DIR / "derived"
WORKERS = ["raw_pycubrid_ping", "sqlalchemy_core_ping", "sqlalchemy_orm_ping"]
ARMS = ["native", "select1"]
TRIALS = [1, 2, 3, 4, 5, 6, 7]
BOOTSTRAP_RESAMPLES = 10000


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def quantile(sorted_values: list[float], q: float) -> float:
    if not sorted_values:
        return 0.0
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = (len(sorted_values) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(sorted_values) - 1)
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def compute_stats(values: list[float]) -> dict[str, Any]:
    ordered = sorted(values)
    return {
        "trial_values": values,
        "median": statistics.median(ordered),
        "iqr": quantile(ordered, 0.75) - quantile(ordered, 0.25),
        "min": min(ordered),
        "max": max(ordered),
        "q25": quantile(ordered, 0.25),
        "q75": quantile(ordered, 0.75),
    }


def fmt_float(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}"


def fmt_ms_from_ns(value: float, digits: int = 3) -> str:
    return fmt_float(value / 1_000_000.0, digits)


def delta_pct(native_value: float, select1_value: float) -> float:
    if select1_value == 0:
        return 0.0
    return ((native_value - select1_value) / select1_value) * 100.0


def bootstrap_ci(values: list[float], seed: int) -> dict[str, float]:
    rng = random.Random(seed)
    resampled_medians: list[float] = []
    for _ in range(BOOTSTRAP_RESAMPLES):
        sample = [values[rng.randrange(len(values))] for _ in values]
        resampled_medians.append(statistics.median(sample))
    ordered = sorted(resampled_medians)
    return {
        "low": quantile(ordered, 0.025),
        "high": quantile(ordered, 0.975),
    }


def get_step(payload: dict[str, Any], step_name: str) -> dict[str, Any]:
    for step in payload["steps"]:
        if step["name"] == step_name:
            return step
    raise KeyError("missing step {0}".format(step_name))


def threshold_for_step(step_name: str) -> float:
    if step_name == "ping_only":
        return 20.0
    return 5.0


def load_payloads() -> dict[str, dict[str, dict[int, dict[str, Any]]]]:
    payloads: dict[str, dict[str, dict[int, dict[str, Any]]]] = {}
    for worker in WORKERS:
        payloads[worker] = {}
        for arm in ARMS:
            payloads[worker][arm] = {}
            for trial in TRIALS:
                path = RAW_DIR / "worker_{0}_{1}_trial{2}.json".format(worker, arm, trial)
                payload = load_json(path)
                if payload.get("status") != "ok":
                    raise SystemExit("{0} status != ok".format(path))
                payloads[worker][arm][trial] = payload
    return payloads


def build_summary(payloads: dict[str, dict[str, dict[int, dict[str, Any]]]]) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "run_id": RUN_ID,
        "trials": len(TRIALS),
        "workers": {},
    }
    for worker in WORKERS:
        worker_summary: dict[str, Any] = {}
        step_names = [step["name"] for step in payloads[worker][ARMS[0]][TRIALS[0]]["steps"]]
        for step_name in step_names:
            worker_summary[step_name] = {}
            for arm in ARMS:
                throughput_values: list[float] = []
                p50_values: list[float] = []
                p95_values: list[float] = []
                errors_values: list[float] = []
                for trial in TRIALS:
                    step = get_step(payloads[worker][arm][trial], step_name)
                    throughput_values.append(float(step["throughput_ops_s"]))
                    p50_values.append(float(step["latency_summary"]["p50_ns"]))
                    p95_values.append(float(step["latency_summary"]["p95_ns"]))
                    errors_values.append(float(step["errors"]))
                worker_summary[step_name][arm] = {
                    "throughput_ops_s": compute_stats(throughput_values),
                    "p50_ns": compute_stats(p50_values),
                    "p95_ns": compute_stats(p95_values),
                    "errors": compute_stats(errors_values),
                }
        summary["workers"][worker] = worker_summary
    return summary


def build_paired_deltas(
    payloads: dict[str, dict[str, dict[int, dict[str, Any]]]],
) -> dict[str, Any]:
    pairs: list[dict[str, Any]] = []
    by_step: dict[str, dict[str, Any]] = {}
    for worker in WORKERS:
        step_names = [step["name"] for step in payloads[worker][ARMS[0]][TRIALS[0]]["steps"]]
        by_step[worker] = {}
        for step_name in step_names:
            throughput_deltas: list[float] = []
            p50_deltas: list[float] = []
            p95_deltas: list[float] = []
            error_pairs: list[dict[str, Any]] = []
            for trial in TRIALS:
                native_step = get_step(payloads[worker]["native"][trial], step_name)
                select1_step = get_step(payloads[worker]["select1"][trial], step_name)
                throughput_delta = delta_pct(
                    float(native_step["throughput_ops_s"]),
                    float(select1_step["throughput_ops_s"]),
                )
                p50_delta = delta_pct(
                    float(native_step["latency_summary"]["p50_ns"]),
                    float(select1_step["latency_summary"]["p50_ns"]),
                )
                p95_delta = delta_pct(
                    float(native_step["latency_summary"]["p95_ns"]),
                    float(select1_step["latency_summary"]["p95_ns"]),
                )
                throughput_deltas.append(throughput_delta)
                p50_deltas.append(p50_delta)
                p95_deltas.append(p95_delta)
                error_pair = {
                    "native": int(native_step["errors"]),
                    "select1": int(select1_step["errors"]),
                }
                error_pairs.append(error_pair)
                pairs.append(
                    {
                        "worker": worker,
                        "step": step_name,
                        "trial": trial,
                        "throughput_delta_pct": throughput_delta,
                        "p50_delta_pct": p50_delta,
                        "p95_delta_pct": p95_delta,
                        "errors": error_pair,
                    }
                )

            throughput_median = statistics.median(throughput_deltas)
            p50_median = statistics.median(p50_deltas)
            p95_median = statistics.median(p95_deltas)
            throughput_ci = bootstrap_ci(
                throughput_deltas, seed=1000 + len(step_name) + len(worker)
            )
            p50_ci = bootstrap_ci(p50_deltas, seed=2000 + len(step_name) + len(worker))
            p95_ci = bootstrap_ci(p95_deltas, seed=3000 + len(step_name) + len(worker))

            throughput_improvement = throughput_median
            p50_improvement = -p50_median
            threshold = threshold_for_step(step_name)
            ci_excludes_zero = False
            if throughput_improvement >= threshold and throughput_ci["low"] > 0.0:
                ci_excludes_zero = True
            if p50_improvement >= threshold and p50_ci["high"] < 0.0:
                ci_excludes_zero = True

            p95_regression = p95_median > 3.0 and p95_ci["low"] > 0.0
            any_errors = any(pair["native"] != 0 or pair["select1"] != 0 for pair in error_pairs)

            if ci_excludes_zero and not p95_regression and not any_errors:
                verdict = "WIN"
            elif (
                (throughput_median <= -threshold and throughput_ci["high"] < 0.0)
                or (p50_median >= threshold and p50_ci["low"] > 0.0)
                or p95_regression
                or any_errors
            ):
                verdict = "REGRESSION"
            else:
                verdict = "NO_WIN"

            by_step[worker][step_name] = {
                "throughput_delta_pct": {
                    "trial_values": throughput_deltas,
                    "median": throughput_median,
                    "bootstrap_95_ci": throughput_ci,
                },
                "p50_delta_pct": {
                    "trial_values": p50_deltas,
                    "median": p50_median,
                    "bootstrap_95_ci": p50_ci,
                },
                "p95_delta_pct": {
                    "trial_values": p95_deltas,
                    "median": p95_median,
                    "bootstrap_95_ci": p95_ci,
                },
                "threshold_pct": threshold,
                "errors": error_pairs,
                "verdict": verdict,
            }
    return {
        "run_id": RUN_ID,
        "pairs": pairs,
        "by_step": by_step,
    }


def write_summary_md(summary: dict[str, Any]) -> None:
    lines = [
        "# {0}".format(RUN_ID),
        "",
        "> Per-arm summary across 7 paired trials.",
        "",
        "| worker | step | arm | ops/s median | ops/s [min..max] | ops/s IQR | p50 ms median | p50 ms [min..max] | p50 ms IQR | p95 ms median | errors median |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for worker in WORKERS:
        for step_name, step_summary in summary["workers"][worker].items():
            for arm in ARMS:
                throughput = step_summary[arm]["throughput_ops_s"]
                p50 = step_summary[arm]["p50_ns"]
                p95 = step_summary[arm]["p95_ns"]
                errors = step_summary[arm]["errors"]
                lines.append(
                    "| {0} | {1} | {2} | {3} | [{4}..{5}] | {6} | {7} | [{8}..{9}] | {10} | {11} | {12} |".format(
                        worker,
                        step_name,
                        arm,
                        fmt_float(throughput["median"]),
                        fmt_float(throughput["min"]),
                        fmt_float(throughput["max"]),
                        fmt_float(throughput["iqr"]),
                        fmt_ms_from_ns(p50["median"]),
                        fmt_ms_from_ns(p50["min"]),
                        fmt_ms_from_ns(p50["max"]),
                        fmt_ms_from_ns(p50["iqr"]),
                        fmt_ms_from_ns(p95["median"]),
                        fmt_float(errors["median"], 0),
                    )
                )
    (DERIVED_DIR / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def classify_run(paired: dict[str, Any]) -> str:
    raw_ping = paired["by_step"]["raw_pycubrid_ping"]["ping_only"]
    raw_mechanism_win = raw_ping["verdict"] == "WIN"
    hot_path_win = False
    for worker, step_name in [
        ("sqlalchemy_core_ping", "checkout_select_by_pk"),
        ("sqlalchemy_orm_ping", "session_select_by_pk"),
    ]:
        if paired["by_step"][worker][step_name]["verdict"] == "WIN":
            hot_path_win = True
    if raw_mechanism_win and hot_path_win:
        return "practical app-level win"
    if raw_mechanism_win:
        return "mechanism-only win"
    return "no measurable win"


def write_comparison_md(paired: dict[str, Any]) -> None:
    overall = classify_run(paired)
    lines = [
        "# {0}".format(RUN_ID),
        "",
        "> Paired same-version A/B: `native` CHECK_CAS ping vs forced `select1` ping path.",
        "> Verdict uses bootstrap 95% CI on paired trial deltas. Throughput delta > 0 is good; p50 delta < 0 is good.",
        "",
        "## Overall classification",
        "",
        "**{0}**".format(overall),
        "",
        "| worker | step | throughput median delta % | throughput 95% CI | p50 median delta % | p50 95% CI | p95 median delta % | p95 95% CI | verdict |",
        "|---|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for worker in WORKERS:
        for step_name, stats in paired["by_step"][worker].items():
            throughput = stats["throughput_delta_pct"]
            p50 = stats["p50_delta_pct"]
            p95 = stats["p95_delta_pct"]
            lines.append(
                "| {0} | {1} | {2} | [{3}..{4}] | {5} | [{6}..{7}] | {8} | [{9}..{10}] | {11} |".format(
                    worker,
                    step_name,
                    fmt_float(throughput["median"]),
                    fmt_float(throughput["bootstrap_95_ci"]["low"]),
                    fmt_float(throughput["bootstrap_95_ci"]["high"]),
                    fmt_float(p50["median"]),
                    fmt_float(p50["bootstrap_95_ci"]["low"]),
                    fmt_float(p50["bootstrap_95_ci"]["high"]),
                    fmt_float(p95["median"]),
                    fmt_float(p95["bootstrap_95_ci"]["low"]),
                    fmt_float(p95["bootstrap_95_ci"]["high"]),
                    stats["verdict"],
                )
            )
    (DERIVED_DIR / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payloads = load_payloads()
    summary = build_summary(payloads)
    paired = build_paired_deltas(payloads)
    (DERIVED_DIR / "summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )
    (DERIVED_DIR / "paired_deltas.json").write_text(
        json.dumps(paired, indent=2) + "\n", encoding="utf-8"
    )
    write_summary_md(summary)
    write_comparison_md(paired)


if __name__ == "__main__":
    main()
