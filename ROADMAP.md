# Roadmap

> **Last updated**: 2026-03-22
>
> This roadmap reflects current priorities. For the ecosystem-wide view, see the
> [CUBRID Labs Ecosystem Roadmap](https://github.com/cubrid-labs/.github/blob/main/ROADMAP.md).

## Links

- 📋 [GitHub Milestones](https://github.com/cubrid-labs/cubrid-benchmark/milestones)
- 🗂️ [Org Project Board](https://github.com/orgs/cubrid-labs/projects/2)
- 🌐 [Ecosystem Roadmap](https://github.com/cubrid-labs/.github/blob/main/ROADMAP.md)
- 📝 [Benchmark Plan](BENCHMARK_PLAN.md)

## Next Release — v1.0 — Comprehensive Benchmarks

See [BENCHMARK_PLAN.md](BENCHMARK_PLAN.md) for the detailed two-track strategy.

### Phase 1 (Immediate)
- Canonical dataset schema (`kv`, `orders`, `order_items`)
- Core scenario YAML files for Python, Go, TypeScript raw drivers
- Tier 0–1 baseline benchmarks with existing benchforge workers
- Track A efficiency ratios for all 3 languages

### Phase 2 (Short-term)
- ORM benchmarks: SQLAlchemy, GORM, Drizzle via ORM workers
- Prepared statement scenario variants
- Nightly CI workflow with regression detection
- Track B comparison using Go prepared-statement results

### Phase 3 (Medium-term)
- Rust external worker (cubrid-rs + sqlx)
- Rust ORM benchmarks (SeaORM)
- Tier 3b/3c concurrency stress (50/100 connections)
- Tier 4 soak/leak testing with resource sampling
- GitHub Pages dashboard with trend lines

## Compatibility

- Python 3.10+, Node.js 18+, Go 1.21+
- CUBRID 11.2 and MySQL 8.0 (comparison target)
- Docker-based reproducible environment
