from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

try:
    import numpy as np
except ImportError:
    np = None


# Cache loaded artifacts globally
_ARTIFACTS = None

def _load_artifacts(data_store):
    global _ARTIFACTS
    if _ARTIFACTS is not None:
        return _ARTIFACTS
    # Try to load from scoring_dir/meta.json
    meta_path = data_store.scoring_dir / "meta.json"
    if not meta_path.exists():
        # No artifacts yet - use fallback computed normalisers on the fly (for dev)
        # compute simple stats directly from features
        feats = data_store.features
        # collect vectors for rhythm
        bpms = [math.log2(v["measurements"]["rhythm.bpm"]) for v in feats.values()]
        onsets = [math.log1p(v["measurements"]["rhythm.onset_rate"]) for v in feats.values()]
        dances = [math.log1p(v["measurements"]["rhythm.danceability"]) for v in feats.values()]
        # spectral etc
        centroids = [math.log(max(1e-6, v["measurements"]["lowlevel.spectral_centroid.mean"])) for v in feats.values()]
        rolloffs = [math.log(max(1e-6, v["measurements"]["lowlevel.spectral_rolloff.mean"])) for v in feats.values()]
        fluxes = [math.log(max(1e-6, v["measurements"]["lowlevel.spectral_flux.mean"])) for v in feats.values()]
        zcrs = [math.log1p(v["measurements"]["lowlevel.zerocrossingrate.mean"]) for v in feats.values()]
        mfccs = [v["measurements"]["lowlevel.mfcc.mean"][1:] for v in feats.values()]  # exclude 0
        # compute median and IQR
        def median_iqr(arr):
            s = sorted(arr)
            n = len(s)
            med = s[n//2] if n%2==1 else (s[n//2-1]+s[n//2])/2
            # simple IQR
            q1 = s[n//4]
            q3 = s[3*n//4]
            iqr = q3 - q1
            if abs(iqr) < 1e-9:
                iqr = 1.0
            return med, iqr
        # build per-dim normalisers
        _ARTIFACTS = {
            "rhythm_medians": {
                "bpm": median_iqr(bpms),
                "onset": median_iqr(onsets),
                "dance": median_iqr(dances),
            },
            "texture_medians": {
                "centroid": median_iqr(centroids),
                "rolloff": median_iqr(rolloffs),
                "flux": median_iqr(fluxes),
                "zcr": median_iqr(zcrs),
                "mfcc": [median_iqr([row[i] for row in mfccs]) for i in range(12)],
            },
            "clip": 4.0,
        }
        return _ARTIFACTS
    else:
        raw = json.loads(meta_path.read_text())
        # Normalize new meta.json shape to internal expected keys
        if "rhythm" in raw and "texture" in raw:
            # new format from build_app_artifacts
            _ARTIFACTS = {
                "rhythm_medians": {
                    "log2_bpm": [raw["rhythm"]["medians"]["log2_bpm"]["median"], raw["rhythm"]["medians"]["log2_bpm"]["iqr"]],
                    "log1p_onset": [raw["rhythm"]["medians"]["log1p_onset"]["median"], raw["rhythm"]["medians"]["log1p_onset"]["iqr"]],
                    "log1p_dance": [raw["rhythm"]["medians"]["log1p_dance"]["median"], raw["rhythm"]["medians"]["log1p_dance"]["iqr"]],
                },
                "texture_medians": {
                    "centroid": [raw["texture"]["medians"]["spectral"]["centroid"]["median"], raw["texture"]["medians"]["spectral"]["centroid"]["iqr"]],
                    "rolloff": [raw["texture"]["medians"]["spectral"]["rolloff"]["median"], raw["texture"]["medians"]["spectral"]["rolloff"]["iqr"]],
                    "flux": [raw["texture"]["medians"]["spectral"]["flux"]["median"], raw["texture"]["medians"]["spectral"]["flux"]["iqr"]],
                    "zcr": [raw["texture"]["medians"]["spectral"]["zcr"]["median"], raw["texture"]["medians"]["spectral"]["zcr"]["iqr"]],
                    "mfcc": [[m["median"], m["iqr"]] for m in raw["texture"]["medians"]["mfcc"]],
                },
                "clip": raw.get("clip", 4.0),
                "version": raw.get("version"),
            }
        else:
            _ARTIFACTS = raw
        return _ARTIFACTS


def _robust_scale(x, median, iqr, clip=4.0):
    s = (x - median) / iqr
    if s > clip: s = clip
    if s < -clip: s = -clip
    return s

def _rhythm_vector(data_store, mbid) -> list[float]:
    feats = data_store.features[mbid]["measurements"]
    arts = _load_artifacts(data_store)
    bpm = math.log2(feats["rhythm.bpm"])
    onset = math.log1p(feats["rhythm.onset_rate"])
    dance = math.log1p(feats["rhythm.danceability"])
    meds = arts["rhythm_medians"]
    # support both old keys (bpm/onset/dance) and new (log2_bpm etc)
    key_map = {"bpm": "log2_bpm", "onset": "log1p_onset", "dance": "log1p_dance"}
    def get(k):
        # try direct, then mapped
        v = meds.get(k) or meds.get(key_map.get(k, k))
        if v is None:
            # fallback to any
            v = list(meds.values())[0]
        if isinstance(v, (list, tuple)):
            return v[0], v[1]
        return v["median"], v["iqr"]
    mb, ib = get("bpm")
    mo, io = get("onset")
    md, id_ = get("dance")
    clip = arts.get("clip", 4.0)
    return [
        _robust_scale(bpm, mb, ib, clip),
        _robust_scale(onset, mo, io, clip),
        _robust_scale(dance, md, id_, clip),
    ]

def _texture_vector(data_store, mbid) -> tuple[list[float], list[float]]:
    feats = data_store.features[mbid]["measurements"]
    arts = _load_artifacts(data_store)
    # spectral
    cent = math.log(max(1e-6, feats["lowlevel.spectral_centroid.mean"]))
    roll = math.log(max(1e-6, feats["lowlevel.spectral_rolloff.mean"]))
    flux = math.log(max(1e-6, feats["lowlevel.spectral_flux.mean"]))
    zcr = math.log1p(feats["lowlevel.zerocrossingrate.mean"])
    mfcc = feats["lowlevel.mfcc.mean"][1:]  # 12 dims
    meds = arts["texture_medians"]
    if isinstance(meds, dict) and "centroid" in meds:
        # new format
        def get_median(key):
            v = meds[key]
            if isinstance(v, (list,tuple)):
                return v[0], v[1]
            return v["median"], v["iqr"]
        mc, ic = get_median("centroid")
        mr, ir = get_median("rolloff")
        mf, ifr = get_median("flux")
        mz, iz = get_median("zcr")
        mfcc_meds = meds["mfcc"]
        # mfcc_meds is list of [med, iqr]
        mfcc_scaled = []
        for i, coeff in enumerate(mfcc):
            med, iqr = mfcc_meds[i] if isinstance(mfcc_meds[i], (list,tuple)) else (mfcc_meds[i]["median"], mfcc_meds[i]["iqr"])
            mfcc_scaled.append(_robust_scale(coeff, med, iqr, arts.get("clip",4.0)))
    else:
        # fallback
        mc, ic = meds["centroid"]
        mr, ir = meds["rolloff"]
        mf, ifr = meds["flux"]
        mz, iz = meds["zcr"]
        mfcc_meds = meds["mfcc"]
        mfcc_scaled = [_robust_scale(c, mfcc_meds[i][0], mfcc_meds[i][1], arts.get("clip",4.0)) for i,c in enumerate(mfcc)]
    clip = arts.get("clip", 4.0)
    spectral = [
        _robust_scale(cent, mc, ic, clip),
        _robust_scale(roll, mr, ir, clip),
        _robust_scale(flux, mf, ifr, clip),
        _robust_scale(zcr, mz, iz, clip),
    ]
    return mfcc_scaled, spectral


def _per_seed_score(data_store, seed_mbid: str, candidate_mbid: str, method: str) -> float:
    if method == "collaborative-v1":
        if data_store.collaborative is None:
            raise RuntimeError("Listener patterns model is not installed")
        return data_store.collaborative.score(seed_mbid, candidate_mbid)
    if method == "clap-v1":
        if data_store.embeddings is None:
            raise RuntimeError("CLAP embeddings not loaded")
        # dot product of unit vectors
        si = data_store.uuid_to_index[seed_mbid]
        ci = data_store.uuid_to_index[candidate_mbid]
        # numpy dot
        if np is not None:
            return float(np.dot(data_store.embeddings[si], data_store.embeddings[ci]))
        else:
            # fallback: cannot compute
            raise RuntimeError("numpy required for CLAP")
    elif method == "rhythm-v1":
        sv = _rhythm_vector(data_store, seed_mbid)
        cv = _rhythm_vector(data_store, candidate_mbid)
        # mean squared difference
        mse = sum((a-b)**2 for a,b in zip(sv, cv)) / len(sv)
        return -mse
    elif method == "texture-v1":
        smfcc, sspec = _texture_vector(data_store, seed_mbid)
        cmfcc, cspec = _texture_vector(data_store, candidate_mbid)
        mse_mfcc = sum((a-b)**2 for a,b in zip(smfcc, cmfcc)) / len(smfcc) if smfcc else 0
        mse_spec = sum((a-b)**2 for a,b in zip(sspec, cspec)) / len(sspec) if sspec else 0
        # 50% each group
        overall = 0.5 * mse_mfcc + 0.5 * mse_spec
        return -overall
    else:
        raise ValueError(f"unknown method {method}")


def _preference_fit(data_store, mbid: str, preferences: Optional[dict]) -> float:
    if not preferences:
        return 0.0
    feats = data_store.features.get(mbid, {})
    preds = feats.get("predictions", {})
    fits = []
    # instrumental vs vocal
    if "instrumental" in preferences:
        want_instrumental = preferences["instrumental"]  # float in [-1,1] or bool?
        # map: -1 = vocal, 1 = instrumental
        # value in voice_instrumental.all
        vi = preds.get("voice_instrumental", {}).get("all", {})
        # missing -> neutral 0
        if vi:
            inst = vi.get("instrumental", 0.5)
            voice = vi.get("voice", 0.5)
            # fit: instrumental score minus vocal? Actually want difference
            # if want instrumental (positive), fit = inst - voice? But inst+voice approx 1
            fit = (inst - voice)  # in [-1,1]
            # weight by preference magnitude
            # preferences instrumental is -1..1 : -1 vocal preference, 1 instrumental
            val = preferences["instrumental"]
            if isinstance(val, bool):
                val = 1.0 if val else -1.0
            # we define preference fit as val * fit? But spec: use sign of answer to favour requested class
            # Simpler: if val>0, fit is (inst - 0.5)*2? Let's use val * fit normalized
            # Actually fit should be in [-1,1] representing how well song matches preference direction
            fits.append(val * fit)
        else:
            fits.append(0.0)
    if "acoustic_electronic" in preferences:
        val = preferences["acoustic_electronic"]  # -1 acoustic, 1 electronic? Let's define -1 acoustic, +1 electronic
        ae_acoustic = preds.get("mood_acoustic", {}).get("all", {}).get("acoustic")
        ae_electronic = preds.get("mood_electronic", {}).get("all", {}).get("electronic")
        if ae_acoustic is not None and ae_electronic is not None:
            # difference: electronic - acoustic? But they are separate classifiers not complementary
            fit = ae_electronic - ae_acoustic  # in [-1,1] roughly
            fits.append(val * fit)
        else:
            fits.append(0.0)
    if not fits:
        return 0.0
    return sum(fits) / len(fits)


def score_candidates(data_store, seed_ids, method, candidates, preferences=None):
    # returns list of (rec, base_score, utility) sorted descending base, then uuid, then utility if preferences
    per_candidate = []
    for rec in candidates:
        cid = rec["recording_mbid"]
        per_seed = [_per_seed_score(data_store, sid, cid, method) for sid in seed_ids]
        base = sum(per_seed) / len(per_seed)
        per_candidate.append((rec, base, per_seed))
    # apply preferences to compute utility for reranking, but preserve base
    scored = []
    for rec, base, per_seed in per_candidate:
        fit = _preference_fit(data_store, rec["recording_mbid"], preferences)
        # need percentile B for utility? But per spec, B is percentile in [0,1] +0.05*fit
        # However to avoid needing calibration here, we approximate B via rank? Better compute percentile lazily
        # For initial implementation without calibration, use base normalized via calibration's percentile
        # Import calibration
        from .calibration import percentile_for_score
        try:
            B = percentile_for_score(data_store, method, len(seed_ids), base) / 100.0
        except Exception:
            B = 0.5
        U = B + 0.05 * fit if preferences else B
        # But if no preferences, we want exact base ordering preserved
        scored.append((rec, base, U, per_seed, fit))
    # sorting: if preferences active, sort by U desc, then base desc, then uuid
    # else sort by base desc, then uuid
    if preferences:
        scored.sort(key=lambda x: (-x[2], -x[1], x[0]["recording_mbid"]))
    else:
        scored.sort(key=lambda x: (-x[1], x[0]["recording_mbid"]))
    # return with utility
    return [(rec, base, U) for rec, base, U, _, _ in scored]

def explain_result(data_store, seed_ids, method, result_id, candidate_filter, preferences):
    # recompute per-seed scores
    per_seed_scores = {}
    for sid in seed_ids:
        s = _per_seed_score(data_store, sid, result_id, method)
        per_seed_scores[sid] = s
    base = sum(per_seed_scores.values()) / len(per_seed_scores) if per_seed_scores else 0
    # detailed components for feature methods
    detail = {}
    if method == "rhythm-v1":
        # show raw values and scaled differences
        detail["seed_values"] = {}
        for sid in seed_ids:
            feats = data_store.features[sid]["measurements"]
            detail["seed_values"][sid] = {
                "rhythm.bpm": feats["rhythm.bpm"],
                "rhythm.onset_rate": feats["rhythm.onset_rate"],
                "rhythm.danceability": feats["rhythm.danceability"],
            }
        cand_feats = data_store.features[result_id]["measurements"]
        detail["candidate_values"] = {
            "rhythm.bpm": cand_feats["rhythm.bpm"],
            "rhythm.onset_rate": cand_feats["rhythm.onset_rate"],
            "rhythm.danceability": cand_feats["rhythm.danceability"],
        }
        # per-dimension distances
        result_vec = _rhythm_vector(data_store, result_id)
        detail["per_seed_distances"] = {}
        for sid in seed_ids:
            sv = _rhythm_vector(data_store, sid)
            diffs = [abs(a-b) for a,b in zip(sv, result_vec)]
            detail["per_seed_distances"][sid] = diffs
    elif method == "texture-v1":
        result_mfcc, result_spec = _texture_vector(data_store, result_id)
        detail["groups"] = {"timbral_weight": 0.5, "spectral_weight": 0.5}
        per_seed_group = {}
        for sid in seed_ids:
            smfcc, sspec = _texture_vector(data_store, sid)
            mse_mfcc = sum((a-b)**2 for a,b in zip(smfcc, result_mfcc))/len(smfcc) if smfcc else 0
            mse_spec = sum((a-b)**2 for a,b in zip(sspec, result_spec))/len(sspec) if sspec else 0
            per_seed_group[sid] = {"timbral_mse": mse_mfcc, "spectral_mse": mse_spec}
        detail["per_seed_group_mse"] = per_seed_group
    elif method == "clap-v1":
        detail["note"] = "CLAP audio embedding proximity; similarity is dot product of unit vectors. No causal acoustic explanation is claimed."
    elif method == "collaborative-v1":
        model = data_store.collaborative
        detail = {"model_id": model.identity, "dimensions": model.meta["dimensions"],
                  "result_positive_listeners": model.meta["listener_counts"][result_id],
                  "seed_positive_listeners": {sid: model.meta["listener_counts"][sid] for sid in seed_ids},
                  "note": "Truncated SVD learned from real ListenBrainz loves across listeners. Mean cosine similarity to selected songs; no audio or CLAP used. These are shared preference patterns, not evidence that the songs sound alike."}
    # preference contribution
    pref_fit = _preference_fit(data_store, result_id, preferences) if preferences else 0.0
    return {
        "method": method,
        "seed_ids": seed_ids,
        "result_id": result_id,
        "base_score": base,
        "per_seed_scores": per_seed_scores,
        "preference_fit": pref_fit,
        "detail": detail,
        "note": "Explanations show scoring components; similarity does not prove audible cause. Match percentages are reference percentiles, not enjoyment probabilities.",
    }
