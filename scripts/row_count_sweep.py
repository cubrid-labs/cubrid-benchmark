#!/usr/bin/env python3
"""Row-count sweep: measure pycubrid SELECT fetch latency at varying result set sizes."""

import argparse
import json
import math
import statistics
import time
from pathlib import Path

from pycubrid.connection import Connection


ROW_COUNTS = [100, 500, 1000, 5000, 10000]


def percentile(data: list[float], p: float) -> float:
    sorted_data = sorted(data)
    n = len(sorted_data)
    k = (n - 1) * p / 100.0
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return sorted_data[int(k)]
    return sorted_data[f] * (c - k) + sorted_data[c] * (k - f)


def compute_stats(times_ns: list[int]) -> dict:
    times_ms = [t / 1_000_000 for t in times_ns]
    mean = statistics.mean(times_ms)
    stdev = statistics.stdev(times_ms) if len(times_ms) > 1 else 0.0
    cv = (stdev / mean * 100) if mean > 0 else 0.0
    return {
        "mean_ms": round(mean, 4),
        "stdev_ms": round(stdev, 4),
        "p50_ms": round(percentile(times_ms, 50), 4),
        "p95_ms": round(percentile(times_ms, 95), 4),
        "p99_ms": round(percentile(times_ms, 99), 4),
        "cv_pct": round(cv, 2),
        "min_ms": round(min(times_ms), 4),
        "max_ms": round(max(times_ms), 4),
        "count": len(times_ms),
    }


def setup_table(conn: Connection, row_count: int) -> None:
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS bench_sweep")
    cur.execute("""
        CREATE TABLE bench_sweep (
            id INT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(200) NOT NULL,
            age INT NOT NULL
        )
    """)
    conn.commit()

    for i in range(1, row_count + 1):
        cur.execute(
            "INSERT INTO bench_sweep (id, name, email, age) VALUES (?, ?, ?, ?)",
            (i, f"user_{i}", f"user_{i}@example.com", 20 + (i % 50)),
        )
    conn.commit()
    cur.close()


def teardown_table(conn: Connection) -> None:
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS bench_sweep")
    conn.commit()
    cur.close()


def bench_select_fetch(conn: Connection, row_count: int, iterations: int, warmup: int) -> dict:
    execute_times: list[int] = []
    fetch_times: list[int] = []

    query = f"SELECT id, name, email, age FROM bench_sweep WHERE id <= {row_count}"

    for i in range(warmup + iterations):
        cur = conn.cursor()

        t0 = time.perf_counter_ns()
        cur.execute(query)
        t1 = time.perf_counter_ns()

        rows = cur.fetchall()
        t2 = time.perf_counter_ns()

        cur.close()

        assert len(rows) == row_count, f"Expected {row_count} rows, got {len(rows)}"

        if i >= warmup:
            execute_times.append(t1 - t0)
            fetch_times.append(t2 - t1)

    return {
        "execute": compute_stats(execute_times),
        "fetch": compute_stats(fetch_times),
        "total": compute_stats(
            [e + f for e, f in zip(execute_times, fetch_times)]
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Row-count sweep benchmark")
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=33000)
    parser.add_argument("--db", default="benchdb")
    parser.add_argument("--user", default="dba")
    parser.add_argument("--password", default="")
    parser.add_argument("--iterations", type=int, default=200)
    parser.add_argument("--warmup", type=int, default=50)
    parser.add_argument("--max-rows", type=int, default=10_000)
    parser.add_argument("--output", type=str, default="sweep.json")
    args = parser.parse_args()

    conn = Connection(host=args.host, port=args.port, database=args.db,
                      user=args.user, password=args.password)
    conn.autocommit = False

    print(f"Setting up table with {args.max_rows} rows...")
    setup_table(conn, args.max_rows)

    results: dict = {
        "metadata": {
            "tool": "row_count_sweep.py",
            "pycubrid_version": "0.5.0+16a8634",
            "python_version": "CPython 3.12.8",
            "iterations": args.iterations,
            "warmup": args.warmup,
            "timer": "time.perf_counter_ns()",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        },
        "sweep": {},
    }

    row_counts = [rc for rc in ROW_COUNTS if rc <= args.max_rows]

    for rc in row_counts:
        print(f"  Benchmarking {rc:>5d} rows ({args.iterations} iterations)...")
        sweep_result = bench_select_fetch(conn, rc, args.iterations, args.warmup)
        results["sweep"][str(rc)] = sweep_result

    teardown_table(conn)
    conn.close()

    output_path = Path(args.output)
    output_path.write_text(json.dumps(results, indent=2) + "\n")
    print(f"\nResults written to {output_path}")

    print("\n--- Row-Count Sweep Summary ---")
    print(f"{'Rows':>6s}  {'Execute (ms)':>13s}  {'Fetch (ms)':>11s}  {'Total (ms)':>11s}  {'ms/row':>8s}")
    print("-" * 60)
    for rc_str, data in results["sweep"].items():
        rc = int(rc_str)
        exe = data["execute"]["mean_ms"]
        fetch = data["fetch"]["mean_ms"]
        total = data["total"]["mean_ms"]
        per_row = fetch / rc * 1000 if rc > 0 else 0
        print(f"{rc:>6d}  {exe:>13.3f}  {fetch:>11.3f}  {total:>11.3f}  {per_row:>7.3f}µs")


if __name__ == "__main__":
    main()
