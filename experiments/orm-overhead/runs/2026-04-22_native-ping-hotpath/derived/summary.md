# 2026-04-22_native-ping-hotpath

> Per-arm summary across 7 paired trials.

| worker | step | arm | ops/s median | ops/s [min..max] | ops/s IQR | p50 ms median | p50 ms [min..max] | p50 ms IQR | p95 ms median | errors median |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| raw_pycubrid_ping | ping_only | native | 5408.85 | [5386.29..5429.27] | 30.48 | 0.176 | [0.175..0.176] | 0.000 | 0.219 | 0 |
| raw_pycubrid_ping | ping_only | select1 | 1420.67 | [1404.80..1448.89] | 8.18 | 0.668 | [0.663..0.676] | 0.006 | 0.927 | 0 |
| raw_pycubrid_ping | ping_select_by_pk | native | 746.40 | [740.24..755.16] | 7.17 | 1.287 | [1.269..1.295] | 0.015 | 1.762 | 0 |
| raw_pycubrid_ping | ping_select_by_pk | select1 | 537.38 | [534.54..538.52] | 2.50 | 1.788 | [1.786..1.817] | 0.014 | 2.441 | 0 |
| sqlalchemy_core_ping | checkout_only | native | 2069.81 | [2050.54..2126.92] | 34.87 | 0.466 | [0.454..0.470] | 0.006 | 0.607 | 0 |
| sqlalchemy_core_ping | checkout_only | select1 | 300.94 | [299.64..303.24] | 1.41 | 3.178 | [3.163..3.188] | 0.008 | 4.247 | 0 |
| sqlalchemy_core_ping | checkout_select_by_pk | native | 334.33 | [333.07..336.02] | 2.05 | 2.912 | [2.889..2.915] | 0.017 | 3.698 | 0 |
| sqlalchemy_core_ping | checkout_select_by_pk | select1 | 160.36 | [159.81..160.92] | 0.54 | 5.667 | [5.654..5.680] | 0.020 | 9.439 | 0 |
| sqlalchemy_orm_ping | session_select_by_pk | native | 158.19 | [157.61..160.71] | 1.98 | 6.191 | [6.093..6.212] | 0.072 | 7.377 | 0 |
| sqlalchemy_orm_ping | session_select_by_pk | select1 | 111.32 | [110.98..111.53] | 0.21 | 8.808 | [8.791..8.819] | 0.005 | 10.546 | 0 |
