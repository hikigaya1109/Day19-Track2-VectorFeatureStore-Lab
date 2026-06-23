"""Standalone NB3 benchmark — runs against the already-started API server."""
import json
import time

import httpx

DATA = "data"
URL = "http://localhost:8000"
golden = [json.loads(l) for l in open(f"{DATA}/golden_set.jsonl", encoding="utf-8")]


def percentile(values, p):
    n = len(values)
    if n == 0:
        return 0.0
    return sorted(values)[min(int(n * p), n - 1)]


def benchmark_mode(mode, reps=2):
    server_latencies, wall_latencies = [], []
    for _ in range(reps):
        for q in golden:
            t0 = time.perf_counter()
            r = httpx.get(f"{URL}/search", params={"q": q["query"], "mode": mode})
            wall_latencies.append((time.perf_counter() - t0) * 1000)
            server_latencies.append(r.json()["latency_ms"])
    return {
        "p50_server": percentile(server_latencies, 0.50),
        "p95_server": percentile(server_latencies, 0.95),
        "p99_server": percentile(server_latencies, 0.99),
        "p99_wall": percentile(wall_latencies, 0.99),
    }


# Warmup
print("Running warmup (10 hybrid queries)...")
for q in golden[:10]:
    httpx.get(f"{URL}/search", params={"q": q["query"], "mode": "hybrid"})
print("Warmup done\n")

# Single query sample
r = httpx.get(
    f"{URL}/search",
    params={"q": "cloud computing tu dong mo rong", "mode": "hybrid"},
)
body = r.json()
print(f"Single query (hybrid):")
print(f"  latency_ms: {body['latency_ms']:.1f}")
print("  top-3 hits:")
for h in body["hits"][:3]:
    print(f"    {h['doc_id']:>14}  score={h['score']:.4f}  {h['title']}")

# Benchmark 3 modes
print()
print(f"  {'mode':10}  {'P50':>7}  {'P95':>7}  {'P99':>7}  {'P99-wall':>9}")
results = {}
for mode in ("keyword", "semantic", "hybrid"):
    res = benchmark_mode(mode)
    results[mode] = res
    print(
        f"  {mode:10}  {res['p50_server']:>5.1f}ms"
        f"  {res['p95_server']:>5.1f}ms"
        f"  {res['p99_server']:>5.1f}ms"
        f"  {res['p99_wall']:>7.1f}ms"
    )

hybrid_p99 = results["hybrid"]["p99_server"]
print()
if hybrid_p99 < 50:
    print(f"PASS -- hybrid P99 < 50ms ({hybrid_p99:.1f}ms)")
else:
    print(f"WARN -- hybrid P99 >= 50ms ({hybrid_p99:.1f}ms)")

with open("nb3_results.json", "w") as f:
    json.dump(results, f, indent=2)
print("\nResults saved to nb3_results.json")
