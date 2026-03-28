#!/usr/bin/env python3
"""benchflow external worker for SQLAlchemy Core on CUBRID."""

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

from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    bindparam,
    create_engine,
    delete,
    insert,
    select,
    text,
    update,
)

TABLE_NAME = "bench_orm_overhead_items"
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
    return WorkerInput(
        dsn=raw["dsn"],
        steps=[InputStep(**s) for s in raw.get("steps", [])],
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


def run_worker(input_obj: WorkerInput) -> dict[str, Any]:
    rng = random.Random(input_obj.seed if input_obj.seed is not None else time.time_ns())
    seed_rows = max(100, int(input_obj.worker_config.get("seed_rows", 1000)))
    batch_size = max(10, int(input_obj.worker_config.get("batch_size", 100)))
    sample_limit = max(100, int(input_obj.worker_config.get("sample_limit", 10000)))

    metadata = MetaData()
    table = Table(
        TABLE_NAME,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(128), nullable=False),
        Column("amount", Integer, nullable=False),
    )

    engine = create_engine(input_obj.dsn, future=True)
    server_info: dict[str, Any] = {}

    with engine.connect() as conn:
        try:
            version_value = conn.execute(text("SELECT version()")).scalar()
            server_info["server_version"] = version_value
        except Exception:
            pass

        for query in input_obj.setup_queries:
            conn.execute(text(query))
        conn.commit()

        conn.execute(text("DROP TABLE IF EXISTS bench_orm_overhead_items"))
        metadata.create_all(conn)
        conn.commit()

        conn.execute(delete(table))
        conn.execute(
            insert(table),
            [{"id": i, "name": f"seed_{i}", "amount": i} for i in range(1, seed_rows + 1)],
        )
        conn.commit()

        next_id = seed_rows + 1
        select_pk_stmt = select(table.c.id, table.c.name, table.c.amount).where(
            table.c.id == bindparam("id")
        )
        update_stmt = (
            update(table)
            .where(table.c.id == bindparam("row_id"))
            .values(amount=bindparam("new_amount"))
        )
        delete_stmt = delete(table).where(table.c.id == bindparam("id"))
        select_full_stmt = text("SELECT id, name, amount FROM bench_orm_overhead_items")
        insert_single_text = text(
            "INSERT INTO bench_orm_overhead_items (id, name, amount) VALUES (:id, :name, :amount)"
        )

        collectors = {name: StepCollector(name) for name in OPERATION_NAMES}

        def op_insert_single() -> None:
            nonlocal next_id
            rid = next_id
            next_id += 1
            conn.execute(insert_single_text, {"id": rid, "name": f"single_{rid}", "amount": rid})
            conn.execute(delete_stmt, {"id": rid})
            conn.commit()

        def op_insert_batch() -> None:
            nonlocal next_id
            start = next_id
            rows = []
            for offset in range(batch_size):
                rid = start + offset
                rows.append({"id": rid, "name": f"batch_{rid}", "amount": rid})
            next_id += batch_size
            conn.execute(insert(table), rows)
            conn.execute(
                delete(table).where(table.c.id >= start).where(table.c.id < start + batch_size)
            )
            conn.commit()

        def op_select_by_pk() -> None:
            rid = rng.randint(1, seed_rows)
            conn.execute(select_pk_stmt, {"id": rid}).first()

        def op_select_full_scan() -> None:
            conn.execute(select_full_stmt).all()

        def op_update_by_pk() -> None:
            rid = rng.randint(1, seed_rows)
            conn.execute(update_stmt, {"row_id": rid, "new_amount": rng.randint(1, 1_000_000)})
            conn.commit()

        def op_delete_by_pk() -> None:
            rid = rng.randint(1, seed_rows)
            conn.execute(delete_stmt, {"id": rid})
            conn.execute(insert_single_text, {"id": rid, "name": f"restored_{rid}", "amount": rid})
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
                conn.execute(text(query))
            except Exception:
                pass
        conn.execute(text("DROP TABLE IF EXISTS bench_orm_overhead_items"))
        conn.commit()

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
        _fatal("usage: worker_sqlalchemy_core.py <config.json>")
    try:
        input_obj = _parse_input(sys.argv[1])
        output = run_worker(input_obj)
        sys.stdout.write(json.dumps(output, indent=2) + "\n")
    except Exception as exc:
        _fatal(str(exc))


if __name__ == "__main__":
    main()
