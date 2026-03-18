package bench

import "testing"

func BenchmarkCubridConnectDisconnect(b *testing.B) {
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runConnectDisconnect(b, openCubrid)
	}
}

func BenchmarkCubridPreparedStatement(b *testing.B) {
	db := openCubrid(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, cubridBenchTable)
	defer dropBenchmarkTable(b, db, cubridBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runPreparedStatement(b, db, cubridBenchTable)
	}
}

func BenchmarkCubridBatchInsert(b *testing.B) {
	db := openCubrid(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, cubridBenchTable)
	defer dropBenchmarkTable(b, db, cubridBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runBatchInsert(b, db, cubridBenchTable)
	}
}

func BenchmarkCubridConcurrentSelect(b *testing.B) {
	db := openCubrid(b)
	defer db.Close()
	ensureBenchmarkTable(b, db, cubridBenchTable)
	defer dropBenchmarkTable(b, db, cubridBenchTable)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		runConcurrentSelect(b, db, cubridBenchTable)
	}
}
