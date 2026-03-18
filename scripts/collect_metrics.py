from __future__ import annotations

import argparse
import json
import resource
import subprocess
from pathlib import Path


def _read_json(path: Path) -> object:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run benchmark command and collect child-process RSS metrics.",
    )
    parser.add_argument(
        "--result-json",
        required=True,
        help="Path to benchmark result JSON produced by command.",
    )
    parser.add_argument(
        "--metrics-json",
        default=None,
        help="Path to metrics output JSON. Defaults to <result>.metrics.json.",
    )
    parser.add_argument(
        "command",
        nargs=argparse.REMAINDER,
        help="Command to execute (prefix with '--').",
    )
    return parser.parse_args()


def _normalize_command(command: list[str]) -> list[str]:
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        raise ValueError("command is required after '--'")
    return command


def main() -> int:
    args = _parse_args()
    command = _normalize_command(args.command)

    result_path = Path(args.result_json)
    metrics_path = (
        Path(args.metrics_json) if args.metrics_json else result_path.with_suffix(".metrics.json")
    )

    usage_before = resource.getrusage(resource.RUSAGE_CHILDREN)
    completed = subprocess.run(command, check=False)
    usage_after = resource.getrusage(resource.RUSAGE_CHILDREN)

    rss_before = int(usage_before.ru_maxrss)
    rss_after = int(usage_after.ru_maxrss)
    rss_delta = max(rss_after - rss_before, 0)

    metrics_payload = {
        "command": command,
        "returncode": completed.returncode,
        "memory": {
            "rusage_children_before_kb": rss_before,
            "rusage_children_after_kb": rss_after,
            "peak_rss_delta_kb": rss_delta,
        },
    }

    result_payload = _read_json(result_path)
    artifact_payload = {
        "result_file": str(result_path),
        "result": result_payload,
        "metrics": metrics_payload,
    }
    _write_json(metrics_path, artifact_payload)

    if completed.returncode != 0:
        return completed.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
