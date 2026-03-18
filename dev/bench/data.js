window.BENCHMARK_DATA = {
  "lastUpdate": 1773800029789,
  "repoUrl": "https://github.com/cubrid-labs/cubrid-benchmark",
  "entries": {
    "Python Tier1 Benchmark": [
      {
        "commit": {
          "author": {
            "name": "Sisyphus",
            "username": "sisyphus-dev-ai",
            "email": "clio-agent@sisyphuslabs.ai"
          },
          "committer": {
            "name": "Sisyphus",
            "username": "sisyphus-dev-ai",
            "email": "clio-agent@sisyphuslabs.ai"
          },
          "id": "859942c26bb5e3da72c41f3500b999491848cffd",
          "message": "fix: resolve publish step failure on nightly benchmark\n\nSave benchmark results to /tmp before git checkout to prevent working\ntree conflicts when github-action-benchmark switches to gh-pages branch.\nAlso add permissions: contents: write for auto-push to work.\n\nUltraworked with Sisyphus (https://github.com/code-yeongyu/oh-my-opencode)\nCo-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>",
          "timestamp": "2026-03-18T01:58:49Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/859942c26bb5e3da72c41f3500b999491848cffd"
        },
        "date": 1773800029289,
        "tool": "pytest",
        "benches": [
          {
            "name": "bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05404847483216762,
            "unit": "iter/sec",
            "range": "stddev: 0.020596845650862575",
            "extra": "mean: 18.50190968580001 sec\nrounds: 5"
          },
          {
            "name": "bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03487278503351505,
            "unit": "iter/sec",
            "range": "stddev: 0.0920965826163279",
            "extra": "mean: 28.67565636180001 sec\nrounds: 5"
          },
          {
            "name": "bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.054098765518145714,
            "unit": "iter/sec",
            "range": "stddev: 0.02069858976186615",
            "extra": "mean: 18.484710148600005 sec\nrounds: 5"
          },
          {
            "name": "bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.051436456221233266,
            "unit": "iter/sec",
            "range": "stddev: 0.039625857148062424",
            "extra": "mean: 19.441463768400013 sec\nrounds: 5"
          },
          {
            "name": "bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.051612870529752164,
            "unit": "iter/sec",
            "range": "stddev: 0.01750203099723076",
            "extra": "mean: 19.37501227380003 sec\nrounds: 5"
          },
          {
            "name": "bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.3958161534048737,
            "unit": "iter/sec",
            "range": "stddev: 0.011546327250713235",
            "extra": "mean: 2.5264254412000127 sec\nrounds: 5"
          },
          {
            "name": "bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.19031226503208046,
            "unit": "iter/sec",
            "range": "stddev: 0.008874455797744098",
            "extra": "mean: 5.254522086799989 sec\nrounds: 5"
          },
          {
            "name": "bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.39021169929154964,
            "unit": "iter/sec",
            "range": "stddev: 0.010516289796756452",
            "extra": "mean: 2.5627114763999996 sec\nrounds: 5"
          },
          {
            "name": "bench_pymysql.py::test_bench_update_indexed",
            "value": 0.3651563224733378,
            "unit": "iter/sec",
            "range": "stddev: 0.007978099774172371",
            "extra": "mean: 2.7385531578000153 sec\nrounds: 5"
          },
          {
            "name": "bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.36594055890522914,
            "unit": "iter/sec",
            "range": "stddev: 0.007412782297549714",
            "extra": "mean: 2.7326842451999935 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}