import { mkdir, writeFile } from "node:fs/promises"
import path from "node:path"
import { fileURLToPath } from "node:url"
import { createClient, type CubridClient } from "cubrid-client"
import mysql from "mysql2/promise"

type QueryParam = string | number | boolean | bigint | Date | Buffer | null
type QueryResultRow = Record<string, unknown>

export type CubridConnection = CubridClient

export type MysqlConnection = mysql.Connection

const __dirname = path.dirname(fileURLToPath(import.meta.url))

function envInt(name: string, fallback: string): number {
  const parsed = Number.parseInt(process.env[name] ?? fallback, 10)
  return Number.isNaN(parsed) ? Number.parseInt(fallback, 10) : parsed
}

export async function getCubridConnection(): Promise<CubridConnection> {
  return createClient({
    host: process.env.CUBRID_HOST ?? "localhost",
    port: envInt("CUBRID_PORT", "33000"),
    database: process.env.CUBRID_DB ?? "benchdb",
    user: "dba",
    password: ""
  })
}

export async function getMysqlConnection(): Promise<MysqlConnection> {
  return mysql.createConnection({
    host: process.env.MYSQL_HOST ?? "localhost",
    port: envInt("MYSQL_PORT", "3306"),
    database: process.env.MYSQL_DB ?? "benchdb",
    user: process.env.MYSQL_USER ?? "root",
    password: process.env.MYSQL_PASSWORD ?? "bench"
  })
}

export async function cubridQuery(
  conn: CubridConnection,
  sql: string,
  params: QueryParam[] = []
): Promise<QueryResultRow[]> {
  return conn.query(sql, params)
}

export async function cubridClose(conn: CubridConnection): Promise<void> {
  await conn.close()
}

export async function ensureResultsDir(): Promise<void> {
  await mkdir(path.resolve(__dirname, "../results"), { recursive: true })
}

export async function writeBenchmarkJson(filename: string, payload: unknown): Promise<void> {
  await ensureResultsDir()
  const target = path.resolve(__dirname, "../results", filename)
  await writeFile(target, JSON.stringify(payload, null, 2), "utf8")
}
