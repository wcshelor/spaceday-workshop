from __future__ import annotations

import json
import math
from pathlib import Path

# Simple in-memory calibration fallback: if no artifact, use heuristic percentile mapping

_artifact_calibration = None

def load_calibration(data_store):
    global _artifact_calibration
    if _artifact_calibration is not None:
        return _artifact_calibration
    cal_path = data_store.scoring_dir / "calibration.json"
    if cal_path.exists():
        _artifact_calibration = json.loads(cal_path.read_text())
        return _artifact_calibration
    return None

def percentile_for_score(data_store, method: str, seed_count: int, score: float) -> float:
    """
    Returns percentile 0..100 (rounded to 1 decimal but we return precise).
    If calibration artifact exists, use table; else use heuristic mapping.
    Monotone, handles ties equally via interpolation on sorted table.
    """
    if method == "collaborative-v1":
        if data_store.collaborative is None:
            raise RuntimeError("Listener patterns model is not installed")
        return data_store.collaborative.percentile(seed_count, score)
    cal = load_calibration(data_store)
    if cal is None:
        # Heuristic: map method-specific ranges to percentiles
        # For CLAP: cosine [-1,1] -> roughly 0..100, 0.3 median maybe 50%
        # For rhythm/texture: negative distances, e.g. -0..-... map
        if method == "clap-v1":
            # pretend distribution: linear map clipped
            # score 0 -> 40%, 0.2->60%, 0.4->85%, 0.8->99%
            # Use logistic approximation
            # (score+1)/2*100 with compression
            pct = (score + 1) * 50  # -1->0, 1->100
            # adjust skewed: real distribution is tighter around 0.1-0.3
            # compress tails
            pct = max(0.0, min(99.9, pct))
            # To make useful: map 0.1->~30, 0.3->70 etc using piecewise
            # For heuristic fallback, just clamp and round
            return round(min(99.9, max(0.0, pct)), 1)
        else:
            # rhythm/texture negative mse: closer to 0 is higher
            # e.g. -0 -> 99.9, -1 -> 50, -4 -> 5
            # Use exponential
            # pct = 100 * exp(score)  where score negative
            pct = 100 * math.exp(score)  # score 0->100, -1->36, -2->13
            pct = max(0.0, min(99.9, pct))
            return round(pct, 1)
    # With artifact: tables per method and seed_count
    # Expected shape: {"tables": {"clap-v1": {"1": [[score, pct], ...]}}}
    tables = cal.get("tables", {})
    method_table = tables.get(method, {})
    points = method_table.get(str(seed_count)) or method_table.get("1")
    if not points:
        return 50.0
    # points sorted by score ascending
    # find percentile via linear interpolation, monotone, ties equal
    # scores ascending, percentiles ascending
    # score may be outside range: clamp to 0 or 99.9
    if score <= points[0][0]:
        return min(99.9, float(points[0][1]))
    if score >= points[-1][0]:
        return min(99.9, float(points[-1][1]))
    # binary search
    lo, hi = 0, len(points)-1
    while lo < hi - 1:
        mid = (lo+hi)//2
        if points[mid][0] <= score:
            lo = mid
        else:
            hi = mid
    # now points[lo].score <= score < points[hi].score
    # handle equal scores segment: find equal-score range and return same percentile (lower)
    if points[lo][0] == points[hi][0]:
        return float(points[lo][1])
    # linear interpolate
    s0, p0 = points[lo]
    s1, p1 = points[hi]
    t = (score - s0) / (s1 - s0) if s1 != s0 else 0
    pct = p0 + t * (p1 - p0)
    # cap non-self at 99.9
    pct = min(99.9, max(0.0, pct))
    return round(float(pct), 1)
