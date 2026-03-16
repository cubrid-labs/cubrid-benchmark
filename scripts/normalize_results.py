from __future__ import annotations

import json
import math
import sys
from collections.abc import Mapping
from pathlib import Path


def _read_input(path_arg: str | None) -> dict[str, object]:
    if path_arg:
        return json.loads(Path(path_arg).read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def _to_percent(stddev: float, mean: float) -> str:
    if mean == 0:
        return "+/- 0.0%"
    value = abs((stddev / mean) * 100.0)
    return "+/- {:.1f}%".format(value)


def _to_value(entry: Mapping[str, object]) -> float:
    stats = entry.get("stats", {})
    if not isinstance(stats, Mapping):
        return 0.0
    ops = stats.get("ops")
    if isinstance(ops, (int, float)) and math.isfinite(ops):
        return float(ops)
    mean = stats.get("mean")
    if isinstance(mean, (int, float)) and mean > 0:
        return 1.0 / float(mean)
    return 0.0


def _as_float(value: object, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


def normalize(pytest_benchmark_json: Mapping[str, object]) -> list[dict[str, object]]:
    benchmarks = pytest_benchmark_json.get("benchmarks", [])
    output: list[dict[str, object]] = []

    if not isinstance(benchmarks, list):
        return output

    for entry in benchmarks:
        if not isinstance(entry, Mapping):
            continue
        stats = entry.get("stats", {})
        if not isinstance(stats, Mapping):
            continue
        mean = _as_float(stats.get("mean", 0.0), 0.0)
        stddev = _as_float(stats.get("stddev", 0.0), 0.0)

        output.append(
            {
                "name": entry.get("name", "unknown"),
                "unit": "ops/sec",
                "value": round(_to_value(entry), 4),
                "range": _to_percent(stddev, mean),
                "extra": "language=python tier=1 framework=pytest-benchmark",
            }
        )

    return output


def main() -> int:
    path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    payload = _read_input(path_arg)
    normalized = normalize(payload)
    json.dump(normalized, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
