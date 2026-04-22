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
| 2026-03-28_post-sa-optimization | 2026-03-28 | post-sa-optimization | devbox-i5-4200M-linux5.15-docker-cubrid112 | 2026-03-28_first-measurement | ORM absolute latency unchanged; raw pycubrid ~15% faster on writes |
| 2026-04-21_post-native-ping | 2026-04-21 | post-native-ping | devbox-i5-4200M-linux5.15-docker-cubrid112 | 2026-03-28_post-sa-optimization | Updated baseline on current stack; NOT a ping causal test (workers don't exercise ping path) |
| 2026-04-22_multitrial-baseline | 2026-04-22 | multitrial-baseline | devbox-i5-4200M-linux5.15-docker-cubrid112 | 2026-04-21_post-native-ping | 5-trial repeat shows several 04-21 read deltas were within noise bands, while Core/ORM full-scan regressions persisted |
| 2026-04-22_native-ping-hotpath | 2026-04-22 | native-ping-hotpath | devbox-i5-4200M-linux5.15-docker-cubrid112 | 2026-04-22_multitrial-baseline | Paired same-version A/B isolated native ping and showed a practical app-level hot-path win |

## 2026-04-21 update

Run [`2026-04-21_post-native-ping`](runs/2026-04-21_post-native-ping/) re-measured the same WorkerInput against the current stack (pycubrid 1.3.2, sqlalchemy-cubrid 1.4.2, SQLAlchemy 2.0.49). Preliminary numbers show improved write performance, mild read regressions (>5% on `select_by_pk` and `select_full_scan` across all three workers), and a large SQLAlchemy Core `insert_batch` gain (+123%, most likely from `use_insertmanyvalues` being enabled in the dialect rather than from ping).

> **This rerun is not a causal test of the native CHECK_CAS ping change.** The workers use a single long-lived connection without `pool_pre_ping`, so `Connection.ping()` is never called in the hot loop. The 03-28 → 04-21 delta also spans multiple stack changes (pycubrid 0.6.0 → 1.3.2, sqlalchemy-cubrid 0.7.1 → 1.4.2, SQLAlchemy 2.0.48 → 2.0.49) and is a single trial. Treat the deltas as an updated steady-state baseline only. Follow-up isolation runs (3–5 trials with bands; pycubrid 1.3.1 vs 1.3.2 raw-only; sqla 1.4.1 vs 1.4.2 with pycubrid pinned) are required before any per-change claim. Note also that worker `throughput_ops_s` is computed against the worker's total duration rather than a fixed measurement window, which slightly compresses per-step rates — this does not explain the read-only regression pattern, but is worth tracking.

## 2026-04-22 update

Run [`2026-04-22_multitrial-baseline`](runs/2026-04-22_multitrial-baseline/) repeated the exact `2026-04-21_post-native-ping` WorkerInput **5× per worker** to add trial-to-trial bands. The aggregation reports median, `[min..max]`, and IQR for each worker/operation from the five trial-level `throughput_ops_s` and `p95_ns` observations.

- **Strongest repeatable signal in the current rerun:** `select_full_scan` stayed slower than `2026-03-28_post-sa-optimization` for all three workers even after adding bands. Relative to the 04-22 five-trial medians, throughput remained lower by about **-7.4% raw**, **-8.6% Core**, and **-6.5% ORM**; p95 latency stayed higher by about **+18.2% raw**, **+20.6% Core**, and **+5.9% ORM**.
- **Smaller and less stable than `select_full_scan`:** `select_by_pk` also remained worse than the 03-28 single-trial baseline in the 04-22 medians, but the 04-21 single-trial values were not consistently representative of the new 5-trial band. Raw and ORM 04-21 throughput landed outside the 04-22 throughput band, and ORM 04-21 p95 was below the 04-22 band floor, so this shift should be treated as weaker evidence than the full-scan regression rather than as a cleanly established or disproven effect.
- **Still separate from ping:** this remains a steady-state rerun, not a ping causal test. The workers keep one long-lived connection and do not enable `pool_pre_ping`, so the native ping path is still absent from the hot loop.

One environment caveat: runtime verification on 2026-04-22 found **SQLAlchemy 2.0.48** installed locally, not `2.0.49` as recorded in the 04-21 run metadata. That mismatch weakens direct stack attribution further, but it does not change the main conclusion from the 5-trial rerun: `select_full_scan` remains the clearest repeated regression, while `select_by_pk` is smaller and less stable to interpret.

To regenerate the multitrial derived artifacts from the raw JSON outputs, run:

```bash
python3 scripts/aggregate_multitrial.py
```

## 2026-04-22 native ping hot-path

Run [`2026-04-22_native-ping-hotpath`](runs/2026-04-22_native-ping-hotpath/) is the **causal** test the earlier 04-21 and 04-22 reruns were not: a paired same-version A/B on the exact installed stack, with only the ping path switched between native CHECK_CAS (`native`) and forced cursor `SELECT 1` (`select1`). The SQLAlchemy workers keep `pool_pre_ping=true`, `pool_size=1`, and short-lived `connect()` / `Session()` loops so ping is exercised on every checkout; the `select1` arm monkey-patches only `engine.dialect.do_ping`, isolating the ping mechanism itself.

- **Mechanism confirmed**: raw `ping_only` showed a large win for native ping (median throughput delta **+279.9%**, bootstrap 95% CI **[+278.0%, +283.9%]**), with p50/p95 both materially lower and zero errors in both arms.
- **App-level hot path also improved**: both SQLAlchemy hot-path steps cleared the practical-win bar with CI excluding zero — Core `checkout_select_by_pk` throughput median delta **+108.2%** (95% CI **[+107.8%, +109.6%]**), ORM `session_select_by_pk` **+42.1%** (95% CI **[+41.8%, +43.9%]**). p50 and p95 also improved rather than regressed.
- **Honest go/no-go conclusion**: this run supports a **practical app-level win**, not just a microbench mechanism win. Under a workload that deliberately forces pre-ping onto the hot loop, native CHECK_CAS ping is measurably and repeatedly better than the legacy `SELECT 1` path.

Methodology caveat: this is intentionally a ping-heavy benchmark, not a claim that all ORM workloads speed up by the same amount. The environment still reports **SQLAlchemy 2.0.48** locally, not 2.0.49, so the result should be interpreted as valid for the verified installed stack captured in `run.yaml`.

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

## Results: 2026-03-28_post-sa-optimization (Candidate)

### Overhead Ratios (× raw pycubrid)

| Operation | Core (baseline) | Core (new) | Δ | ORM (baseline) | ORM (new) | Δ |
|-----------|----------------|-----------|---|----------------|-----------|---|
| insert_single | 1.00× | 1.19× | +0.19 | 1.18× | 1.41× | +0.23 |
| insert_batch | 0.93× | 1.00× | +0.07 | 1.01× | 1.14× | +0.13 |
| select_by_pk | 1.16× | 1.24× | +0.08 | 1.72× | 1.78× | +0.06 |
| select_full_scan | 1.08× | 1.07× | −0.01 | 2.09× | 2.06× | −0.03 |
| update_by_pk | 0.99× | 0.99× | +0.00 | 1.03× | 1.23× | +0.20 |
| delete_by_pk | 1.00× | 1.00× | +0.00 | 1.18× | 1.18× | +0.00 |

> ⚠️ **Overhead ratios appear higher** in some cases, but this is misleading — see absolute latency comparison below.

### Absolute p50 Latency Comparison (ms)

| Operation | raw (baseline) | raw (new) | Δ | Core (baseline) | Core (new) | Δ | ORM (baseline) | ORM (new) | Δ |
|-----------|---------------|----------|---|----------------|-----------|---|----------------|----------|---|
| insert_single | 66.48 | 55.83 | −16.0% | 66.55 | 66.48 | −0.1% | 78.21 | 78.85 | +0.8% |
| insert_batch | 166.28 | 155.46 | −6.5% | 154.76 | 155.30 | +0.3% | 168.50 | 177.44 | +5.3% |
| select_by_pk | 1.10 | 1.06 | −3.6% | 1.28 | 1.31 | +2.3% | 1.89 | 1.89 | +0.0% |
| select_full_scan | 6.85 | 6.88 | +0.4% | 7.41 | 7.39 | −0.3% | 14.30 | 14.17 | −0.9% |
| update_by_pk | 66.28 | 56.10 | −15.4% | 65.87 | 55.68 | −15.5% | 67.94 | 69.06 | +1.6% |
| delete_by_pk | 66.39 | 66.40 | +0.0% | 66.50 | 66.58 | +0.1% | 78.37 | 78.06 | −0.4% |

### Charts

![Overhead Comparison](runs/2026-03-28_post-sa-optimization/figures/overhead_comparison.png)
![Latency Comparison](runs/2026-03-28_post-sa-optimization/figures/latency_comparison.png)

### Analysis

The overhead *ratios* appear higher because **raw pycubrid itself improved ~15% on write operations** (insert_single: 66.5→55.8ms, update_by_pk: 66.3→56.1ms), shrinking the denominator. When examining **absolute latencies**:

- **SA Core**: Essentially unchanged. update_by_pk improved 15.5% (tracks raw improvement).
- **SA ORM**: Essentially unchanged. No significant improvement or degradation.
- **Raw pycubrid**: 15% faster on writes — this is a pycubrid v0.6.0 variance/warmup effect, not a sqlalchemy-cubrid change.

**Verdict**: The sqlalchemy-cubrid v0.7.1 query compilation caching and result mapping optimizations did **not measurably change** ORM overhead in this 10-second-per-operation benchmark. The optimizations likely benefit cold-start and varied-query workloads more than this repetitive benchmark.

## Latest Conclusion

**The 5-trial rerun weakens the original 04-21 single-trial read-regression story: `select_full_scan` remains the clearest repeated regression, while `select_by_pk` still trends slower than 03-28 but is smaller and less stable to interpret.**

Compared with `2026-03-28_post-sa-optimization` using the 04-22 five-trial medians:

- **raw pycubrid**: write-heavy operations remain improved; `select_full_scan` still regresses clearly, while `select_by_pk` also remains slower than 03-28 but is less stable to attribute from one trial
- **SQLAlchemy Core**: `insert_batch` remains much faster (still most plausibly tied to `use_insertmanyvalues`, not ping); `select_full_scan` regression persists, while `select_by_pk` remains a milder shift that needs more controlled follow-up
- **SQLAlchemy ORM**: write performance remains improved overall; `select_full_scan` still regresses, and `select_by_pk` also trends slower than 03-28, but the 04-21 single-trial value does not map cleanly onto the 5-trial band

The original overhead shape still holds — Core stays near raw for many operations, ORM still carries the largest read overhead. But this experiment still does **not** isolate native CHECK_CAS ping behavior: the workers use a single long-lived connection without `pool_pre_ping`, so the ping path is never exercised in the hot loop. The rerun also exposed an environment mismatch (`SQLAlchemy 2.0.48` observed locally on 2026-04-22 versus `2.0.49` recorded in the 04-21 metadata), so any per-change attribution would remain unsound even with the improved statistics.

**Next steps**:

1. Isolate pycubrid by running the raw worker on `1.3.1` vs `1.3.2` only (everything else fixed).
2. Isolate sqlalchemy-cubrid by running Core/ORM on `1.4.1` vs `1.4.2` with pycubrid pinned to `1.3.2`.
3. Investigate the Core `insert_batch` improvement as a separate finding tied to `use_insertmanyvalues`.
4. Add a connection-health / reconnect-heavy benchmark where native ping behavior is actually on the hot path.

### Environment

- CUBRID 11.2.9.0866 (Docker, container `pycubrid-cubrid-1`)
- pycubrid 1.3.2, sqlalchemy-cubrid 1.4.2, SQLAlchemy 2.0.49 in the 04-21 metadata; 04-22 runtime verification found 2.0.48 locally
- CPython 3.10.12, Intel i5-4200M, 4 cores, 15.3 GB RAM
- Protocol: 10s duration per operation, 2s warmup, seed=42, 1000 seed rows, batch_size=100, concurrency=1
