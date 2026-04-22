# 2026-04-22_multitrial-baseline

> Five serial trials per worker using the exact same WorkerInput as 2026-04-21.
> Statistics summarize trial-level `throughput_ops_s` and trial-level `p95_ns` only;
> they do not recompute p95 from pooled latency samples.

| operation | worker | ops/s median | ops/s [min..max] | ops/s IQR | p95 ms median | p95 ms [min..max] | p95 ms IQR |
|---|---|---:|---:|---:|---:|---:|---:|
| insert_single | raw_pycubrid | 2.42 | [2.33..2.51] | 0.05 | 66.68 | [66.67..66.71] | 0.03 |
| insert_batch | raw_pycubrid | 0.83 | [0.83..0.86] | 0.01 | 203.63 | [199.44..221.92] | 10.90 |
| select_by_pk | raw_pycubrid | 115.61 | [114.92..116.23] | 0.94 | 1.57 | [1.50..1.60] | 0.02 |
| select_full_scan | raw_pycubrid | 18.14 | [17.86..18.15] | 0.22 | 9.89 | [9.78..10.13] | 0.24 |
| update_by_pk | raw_pycubrid | 2.69 | [2.63..2.77] | 0.10 | 66.52 | [55.68..66.61] | 0.06 |
| delete_by_pk | raw_pycubrid | 2.39 | [2.33..2.45] | 0.06 | 66.71 | [66.66..66.75] | 0.03 |
| insert_single | sqlalchemy_core | 2.38 | [2.37..2.45] | 0.08 | 66.77 | [66.69..66.84] | 0.08 |
| insert_batch | sqlalchemy_core | 1.95 | [1.92..2.09] | 0.05 | 88.49 | [78.07..88.65] | 0.06 |
| select_by_pk | sqlalchemy_core | 95.16 | [90.58..96.40] | 1.80 | 1.88 | [1.80..2.03] | 0.03 |
| select_full_scan | sqlalchemy_core | 16.49 | [16.29..16.71] | 0.17 | 10.85 | [10.73..11.02] | 0.14 |
| update_by_pk | sqlalchemy_core | 2.59 | [2.52..2.78] | 0.11 | 66.67 | [66.38..66.68] | 0.16 |
| delete_by_pk | sqlalchemy_core | 2.37 | [2.34..2.49] | 0.00 | 66.72 | [66.70..66.89] | 0.03 |
| insert_single | sqlalchemy_orm | 2.09 | [2.06..2.16] | 0.06 | 78.38 | [77.87..79.37] | 0.38 |
| insert_batch | sqlalchemy_orm | 1.06 | [1.05..1.06] | 0.00 | 165.25 | [154.67..184.37] | 0.75 |
| select_by_pk | sqlalchemy_orm | 66.95 | [62.45..67.02] | 2.28 | 2.54 | [2.53..3.05] | 0.14 |
| select_full_scan | sqlalchemy_orm | 8.06 | [7.54..8.18] | 0.22 | 33.61 | [32.93..34.16] | 0.71 |
| update_by_pk | sqlalchemy_orm | 2.21 | [2.18..2.31] | 0.04 | 77.99 | [72.72..78.15] | 0.58 |
| delete_by_pk | sqlalchemy_orm | 2.12 | [1.92..2.27] | 0.07 | 78.41 | [76.68..98.31] | 0.33 |

## Per-worker averages

> Simple arithmetic mean across the six operations within each trial, then summarized across 5 trials.

| worker | avg ops/s median | avg ops/s [min..max] | avg ops/s IQR | avg p95 ms median | avg p95 ms [min..max] | avg p95 ms IQR |
|---|---:|---:|---:|---:|---:|---:|
| raw_pycubrid | 23.68 | [23.55..23.79] | 0.17 | 69.14 | [66.73..72.20] | 1.91 |
| sqlalchemy_core | 20.19 | [19.45..20.39] | 0.34 | 50.21 | [48.54..50.25] | 0.04 |
| sqlalchemy_orm | 13.73 | [12.87..13.79] | 0.34 | 72.85 | [72.35..74.62] | 1.94 |
