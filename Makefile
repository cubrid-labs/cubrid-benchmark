.PHONY: up down clean seed tier0 tier0-ts tier0-go tier1-python tier1-ts tier1-go all

up:
	docker compose -f docker/compose.yml up -d
	./scripts/wait_for_db.sh

down:
	docker compose -f docker/compose.yml down

clean:
	docker compose -f docker/compose.yml down -v

seed:
	python3 scripts/apply_schema.py

# Python
tier0:
	cd python && pytest bench_tier0_cubrid.py bench_tier0_mysql.py -v

tier1-python:
	cd python && pytest bench_pycubrid.py bench_pymysql.py --benchmark-json=../results/python_tier1.json -v

# TypeScript
tier0-ts:
	cd typescript && npm run tier0

tier1-ts:
	cd typescript && npm run tier1

# Go
tier0-go:
	cd go && go test -v -run TestTier0 -timeout 120s ./...

tier1-go:
	cd go && go test -v -run TestTier1 -timeout 900s ./...

all: tier0 tier1-python tier0-ts tier1-ts tier0-go tier1-go
