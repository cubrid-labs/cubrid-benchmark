import { Bench } from "tinybench"
import { afterAll, beforeAll, test } from "vitest"
import { getMysqlConnection, type MysqlConnection, writeBenchmarkJson } from "./helpers"

const TABLE = "bench_driver_mysql_ts"
let conn: MysqlConnection

async function recreateTable(): Promise<void> {
  await conn.query(`DROP TABLE IF EXISTS ${TABLE}`)
  await conn.query(
    `CREATE TABLE ${TABLE} (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), amount INT)`
  )
}

async function clearTable(): Promise<void> {
  await conn.query(`DELETE FROM ${TABLE}`)
}

async function seedRows(prefix: string, count = 1000): Promise<void> {
  for (let i = 1; i <= count; i += 1) {
    await conn.query(`INSERT INTO ${TABLE} (name, amount) VALUES (?, ?)`, [
      `${prefix}_${String(i).padStart(5, "0")}`,
      i
    ])
  }
}

beforeAll(async () => {
  conn = await getMysqlConnection()
  await recreateTable()
})

afterAll(async () => {
  await conn.query(`DROP TABLE IF EXISTS ${TABLE}`)
  await conn.end()
})

test("mysql tier1 throughput", async () => {
  const bench = new Bench({
    iterations: 5,
    warmupIterations: 1,
    time: 0
  })

  bench.add("insert_sequential", async () => {
    await clearTable()
    await seedRows("insert", 1000)
  })

  bench.add("select_by_pk", async () => {
    await clearTable()
    await seedRows("select", 1000)
    for (let i = 1; i <= 1000; i += 1) {
      await conn.query(`SELECT id, name, amount FROM ${TABLE} WHERE id = ?`, [i])
    }
  })

  bench.add("select_full_scan", async () => {
    await clearTable()
    await seedRows("scan", 1000)
    await conn.query(`SELECT id, name, amount FROM ${TABLE}`)
  })

  bench.add("update_indexed", async () => {
    await clearTable()
    await seedRows("update", 1000)
    for (let i = 1; i <= 100; i += 1) {
      await conn.query(`UPDATE ${TABLE} SET amount = ? WHERE id = ?`, [i + 100000, i])
    }
  })

  bench.add("delete_sequential", async () => {
    await clearTable()
    await seedRows("delete", 1000)
    for (let i = 1; i <= 100; i += 1) {
      await conn.query(`DELETE FROM ${TABLE} WHERE id = ?`, [i])
    }
  })

  await bench.run()

  const results = bench.tasks.map((task) => ({
    name: task.name,
    runs: task.result?.latency.samples.length ?? 0,
    hz: task.result?.throughput.mean ?? 0,
    meanSeconds: (task.result?.latency.mean ?? 0) / 1000,
    minSeconds: (task.result?.latency.min ?? 0) / 1000,
    maxSeconds: (task.result?.latency.max ?? 0) / 1000,
    variance: task.result?.latency.variance ?? 0
  }))

  await writeBenchmarkJson("typescript_tier1_mysql.json", {
    database: "mysql",
    tier: 1,
    rounds: 5,
    warmupRounds: 1,
    benchmarks: results
  })
})
