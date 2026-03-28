#!/usr/bin/env python3
"""benchflow external worker for SQLAlchemy ORM on CUBRID."""

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

from sqlalchemy import Integer, String, create_engine, text
from sqlalchemy.orm import Mapped, Session, declarative_base, mapped_column

TABLE_NAME = "bench_orm_overhead_items"
Base = declarative_base()
OPERATION_NAMES = (
    "insert_single",
    "insert_batch",
    "select_by_pk",
    "select_full_scan",
    "update_by_pk",
    "delete_by_pk",
)


class BenchItem(Base):
    __tablename__ = TABLE_NAME

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)


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

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.query(BenchItem).delete()
        session.add_all(
            [BenchItem(id=i, name=f"seed_{i}", amount=i) for i in range(1, seed_rows + 1)]
        )
        session.commit()

    next_id = seed_rows + 1
    collectors = {name: StepCollector(name) for name in OPERATION_NAMES}

    def op_insert_single(session: Session) -> None:
        nonlocal next_id
        rid = next_id
        next_id += 1
        session.add(BenchItem(id=rid, name=f"single_{rid}", amount=rid))
        session.flush()
        obj = session.get(BenchItem, rid)
        if obj is not None:
            session.delete(obj)
        session.commit()

    def op_insert_batch(session: Session) -> None:
        nonlocal next_id
        start = next_id
        rows = []
        for offset in range(batch_size):
            rid = start + offset
            rows.append(BenchItem(id=rid, name=f"batch_{rid}", amount=rid))
        next_id += batch_size
        session.add_all(rows)
        session.flush()
        for row in rows:
            session.delete(row)
        session.commit()

    def op_select_by_pk(session: Session) -> None:
        rid = rng.randint(1, seed_rows)
        session.get(BenchItem, rid)

    def op_select_full_scan(session: Session) -> None:
        session.query(BenchItem).all()

    def op_update_by_pk(session: Session) -> None:
        rid = rng.randint(1, seed_rows)
        obj = session.get(BenchItem, rid)
        if obj is not None:
            obj.amount = rng.randint(1, 1_000_000)
        session.commit()

    def op_delete_by_pk(session: Session) -> None:
        rid = rng.randint(1, seed_rows)
        obj = session.get(BenchItem, rid)
        if obj is not None:
            session.delete(obj)
            session.flush()
        session.add(BenchItem(id=rid, name=f"restored_{rid}", amount=rid))
        session.commit()

    operations = [
        ("insert_single", op_insert_single),
        ("insert_batch", op_insert_batch),
        ("select_by_pk", op_select_by_pk),
        ("select_full_scan", op_select_full_scan),
        ("update_by_pk", op_update_by_pk),
        ("delete_by_pk", op_delete_by_pk),
    ]

    bench_start = time.perf_counter()
    with Session(engine) as session:
        for name, fn in operations:
            if input_obj.warmup_s > 0:
                deadline = time.perf_counter() + input_obj.warmup_s
                while time.perf_counter() < deadline:
                    try:
                        fn(session)
                    except Exception:
                        session.rollback()

            deadline = time.perf_counter() + input_obj.duration_s
            while time.perf_counter() < deadline:
                t0 = time.perf_counter_ns()
                sec = int(time.perf_counter() - bench_start)
                try:
                    fn(session)
                    collectors[name].record(time.perf_counter_ns() - t0, sec)
                except Exception:
                    session.rollback()
                    collectors[name].record_error(sec)

    actual_duration = time.perf_counter() - bench_start

    with engine.connect() as conn:
        for query in input_obj.teardown_queries:
            try:
                conn.execute(text(query))
            except Exception:
                pass
        conn.commit()

    Base.metadata.drop_all(engine)
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
        _fatal("usage: worker_sqlalchemy_orm.py <config.json>")
    try:
        input_obj = _parse_input(sys.argv[1])
        output = run_worker(input_obj)
        sys.stdout.write(json.dumps(output, indent=2) + "\n")
    except Exception as exc:
        _fatal(str(exc))


if __name__ == "__main__":
    main()
