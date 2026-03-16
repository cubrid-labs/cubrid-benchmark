package bench

import (
	"fmt"
	"testing"
)

const cubridBenchTable = "bench_driver_cubrid_go"

func BenchmarkCubridInsertSequential(b *testing.B) {
	db := openCubrid(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, cubridBenchTable)
	defer dropBenchmarkTable(b, db, cubridBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runInsertSequential(b, db, cubridBenchTable)
	}
}

func BenchmarkCubridSelectByPK(b *testing.B) {
	db := openCubrid(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, cubridBenchTable)
	defer dropBenchmarkTable(b, db, cubridBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runSelectByPK(b, db, cubridBenchTable)
	}
}

func BenchmarkCubridSelectFullScan(b *testing.B) {
	db := openCubrid(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, cubridBenchTable)
	defer dropBenchmarkTable(b, db, cubridBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runSelectFullScan(b, db, cubridBenchTable)
	}
}

func BenchmarkCubridUpdateIndexed(b *testing.B) {
	db := openCubrid(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, cubridBenchTable)
	defer dropBenchmarkTable(b, db, cubridBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runUpdateIndexed(b, db, cubridBenchTable)
	}
}

func BenchmarkCubridDeleteSequential(b *testing.B) {
	db := openCubrid(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, cubridBenchTable)
	defer dropBenchmarkTable(b, db, cubridBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runDeleteSequential(b, db, cubridBenchTable)
	}
}

func ensureBenchmarkTable(b *testing.B, db Execer, tableName string) {
	b.Helper()
	if _, err := db.Exec(fmt.Sprintf("DROP TABLE IF EXISTS %s", tableName)); err != nil {
		b.Fatalf("drop table %s: %v", tableName, err)
	}
	query := fmt.Sprintf(
		"CREATE TABLE %s (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), amount INT)",
		tableName,
	)
	if _, err := db.Exec(query); err != nil {
		b.Fatalf("create table %s: %v", tableName, err)
	}
}

func dropBenchmarkTable(b *testing.B, db Execer, tableName string) {
	b.Helper()
	if _, err := db.Exec(fmt.Sprintf("DROP TABLE IF EXISTS %s", tableName)); err != nil {
		b.Fatalf("cleanup drop table %s: %v", tableName, err)
	}
}
