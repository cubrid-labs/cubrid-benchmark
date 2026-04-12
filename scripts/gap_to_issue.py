#!/usr/bin/env python3
# pyright: basic
from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Mapping
from pathlib import Path

EXIT_NO_ISSUES = 0
EXIT_ISSUES_GENERATED = 1
EXIT_ERROR = 2

DEFAULT_TARGET_REPO = "cubrid-labs/pycubrid"


def _load_report(path_arg: str | None) -> dict[str, object]:
    if path_arg and path_arg != "-":
        return json.loads(Path(path_arg).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def _as_float(value: object, default: float | None = None) -> float | None:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _as_int(value: object, default: int | None = None) -> int | None:
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    return default


def _as_str(value: object, default: str = "") -> str:
    if isinstance(value, str):
        return value
    return default


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "issue"


def _format_number(value: object) -> str:
    number = _as_float(value)
    if number is None:
        return "unknown"
    return f"{number:.4f}"


def _format_percent(value: object) -> str:
    number = _as_float(value)
    if number is None:
        return "unknown"
    return f"{number:+.2f}%"


def _infer_tier(provenance: Mapping[str, object], operation: Mapping[str, object]) -> str:
    candidates = [
        _as_str(operation.get("tier"), ""),
        _as_str(provenance.get("tier"), ""),
        _as_str(provenance.get("candidate_results_path"), ""),
        _as_str(provenance.get("baseline_results_path"), ""),
    ]
    for candidate in candidates:
        match = re.search(r"(tier\d+)", candidate, flags=re.IGNORECASE)
        if match:
            return match.group(1).lower()
    return "unknown"


def _extract_replications(report: Mapping[str, object]) -> int | None:
    values: list[int] = []
    for section_name in ("provenance", "thresholds", "summary"):
        section = report.get(section_name)
        if not isinstance(section, Mapping):
            continue
        for key, value in section.items():
            if not isinstance(key, str):
                continue
            normalized = key.lower()
            if "replication" in normalized or normalized in {"iterations", "iteration_count"}:
                parsed = _as_int(value)
                if parsed is not None and parsed > 0:
                    values.append(parsed)
    if not values:
        return None
    return min(values)


def _report_artifact_label(path_arg: str | None) -> str:
    if path_arg and path_arg != "-":
        return f"`{path_arg}`"
    return "stdin (persist the compare report artifact before filing)"


def _reproduction_commands(
    provenance: Mapping[str, object],
    report_path_arg: str | None,
    min_effect_size: float,
    min_replications: int,
    target_repo: str,
) -> list[str]:
    baseline_dir = _as_str(provenance.get("baseline_results_path"), "")
    candidate_dir = _as_str(provenance.get("candidate_results_path"), "")

    baseline_run_dir = (
        str(Path(baseline_dir).parent.parent) if baseline_dir else "<baseline-run-dir>"
    )
    candidate_run_dir = (
        str(Path(candidate_dir).parent.parent) if candidate_dir else "<candidate-run-dir>"
    )
    report_path = (
        report_path_arg
        if report_path_arg and report_path_arg != "-"
        else "results/compare_latest.json"
    )

    return [
        "make up",
        "make seed",
        (
            "make compare "
            f'COMPARE_BASELINE_DIR="{baseline_run_dir}" '
            f'COMPARE_CANDIDATE_DIR="{candidate_run_dir}" '
            f'COMPARE_REPORT="{report_path}"'
        ),
        (
            "make gap-issues "
            f'COMPARE_BASELINE_DIR="{baseline_run_dir}" '
            f'COMPARE_CANDIDATE_DIR="{candidate_run_dir}" '
            f'COMPARE_REPORT="{report_path}" '
            f'MIN_EFFECT_SIZE="{min_effect_size:.1f}" '
            f'MIN_REPLICATIONS="{min_replications}" '
            f'TARGET_REPO="{target_repo}"'
        ),
    ]


def _render_issue(
    report: Mapping[str, object],
    operation: Mapping[str, object],
    report_path_arg: str | None,
    min_effect_size: float,
    min_replications: int,
    target_repo: str,
    dry_run: bool,
) -> tuple[str, str]:
    provenance = report.get("provenance", {})
    if not isinstance(provenance, Mapping):
        raise ValueError("Invalid compare report structure")

    operation_name = _as_str(operation.get("name"), "unknown")
    tier = _infer_tier(provenance, operation)
    unit = _as_str(operation.get("unit"), "ops/sec")
    percent_change = _as_float(operation.get("percent_change"), 0.0)
    absolute_delta = _as_float(operation.get("absolute_delta"), 0.0)
    baseline_value = _format_number(operation.get("baseline"))
    candidate_value = _format_number(operation.get("candidate"))
    replications = _extract_replications(report)
    replications_text = (
        str(replications)
        if replications is not None
        else f"not encoded in compare report (filing bar: >= {min_replications})"
    )

    commands = _reproduction_commands(
        provenance,
        report_path_arg,
        min_effect_size,
        min_replications,
        target_repo,
    )

    title = f"perf: {operation_name} regression detected ({percent_change:+.2f}%)"
    lines = [
        f"# {title}",
        "",
        f"Target repository: `{target_repo}`",
        f"Issue mode: {'dry-run draft only' if dry_run else 'draft content only'}",
        "",
        "## Summary",
        (
            f"A relative improvement opportunity was detected for `{operation_name}` in `{tier}` "
            f"within the same comparable group. Candidate throughput moved {percent_change:+.2f}% "
            f"({absolute_delta:+.4f} {unit}) versus the recorded baseline."
        ),
        "",
        "## Measurement",
        f"- Operation: `{operation_name}`",
        f"- Tier: `{tier}`",
        f"- Status: `{_as_str(operation.get('status'), 'unknown')}`",
        f"- Delta: `{_format_percent(percent_change)}` (`{absolute_delta:+.4f} {unit}`)",
        f"- Baseline: `{baseline_value} {unit}`",
        f"- Candidate: `{candidate_value} {unit}`",
        "",
        "## Provenance",
        f"- Comparable group: `{_as_str(provenance.get('comparable_group'), 'unknown-group')}`",
        (
            f"- Baseline run: `{_as_str(provenance.get('baseline_run_id'), 'unknown-baseline')}` "
            f"({_as_str(provenance.get('baseline_date'), 'unknown-date')})"
        ),
        (
            f"- Candidate run: "
            f"`{_as_str(provenance.get('candidate_run_id'), 'unknown-candidate')}` "
            f"({_as_str(provenance.get('candidate_date'), 'unknown-date')})"
        ),
        (
            f"- Baseline results artifact: "
            f"`{_as_str(provenance.get('baseline_results_path'), 'unknown')}`"
        ),
        (
            f"- Candidate results artifact: "
            f"`{_as_str(provenance.get('candidate_results_path'), 'unknown')}`"
        ),
        f"- Replications noted: `{replications_text}`",
        f"- Compare report artifact: {_report_artifact_label(report_path_arg)}",
        "",
        "## Reproduction",
        "Run the same benchmark flow inside the recorded comparable group:",
        "",
    ]

    lines.extend([f"```bash\n{command}\n```" for command in commands])
    lines.extend(
        [
            "",
            "## Filing guidance",
            (
                f"- Keep this framed as a regression from baseline or a relative improvement "
                f"opportunity within "
                f"`{_as_str(provenance.get('comparable_group'), 'unknown-group')}`."
            ),
            (
                f"- Current generation threshold: fail-only operations with >= "
                f"{min_effect_size:.1f}% regression and a filing bar of "
                f"{min_replications} replications when provenance records it."
            ),
            (
                "- Do not restate this as a requirement to beat MySQL or any absolute "
                "performance target."
            ),
            "",
        ]
    )
    return title, "\n".join(lines)


def _select_operations(
    report: Mapping[str, object], min_effect_size: float, min_replications: int
) -> list[Mapping[str, object]]:
    operations = report.get("operations")
    if not isinstance(operations, list):
        raise ValueError("Invalid compare report structure")

    replications = _extract_replications(report)
    if replications is not None and replications < min_replications:
        return []
    if replications is None and min_replications > 1:
        sys.stderr.write(
            f"WARNING: no replication evidence in report; "
            f"refusing to generate issues (min_replications={min_replications})\n"
        )
        return []

    selected: list[Mapping[str, object]] = []
    for operation in operations:
        if not isinstance(operation, Mapping):
            continue
        if _as_str(operation.get("status"), "") != "fail":
            continue
        percent_change = _as_float(operation.get("percent_change"))
        if percent_change is None:
            continue
        if abs(percent_change) < min_effect_size:
            continue
        selected.append(operation)
    return selected


def _write_issues(output_dir: str | None, issues: list[tuple[str, str]]) -> None:
    if not output_dir:
        for index, (_, body) in enumerate(issues):
            if index:
                sys.stdout.write("\n---\n\n")
            sys.stdout.write(body)
            if not body.endswith("\n"):
                sys.stdout.write("\n")
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    for index, (title, body) in enumerate(issues, start=1):
        filename = f"{index:02d}-{_slugify(title)}.md"
        (output_path / filename).write_text(body.rstrip() + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate draft GitHub issue markdown from compare_runs regression reports."
    )
    parser.add_argument(
        "--report",
        default="-",
        help="Path to compare_runs JSON output, or -/stdin for standard input (default: stdin)",
    )
    parser.add_argument(
        "--min-effect-size",
        type=float,
        default=10.0,
        help="Minimum absolute percent regression required to draft an issue (default: 10.0)",
    )
    parser.add_argument(
        "--min-replications",
        type=int,
        default=3,
        help="Minimum replication count to note as the filing bar in provenance (default: 3)",
    )
    parser.add_argument(
        "--target-repo",
        default=DEFAULT_TARGET_REPO,
        help=f"Target repository for the draft issue (default: {DEFAULT_TARGET_REPO})",
    )
    parser.add_argument(
        "--output-dir",
        help="Write one markdown file per generated issue to this directory instead of stdout",
    )
    parser.add_argument(
        "--dry-run",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Keep generation in draft-only mode (default: true)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.min_effect_size < 0:
        sys.stderr.write("ERROR: --min-effect-size must be non-negative\n")
        return EXIT_ERROR
    if args.min_replications < 1:
        sys.stderr.write("ERROR: --min-replications must be at least 1\n")
        return EXIT_ERROR

    try:
        report = _load_report(args.report)
        selected = _select_operations(report, args.min_effect_size, args.min_replications)
        issues = [
            _render_issue(
                report,
                operation,
                args.report,
                args.min_effect_size,
                args.min_replications,
                args.target_repo,
                args.dry_run,
            )
            for operation in selected
        ]
        _write_issues(args.output_dir, issues)
        if not issues:
            return EXIT_NO_ISSUES
        return EXIT_ISSUES_GENERATED
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        sys.stderr.write(f"ERROR: {exc}\n")
        return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
