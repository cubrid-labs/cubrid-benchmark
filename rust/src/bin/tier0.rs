use cubrid_benchmark_rust::{connect, drop_table, first_i64, table_name, BenchmarkResult};
use cubrid_protocol::value::Value;

fn main() -> BenchmarkResult<()> {
    let table = table_name("tier0_cubrid");
    let mut client = connect()?;

    client.execute(&format!("DROP TABLE IF EXISTS {table}"), &[])?;
    client.execute(
        &format!(
            "CREATE TABLE {table} (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), amount INT)"
        ),
        &[],
    )?;

    let inserted = client.execute(
        &format!("INSERT INTO {table} (name, amount) VALUES (?, ?)"),
        &[Value::from("alice"), Value::Int(30)],
    )?;
    assert_eq!(inserted, 1, "insert should affect 1 row");

    let row = client.query(
        &format!("SELECT name, amount FROM {table} WHERE id = ?"),
        &[Value::Int(1)],
    )?;
    assert_eq!(row.len(), 1, "select should return 1 row");
    assert_eq!(row.rows[0][0].as_str(), Some("alice"));
    assert_eq!(first_i64(&row.rows[0][1]), Some(30));

    let updated = client.execute(
        &format!("UPDATE {table} SET amount = ? WHERE id = ?"),
        &[Value::Int(31), Value::Int(1)],
    )?;
    assert_eq!(updated, 1, "update should affect 1 row");

    let updated_row = client.query(
        &format!("SELECT amount FROM {table} WHERE id = ?"),
        &[Value::Int(1)],
    )?;
    assert_eq!(updated_row.len(), 1, "updated row should exist");
    assert_eq!(first_i64(&updated_row.rows[0][0]), Some(31));

    let deleted = client.execute(
        &format!("DELETE FROM {table} WHERE id = ?"),
        &[Value::Int(1)],
    )?;
    assert_eq!(deleted, 1, "delete should affect 1 row");

    let count = client.query(&format!("SELECT COUNT(*) FROM {table}"), &[])?;
    assert_eq!(count.len(), 1, "count should return 1 row");
    assert_eq!(first_i64(&count.rows[0][0]), Some(0));

    drop_table(&mut client, &table)?;
    client.close()?;

    println!("Rust Tier 0 benchmark passed");
    Ok(())
}
