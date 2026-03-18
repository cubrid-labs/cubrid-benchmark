import { Bench } from "tinybench"
import { afterAll, beforeAll, test } from "vitest"
import { getMysqlConnection, type MysqlConnection, writeBenchmarkJson } from "./helpers"

const TABLE = "bench_driver_mysql_ts_extended"
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
  await clearTable()
  for (let i = 1; i <= count; i += 1) {
    await conn.query(`INSERT INTO ${TABLE} (name, amount) VALUES (?, ?)`, [
      `${prefix}_${String(i).padStart(5, "0")}`,
      i
    ])
  }
}

async function runConnectDisconnect(): Promise<void> {
  for (let i = 0; i < 100; i += 1) {
    const workerConn = await getMysqlConnection()
    await workerConn.query("SELECT 1")
    await workerConn.end()
  }
}

async function runPreparedStatement(): Promise<void> {
  await seedRows("prepared", 1000)
  for (let i = 1; i <= 1000; i += 1) {
    await conn.query(`SELECT id, name, amount FROM ${TABLE} WHERE amount = ?`, [i])
  }
}

async function runBatchInsert(): Promise<void> {
  await clearTable()
  const placeholders = Array.from({ length: 1000 }, () => "(?, ?)").join(", ")
  const params: Array<number | string> = []
  for (let i = 1; i <= 1000; i += 1) {
    params.push(`batch_${String(i).padStart(5, "0")}`)
    params.push(i)
  }
  await conn.query(`INSERT INTO ${TABLE} (name, amount) VALUES ${placeholders}`, params)
}

async function runConcurrentSelect(): Promise<void> {
  await seedRows("concurrent", 1000)

  const ranges = [
    [1, 250],
    [251, 500],
    [501, 750],
    [751, 1000]
  ]

  await Promise.all(
    ranges.map(async ([start, end]) => {
      const workerConn = await getMysqlConnection()
      try {
        for (let value = start; value <= end; value += 1) {
          await workerConn.query(`SELECT id, name, amount FROM ${TABLE} WHERE amount = ?`, [value])
        }
      } finally {
        await workerConn.end()
      }
    })
  )
}

beforeAll(async () => {
  conn = await getMysqlConnection()
  await recreateTable()
})

afterAll(async () => {
  await conn.query(`DROP TABLE IF EXISTS ${TABLE}`)
  await conn.end()
})

test("mysql tier1 extended throughput", async () => {
  const bench = new Bench({
    iterations: 3,
    warmupIterations: 1,
    time: 0
  })

  bench.add("connect_disconnect", runConnectDisconnect)
  bench.add("prepared_statement", runPreparedStatement)
  bench.add("batch_insert", runBatchInsert)
  bench.add("concurrent_select", runConcurrentSelect)

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

  await writeBenchmarkJson("typescript_tier1_extended_mysql.json", {
    database: "mysql",
    tier: 1,
    rounds: 3,
    warmupRounds: 1,
    benchmarks: results
  })
})
