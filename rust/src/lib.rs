use cubrid_client::Client;
use cubrid_protocol::value::Value;

pub const DEFAULT_DSN: &str = "cubrid://dba@localhost:33000/benchdb";

pub type BenchmarkResult<T> = Result<T, Box<dyn std::error::Error>>;

pub fn test_dsn() -> String {
    std::env::var("CUBRID_TEST_URL").unwrap_or_else(|_| DEFAULT_DSN.to_string())
}

pub fn connect() -> BenchmarkResult<Client> {
    Ok(Client::connect(&test_dsn())?)
}

pub fn table_name(suffix: &str) -> String {
    format!("bench_rust_{suffix}")
}

pub fn recreate_table(client: &mut Client, table: &str) -> BenchmarkResult<()> {
    client.execute(&format!("DROP TABLE IF EXISTS {table}"), &[])?;
    client.execute(
        &format!(
            "CREATE TABLE {table} (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), amount INT)"
        ),
        &[],
    )?;
    Ok(())
}

pub fn drop_table(client: &mut Client, table: &str) -> BenchmarkResult<()> {
    client.execute(&format!("DROP TABLE IF EXISTS {table}"), &[])?;
    Ok(())
}

pub fn clear_table(client: &mut Client, table: &str) -> BenchmarkResult<()> {
    client.execute(&format!("DELETE FROM {table}"), &[])?;
    Ok(())
}

pub fn insert_rows(
    client: &mut Client,
    table: &str,
    prefix: &str,
    count: i32,
) -> BenchmarkResult<()> {
    clear_table(client, table)?;
    for i in 1..=count {
        client.execute(
            &format!("INSERT INTO {table} (id, name, amount) VALUES (?, ?, ?)"),
            &[
                Value::Int(i),
                Value::from(format!("{prefix}_{i:05}")),
                Value::Int(i),
            ],
        )?;
    }
    Ok(())
}

pub fn select_by_pk(client: &mut Client, table: &str, count: i32) -> BenchmarkResult<usize> {
    let mut rows_read = 0;
    for i in 1..=count {
        let result = client.query(
            &format!("SELECT id, name, amount FROM {table} WHERE id = ?"),
            &[Value::Int(i)],
        )?;
        rows_read += result.len();
    }
    Ok(rows_read)
}

pub fn select_full_scan(client: &mut Client, table: &str) -> BenchmarkResult<usize> {
    let result = client.query(&format!("SELECT id, name, amount FROM {table}"), &[])?;
    Ok(result.len())
}

pub fn update_indexed(client: &mut Client, table: &str, count: i32) -> BenchmarkResult<u64> {
    let mut affected = 0;
    for i in 1..=count {
        affected += client.execute(
            &format!("UPDATE {table} SET amount = ? WHERE id = ?"),
            &[Value::Int(i + 100_000), Value::Int(i)],
        )?;
    }
    Ok(affected)
}

pub fn delete_sequential(client: &mut Client, table: &str, count: i32) -> BenchmarkResult<u64> {
    let mut affected = 0;
    for i in 1..=count {
        affected += client.execute(
            &format!("DELETE FROM {table} WHERE id = ?"),
            &[Value::Int(i)],
        )?;
    }
    Ok(affected)
}

pub fn first_i64(value: &Value) -> Option<i64> {
    match value {
        Value::Short(v) => Some((*v).into()),
        Value::Int(v) => Some((*v).into()),
        Value::Long(v) => Some(*v),
        _ => None,
    }
}
