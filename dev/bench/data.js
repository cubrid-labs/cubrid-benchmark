window.BENCHMARK_DATA = {
  "lastUpdate": 1773805390074,
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
      },
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
          "id": "2da094f1b61c6f0f8590071558acefebf4478182",
          "message": "feat: add extended benchmark workloads with P95/P99 latency and RSS tracking\n\nAdd 4 new benchmark workloads (connect_disconnect, prepared_statement,\nbatch_insert, concurrent_select) across Python, TypeScript, and Go.\nEnhance normalize_results.py with P95/P99 latency approximation.\nAdd collect_metrics.py for RSS memory tracking via resource.getrusage.\nFix tier1 Makefile/script globs to isolate base vs extended benchmarks.\n\nUltraworked with Sisyphus (https://github.com/code-yeongyu/oh-my-opencode)\nCo-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>",
          "timestamp": "2026-03-18T03:04:01Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/2da094f1b61c6f0f8590071558acefebf4478182"
        },
        "date": 1773805389231,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05535821889845797,
            "unit": "iter/sec",
            "range": "stddev: 0.027800412538417404",
            "extra": "mean: 18.064164994799995 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.035758649295318856,
            "unit": "iter/sec",
            "range": "stddev: 0.012782478785660483",
            "extra": "mean: 27.965262103200008 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.0553563611658745,
            "unit": "iter/sec",
            "range": "stddev: 0.03957507771834297",
            "extra": "mean: 18.064771219399972 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05271136036556384,
            "unit": "iter/sec",
            "range": "stddev: 0.027066270585493955",
            "extra": "mean: 18.971242499999995 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.052741146158040056,
            "unit": "iter/sec",
            "range": "stddev: 0.014852933903165569",
            "extra": "mean: 18.960528408000027 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.41364341276652217,
            "unit": "iter/sec",
            "range": "stddev: 0.00717889260071208",
            "extra": "mean: 2.41754121820004 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.19735544719897052,
            "unit": "iter/sec",
            "range": "stddev: 0.019084859493230157",
            "extra": "mean: 5.066999741799964 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.4053952899383065,
            "unit": "iter/sec",
            "range": "stddev: 0.005784743445234346",
            "extra": "mean: 2.466728215199987 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.3789579401253421,
            "unit": "iter/sec",
            "range": "stddev: 0.020464951399798956",
            "extra": "mean: 2.6388152724000067 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3824560167040554,
            "unit": "iter/sec",
            "range": "stddev: 0.004391298524170777",
            "extra": "mean: 2.6146797443999956 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}