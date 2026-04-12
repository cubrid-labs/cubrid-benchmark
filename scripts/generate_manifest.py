from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import cast


def _parse_args() -> Path:
    parser = argparse.ArgumentParser(
        description="Generate a version-matrix manifest from packaged benchmark result files."
    )
    _ = parser.add_argument(
        "--results-dir",
        required=True,
        type=Path,
        help="Directory containing packaged matrix benchmark JSON files.",
    )
    args = parser.parse_args()
    results_dir = getattr(args, "results_dir", None)
    if not isinstance(results_dir, Path):
        raise SystemExit("--results-dir must be a path")
    return results_dir.resolve()


def _iter_result_files(results_dir: Path) -> Iterable[Path]:
    for path in sorted(results_dir.glob("*.json")):
        if path.name == "manifest.json":
            continue
        yield path


def _read_result_file(result_file: Path) -> Mapping[str, object]:
    raw_payload = cast(object, json.loads(result_file.read_text(encoding="utf-8")))
    if not isinstance(raw_payload, Mapping):
        raise ValueError(f"Expected object payload in {result_file}")
    return cast(Mapping[str, object], raw_payload)


def _require_string(payload: Mapping[str, object], key: str, result_file: Path) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"Missing '{key}' in {result_file}")
    return value


def build_manifest(results_dir: Path) -> dict[str, object]:
    entries: list[dict[str, str]] = []
    relative_base = results_dir.parent

    for result_file in _iter_result_files(results_dir):
        payload = _read_result_file(result_file)
        entries.append(
            {
                "scenario": _require_string(payload, "scenario", result_file),
                "python": _require_string(payload, "python", result_file),
                "driver": _require_string(payload, "driver", result_file),
                "driver_version": _require_string(payload, "driver_version", result_file),
                "result_file": result_file.relative_to(relative_base).as_posix(),
            }
        )

    entries.sort(
        key=lambda entry: (
            entry["scenario"],
            entry["python"],
            entry["driver"],
            entry["driver_version"],
            entry["result_file"],
        )
    )
    if not entries:
        raise ValueError(f"No result JSON files found in {results_dir}")

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        ),
        "matrix": entries,
    }


def main() -> int:
    results_dir = _parse_args()

    if not results_dir.is_dir():
        raise SystemExit(f"Results directory does not exist: {results_dir}")

    manifest = build_manifest(results_dir)
    manifest_path = results_dir / "manifest.json"
    _ = manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(manifest_path)
    return 0


if __name__ == "__main__":
    _ = sys.exit(main())
