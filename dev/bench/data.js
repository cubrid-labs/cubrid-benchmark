window.BENCHMARK_DATA = {
  "lastUpdate": 1773897175737,
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
        "date": 1773811174472,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05533563496444235,
            "unit": "iter/sec",
            "range": "stddev: 0.033402089721645926",
            "extra": "mean: 18.071537457599998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03558232106884749,
            "unit": "iter/sec",
            "range": "stddev: 0.18640830745982384",
            "extra": "mean: 28.103843986599998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.0550388168810131,
            "unit": "iter/sec",
            "range": "stddev: 0.09431249062869922",
            "extra": "mean: 18.168995204999998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.052336760201927235,
            "unit": "iter/sec",
            "range": "stddev: 0.06041677678374102",
            "extra": "mean: 19.10702909659999 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.05268226072568055,
            "unit": "iter/sec",
            "range": "stddev: 0.09505059172212173",
            "extra": "mean: 18.981721479399972 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.4126714134471596,
            "unit": "iter/sec",
            "range": "stddev: 0.003975513850138564",
            "extra": "mean: 2.4232354542000394 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.19666022865621954,
            "unit": "iter/sec",
            "range": "stddev: 0.0261878893500437",
            "extra": "mean: 5.084912220599994 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.40377853289374194,
            "unit": "iter/sec",
            "range": "stddev: 0.00951709337515261",
            "extra": "mean: 2.47660516479998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.37544256443013857,
            "unit": "iter/sec",
            "range": "stddev: 0.010480774872315912",
            "extra": "mean: 2.663523251599986 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3769836625387569,
            "unit": "iter/sec",
            "range": "stddev: 0.015049516034576698",
            "extra": "mean: 2.652634847000013 sec\nrounds: 5"
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
        "date": 1773897175364,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.07454176949295405,
            "unit": "iter/sec",
            "range": "stddev: 0.035377440321347584",
            "extra": "mean: 13.415297313199996 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.04857960922541525,
            "unit": "iter/sec",
            "range": "stddev: 0.0786246768603865",
            "extra": "mean: 20.58476829980001 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.07434249414948821,
            "unit": "iter/sec",
            "range": "stddev: 0.06718843907290785",
            "extra": "mean: 13.4512570696 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.07198487778417077,
            "unit": "iter/sec",
            "range": "stddev: 0.028778943189233696",
            "extra": "mean: 13.891806595799995 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.07207703540114403,
            "unit": "iter/sec",
            "range": "stddev: 0.03586933234749319",
            "extra": "mean: 13.874044547400013 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.5209736929260523,
            "unit": "iter/sec",
            "range": "stddev: 0.01711142464018649",
            "extra": "mean: 1.919482717799997 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.2533972549714673,
            "unit": "iter/sec",
            "range": "stddev: 0.008257289907031637",
            "extra": "mean: 3.9463726634000067 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.5084751523821539,
            "unit": "iter/sec",
            "range": "stddev: 0.012662347035120678",
            "extra": "mean: 1.9666644383999938 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.4751827165144914,
            "unit": "iter/sec",
            "range": "stddev: 0.03973989497454652",
            "extra": "mean: 2.104453645400008 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.4786824466320075,
            "unit": "iter/sec",
            "range": "stddev: 0.0042257440763142405",
            "extra": "mean: 2.0890676210000265 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}