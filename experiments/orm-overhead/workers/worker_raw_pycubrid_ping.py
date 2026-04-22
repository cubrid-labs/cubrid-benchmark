#!/usr/bin/env python3
"""benchflow external worker for raw pycubrid ping hot-path benchmarking."""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

import pycubrid

TABLE_NAME = "bench_orm_overhead_items"
PING_MODE_NATIVE = "native"
PING_MODE_SELECT1 = "select1"
OPERATION_NAMES = ("ping_only", "ping_select_by_pk")
SQL_DROP_TABLE = "DROP TABLE IF EXISTS bench_orm_overhead_items"
SQL_CREATE_TABLE = (
    "CREATE TABLE bench_orm_overhead_items (id INT PRIMARY KEY, name VARCHAR(128), amount INT)"
)
SQL_DELETE_ALL = "DELETE FROM bench_orm_overhead_items"
SQL_INSERT_ONE = "INSERT INTO bench_orm_overhead_items (id, name, amount) VALUES (?, ?, ?)"
SQL_SELECT_BY_FIXED_PK = "SELECT name FROM bench_orm_overhead_items WHERE id = ?"


@dataclass
class InputStep:
    name: str
    query: str
    params: dict[str, Any] | None = None


@dataclass
class WorkerInput:
    dsn: str
    steps: list[InputStep]
    concurrency: int
    duration_s: int
    warmup_s: int
    seed: int | None
    setup_queries: list[str]
    teardown_queries: list[str]
    worker_config: dict[str, Any]


def _parse_input(path: str) -> WorkerInput:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    steps = [InputStep(**s) for s in raw.get("steps", [])]
    return WorkerInput(
        dsn=raw["dsn"],
        steps=steps,
        concurrency=max(1, int(raw.get("concurrency", 1))),
        duration_s=max(1, int(raw.get("duration_s", 10))),
        warmup_s=max(0, int(raw.get("warmup_s", 0))),
        seed=raw.get("seed"),
        setup_queries=list(raw.get("setup_queries", [])),
        teardown_queries=list(raw.get("teardown_queries", [])),
        worker_config=dict(raw.get("worker_config", {})),
    )


def _percentile(sorted_vals: list[int], p: float) -> int:
    if not sorted_vals:
        return 0
    idx = max(0, min(math.ceil((p / 100.0) * len(sorted_vals)) - 1, len(sorted_vals) - 1))
    return sorted_vals[idx]


class StepCollector:
    def __init__(self, name: str) -> None:
        self.name = name
        self.latencies_ns: list[int] = []
        self.errors = 0
        self.time_buckets: dict[int, list[int]] = {}
        self.time_errors: dict[int, int] = {}

    def record(self, latency_ns: int, second: int) -> None:
        self.latencies_ns.append(latency_ns)
        self.time_buckets.setdefault(second, []).append(latency_ns)

    def record_error(self, second: int) -> None:
        self.errors += 1
        self.time_errors[second] = self.time_errors.get(second, 0) + 1

    def to_output(self, duration_s: float, sample_limit: int, rng: random.Random) -> dict[str, Any]:
        sorted_vals = sorted(self.latencies_ns)
        if not sorted_vals:
            return {
                "name": self.name,
                "ops": 0,
                "errors": self.errors,
                "latency_summary": {
                    "min_ns": 0,
                    "max_ns": 0,
                    "mean_ns": 0,
                    "stdev_ns": 0,
                    "p50_ns": 0,
                    "p95_ns": 0,
                    "p99_ns": 0,
                    "p999_ns": 0,
                    "p9999_ns": 0,
                },
                "throughput_ops_s": 0.0,
                "samples_ns": [],
                "time_series": [],
            }

        mean_ns = int(sum(sorted_vals) / len(sorted_vals))
        stdev_ns = int(statistics.pstdev(sorted_vals)) if len(sorted_vals) > 1 else 0
        samples = sorted_vals
        if len(samples) > sample_limit:
            samples = [sorted_vals[rng.randrange(len(sorted_vals))] for _ in range(sample_limit)]

        series: list[dict[str, Any]] = []
        for second in range(max(self.time_buckets.keys(), default=-1) + 1):
            bucket = self.time_buckets.get(second, [])
            if not bucket:
                continue
            bucket_sorted = sorted(bucket)
            series.append(
                {
                    "second": second,
                    "ops": len(bucket),
                    "errors": self.time_errors.get(second, 0),
                    "p50_ns": _percentile(bucket_sorted, 50),
                    "p95_ns": _percentile(bucket_sorted, 95),
                    "p99_ns": _percentile(bucket_sorted, 99),
                }
            )

        return {
            "name": self.name,
            "ops": len(sorted_vals),
            "errors": self.errors,
            "latency_summary": {
                "min_ns": sorted_vals[0],
                "max_ns": sorted_vals[-1],
                "mean_ns": mean_ns,
                "stdev_ns": stdev_ns,
                "p50_ns": _percentile(sorted_vals, 50),
                "p95_ns": _percentile(sorted_vals, 95),
                "p99_ns": _percentile(sorted_vals, 99),
                "p999_ns": _percentile(sorted_vals, 99.9),
                "p9999_ns": _percentile(sorted_vals, 99.99),
            },
            "throughput_ops_s": len(sorted_vals) / max(duration_s, 1e-9),
            "samples_ns": samples,
            "time_series": series,
        }


def _connect_from_dsn(dsn: str):
    parsed = urlparse(dsn)
    scheme = parsed.scheme.replace("+pycubrid", "")
    if scheme != "cubrid":
        raise ValueError("unsupported DSN for raw pycubrid worker: {0}".format(dsn))

    return pycubrid.connect(
        host=parsed.hostname or "localhost",
        port=parsed.port or 33000,
        database=(parsed.path or "/testdb").lstrip("/"),
        user=parsed.username or "dba",
        password=parsed.password or "",
    )


def _create_and_seed(cur: Any, conn: Any, seed_rows: int) -> None:
    cur.execute(SQL_DROP_TABLE)
    cur.execute(SQL_CREATE_TABLE)
    cur.execute(SQL_DELETE_ALL)
    for row_id in range(1, seed_rows + 1):
        cur.execute(SQL_INSERT_ONE, (row_id, "seed_{0}".format(row_id), row_id))
    conn.commit()


def _run_step(
    collector: StepCollector,
    fn: Callable[[], None],
    warmup_s: int,
    duration_s: int,
) -> float:
    if warmup_s > 0:
        warmup_deadline = time.perf_counter() + warmup_s
        while time.perf_counter() < warmup_deadline:
            try:
                fn()
            except Exception:
                pass

    measure_start = time.perf_counter()
    deadline = measure_start + duration_s
    while time.perf_counter() < deadline:
        t0 = time.perf_counter_ns()
        sec = int(time.perf_counter() - measure_start)
        try:
            fn()
            collector.record(time.perf_counter_ns() - t0, sec)
        except Exception:
            collector.record_error(sec)
    return time.perf_counter() - measure_start


def run_worker(input_obj: WorkerInput) -> dict[str, Any]:
    _ = random.Random(input_obj.seed if input_obj.seed is not None else time.time_ns())
    seed_rows = max(1, int(input_obj.worker_config.get("seed_rows", 1000)))
    sample_limit = max(100, int(input_obj.worker_config.get("sample_limit", 10000)))
    ping_mode = str(input_obj.worker_config.get("ping_mode", PING_MODE_NATIVE))
    if ping_mode not in {PING_MODE_NATIVE, PING_MODE_SELECT1}:
        raise ValueError("unsupported ping_mode: {0}".format(ping_mode))

    conn = _connect_from_dsn(input_obj.dsn)
    cur = conn.cursor()

    ping_calls = 0
    query_calls = 0
    server_info: dict[str, Any] = {
        "ping_mode": ping_mode,
        "ping_calls": 0,
        "query_calls": 0,
        "pool_pre_ping": False,
    }

    try:
        cur.execute("SELECT version()")
        row = cur.fetchone()
        if row:
            server_info["server_version"] = row[0]
    except Exception:
        pass

    for query in input_obj.setup_queries:
        cur.execute(query)
    conn.commit()

    _create_and_seed(cur, conn, seed_rows)
    collectors = {name: StepCollector(name) for name in OPERATION_NAMES}
    step_durations: dict[str, float] = {}

    def run_ping() -> None:
        nonlocal ping_calls
        ping_calls += 1
        if ping_mode == PING_MODE_NATIVE:
            conn.ping(reconnect=False)
            return
        ping_cur = conn.cursor()
        try:
            ping_cur.execute("SELECT 1")
            ping_cur.fetchone()
        finally:
            ping_cur.close()

    def op_ping_only() -> None:
        run_ping()

    def op_ping_select_by_pk() -> None:
        nonlocal query_calls
        run_ping()
        query_calls += 1
        cur.execute(SQL_SELECT_BY_FIXED_PK, (1,))
        cur.fetchone()

    operations: list[tuple[str, Callable[[], None]]] = [
        ("ping_only", op_ping_only),
        ("ping_select_by_pk", op_ping_select_by_pk),
    ]

    for name, fn in operations:
        step_durations[name] = _run_step(
            collectors[name], fn, input_obj.warmup_s, input_obj.duration_s
        )

    for query in input_obj.teardown_queries:
        try:
            cur.execute(query)
        except Exception:
            pass

    try:
        cur.execute(SQL_DROP_TABLE)
        conn.commit()
    except Exception:
        pass

    cur.close()
    conn.close()

    server_info["ping_calls"] = ping_calls
    server_info["query_calls"] = query_calls

    output_steps = [
        collectors[name].to_output(
            step_durations[name],
            sample_limit=sample_limit,
            rng=random.Random(42),
        )
        for name in OPERATION_NAMES
    ]

    return {
        "status": "ok",
        "steps": output_steps,
        "duration_s": sum(step_durations.values()),
        "error_message": None,
        "server_info": server_info,
    }


def _fatal(msg: str) -> None:
    out = {
        "status": "error",
        "steps": [],
        "duration_s": 0,
        "error_message": msg,
        "server_info": {},
    }
    sys.stdout.write(json.dumps(out) + "\n")
    raise SystemExit(1)


def main() -> None:
    if len(sys.argv) < 2:
        _fatal("usage: worker_raw_pycubrid_ping.py <config.json>")
    try:
        input_obj = _parse_input(sys.argv[1])
        output = run_worker(input_obj)
        sys.stdout.write(json.dumps(output, indent=2) + "\n")
    except Exception as exc:
        _fatal(str(exc))


if __name__ == "__main__":
    main()
