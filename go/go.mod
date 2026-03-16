module github.com/cubrid-labs/cubrid-benchmark/go

go 1.22

require (
	github.com/cubrid-labs/cubrid-go v0.1.0
	github.com/go-sql-driver/mysql v1.8.1
)

require filippo.io/edwards25519 v1.1.0 // indirect

replace github.com/cubrid-labs/cubrid-go => /data/GitHub/cubrid-go
