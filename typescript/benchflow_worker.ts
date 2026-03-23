/**
 * benchflow external worker for TypeScript.
 *
 * Reads a benchflow WorkerInput JSON config from the file path given as
 * the first CLI argument, runs the benchmark, and writes a WorkerOutput
 * JSON to stdout.
 *
 * Supports CUBRID (cubrid-client) and MySQL (mysql2).
 *
 * Usage:
 *   npx tsx benchflow_worker.ts /tmp/benchflow_xyz.json
 */

import { readFileSync } from "node:fs"
import { performance } from "node:perf_hooks"
import { createClient, type CubridClient } from "cubrid-client"

type QueryParam = string | number | boolean | bigint | Date | Buffer | null
import mysql from "mysql2/promise"

// ---------------------------------------------------------------------------
// Types (mirrors benchflow.workers.external.protocol)
// ---------------------------------------------------------------------------

interface InputStep {
  name: string
  query: string
  params?: Record<string, unknown>
}

interface WorkerInput {
  dsn: string
  steps: InputStep[]
  concurrency: number
  duration_s: number
  warmup_s: number
  seed: number | null
  setup_queries: string[]
  teardown_queries: string[]
  worker_config: Record<string, unknown>
}

interface LatencySummary {
  min_ns: number
  max_ns: number
  mean_ns: number
  stdev_ns: number
  p50_ns: number
  p95_ns: number
  p99_ns: number
  p999_ns: number
  p9999_ns: number
}

interface TimeWindowOut {
  second: number
  ops: number
  errors: number
  p50_ns: number
  p95_ns: number
  p99_ns: number
}

interface OutputStep {
  name: string
  ops: number
  errors: number
  latency_summary: LatencySummary
  throughput_ops_s: number
  samples_ns: number[]
  time_series: TimeWindowOut[]
}

interface WorkerOutput {
  status: string
  steps: OutputStep[]
  duration_s: number
  error_message: string | null
  server_info: Record<string, unknown>
}

// ---------------------------------------------------------------------------
// DSN parsing
// ---------------------------------------------------------------------------

interface ParsedDSN {
  driver: "cubrid" | "mysql"
  host: string
  port: number
  database: string
  user: string
  password: string
}

function parseDSN(dsn: string): ParsedDSN {
  const url = new URL(dsn)
  const driver = url.protocol.replace(":", "") as "cubrid" | "mysql"
  return {
    driver,
    host: url.hostname || "localhost",
    port: parseInt(url.port || (driver === "cubrid" ? "33000" : "3306"), 10),
    database: url.pathname.replace("/", ""),
    user: url.username || (driver === "cubrid" ? "dba" : "root"),
    password: url.password || "",
  }
}

// ---------------------------------------------------------------------------
// DB abstraction
// ---------------------------------------------------------------------------

interface DBConn {
  query(sql: string, params?: unknown[]): Promise<unknown[]>
  execute(sql: string): Promise<void>
  close(): Promise<void>
  getVersion(): Promise<string>
}

async function openConnection(parsed: ParsedDSN): Promise<DBConn> {
  if (parsed.driver === "cubrid") {
    const client: CubridClient = createClient({
      host: parsed.host,
      port: parsed.port,
      database: parsed.database,
      user: parsed.user,
      password: parsed.password,
    })
    return {
      async query(sql: string, params?: unknown[]) {
        return client.query(sql, (params ?? []) as QueryParam[])
      },
      async execute(sql: string) {
        await client.query(sql)
      },
      async close() {
        await client.close()
      },
      async getVersion() {
        const rows = await client.query("SELECT version()")
        return (rows?.[0]?.["version()"] as string) ?? "unknown"
      },
    }
  } else {
    const conn = await mysql.createConnection({
      host: parsed.host,
      port: parsed.port,
      database: parsed.database,
      user: parsed.user,
      password: parsed.password,
    })
    return {
      async query(sql: string, params?: unknown[]) {
        const [rows] = await conn.query(sql, params ?? [])
        return rows as unknown[]
      },
      async execute(sql: string) {
        await conn.query(sql)
      },
      async close() {
        await conn.end()
      },
      async getVersion() {
        const [rows] = await conn.query("SELECT version() as v")
        return (rows as Array<{ v: string }>)?.[0]?.v ?? "unknown"
      },
    }
  }
}

// ---------------------------------------------------------------------------
// Parameter resolution
// ---------------------------------------------------------------------------

const RE_RANDOM_INT = /^random_int\((\d+),\s*(\d+)\)$/
const RE_RANDOM_CHOICE = /^random_choice\((.+)\)$/
const RE_PYFORMAT = /%\((\w+)\)s/g

// Simple seeded PRNG (xoshiro128)
function createRNG(seed: number): () => number {
  let s = seed | 0 || 1
  return () => {
    s ^= s << 13
    s ^= s >> 17
    s ^= s << 5
    return (s >>> 0) / 0xffffffff
  }
}

function resolveParams(
  params: Record<string, unknown> | undefined,
  rng: () => number
): Record<string, unknown> | undefined {
  if (!params) return undefined
  const resolved: Record<string, unknown> = {}
  for (const [k, v] of Object.entries(params)) {
    if (typeof v !== "string") {
      resolved[k] = v
      continue
    }
    const intMatch = RE_RANDOM_INT.exec(v)
    if (intMatch) {
      const lo = parseInt(intMatch[1], 10)
      const hi = parseInt(intMatch[2], 10)
      resolved[k] = lo + Math.floor(rng() * (hi - lo + 1))
      continue
    }
    const choiceMatch = RE_RANDOM_CHOICE.exec(v)
    if (choiceMatch) {
      const choices = choiceMatch[1].split(",").map((c) => c.trim())
      resolved[k] = choices[Math.floor(rng() * choices.length)]
      continue
    }
    resolved[k] = v
  }
  return resolved
}

function translateQuery(
  query: string,
  params: Record<string, unknown> | undefined
): { sql: string; args: unknown[] } {
  if (!params) return { sql: query, args: [] }
  const args: unknown[] = []
  const sql = query.replace(RE_PYFORMAT, (_match, name: string) => {
    args.push(params[name])
    return "?"
  })
  return { sql, args }
}

// ---------------------------------------------------------------------------
// Latency math
// ---------------------------------------------------------------------------

function percentile(sorted: number[], p: number): number {
  if (sorted.length === 0) return 0
  const idx = Math.max(0, Math.min(Math.ceil((p / 100) * sorted.length) - 1, sorted.length - 1))
  return sorted[idx]
}

function mean(arr: number[]): number {
  if (arr.length === 0) return 0
  let sum = 0
  for (const v of arr) sum += v
  return Math.round(sum / arr.length)
}

function stdev(arr: number[]): number {
  if (arr.length < 2) return 0
  const m = mean(arr)
  let sumSq = 0
  for (const v of arr) {
    const d = v - m
    sumSq += d * d
  }
  return Math.round(Math.sqrt(sumSq / arr.length))
}

// ---------------------------------------------------------------------------
// Step collector
// ---------------------------------------------------------------------------

class StepCollector {
  name: string
  latencies: number[] = []
  errors = 0
  timeBuckets: Map<number, number[]> = new Map()
  timeErrors: Map<number, number> = new Map()

  constructor(name: string) {
    this.name = name
  }

  record(latencyNs: number, second: number) {
    this.latencies.push(latencyNs)
    let bucket = this.timeBuckets.get(second)
    if (!bucket) {
      bucket = []
      this.timeBuckets.set(second, bucket)
    }
    bucket.push(latencyNs)
  }

  recordError(second: number) {
    this.errors++
    this.timeErrors.set(second, (this.timeErrors.get(second) ?? 0) + 1)
  }

  toOutputStep(durationS: number): OutputStep {
    const sorted = [...this.latencies].sort((a, b) => a - b)
    const ops = sorted.length

    if (ops === 0) {
      return {
        name: this.name,
        ops: 0,
        errors: this.errors,
        latency_summary: { min_ns: 0, max_ns: 0, mean_ns: 0, stdev_ns: 0, p50_ns: 0, p95_ns: 0, p99_ns: 0, p999_ns: 0, p9999_ns: 0 },
        throughput_ops_s: 0,
        samples_ns: [],
        time_series: [],
      }
    }

    const summary: LatencySummary = {
      min_ns: sorted[0],
      max_ns: sorted[sorted.length - 1],
      mean_ns: mean(sorted),
      stdev_ns: stdev(sorted),
      p50_ns: percentile(sorted, 50),
      p95_ns: percentile(sorted, 95),
      p99_ns: percentile(sorted, 99),
      p999_ns: percentile(sorted, 99.9),
      p9999_ns: percentile(sorted, 99.99),
    }

    // Reservoir sample
    let samples = sorted
    if (samples.length > 10000) {
      const rng = createRNG(42)
      samples = Array.from({ length: 10000 }, () => sorted[Math.floor(rng() * sorted.length)])
    }

    // Time series
    const timeSeries: TimeWindowOut[] = []
    if (this.timeBuckets.size > 0) {
      const maxSec = Math.max(...this.timeBuckets.keys())
      for (let s = 0; s <= maxSec; s++) {
        const lats = this.timeBuckets.get(s)
        const errs = this.timeErrors.get(s) ?? 0
        if (lats && lats.length > 0) {
          const sb = [...lats].sort((a, b) => a - b)
          timeSeries.push({
            second: s,
            ops: lats.length,
            errors: errs,
            p50_ns: percentile(sb, 50),
            p95_ns: percentile(sb, 95),
            p99_ns: percentile(sb, 99),
          })
        }
      }
    }

    return {
      name: this.name,
      ops,
      errors: this.errors,
      latency_summary: summary,
      throughput_ops_s: ops / durationS,
      samples_ns: samples,
      time_series: timeSeries,
    }
  }
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

async function main() {
  const configPath = process.argv[2]
  if (!configPath) {
    fatal("usage: benchflow_worker <config.json>")
    return
  }

  const raw = readFileSync(configPath, "utf-8")
  const input: WorkerInput = JSON.parse(raw)

  const parsed = parseDSN(input.dsn)
  const conn = await openConnection(parsed)

  // Server info
  const serverInfo: Record<string, unknown> = {}
  try {
    serverInfo.server_version = await conn.getVersion()
  } catch {
    // ignore
  }

  // Setup
  for (const q of input.setup_queries) {
    await conn.execute(q)
  }

  // Pre-translate queries
  const steps = input.steps.map((s) => ({
    name: s.name,
    rawQuery: s.query,
    rawParams: s.params,
  }))

  const collectors = new Map<string, StepCollector>()
  for (const s of steps) {
    collectors.set(s.name, new StepCollector(s.name))
  }

  const baseSeed = input.seed ?? Date.now()
  const rng = createRNG(baseSeed)

  // Warmup
  if (input.warmup_s > 0) {
    const warmupEnd = performance.now() + input.warmup_s * 1000
    while (performance.now() < warmupEnd) {
      for (const s of steps) {
        const resolved = resolveParams(s.rawParams, rng)
        const { sql, args } = translateQuery(s.rawQuery, resolved)
        try {
          await conn.query(sql, args)
        } catch {
          // ignore warmup errors
        }
      }
    }
  }

  // Benchmark
  // Note: TypeScript is single-threaded, so concurrency > 1 means
  // we fire off multiple async operations concurrently.
  // Each worker gets its own connection to avoid driver-level deadlocks
  // (especially with cubrid-client which doesn't support concurrent queries on one connection).
  const benchStart = performance.now()
  const durationMs = input.duration_s * 1000
  const concurrency = Math.max(1, input.concurrency)

  // Create per-worker connections (reuse the main conn for worker 0)
  const workerConns: DBConn[] = [conn]
  for (let w = 1; w < concurrency; w++) {
    workerConns.push(await openConnection(parsed))
  }

  const workerPromises: Promise<void>[] = []
  for (let w = 0; w < concurrency; w++) {
    const workerRng = createRNG(baseSeed + w * 1000)
    const wConn = workerConns[w]
    workerPromises.push(
      (async () => {
        const deadline = performance.now() + durationMs
        while (performance.now() < deadline) {
          for (const s of steps) {
            const resolved = resolveParams(s.rawParams, workerRng)
            const { sql, args } = translateQuery(s.rawQuery, resolved)
            const t0 = performance.now()
            try {
              await wConn.query(sql, args)
              const latencyNs = Math.round((performance.now() - t0) * 1_000_000)
              const sec = Math.floor((performance.now() - benchStart) / 1000)
              collectors.get(s.name)!.record(latencyNs, sec)
            } catch {
              const sec = Math.floor((performance.now() - benchStart) / 1000)
              collectors.get(s.name)!.recordError(sec)
            }
          }
        }
      })()
    )
  }

  await Promise.all(workerPromises)
  const actualDuration = (performance.now() - benchStart) / 1000

  // Teardown
  for (const q of input.teardown_queries) {
    try {
      await conn.execute(q)
    } catch {
      // best-effort
    }
  }

  // Close all connections (worker 0's conn is the main conn)
  for (const wc of workerConns) {
    try { await wc.close() } catch { /* best-effort */ }
  }

  // Output
  const outputSteps: OutputStep[] = input.steps.map((s) =>
    collectors.get(s.name)!.toOutputStep(actualDuration)
  )

  const output: WorkerOutput = {
    status: "ok",
    steps: outputSteps,
    duration_s: actualDuration,
    error_message: null,
    server_info: serverInfo,
  }

  process.stdout.write(JSON.stringify(output, null, 2) + "\n")
}

function fatal(msg: string) {
  const output: WorkerOutput = {
    status: "error",
    steps: [],
    duration_s: 0,
    error_message: msg,
    server_info: {},
  }
  process.stdout.write(JSON.stringify(output) + "\n")
  process.exit(1)
}

main().catch((err) => {
  fatal(String(err))
})
