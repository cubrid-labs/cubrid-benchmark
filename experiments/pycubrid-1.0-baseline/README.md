# pycubrid 1.0.0 baseline

> **Status**: completed
> **Question**: What is the official pycubrid/sqlalchemy-cubrid 1.0.0 baseline for future benchmark comparisons?

## Methodology

This experiment records the official Python baseline for the pycubrid 1.0.0 release line on the
standard CUBRID 11.2 benchmark environment. The recorded numbers are taken from the
post-1.0 optimization experiment's AFTER results, because PR #55 was merged into the 1.0.0+
release line and defines the new baseline for future comparisons.

The workload covers the existing Tier 1 pycubrid driver benchmarks: INSERT, SELECT by primary key,
SELECT full scan, UPDATE, and DELETE.

## Results

| Operation | Baseline (1.0.0) |
|-----------|-----------------:|
| INSERT | 640 ops/s |
| SELECT_PK | 732 ops/s |
| SELECT_ALL | 123 scan/s |
| UPDATE | 736 ops/s |
| DELETE | 746 ops/s |

## Run History

| Run ID | Date | Label | Comparable Group | Compares To | Key Finding |
|--------|------|-------|-----------------|-------------|-------------|
| 2026-04-12_1.0.0-baseline | 2026-04-12 | 1.0.0-baseline | devbox-i5-4200M-linux5.15-docker-cubrid112 | — | Official pycubrid 1.0.0 baseline from PR #55 optimized release line |

## Latest Conclusion

pycubrid 1.0.0 establishes a new official Python baseline of 640 INSERT ops/s, 732 SELECT_PK ops/s,
123 SELECT_ALL scan/s, 736 UPDATE ops/s, and 746 DELETE ops/s. Future pycubrid and
sqlalchemy-cubrid changes should compare against this baseline within the same comparable group.

## Reproduction

```bash
docker compose -f docker/compose.yml up -d
python3 scripts/apply_schema.py
pip install -r python/requirements.txt
pytest python/bench_pycubrid.py --benchmark-json=results.json -v
```
