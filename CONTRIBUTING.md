# Contributing to cubrid-benchmark

Thank you for your interest in contributing to `cubrid-benchmark`.

## Development Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- Go 1.19+
- Git
- Docker

### Installation

```bash
git clone https://github.com/cubrid-labs/cubrid-benchmark.git
cd cubrid-benchmark

# Install Python dependencies
pip install -r python/requirements.txt

# Install Node.js dependencies
npm install --prefix typescript

# Verify Go setup (no external dependencies required)
go version
```

## Running Benchmarks

### Start CUBRID

```bash
docker compose up -d
```

### Run Python benchmarks

```bash
cd python
python -m benchmark
```

### Run TypeScript benchmarks

```bash
cd typescript
npm run benchmark
```

### Run Go benchmarks

```bash
cd go
go run main.go
```

### Cleanup

```bash
docker compose down -v
```

## Code Style

This project uses multiple linters depending on language:

**Python:**
```bash
ruff check python/
ruff format --check python/
```

**TypeScript:**
```bash
npm run lint --prefix typescript
npm run format --prefix typescript
```

**Go:**
```bash
cd go && gofmt -d .
```

## Pull Request Guidelines

1. Keep changes focused and explain the motivation in the PR description.
2. Add or update benchmarks for new test cases.
3. Ensure lint passes before submitting.
4. Run benchmarks locally and include performance data in PR description.
5. Update `CHANGELOG.md` for user-visible changes.

## Reporting Issues

When filing an issue, include:

- Language/implementation affected (Python/TypeScript/Go)
- CUBRID server version
- Driver version
- Detailed description of the benchmark issue
- Performance metrics (if applicable)
