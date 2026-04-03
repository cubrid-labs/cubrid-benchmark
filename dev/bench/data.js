window.BENCHMARK_DATA = {
  "lastUpdate": 1775193991283,
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
          "id": "a66c1971f7046399883b619b17bfd9b69c72c4a3",
          "message": "docs: add roadmap with milestone links",
          "timestamp": "2026-03-20T01:03:31Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/a66c1971f7046399883b619b17bfd9b69c72c4a3"
        },
        "date": 1773983399041,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.055170589973024,
            "unit": "iter/sec",
            "range": "stddev: 0.026624210520741143",
            "extra": "mean: 18.125599173199998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03572860896118106,
            "unit": "iter/sec",
            "range": "stddev: 0.0722307334195611",
            "extra": "mean: 27.98877507619999 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05522072353630376,
            "unit": "iter/sec",
            "range": "stddev: 0.04605995339042017",
            "extra": "mean: 18.109143378799992 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05260029394307285,
            "unit": "iter/sec",
            "range": "stddev: 0.057960137055377704",
            "extra": "mean: 19.01130060380003 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.0525837770233433,
            "unit": "iter/sec",
            "range": "stddev: 0.04283394862589223",
            "extra": "mean: 19.01727218179999 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.41008237382054374,
            "unit": "iter/sec",
            "range": "stddev: 0.008102378785859156",
            "extra": "mean: 2.4385344600000054 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.19583841646337222,
            "unit": "iter/sec",
            "range": "stddev: 0.023402827074512616",
            "extra": "mean: 5.106250438800044 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.40243306057571004,
            "unit": "iter/sec",
            "range": "stddev: 0.007732893691540515",
            "extra": "mean: 2.4848853087999943 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.37872994799680815,
            "unit": "iter/sec",
            "range": "stddev: 0.014380335501870975",
            "extra": "mean: 2.6404038162000005 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.37917894401511953,
            "unit": "iter/sec",
            "range": "stddev: 0.0070520315788217885",
            "extra": "mean: 2.6372772427999736 sec\nrounds: 5"
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
          "id": "a66c1971f7046399883b619b17bfd9b69c72c4a3",
          "message": "docs: add roadmap with milestone links",
          "timestamp": "2026-03-20T01:03:31Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/a66c1971f7046399883b619b17bfd9b69c72c4a3"
        },
        "date": 1774069174105,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.054931878711778716,
            "unit": "iter/sec",
            "range": "stddev: 0.015512583530272716",
            "extra": "mean: 18.20436554239999 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03553717770595614,
            "unit": "iter/sec",
            "range": "stddev: 0.0665543726887539",
            "extra": "mean: 28.139544683999965 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.054676879012407344,
            "unit": "iter/sec",
            "range": "stddev: 0.06624307598149391",
            "extra": "mean: 18.28926628700001 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05201641079805346,
            "unit": "iter/sec",
            "range": "stddev: 0.06609212771511899",
            "extra": "mean: 19.22470206339999 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.05203929833120291,
            "unit": "iter/sec",
            "range": "stddev: 0.05517284389935411",
            "extra": "mean: 19.216246799400004 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.404801097528983,
            "unit": "iter/sec",
            "range": "stddev: 0.009086720966192575",
            "extra": "mean: 2.4703490334000433 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.19437829255052336,
            "unit": "iter/sec",
            "range": "stddev: 0.014281489821452118",
            "extra": "mean: 5.144607388400004 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.3973729909988964,
            "unit": "iter/sec",
            "range": "stddev: 0.007733753504312324",
            "extra": "mean: 2.516527349999933 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.3729738785583841,
            "unit": "iter/sec",
            "range": "stddev: 0.007688126468078018",
            "extra": "mean: 2.6811529104000327 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.37442896030222417,
            "unit": "iter/sec",
            "range": "stddev: 0.010533238892263156",
            "extra": "mean: 2.670733586400047 sec\nrounds: 5"
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
          "id": "b77877721645571a34d41994904bfc115b537b79",
          "message": "feat: add benchflow integration with Go and TypeScript external workers\n\nAdd Go (cmd/benchflow_worker) and TypeScript (benchflow_worker.ts)\nexternal worker harnesses that implement the benchflow subprocess protocol.\nAdd scenario YAML files for point select, full scan, and mixed CRUD\nbenchmarks comparing CUBRID vs MySQL across Python, Go, and TypeScript.\n\nCo-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>",
          "timestamp": "2026-03-21T13:10:23Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/b77877721645571a34d41994904bfc115b537b79"
        },
        "date": 1774156546171,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.0531139558758633,
            "unit": "iter/sec",
            "range": "stddev: 0.020651936912244637",
            "extra": "mean: 18.827443437600028 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03428459586193474,
            "unit": "iter/sec",
            "range": "stddev: 0.026370986294961457",
            "extra": "mean: 29.1676181346 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05317003753786717,
            "unit": "iter/sec",
            "range": "stddev: 0.03549859054157949",
            "extra": "mean: 18.807584991600017 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.050580371824835685,
            "unit": "iter/sec",
            "range": "stddev: 0.012444936875676433",
            "extra": "mean: 19.770515002599996 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.05058045924360332,
            "unit": "iter/sec",
            "range": "stddev: 0.008150938336683077",
            "extra": "mean: 19.770480833000057 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.3920858012067511,
            "unit": "iter/sec",
            "range": "stddev: 0.012736193318839425",
            "extra": "mean: 2.5504621613999463 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.1880603308993671,
            "unit": "iter/sec",
            "range": "stddev: 0.016800127948485438",
            "extra": "mean: 5.317442520799932 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.3847884063798638,
            "unit": "iter/sec",
            "range": "stddev: 0.0032089361905186147",
            "extra": "mean: 2.598830898799997 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.360375956003214,
            "unit": "iter/sec",
            "range": "stddev: 0.016710566443878926",
            "extra": "mean: 2.7748799090000373 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.36144226717892564,
            "unit": "iter/sec",
            "range": "stddev: 0.008399838573486815",
            "extra": "mean: 2.766693579599996 sec\nrounds: 5"
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
          "id": "0bcfc67777bea0c30ac0d3b785f30522e512db57",
          "message": "chore: ignore bin/ directory for compiled worker binaries",
          "timestamp": "2026-03-23T00:51:30Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/0bcfc67777bea0c30ac0d3b785f30522e512db57"
        },
        "date": 1774243557955,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05591865985479641,
            "unit": "iter/sec",
            "range": "stddev: 0.03764025380565229",
            "extra": "mean: 17.883118132599975 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.036125455251634186,
            "unit": "iter/sec",
            "range": "stddev: 0.02891179375001032",
            "extra": "mean: 27.681312056399996 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05598168782740773,
            "unit": "iter/sec",
            "range": "stddev: 0.02690334198594207",
            "extra": "mean: 17.862984107999978 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.053500241639239554,
            "unit": "iter/sec",
            "range": "stddev: 0.08341688785702812",
            "extra": "mean: 18.691504362599993 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.053370568915839495,
            "unit": "iter/sec",
            "range": "stddev: 0.029892476852052954",
            "extra": "mean: 18.736918498600016 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.4160530496821919,
            "unit": "iter/sec",
            "range": "stddev: 0.00676356443190654",
            "extra": "mean: 2.4035396466000294 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.1983775171991417,
            "unit": "iter/sec",
            "range": "stddev: 0.014758360731813004",
            "extra": "mean: 5.040893817600045 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.40726828079169614,
            "unit": "iter/sec",
            "range": "stddev: 0.006881254594278321",
            "extra": "mean: 2.4553839499999413 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.3826265851338999,
            "unit": "iter/sec",
            "range": "stddev: 0.00839664526984262",
            "extra": "mean: 2.6135141646000646 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3833459426061973,
            "unit": "iter/sec",
            "range": "stddev: 0.008339823544151477",
            "extra": "mean: 2.608609845199999 sec\nrounds: 5"
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
          "id": "0bcfc67777bea0c30ac0d3b785f30522e512db57",
          "message": "chore: ignore bin/ directory for compiled worker binaries",
          "timestamp": "2026-03-23T00:51:30Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/0bcfc67777bea0c30ac0d3b785f30522e512db57"
        },
        "date": 1774329439824,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05350623793420095,
            "unit": "iter/sec",
            "range": "stddev: 0.04446126805482022",
            "extra": "mean: 18.689409657800002 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03430606123070417,
            "unit": "iter/sec",
            "range": "stddev: 0.0605580339374052",
            "extra": "mean: 29.149367899599998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05329470847685432,
            "unit": "iter/sec",
            "range": "stddev: 0.06143867200464066",
            "extra": "mean: 18.7635888924 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05039729501619537,
            "unit": "iter/sec",
            "range": "stddev: 0.0877938140146669",
            "extra": "mean: 19.84233478560002 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.050283444773753835,
            "unit": "iter/sec",
            "range": "stddev: 0.05793164332465396",
            "extra": "mean: 19.887261194999997 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.38923165225008366,
            "unit": "iter/sec",
            "range": "stddev: 0.016311754212440736",
            "extra": "mean: 2.569164131999969 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.18664488447401506,
            "unit": "iter/sec",
            "range": "stddev: 0.012931080245284287",
            "extra": "mean: 5.357768056799978 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.3832611652508047,
            "unit": "iter/sec",
            "range": "stddev: 0.008898584010503998",
            "extra": "mean: 2.609186869600012 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.3593145710155462,
            "unit": "iter/sec",
            "range": "stddev: 0.01201525260523722",
            "extra": "mean: 2.783076670599962 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3610266515293901,
            "unit": "iter/sec",
            "range": "stddev: 0.007783355216239879",
            "extra": "mean: 2.769878610799992 sec\nrounds: 5"
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
          "id": "0bcfc67777bea0c30ac0d3b785f30522e512db57",
          "message": "chore: ignore bin/ directory for compiled worker binaries",
          "timestamp": "2026-03-23T00:51:30Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/0bcfc67777bea0c30ac0d3b785f30522e512db57"
        },
        "date": 1774415863775,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.053168674092571734,
            "unit": "iter/sec",
            "range": "stddev: 0.027813615203182145",
            "extra": "mean: 18.808067288999997 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03439292869371095,
            "unit": "iter/sec",
            "range": "stddev: 0.08891218850528188",
            "extra": "mean: 29.075744287599992 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05331129692365316,
            "unit": "iter/sec",
            "range": "stddev: 0.01615180250536367",
            "extra": "mean: 18.757750377599983 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05070207714772219,
            "unit": "iter/sec",
            "range": "stddev: 0.025193670531613633",
            "extra": "mean: 19.72305783620002 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.050757627259817396,
            "unit": "iter/sec",
            "range": "stddev: 0.06029389881799219",
            "extra": "mean: 19.701472546800005 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.3924297637583254,
            "unit": "iter/sec",
            "range": "stddev: 0.013590805972507893",
            "extra": "mean: 2.5482266952000145 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.18798699408056244,
            "unit": "iter/sec",
            "range": "stddev: 0.02535349255883091",
            "extra": "mean: 5.319516942600012 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.3869069369320493,
            "unit": "iter/sec",
            "range": "stddev: 0.01231474797378085",
            "extra": "mean: 2.584600854999985 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.3624161964162927,
            "unit": "iter/sec",
            "range": "stddev: 0.012279057223276255",
            "extra": "mean: 2.7592585813999904 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3625303615198962,
            "unit": "iter/sec",
            "range": "stddev: 0.018275625825421325",
            "extra": "mean: 2.7583896582000307 sec\nrounds: 5"
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
          "id": "69d368034f14c349c150b9c03e840c349bfef8b2",
          "message": "docs: reframe AGENTS.md — remove competition references, neutral project context",
          "timestamp": "2026-03-25T10:59:54Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/69d368034f14c349c150b9c03e840c349bfef8b2"
        },
        "date": 1774502970473,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05478166155517441,
            "unit": "iter/sec",
            "range": "stddev: 0.03520533460808038",
            "extra": "mean: 18.254283853599997 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03562702906072182,
            "unit": "iter/sec",
            "range": "stddev: 0.1143757995387728",
            "extra": "mean: 28.068576762199985 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05526337467652221,
            "unit": "iter/sec",
            "range": "stddev: 0.01976645691712796",
            "extra": "mean: 18.095167112999967 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05260769249381226,
            "unit": "iter/sec",
            "range": "stddev: 0.0250433110156426",
            "extra": "mean: 19.008626924999998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.052713735573169426,
            "unit": "iter/sec",
            "range": "stddev: 0.04473632950713552",
            "extra": "mean: 18.970387682199977 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.4097034338594928,
            "unit": "iter/sec",
            "range": "stddev: 0.005902193293468927",
            "extra": "mean: 2.4407898918 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.19566862068071839,
            "unit": "iter/sec",
            "range": "stddev: 0.008698056465964932",
            "extra": "mean: 5.110681500800001 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.4004531420433922,
            "unit": "iter/sec",
            "range": "stddev: 0.0049757061367404175",
            "extra": "mean: 2.497171066999999 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.3769601454288795,
            "unit": "iter/sec",
            "range": "stddev: 0.007905805777057785",
            "extra": "mean: 2.6528003348000313 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3794263087097634,
            "unit": "iter/sec",
            "range": "stddev: 0.0037146662928131723",
            "extra": "mean: 2.6355578857999946 sec\nrounds: 5"
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
          "id": "69d368034f14c349c150b9c03e840c349bfef8b2",
          "message": "docs: reframe AGENTS.md — remove competition references, neutral project context",
          "timestamp": "2026-03-25T10:59:54Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/69d368034f14c349c150b9c03e840c349bfef8b2"
        },
        "date": 1774589394988,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05870614344111989,
            "unit": "iter/sec",
            "range": "stddev: 0.019571973589587444",
            "extra": "mean: 17.033992379400008 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.037723555503618465,
            "unit": "iter/sec",
            "range": "stddev: 0.05538217616023618",
            "extra": "mean: 26.508635961000003 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05887935587442246,
            "unit": "iter/sec",
            "range": "stddev: 0.0393825165169713",
            "extra": "mean: 16.983881449599995 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05617961995813681,
            "unit": "iter/sec",
            "range": "stddev: 0.03510459830580723",
            "extra": "mean: 17.800049212599994 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.056116668508934875,
            "unit": "iter/sec",
            "range": "stddev: 0.021817421845346952",
            "extra": "mean: 17.820017234999977 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.42830828817208294,
            "unit": "iter/sec",
            "range": "stddev: 0.0073521327339785844",
            "extra": "mean: 2.334766866799987 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.20274156277530703,
            "unit": "iter/sec",
            "range": "stddev: 0.013374226277211972",
            "extra": "mean: 4.9323877467999635 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.4193328378252733,
            "unit": "iter/sec",
            "range": "stddev: 0.0083638190132786",
            "extra": "mean: 2.384740496800009 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.3924999955072517,
            "unit": "iter/sec",
            "range": "stddev: 0.01640283390856062",
            "extra": "mean: 2.547770729799981 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3938021955289725,
            "unit": "iter/sec",
            "range": "stddev: 0.0059867828819182446",
            "extra": "mean: 2.5393459238000333 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "committer": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "id": "13f57927a0bcd0f07ebce5304ed68cfb4f42d37d",
          "message": "docs: add status badge, fix pycubrid version, add ORM experiment to table\n\nUltraworked with [Sisyphus](https://github.com/code-yeongyu/oh-my-opencode)\nCo-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>",
          "timestamp": "2026-03-28T04:20:40Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/13f57927a0bcd0f07ebce5304ed68cfb4f42d37d"
        },
        "date": 1774674920562,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05960726445979598,
            "unit": "iter/sec",
            "range": "stddev: 0.2634659764367546",
            "extra": "mean: 16.77647865679999 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.0376458621546498,
            "unit": "iter/sec",
            "range": "stddev: 0.06384722476323218",
            "extra": "mean: 26.563344356200002 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05939835709359927,
            "unit": "iter/sec",
            "range": "stddev: 0.2818922049587765",
            "extra": "mean: 16.835482476800006 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.056575921730886394,
            "unit": "iter/sec",
            "range": "stddev: 0.26621805463012893",
            "extra": "mean: 17.675363819199994 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.056246800752773767,
            "unit": "iter/sec",
            "range": "stddev: 0.2122593078162377",
            "extra": "mean: 17.778788955400024 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.4275496305068761,
            "unit": "iter/sec",
            "range": "stddev: 0.010923927160930415",
            "extra": "mean: 2.3389097514000015 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.20241128154424437,
            "unit": "iter/sec",
            "range": "stddev: 0.014804731057130833",
            "extra": "mean: 4.940436088200022 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.41974203918031405,
            "unit": "iter/sec",
            "range": "stddev: 0.02452992643063808",
            "extra": "mean: 2.3824156425999945 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.39305932433337476,
            "unit": "iter/sec",
            "range": "stddev: 0.014271563178453002",
            "extra": "mean: 2.544145216999982 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3943414457235296,
            "unit": "iter/sec",
            "range": "stddev: 0.004605609095263277",
            "extra": "mean: 2.5358734438000057 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "committer": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "id": "6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2",
          "message": "bench: add post-sa-optimization ORM overhead re-measurement\n\nRe-measure ORM overhead after sqlalchemy-cubrid v0.7.1 optimizations\n(query compilation caching, result mapping). Finding: absolute SA ORM\nlatencies unchanged — optimizations target cold-start/diverse-query\nworkloads rather than steady-state repetitive benchmarks.\n\nUltraworked with [Sisyphus](https://github.com/code-yeongyu/oh-my-opencode)\n\nCo-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>",
          "timestamp": "2026-03-28T12:15:32Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2"
        },
        "date": 1774762487248,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05416966305200841,
            "unit": "iter/sec",
            "range": "stddev: 0.18180273610850411",
            "extra": "mean: 18.4605172648 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.035122303008254634,
            "unit": "iter/sec",
            "range": "stddev: 0.2924417762447312",
            "extra": "mean: 28.471937041400007 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.054727840663271986,
            "unit": "iter/sec",
            "range": "stddev: 0.26253629512297705",
            "extra": "mean: 18.2722356278 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05197924909895618,
            "unit": "iter/sec",
            "range": "stddev: 0.19971225902690817",
            "extra": "mean: 19.238446444200008 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.05212197305352313,
            "unit": "iter/sec",
            "range": "stddev: 0.22983409540704472",
            "extra": "mean: 19.185766413200007 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.39650980331262586,
            "unit": "iter/sec",
            "range": "stddev: 0.011498230549498752",
            "extra": "mean: 2.522005740199961 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.19089961758741586,
            "unit": "iter/sec",
            "range": "stddev: 0.0106594140575777",
            "extra": "mean: 5.238355176599998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.38933314993395346,
            "unit": "iter/sec",
            "range": "stddev: 0.01524646778085727",
            "extra": "mean: 2.568494360600016 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.36452216322984315,
            "unit": "iter/sec",
            "range": "stddev: 0.010846718059874402",
            "extra": "mean: 2.7433174190000273 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3657415914147036,
            "unit": "iter/sec",
            "range": "stddev: 0.0031980983237322605",
            "extra": "mean: 2.7341708558000164 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "committer": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "id": "6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2",
          "message": "bench: add post-sa-optimization ORM overhead re-measurement\n\nRe-measure ORM overhead after sqlalchemy-cubrid v0.7.1 optimizations\n(query compilation caching, result mapping). Finding: absolute SA ORM\nlatencies unchanged — optimizations target cold-start/diverse-query\nworkloads rather than steady-state repetitive benchmarks.\n\nUltraworked with [Sisyphus](https://github.com/code-yeongyu/oh-my-opencode)\n\nCo-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>",
          "timestamp": "2026-03-28T12:15:32Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2"
        },
        "date": 1774849669226,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05379931821518076,
            "unit": "iter/sec",
            "range": "stddev: 0.02977713017199653",
            "extra": "mean: 18.587596147599992 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03456911491631437,
            "unit": "iter/sec",
            "range": "stddev: 0.06641274313482884",
            "extra": "mean: 28.927555779799995 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05407775693064899,
            "unit": "iter/sec",
            "range": "stddev: 0.1551077077211135",
            "extra": "mean: 18.49189124620001 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05058266609041542,
            "unit": "iter/sec",
            "range": "stddev: 0.0244068021503629",
            "extra": "mean: 19.769618276200028 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.05137088353993022,
            "unit": "iter/sec",
            "range": "stddev: 0.36736487264996126",
            "extra": "mean: 19.4662799448 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.39304010975483566,
            "unit": "iter/sec",
            "range": "stddev: 0.011800859357506464",
            "extra": "mean: 2.544269592799992 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.18861054960558038,
            "unit": "iter/sec",
            "range": "stddev: 0.012254721612021485",
            "extra": "mean: 5.301930364400005 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.3870236899283551,
            "unit": "iter/sec",
            "range": "stddev: 0.011104355533603378",
            "extra": "mean: 2.58382116140001 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.36210886265050374,
            "unit": "iter/sec",
            "range": "stddev: 0.006981939092633659",
            "extra": "mean: 2.76160045539998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.36390945195496394,
            "unit": "iter/sec",
            "range": "stddev: 0.009476855691889448",
            "extra": "mean: 2.747936319400014 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "committer": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "id": "6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2",
          "message": "bench: add post-sa-optimization ORM overhead re-measurement\n\nRe-measure ORM overhead after sqlalchemy-cubrid v0.7.1 optimizations\n(query compilation caching, result mapping). Finding: absolute SA ORM\nlatencies unchanged — optimizations target cold-start/diverse-query\nworkloads rather than steady-state repetitive benchmarks.\n\nUltraworked with [Sisyphus](https://github.com/code-yeongyu/oh-my-opencode)\n\nCo-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>",
          "timestamp": "2026-03-28T12:15:32Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2"
        },
        "date": 1774934934196,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.07850964899664951,
            "unit": "iter/sec",
            "range": "stddev: 0.20960926845426675",
            "extra": "mean: 12.73728787199999 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.051384043239170826,
            "unit": "iter/sec",
            "range": "stddev: 0.2974332805067403",
            "extra": "mean: 19.461294537399986 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.07922979803016189,
            "unit": "iter/sec",
            "range": "stddev: 0.2861519689343941",
            "extra": "mean: 12.621513936200007 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.07483759828554931,
            "unit": "iter/sec",
            "range": "stddev: 0.05166576884414742",
            "extra": "mean: 13.362267401800011 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.07510269494365776,
            "unit": "iter/sec",
            "range": "stddev: 0.23867712015128761",
            "extra": "mean: 13.315101418799987 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.5420284846735504,
            "unit": "iter/sec",
            "range": "stddev: 0.01496451705848185",
            "extra": "mean: 1.8449214908000158 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.26431778067166367,
            "unit": "iter/sec",
            "range": "stddev: 0.014215122349915652",
            "extra": "mean: 3.783324744400011 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.5330182330238812,
            "unit": "iter/sec",
            "range": "stddev: 0.02447183250279286",
            "extra": "mean: 1.8761084294000057 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.49852336541642944,
            "unit": "iter/sec",
            "range": "stddev: 0.009398848332940545",
            "extra": "mean: 2.0059240336000586 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.5033012196893322,
            "unit": "iter/sec",
            "range": "stddev: 0.012671619453794804",
            "extra": "mean: 1.98688173380001 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "committer": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "id": "6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2",
          "message": "bench: add post-sa-optimization ORM overhead re-measurement\n\nRe-measure ORM overhead after sqlalchemy-cubrid v0.7.1 optimizations\n(query compilation caching, result mapping). Finding: absolute SA ORM\nlatencies unchanged — optimizations target cold-start/diverse-query\nworkloads rather than steady-state repetitive benchmarks.\n\nUltraworked with [Sisyphus](https://github.com/code-yeongyu/oh-my-opencode)\n\nCo-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>",
          "timestamp": "2026-03-28T12:15:32Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2"
        },
        "date": 1775022275261,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05969039697700236,
            "unit": "iter/sec",
            "range": "stddev: 0.15501318766878416",
            "extra": "mean: 16.7531135768 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.038313253391674365,
            "unit": "iter/sec",
            "range": "stddev: 0.18673722986060884",
            "extra": "mean: 26.100628672200003 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05973584317708694,
            "unit": "iter/sec",
            "range": "stddev: 0.2037345271063466",
            "extra": "mean: 16.740368040600003 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.056916272468240305,
            "unit": "iter/sec",
            "range": "stddev: 0.19106117417574967",
            "extra": "mean: 17.569667805600012 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.05660033722977646,
            "unit": "iter/sec",
            "range": "stddev: 0.0654348635781523",
            "extra": "mean: 17.6677392564 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.43588753264893554,
            "unit": "iter/sec",
            "range": "stddev: 0.007598551117416148",
            "extra": "mean: 2.294169768799975 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.20680104301282282,
            "unit": "iter/sec",
            "range": "stddev: 0.017875638960515115",
            "extra": "mean: 4.835565553400011 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.42817996935295477,
            "unit": "iter/sec",
            "range": "stddev: 0.007685550284207359",
            "extra": "mean: 2.3354665597999658 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.40001412437072953,
            "unit": "iter/sec",
            "range": "stddev: 0.00949173299778379",
            "extra": "mean: 2.499911725799984 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.4006457124253861,
            "unit": "iter/sec",
            "range": "stddev: 0.012410653099430118",
            "extra": "mean: 2.495970801600015 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "committer": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "id": "6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2",
          "message": "bench: add post-sa-optimization ORM overhead re-measurement\n\nRe-measure ORM overhead after sqlalchemy-cubrid v0.7.1 optimizations\n(query compilation caching, result mapping). Finding: absolute SA ORM\nlatencies unchanged — optimizations target cold-start/diverse-query\nworkloads rather than steady-state repetitive benchmarks.\n\nUltraworked with [Sisyphus](https://github.com/code-yeongyu/oh-my-opencode)\n\nCo-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>",
          "timestamp": "2026-03-28T12:15:32Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2"
        },
        "date": 1775107468408,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05910129065524062,
            "unit": "iter/sec",
            "range": "stddev: 0.36359201625911536",
            "extra": "mean: 16.920104263600006 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03781711129962414,
            "unit": "iter/sec",
            "range": "stddev: 0.3093159773455348",
            "extra": "mean: 26.44305621540001 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.05935063051685977,
            "unit": "iter/sec",
            "range": "stddev: 0.3632223140597349",
            "extra": "mean: 16.84902066400001 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.056628801180852575,
            "unit": "iter/sec",
            "range": "stddev: 0.28854427424758394",
            "extra": "mean: 17.65885872819998 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.05613045833051369,
            "unit": "iter/sec",
            "range": "stddev: 0.3260688804795468",
            "extra": "mean: 17.815639311400012 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.42677954037261756,
            "unit": "iter/sec",
            "range": "stddev: 0.012257381918306073",
            "extra": "mean: 2.3431301302000294 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.20205581031973632,
            "unit": "iter/sec",
            "range": "stddev: 0.03708817915047274",
            "extra": "mean: 4.9491276614000075 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.41801182069376125,
            "unit": "iter/sec",
            "range": "stddev: 0.009210590261737237",
            "extra": "mean: 2.392276846000027 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.3906096135211289,
            "unit": "iter/sec",
            "range": "stddev: 0.012489106931510209",
            "extra": "mean: 2.5601008407999872 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.3941033338873702,
            "unit": "iter/sec",
            "range": "stddev: 0.00833082914572227",
            "extra": "mean: 2.537405583799978 sec\nrounds: 5"
          }
        ]
      },
      {
        "commit": {
          "author": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "committer": {
            "name": "yeongseon",
            "username": "yeongseon",
            "email": "yeongseon@users.noreply.github.com"
          },
          "id": "6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2",
          "message": "bench: add post-sa-optimization ORM overhead re-measurement\n\nRe-measure ORM overhead after sqlalchemy-cubrid v0.7.1 optimizations\n(query compilation caching, result mapping). Finding: absolute SA ORM\nlatencies unchanged — optimizations target cold-start/diverse-query\nworkloads rather than steady-state repetitive benchmarks.\n\nUltraworked with [Sisyphus](https://github.com/code-yeongyu/oh-my-opencode)\n\nCo-authored-by: Sisyphus <clio-agent@sisyphuslabs.ai>",
          "timestamp": "2026-03-28T12:15:32Z",
          "url": "https://github.com/cubrid-labs/cubrid-benchmark/commit/6c29a6ad380d3a43fe575fd9ec8b1cf639fc66e2"
        },
        "date": 1775193990744,
        "tool": "pytest",
        "benches": [
          {
            "name": "python/bench_pycubrid.py::test_bench_insert_sequential",
            "value": 0.05964459927396697,
            "unit": "iter/sec",
            "range": "stddev: 0.05155232562748855",
            "extra": "mean: 16.765977342000003 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_by_pk",
            "value": 0.03927422780176657,
            "unit": "iter/sec",
            "range": "stddev: 0.35094731415240604",
            "extra": "mean: 25.461990113400002 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_select_full_scan",
            "value": 0.061634478788104935,
            "unit": "iter/sec",
            "range": "stddev: 0.4246966902935909",
            "extra": "mean: 16.224684943600003 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_update_indexed",
            "value": 0.05778718331953968,
            "unit": "iter/sec",
            "range": "stddev: 0.2990135733497258",
            "extra": "mean: 17.304875277800022 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pycubrid.py::test_bench_delete_sequential",
            "value": 0.05849722096118702,
            "unit": "iter/sec",
            "range": "stddev: 0.48469581523527683",
            "extra": "mean: 17.094829182800005 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_insert_sequential",
            "value": 0.44775119010544573,
            "unit": "iter/sec",
            "range": "stddev: 0.003990665954486797",
            "extra": "mean: 2.2333832318000075 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_by_pk",
            "value": 0.2154529903165452,
            "unit": "iter/sec",
            "range": "stddev: 0.024892111208032478",
            "extra": "mean: 4.641383712200013 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_select_full_scan",
            "value": 0.44072942742658383,
            "unit": "iter/sec",
            "range": "stddev: 0.007824120947231537",
            "extra": "mean: 2.2689658047999957 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_update_indexed",
            "value": 0.4121983230777623,
            "unit": "iter/sec",
            "range": "stddev: 0.006806141756918356",
            "extra": "mean: 2.426016662400025 sec\nrounds: 5"
          },
          {
            "name": "python/bench_pymysql.py::test_bench_delete_sequential",
            "value": 0.41248828140694727,
            "unit": "iter/sec",
            "range": "stddev: 0.01403294464372437",
            "extra": "mean: 2.4243112958000212 sec\nrounds: 5"
          }
        ]
      }
    ]
  }
}