from __future__ import annotations

from collections.abc import Generator
from typing import Protocol

import pytest


class DBCursor(Protocol):
    def execute(self, sql: str, params: tuple[object, ...] | None = None) -> object:
        ...

    def fetchone(self) -> tuple[object, ...] | None:
        ...

    def fetchall(self) -> list[tuple[object, ...]]:
        ...

    def close(self) -> None:
        ...


class DBConnection(Protocol):
    def cursor(self) -> DBCursor:
        ...

    def commit(self) -> None:
        ...


TABLE_SQL = (
    "CREATE TABLE bench_driver_pycubrid ("
    "id INT AUTO_INCREMENT PRIMARY KEY, "
    "name VARCHAR(100), "
    "amount INT"
    ")"
)


def _reset_table(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DROP TABLE IF EXISTS bench_driver_pycubrid")
    cursor.execute(TABLE_SQL)
    conn.commit()


@pytest.fixture
def cubrid_bench_cursor(cubrid_conn: DBConnection) -> Generator[DBCursor, None, None]:
    cursor = cubrid_conn.cursor()
    _reset_table(cursor, cubrid_conn)
    try:
        yield cursor
    finally:
        cursor.execute("DROP TABLE IF EXISTS bench_driver_pycubrid")
        cubrid_conn.commit()
        cursor.close()


def _run_insert_sequential(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pycubrid")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pycubrid (name, amount) VALUES (?, ?)",
            ("insert_{:05d}".format(i), i),
        )
    conn.commit()


def _run_select_by_pk(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pycubrid")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pycubrid (name, amount) VALUES (?, ?)",
            ("select_{:05d}".format(i), i),
        )
    conn.commit()
    for i in range(1, 10001):
        cursor.execute("SELECT id, name, amount FROM bench_driver_pycubrid WHERE id = ?", (i,))
        cursor.fetchone()


def _run_select_full_scan(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pycubrid")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pycubrid (name, amount) VALUES (?, ?)",
            ("scan_{:05d}".format(i), i),
        )
    conn.commit()
    cursor.execute("SELECT id, name, amount FROM bench_driver_pycubrid")
    cursor.fetchall()


def _run_update_indexed(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pycubrid")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pycubrid (name, amount) VALUES (?, ?)",
            ("update_{:05d}".format(i), i),
        )
    conn.commit()
    for i in range(1, 1001):
        cursor.execute("UPDATE bench_driver_pycubrid SET amount = ? WHERE id = ?", (i + 100000, i))
    conn.commit()


def _run_delete_sequential(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pycubrid")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pycubrid (name, amount) VALUES (?, ?)",
            ("delete_{:05d}".format(i), i),
        )
    conn.commit()
    for i in range(1, 1001):
        cursor.execute("DELETE FROM bench_driver_pycubrid WHERE id = ?", (i,))
    conn.commit()


def test_bench_insert_sequential(benchmark, cubrid_bench_cursor, cubrid_conn) -> None:
    benchmark.pedantic(
        _run_insert_sequential,
        args=(cubrid_bench_cursor, cubrid_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_select_by_pk(benchmark, cubrid_bench_cursor, cubrid_conn) -> None:
    benchmark.pedantic(
        _run_select_by_pk,
        args=(cubrid_bench_cursor, cubrid_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_select_full_scan(benchmark, cubrid_bench_cursor, cubrid_conn) -> None:
    benchmark.pedantic(
        _run_select_full_scan,
        args=(cubrid_bench_cursor, cubrid_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_update_indexed(benchmark, cubrid_bench_cursor, cubrid_conn) -> None:
    benchmark.pedantic(
        _run_update_indexed,
        args=(cubrid_bench_cursor, cubrid_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_delete_sequential(benchmark, cubrid_bench_cursor, cubrid_conn) -> None:
    benchmark.pedantic(
        _run_delete_sequential,
        args=(cubrid_bench_cursor, cubrid_conn),
        rounds=5,
        warmup_rounds=1,
    )
