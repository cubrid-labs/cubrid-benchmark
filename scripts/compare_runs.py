# pyright: basic
from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Mapping
from pathlib import Path

EXIT_PASS = 0
EXIT_REGRESSION = 1
EXIT_ERROR = 2

RESULT_PRIORITY = (
    "results.json",
    "summary.json",
    "normalized_results.json",
    "python_tier1.json",
)


def _parse_scalar(raw_value: str) -> object:
    value = raw_value.strip()
    if not value:
        return ""
    if value in {"null", "Null", "NULL"}:
        return None
    if value in {"true", "True"}:
        return True
    if value in {"false", "False"}:
        return False
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        if any(marker in value for marker in (".", "e", "E")):
            return float(value)
        return int(value)
    except ValueError:
        return value


def _parse_run_yaml(path: Path) -> dict[str, object]:
    root: dict[str, object] = {}
    stack: list[tuple[int, dict[str, object]]] = [(-1, root)]

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        if ":" not in stripped:
            continue

        key, raw_value = stripped.split(":", 1)
        value = raw_value.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()

        current = stack[-1][1]
        if not value:
            child: dict[str, object] = {}
            current[key] = child
            stack.append((indent, child))
            continue

        current[key] = _parse_scalar(value.split("#", 1)[0].rstrip())

    return root


def _coerce_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        if math.isfinite(number):
            return number
    return None


def _coerce_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return default


def _pytest_ops_value(stats: Mapping[str, object]) -> float | None:
    ops = _coerce_float(stats.get("ops"))
    if ops is not None:
        return ops

    mean = _coerce_float(stats.get("mean"))
    if mean is not None and mean > 0:
        return 1.0 / mean

    return None


def _normalize_named_results(entries: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    operations: dict[str, dict[str, object]] = {}
    for entry in entries:
        name = entry.get("name")
        value = _coerce_float(entry.get("value"))
        if not isinstance(name, str) or value is None:
            continue
        operations[name] = {
            "name": name,
            "value": value,
            "unit": entry.get("unit", "ops/sec"),
            "source": "normalized",
        }
    return operations


def _extract_custom_results(payload: Mapping[str, object]) -> dict[str, dict[str, object]]:
    results = payload.get("results")
    if not isinstance(results, Mapping):
        return {}

    operations: dict[str, dict[str, object]] = {}
    for name, metrics in results.items():
        if not isinstance(name, str) or not isinstance(metrics, Mapping):
            continue

        value = None
        unit = "ops/sec"
        for metric_name, metric_unit in (("ops_per_sec", "ops/sec"), ("scans_per_sec", "scans/sec")):
            metric_value = _coerce_float(metrics.get(metric_name))
            if metric_value is not None:
                value = metric_value
                unit = metric_unit
                break

        if value is None:
            continue

        operations[name] = {
            "name": name,
            "value": value,
            "unit": unit,
            "source": "raw-results",
        }
    return operations


def _extract_pytest_results(payload: Mapping[str, object]) -> dict[str, dict[str, object]]:
    benchmarks = payload.get("benchmarks")
    if not isinstance(benchmarks, list):
        return {}

    operations: dict[str, dict[str, object]] = {}
    for entry in benchmarks:
        if not isinstance(entry, Mapping):
            continue
        name = entry.get("name")
        stats = entry.get("stats")
        if not isinstance(name, str) or not isinstance(stats, Mapping):
            continue

        value = _pytest_ops_value(stats)
        if value is None:
            continue

        operations[name] = {
            "name": name,
            "value": round(value, 4),
            "unit": "ops/sec",
            "source": "pytest-benchmark",
        }

    return operations


def _load_operations(path: Path) -> dict[str, dict[str, object]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        operations = _normalize_named_results([entry for entry in payload if isinstance(entry, dict)])
    elif isinstance(payload, Mapping):
        operations = _extract_custom_results(payload)
        if not operations:
            operations = _extract_pytest_results(payload)
    else:
        operations = {}

    if not operations:
        raise ValueError(f"Could not extract comparable benchmark operations from {path}")

    return operations


def _find_results_json(run_dir: Path, run_meta: Mapping[str, object]) -> Path:
    artifacts = run_meta.get("artifacts")
    raw_dir_name = "raw"
    if isinstance(artifacts, Mapping):
        candidate = artifacts.get("raw_dir")
        if isinstance(candidate, str) and candidate.strip():
            raw_dir_name = candidate.strip()

    raw_dir = run_dir / raw_dir_name
    if not raw_dir.is_dir():
        raise FileNotFoundError(f"Raw results directory not found: {raw_dir}")

    candidates = sorted(raw_dir.glob("*.json"))
    if not candidates:
        raise FileNotFoundError(f"No JSON result files found in {raw_dir}")

    for name in RESULT_PRIORITY:
        for path in candidates:
            if path.name == name:
                return path

    if len(candidates) == 1:
        return candidates[0]

    raise ValueError(
        f"Ambiguous raw result file in {raw_dir}; expected one JSON file or one of {RESULT_PRIORITY}"
    )


def _load_run(run_dir: Path) -> dict[str, object]:
    run_yaml_path = run_dir / "run.yaml"
    if not run_yaml_path.is_file():
        raise FileNotFoundError(f"run.yaml not found in {run_dir}")

    run_meta = _parse_run_yaml(run_yaml_path)
    results_path = _find_results_json(run_dir, run_meta)
    operations = _load_operations(results_path)

    return {
        "dir": str(run_dir),
        "run_yaml_path": str(run_yaml_path),
        "results_path": str(results_path),
        "run_id": run_meta.get("run_id", run_dir.name),
        "date": run_meta.get("date"),
        "role": run_meta.get("role"),
        "compares_to": run_meta.get("compares_to"),
        "comparable_group": run_meta.get("comparable_group"),
        "operations": operations,
    }


def _status_for_change(percent_change: float, alert_threshold: float, fail_threshold: float) -> str:
    if percent_change <= -fail_threshold:
        return "fail"
    if percent_change <= -alert_threshold:
        return "alert"
    if percent_change > 0:
        return "improved"
    return "neutral"


def _compare_runs(
    baseline: Mapping[str, object],
    candidate: Mapping[str, object],
    alert_threshold: float,
    fail_threshold: float,
) -> dict[str, object]:
    baseline_group = baseline.get("comparable_group")
    candidate_group = candidate.get("comparable_group")
    if baseline_group != candidate_group:
        raise ValueError(
            "Runs are not comparable: comparable_group mismatch "
            f"({baseline_group!r} != {candidate_group!r})"
        )

    baseline_ops = baseline["operations"]
    candidate_ops = candidate["operations"]
    if not isinstance(baseline_ops, dict) or not isinstance(candidate_ops, dict):
        raise ValueError("Invalid operation data extracted from run results")

    baseline_names = set(baseline_ops)
    candidate_names = set(candidate_ops)
    if baseline_names != candidate_names:
        missing_in_candidate = sorted(baseline_names - candidate_names)
        missing_in_baseline = sorted(candidate_names - baseline_names)
        details: list[str] = []
        if missing_in_candidate:
            details.append(f"missing in candidate: {', '.join(missing_in_candidate)}")
        if missing_in_baseline:
            details.append(f"missing in baseline: {', '.join(missing_in_baseline)}")
        raise ValueError(f"Run operations do not match ({'; '.join(details)})")

    operations: list[dict[str, object]] = []
    counts = {"improved": 0, "neutral": 0, "alert": 0, "fail": 0}

    for name in sorted(baseline_names):
        baseline_entry = baseline_ops[name]
        candidate_entry = candidate_ops[name]
        baseline_value = _coerce_float(baseline_entry.get("value"))
        candidate_value = _coerce_float(candidate_entry.get("value"))
        if baseline_value is None or candidate_value is None:
            raise ValueError(f"Operation {name} has a non-numeric benchmark value")
        if baseline_value == 0:
            raise ValueError(f"Operation {name} has a zero baseline value; cannot compute percent change")

        absolute_delta = candidate_value - baseline_value
        percent_change = (absolute_delta / baseline_value) * 100.0
        status = _status_for_change(percent_change, alert_threshold, fail_threshold)
        counts[status] += 1

        operations.append(
            {
                "name": name,
                "unit": baseline_entry.get("unit") or candidate_entry.get("unit") or "ops/sec",
                "baseline": round(baseline_value, 4),
                "candidate": round(candidate_value, 4),
                "absolute_delta": round(absolute_delta, 4),
                "percent_change": round(percent_change, 2),
                "status": status,
            }
        )

    overall_status = "pass"
    exit_code = EXIT_PASS
    if counts["fail"]:
        overall_status = "fail"
        exit_code = EXIT_REGRESSION
    elif counts["alert"]:
        overall_status = "alert"
        exit_code = EXIT_REGRESSION

    return {
        "provenance": {
            "baseline_run_id": baseline.get("run_id"),
            "baseline_date": baseline.get("date"),
            "baseline_results_path": baseline.get("results_path"),
            "candidate_run_id": candidate.get("run_id"),
            "candidate_date": candidate.get("date"),
            "candidate_results_path": candidate.get("results_path"),
            "comparable_group": baseline_group,
        },
        "thresholds": {
            "alert_regression_percent": alert_threshold,
            "fail_regression_percent": fail_threshold,
        },
        "summary": {
            "total_operations": len(operations),
            "improved": counts["improved"],
            "neutral": counts["neutral"],
            "alert_regressions": counts["alert"],
            "fail_regressions": counts["fail"],
            "overall_status": overall_status,
            "exit_code": exit_code,
        },
        "operations": operations,
    }


def _write_output(report: Mapping[str, object], output_path: str | None) -> None:
    if output_path and output_path != "-":
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return

    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")


def _print_summary(report: Mapping[str, object]) -> None:
    provenance = report.get("provenance", {})
    summary = report.get("summary", {})
    operations = report.get("operations", [])
    if not isinstance(provenance, Mapping) or not isinstance(summary, Mapping) or not isinstance(
        operations, list
    ):
        return

    sys.stderr.write(
        "Compared {baseline} -> {candidate} ({group})\n".format(
            baseline=provenance.get("baseline_run_id", "unknown-baseline"),
            candidate=provenance.get("candidate_run_id", "unknown-candidate"),
            group=provenance.get("comparable_group", "unknown-group"),
        )
    )
    sys.stderr.write(
        "Summary: {improved} improved, {neutral} neutral, {alert} alerts, {fail} fails\n".format(
            improved=summary.get("improved", 0),
            neutral=summary.get("neutral", 0),
            alert=summary.get("alert_regressions", 0),
            fail=summary.get("fail_regressions", 0),
        )
    )

    for operation in operations:
        if not isinstance(operation, Mapping):
            continue
        sys.stderr.write(
            "- {name}: {change:+.2f}% ({delta:+.4f} {unit}) [{status}]\n".format(
                name=operation.get("name", "unknown"),
                change=float(operation.get("percent_change", 0.0)),
                delta=float(operation.get("absolute_delta", 0.0)),
                unit=operation.get("unit", "ops/sec"),
                status=operation.get("status", "unknown"),
            )
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare two experiment runs for regressions.")
    parser.add_argument("--baseline-dir", required=True, help="Path to the baseline experiment run directory")
    parser.add_argument("--candidate-dir", required=True, help="Path to the candidate experiment run directory")
    parser.add_argument("--output", help="Write JSON report to this path instead of stdout")
    parser.add_argument(
        "--alert-threshold",
        type=float,
        default=5.0,
        help="Regression alert threshold in percent (default: 5.0)",
    )
    parser.add_argument(
        "--fail-threshold",
        type=float,
        default=10.0,
        help="Regression fail threshold in percent (default: 10.0)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.alert_threshold < 0 or args.fail_threshold < 0:
        sys.stderr.write("Thresholds must be non-negative\n")
        return EXIT_ERROR
    if args.fail_threshold < args.alert_threshold:
        sys.stderr.write("--fail-threshold must be greater than or equal to --alert-threshold\n")
        return EXIT_ERROR

    try:
        baseline = _load_run(Path(args.baseline_dir).resolve())
        candidate = _load_run(Path(args.candidate_dir).resolve())
        report = _compare_runs(baseline, candidate, args.alert_threshold, args.fail_threshold)
        _write_output(report, args.output)
        _print_summary(report)
        summary = report.get("summary", {})
        if isinstance(summary, Mapping):
            return _coerce_int(summary.get("exit_code"), EXIT_ERROR)
        return EXIT_ERROR
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
