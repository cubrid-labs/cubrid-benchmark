package bench

import (
	"database/sql"
	"fmt"
	"os"
	"testing"

	_ "github.com/cubrid-labs/cubrid-go"
	_ "github.com/go-sql-driver/mysql"
)

func envOrDefault(key string, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getCubridDSN() string {
	host := envOrDefault("CUBRID_HOST", "localhost")
	port := envOrDefault("CUBRID_PORT", "33000")
	database := envOrDefault("CUBRID_DB", "benchdb")
	return fmt.Sprintf("CUBRID:%s:%s:%s:::", host, port, database)
}

func getMysqlDSN() string {
	host := envOrDefault("MYSQL_HOST", "localhost")
	port := envOrDefault("MYSQL_PORT", "3306")
	database := envOrDefault("MYSQL_DB", "benchdb")
	return fmt.Sprintf("root:bench@tcp(%s:%s)/%s", host, port, database)
}

func openCubrid(t testing.TB) *sql.DB {
	t.Helper()
	db, err := sql.Open("cubrid", getCubridDSN())
	if err != nil {
		t.Fatalf("open cubrid: %v", err)
	}
	if err = db.Ping(); err != nil {
		db.Close()
		t.Fatalf("ping cubrid: %v", err)
	}
	return db
}

func openMysql(t testing.TB) *sql.DB {
	t.Helper()
	db, err := sql.Open("mysql", getMysqlDSN())
	if err != nil {
		t.Fatalf("open mysql: %v", err)
	}
	if err = db.Ping(); err != nil {
		db.Close()
		t.Fatalf("ping mysql: %v", err)
	}
	return db
}
