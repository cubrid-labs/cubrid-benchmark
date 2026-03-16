import { Bench } from "tinybench"
import { beforeAll, afterAll, test } from "vitest"
import {
  cubridClose,
  cubridQuery,
  getCubridConnection,
  type CubridConnection,
  writeBenchmarkJson
} from "./helpers"

const TABLE = "bench_driver_cubrid_ts"
let conn: CubridConnection

async function recreateTable(): Promise<void> {
  await cubridQuery(conn, `DROP TABLE IF EXISTS ${TABLE}`)
  await cubridQuery(
    conn,
    `CREATE TABLE ${TABLE} (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), amount INT)`
  )
}

async function clearTable(): Promise<void> {
  await cubridQuery(conn, `DELETE FROM ${TABLE}`)
}

async function seedRows(prefix: string, count = 100): Promise<void> {
  for (let i = 1; i <= count; i += 1) {
    await cubridQuery(conn, `INSERT INTO ${TABLE} (name, amount) VALUES (?, ?)`, [
      `${prefix}_${String(i).padStart(5, "0")}`,
      i
    ])
  }
}

beforeAll(async () => {
  conn = await getCubridConnection()
  await recreateTable()
})

afterAll(async () => {
  await cubridQuery(conn, `DROP TABLE IF EXISTS ${TABLE}`)
  await cubridClose(conn)
})

test("cubrid tier1 throughput", async () => {
  const bench = new Bench({
    iterations: 3,
    warmupIterations: 1,
    time: 0
  })

  bench.add("insert_sequential", async () => {
    await clearTable()
    await seedRows("insert", 100)
  })

  bench.add("select_by_pk", async () => {
    await clearTable()
    await seedRows("select", 100)
    for (let i = 1; i <= 100; i += 1) {
      await cubridQuery(conn, `SELECT id, name, amount FROM ${TABLE} WHERE id = ?`, [i])
    }
  })

  bench.add("select_full_scan", async () => {
    await clearTable()
    await seedRows("scan", 100)
    await cubridQuery(conn, `SELECT id, name, amount FROM ${TABLE}`)
  })

  bench.add("update_indexed", async () => {
    await clearTable()
    await seedRows("update", 100)
    for (let i = 1; i <= 100; i += 1) {
      await cubridQuery(conn, `UPDATE ${TABLE} SET amount = ? WHERE id = ?`, [i + 100000, i])
    }
  })

  bench.add("delete_sequential", async () => {
    await clearTable()
    await seedRows("delete", 100)
    for (let i = 1; i <= 100; i += 1) {
      await cubridQuery(conn, `DELETE FROM ${TABLE} WHERE id = ?`, [i])
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

  await writeBenchmarkJson("typescript_tier1_cubrid.json", {
    database: "cubrid",
    tier: 1,
    rounds: 3,
    warmupRounds: 1,
    benchmarks: results
  })
})
