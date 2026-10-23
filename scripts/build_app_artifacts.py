#!/usr/bin/env python3
"""
Build scoring-v1 artifacts: robust-scaled transformed matrices, normalisers, and percentile calibration.
Implements IMPLEMENTATION_PLAN §5.
"""
from __future__ import annotations
import json, hashlib, math, random
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data" / "workshop"
CONFIG_PATH = ROOT / "config" / "scoring-v1.json"
OUT_DIR = ROOT / "artifacts" / "scoring-v1"

def load_json(p: Path):
    return json.loads(p.read_text())

def robust_stats(values: list[float]):
    s = sorted(values)
    n = len(s)
    med = s[n//2] if n%2==1 else (s[n//2-1]+s[n//2])/2
    q1 = s[n//4]
    q3 = s[3*n//4]
    iqr = q3 - q1
    if abs(iqr) < 1e-9:
        iqr = 1.0
    return med, iqr

def main():
    print("=== Build scoring-v1 artifacts ===")
    manifest = load_json(DATA_DIR / "manifest.json")
    features = load_json(DATA_DIR / "features.json")
    songs = load_json(DATA_DIR / "songs.json")
    config = load_json(CONFIG_PATH)

    # Verify dataset
    canon = json.dumps(manifest, sort_keys=True).encode()
    dataset_hash = hashlib.sha256(canon).hexdigest()[:16]
    pipeline = manifest["pipeline_version"]

    # --- Rhythm recipe: log2 BPM, log1p onset, log1p danceability ---
    bpm_raw = [math.log2(f["measurements"]["rhythm.bpm"]) for f in features.values()]
    onset_raw = [math.log1p(f["measurements"]["rhythm.onset_rate"]) for f in features.values()]
    dance_raw = [math.log1p(f["measurements"]["rhythm.danceability"]) for f in features.values()]

    rhythm_meds = {
        "log2_bpm": {"median": robust_stats(bpm_raw)[0], "iqr": robust_stats(bpm_raw)[1]},
        "log1p_onset": {"median": robust_stats(onset_raw)[0], "iqr": robust_stats(onset_raw)[1]},
        "log1p_dance": {"median": robust_stats(dance_raw)[0], "iqr": robust_stats(dance_raw)[1]},
    }
    # quick outlier check
    clip = config["rhythm"]["clip"]

    # --- Texture recipe ---
    # MFCC mean 1..12
    mfcc_raw_by_dim = [ [] for _ in range(12) ]
    for f in features.values():
        mfcc = f["measurements"]["lowlevel.mfcc.mean"][1:]  # 12
        for i, v in enumerate(mfcc):
            mfcc_raw_by_dim[i].append(v)
    centroid_raw = [math.log(max(1e-6, f["measurements"]["lowlevel.spectral_centroid.mean"])) for f in features.values()]
    rolloff_raw = [math.log(max(1e-6, f["measurements"]["lowlevel.spectral_rolloff.mean"])) for f in features.values()]
    flux_raw = [math.log(max(1e-6, f["measurements"]["lowlevel.spectral_flux.mean"])) for f in features.values()]
    zcr_raw = [math.log1p(f["measurements"]["lowlevel.zerocrossingrate.mean"]) for f in features.values()]

    texture_meds = {
        "mfcc": [{"median": robust_stats(col)[0], "iqr": robust_stats(col)[1], "index": i+1} for i, col in enumerate(mfcc_raw_by_dim)],
        "spectral": {
            "centroid": {"median": robust_stats(centroid_raw)[0], "iqr": robust_stats(centroid_raw)[1], "transform": "log_floor_1e-6"},
            "rolloff": {"median": robust_stats(rolloff_raw)[0], "iqr": robust_stats(rolloff_raw)[1], "transform": "log_floor_1e-6"},
            "flux": {"median": robust_stats(flux_raw)[0], "iqr": robust_stats(flux_raw)[1], "transform": "log_floor_1e-6"},
            "zcr": {"median": robust_stats(zcr_raw)[0], "iqr": robust_stats(zcr_raw)[1], "transform": "log1p"},
        }
    }

    # Check zero IQR handling
    dropped = []
    for key, v in list(rhythm_meds.items()):
        if abs(v["iqr"]) < 1e-9:
            dropped.append(key)
    # texture similarly – none expected
    # Persist transformed matrices? For now persist normalisers and a small human readable summary
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "version": "scoring-v1",
        "dataset_hash": dataset_hash,
        "dataset_snapshot": manifest["source_snapshot"],
        "pipeline_version": pipeline,
        "config_path": "config/scoring-v1.json",
        "config_sha256": hashlib.sha256(CONFIG_PATH.read_bytes()).hexdigest(),
        "clip": clip,
        "rhythm": {
            "features": ["rhythm.bpm", "rhythm.onset_rate", "rhythm.danceability"],
            "transforms": {"rhythm.bpm": "log2", "rhythm.onset_rate": "log1p", "rhythm.danceability": "log1p"},
            "medians": rhythm_meds,
            "group_weights": config["rhythm"]["group_weights"],
            "feature_order": ["log2_bpm", "log1p_onset", "log1p_dance"],
            "dropped_dimensions": dropped,
        },
        "texture": {
            "mfcc_exclude_0": True,
            "coefficient_count": 12,
            "medians": texture_meds,
            "group_weights": config["texture"]["group_weights"],
            "spectral_floor": config["texture"]["spectral_floor"],
            "feature_order": ["mfcc_1..12", "centroid", "rolloff", "flux", "zcr"],
        },
        "notes": "Robust (median/IQR) scaling on full frozen collection; clip ±4; no per-filter refit; missing required input fails.",
    }
    (OUT_DIR / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"Wrote {OUT_DIR / 'meta.json'}")

    # --- Also produce a summary markdown ---
    summary = f"""# Scoring v1 artifact summary
- Dataset: {dataset_hash} ({manifest['source_snapshot']})
- Pipeline: {pipeline}
- Songs: 1500
- Rhythm medians: bpm log2 median {rhythm_meds['log2_bpm']['median']:.3f} IQR {rhythm_meds['log2_bpm']['iqr']:.3f}
- Clip: ±{clip}
- MFCC dims: 12 (coeff 0 excluded)
- Spectral floor: {config['texture']['spectral_floor']}
"""
    (OUT_DIR / "SUMMARY.md").write_text(summary)

    # --- Calibration: generate reference distributions per §5.4 ---
    # Need numpy for embeddings; fallback pure python if missing
    try:
        import numpy as np
        has_np = True
    except ImportError:
        has_np = False
        print("numpy not available, skipping calibration generation – install numpy to produce calibration.json")
        return

    emb_path = DATA_DIR / "clap_embeddings.f32"
    mat = np.fromfile(str(emb_path), dtype="<f4").reshape(1500, 512)
    # Verify unit norms already
    # Build per-method base score distributions

    # For rhythm/texture, need computed negative distances – we compute on the fly using same logic as scoring.py
    # To avoid duplicating, reimplement simple transforms here

    # Helper to compute scaled rhythm matrix (1500 x 3)
    def scale(x, med, iqr):
        s = (x - med)/iqr
        return max(-clip, min(clip, s))

    rhythm_mat = []
    for f in features.values():
        # features is keyed by mbid unordered – need to map via songs order
        pass

    # Instead build per mbid map and iterate songs order for determinism
    mbid_to_feat = features
    rhythm_vectors = {}
    texture_vectors = {}
    for rec in songs:
        mbid = rec["recording_mbid"]
        feats = mbid_to_feat[mbid]["measurements"]
        # rhythm
        bpm = math.log2(feats["rhythm.bpm"])
        onset = math.log1p(feats["rhythm.onset_rate"])
        dance = math.log1p(feats["rhythm.danceability"])
        rv = [
            scale(bpm, rhythm_meds["log2_bpm"]["median"], rhythm_meds["log2_bpm"]["iqr"]),
            scale(onset, rhythm_meds["log1p_onset"]["median"], rhythm_meds["log1p_onset"]["iqr"]),
            scale(dance, rhythm_meds["log1p_dance"]["median"], rhythm_meds["log1p_dance"]["iqr"]),
        ]
        rhythm_vectors[mbid] = rv
        # texture
        mfcc = feats["lowlevel.mfcc.mean"][1:]
        cent = math.log(max(1e-6, feats["lowlevel.spectral_centroid.mean"]))
        roll = math.log(max(1e-6, feats["lowlevel.spectral_rolloff.mean"]))
        flux = math.log(max(1e-6, feats["lowlevel.spectral_flux.mean"]))
        zcr = math.log1p(feats["lowlevel.zerocrossingrate.mean"])
        mfcc_scaled = []
        for i, coeff in enumerate(mfcc):
            med = texture_meds["mfcc"][i]["median"]
            iqr = texture_meds["mfcc"][i]["iqr"]
            mfcc_scaled.append(scale(coeff, med, iqr))
        spec_scaled = [
            scale(cent, texture_meds["spectral"]["centroid"]["median"], texture_meds["spectral"]["centroid"]["iqr"]),
            scale(roll, texture_meds["spectral"]["rolloff"]["median"], texture_meds["spectral"]["rolloff"]["iqr"]),
            scale(flux, texture_meds["spectral"]["flux"]["median"], texture_meds["spectral"]["flux"]["iqr"]),
            scale(zcr, texture_meds["spectral"]["zcr"]["median"], texture_meds["spectral"]["zcr"]["iqr"]),
        ]
        texture_vectors[mbid] = (mfcc_scaled, spec_scaled)

    # Precompute score distributions
    import itertools
    random_seed = config["calibration"]["random_seed"]
    samples_per_count = config["calibration"]["samples_per_count"]
    seed_counts = config["calibration"]["seed_counts"]

    # Map mbid -> index for CLAP
    mbid_to_idx = {r["recording_mbid"]: r["embedding_index"] for r in songs}
    idx_to_mbid = {v:k for k,v in mbid_to_idx.items()}
    all_mbids = [r["recording_mbid"] for r in songs]

    def per_seed_score(method, seed_mbid, cand_mbid):
        if method == "clap-v1":
            si = mbid_to_idx[seed_mbid]; ci = mbid_to_idx[cand_mbid]
            return float(np.dot(mat[si], mat[ci]))
        elif method == "rhythm-v1":
            sv = rhythm_vectors[seed_mbid]; cv = rhythm_vectors[cand_mbid]
            mse = sum((a-b)**2 for a,b in zip(sv,cv))/len(sv)
            return -mse
        elif method == "texture-v1":
            smfcc, sspec = texture_vectors[seed_mbid]
            cmfcc, cspec = texture_vectors[cand_mbid]
            mse_mfcc = sum((a-b)**2 for a,b in zip(smfcc, cmfcc))/len(smfcc)
            mse_spec = sum((a-b)**2 for a,b in zip(sspec, cspec))/len(sspec)
            return -(0.5*mse_mfcc + 0.5*mse_spec)
        else:
            raise ValueError(method)

    calibration_tables = {}
    checksums = {}

    # Build numpy matrices for vectorized calibration
    # rhythm_mat: 1500 x 3 ordered by songs
    rhythm_mat = np.array([rhythm_vectors[rec["recording_mbid"]] for rec in songs], dtype=np.float64)
    # texture: combine mfcc (12) + spectral (4) -> but scoring uses weighted groups; we compute effective distance via same function
    # For calibration we keep per-method vectorized distance using same weighting
    # texture_mat splits
    texture_mfcc_mat = np.array([texture_vectors[rec["recording_mbid"]][0] for rec in songs], dtype=np.float64)  # 1500x12
    texture_spec_mat = np.array([texture_vectors[rec["recording_mbid"]][1] for rec in songs], dtype=np.float64)  # 1500x4

    for method in ["rhythm-v1", "texture-v1", "clap-v1"]:
        method_tables = {}
        for k in seed_counts:
            if k == 1:
                if method == "clap-v1":
                    sim = mat @ mat.T
                    off = sim[~np.eye(1500, dtype=bool)]
                    scores = off.tolist()
                elif method == "rhythm-v1":
                    # pairwise negative MSE: compute via broadcasting (1500x1500)
                    # Use efficient cdist: ||a-b||^2 mean
                    # mse = mean((a-b)^2) = mean(a^2)+mean(b^2)-2*mean(a*b)? Simpler to loop blocks of 500 to keep memory low
                    scores = []
                    for i_start in range(0, 1500, 300):
                        i_end = min(1500, i_start+300)
                        block = rhythm_mat[i_start:i_end]  # Bx3
                        # compute distances to all (1500)
                        # diff shape Bx1500x3
                        diff = block[:, None, :] - rhythm_mat[None, :, :]  # Bx1500x3
                        mse = (diff**2).mean(axis=2)  # Bx1500
                        # mask diagonal for this block
                        for bi in range(i_end - i_start):
                            gi = i_start + bi
                            row = mse[bi]
                            # exclude self (gi)
                            row_filtered = np.delete(row, gi)
                            scores.extend((-row_filtered).tolist())
                    # scores length should be 1500*1499
                elif method == "texture-v1":
                    scores = []
                    for i_start in range(0, 1500, 300):
                        i_end = min(1500, i_start+300)
                        mfcc_b = texture_mfcc_mat[i_start:i_end]
                        spec_b = texture_spec_mat[i_start:i_end]
                        # compute mse_mfcc and mse_spec separately
                        diff_mfcc = mfcc_b[:, None, :] - texture_mfcc_mat[None, :, :]  # Bx1500x12
                        mse_mfcc = (diff_mfcc**2).mean(axis=2)
                        diff_spec = spec_b[:, None, :] - texture_spec_mat[None, :, :]  # Bx1500x4
                        mse_spec = (diff_spec**2).mean(axis=2)
                        combined = -(0.5*mse_mfcc + 0.5*mse_spec)
                        for bi in range(i_end - i_start):
                            gi = i_start + bi
                            row = combined[bi]
                            row_filtered = np.delete(row, gi)
                            scores.extend(row_filtered.tolist())
                else:
                    scores = []
                # Sort ascending
                scores_sorted = sorted(scores)
                n = len(scores_sorted)
                print(f"method={method} k={k} scores_len={n}")
                if n == 0:
                    print(f"EMPTY scores for {method} k={k}")
                    continue
                table = []
                for p in range(1001):
                    pct = p/10  # 0.0..100.0
                    idx = int(round(p/1000 * (n-1)))
                    if idx < 0: idx = 0
                    if idx >= n: idx = n-1
                    s = scores_sorted[idx]
                    table.append([float(s), float(pct)])
                method_tables[str(k)] = table
                checksums[f"{method}_{k}"] = hashlib.sha256(json.dumps(table).encode()).hexdigest()[:12]
            else:
                rng = random.Random(random_seed + k)
                ref_scores = []
                for _ in range(samples_per_count):
                    seed_set = rng.sample(all_mbids, k)
                    seed_set_set = set(seed_set)
                    for cand in all_mbids:
                        if cand in seed_set_set: continue
                        per = [per_seed_score(method, s, cand) for s in seed_set]
                        base = sum(per)/len(per)
                        ref_scores.append(base)
                ref_sorted = sorted(ref_scores)
                n = len(ref_sorted)
                print(f"method={method} k={k} ref_scores_len={n}")
                if n == 0:
                    print(f"EMPTY ref for {method} k={k}")
                    continue
                table = []
                for p in range(1001):
                    pct = p/10
                    idx = int(round(p/1000 * (n-1)))
                    if idx < 0: idx = 0
                    if idx >= n: idx = n-1
                    s = ref_sorted[idx]
                    table.append([float(s), float(pct)])
                method_tables[str(k)] = table
                checksums[f"{method}_{k}"] = hashlib.sha256(json.dumps(table).encode()).hexdigest()[:12]
        calibration_tables[method] = method_tables

    cal_out = {
        "version": "calibration-v1",
        "dataset_hash": dataset_hash,
        "scoring_version": "scoring-v1",
        "params": {
            "seed_counts": seed_counts,
            "samples_per_count": samples_per_count,
            "random_seed": random_seed,
            "table_resolution": "0.1 percentile, 1001 points per table",
            "handling": "tail capped at 99.9, ties equal percentile, filtering does not alter mapping",
        },
        "tables": calibration_tables,
        "checksums": checksums,
    }
    (OUT_DIR / "calibration.json").write_text(json.dumps(cal_out, indent=2))
    print(f"Wrote {OUT_DIR / 'calibration.json'} ({len(json.dumps(cal_out))//1024} KB)")
    # Write summary of clustering
    # Inspect top-result percentile clustering: compute per method median top-5 percentile
    for method in ["rhythm-v1","texture-v1","clap-v1"]:
        table = calibration_tables[method]["1"]
        print(f"{method} 1-seed: 90th={next(s for s,p in table if p>=90):.3f} 99th={next(s for s,p in table if p>=99):.3f}")

if __name__ == "__main__":
    main()
