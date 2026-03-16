.PHONY: up down clean seed tier0 tier1-python all

up:
	docker compose -f docker/compose.yml up -d
	./scripts/wait_for_db.sh

down:
	docker compose -f docker/compose.yml down

clean:
	docker compose -f docker/compose.yml down -v

seed:
	python3 scripts/apply_schema.py

tier0:
	cd python && pytest bench_tier0_cubrid.py bench_tier0_mysql.py -v

tier1-python:
	cd python && pytest bench_pycubrid.py bench_pymysql.py --benchmark-json=../results/python_tier1.json -v

all: tier0 tier1-python
