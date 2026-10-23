"""The capacity harness must generate and account for the load it reports."""
import importlib.util
from pathlib import Path
import threading
import time

import httpx

spec = importlib.util.spec_from_file_location(
    'workshop_benchmark', Path(__file__).resolve().parents[2] / 'scripts/benchmark_app.py')
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)


def test_mixed_phase_reaches_requested_concurrency():
    active = peak = calls = 0
    lock = threading.Lock()

    def task():
        nonlocal active, peak, calls
        with lock:
            active += 1
            calls += 1
            peak = max(peak, active)
        time.sleep(0.02)
        with lock:
            active -= 1
        return 0.02, 200, None

    timings, errors, _ = bench.run_phase('mixed', 30, lambda: [task] * 14)
    assert peak == 30
    assert len(timings) == calls == 90
    assert errors == 0


def test_sustained_collects_failures_finishing_after_deadline():
    def task():
        time.sleep(0.04)
        return 0.04, 500, None

    timings, errors, _ = bench.run_phase('sustained', 4, lambda: task, duration=0.01)
    assert len(timings) == errors == 4


def test_only_disabled_text_response_is_expected():
    disabled = httpx.Response(503, json={'detail': 'Live encoder disabled'})
    not_ready = httpx.Response(503, json={'detail': 'Data not ready'})
    assert bench.expected_disabled_text('text', 503, disabled, 'disabled')
    assert not bench.expected_disabled_text('text', 503, not_ready, 'disabled')
    assert not bench.expected_disabled_text('text', 503, disabled, 'live')
    assert not bench.expected_disabled_text('rec_1_texture-v1', 503, disabled, 'disabled')


def test_bootstrap_rejects_unready_server():
    def handler(request):
        return httpx.Response(503, json={'status': 'not_ready'})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        import pytest
        with pytest.raises(httpx.HTTPStatusError):
            bench.fetch_bootstrap(client)
