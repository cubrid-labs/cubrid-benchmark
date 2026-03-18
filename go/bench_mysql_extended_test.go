package bench

import "testing"

func BenchmarkMysqlConnectDisconnect(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runConnectDisconnect(b, openMysql)
	}
}

func BenchmarkMysqlPreparedStatement(b *testing.B) {
	db := openMysql(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, mysqlBenchTable)
	defer dropBenchmarkTable(b, db, mysqlBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runPreparedStatement(b, db, mysqlBenchTable)
	}
}

func BenchmarkMysqlBatchInsert(b *testing.B) {
	db := openMysql(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, mysqlBenchTable)
	defer dropBenchmarkTable(b, db, mysqlBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runBatchInsert(b, db, mysqlBenchTable)
	}
}

func BenchmarkMysqlConcurrentSelect(b *testing.B) {
	db := openMysql(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, mysqlBenchTable)
	defer dropBenchmarkTable(b, db, mysqlBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runConcurrentSelect(b, db, mysqlBenchTable)
	}
}
