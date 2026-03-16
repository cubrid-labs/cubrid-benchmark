package bench

import "testing"

const mysqlBenchTable = "bench_driver_mysql_go"

func BenchmarkMysqlInsertSequential(b *testing.B) {
	db := openMysql(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, mysqlBenchTable)
	defer dropBenchmarkTable(b, db, mysqlBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runInsertSequential(b, db, mysqlBenchTable)
	}
}

func BenchmarkMysqlSelectByPK(b *testing.B) {
	db := openMysql(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, mysqlBenchTable)
	defer dropBenchmarkTable(b, db, mysqlBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runSelectByPK(b, db, mysqlBenchTable)
	}
}

func BenchmarkMysqlSelectFullScan(b *testing.B) {
	db := openMysql(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, mysqlBenchTable)
	defer dropBenchmarkTable(b, db, mysqlBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runSelectFullScan(b, db, mysqlBenchTable)
	}
}

func BenchmarkMysqlUpdateIndexed(b *testing.B) {
	db := openMysql(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, mysqlBenchTable)
	defer dropBenchmarkTable(b, db, mysqlBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runUpdateIndexed(b, db, mysqlBenchTable)
	}
}

func BenchmarkMysqlDeleteSequential(b *testing.B) {
	db := openMysql(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, mysqlBenchTable)
	defer dropBenchmarkTable(b, db, mysqlBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runDeleteSequential(b, db, mysqlBenchTable)
	}
}
