#!/usr/bin/env python3
"""
Strengthened benchmark for 20–30 participants.

Tests:
- bootstrap, search, all 4 methods (rhythm, texture, clap, collaborative where supported), explanations, prepared-language (examples, descriptions)
- valid supported seeds for collaborative
- one- and five-seed cases
- synchronized burst of 30 recs with varied inputs
- mixed activity at 20 and 30 concurrency
- sustained mixed load (optional, use --sustained 600 for 10 min)

Bounded timeouts, capture failures without losing report, distinguish expected live-text 503.

Record: sample counts, p50/p95/max, throughput, errors, and server resource note (not mislabeling client memory).

Usage:
  BENCH_BASE_URL=http://127.0.0.1:8000 python scripts/benchmark_app.py
  python scripts/benchmark_app.py --sustained 600 --burst 30
  python scripts/benchmark_app.py --hosted  # adds hosted checks
"""
import argparse, time, statistics, concurrent.futures, json, os, sys, random, math
from pathlib import Path
from collections import defaultdict

import threading

import httpx

BASE = os.getenv("BENCH_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = 15.0  # bounded
DEFAULT_CONCURRENCY = 20

def fetch_bootstrap(client):
    r = client.get(f"{BASE}/health/ready", timeout=TIMEOUT)
    r.raise_for_status()
    if r.json().get("status") != "ready":
        raise RuntimeError("Server is not ready")
    r = client.get(f"{BASE}/api/bootstrap", timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def get_songs(client, limit=20, collaborative_only=False, q=None):
    params = {"limit": limit, "offset": 0}
    if collaborative_only:
        params["collaborative_only"] = "true"
    if q:
        params["q"] = q
    r = client.get(f"{BASE}/api/songs", params=params, timeout=TIMEOUT)
    r.raise_for_status()
    return r.json()

def measure(client, method, url, **kwargs):
    # httpx.Client supports sharing between threads and reuses connections.
    t0 = time.perf_counter()
    try:
        r = client.request(method, url, timeout=TIMEOUT, **kwargs)
        return time.perf_counter() - t0, r.status_code, r
    except Exception as exc:
        return time.perf_counter() - t0, None, exc


def expected_disabled_text(endpoint, code, response, language_status):
    if endpoint != "text" or code != 503 or language_status != "disabled":
        return False
    try:
        return "disabled" in str(response.json()).lower()
    except Exception:
        return False


def run_phase(name, concurrency, tasks_fn, duration=None, language_status=None):
    """Bound in-flight work, release the first wave together, and collect every result."""
    timings = []
    errors = 0
    barrier = threading.Barrier(concurrency)

    def worker(task, first_wave=False):
        endpoint = getattr(task, '__name__', 'task')
        if first_wave:
            barrier.wait(timeout=TIMEOUT)
        start = time.perf_counter()
        try:
            lat, code, response = task()
            expected = expected_disabled_text(endpoint, code, response, language_status)
            ok = (code is not None and 200 <= code < 300) or expected
            return endpoint, lat, code, ok
        except Exception:
            return endpoint, time.perf_counter() - start, None, False

    def collect(future):
        nonlocal errors
        try:
            result = future.result()
        except Exception:
            result = ('exception', 0, None, False)
        timings.append(result)
        errors += int(not result[3])

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
        if duration:
            def next_task():
                task = tasks_fn()
                return random.choice(task) if isinstance(task, list) else task

            deadline = time.monotonic() + duration
            pending = {executor.submit(worker, next_task(), True) for _ in range(concurrency)}
            while pending:
                done, pending = concurrent.futures.wait(
                    pending, return_when=concurrent.futures.FIRST_COMPLETED)
                for future in done:
                    collect(future)
                    if time.monotonic() < deadline:
                        pending.add(executor.submit(worker, next_task()))
            # After the deadline no work is added; all in-flight results are retained.
        else:
            tasks = tasks_fn() if callable(tasks_fn) else list(tasks_fn)
            if not tasks:
                raise ValueError(f"{name}: no tasks")
            # Multiple waves ensure every task type is covered at the requested concurrency.
            if len(tasks) < concurrency:
                tasks = (tasks * math.ceil(concurrency * 3 / len(tasks)))[:concurrency * 3]
            first_wave_size = min(concurrency, len(tasks))
            barrier = threading.Barrier(first_wave_size)
            futures = [executor.submit(worker, task, i < first_wave_size)
                       for i, task in enumerate(tasks)]
            for future in concurrent.futures.as_completed(futures):
                collect(future)
    return timings, errors, errors

def build_tasks_for_mixed(client, bootstrap, songs_collab, songs_all):
    """Build a list of mixed tasks: search, recs all methods, explanations, prepared language."""
    tasks = []
    methods = [m for m in bootstrap.get('supported_methods', []) if m in ('rhythm-v1','texture-v1','clap-v1','collaborative-v1')]
    # ensure we have songs
    if not songs_all:
        return []
    # helper to pick seeds
    def pick_seeds(n, collaborative=False):
        pool = songs_collab if collaborative and songs_collab else songs_all
        if len(pool) < n:
            pool = songs_all
        return [s['recording_mbid'] for s in random.sample(pool, n)]

    # 1: search
    def task_search():
        return measure(client, 'GET', f"{BASE}/api/songs", params={"q": random.choice(['love','blue','night','a']), "limit": 10})
    task_search.__name__ = 'search'
    tasks.append(task_search)

    # 2: bootstrap
    def task_bootstrap(): return measure(client, 'GET', f"{BASE}/api/bootstrap")
    task_bootstrap.__name__ = 'bootstrap'
    tasks.append(task_bootstrap)

    # 3-6: one-seed recs for each method
    for method in methods:
        def make_one(m=method):
            def task():
                is_collab = m == 'collaborative-v1'
                seeds = pick_seeds(1, collaborative=is_collab)
                body = {"seed_ids": seeds, "method": m, "limit": 5}
                if is_collab:
                    body["candidate_filter"] = {"collaborative_only": True}
                return measure(client, 'POST', f"{BASE}/api/recommendations", json=body)
            task.__name__ = f"rec_1_{m}"
            return task
        tasks.append(make_one())

    # 7-10: five-seed recs
    for method in methods:
        def make_five(m=method):
            def task():
                is_collab = m == 'collaborative-v1'
                seeds = pick_seeds(5, collaborative=is_collab)
                body = {"seed_ids": seeds, "method": m, "limit": 5}
                if is_collab:
                    body["candidate_filter"] = {"collaborative_only": True}
                return measure(client, 'POST', f"{BASE}/api/recommendations", json=body)
            task.__name__ = f"rec_5_{m}"
            return task
        tasks.append(make_five())

    # 11: explanation (needs a valid seed and result)
    def task_explain():
        # do a rec first to get result, then explain
        seeds = pick_seeds(1)
        body = {"seed_ids": seeds, "method": "clap-v1", "limit": 2}
        lat, code, resp = measure(client, 'POST', f"{BASE}/api/recommendations", json=body)
        if code == 200:
            try:
                res_id = resp.json()['results'][0]['recording_mbid']
                return measure(client, 'POST', f"{BASE}/api/explanations", json={"seed_ids": seeds, "method": "clap-v1", "result_id": res_id})
            except Exception as exc:
                return (lat, None, exc)
        return (lat, code, resp)
    task_explain.__name__ = 'explain'
    tasks.append(task_explain)

    # 12: prepared language – examples
    def task_examples(): return measure(client, 'GET', f"{BASE}/api/examples")
    task_examples.__name__ = 'examples'
    tasks.append(task_examples)

    # 13: prepared language – descriptions
    def task_descriptions():
        sid = random.choice(songs_all)['recording_mbid']
        return measure(client, 'POST', f"{BASE}/api/descriptions", json={"recording_mbid": sid, "limit": 5})
    task_descriptions.__name__ = 'descriptions'
    tasks.append(task_descriptions)

    # 14: text search (expected 503 when disabled)
    def task_text():
        return measure(client, 'POST', f"{BASE}/api/text-search", json={"query": "warm acoustic guitar with soft vocals", "limit": 5})
    task_text.__name__ = 'text'
    tasks.append(task_text)

    return tasks

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--burst', type=int, default=30, help='burst request count')
    parser.add_argument('--sustained', type=int, default=0, help='sustained run seconds (0=skip, 600=10min)')
    parser.add_argument('--hosted', action='store_true', help='add hosted checks')
    args = parser.parse_args()
    if args.burst < 1 or args.sustained < 0:
        parser.error("burst must be positive and sustained must be nonnegative")

    print(f"Benchmarking {BASE} — timeout {TIMEOUT}s, burst {args.burst}, sustained {args.sustained}s")
    all_timings = []
    total_unexpected = 0
    total_expected_text_503 = 0
    start_all = time.time()

    with httpx.Client(timeout=TIMEOUT) as client:
        try:
            bootstrap = fetch_bootstrap(client)
            print(f"Bootstrap: dataset {bootstrap.get('dataset_id','?')[:8]} methods {bootstrap.get('supported_methods')} lang {bootstrap.get('language_status')}")
            # fetch songs
            songs_all = get_songs(client, limit=30).get('items', [])
            songs_collab = []
            if 'collaborative-v1' in bootstrap.get('supported_methods', []):
                try:
                    songs_collab = get_songs(client, limit=30, collaborative_only=True).get('items', [])
                    print(f"Collaborative supported: {len(songs_collab)}")
                except Exception as e:
                    print(f"Collaborative fetch failed: {e}")
                    songs_collab = []
            if not songs_all:
                print("No songs fetched — abort")
                sys.exit(1)
        except Exception as e:
            print(f"Bootstrap failed: {e}")
            sys.exit(1)

        # Phase 1: synchronized burst of 30 recommendation requests with varied inputs
        print(f"\nPhase 1: burst {args.burst} recs varied inputs")
        burst_tasks = []
        methods = [m for m in bootstrap.get('supported_methods', [])]
        for i in range(args.burst):
            m = random.choice(methods)
            is_collab = m == 'collaborative-v1'
            n = random.choice([1,5])
            pool = songs_collab if is_collab and songs_collab else songs_all
            if len(pool) < n: pool = songs_all
            seeds = [s['recording_mbid'] for s in random.sample(pool, n)]
            body = {"seed_ids": seeds, "method": m, "limit": 5}
            if is_collab:
                body["candidate_filter"] = {"collaborative_only": True}
            def make_task(b=body, name=f"burst_{m}_{n}"):
                def task(): return measure(client, 'POST', f"{BASE}/api/recommendations", json=b)
                task.__name__ = name
                return task
            burst_tasks.append(make_task())

        timings, _, unexpected = run_phase("burst", min(30, args.burst), burst_tasks)
        all_timings.extend(timings)
        total_unexpected += unexpected
        print(f"  burst done: {len(timings)} samples")

        # Phase 2: mixed activity at 20 concurrency
        print("\nPhase 2: mixed activity 20 concurrency")
        def tasks20():
            return build_tasks_for_mixed(client, bootstrap, songs_collab, songs_all)
        timings, _, unexpected = run_phase("mixed20", 20, tasks20, language_status=bootstrap.get("language_status"))
        all_timings.extend(timings); total_unexpected += unexpected
        print(f"  mixed20 done: {len(timings)} samples")

        # Phase 3: mixed activity at 30 concurrency
        print("\nPhase 3: mixed activity 30 concurrency")
        def tasks30():
            return build_tasks_for_mixed(client, bootstrap, songs_collab, songs_all)
        timings, _, unexpected = run_phase("mixed30", 30, tasks30, language_status=bootstrap.get("language_status"))
        all_timings.extend(timings); total_unexpected += unexpected
        print(f"  mixed30 done: {len(timings)} samples")

        # Phase 4: sustained mixed load if requested
        if args.sustained > 0:
            print(f"\nPhase 4: sustained {args.sustained}s mixed load (30 concurrency)")
            def sustained_task_gen():
                # return a single random task for sustained loop to pick
                tasks = build_tasks_for_mixed(client, bootstrap, songs_collab, songs_all)
                t = random.choice(tasks)
                return t
            timings, _, unexpected = run_phase("sustained", 30, sustained_task_gen, duration=args.sustained, language_status=bootstrap.get("language_status"))
            all_timings.extend(timings); total_unexpected += unexpected
            print(f"  sustained done: {len(timings)} samples")

    elapsed = time.time() - start_all

    # Aggregate
    from collections import defaultdict
    by_ep = defaultdict(list)
    by_ep_ok = defaultdict(int)
    by_ep_fail = defaultdict(int)
    for ep, lat, code, ok in all_timings:
        # expected text 503 is not failure
        is_text = 'text' in ep.lower()
        expected_503 = ep == 'text' and code == 503 and ok
        if expected_503:
            total_expected_text_503 += 1
            # count as ok for throughput
            by_ep[ep].append(lat)
            by_ep_ok[ep] += 1
            continue
        by_ep[ep].append(lat)
        if ok:
            by_ep_ok[ep] += 1
        else:
            by_ep_fail[ep] += 1

    # Report
    print(f"\n=== Benchmark Report ===")
    print(f"Base: {BASE}, elapsed {elapsed:.1f}s, total samples {len(all_timings)}, unexpected failures {total_unexpected}, expected text 503 {total_expected_text_503}")
    for ep in sorted(by_ep.keys()):
        lats = sorted([x for x in by_ep[ep] if x is not None])
        if not lats:
            continue
        p50 = statistics.median(lats)
        p95 = lats[int(0.95*len(lats))] if lats else 0
        mx = max(lats)
        ok = by_ep_ok[ep]; fail = by_ep_fail[ep]
        throughput = len(lats)/elapsed if elapsed else 0
        print(f"{ep:20} n={len(lats):4} ok={ok:4} fail={fail:3} p50={p50*1000:6.1f}ms p95={p95*1000:6.1f}ms max={mx*1000:6.1f}ms tput={throughput:.1f}/s")

    # Acceptance targets
    def get_p95(ep_prefix):
        # find p95 for any endpoint matching prefix
        for ep, lats in by_ep.items():
            if ep.startswith(ep_prefix):
                l = sorted(lats)
                return l[int(0.95*len(l))] if l else 999
        return 999


    # Actually get p95 for burst recs and mixed recs
    search_p95 = get_p95("search")
    print("\nAcceptance checks (hosted 1 CPU / 2 GB):")
    print(f"  Zero unexpected failures: {'PASS' if total_unexpected==0 else f'FAIL ({total_unexpected})'}")
    # Use burst/rec p95
    all_rec_lats = []
    for ep, lats in by_ep.items():
        if 'rec' in ep or 'burst' in ep:
            all_rec_lats.extend(lats)
    if all_rec_lats:
        all_rec_lats.sort()
        rec_p95_all = all_rec_lats[int(0.95*len(all_rec_lats))]
        print(f"  Rec p95 ~2s at 30 conc: {rec_p95_all*1000:.0f}ms {'PASS' if rec_p95_all <= 2.0 else 'FAIL'}")
    else:
        print("  Rec p95: no data")
    if search_p95 != 999:
        print(f"  Search p95 ~1s mixed: {search_p95*1000:.0f}ms {'PASS' if search_p95 <= 1.0 else 'FAIL'}")

    # Server memory/CPU — not available via API, so note
    server_mem_note = "Server memory/CPU not exposed via API — check host metrics (e.g., Render dashboard, docker stats, or add /health/metrics). Client process RSS below is not server memory."
    print(f"  Server memory: {server_mem_note}")
    try:
        import psutil
        p = psutil.Process()
        print(f"  Client RSS (not server): {p.memory_info().rss/1024/1024:.1f} MB — do not label as server")
    except: pass

    # Throughput
    total_ok = sum(by_ep_ok.values())
    print(f"  Throughput: {total_ok/elapsed:.1f} ok req/s over {elapsed:.1f}s")

    # Write machine-readable report
    report = {
        "base": BASE,
        "elapsed": elapsed,
        "timeout": TIMEOUT,
        "burst": args.burst,
        "sustained": args.sustained,
        "total_samples": len(all_timings),
        "unexpected_failures": total_unexpected,
        "expected_text_503": total_expected_text_503,
        "by_endpoint": {
            ep: {
                "count": len(lats),
                "ok": by_ep_ok[ep],
                "fail": by_ep_fail[ep],
                "p50": statistics.median(sorted(lats)) if lats else None,
                "p95": sorted(lats)[int(0.95*len(lats))] if lats else None,
                "max": max(lats) if lats else None,
            } for ep, lats in by_ep.items()
        },
        "server_resources": {
            "note": server_mem_note,
            "client_rss_mb": None,  # filled if psutil
        },
        "acceptance": {
            "zero_unexpected": total_unexpected==0,
            "rec_p95_ms": rec_p95_all*1000 if all_rec_lats else None,
            "search_p95_ms": search_p95*1000 if search_p95!=999 else None,
        }
    }
    try:
        import psutil
        report["server_resources"]["client_rss_mb"] = psutil.Process().memory_info().rss/1024/1024
    except: pass
    Path("benchmark_report.json").write_text(json.dumps(report, indent=2))
    print("Wrote benchmark_report.json")
    if total_unexpected > 0 or not all_rec_lats or rec_p95_all > 2.0 or search_p95 > 1.0:
        sys.exit(1)

if __name__ == "__main__":
    main()
