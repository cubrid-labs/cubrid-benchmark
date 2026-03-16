package bench

import "testing"

func TestMysqlTier0Smoke(t *testing.T) {
	db := openMysql(t)
	defer db.Close()

	if _, err := db.Exec("DROP TABLE IF EXISTS bench_tier0_mysql_go"); err != nil {
		t.Fatalf("drop table: %v", err)
	}

	_, err := db.Exec(
		"CREATE TABLE bench_tier0_mysql_go (" +
			"id INT AUTO_INCREMENT PRIMARY KEY, " +
			"name VARCHAR(100), " +
			"age INT" +
			")",
	)
	if err != nil {
		t.Fatalf("create table: %v", err)
	}

	defer func() {
		if _, cleanupErr := db.Exec("DROP TABLE IF EXISTS bench_tier0_mysql_go"); cleanupErr != nil {
			t.Fatalf("cleanup drop table: %v", cleanupErr)
		}
	}()

	if _, err = db.Exec("INSERT INTO bench_tier0_mysql_go (name, age) VALUES (?, ?)", "alice", 30); err != nil {
		t.Fatalf("insert: %v", err)
	}

	var name string
	var age int
	if err = db.QueryRow("SELECT name, age FROM bench_tier0_mysql_go WHERE id = ?", 1).Scan(&name, &age); err != nil {
		t.Fatalf("select row: %v", err)
	}
	if name != "alice" {
		t.Fatalf("unexpected name: %s", name)
	}
	if age != 30 {
		t.Fatalf("unexpected age: %d", age)
	}

	if _, err = db.Exec("UPDATE bench_tier0_mysql_go SET age = ? WHERE id = ?", 31, 1); err != nil {
		t.Fatalf("update: %v", err)
	}

	if err = db.QueryRow("SELECT age FROM bench_tier0_mysql_go WHERE id = ?", 1).Scan(&age); err != nil {
		t.Fatalf("select updated row: %v", err)
	}
	if age != 31 {
		t.Fatalf("unexpected updated age: %d", age)
	}

	if _, err = db.Exec("DELETE FROM bench_tier0_mysql_go WHERE id = ?", 1); err != nil {
		t.Fatalf("delete: %v", err)
	}

	var count int
	if err = db.QueryRow("SELECT COUNT(*) FROM bench_tier0_mysql_go").Scan(&count); err != nil {
		t.Fatalf("count rows: %v", err)
	}
	if count != 0 {
		t.Fatalf("expected count 0, got %d", count)
	}
}
