.PHONY: up down clean seed tier0 tier0-ts tier0-go tier1-python tier1-python-extended tier1-ts tier1-ts-extended tier1-go tier1-go-extended all

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

tier1-python-extended:
	cd python && python3 ../scripts/collect_metrics.py --result-json ../results/python_tier1_extended.json --metrics-json ../results/python_tier1_extended.metrics.json -- pytest bench_pycubrid_extended.py bench_pymysql_extended.py --benchmark-json=../results/python_tier1_extended.json -v

# TypeScript
tier0-ts:
	cd typescript && npm run tier0

tier1-ts:
	cd typescript && npm run tier1

tier1-ts-extended:
	cd typescript && npm run tier1:extended

# Go
tier0-go:
	cd go && go test -v -run TestTier0 -timeout 120s ./...

tier1-go:
	cd go && go test -v -bench 'Benchmark(Cubrid|Mysql)(InsertSequential|SelectByPK|SelectFullScan|UpdateIndexed|DeleteSequential)$$' -benchtime 5x -timeout 900s ./...

tier1-go-extended:
	cd go && go test -v -bench 'Benchmark(Cubrid|Mysql)(ConnectDisconnect|PreparedStatement|BatchInsert|ConcurrentSelect)$$' -benchtime 5x -timeout 900s ./...

all: tier0 tier1-python tier1-python-extended tier0-ts tier1-ts tier1-ts-extended tier0-go tier1-go tier1-go-extended
