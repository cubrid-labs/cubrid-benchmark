# CUBRID Benchmark Suite

<!-- BADGES:START -->
![CI](https://github.com/cubrid-labs/cubrid-benchmark/actions/workflows/bench.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
[![GitHub stars](https://img.shields.io/github/stars/cubrid-labs/cubrid-benchmark)](https://github.com/cubrid-labs/cubrid-benchmark)
![status](https://img.shields.io/badge/status-active%20development-yellow)
<!-- BADGES:END -->

Scientific benchmark suite for CUBRID database ecosystem — reproducible experiments, automated comparison.

## Experiments

| # | Experiment | Status | Question | Latest Run | Report |
|---|---|---|---|---|---|
| 1 | Baseline (multi-language) | completed | CUBRID vs MySQL across Python/Go/TypeScript | 2026-03-16 | [Report](experiments/baseline-multilang/README.md) |
| 2 | pycubrid vs PyMySQL | completed | Cross-database driver comparison | 2026-03-27 | [Report](experiments/benchforge-pycubrid-vs-pymysql/README.md) |
| 3 | pycubrid vs CUBRIDdb | active | Same-database driver comparison, optimization targets | 2026-03-27 | [Report](experiments/driver-comparison/README.md) |
| 4 | Row-count sweep | active | SELECT fetch scaling by result set size (100–10K rows) | 2026-03-27 | [Report](experiments/row-count-sweep/README.md) |
| 5 | ORM overhead | scaffold | Raw pycubrid vs SQLAlchemy Core vs SQLAlchemy ORM | — | [Report](experiments/orm-overhead/README.md) |

## Quick Start

```bash
make up        # Start CUBRID + MySQL Docker containers
make seed      # Apply schema
make all       # Run all benchmarks
```

## Drivers Tested

| Language | CUBRID Driver | MySQL Driver |
|----------|--------------|--------------|
| Python | [pycubrid](https://github.com/cubrid-labs/pycubrid) v0.6.0 | PyMySQL |
| Python | [CUBRIDdb](https://github.com/cubrid/cubrid-python) v9.3.0.1 (C ext) | — |
| TypeScript | [cubrid-client](https://github.com/cubrid-labs/cubrid-client) v1.1.0 | mysql2 |
| Go | [cubrid-go](https://github.com/cubrid-labs/cubrid-go) v0.2.1 | go-sql-driver/mysql |

## Tier Model

| Tier | Description | Status |
|------|-------------|--------|
| 0 | Functional smoke (connect + CRUD) | ✅ |
| 1 | Driver throughput (sequential ops) | ✅ |
| 2 | ORM overhead vs raw driver | Planned |
| 3/4 | Concurrency and soak stability | Planned |

## Links

- [Roadmap](ROADMAP.md)
- [Methodology](docs/METHODOLOGY.md)
- [Project Board](https://github.com/orgs/cubrid-labs/projects/2)
- [CUBRID Ecosystem](https://github.com/cubrid-labs)

## License

MIT
