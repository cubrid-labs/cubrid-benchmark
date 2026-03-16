import { defineConfig } from "vitest/config"

export default defineConfig({
  test: {
    testTimeout: 900000,
    include: ["bench_*.test.ts"]
  }
})
