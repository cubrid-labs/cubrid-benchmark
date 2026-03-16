# CUBRID Benchmark Suite

![CI](https://github.com/cubrid-labs/cubrid-benchmark/actions/workflows/bench.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

Unified benchmark suite for CUBRID vs MySQL across CUBRID ecosystem drivers and ORMs.

## Overview

This repository benchmarks:
- CUBRID 11.2 against MySQL 8.0
- Identical operations and deterministic data
- Driver-level and ORM-level behavior by tier

### 4-tier model

1. Tier 0: Functional smoke checks (connect + CRUD)
2. Tier 1: Driver throughput (10K/1K operation loops)
3. Tier 2: ORM overhead vs raw driver
4. Tier 3/4: Concurrency and soak stability

Phase 1 in this repo includes Tier 0 and Tier 1 (Python only).

## Quick Start

```bash
make up
make seed
make all
```

## Results

- GitHub Pages dashboard (placeholder): https://cubrid-labs.github.io/cubrid-benchmark/

## Architecture

```text
┌──────────────────────────────────────┐
│               Makefile               │
│      up/down/seed/tier0/tier1        │
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
         ┌─────────▼─────────┐
         │      python/      │
         │ tier0 + tier1     │
         └─────────┬─────────┘
                   │
         ┌─────────▼─────────┐
         │ scripts/normalize │
         │ + GitHub Actions  │
         └───────────────────┘
```

## Comparison Methodology

- Same schema, same deterministic seed data, same operation counts
- Same CI hardware per run to track trends over time
- Warm-up rounds before timed rounds for Tier 1
- Focus on regression detection and directional comparison

## CUBRID Ecosystem Repos

- https://github.com/cubrid-labs/pycubrid
- https://github.com/cubrid-labs/sqlalchemy-cubrid
- https://github.com/cubrid-labs/cubrid-go
- https://github.com/cubrid-labs/cubrid-client
- https://github.com/cubrid-labs/drizzle-cubrid
