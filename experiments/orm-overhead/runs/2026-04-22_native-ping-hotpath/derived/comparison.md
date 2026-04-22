# 2026-04-22_native-ping-hotpath

> Paired same-version A/B: `native` CHECK_CAS ping vs forced `select1` ping path.
> Verdict uses bootstrap 95% CI on paired trial deltas. Throughput delta > 0 is good; p50 delta < 0 is good.

## Overall classification

**practical app-level win**

| worker | step | throughput median delta % | throughput 95% CI | p50 median delta % | p50 95% CI | p95 median delta % | p95 95% CI | verdict |
|---|---|---:|---:|---:|---:|---:|---:|---|
| raw_pycubrid_ping | ping_only | 279.86 | [277.98..283.89] | -73.67 | [-73.98..-73.54] | -76.24 | [-76.72..-75.58] | WIN |
| raw_pycubrid_ping | ping_select_by_pk | 39.30 | [37.84..40.53] | -28.77 | [-29.15..-27.60] | -27.89 | [-28.70..-27.04] | WIN |
| sqlalchemy_core_ping | checkout_only | 587.79 | [581.84..603.79] | -85.35 | [-85.62..-85.25] | -85.67 | [-86.27..-85.56] | WIN |
| sqlalchemy_core_ping | checkout_select_by_pk | 108.16 | [107.77..109.57] | -48.74 | [-48.92..-48.57] | -60.79 | [-60.97..-60.75] | WIN |
| sqlalchemy_orm_ping | session_select_by_pk | 42.08 | [41.78..43.93] | -29.68 | [-30.52..-29.58] | -30.01 | [-31.39..-29.89] | WIN |
