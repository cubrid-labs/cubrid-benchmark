import { defineConfig } from "vitest/config"

export default defineConfig({
  test: {
    testTimeout: 900000,
    include: ["bench_*.test.ts"],
    pool: "forks",
    poolOptions: {
      forks: {
        singleFork: true
      }
    },
    teardownTimeout: 10000,
    forceExit: true
  }
})
