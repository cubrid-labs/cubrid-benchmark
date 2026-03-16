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
    "CREATE TABLE bench_driver_pymysql ("
    "id INT AUTO_INCREMENT PRIMARY KEY, "
    "name VARCHAR(100), "
    "amount INT"
    ")"
)


def _reset_table(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DROP TABLE IF EXISTS bench_driver_pymysql")
    cursor.execute(TABLE_SQL)
    conn.commit()


@pytest.fixture
def mysql_bench_cursor(mysql_conn: DBConnection) -> Generator[DBCursor, None, None]:
    cursor = mysql_conn.cursor()
    _reset_table(cursor, mysql_conn)
    try:
        yield cursor
    finally:
        cursor.execute("DROP TABLE IF EXISTS bench_driver_pymysql")
        mysql_conn.commit()
        cursor.close()


def _run_insert_sequential(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pymysql")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pymysql (name, amount) VALUES (%s, %s)",
            ("insert_{:05d}".format(i), i),
        )
    conn.commit()


def _run_select_by_pk(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pymysql")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pymysql (name, amount) VALUES (%s, %s)",
            ("select_{:05d}".format(i), i),
        )
    conn.commit()
    for i in range(1, 10001):
        cursor.execute("SELECT id, name, amount FROM bench_driver_pymysql WHERE id = %s", (i,))
        cursor.fetchone()


def _run_select_full_scan(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pymysql")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pymysql (name, amount) VALUES (%s, %s)",
            ("scan_{:05d}".format(i), i),
        )
    conn.commit()
    cursor.execute("SELECT id, name, amount FROM bench_driver_pymysql")
    cursor.fetchall()


def _run_update_indexed(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pymysql")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pymysql (name, amount) VALUES (%s, %s)",
            ("update_{:05d}".format(i), i),
        )
    conn.commit()
    for i in range(1, 1001):
        cursor.execute("UPDATE bench_driver_pymysql SET amount = %s WHERE id = %s", (i + 100000, i))
    conn.commit()


def _run_delete_sequential(cursor: DBCursor, conn: DBConnection) -> None:
    cursor.execute("DELETE FROM bench_driver_pymysql")
    conn.commit()
    for i in range(1, 10001):
        cursor.execute(
            "INSERT INTO bench_driver_pymysql (name, amount) VALUES (%s, %s)",
            ("delete_{:05d}".format(i), i),
        )
    conn.commit()
    for i in range(1, 1001):
        cursor.execute("DELETE FROM bench_driver_pymysql WHERE id = %s", (i,))
    conn.commit()


def test_bench_insert_sequential(benchmark, mysql_bench_cursor, mysql_conn) -> None:
    benchmark.pedantic(
        _run_insert_sequential,
        args=(mysql_bench_cursor, mysql_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_select_by_pk(benchmark, mysql_bench_cursor, mysql_conn) -> None:
    benchmark.pedantic(
        _run_select_by_pk,
        args=(mysql_bench_cursor, mysql_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_select_full_scan(benchmark, mysql_bench_cursor, mysql_conn) -> None:
    benchmark.pedantic(
        _run_select_full_scan,
        args=(mysql_bench_cursor, mysql_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_update_indexed(benchmark, mysql_bench_cursor, mysql_conn) -> None:
    benchmark.pedantic(
        _run_update_indexed,
        args=(mysql_bench_cursor, mysql_conn),
        rounds=5,
        warmup_rounds=1,
    )


def test_bench_delete_sequential(benchmark, mysql_bench_cursor, mysql_conn) -> None:
    benchmark.pedantic(
        _run_delete_sequential,
        args=(mysql_bench_cursor, mysql_conn),
        rounds=5,
        warmup_rounds=1,
    )
