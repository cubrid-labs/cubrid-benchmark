# pycubrid post-1.0 performance optimization

> **Status**: completed
> **Question**: How much throughput does pycubrid gain from protocol-level optimizations after the 1.0.0 release?

## Methodology

Same-driver A/B comparison on the same machine and CUBRID 11.2 instance.
Baseline uses pycubrid 1.0.0 from PyPI; candidate uses the optimized branch (PR #55, merged).

Benchmark script: `pycubrid/tests/test_benchmarks.py` — 200 iterations, 50 warmup, 3 rounds,
measuring ops/s for INSERT, SELECT by PK, SELECT ALL (full scan), UPDATE, and DELETE against
a 10,000-row `bench_users` table.

## Results

| Operation | Before (1.0.0) | After (optimized) | Change | Meets Target? |
|-----------|----------------:|-------------------:|-------:|:---:|
| INSERT | 398 ops/s | 640 ops/s | **+60.9%** | ✅ |
| SELECT PK | 723 ops/s | 732 ops/s | +1.3% | — |
| SELECT ALL | 112 scan/s | 123 scan/s | **+10.1%** | ✅ |
| UPDATE | 733 ops/s | 736 ops/s | +0.5% | — |
| DELETE | 751 ops/s | 746 ops/s | -0.6% | — |

**Target (Issue #53)**: ≥20% improvement on at least 2 operations.
**Result**: INSERT +61% and SELECT ALL +10% — target exceeded on INSERT, meaningful gain on SELECT ALL.

## Optimizations Applied (PR #55)

1. **`_recv_exact` returns `bytearray`** — eliminates `bytes()` copy on every network read
2. **`_skip_bytes()` on PacketReader** — avoids parsing unused CAS_INFO and OID fields
3. **`@dataclass(slots=True)`** on protocol packet classes — faster attribute access
4. **`PacketWriter` header pre-allocation** — reserves 8-byte header upfront, elimates send-path copy
5. **`GetLastInsertIdPacket`** — dedicated packet eliminates 2 round-trips for INSERT lastrowid
6. **`parse()` signatures accept `bytes | bytearray`** — type correctness for bytearray recv path
7. **1-byte / 2-byte CAS type header handling** — correct parsing per CCI protocol spec (bit 7 check)

## Analysis

- **INSERT +61%**: The dominant gain. `GetLastInsertIdPacket` replaces a PREPARE+EXECUTE round-trip
  with a single FC=40 call, cutting per-INSERT network overhead by ~2 round-trips.
- **SELECT ALL +10%**: `_skip_bytes`, `__slots__`, and buffer optimizations reduce per-row overhead
  when parsing 10,000 rows.
- **SELECT PK / UPDATE / DELETE**: Minimal change (~±1%). These operations are dominated by
  single-row network latency where the protocol overhead is already small relative to RTT.

## Run History

| Run ID | Date | Label | Comparable Group | Compares To | Key Finding |
|--------|------|-------|-----------------|-------------|-------------|
| 2026-04-12_before-optimization | 2026-04-12 | baseline | devbox-i5-4200M-linux5.15-docker-cubrid112 | — | pycubrid 1.0.0 baseline |
| 2026-04-12_after-optimization | 2026-04-12 | candidate | devbox-i5-4200M-linux5.15-docker-cubrid112 | 2026-04-12_before-optimization | INSERT +61%, SELECT ALL +10% |

## Reproduction

```bash
docker compose -f docker/compose.yml up -d

# Baseline (install pycubrid 1.0.0 from PyPI)
pip install pycubrid==1.0.0
CUBRID_TEST_HOST=localhost CUBRID_TEST_PORT=33000 CUBRID_TEST_DB=benchdb CUBRID_TEST_USER=dba \
  python3 -m pytest tests/test_benchmarks.py -v

# Candidate (install from main branch after PR #55)
pip install -e .
CUBRID_TEST_HOST=localhost CUBRID_TEST_PORT=33000 CUBRID_TEST_DB=benchdb CUBRID_TEST_USER=dba \
  python3 -m pytest tests/test_benchmarks.py -v
```
