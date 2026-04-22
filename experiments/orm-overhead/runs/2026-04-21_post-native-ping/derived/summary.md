# 2026-04-21_post-native-ping vs 2026-03-28_post-sa-optimization

| operation | worker | 03-28 ops/s | 04-21 ops/s | Δ% | 03-28 p95 ms | 04-21 p95 ms | Δ% |
|---|---|---:|---:|---:|---:|---:|---:|
| insert_single | raw_pycubrid | 2.26 | 2.40 | +6.19% | 77.62 | 66.72 | -14.04% |
| insert_batch | raw_pycubrid | 0.81 | 0.83 | +2.47% | 221.73 | 210.23 | -5.19% |
| select_by_pk | raw_pycubrid | 124.74 | 116.32 | -6.75% | 1.45 | 1.56 | +7.59% |
| select_full_scan | raw_pycubrid | 19.58 | 17.97 | -8.22% | 8.37 | 10.02 | +19.71% |
| update_by_pk | raw_pycubrid | 2.28 | 2.65 | +16.23% | 66.71 | 66.60 | -0.16% |
| delete_by_pk | raw_pycubrid | 2.20 | 2.37 | +7.73% | 77.61 | 66.81 | -13.92% |
| insert_single | sqlalchemy_core | 2.11 | 2.34 | +10.90% | 77.71 | 66.77 | -14.08% |
| insert_batch | sqlalchemy_core | 0.87 | 1.94 | +122.99% | 209.93 | 88.80 | -57.70% |
| select_by_pk | sqlalchemy_core | 103.52 | 95.81 | -7.45% | 1.65 | 1.83 | +10.91% |
| select_full_scan | sqlalchemy_core | 18.05 | 16.72 | -7.37% | 9.00 | 10.79 | +19.89% |
| update_by_pk | sqlalchemy_core | 2.35 | 2.51 | +6.81% | 66.77 | 66.72 | -0.07% |
| delete_by_pk | sqlalchemy_core | 2.03 | 2.24 | +10.34% | 77.75 | 77.63 | -0.15% |
| insert_single | sqlalchemy_orm | 1.75 | 2.02 | +15.43% | 89.46 | 80.14 | -10.42% |
| insert_batch | sqlalchemy_orm | 0.77 | 1.08 | +40.26% | 240.13 | 155.53 | -35.23% |
| select_by_pk | sqlalchemy_orm | 70.84 | 67.15 | -5.21% | 2.36 | 2.52 | +6.78% |
| select_full_scan | sqlalchemy_orm | 8.62 | 7.98 | -7.42% | 31.74 | 33.15 | +4.44% |
| update_by_pk | sqlalchemy_orm | 2.00 | 2.29 | +14.50% | 80.18 | 77.03 | -3.93% |
| delete_by_pk | sqlalchemy_orm | 1.78 | 2.00 | +12.36% | 89.69 | 88.06 | -1.82% |

## Per-worker averages

| worker | 03-28 avg ops/s | 04-21 avg ops/s | Δ% | 03-28 avg p95 ms | 04-21 avg p95 ms | Δ% |
|---|---:|---:|---:|---:|---:|---:|
| raw_pycubrid | 25.31 | 23.76 | -6.14% | 75.58 | 70.32 | -6.96% |
| sqlalchemy_core | 21.49 | 20.26 | -5.72% | 73.80 | 52.09 | -29.42% |
| sqlalchemy_orm | 14.29 | 13.75 | -3.78% | 88.93 | 72.74 | -18.20% |

## Regressions >5% (throughput drop or p95 increase)

- raw_pycubrid / select_by_pk: throughput -6.75%, p95 +7.59%
- raw_pycubrid / select_full_scan: throughput -8.22%, p95 +19.71%
- sqlalchemy_core / select_by_pk: throughput -7.45%, p95 +10.91%
- sqlalchemy_core / select_full_scan: throughput -7.37%, p95 +19.89%
- sqlalchemy_orm / select_by_pk: throughput -5.21%, p95 +6.78%
- sqlalchemy_orm / select_full_scan: throughput -7.42%, p95 +4.44%
