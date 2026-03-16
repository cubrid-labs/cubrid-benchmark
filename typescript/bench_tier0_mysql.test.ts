import { afterAll, test } from "vitest"
import { getMysqlConnection, type MysqlConnection } from "./helpers"

let conn: MysqlConnection | null = null

afterAll(async () => {
  if (conn) {
    await conn.end()
  }
})

test("mysql tier0 smoke", async () => {
  conn = await getMysqlConnection()

  await conn.query("DROP TABLE IF EXISTS bench_tier0_mysql_ts")
  await conn.query(
    "CREATE TABLE bench_tier0_mysql_ts (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), age INT)"
  )

  await conn.query("INSERT INTO bench_tier0_mysql_ts (name, age) VALUES (?, ?)", ["alice", 30])

  const [selectRows] = await conn.query("SELECT name, age FROM bench_tier0_mysql_ts WHERE id = ?", [1])
  const row = (selectRows as Array<{ name: string; age: number }>)[0]
  expect(row.name).toBe("alice")
  expect(Number(row.age)).toBe(30)

  await conn.query("UPDATE bench_tier0_mysql_ts SET age = ? WHERE id = ?", [31, 1])

  const [updatedRows] = await conn.query("SELECT age FROM bench_tier0_mysql_ts WHERE id = ?", [1])
  const updatedRow = (updatedRows as Array<{ age: number }>)[0]
  expect(Number(updatedRow.age)).toBe(31)

  await conn.query("DELETE FROM bench_tier0_mysql_ts WHERE id = ?", [1])

  const [countRows] = await conn.query("SELECT COUNT(*) AS count FROM bench_tier0_mysql_ts")
  const countRow = (countRows as Array<{ count: number }>)[0]
  expect(Number(countRow.count)).toBe(0)

  await conn.query("DROP TABLE IF EXISTS bench_tier0_mysql_ts")
})
