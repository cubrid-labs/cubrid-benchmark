#!/usr/bin/env python3
"""Deterministic seed script for canonical benchmark tables (kv, orders, order_items).

Populates both CUBRID and MySQL with identical data using seed=42.
Dataset size S = 10,000 rows per primary table.

Usage:
    python3 scripts/seed_canonical.py [--size S|M] [--seed 42]
"""

from __future__ import annotations

import argparse
import random
import sys
import time
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

SIZES = {
    "S": {"kv": 10_000, "orders": 10_000, "items_per_order_max": 5},
    "M": {"kv": 1_000_000, "orders": 1_000_000, "items_per_order_max": 5},
}

CUBRID_DSN = {
    "host": "localhost",
    "port": 33000,
    "database": "benchdb",
    "user": "dba",
    "password": "",
}

MYSQL_DSN = {
    "host": "127.0.0.1",
    "port": 3306,
    "database": "benchdb",
    "user": "root",
    "password": "bench",
}



# ---------------------------------------------------------------------------
# Data generators (deterministic via seed)
# ---------------------------------------------------------------------------


def generate_kv_rows(rng: random.Random, count: int):
    """Yield (id, k, v, pad) tuples."""
    for i in range(1, count + 1):
        k = f"key_{i:08d}"
        v = f"val_{i:08d}"
        pad = f"pad_{'x' * (rng.randint(50, 200))}"
        yield (i, k, v, pad)


def generate_orders(rng: random.Random, count: int):
    """Yield (user_id, total, created_at) tuples. id is auto-increment."""
    base_date = datetime(2025, 1, 1)
    max_offset = 90 * 24 * 3600  # 90 days in seconds
    for _ in range(count):
        user_id = rng.randint(1, 1000)
        total = round(rng.uniform(10.0, 999.99), 2)
        offset = rng.randint(0, max_offset)
        created_at = base_date + timedelta(seconds=offset)
        yield (user_id, total, created_at.strftime("%Y-%m-%d %H:%M:%S"))


def generate_order_items(rng: random.Random, order_count: int, max_items: int):
    """Yield (order_id, sku, qty, price) tuples."""
    for order_id in range(1, order_count + 1):
        num_items = rng.randint(1, max_items)
        used_skus: set[str] = set()
        for _ in range(num_items):
            sku = f"SKU-{rng.randint(1, 10000):06d}"
            if sku in used_skus:
                continue
            used_skus.add(sku)
            qty = rng.randint(1, 20)
            price = round(rng.uniform(1.0, 299.99), 2)
            yield (order_id, sku, qty, price)


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


def connect_cubrid():
    """Connect to CUBRID using CUBRIDdb."""
    try:
        import CUBRIDdb

        conn = CUBRIDdb.connect(
            f"CUBRID:{CUBRID_DSN['host']}:{CUBRID_DSN['port']}:{CUBRID_DSN['database']}:::",
            CUBRID_DSN["user"],
            CUBRID_DSN["password"],
        )
        return conn
    except ImportError:
        print("WARNING: CUBRIDdb not available, skipping CUBRID seeding")
        return None


def connect_mysql():
    """Connect to MySQL using PyMySQL."""
    try:
        import pymysql

        conn = pymysql.connect(
            host=MYSQL_DSN["host"],
            port=MYSQL_DSN["port"],
            database=MYSQL_DSN["database"],
            user=MYSQL_DSN["user"],
            password=MYSQL_DSN["password"],
            autocommit=False,
        )
        return conn
    except ImportError:
        print("WARNING: PyMySQL not available, skipping MySQL seeding")
        return None


def apply_schema(conn, db_type: str):
    """Apply canonical schema SQL file."""
    schema_file = f"schema/canonical_{db_type}.sql"
    with open(schema_file) as f:
        sql_content = f.read()

    cursor = conn.cursor()
    for statement in sql_content.split(";"):
        statement = statement.strip()
        if statement:
            try:
                cursor.execute(statement)
            except Exception as e:
                print(f"  Schema warning ({db_type}): {e}")
    conn.commit()
    cursor.close()


def batch_insert(conn, sql: str, rows: list, db_type: str):
    """Insert rows in batches.

    For CUBRID (no executemany), builds multi-value INSERT statements
    in batches of 100 to avoid SQL length limits while still being fast.
    For MySQL, uses executemany with batch size 1000.
    """
    cursor = conn.cursor()
    if db_type == "cubrid":
        # Parse the INSERT template to build multi-value INSERTs
        # sql looks like: INSERT INTO kv (id, k, v, pad) VALUES (?, ?, ?, ?)
        # We build: INSERT INTO kv (id, k, v, pad) VALUES (...), (...), ...
        parts = sql.split("VALUES")
        insert_prefix = parts[0] + "VALUES "
        placeholder_count = sql.count("?")
        cubrid_batch = 100  # smaller batches to avoid SQL length limits
        for i in range(0, len(rows), cubrid_batch):
            batch = rows[i : i + cubrid_batch]
            value_parts = []
            flat_params = []
            for row in batch:
                placeholders = ", ".join(["?"] * placeholder_count)
                value_parts.append(f"({placeholders})")
                flat_params.extend(row)
            multi_sql = insert_prefix + ", ".join(value_parts)
            cursor.execute(multi_sql, flat_params)
        conn.commit()
    else:
        mysql_batch = 1000
        for i in range(0, len(rows), mysql_batch):
            batch = rows[i : i + mysql_batch]
            cursor.executemany(sql, batch)
        conn.commit()
    cursor.close()


def seed_database(conn, db_type: str, size_config: dict, seed: int):
    """Seed one database with canonical data."""
    rng = random.Random(seed)

    print(f"\n{'='*60}")
    print(f"Seeding {db_type.upper()} (kv={size_config['kv']}, orders={size_config['orders']})")
    print(f"{'='*60}")

    # Apply schema
    print(f"  Applying schema...", end=" ", flush=True)
    apply_schema(conn, db_type)
    print("done")

    # Seed kv table
    print(f"  Seeding kv ({size_config['kv']} rows)...", end=" ", flush=True)
    t0 = time.time()
    kv_rows = list(generate_kv_rows(rng, size_config["kv"]))
    if db_type == "cubrid":
        batch_insert(
            conn,
            "INSERT INTO kv (id, k, v, pad) VALUES (?, ?, ?, ?)",
            kv_rows,
            db_type,
        )
    else:
        batch_insert(
            conn,
            "INSERT INTO kv (id, k, v, pad) VALUES (%s, %s, %s, %s)",
            kv_rows,
            db_type,
        )
    print(f"done ({time.time()-t0:.1f}s)")

    # Seed orders table
    print(f"  Seeding orders ({size_config['orders']} rows)...", end=" ", flush=True)
    t0 = time.time()
    order_rows = list(generate_orders(rng, size_config["orders"]))
    if db_type == "cubrid":
        batch_insert(
            conn,
            "INSERT INTO orders (user_id, total, created_at) VALUES (?, ?, ?)",
            order_rows,
            db_type,
        )
    else:
        batch_insert(
            conn,
            "INSERT INTO orders (user_id, total, created_at) VALUES (%s, %s, %s)",
            order_rows,
            db_type,
        )
    print(f"done ({time.time()-t0:.1f}s)")

    # Seed order_items table
    print(f"  Seeding order_items...", end=" ", flush=True)
    t0 = time.time()
    item_rows = list(
        generate_order_items(rng, size_config["orders"], size_config["items_per_order_max"])
    )
    if db_type == "cubrid":
        batch_insert(
            conn,
            "INSERT INTO order_items (order_id, sku, qty, price) VALUES (?, ?, ?, ?)",
            item_rows,
            db_type,
        )
    else:
        batch_insert(
            conn,
            "INSERT INTO order_items (order_id, sku, qty, price) VALUES (%s, %s, %s, %s)",
            item_rows,
            db_type,
        )
    print(f"done ({len(item_rows)} rows, {time.time()-t0:.1f}s)")

    # Verify
    cursor = conn.cursor()
    for table in ["kv", "orders", "order_items"]:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  ✓ {table}: {count} rows")
    cursor.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Seed canonical benchmark tables")
    parser.add_argument("--size", choices=["S", "M"], default="S", help="Dataset size")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument(
        "--db",
        choices=["cubrid", "mysql", "both"],
        default="both",
        help="Which database to seed",
    )
    args = parser.parse_args()

    size_config = SIZES[args.size]

    if args.db in ("cubrid", "both"):
        conn = connect_cubrid()
        if conn:
            try:
                seed_database(conn, "cubrid", size_config, args.seed)
            finally:
                conn.close()

    if args.db in ("mysql", "both"):
        conn = connect_mysql()
        if conn:
            try:
                seed_database(conn, "mysql", size_config, args.seed)
            finally:
                conn.close()

    print("\n✅ Seeding complete!")


if __name__ == "__main__":
    main()
