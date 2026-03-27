"""Generate run.yaml with auto-captured environment metadata.

Usage:
    python scripts/generate_run_yaml.py \
        --experiment driver-comparison \
        --label before-optimization \
        --role baseline \
        [--compares-to 2026-03-27_before-optimization] \
        [--drivers pycubrid=0.5.0 cubriddb=9.3.0.1] \
        [--notes "initial measurement"]

Creates: experiments/<experiment>/runs/YYYY-MM-DD_<label>/run.yaml
"""

from __future__ import annotations

import argparse
import datetime
import platform
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import cpuinfo

    _HAS_CPUINFO = True
except ImportError:
    _HAS_CPUINFO = False


def _get_cpu_info() -> tuple[str, int]:
    """Return (cpu model string, core count)."""
    if _HAS_CPUINFO:
        info = cpuinfo.get_cpu_info()
        return info.get("brand_raw", platform.processor()), info.get("count", 0)
    return platform.processor(), 0


def _get_memory_gb() -> float:
    """Return total system memory in GB."""
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    return round(kb / 1024 / 1024, 1)
    except (FileNotFoundError, ValueError):
        pass
    return 0.0


def _get_docker_version() -> str:
    """Return Docker version string."""
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            # "Docker version 24.0.5, build ced0996"
            parts = result.stdout.strip().split()
            if len(parts) >= 3:
                return parts[2].rstrip(",")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _get_cubrid_version() -> str:
    """Try to get CUBRID server version from Docker container."""
    try:
        result = subprocess.run(
            ["docker", "exec", "cubrid-bench-cubrid", "cubrid_rel"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    return "unknown"


def _get_python_version() -> str:
    """Return Python implementation and version."""
    impl = platform.python_implementation()
    ver = platform.python_version()
    return f"{impl} {ver}"


def _build_comparable_group(hostname: str, cpu: str, kernel: str) -> str:
    """Generate a comparable_group identifier from environment."""
    # Simplify CPU name: "Intel(R) Core(TM) i5-4200M CPU @ 2.50GHz" -> "i5-4200M"
    cpu_short = cpu
    for token in cpu.split():
        if token.startswith("i") and "-" in token:
            cpu_short = token
            break
        if token.startswith("Ryzen") or token.startswith("Xeon"):
            cpu_short = token
            break

    # Simplify kernel: "5.15.0-173-generic" -> "5.15"
    kernel_short = ".".join(kernel.split(".")[:2]) if kernel else "unknown"

    return f"{hostname}-{cpu_short}-linux{kernel_short}".lower()


def generate_run_yaml(args: argparse.Namespace) -> str:
    """Generate YAML content from auto-captured environment + CLI args."""
    today = datetime.date.today().isoformat()
    run_id = f"{today}_{args.label}"

    cpu_model, cores = _get_cpu_info()
    memory_gb = _get_memory_gb()
    hostname = platform.node()
    kernel = platform.release()
    os_name = platform.system()
    python_ver = _get_python_version()
    docker_ver = _get_docker_version()
    cubrid_ver = _get_cubrid_version()

    comparable_group = _build_comparable_group(hostname, cpu_model, kernel)

    drivers_yaml = ""
    if args.drivers:
        for d in args.drivers:
            name, _, version = d.partition("=")
            drivers_yaml += f"    {name}: \"{version}\"\n"
    else:
        drivers_yaml = "    {}\n"

    compares_to = f"\"{args.compares_to}\"" if args.compares_to else "null"

    yaml_content = f"""run_id: \"{run_id}\"
date: \"{today}T00:00:00Z\"
label: \"{args.label}\"
role: {args.role}
compares_to: {compares_to}
comparable_group: \"{comparable_group}\"

environment:
  host:
    hostname: \"{hostname}\"
    cpu: \"{cpu_model}\"
    cores: {cores}
    memory_gb: {memory_gb}
    os: \"{os_name}\"
    kernel: \"{kernel}\"
  software:
    python: \"{python_ver}\"
    cubrid_server: \"{cubrid_ver}\"
    docker: \"{docker_ver}\"
  drivers:
{drivers_yaml.rstrip()}
  database:
    name: benchdb
    host: localhost
    port: 33000
    autocommit: false

artifacts:
  raw_dir: raw/
  figures_dir: figures/

notes: \"{args.notes or ''}\"
"""
    return yaml_content, run_id


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate run.yaml with auto-captured environment metadata.",
    )
    parser.add_argument(
        "--experiment",
        required=True,
        help="Experiment slug (folder name under experiments/)",
    )
    parser.add_argument(
        "--label",
        required=True,
        help="Run label (e.g. 'before-optimization', 'after-parse-int-fix')",
    )
    parser.add_argument(
        "--role",
        choices=["baseline", "candidate"],
        default="baseline",
        help="Run role: baseline or candidate (default: baseline)",
    )
    parser.add_argument(
        "--compares-to",
        default=None,
        help="Run ID of the baseline to compare against (required if role=candidate)",
    )
    parser.add_argument(
        "--drivers",
        nargs="*",
        help="Driver versions as name=version pairs (e.g. pycubrid=0.5.0 cubriddb=9.3.0.1)",
    )
    parser.add_argument(
        "--notes",
        default="",
        help="Optional notes for this run",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print run.yaml to stdout without writing to disk",
    )

    args = parser.parse_args()

    if args.role == "candidate" and not args.compares_to:
        parser.error("--compares-to is required when --role=candidate")

    yaml_content, run_id = generate_run_yaml(args)

    if args.dry_run:
        print(yaml_content)
        return

    repo_root = Path(__file__).resolve().parent.parent
    run_dir = repo_root / "experiments" / args.experiment / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "raw").mkdir(exist_ok=True)
    (run_dir / "figures").mkdir(exist_ok=True)

    run_yaml_path = run_dir / "run.yaml"
    if run_yaml_path.exists():
        print(f"ERROR: {run_yaml_path} already exists. Runs are immutable.", file=sys.stderr)
        sys.exit(1)

    run_yaml_path.write_text(yaml_content, encoding="utf-8")
    print(f"Created: {run_yaml_path}")
    print(f"Run ID:  {run_id}")
    print(f"Group:   {yaml_content.split('comparable_group:')[1].split(chr(10))[0].strip()}")
    print(f"\nNext steps:")
    print(f"  1. Place raw data in: {run_dir / 'raw/'}")
    print(f"  2. Place charts in:   {run_dir / 'figures/'}")
    print(f"  3. Update experiment README.md run history table")


if __name__ == "__main__":
    main()
