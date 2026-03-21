// benchflow_worker is an external worker for benchflow.
//
// It reads a benchflow WorkerInput JSON config from the file path given as
// the first CLI argument, runs the benchmark, and writes a WorkerOutput JSON
// to stdout.
//
// Supports both CUBRID and MySQL via database/sql, determined by DSN prefix.
//
// Usage:
//
//	go run ./cmd/benchflow_worker /tmp/benchflow_xyz.json
package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"math"
	"math/rand"
	"net/url"
	"os"
	"regexp"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"
	"time"

	_ "github.com/cubrid-labs/cubrid-go"
	_ "github.com/go-sql-driver/mysql"
)

// ---------------------------------------------------------------------------
// Input / Output schemas (mirrors benchflow.workers.external.protocol)
// ---------------------------------------------------------------------------

type InputStep struct {
	Name   string                 `json:"name"`
	Query  string                 `json:"query"`
	Params map[string]interface{} `json:"params"`
}

type WorkerInput struct {
	DSN            string                 `json:"dsn"`
	Steps          []InputStep            `json:"steps"`
	Concurrency    int                    `json:"concurrency"`
	DurationS      int                    `json:"duration_s"`
	WarmupS        int                    `json:"warmup_s"`
	Seed           *int64                 `json:"seed"`
	SetupQueries   []string               `json:"setup_queries"`
	TeardownQueries []string              `json:"teardown_queries"`
	WorkerConfig   map[string]interface{} `json:"worker_config"`
}

type LatencySummary struct {
	MinNs   int64   `json:"min_ns"`
	MaxNs   int64   `json:"max_ns"`
	MeanNs  int64   `json:"mean_ns"`
	StdevNs int64   `json:"stdev_ns"`
	P50Ns   int64   `json:"p50_ns"`
	P95Ns   int64   `json:"p95_ns"`
	P99Ns   int64   `json:"p99_ns"`
	P999Ns  int64   `json:"p999_ns"`
	P9999Ns int64   `json:"p9999_ns"`
}

type TimeWindow struct {
	Second int     `json:"second"`
	Ops    int     `json:"ops"`
	Errors int     `json:"errors"`
	P50Ns  float64 `json:"p50_ns"`
	P95Ns  float64 `json:"p95_ns"`
	P99Ns  float64 `json:"p99_ns"`
}

type OutputStep struct {
	Name           string         `json:"name"`
	Ops            int            `json:"ops"`
	Errors         int            `json:"errors"`
	LatencySummary LatencySummary `json:"latency_summary"`
	ThroughputOpsS float64       `json:"throughput_ops_s"`
	SamplesNs      []int64        `json:"samples_ns"`
	TimeSeries     []TimeWindow   `json:"time_series"`
}

type WorkerOutput struct {
	Status       string                 `json:"status"`
	Steps        []OutputStep           `json:"steps"`
	DurationS    float64                `json:"duration_s"`
	ErrorMessage *string                `json:"error_message"`
	ServerInfo   map[string]interface{} `json:"server_info"`
}

// ---------------------------------------------------------------------------
// DSN parsing
// ---------------------------------------------------------------------------

func parseDriver(dsn string) (driverName string, driverDSN string, err error) {
	if strings.HasPrefix(dsn, "cubrid://") {
		return "cubrid", dsn, nil
	}
	if strings.HasPrefix(dsn, "mysql://") {
		u, err := url.Parse(dsn)
		if err != nil {
			return "", "", fmt.Errorf("parse mysql DSN: %w", err)
		}
		user := u.User.Username()
		pass, _ := u.User.Password()
		host := u.Hostname()
		port := u.Port()
		if port == "" {
			port = "3306"
		}
		dbName := strings.TrimPrefix(u.Path, "/")
		mysqlDSN := fmt.Sprintf("%s:%s@tcp(%s:%s)/%s", user, pass, host, port, dbName)
		return "mysql", mysqlDSN, nil
	}
	return "", "", fmt.Errorf("unsupported DSN scheme: %s", dsn)
}

// ---------------------------------------------------------------------------
// Parameter resolution
// ---------------------------------------------------------------------------

var (
	reRandomInt    = regexp.MustCompile(`^random_int\((\d+),\s*(\d+)\)$`)
	reRandomChoice = regexp.MustCompile(`^random_choice\((.+)\)$`)
	rePyformat     = regexp.MustCompile(`%\((\w+)\)s`)
)

func resolveParams(params map[string]interface{}, rng *rand.Rand) map[string]interface{} {
	if params == nil {
		return nil
	}
	resolved := make(map[string]interface{}, len(params))
	for k, v := range params {
		s, ok := v.(string)
		if !ok {
			resolved[k] = v
			continue
		}
		if m := reRandomInt.FindStringSubmatch(s); m != nil {
			lo, _ := strconv.Atoi(m[1])
			hi, _ := strconv.Atoi(m[2])
			resolved[k] = lo + rng.Intn(hi-lo+1)
		} else if m := reRandomChoice.FindStringSubmatch(s); m != nil {
			choices := strings.Split(m[1], ",")
			for i := range choices {
				choices[i] = strings.TrimSpace(choices[i])
			}
			resolved[k] = choices[rng.Intn(len(choices))]
		} else {
			resolved[k] = v
		}
	}
	return resolved
}

// translateQuery converts %(name)s placeholders to ? and returns ordered args.
func translateQuery(query string, params map[string]interface{}) (string, []interface{}) {
	if params == nil {
		return query, nil
	}
	var args []interface{}
	translated := rePyformat.ReplaceAllStringFunc(query, func(match string) string {
		name := rePyformat.FindStringSubmatch(match)[1]
		args = append(args, params[name])
		return "?"
	})
	return translated, args
}

// ---------------------------------------------------------------------------
// Per-step collector
// ---------------------------------------------------------------------------

type stepCollector struct {
	name      string
	latencies []int64 // nanoseconds
	errors    int64
	mu        sync.Mutex
	// time-series: second -> latencies
	timeBuckets map[int][]int64
	timeErrors  map[int]int64
}

func newStepCollector(name string) *stepCollector {
	return &stepCollector{
		name:        name,
		timeBuckets: make(map[int][]int64),
		timeErrors:  make(map[int]int64),
	}
}

func (sc *stepCollector) record(latencyNs int64, second int) {
	sc.mu.Lock()
	sc.latencies = append(sc.latencies, latencyNs)
	sc.timeBuckets[second] = append(sc.timeBuckets[second], latencyNs)
	sc.mu.Unlock()
}

func (sc *stepCollector) recordError(second int) {
	sc.mu.Lock()
	sc.errors++
	sc.timeErrors[second]++
	sc.mu.Unlock()
}

func (sc *stepCollector) toOutputStep(durationS float64) OutputStep {
	sc.mu.Lock()
	defer sc.mu.Unlock()

	ops := len(sc.latencies)
	if ops == 0 {
		return OutputStep{Name: sc.name, Errors: int(sc.errors)}
	}

	sorted := make([]int64, len(sc.latencies))
	copy(sorted, sc.latencies)
	sort.Slice(sorted, func(i, j int) bool { return sorted[i] < sorted[j] })

	summary := LatencySummary{
		MinNs:   sorted[0],
		MaxNs:   sorted[len(sorted)-1],
		MeanNs:  mean(sorted),
		StdevNs: stdev(sorted),
		P50Ns:   percentile(sorted, 50),
		P95Ns:   percentile(sorted, 95),
		P99Ns:   percentile(sorted, 99),
		P999Ns:  percentile(sorted, 99.9),
		P9999Ns: percentile(sorted, 99.99),
	}

	// Reservoir sample (max 10000)
	samples := sorted
	if len(samples) > 10000 {
		sampled := make([]int64, 10000)
		rng := rand.New(rand.NewSource(42))
		for i := range sampled {
			sampled[i] = sorted[rng.Intn(len(sorted))]
		}
		samples = sampled
	}

	// Time-series
	var timeSeries []TimeWindow
	if len(sc.timeBuckets) > 0 {
		maxSec := 0
		for s := range sc.timeBuckets {
			if s > maxSec {
				maxSec = s
			}
		}
		for s := 0; s <= maxSec; s++ {
			lats := sc.timeBuckets[s]
			errs := sc.timeErrors[s]
			if len(lats) > 0 {
				sortedBucket := make([]int64, len(lats))
				copy(sortedBucket, lats)
				sort.Slice(sortedBucket, func(i, j int) bool { return sortedBucket[i] < sortedBucket[j] })
				timeSeries = append(timeSeries, TimeWindow{
					Second: s,
					Ops:    len(lats),
					Errors: int(errs),
					P50Ns:  float64(percentile(sortedBucket, 50)),
					P95Ns:  float64(percentile(sortedBucket, 95)),
					P99Ns:  float64(percentile(sortedBucket, 99)),
				})
			}
		}
	}

	throughput := float64(ops) / durationS

	return OutputStep{
		Name:           sc.name,
		Ops:            ops,
		Errors:         int(sc.errors),
		LatencySummary: summary,
		ThroughputOpsS: throughput,
		SamplesNs:      samples,
		TimeSeries:     timeSeries,
	}
}

// ---------------------------------------------------------------------------
// Math helpers
// ---------------------------------------------------------------------------

func mean(sorted []int64) int64 {
	if len(sorted) == 0 {
		return 0
	}
	var sum int64
	for _, v := range sorted {
		sum += v
	}
	return sum / int64(len(sorted))
}

func stdev(sorted []int64) int64 {
	if len(sorted) < 2 {
		return 0
	}
	m := mean(sorted)
	var sumSq float64
	for _, v := range sorted {
		d := float64(v - m)
		sumSq += d * d
	}
	return int64(math.Sqrt(sumSq / float64(len(sorted))))
}

func percentile(sorted []int64, p float64) int64 {
	if len(sorted) == 0 {
		return 0
	}
	idx := int(math.Ceil(p/100*float64(len(sorted)))) - 1
	if idx < 0 {
		idx = 0
	}
	if idx >= len(sorted) {
		idx = len(sorted) - 1
	}
	return sorted[idx]
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

func main() {
	if len(os.Args) < 2 {
		fatal("usage: benchflow_worker <config.json>")
	}

	data, err := os.ReadFile(os.Args[1])
	if err != nil {
		fatal("read config: %v", err)
	}

	var input WorkerInput
	if err := json.Unmarshal(data, &input); err != nil {
		fatal("parse config: %v", err)
	}

	if input.Concurrency < 1 {
		input.Concurrency = 1
	}

	driverName, driverDSN, err := parseDriver(input.DSN)
	if err != nil {
		fatal("%v", err)
	}

	db, err := sql.Open(driverName, driverDSN)
	if err != nil {
		fatal("open db: %v", err)
	}
	defer db.Close()

	if err := db.Ping(); err != nil {
		fatal("ping db: %v", err)
	}

	// Server info
	serverInfo := map[string]interface{}{}
	var version string
	if err := db.QueryRow("SELECT version()").Scan(&version); err == nil {
		serverInfo["server_version"] = version
	}

	// Setup
	for _, q := range input.SetupQueries {
		if _, err := db.Exec(q); err != nil {
			fatal("setup query failed: %v\nquery: %s", err, q)
		}
	}

	// Pre-translate queries (strip %(name)s → ?)
	type preparedStep struct {
		name      string
		query     string // with ? placeholders
		rawParams map[string]interface{}
		paramOrder []string // ordered param names matching ?s
	}

	var steps []preparedStep
	for _, s := range input.Steps {
		var paramOrder []string
		query := rePyformat.ReplaceAllStringFunc(s.Query, func(match string) string {
			name := rePyformat.FindStringSubmatch(match)[1]
			paramOrder = append(paramOrder, name)
			return "?"
		})
		steps = append(steps, preparedStep{
			name:       s.Name,
			query:      query,
			rawParams:  s.Params,
			paramOrder: paramOrder,
		})
	}

	// Create collectors
	collectors := make(map[string]*stepCollector)
	for _, s := range steps {
		collectors[s.name] = newStepCollector(s.name)
	}

	// Seed
	var baseSeed int64 = time.Now().UnixNano()
	if input.Seed != nil {
		baseSeed = *input.Seed
	}

	// Warmup
	if input.WarmupS > 0 {
		warmupDeadline := time.Now().Add(time.Duration(input.WarmupS) * time.Second)
		warmupRng := rand.New(rand.NewSource(baseSeed))
		for time.Now().Before(warmupDeadline) {
			for _, s := range steps {
				resolved := resolveParams(s.rawParams, warmupRng)
				args := make([]interface{}, len(s.paramOrder))
				for i, name := range s.paramOrder {
					args[i] = resolved[name]
				}
				rows, err := db.Query(s.query, args...)
				if err == nil {
					for rows.Next() {
					}
					rows.Close()
				}
			}
		}
	}

	// Benchmark
	runtime.GC()

	var ready sync.WaitGroup
	ready.Add(input.Concurrency)
	var start sync.WaitGroup
	start.Add(1)
	var done int64

	durationNs := int64(input.DurationS) * 1e9
	benchStart := time.Now()

	for w := 0; w < input.Concurrency; w++ {
		go func(workerID int) {
			rng := rand.New(rand.NewSource(baseSeed + int64(workerID)*1000))
			ready.Done()
			start.Wait()

			deadline := time.Now().Add(time.Duration(durationNs))
			for time.Now().Before(deadline) {
				for _, s := range steps {
					resolved := resolveParams(s.rawParams, rng)
					args := make([]interface{}, len(s.paramOrder))
					for i, name := range s.paramOrder {
						args[i] = resolved[name]
					}

					t0 := time.Now()
					rows, err := db.Query(s.query, args...)
					if err != nil {
						sec := int(time.Since(benchStart).Seconds())
						collectors[s.name].recordError(sec)
						continue
					}
					for rows.Next() {
					}
					rows.Close()
					latency := time.Since(t0).Nanoseconds()
					sec := int(time.Since(benchStart).Seconds())
					collectors[s.name].record(latency, sec)
				}
			}
			atomic.AddInt64(&done, 1)
		}(w)
	}

	ready.Wait()
	start.Done() // release all goroutines
	// Wait for all to finish
	for atomic.LoadInt64(&done) < int64(input.Concurrency) {
		time.Sleep(10 * time.Millisecond)
	}

	actualDuration := time.Since(benchStart).Seconds()

	// Teardown
	for _, q := range input.TeardownQueries {
		db.Exec(q) // best-effort
	}

	// Build output
	var outputSteps []OutputStep
	for _, s := range input.Steps {
		outputSteps = append(outputSteps, collectors[s.Name].toOutputStep(actualDuration))
	}

	output := WorkerOutput{
		Status:     "ok",
		Steps:      outputSteps,
		DurationS:  actualDuration,
		ServerInfo: serverInfo,
	}

	enc := json.NewEncoder(os.Stdout)
	enc.SetIndent("", "  ")
	if err := enc.Encode(output); err != nil {
		fatal("encode output: %v", err)
	}
}

func fatal(format string, args ...interface{}) {
	msg := fmt.Sprintf(format, args...)
	output := WorkerOutput{
		Status:       "error",
		ErrorMessage: &msg,
	}
	enc := json.NewEncoder(os.Stdout)
	enc.Encode(output)
	os.Exit(1)
}
