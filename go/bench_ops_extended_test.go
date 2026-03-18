package bench

import (
	"database/sql"
	"fmt"
	"sync"
	"testing"
)

func runConnectDisconnect(b *testing.B, open func(testing.TB) *sql.DB) {
	b.Helper()
	for i := 0; i < 100; i++ {
		db := open(b)
		db.Close()
	}
}

func runPreparedStatement(b *testing.B, db *sql.DB, tableName string) {
	b.Helper()
	seedRows(b, db, tableName, "prepared")

	stmt, err := db.Prepare(fmt.Sprintf("SELECT id, name, amount FROM %s WHERE amount = ?", tableName))
	if err != nil {
		b.Fatalf("prepare statement: %v", err)
	}
	defer stmt.Close()

	for i := 1; i <= 1000; i++ {
		rows, queryErr := stmt.Query(i)
		if queryErr != nil {
			b.Fatalf("prepared query row %d: %v", i, queryErr)
		}
		for rows.Next() {
			var id int
			var name string
			var amount int
			if scanErr := rows.Scan(&id, &name, &amount); scanErr != nil {
				rows.Close()
				b.Fatalf("prepared scan row %d: %v", i, scanErr)
			}
		}
		if rowsErr := rows.Err(); rowsErr != nil {
			rows.Close()
			b.Fatalf("prepared rows error row %d: %v", i, rowsErr)
		}
		rows.Close()
	}
}

func runBatchInsert(b *testing.B, db *sql.DB, tableName string) {
	b.Helper()
	clearTable(b, db, tableName)

	tx, err := db.Begin()
	if err != nil {
		b.Fatalf("begin batch insert transaction: %v", err)
	}
	stmt, err := tx.Prepare(fmt.Sprintf("INSERT INTO %s (name, amount) VALUES (?, ?)", tableName))
	if err != nil {
		tx.Rollback()
		b.Fatalf("prepare batch insert: %v", err)
	}
	defer stmt.Close()

	for i := 1; i <= 1000; i++ {
		if _, err = stmt.Exec(fmt.Sprintf("batch_%05d", i), i); err != nil {
			tx.Rollback()
			b.Fatalf("batch insert row %d: %v", i, err)
		}
	}
	if err = tx.Commit(); err != nil {
		b.Fatalf("commit batch insert transaction: %v", err)
	}
}

func runConcurrentSelect(b *testing.B, db *sql.DB, tableName string) {
	b.Helper()
	seedRows(b, db, tableName, "concurrent")

	type rangePair struct {
		start int
		end   int
	}

	ranges := []rangePair{{start: 1, end: 250}, {start: 251, end: 500}, {start: 501, end: 750}, {start: 751, end: 1000}}
	var wg sync.WaitGroup
	errCh := make(chan error, len(ranges))

	for _, current := range ranges {
		current := current
		wg.Add(1)
		go func() {
			defer wg.Done()
			stmt, err := db.Prepare(fmt.Sprintf("SELECT id, name, amount FROM %s WHERE amount = ?", tableName))
			if err != nil {
				errCh <- fmt.Errorf("prepare concurrent select: %w", err)
				return
			}
			defer stmt.Close()

			for value := current.start; value <= current.end; value++ {
				rows, queryErr := stmt.Query(value)
				if queryErr != nil {
					errCh <- fmt.Errorf("concurrent query %d: %w", value, queryErr)
					return
				}
				for rows.Next() {
					var id int
					var name string
					var amount int
					if scanErr := rows.Scan(&id, &name, &amount); scanErr != nil {
						rows.Close()
						errCh <- fmt.Errorf("concurrent scan %d: %w", value, scanErr)
						return
					}
				}
				if rowsErr := rows.Err(); rowsErr != nil {
					rows.Close()
					errCh <- fmt.Errorf("concurrent rows error %d: %w", value, rowsErr)
					return
				}
				rows.Close()
			}
		}()
	}

	wg.Wait()
	close(errCh)
	for err := range errCh {
		if err != nil {
			b.Fatalf("concurrent select: %v", err)
		}
	}
}
