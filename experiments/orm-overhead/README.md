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

## Latest Conclusion

No committed run data yet. This folder currently provides experiment definition and runnable worker scaffolding.
