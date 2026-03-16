package bench

import (
	"database/sql"
	"fmt"
	"testing"
)

type Execer interface {
	Exec(query string, args ...any) (sql.Result, error)
}

func runInsertSequential(b *testing.B, db *sql.DB, tableName string) {
	b.Helper()
	clearTable(b, db, tableName)

	tx, err := db.Begin()
	if err != nil {
		b.Fatalf("begin insert transaction: %v", err)
	}
	for i := 1; i <= 10000; i++ {
		if _, err = tx.Exec(
			fmt.Sprintf("INSERT INTO %s (name, amount) VALUES (?, ?)", tableName),
			fmt.Sprintf("insert_%05d", i),
			i,
		); err != nil {
			tx.Rollback()
			b.Fatalf("insert row %d: %v", i, err)
		}
	}
	if err = tx.Commit(); err != nil {
		b.Fatalf("commit insert transaction: %v", err)
	}
}

func runSelectByPK(b *testing.B, db *sql.DB, tableName string) {
	b.Helper()
	seedRows(b, db, tableName, "select")

	for i := 1; i <= 10000; i++ {
		rows, err := db.Query(
			fmt.Sprintf("SELECT id, name, amount FROM %s WHERE id = ?", tableName),
			i,
		)
		if err != nil {
			b.Fatalf("select by pk row %d: %v", i, err)
		}
		for rows.Next() {
			var id int
			var name string
			var amount int
			if scanErr := rows.Scan(&id, &name, &amount); scanErr != nil {
				rows.Close()
				b.Fatalf("scan select by pk row %d: %v", i, scanErr)
			}
		}
		if err = rows.Err(); err != nil {
			rows.Close()
			b.Fatalf("rows error select by pk row %d: %v", i, err)
		}
		rows.Close()
	}
}

func runSelectFullScan(b *testing.B, db *sql.DB, tableName string) {
	b.Helper()
	seedRows(b, db, tableName, "scan")

	rows, err := db.Query(fmt.Sprintf("SELECT id, name, amount FROM %s", tableName))
	if err != nil {
		b.Fatalf("full scan query: %v", err)
	}
	defer rows.Close()

	for rows.Next() {
		var id int
		var name string
		var amount int
		if scanErr := rows.Scan(&id, &name, &amount); scanErr != nil {
			b.Fatalf("scan full scan row: %v", scanErr)
		}
	}
	if err = rows.Err(); err != nil {
		b.Fatalf("rows error full scan: %v", err)
	}
}

func runUpdateIndexed(b *testing.B, db *sql.DB, tableName string) {
	b.Helper()
	seedRows(b, db, tableName, "update")

	tx, err := db.Begin()
	if err != nil {
		b.Fatalf("begin update transaction: %v", err)
	}
	for i := 1; i <= 1000; i++ {
		if _, err = tx.Exec(
			fmt.Sprintf("UPDATE %s SET amount = ? WHERE id = ?", tableName),
			i+100000,
			i,
		); err != nil {
			tx.Rollback()
			b.Fatalf("update row %d: %v", i, err)
		}
	}
	if err = tx.Commit(); err != nil {
		b.Fatalf("commit update transaction: %v", err)
	}
}

func runDeleteSequential(b *testing.B, db *sql.DB, tableName string) {
	b.Helper()
	seedRows(b, db, tableName, "delete")

	tx, err := db.Begin()
	if err != nil {
		b.Fatalf("begin delete transaction: %v", err)
	}
	for i := 1; i <= 1000; i++ {
		if _, err = tx.Exec(fmt.Sprintf("DELETE FROM %s WHERE id = ?", tableName), i); err != nil {
			tx.Rollback()
			b.Fatalf("delete row %d: %v", i, err)
		}
	}
	if err = tx.Commit(); err != nil {
		b.Fatalf("commit delete transaction: %v", err)
	}
}

func seedRows(b *testing.B, db *sql.DB, tableName string, prefix string) {
	b.Helper()
	clearTable(b, db, tableName)

	tx, err := db.Begin()
	if err != nil {
		b.Fatalf("begin seed transaction: %v", err)
	}
	for i := 1; i <= 10000; i++ {
		if _, err = tx.Exec(
			fmt.Sprintf("INSERT INTO %s (name, amount) VALUES (?, ?)", tableName),
			fmt.Sprintf("%s_%05d", prefix, i),
			i,
		); err != nil {
			tx.Rollback()
			b.Fatalf("seed row %d: %v", i, err)
		}
	}
	if err = tx.Commit(); err != nil {
		b.Fatalf("commit seed transaction: %v", err)
	}
}

func clearTable(b *testing.B, db *sql.DB, tableName string) {
	b.Helper()
	if _, err := db.Exec(fmt.Sprintf("DELETE FROM %s", tableName)); err != nil {
		b.Fatalf("clear table %s: %v", tableName, err)
	}
}
