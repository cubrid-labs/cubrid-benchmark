import { defineConfig } from "vitest/config"

export default defineConfig({
  test: {
    testTimeout: 300000,
    include: ["bench_*.test.ts"]
  }
})
