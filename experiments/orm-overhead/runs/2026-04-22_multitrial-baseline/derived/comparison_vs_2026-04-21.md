# 2026-04-22_multitrial-baseline vs 2026-04-21_post-native-ping

> Side-by-side of 5-trial medians versus the 2026-04-21 single trial.
> `outside_band` means the 2026-04-21 single-trial value falls outside the 2026-04-22
> five-trial [min..max] band and is therefore not representative of the repeated-run band.

| operation | worker | 04-21 ops/s | 04-22 median ops/s | 04-22 ops/s band | ops/s status | 04-21 p95 ms | 04-22 median p95 ms | 04-22 p95 band | p95 status |
|---|---|---:|---:|---:|---|---:|---:|---:|---|
| insert_single | raw_pycubrid | 2.40 | 2.42 | [2.33..2.51] | within_band | 66.72 | 66.68 | [66.67..66.71] | outside_band |
| insert_batch | raw_pycubrid | 0.83 | 0.83 | [0.83..0.86] | within_band | 210.23 | 203.63 | [199.44..221.92] | within_band |
| select_by_pk | raw_pycubrid | 116.32 | 115.61 | [114.92..116.23] | outside_band | 1.56 | 1.57 | [1.50..1.60] | within_band |
| select_full_scan | raw_pycubrid | 17.97 | 18.14 | [17.86..18.15] | within_band | 10.02 | 9.89 | [9.78..10.13] | within_band |
| update_by_pk | raw_pycubrid | 2.65 | 2.69 | [2.63..2.77] | within_band | 66.60 | 66.52 | [55.68..66.61] | within_band |
| delete_by_pk | raw_pycubrid | 2.37 | 2.39 | [2.33..2.45] | within_band | 66.81 | 66.71 | [66.66..66.75] | outside_band |
| insert_single | sqlalchemy_core | 2.34 | 2.38 | [2.37..2.45] | outside_band | 66.77 | 66.77 | [66.69..66.84] | within_band |
| insert_batch | sqlalchemy_core | 1.94 | 1.95 | [1.92..2.09] | within_band | 88.80 | 88.49 | [78.07..88.65] | outside_band |
| select_by_pk | sqlalchemy_core | 95.81 | 95.16 | [90.58..96.40] | within_band | 1.83 | 1.88 | [1.80..2.03] | within_band |
| select_full_scan | sqlalchemy_core | 16.72 | 16.49 | [16.29..16.71] | outside_band | 10.79 | 10.85 | [10.73..11.02] | within_band |
| update_by_pk | sqlalchemy_core | 2.51 | 2.59 | [2.52..2.78] | outside_band | 66.72 | 66.67 | [66.38..66.68] | outside_band |
| delete_by_pk | sqlalchemy_core | 2.24 | 2.37 | [2.34..2.49] | outside_band | 77.63 | 66.72 | [66.70..66.89] | outside_band |
| insert_single | sqlalchemy_orm | 2.02 | 2.09 | [2.06..2.16] | outside_band | 80.14 | 78.38 | [77.87..79.37] | outside_band |
| insert_batch | sqlalchemy_orm | 1.08 | 1.06 | [1.05..1.06] | outside_band | 155.53 | 165.25 | [154.67..184.37] | within_band |
| select_by_pk | sqlalchemy_orm | 67.15 | 66.95 | [62.45..67.02] | outside_band | 2.52 | 2.54 | [2.53..3.05] | outside_band |
| select_full_scan | sqlalchemy_orm | 7.98 | 8.06 | [7.54..8.18] | within_band | 33.15 | 33.61 | [32.93..34.16] | within_band |
| update_by_pk | sqlalchemy_orm | 2.29 | 2.21 | [2.18..2.31] | within_band | 77.03 | 77.99 | [72.72..78.15] | within_band |
| delete_by_pk | sqlalchemy_orm | 2.00 | 2.12 | [1.92..2.27] | within_band | 88.06 | 78.41 | [76.68..98.31] | within_band |

## 04-21 single-trial values outside the 04-22 five-trial band

- raw_pycubrid / insert_single: 04-21 p95 66.72 ms vs 04-22 band [66.67..66.71] ms
- raw_pycubrid / select_by_pk: 04-21 ops/s 116.32 vs 04-22 band [114.92..116.23]
- raw_pycubrid / delete_by_pk: 04-21 p95 66.81 ms vs 04-22 band [66.66..66.75] ms
- sqlalchemy_core / insert_single: 04-21 ops/s 2.34 vs 04-22 band [2.37..2.45]
- sqlalchemy_core / insert_batch: 04-21 p95 88.80 ms vs 04-22 band [78.07..88.65] ms
- sqlalchemy_core / select_full_scan: 04-21 ops/s 16.72 vs 04-22 band [16.29..16.71]
- sqlalchemy_core / update_by_pk: 04-21 ops/s 2.51 vs 04-22 band [2.52..2.78]
- sqlalchemy_core / update_by_pk: 04-21 p95 66.72 ms vs 04-22 band [66.38..66.68] ms
- sqlalchemy_core / delete_by_pk: 04-21 ops/s 2.24 vs 04-22 band [2.34..2.49]
- sqlalchemy_core / delete_by_pk: 04-21 p95 77.63 ms vs 04-22 band [66.70..66.89] ms
- sqlalchemy_orm / insert_single: 04-21 ops/s 2.02 vs 04-22 band [2.06..2.16]
- sqlalchemy_orm / insert_single: 04-21 p95 80.14 ms vs 04-22 band [77.87..79.37] ms
- sqlalchemy_orm / insert_batch: 04-21 ops/s 1.08 vs 04-22 band [1.05..1.06]
- sqlalchemy_orm / select_by_pk: 04-21 ops/s 67.15 vs 04-22 band [62.45..67.02]
- sqlalchemy_orm / select_by_pk: 04-21 p95 2.52 ms vs 04-22 band [2.53..3.05] ms
