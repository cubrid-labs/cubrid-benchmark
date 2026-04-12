# Baseline Benchmark Results

This file keeps major benchmark baselines easy to find. The original multi-language baseline
report remains at [experiments/baseline-multilang/README.md](experiments/baseline-multilang/README.md).

## Historical baseline reference

- **2026-03-16 multi-language baseline**: see [experiments/baseline-multilang/README.md](experiments/baseline-multilang/README.md)

## pycubrid 1.0.0 baseline (2026-04-12)

The official pycubrid 1.0.0 baseline is recorded in
[experiments/pycubrid-1.0-baseline/README.md](experiments/pycubrid-1.0-baseline/README.md).

This baseline reflects the 1.0.0 release line after the post-1.0 optimization work from PR #55,
which shipped as the new reference point for subsequent benchmark comparisons.

| Operation | Result |
|-----------|-------:|
| INSERT | 640 ops/s |
| SELECT_PK | 732 ops/s |
| SELECT_ALL | 123 scan/s |
| UPDATE | 736 ops/s |
| DELETE | 746 ops/s |
