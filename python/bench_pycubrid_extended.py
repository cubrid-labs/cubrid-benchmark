from __future__ import annotations

import importlib
import os
from collections.abc import Callable, Generator, Sequence
from concurrent.futures import ThreadPoolExecutor
from typing import Protocol, cast

import pytest


class DBCursor(Protocol):
    def execute(self, sql: str, params: tuple[object, ...] | None = None) -> object: ...

    def executemany(self, sql: str, params: Sequence[tuple[object, ...]]) -> object: ...

    def fetchone(self) -> tuple[object, ...] | None: ...

    def close(self) -> None: ...


class DBConnection(Protocol):
    def cursor(self) -> DBCursor: ...

    def commit(self) -> None: ...

    def close(self) -> None: ...


TABLE_SQL = (
    "CREATE TABLE bench_driver_pycubrid_extended ("
    "id INT AUTO_INCREMENT PRIMARY KEY, "
    "name VARCHAR(100), "
    "amount INT"
    ")"
)


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


def _connect_cubrid() -> DBConnection:
    cubrid_module = importlib.import_module("pycubrid")
    cubrid_connect = getattr(cubrid_module, "connect")
    return cast(
        DBConnection,
        cubrid_connect(
            host=_env("CUBRID_HOST", "localhost"),
            port=int(_env("CUBRID_PORT", "33000")),
            database=_env("CUBRID_DB", "benchdb"),
            user="dba",
            password="",
        ),
    )


def _reset_table(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DROP TABLE IF EXISTS bench_driver_pycubrid_extended")
    cursor.execute(TABLE_SQL)
    conn.commit()


@pytest.fixture
def cubrid_extended_cursor(cubrid_conn: DBConnection) -> Generator[DBCursor, None, None]:
    cursor = cubrid_conn.cursor()
    _reset_table(cursor, cubrid_conn)
    try:
        yield cursor
    finally:
        cursor.execute("DROP TABLE IF EXISTS bench_driver_pycubrid_extended")
        cubrid_conn.commit()
        cursor.close()


@pytest.fixture
def cubrid_connect_factory() -> Callable[[], DBConnection]:
    return _connect_cubrid


def _insert_rows(cursor: DBCursor, rows: Sequence[tuple[object, ...]]) -> None:
    sql = "INSERT INTO bench_driver_pycubrid_extended (name, amount) VALUES (?, ?)"
    executemany = getattr(cursor, "executemany", None)
    if callable(executemany):
        executemany(sql, rows)
        return
    for row in rows:
        cursor.execute(sql, row)


def _seed_rows(cursor: DBCursor, conn: DBConnection, prefix: str, count: int = 1000) -> None:
    cursor.execute("DELETE FROM bench_driver_pycubrid_extended")
    conn.commit()
    rows = [("{}_{:05d}".format(prefix, i), i) for i in range(1, count + 1)]
    _insert_rows(cursor, rows)
    conn.commit()


def _run_connect_disconnect(connect_factory: Callable[[], DBConnection]) -> None:
    for _ in range(100):
        conn = connect_factory()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()


def _run_prepared_statement(cursor: DBCursor, conn: DBConnection) -> None:
    _seed_rows(cursor, conn, "prepared", 1000)
    for i in range(1, 1001):
        cursor.execute(
            "SELECT id, name, amount FROM bench_driver_pycubrid_extended WHERE amount = ?",
            (i,),
        )
        cursor.fetchone()


def _run_batch_insert(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pycubrid_extended")
    conn.commit()
    rows = [("batch_{:05d}".format(i), i) for i in range(1, 1001)]
    _insert_rows(cursor, rows)
    conn.commit()


def _run_concurrent_select(
    connect_factory: Callable[[], DBConnection], cursor: DBCursor, conn: DBConnection
) -> None:
    _seed_rows(cursor, conn, "concurrent", 1000)

    def _worker(start: int, end: int) -> None:
        worker_conn = connect_factory()
        worker_cursor = worker_conn.cursor()
        try:
            for amount in range(start, end + 1):
                worker_cursor.execute(
                    "SELECT id, name, amount FROM bench_driver_pycubrid_extended WHERE amount = ?",
                    (amount,),
                )
                worker_cursor.fetchone()
        finally:
            worker_cursor.close()
            worker_conn.close()

    ranges = [(1, 250), (251, 500), (501, 750), (751, 1000)]
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(lambda values: _worker(values[0], values[1]), ranges))


def test_bench_connect_disconnect(benchmark, cubrid_connect_factory) -> None:
    benchmark.pedantic(
        _run_connect_disconnect,
        args=(cubrid_connect_factory,),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_prepared_statement(benchmark, cubrid_extended_cursor, cubrid_conn) -> None:
    benchmark.pedantic(
        _run_prepared_statement,
        args=(cubrid_extended_cursor, cubrid_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_batch_insert(benchmark, cubrid_extended_cursor, cubrid_conn) -> None:
    benchmark.pedantic(
        _run_batch_insert,
        args=(cubrid_extended_cursor, cubrid_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_concurrent_select(
    benchmark, cubrid_connect_factory, cubrid_extended_cursor, cubrid_conn
) -> None:
    benchmark.pedantic(
        _run_concurrent_select,
        args=(cubrid_connect_factory, cubrid_extended_cursor, cubrid_conn),
        rounds=5,
        warmup_rounds=1,
    )
