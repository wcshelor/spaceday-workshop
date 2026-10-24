#!/usr/bin/env python3
"""Measure a frozen description bank's coverage; concentration is not accuracy.

No encoder or network needed. Example:
python scripts/audit_description_bank.py --output docs/diagnostics/prompts-v3
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Output prefix for JSON and CSV")
    parser.add_argument("--method", choices=["raw", "standardized"], default="standardized")
    args = parser.parse_args()
    import numpy as np
    from backend.app.config import settings
    from backend.app.data_store import DataStore

    store = DataStore(settings.data_dir, settings.scoring_artifact, settings.language_artifact)
    store.load()
    if store.prompt_embeddings is None:
        raise RuntimeError(store.description_error)
    audio = np.asarray(store.embeddings, dtype=np.float64)
    text = np.asarray(store.prompt_embeddings, dtype=np.float64)
    scores = audio @ text.T
    raw_scores = scores.copy()
    if args.method == "standardized":
        stds = raw_scores.std(axis=0)
        scores = np.divide(raw_scores - raw_scores.mean(axis=0), stds,
                           out=np.full_like(raw_scores, -np.inf), where=stds > 1e-8)
    ids = np.array([p["id"] for p in store.language_bank])
    valid = np.flatnonzero(np.isfinite(scores).all(axis=0))
    order = np.array([valid[np.lexsort((ids[valid], -row[valid]))] for row in scores])
    supported = [store.uuid_to_index[sid] for sid in store.collaborative.index] if store.collaborative else []
    rows = []
    for j, prompt in enumerate(store.language_bank):
        count = int(np.sum(order[:, 0] == j))
        rows.append({"id": prompt["id"], "text": prompt["text"], "category": prompt["category"],
                     "top1": count, "top1_percent": round(100 * count / len(audio), 2),
                     "top5": int(np.sum(order[:, :5] == j)), "top8": int(np.sum(order[:, :8] == j)),
                     "shared_pool_top1": int(np.sum(order[supported, 0] == j)),
                     "mean_score": float(raw_scores[:, j].mean()), "std_score": float(raw_scores[:, j].std())})
    rows.sort(key=lambda p: (-p["top1"], p["id"]))
    report = {"ranking_method": args.method,
              "scoring_version": store.description_scoring_id if args.method == "standardized" else "raw-cosine",
              "dataset_id": store.dataset_id, "prompt_version": store.language_meta["prompt_version"],
              "encoder_id": store.language_meta["encoder_id"],
              "prompt_bank_sha256": store.language_meta["prompt_bank_sha256"],
              "embeddings_sha256": store.language_meta["embeddings_sha256"],
              "audit_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "song_count": len(audio), "prompt_count": len(text), "shared_pool_count": len(supported),
              "unique_first_place_prompts": int(len(set(order[:, 0]))),
              "note": "Counts measure coverage, not musical accuracy. Mean/std columns describe raw cosine. Top-eight counts precede paraphrase diversification.",
              "prompts": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.with_suffix(".json").write_text(json.dumps(report, indent=2) + "\n")
    with args.output.with_suffix(".csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps({k: v for k, v in report.items() if k != "prompts"}, indent=2))
    print(json.dumps(rows[:10], indent=2))


if __name__ == "__main__":
    main()
