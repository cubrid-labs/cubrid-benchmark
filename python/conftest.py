from __future__ import annotations

import os
import importlib
from collections.abc import Generator
from typing import Protocol, cast

import pytest


class DBCursor(Protocol):
    def execute(self, sql: str, params: tuple[object, ...] | None = None) -> object:
        ...

    def close(self) -> None:
        ...


class DBConnection(Protocol):
    def cursor(self) -> DBCursor:
        ...

    def commit(self) -> None:
        ...

    def close(self) -> None:
        ...


def _env(name: str, default: str) -> str:
    return os.getenv(name, default)


@pytest.fixture(scope="session")
def cubrid_conn() -> Generator[DBConnection, None, None]:
    cubrid_module = importlib.import_module("pycubrid")
    cubrid_connect = getattr(cubrid_module, "connect")

    conn = cast(DBConnection, cubrid_connect(
        host=_env("CUBRID_HOST", "localhost"),
        port=int(_env("CUBRID_PORT", "33000")),
        database=_env("CUBRID_DB", "benchdb"),
        user="dba",
        password="",
    ))
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture(scope="session")
def mysql_conn() -> Generator[DBConnection, None, None]:
    pymysql = importlib.import_module("pymysql")

    conn = cast(
        DBConnection,
        pymysql.connect(
        host=_env("MYSQL_HOST", "localhost"),
        port=int(_env("MYSQL_PORT", "3306")),
        database=_env("MYSQL_DB", "benchdb"),
        user=_env("MYSQL_USER", "root"),
        password=_env("MYSQL_PASSWORD", "bench"),
        autocommit=False,
        ),
    )
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture(scope="session", autouse=True)
def session_temp_tables(
    cubrid_conn: DBConnection, mysql_conn: DBConnection
) -> Generator[None, None, None]:
    cubrid_cursor = cubrid_conn.cursor()
    mysql_cursor = mysql_conn.cursor()

    cubrid_cursor.execute("DROP TABLE IF EXISTS bench_temp_session")
    cubrid_cursor.execute("CREATE TABLE bench_temp_session (id INT AUTO_INCREMENT PRIMARY KEY, note VARCHAR(64))")
    cubrid_conn.commit()

    mysql_cursor.execute("DROP TABLE IF EXISTS bench_temp_session")
    mysql_cursor.execute("CREATE TABLE bench_temp_session (id INT AUTO_INCREMENT PRIMARY KEY, note VARCHAR(64))")
    mysql_conn.commit()

    try:
        yield
    finally:
        cubrid_cursor.execute("DROP TABLE IF EXISTS bench_temp_session")
        cubrid_conn.commit()
        cubrid_cursor.close()

        mysql_cursor.execute("DROP TABLE IF EXISTS bench_temp_session")
        mysql_conn.commit()
        mysql_cursor.close()
