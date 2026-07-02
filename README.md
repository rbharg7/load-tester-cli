# Load Tester CLI

An async Python CLI tool for load testing APIs and backend services. Fires concurrent requests with controlled concurrency, measures percentile latencies, and reports results with live terminal output.

Built to stress test my own projects ([url-shortener](https://github.com/rbharg7/url-shortener), [task-queue](https://github.com/rbharg7/task-queue)) and then generalized into a standalone tool.

## Demo

```
╭──────────────────── Load Test Results ─────────────────────╮
│ POST http://localhost:8000/shorten                         │
╰────────────────────────────────────────────────────────────╯
  Duration:    5s
  Concurrency: 20
  Requests:    4418
  Throughput:  883.6 req/s

        Latency
  ┌────────┬──────────┐
  │ Metric │    Value │
  ├────────┼──────────┤
  │ Avg    │  1.37 ms │
  │ Median │  0.59 ms │
  │ P90    │  0.73 ms │
  │ P95    │  0.89 ms │
  │ P99    │ 22.01 ms │
  │ Max    │ 174.6 ms │
  └────────┴──────────┘

      Status Codes
  ┌──────┬───────┬──────────┐
  │ 200  │    10 │  0.2%    │
  │ 429  │  4408 │  99.8%   │
  └──────┴───────┴──────────┘
```

The 429 responses are the URL shortener's rate limiter doing its job i.e. one project stress testing another.

## Usage

```bash
# Basic GET request
loadtest http://localhost:8000/docs -c 10 -d 5

# POST with body
loadtest http://localhost:8000/shorten \
  -m POST \
  -b '{"url": "https://google.com"}' \
  -c 20 -d 10

# Custom headers
loadtest http://api.example.com/data \
  -H "Authorization:Bearer token123" \
  -c 50 -d 30

# JSON output for piping to other tools
loadtest http://localhost:8000/docs --json-output
```

### Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--method` | `-m` | GET | HTTP method |
| `--body` | `-b` | None | Request body (JSON string) |
| `--header` | `-H` | None | Headers (key:value), repeatable |
| `--concurrency` | `-c` | 10 | Concurrent connections |
| `--duration` | `-d` | 5 | Test duration in seconds |
| `--json-output` | | False | Output as JSON |

## Design Decisions

**Async with aiohttp**: HTTP requests are I/O-bound (the CPU waits for network responses). Async handles thousands of concurrent waiting tasks on a single thread. Threads would work but use more memory and add context-switching overhead. `aiohttp` with `asyncio` is the standard for high-concurrency HTTP in Python.

**Semaphore-controlled concurrency**: an `asyncio.Semaphore` gates how many requests are in-flight simultaneously. Without it, firing 1000 requests with only 50 available connections means 950 wait in a local queue — and the latency numbers become meaningless because they measure local queueing, not server response time.

**Percentile latency tracking**: averages hide problems. If 99 requests take 10ms and 1 takes 5000ms, the average (59ms) looks fine. P99 (5000ms) tells the truth. This tool reports P90, P95, and P99 because that's what production systems actually alert on.

**`time.monotonic()` for measurement**: unlike `time.time()`, the monotonic clock never goes backward (even if the system clock adjusts). For measuring latency down to the millisecond, the clock must be reliable.

## Installation

```bash
git clone https://github.com/rbharg7/load-tester-cli
cd load-tester-cli
pip install -e .
```

The `-e` flag (editable) means changes take effect immediately without reinstalling. After installation, `loadtest` is available as a command anywhere on your system.

### Requirements
- Python 3.11+
- click
- aiohttp
- rich
- numpy

## Project Structure

```
load-tester-cli/
├── loadtest/
│   ├── __init__.py
│   ├── cli.py        # Click command definitions
│   ├── runner.py     # Async load generation engine
│   ├── stats.py      # Percentile and histogram computation
│   └── display.py    # Rich terminal output formatting
└── setup.py          # Package installation config
```
