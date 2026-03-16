import { afterAll, expect, test } from "vitest"
import {
  cubridClose,
  cubridQuery,
  getCubridConnection,
  type CubridConnection
} from "./helpers"

let conn: CubridConnection | null = null

afterAll(async () => {
  if (conn) {
    await cubridClose(conn)
  }
})

test("cubrid tier0 smoke", async () => {
  conn = await getCubridConnection()

  await cubridQuery(conn, "DROP TABLE IF EXISTS bench_tier0_cubrid_ts")
  await cubridQuery(
    conn,
    "CREATE TABLE bench_tier0_cubrid_ts (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), age INT)"
  )

  await cubridQuery(conn, "INSERT INTO bench_tier0_cubrid_ts (name, age) VALUES (?, ?)", ["alice", 30])

  const selectRows = (await cubridQuery(
    conn,
    "SELECT name, age FROM bench_tier0_cubrid_ts WHERE id = ?",
    [1]
  )) as Array<{ name: string; age: number }>
  expect(selectRows[0].name).toBe("alice")
  expect(Number(selectRows[0].age)).toBe(30)

  await cubridQuery(conn, "UPDATE bench_tier0_cubrid_ts SET age = ? WHERE id = ?", [31, 1])

  const updatedRows = (await cubridQuery(
    conn,
    "SELECT age FROM bench_tier0_cubrid_ts WHERE id = ?",
    [1]
  )) as Array<{ age: number }>
  expect(Number(updatedRows[0].age)).toBe(31)

  await cubridQuery(conn, "DELETE FROM bench_tier0_cubrid_ts WHERE id = ?", [1])

  const countRows = (await cubridQuery(
    conn,
    "SELECT COUNT(*) AS cnt FROM bench_tier0_cubrid_ts"
  )) as Array<{ cnt: number }>
  expect(Number(countRows[0].cnt)).toBe(0)

  await cubridQuery(conn, "DROP TABLE IF EXISTS bench_tier0_cubrid_ts")
})
