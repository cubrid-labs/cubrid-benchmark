from __future__ import annotations


def test_cubrid_tier0_smoke(cubrid_conn) -> None:
    cursor = cubrid_conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS bench_tier0_cubrid")
    cursor.execute(
        "CREATE TABLE bench_tier0_cubrid ("
        "id INT AUTO_INCREMENT PRIMARY KEY, "
        "name VARCHAR(100), "
        "age INT"
        ")"
    )

    cursor.execute("INSERT INTO bench_tier0_cubrid (name, age) VALUES (?, ?)", ("alice", 30))
    cubrid_conn.commit()

    cursor.execute("SELECT name, age FROM bench_tier0_cubrid WHERE id = ?", (1,))
    row = cursor.fetchone()
    assert row is not None
    assert row[0] == "alice"
    assert int(row[1]) == 30

    cursor.execute("UPDATE bench_tier0_cubrid SET age = ? WHERE id = ?", (31, 1))
    cubrid_conn.commit()

    cursor.execute("SELECT age FROM bench_tier0_cubrid WHERE id = ?", (1,))
    updated = cursor.fetchone()
    assert updated is not None
    assert int(updated[0]) == 31

    cursor.execute("DELETE FROM bench_tier0_cubrid WHERE id = ?", (1,))
    cubrid_conn.commit()

    cursor.execute("SELECT COUNT(*) FROM bench_tier0_cubrid")
    count_row = cursor.fetchone()
    assert count_row is not None
    assert int(count_row[0]) == 0

    cursor.execute("DROP TABLE IF EXISTS bench_tier0_cubrid")
    cubrid_conn.commit()
    cursor.close()
