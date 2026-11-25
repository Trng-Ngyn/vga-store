import concurrent.futures
import json
import statistics
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

BASE_API = "http://localhost:8080"
BASE_USER = "http://localhost:5173"
BASE_ADMIN = "http://localhost:5174"


def hit_url(url: str, timeout: float = 10.0):
    start = time.perf_counter()
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            _ = resp.read()
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return resp.status, elapsed_ms, None
    except urllib.error.HTTPError as e:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return e.code, elapsed_ms, str(e)
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000.0
        return 0, elapsed_ms, str(e)


def percentile(sorted_vals, pct):
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * (pct / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    return sorted_vals[f] + (sorted_vals[c] - sorted_vals[f]) * (k - f)


def run_scenario(name: str, url: str, concurrency: int, total_requests: int):
    t0 = time.perf_counter()
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as ex:
        futures = [ex.submit(hit_url, url) for _ in range(total_requests)]
        for fut in concurrent.futures.as_completed(futures):
            results.append(fut.result())
    wall_s = time.perf_counter() - t0

    latencies = sorted(r[1] for r in results)
    ok_count = sum(1 for r in results if 200 <= r[0] < 300)
    err_count = len(results) - ok_count
    return {
        "scenario": name,
        "url": url,
        "concurrency_vu": concurrency,
        "total_requests": total_requests,
        "success_count": ok_count,
        "error_count": err_count,
        "error_rate_pct": round(err_count * 100.0 / total_requests, 2),
        "duration_s": round(wall_s, 3),
        "throughput_rps": round(total_requests / wall_s, 2) if wall_s > 0 else 0,
        "min_ms": round(min(latencies), 2),
        "avg_ms": round(statistics.mean(latencies), 2),
        "p50_ms": round(percentile(latencies, 50), 2),
        "p95_ms": round(percentile(latencies, 95), 2),
        "p99_ms": round(percentile(latencies, 99), 2),
        "max_ms": round(max(latencies), 2),
    }


def main():
    scenarios = [
        ("LOAD-01: GET /api/products (Catalog Browse - 10 VUs)", f"{BASE_API}/api/products?page=0&size=10", 10, 100),
        ("LOAD-02: GET /api/products (Peak Load - 25 VUs)", f"{BASE_API}/api/products?page=0&size=10", 25, 150),
        ("LOAD-03: GET /api/products/search?keyWord=RTX (15 VUs)", f"{BASE_API}/api/products/search?keyWord=RTX&page=0&size=10", 15, 120),
        ("LOAD-04: GET /api/products/filter?minPrice=5M..60M (15 VUs)", f"{BASE_API}/api/products/filter?minPrice=5000000&maxPrice=60000000&page=0&size=10", 15, 120),
        ("LOAD-05: GET /api/categories & /api/brands Warmup (20 VUs)", f"{BASE_API}/api/brands?page=0&size=10", 20, 120),
        ("LOAD-06: GET Frontend User Portal (20 VUs)", f"{BASE_USER}/", 20, 100),
        ("LOAD-07: GET Frontend Admin Portal (15 VUs)", f"{BASE_ADMIN}/", 15, 80),
    ]

    report = {
        "executed_at": datetime.now().isoformat(),
        "scenarios": []
    }
    for name, url, vu, reqs in scenarios:
        res = run_scenario(name, url, vu, reqs)
        report["scenarios"].append(res)
        print(f"{res['scenario']}: {res['success_count']}/{res['total_requests']} OK | avg={res['avg_ms']}ms | p95={res['p95_ms']}ms | max={res['max_ms']}ms | RPS={res['throughput_rps']}")

    out_path = Path(__file__).resolve().parent / "performance_results.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Saved -> {out_path}")


if __name__ == "__main__":
    main()
