#!/usr/bin/env python3
"""benchflow external worker for raw pycubrid.

Reads WorkerInput JSON from a file path argument and writes WorkerOutput JSON to stdout.
"""

from __future__ import annotations

import json
import math
import random
import statistics
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import pycubrid

TABLE_NAME = "bench_orm_overhead_items"
SQL_DROP_TABLE = "DROP TABLE IF EXISTS bench_orm_overhead_items"
SQL_CREATE_TABLE = (
    "CREATE TABLE bench_orm_overhead_items (id INT PRIMARY KEY, name VARCHAR(128), amount INT)"
)
SQL_DELETE_ALL = "DELETE FROM bench_orm_overhead_items"
SQL_INSERT_ONE = "INSERT INTO bench_orm_overhead_items (id, name, amount) VALUES (?, ?, ?)"
SQL_SELECT_BY_PK = "SELECT id, name, amount FROM bench_orm_overhead_items WHERE id = ?"
SQL_SELECT_ALL = "SELECT id, name, amount FROM bench_orm_overhead_items"
SQL_UPDATE_BY_PK = "UPDATE bench_orm_overhead_items SET amount = ? WHERE id = ?"
SQL_DELETE_BY_PK = "DELETE FROM bench_orm_overhead_items WHERE id = ?"
OPERATION_NAMES = (
    "insert_single",
    "insert_batch",
    "select_by_pk",
    "select_full_scan",
    "update_by_pk",
    "delete_by_pk",
)


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
        raise ValueError(f"unsupported DSN for raw pycubrid worker: {dsn}")

    return pycubrid.connect(
        host=parsed.hostname or "localhost",
        port=parsed.port or 33000,
        database=(parsed.path or "/testdb").lstrip("/"),
        user=parsed.username or "dba",
        password=parsed.password or "",
    )


def _create_table(cur: Any, conn: Any) -> None:
    cur.execute(SQL_DROP_TABLE)
    cur.execute(SQL_CREATE_TABLE)
    conn.commit()


def _seed_rows(cur: Any, conn: Any, seed_rows: int) -> None:
    cur.execute(SQL_DELETE_ALL)
    for i in range(1, seed_rows + 1):
        cur.execute(SQL_INSERT_ONE, (i, f"seed_{i}", i))
    conn.commit()


def run_worker(input_obj: WorkerInput) -> dict[str, Any]:
    rng = random.Random(input_obj.seed if input_obj.seed is not None else time.time_ns())
    seed_rows = max(100, int(input_obj.worker_config.get("seed_rows", 1000)))
    batch_size = max(10, int(input_obj.worker_config.get("batch_size", 100)))
    sample_limit = max(100, int(input_obj.worker_config.get("sample_limit", 10000)))

    conn = _connect_from_dsn(input_obj.dsn)
    cur = conn.cursor()

    server_info: dict[str, Any] = {}
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

    _create_table(cur, conn)
    _seed_rows(cur, conn, seed_rows)
    next_id = seed_rows + 1

    collectors = {name: StepCollector(name) for name in OPERATION_NAMES}

    def op_insert_single() -> None:
        nonlocal next_id
        row_id = next_id
        next_id += 1
        cur.execute(SQL_INSERT_ONE, (row_id, f"single_{row_id}", row_id))
        cur.execute(SQL_DELETE_BY_PK, (row_id,))
        conn.commit()

    def op_insert_batch() -> None:
        nonlocal next_id
        start = next_id
        values_sql = ", ".join(["(?, ?, ?)"] * batch_size)
        params: list[Any] = []
        for offset in range(batch_size):
            rid = start + offset
            params.extend((rid, f"batch_{rid}", rid))
        next_id += batch_size
        insert_batch_sql = (
            "INSERT INTO bench_orm_overhead_items (id, name, amount) VALUES " + values_sql
        )
        cur.execute(insert_batch_sql, tuple(params))
        for offset in range(batch_size):
            rid = start + offset
            cur.execute(SQL_DELETE_BY_PK, (rid,))
        conn.commit()

    def op_select_by_pk() -> None:
        rid = rng.randint(1, seed_rows)
        cur.execute(SQL_SELECT_BY_PK, (rid,))
        cur.fetchone()

    def op_select_full_scan() -> None:
        cur.execute(SQL_SELECT_ALL)
        cur.fetchall()

    def op_update_by_pk() -> None:
        rid = rng.randint(1, seed_rows)
        new_amount = rng.randint(1, 1_000_000)
        cur.execute(SQL_UPDATE_BY_PK, (new_amount, rid))
        conn.commit()

    def op_delete_by_pk() -> None:
        rid = rng.randint(1, seed_rows)
        cur.execute(SQL_DELETE_BY_PK, (rid,))
        cur.execute(SQL_INSERT_ONE, (rid, f"restored_{rid}", rid))
        conn.commit()

    operations: list[tuple[str, Any]] = [
        ("insert_single", op_insert_single),
        ("insert_batch", op_insert_batch),
        ("select_by_pk", op_select_by_pk),
        ("select_full_scan", op_select_full_scan),
        ("update_by_pk", op_update_by_pk),
        ("delete_by_pk", op_delete_by_pk),
    ]

    bench_start = time.perf_counter()
    for name, fn in operations:
        if input_obj.warmup_s > 0:
            deadline = time.perf_counter() + input_obj.warmup_s
            while time.perf_counter() < deadline:
                try:
                    fn()
                except Exception:
                    pass

        deadline = time.perf_counter() + input_obj.duration_s
        while time.perf_counter() < deadline:
            t0 = time.perf_counter_ns()
            sec = int(time.perf_counter() - bench_start)
            try:
                fn()
                collectors[name].record(time.perf_counter_ns() - t0, sec)
            except Exception:
                collectors[name].record_error(sec)

    actual_duration = time.perf_counter() - bench_start

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

    output_steps = [
        collectors[name].to_output(
            actual_duration,
            sample_limit=sample_limit,
            rng=random.Random(42),
        )
        for name in OPERATION_NAMES
    ]

    return {
        "status": "ok",
        "steps": output_steps,
        "duration_s": actual_duration,
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
        _fatal("usage: worker_raw_pycubrid.py <config.json>")
    try:
        input_obj = _parse_input(sys.argv[1])
        output = run_worker(input_obj)
        sys.stdout.write(json.dumps(output, indent=2) + "\n")
    except Exception as exc:
        _fatal(str(exc))


if __name__ == "__main__":
    main()
