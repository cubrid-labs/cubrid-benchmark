# CUBRID Benchmark Suite

![CI](https://github.com/cubrid-labs/cubrid-benchmark/actions/workflows/bench.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Unified benchmark suite for CUBRID 11.2 vs MySQL 8.0 across Python, TypeScript, and Go drivers.

## Overview

This repository benchmarks:
- **CUBRID 11.2** against **MySQL 8.0**
- Identical operations and deterministic data
- Driver-level throughput across 3 languages

### Tier Model

| Tier | Description | Status |
|------|-------------|--------|
| **Tier 0** | Functional smoke (connect + CRUD) | ✅ Python, TypeScript, Go |
| **Tier 1** | Driver throughput (sequential ops) | ✅ Python, TypeScript, Go |
| Tier 2 | ORM overhead vs raw driver | Planned |
| Tier 3/4 | Concurrency and soak stability | Planned |

## Benchmark Results

> **Environment**: Intel Core i5-9400F @ 2.90GHz · 6 cores · Linux x86_64  
> **Databases**: CUBRID 11.2 (Docker) · MySQL 8.0 (Docker) · localhost networking  
> **Date**: 2026-03-17

### Python — pycubrid vs PyMySQL (1000 rows × 5 rounds)

| Operation | CUBRID (s) | MySQL (s) | Ratio |
|-----------|-----------|-----------|-------|
| insert_sequential | 10.47 | 1.74 | 6.0× |
| select_by_pk | 15.99 | 3.52 | 4.5× |
| select_full_scan | 10.31 | 1.86 | 5.5× |
| update_indexed | 10.70 | 2.19 | 4.9× |
| delete_sequential | 10.75 | 2.10 | 5.1× |

### TypeScript — cubrid-client vs mysql2 (100 rows × 3 rounds)

| Operation | CUBRID (s) | MySQL (s) | Ratio |
|-----------|-----------|-----------|-------|
| insert_sequential | 6.18 | 14.85 | 0.4× |
| select_by_pk | 6.57 | 13.89 | 0.5× |
| select_full_scan | 5.60 | 14.71 | 0.4× |
| update_indexed | 6.32 | 14.87 | 0.4× |
| delete_sequential | 6.47 | 14.56 | 0.4× |

### Go — cubrid-go vs go-sql-driver/mysql (1000 rows × 5 rounds)

| Operation | CUBRID (s) | MySQL (s) | Ratio |
|-----------|-----------|-----------|-------|
| insert_sequential | 0.98 | 1.02 | 1.0× |
| select_by_pk | 1.58 | 1.14 | 1.4× |
| select_full_scan | 1.02 | 1.11 | 0.9× |
| update_indexed | 1.07 | 1.11 | 1.0× |
| delete_sequential | 1.14 | 1.06 | 1.1× |

### Key Takeaways

- **Go**: CUBRID and MySQL perform nearly identically at the driver level (~1:1 ratio)
- **TypeScript**: cubrid-client (native CAS protocol) outperforms mysql2 for equivalent operations
- **Python**: pycubrid (pure Python) is slower than PyMySQL due to Python-level protocol parsing overhead
- All drivers pass functional smoke tests (Tier 0) for both databases

## Quick Start

```bash
make up        # Start CUBRID + MySQL Docker containers
make seed      # Apply schema
make all       # Run all benchmarks
```

### Run by Language

```bash
# Python
make tier0             # Python tier0
make tier1-python      # Python tier1

# TypeScript
make tier0-ts          # TypeScript tier0
make tier1-ts          # TypeScript tier1

# Go
make tier0-go          # Go tier0
make tier1-go          # Go tier1
```

## Architecture

```text
┌──────────────────────────────────────┐
│               Makefile               │
│    up/down/seed/tier0/tier1/all      │
└──────────────────┬───────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
┌────────▼────────┐ ┌────────▼────────┐
│ docker/compose  │ │    schema/      │
│ CUBRID + MySQL  │ │ init + seed SQL │
└────────┬────────┘ └────────┬────────┘
         │                   │
         └─────────┬─────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
┌───▼───┐   ┌─────▼─────┐   ┌───▼───┐
│python/│   │typescript/│   │  go/  │
│tier0+1│   │  tier0+1  │   │tier0+1│
└───┬───┘   └─────┬─────┘   └───┬───┘
    │              │              │
    └──────────────┼──────────────┘
                   │
         ┌─────────▼─────────┐
         │    results/*.json  │
         │  + GitHub Actions  │
         └───────────────────┘
```

## Comparison Methodology

- Same schema, same deterministic seed data, same operation counts
- Same CI hardware per run to track trends over time
- Warm-up rounds before timed rounds for Tier 1
- Focus on regression detection and directional comparison

## Drivers Tested

| Language | CUBRID Driver | MySQL Driver | Row Count | Rounds |
|----------|--------------|--------------|-----------|--------|
| Python | [pycubrid](https://github.com/cubrid-labs/pycubrid) v0.5.0 | PyMySQL | 1000 | 5 |
| TypeScript | [cubrid-client](https://github.com/cubrid-labs/cubrid-client) v1.1.0 | mysql2 | 100 | 3 |
| Go | [cubrid-go](https://github.com/cubrid-labs/cubrid-go) v0.2.1 | go-sql-driver/mysql | 1000 | 5 |

## CUBRID Ecosystem

| Package | Language | Registry |
|---------|----------|----------|
| [pycubrid](https://github.com/cubrid-labs/pycubrid) | Python | [PyPI](https://pypi.org/project/pycubrid/) |
| [sqlalchemy-cubrid](https://github.com/cubrid-labs/sqlalchemy-cubrid) | Python | [PyPI](https://pypi.org/project/sqlalchemy-cubrid/) |
| [cubrid-client](https://github.com/cubrid-labs/cubrid-client) | TypeScript | [npm](https://www.npmjs.com/package/cubrid-client) |
| [drizzle-cubrid](https://github.com/cubrid-labs/drizzle-cubrid) | TypeScript | [npm](https://www.npmjs.com/package/drizzle-cubrid) |
| [cubrid-go](https://github.com/cubrid-labs/cubrid-go) | Go | [pkg.go.dev](https://pkg.go.dev/github.com/cubrid-labs/cubrid-go) |
| [gorm-cubrid](https://github.com/cubrid-labs/gorm-cubrid) | Go | [pkg.go.dev](https://pkg.go.dev/github.com/cubrid-labs/gorm-cubrid) |
| [cubrid-rs](https://github.com/cubrid-labs/cubrid-rs) | Rust | [crates.io](https://crates.io/crates/cubrid-client) |
| [sea-orm-cubrid](https://github.com/cubrid-labs/sea-orm-cubrid) | Rust | [crates.io](https://crates.io/crates/sea-orm-cubrid) |
| [cubrid-cookbook](https://github.com/cubrid-labs/cubrid-cookbook) | Multi | — |

## License

MIT
