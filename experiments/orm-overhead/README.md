# ORM Overhead on CUBRID: raw pycubrid vs SQLAlchemy Core vs SQLAlchemy ORM

> **Status**: active
> **Question**: What overhead do SQLAlchemy Core and SQLAlchemy ORM add versus raw pycubrid for identical CRUD workloads on CUBRID?

## Hypothesis

For equivalent SQL semantics on the same CUBRID server:

1. **raw pycubrid** should have the lowest client-side overhead.
2. **SQLAlchemy Core** should be close to raw for simple statements, with moderate overhead from SQL construction and abstraction.
3. **SQLAlchemy ORM** should show the highest overhead, especially for object materialization and unit-of-work bookkeeping.

## Methodology

This experiment compares three worker implementations under the same WorkerInput/WorkerOutput protocol:

- `workers/worker_raw_pycubrid.py`
- `workers/worker_sqlalchemy_core.py`
- `workers/worker_sqlalchemy_orm.py`

All workers execute the same operation set against a `bench_`-prefixed table (`bench_orm_overhead_items`):

1. `insert_single`
2. `insert_batch`
3. `select_by_pk`
4. `select_full_scan`
5. `update_by_pk`
6. `delete_by_pk`

### Worker protocol

Each worker:

- Reads a JSON config file path from CLI argument 1.
- Parses `WorkerInput` fields (`dsn`, `duration_s`, `warmup_s`, `concurrency`, `setup_queries`, `teardown_queries`, `worker_config`).
- Emits `WorkerOutput` JSON to stdout with per-step latency summaries and throughput.

### Query parameterization policy

- raw pycubrid: `?` markers
- SQLAlchemy Core/ORM: named `:param` markers for text SQL, and bound parameters for Core/ORM constructs
- No SQL string interpolation with user values

## Metrics

Per operation (`steps[]` in worker output):

- `ops`
- `errors`
- `throughput_ops_s`
- latency distribution (`min_ns`, `max_ns`, `mean_ns`, `stdev_ns`, `p50_ns`, `p95_ns`, `p99_ns`, `p999_ns`, `p9999_ns`)
- optional sampled latencies (`samples_ns`) and second-level `time_series`

## Reproduction

From repository root:

```bash
# 1) Start databases
docker compose -f docker/compose.yml up -d

# 2) Prepare an input JSON file for workers (example path)
# /tmp/orm_overhead_input.json

# 3) Run all three variants
python experiments/orm-overhead/workers/worker_raw_pycubrid.py /tmp/orm_overhead_input.json
python experiments/orm-overhead/workers/worker_sqlalchemy_core.py /tmp/orm_overhead_input.json
python experiments/orm-overhead/workers/worker_sqlalchemy_orm.py /tmp/orm_overhead_input.json
```

### Minimal example WorkerInput

```json
{
  "dsn": "cubrid+pycubrid://dba@localhost:33000/testdb",
  "steps": [],
  "concurrency": 1,
  "duration_s": 10,
  "warmup_s": 2,
  "seed": 42,
  "setup_queries": [],
  "teardown_queries": [],
  "worker_config": {
    "seed_rows": 1000,
    "batch_size": 100,
    "sample_limit": 10000
  }
}
```

## Run History

| Run ID | Date | Label | Comparable Group | Compares To | Key Finding |
|--------|------|-------|-----------------|-------------|-------------|
| 2026-03-28_first-measurement | 2026-03-28 | first-measurement | devbox-i5-4200M-linux5.15-docker-cubrid112 | — (baseline) | Core ≈ raw for writes; ORM adds 1.7–2.1× on reads |

## Results: 2026-03-28_first-measurement (Baseline)

### p50 Latency (ms)

| Operation | raw pycubrid | SA Core | SA ORM | Core Overhead | ORM Overhead |
|-----------|-------------|---------|--------|---------------|--------------|
| insert_single | 66.48 | 66.55 | 78.21 | 1.00× | 1.18× |
| insert_batch | 166.28 | 154.76 | 168.50 | 0.93× | 1.01× |
| select_by_pk | 1.10 | 1.28 | 1.89 | 1.16× | 1.72× |
| select_full_scan | 6.85 | 7.41 | 14.30 | 1.08× | 2.09× |
| update_by_pk | 66.28 | 65.87 | 67.94 | 0.99× | 1.03× |
| delete_by_pk | 66.39 | 66.50 | 78.37 | 1.00× | 1.18× |

### Throughput (ops/s)

| Operation | raw pycubrid | SA Core | SA ORM |
|-----------|-------------|---------|--------|
| insert_single | 2.1 | 2.1 | 1.8 |
| insert_batch | 0.8 | 0.9 | 0.8 |
| select_by_pk | 121.6 | 104.4 | 71.7 |
| select_full_scan | 19.7 | 18.0 | 8.6 |
| update_by_pk | 2.3 | 2.3 | 2.0 |
| delete_by_pk | 2.2 | 2.1 | 1.7 |

### Chart

![ORM Overhead Comparison](runs/2026-03-28_first-measurement/figures/orm_overhead_comparison.png)

## Latest Conclusion

**Hypothesis confirmed.** SQLAlchemy Core adds minimal overhead (0.93–1.16×) for most operations, essentially matching raw pycubrid for write-heavy workloads. SQLAlchemy ORM adds measurable overhead primarily on read operations:

- **select_full_scan**: 2.09× overhead — object materialization dominates when fetching 1000 rows
- **select_by_pk**: 1.72× overhead — identity map lookup and object construction
- **insert/update/delete**: 1.01–1.18× — write operations are dominated by network + CUBRID commit latency, so ORM overhead is negligible

**Key insight**: For CUBRID workloads, the write-path latency is dominated by server-side commit (~66ms), making ORM overhead invisible for writes. Read-path optimization (object materialization, row mapping) is where ORM overhead is most impactful.

### Environment

- CUBRID 11.2.9.0866 (Docker)
- pycubrid 0.6.0, sqlalchemy-cubrid 0.7.1, SQLAlchemy 2.0.48
- CPython 3.10.12, Intel i5-4200M, 4 cores, 15.3 GB RAM
- Protocol: 10s duration per operation, 2s warmup, seed=42, 1000 seed rows
