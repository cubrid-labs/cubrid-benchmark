# pyright: basic, reportAny=false, reportArgumentType=false, reportImplicitStringConcatenation=false, reportUnknownArgumentType=false, reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnusedCallResult=false
from __future__ import annotations

import argparse
import json
import math
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from html import escape
from pathlib import Path

ALERT_THRESHOLD = 5.0
FAIL_THRESHOLD = 10.0


@dataclass(frozen=True)
class OperationComparison:
    name: str
    current: Mapping[str, object]
    baseline: Mapping[str, object] | None
    delta: float | None
    percent_change: float | None
    status: str


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate HTML and Markdown reports from benchforge v2 results.",
    )
    parser.add_argument("--input", required=True, help="Path to the benchforge v2 JSON artifact")
    parser.add_argument("--output-dir", required=True, help="Directory for generated report files")
    parser.add_argument(
        "--format",
        choices=("html", "markdown", "both"),
        default="both",
        help="Report format to generate (default: both)",
    )
    parser.add_argument(
        "--baseline",
        help="Optional second benchforge v2 JSON artifact used for comparison columns",
    )
    return parser.parse_args()


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _as_mapping(value: object, label: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _as_results(value: object, label: str) -> list[Mapping[str, object]]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label}.results must be a non-empty array")
    results: list[Mapping[str, object]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise ValueError(f"{label}.results[{index}] must be an object")
        name = item.get("name")
        unit = item.get("unit")
        range_value = item.get("range")
        metric_value = item.get("value")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{label}.results[{index}].name must be a non-empty string")
        if not isinstance(unit, str) or not unit:
            raise ValueError(f"{label}.results[{index}].unit must be a non-empty string")
        if not isinstance(range_value, str) or not range_value:
            raise ValueError(f"{label}.results[{index}].range must be a non-empty string")
        if not isinstance(metric_value, (int, float)) or isinstance(metric_value, bool):
            raise ValueError(f"{label}.results[{index}].value must be numeric")
        if not math.isfinite(float(metric_value)):
            raise ValueError(f"{label}.results[{index}].value must be finite")
        results.append(item)
    return results


def _load_benchforge_v2(path: Path, label: str) -> dict[str, object]:
    payload = _as_mapping(_load_json(path), label)
    if payload.get("schema_version") != "2.0":
        raise ValueError(f"{label}.schema_version must equal '2.0'")

    metadata = _as_mapping(payload.get("metadata"), f"{label}.metadata")
    provenance = _as_mapping(payload.get("provenance"), f"{label}.provenance")
    comparable_group = payload.get("comparable_group")
    if not isinstance(comparable_group, str) or not comparable_group:
        raise ValueError(f"{label}.comparable_group must be a non-empty string")

    return {
        "schema_version": payload["schema_version"],
        "metadata": metadata,
        "provenance": provenance,
        "results": _as_results(payload.get("results"), label),
        "comparable_group": comparable_group,
        "source_path": str(path),
    }


def _coerce_float(value: object) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        number = float(value)
        if math.isfinite(number):
            return number
    return None


def _format_number(value: float | None) -> str:
    if value is None:
        return "n/a"
    text = f"{value:,.4f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:+.2f}%"


def _status_for_change(percent_change: float | None) -> str:
    if percent_change is None:
        return "missing"
    if percent_change <= -FAIL_THRESHOLD:
        return "fail"
    if percent_change <= -ALERT_THRESHOLD:
        return "alert"
    if percent_change >= ALERT_THRESHOLD:
        return "improved"
    return "neutral"


def _status_icon(status: str) -> str:
    return {
        "improved": "✅",
        "neutral": "⚪",
        "alert": "⚠️",
        "fail": "❌",
        "missing": "➖",
    }.get(status, "➖")


def _status_label(status: str) -> str:
    return {
        "improved": "Improved",
        "neutral": "Neutral",
        "alert": "Alert regression",
        "fail": "Fail regression",
        "missing": "Unavailable",
    }.get(status, "Unavailable")


def _results_by_name(results: Sequence[Mapping[str, object]]) -> dict[str, Mapping[str, object]]:
    mapping: dict[str, Mapping[str, object]] = {}
    for result in results:
        name = result.get("name")
        if isinstance(name, str):
            mapping[name] = result
    return mapping


def _build_comparisons(
    current_results: Sequence[Mapping[str, object]],
    baseline_results: Sequence[Mapping[str, object]] | None,
) -> list[OperationComparison]:
    current_by_name = _results_by_name(current_results)
    baseline_by_name = _results_by_name(baseline_results or [])
    names = sorted(set(current_by_name.keys()) | set(baseline_by_name.keys()))
    comparisons: list[OperationComparison] = []

    for name in names:
        current = current_by_name.get(name)
        baseline = baseline_by_name.get(name)
        if current is not None:
            current_value = _coerce_float(current.get("value"))
        else:
            current_value = None
        baseline_value = _coerce_float(baseline.get("value")) if baseline is not None else None
        delta = None
        percent_change = None
        if current_value is not None and baseline_value is not None:
            delta = current_value - baseline_value
            if baseline_value != 0:
                percent_change = (delta / baseline_value) * 100.0
        status = _status_for_change(percent_change) if current is not None else "missing"
        comparisons.append(
            OperationComparison(
                name=name,
                current=current or {},
                baseline=baseline,
                delta=delta,
                percent_change=percent_change,
                status=status,
            )
        )

    return comparisons


def _metadata_field(payload: Mapping[str, object], key: str, default: str = "unknown") -> str:
    metadata = payload.get("metadata")
    if not isinstance(metadata, Mapping):
        return default
    value = metadata.get(key)
    return value if isinstance(value, str) and value else default


def _nested_mapping(payload: Mapping[str, object], *keys: str) -> Mapping[str, object]:
    current: object = payload
    for key in keys:
        if not isinstance(current, Mapping):
            return {}
        current = current.get(key)
    return current if isinstance(current, Mapping) else {}


def _comparison_summary(comparisons: Sequence[OperationComparison]) -> dict[str, int]:
    counts = {"improved": 0, "neutral": 0, "alert": 0, "fail": 0, "missing": 0}
    for item in comparisons:
        counts[item.status] = counts.get(item.status, 0) + 1
    return counts


def _source_lines(
    current: Mapping[str, object], baseline: Mapping[str, object] | None
) -> list[str]:
    lines = [f"Current artifact: {current['source_path']}"]
    if baseline is not None:
        lines.append(f"Baseline artifact: {baseline['source_path']}")
    return lines


def _extra_rows(extra: Mapping[str, object]) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for key in sorted(extra):
        value = extra[key]
        if isinstance(value, float):
            rendered = _format_number(value)
        else:
            if isinstance(value, (dict, list)):
                rendered = json.dumps(value, ensure_ascii=False)
            else:
                rendered = str(value)
        rows.append((key, rendered))
    return rows


def _render_markdown(
    current: Mapping[str, object],
    baseline: Mapping[str, object] | None,
    comparisons: Sequence[OperationComparison],
) -> str:
    suite_name = _metadata_field(current, "benchmark_suite")
    timestamp = _metadata_field(current, "timestamp")
    lines = [f"# Benchforge Report: {suite_name}", ""]
    lines.append(f"Generated from `{current['source_path']}`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Suite: `{suite_name}`")
    lines.append(f"- Timestamp: `{timestamp}`")
    lines.append(f"- Comparable group: `{current['comparable_group']}`")
    lines.append(f"- Git branch: `{_metadata_field(current, 'git_branch')}`")
    lines.append(f"- Git SHA: `{_metadata_field(current, 'git_sha')}`")
    lines.append(f"- Runner: `{_metadata_field(current, 'runner_id')}`")
    lines.append("")

    hardware = _nested_mapping(current, "provenance", "hardware")
    software = _nested_mapping(current, "provenance", "software")
    drivers = _nested_mapping(current, "provenance", "drivers")
    lines.append("## Provenance")
    lines.append("")
    lines.append(
        "- Host: `{hostname}` | CPU: `{cpu}` | Cores: `{cores}` | Memory: `{memory_gb}` GB".format(
            hostname=hardware.get("hostname", "unknown"),
            cpu=hardware.get("cpu", "unknown"),
            cores=hardware.get("cores", "unknown"),
            memory_gb=hardware.get("memory_gb", "unknown"),
        )
    )
    lines.append(
        (
            "- OS: `{os}` | Kernel: `{kernel}` | Python: `{python}` | Docker: `{docker}` | "
            "CUBRID: `{cubrid}`"
        ).format(
            os=hardware.get("os", "unknown"),
            kernel=hardware.get("kernel", "unknown"),
            python=software.get("python", "unknown"),
            docker=software.get("docker", "unknown"),
            cubrid=software.get("cubrid_server", "unknown"),
        )
    )
    if drivers:
        driver_summary = ", ".join(
            f"`{key}={value}`" for key, value in sorted(drivers.items(), key=lambda item: item[0])
        )
        lines.append(
            "- Drivers: " + driver_summary
        )
    lines.append("")

    if baseline is not None:
        counts = _comparison_summary(comparisons)
        lines.append("## Comparison")
        lines.append("")
        lines.append(f"- Baseline suite: `{_metadata_field(baseline, 'benchmark_suite')}`")
        lines.append(f"- Baseline timestamp: `{_metadata_field(baseline, 'timestamp')}`")
        lines.append(f"- Baseline artifact: `{baseline['source_path']}`")
        lines.append(
            "- Status counts: "
            f"{counts['improved']} improved, {counts['neutral']} neutral, "
            f"{counts['alert']} alerts, {counts['fail']} fails, {counts['missing']} unavailable"
        )
        lines.append("")

    header = [
        "Operation",
        "Tier",
        "Language",
        "Driver",
        "Database",
        "Value",
        "Unit",
        "Range",
    ]
    if baseline is not None:
        header.extend(["Baseline", "Delta", "% Change", "Status"])

    divider = ["---"] * len(header)
    lines.append("## Results")
    lines.append("")
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(divider) + " |")
    for item in comparisons:
        current_result = item.current
        row = [
            str(current_result.get("name", "unknown")),
            str(current_result.get("tier", "unknown")),
            str(current_result.get("language", "unknown")),
            str(current_result.get("driver", "unknown")),
            str(current_result.get("database", "unknown")),
            _format_number(_coerce_float(current_result.get("value"))),
            str(current_result.get("unit", "unknown")),
            str(current_result.get("range", "unknown")),
        ]
        if baseline is not None:
            baseline_value = (
                _format_number(_coerce_float(item.baseline.get("value")))
                if item.baseline
                else "n/a"
            )
            row.extend(
                [
                    baseline_value,
                    _format_number(item.delta),
                    _format_percent(item.percent_change),
                    f"{_status_icon(item.status)} {_status_label(item.status)}",
                ]
            )
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## Per-operation details")
    lines.append("")
    for item in comparisons:
        current_result = item.current
        lines.append(f"### {item.name}")
        lines.append("")
        value_text = _format_number(_coerce_float(current_result.get("value")))
        unit_text = str(current_result.get("unit", ""))
        lines.append(f"- Value: `{value_text} {unit_text}`")
        lines.append(f"- Range: `{current_result.get('range', 'unknown')}`")
        if baseline is not None:
            lines.append(
                f"- Comparison: `{_format_number(item.delta)}` delta, "
                f"`{_format_percent(item.percent_change)}` change, "
                f"{_status_icon(item.status)} {_status_label(item.status)}"
            )
        extra = current_result.get("extra")
        if isinstance(extra, Mapping) and extra:
            lines.append("- Extra metrics:")
            for key, value in _extra_rows(extra):
                lines.append(f"  - `{key}`: `{value}`")
        lines.append("")

    lines.append("## Source artifacts")
    lines.append("")
    for line in _source_lines(current, baseline):
        lines.append(f"- `{line}`")
    lines.append("")
    return "\n".join(lines)


def _render_html(
    current: Mapping[str, object],
    baseline: Mapping[str, object] | None,
    comparisons: Sequence[OperationComparison],
) -> str:
    suite_name = escape(_metadata_field(current, "benchmark_suite"))
    timestamp = escape(_metadata_field(current, "timestamp"))
    hardware = _nested_mapping(current, "provenance", "hardware")
    software = _nested_mapping(current, "provenance", "software")
    drivers = _nested_mapping(current, "provenance", "drivers")
    counts = _comparison_summary(comparisons) if baseline is not None else None

    summary_items = [
        ("Suite", suite_name),
        ("Timestamp", timestamp),
        ("Comparable group", escape(str(current.get("comparable_group", "unknown")))),
        ("Git branch", escape(_metadata_field(current, "git_branch"))),
        ("Git SHA", escape(_metadata_field(current, "git_sha"))),
        ("Runner", escape(_metadata_field(current, "runner_id"))),
    ]

    provenance_items = [
        (
            "Hardware",
            escape(
                "{hostname} | {cpu} | {cores} cores | {memory_gb} GB".format(
                    hostname=hardware.get("hostname", "unknown"),
                    cpu=hardware.get("cpu", "unknown"),
                    cores=hardware.get("cores", "unknown"),
                    memory_gb=hardware.get("memory_gb", "unknown"),
                )
            ),
        ),
        (
            "Software",
            escape(
                "{os} {kernel} | Python {python} | Docker {docker} | CUBRID {cubrid}".format(
                    os=hardware.get("os", "unknown"),
                    kernel=hardware.get("kernel", "unknown"),
                    python=software.get("python", "unknown"),
                    docker=software.get("docker", "unknown"),
                    cubrid=software.get("cubrid_server", "unknown"),
                )
            ),
        ),
    ]
    if drivers:
        driver_values = ", ".join(
            f"{key}={value}" for key, value in sorted(drivers.items(), key=lambda item: item[0])
        )
        provenance_items.append(
            (
                "Drivers",
                escape(driver_values),
            )
        )

    rows: list[str] = []
    for item in comparisons:
        current_result = item.current
        columns = [
            escape(str(current_result.get("name", "unknown"))),
            escape(str(current_result.get("tier", "unknown"))),
            escape(str(current_result.get("language", "unknown"))),
            escape(str(current_result.get("driver", "unknown"))),
            escape(str(current_result.get("database", "unknown"))),
            escape(_format_number(_coerce_float(current_result.get("value")))),
            escape(str(current_result.get("unit", "unknown"))),
            escape(str(current_result.get("range", "unknown"))),
        ]
        if baseline is not None:
            baseline_value = (
                _format_number(_coerce_float(item.baseline.get("value")))
                if item.baseline
                else "n/a"
            )
            columns.extend(
                [
                    escape(baseline_value),
                    escape(_format_number(item.delta)),
                    escape(_format_percent(item.percent_change)),
                    escape(f"{_status_icon(item.status)} {_status_label(item.status)}"),
                ]
            )
        row_class = f' class="status-{escape(item.status)}"' if baseline is not None else ""
        row_html = "".join(f"<td>{value}</td>" for value in columns)
        rows.append("<tr{row_class}>".format(row_class=row_class) + row_html + "</tr>")

    details: list[str] = []
    for item in comparisons:
        current_result = item.current
        extra = current_result.get("extra")
        detail_rows = []
        if isinstance(extra, Mapping):
            for key, value in _extra_rows(extra):
                detail_rows.append(
                    f"<tr><th>{escape(key)}</th><td>{escape(value)}</td></tr>"
                )
        comparison_line = ""
        if baseline is not None:
            comparison_line = (
                (
                    "<p><strong>Comparison:</strong> {delta} delta, {change} change, "
                    "{status}</p>"
                ).format(
                    delta=escape(_format_number(item.delta)),
                    change=escape(_format_percent(item.percent_change)),
                    status=escape(f"{_status_icon(item.status)} {_status_label(item.status)}"),
                )
            )
        value_html = escape(_format_number(_coerce_float(current_result.get("value"))))
        unit_html = escape(str(current_result.get("unit", "")))
        range_html = escape(str(current_result.get("range", "unknown")))
        details.append(
            "".join(
                [
                    f"<section class=\"detail-card\"><h3>{escape(item.name)}</h3>",
                    f"<p><strong>Value:</strong> {value_html} {unit_html}</p>",
                    f"<p><strong>Range:</strong> {range_html}</p>",
                    comparison_line,
                    "<table class=\"detail-table\"><tbody>",
                    "".join(detail_rows) or "<tr><td colspan=\"2\">No extra metrics</td></tr>",
                    "</tbody></table></section>",
                ]
            )
        )

    comparison_section = ""
    if baseline is not None and counts is not None:
        baseline_suite = escape(_metadata_field(baseline, "benchmark_suite"))
        baseline_timestamp = escape(_metadata_field(baseline, "timestamp"))
        baseline_path = escape(str(baseline["source_path"]))
        comparison_section = "".join(
            [
                "<section><h2>Comparison</h2><ul>",
                f"<li><strong>Baseline suite:</strong> {baseline_suite}</li>",
                f"<li><strong>Baseline timestamp:</strong> {baseline_timestamp}</li>",
                f"<li><strong>Baseline artifact:</strong> {baseline_path}</li>",
                "<li><strong>Status counts:</strong> "
                f"{counts['improved']} improved, {counts['neutral']} neutral, "
                f"{counts['alert']} alerts, "
                f"{counts['fail']} fails, {counts['missing']} unavailable</li>",
                "</ul></section>",
            ]
        )

    headers = [
        "Operation",
        "Tier",
        "Language",
        "Driver",
        "Database",
        "Value",
        "Unit",
        "Range",
    ]
    if baseline is not None:
        headers.extend(["Baseline", "Delta", "% Change", "Status"])
    header_html = "".join(f"<th>{escape(header)}</th>" for header in headers)

    summary_html = "".join(
        f"<tr><th>{escape(label)}</th><td>{value}</td></tr>" for label, value in summary_items
    )
    provenance_html = "".join(
        f"<tr><th>{escape(label)}</th><td>{value}</td></tr>" for label, value in provenance_items
    )
    sources_html = "".join(f"<li>{escape(line)}</li>" for line in _source_lines(current, baseline))

    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    :root {{ color-scheme: light dark; }}
    body {{ font-family: Arial, sans-serif; margin: 2rem; line-height: 1.5; }}
    h1, h2, h3 {{ margin-top: 1.5rem; }}
    table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
    th, td {{ border: 1px solid #c9d1d9; padding: 0.6rem; text-align: left; vertical-align: top; }}
    th {{ background: #f6f8fa; }}
    .status-improved td:last-child {{ color: #1a7f37; font-weight: 700; }}
    .status-neutral td:last-child {{ color: #57606a; font-weight: 700; }}
    .status-alert td:last-child {{ color: #9a6700; font-weight: 700; }}
    .status-fail td:last-child {{ color: #cf222e; font-weight: 700; }}
    .status-missing td:last-child {{ color: #57606a; font-weight: 700; }}
    .detail-card {{
      border: 1px solid #d0d7de;
      border-radius: 8px;
      padding: 1rem;
      margin-bottom: 1rem;
    }}
    .detail-table th {{ width: 30%; }}
    code {{ background: rgba(175, 184, 193, 0.2); padding: 0.1rem 0.3rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>Benchforge Report: {title}</h1>
  <p>Generated from <code>{source_path}</code>.</p>
  <section>
    <h2>Summary</h2>
    <table><tbody>{summary_html}</tbody></table>
  </section>
  <section>
    <h2>Provenance</h2>
    <table><tbody>{provenance_html}</tbody></table>
  </section>
  {comparison_section}
  <section>
    <h2>Results</h2>
    <table>
      <thead><tr>{header_html}</tr></thead>
      <tbody>{rows}</tbody>
    </table>
  </section>
  <section>
    <h2>Per-operation details</h2>
    {details}
  </section>
  <section>
    <h2>Source artifacts</h2>
    <ul>{sources_html}</ul>
  </section>
</body>
</html>
""".format(
        title=suite_name,
        source_path=escape(str(current["source_path"])),
        summary_html=summary_html,
        provenance_html=provenance_html,
        comparison_section=comparison_section,
        header_html=header_html,
        rows="".join(rows),
        details="".join(details),
        sources_html=sources_html,
    )


def _write_reports(
    output_dir: Path, report_format: str, html_report: str, markdown_report: str
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    if report_format in {"html", "both"}:
        output_dir.joinpath("report.html").write_text(html_report, encoding="utf-8")
    if report_format in {"markdown", "both"}:
        output_dir.joinpath("report.md").write_text(markdown_report, encoding="utf-8")


def main() -> int:
    args = _parse_args()
    try:
        input_payload = _load_benchforge_v2(Path(args.input), "input")
        baseline_payload = None
        if args.baseline:
            baseline_payload = _load_benchforge_v2(Path(args.baseline), "baseline")
            if baseline_payload["comparable_group"] != input_payload["comparable_group"]:
                raise ValueError(
                    "baseline.comparable_group must match input.comparable_group for comparisons"
                )

        comparisons = _build_comparisons(
            input_payload["results"],
            baseline_payload["results"] if baseline_payload is not None else None,
        )
        markdown_report = _render_markdown(input_payload, baseline_payload, comparisons)
        html_report = _render_html(input_payload, baseline_payload, comparisons)
        _write_reports(Path(args.output_dir), args.format, html_report, markdown_report)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
