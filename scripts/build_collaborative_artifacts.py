"""Build a small, reproducible collaborative SVD model from real ListenBrainz loves.

Preparation only: pandas, pyarrow, scipy, numpy. Runtime needs only numpy.
No listener identifiers are written to the deployable artifacts.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json

import numpy as np
import pandas as pd
from scipy import sparse
from scipy.sparse.linalg import svds

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "https://data.metabrainz.org/pub/musicbrainz/listenbrainz/sample/listenbrainz-sample-20250610-094311-full/listenbrainz-sample-dump-20250610-094311.tar.zst"
SEED = 20261023


def fit(matrix, dimensions=32):
    # TF-IDF weighting reduces dominance by heavily represented songs/listeners.
    counts = np.asarray(matrix.sum(axis=0)).ravel()
    idf = np.log1p(matrix.shape[0] / np.maximum(counts, 1))
    weighted = matrix.multiply(idf).tocsr()
    norms = np.sqrt(np.asarray(weighted.power(2).sum(axis=1)).ravel())
    weighted = sparse.diags(1 / np.maximum(norms, 1e-12)) @ weighted
    k = min(dimensions, min(weighted.shape) - 1)
    _, singular, vt = svds(weighted, k=k, random_state=SEED)
    order = np.argsort(singular)[::-1]
    factors = vt[order].T * np.sqrt(singular[order])
    norms = np.linalg.norm(factors, axis=1, keepdims=True)
    return (factors / np.maximum(norms, 1e-12)).astype("<f4")


def evaluate(matrix, item_ids, workshop_ids):
    """Hide one workshop love per eligible listener; score using <=5 other loves.

    Held-out loves are removed BEFORE fitting. Compare with train-only popularity
    over the same supported workshop candidates; exclude seeds from both rankings.
    This random split measures reconstruction, not future listening satisfaction.
    """
    rng = np.random.default_rng(SEED)
    lookup = {mbid: i for i, mbid in enumerate(item_ids)}
    pool = np.array([lookup[m] for m in workshop_ids if m in lookup])
    pool_set = set(pool)
    train = matrix.tolil(copy=True)
    cases = []
    for user in range(matrix.shape[0]):
        loved = [i for i in matrix[user].indices if i in pool_set]
        if len(loved) >= 3:
            rng.shuffle(loved)
            target, seeds = loved[0], loved[1:6]
            train[user, target] = 0
            cases.append((target, seeds))
    train = train.tocsr()
    train.eliminate_zeros()
    counts = np.asarray(train.sum(axis=0)).ravel()
    supported = pool[counts[pool] >= 5]
    factors = fit(train)
    metrics = {"svd": [], "popularity": []}
    for target, seeds in cases:
        if target not in supported or any(counts[s] < 5 for s in seeds):
            continue
        candidates = supported[~np.isin(supported, seeds)]
        scores = factors[candidates] @ factors[seeds].mean(axis=0)
        for name, values in [("svd", scores), ("popularity", counts[candidates])]:
            # Candidate ordering is sorted MBID, used as deterministic tie break.
            top = candidates[np.argsort(-values, kind="stable")[:10]]
            position = np.flatnonzero(top == target)
            metrics[name].append((bool(position.size), 1 / np.log2(position[0] + 2) if position.size else 0.0))
    return {
        "protocol": "One held-out workshop love per listener with >=3 workshop loves; 1-5 seeds; fit after removal; same >=5-training-listener candidate pool; seed exclusion; fixed random split, not temporal.",
        "cases": len(metrics["svd"]),
        "candidate_songs": len(supported),
        "results": {name: {"hit_rate_at_10": float(np.mean([v[0] for v in rows])) if rows else None,
                            "ndcg_at_10": float(np.mean([v[1] for v in rows])) if rows else None}
                    for name, rows in metrics.items()},
    }


def build(source, out):
    songs = json.loads((ROOT / "data/workshop/songs.json").read_text())
    data = pd.read_parquet(source)
    positive = data[data.feedback == 1].drop_duplicates(["user_id", "recording_mbid"])
    counts = positive.groupby("recording_mbid").user_id.nunique()
    raw_counts = counts.copy()
    # Keep useful surrounding items, rather than training only on our catalogue.
    filtered = positive[positive.recording_mbid.isin(counts[counts >= 5].index)]
    users = filtered.groupby("user_id").recording_mbid.nunique()
    filtered = filtered[filtered.user_id.isin(users[users >= 5].index)]
    counts = filtered.groupby("recording_mbid").user_id.nunique()
    filtered = filtered[filtered.recording_mbid.isin(counts[counts >= 5].index)]
    item_ids = sorted(filtered.recording_mbid.unique())
    user_ids = sorted(filtered.user_id.unique())
    item_index = {m: i for i, m in enumerate(item_ids)}
    user_index = {u: i for i, u in enumerate(user_ids)}
    matrix = sparse.csr_matrix((np.ones(len(filtered)),
                               (filtered.user_id.map(user_index), filtered.recording_mbid.map(item_index))),
                              shape=(len(user_ids), len(item_ids)))
    evaluation = evaluate(matrix, item_ids, sorted(s["recording_mbid"] for s in songs))
    factors = fit(matrix)
    trained_counts = np.asarray(matrix.sum(axis=0)).ravel()
    supported = sorted(s["recording_mbid"] for s in songs if s["recording_mbid"] in item_index)
    vectors = factors[[item_index[m] for m in supported]]
    out.mkdir(parents=True, exist_ok=True)
    vectors.tofile(out / "embeddings.f32")
    # Independent reference distributions for each seed count; no CLAP calibration reuse.
    rng = np.random.default_rng(SEED)
    tables = {}
    for seed_count in range(1, 6):
        reference = []
        for _ in range(512):
            seeds = rng.choice(len(supported), seed_count, replace=False)
            scores = vectors @ vectors[seeds].mean(axis=0)
            reference.extend(np.delete(scores, seeds).tolist())
        quantiles = np.linspace(0, 1, 1001)
        values = np.quantile(reference, quantiles)
        # Collapse equal quantiles so ties have a single reference percentile.
        unique = {}
        for value, q in zip(values, quantiles):
            unique.setdefault(float(value), min(99.9, round(float(q * 100), 1)))
        tables[str(seed_count)] = [[v, p] for v, p in unique.items()]
    coverage = []
    for song in songs:
        mbid = song["recording_mbid"]
        coverage.append({"recording_mbid": mbid, "title": song["title"], "artist": song["artist"],
                         "distinct_positive_listeners": int(raw_counts.get(mbid, 0)),
                         "training_listeners": int(trained_counts[item_index[mbid]]) if mbid in item_index else 0,
                         "supported": mbid in supported})
    with (out / "coverage.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(coverage[0])); writer.writeheader(); writer.writerows(coverage)
    meta = {
        "version": "collaborative-v1", "algorithm": "TF-IDF weighted, row-normalized truncated SVD; unit song factors V sqrt(S); mean seed cosine",
        "dimensions": vectors.shape[1], "recording_mbids": supported, "minimum_positive_listeners": 5,
        "source_url": SOURCE, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "source_snapshot": "2025-06-10", "license": "CC0-1.0", "random_seed": SEED,
        "catalogue_sha256": hashlib.sha256((ROOT / "data/workshop/songs.json").read_bytes()).hexdigest(),
        "embeddings_sha256": hashlib.sha256((out / "embeddings.f32").read_bytes()).hexdigest(),
        "coverage": {"catalogue": len(songs), "any_positive_feedback": sum(int(raw_counts.get(s["recording_mbid"], 0)) > 0 for s in songs),
                     "supported": len(supported)},
        "training": {"listeners": len(user_ids), "songs": len(item_ids), "positive_pairs": matrix.nnz},
        "identity_policy": "Exact recording MBID only. No title matching, redirects or canonical-version merging; coverage is a conservative lower bound for this sample, not all ListenBrainz.",
        "signal": "Explicit positive feedback (loves), not play counts. Dislikes are excluded; missing feedback is not a dislike.",
        "listener_counts": {m: int(trained_counts[item_index[m]]) for m in supported},
        "calibration_tables": tables, "evaluation": evaluation,
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")
    print(json.dumps({k: meta[k] for k in ["coverage", "training", "evaluation"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=ROOT / "data/sources/listenbrainz/recording_feedback.parquet")
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts/collaborative-v1")
    args = parser.parse_args()
    build(args.source, args.out)
