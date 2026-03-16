from __future__ import annotations


def test_mysql_tier0_smoke(mysql_conn) -> None:
    cursor = mysql_conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS bench_tier0_mysql")
    cursor.execute(
        "CREATE TABLE bench_tier0_mysql ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "name VARCHAR(100), "
        "age INT"
        ")"
    )

    cursor.execute("INSERT INTO bench_tier0_mysql (name, age) VALUES (%s, %s)", ("alice", 30))
    mysql_conn.commit()

    cursor.execute("SELECT name, age FROM bench_tier0_mysql WHERE id = %s", (1,))
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "alice"
    assert int(row[1]) == 30

    cursor.execute("UPDATE bench_tier0_mysql SET age = %s WHERE id = %s", (31, 1))
    mysql_conn.commit()

    cursor.execute("SELECT age FROM bench_tier0_mysql WHERE id = %s", (1,))
    updated = cursor.fetchone()
    assert updated is not None
    assert int(updated[0]) == 31

    cursor.execute("DELETE FROM bench_tier0_mysql WHERE id = %s", (1,))
    mysql_conn.commit()

    cursor.execute("SELECT COUNT(*) FROM bench_tier0_mysql")
    count_row = cursor.fetchone()
    assert count_row is not None
    assert int(count_row[0]) == 0

    cursor.execute("DROP TABLE IF EXISTS bench_tier0_mysql")
    mysql_conn.commit()
    cursor.close()
