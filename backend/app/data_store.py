from __future__ import annotations

import json
import hashlib
import gzip
import struct
from pathlib import Path
import unicodedata
import re
from typing import Optional

# Will use numpy if available; fallback to pure python for minimal readiness
try:
    import numpy as np
except ImportError:
    np = None


def _norm_text(s: str) -> str:
    # case/diacritic tolerant
    nfkd = unicodedata.normalize("NFKD", s)
    ascii_only = "".join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_only.lower()


class DataStore:
    def __init__(self, data_dir: Path, scoring_dir: Path, language_dir: Path):
        self.data_dir = Path(data_dir)
        self.scoring_dir = Path(scoring_dir)
        self.language_dir = Path(language_dir)
        self.songs: list[dict] = []
        self.features: dict = {}
        self.manifest: dict = {}
        self.dataset_id: str = "unknown"
        self.pipeline_version: str = ""
        self.snapshot_date: str = ""
        self.uuid_to_index: dict[str, int] = {}
        self.index_to_uuid: dict[int, str] = {}
        self.embeddings: Optional[object] = None  # np array or None
        self.scoring_artifacts = None
        self.calibration = None
        self.language_bank = None
        self.prompt_embeddings = None
        self.language_meta = None
        self.description_reference = None
        self.description_scoring_id = None
        self.description_error = "Description embeddings are not installed"
        self.collaborative = None

    def load(self):
        # 1. manifest hashes verification
        manifest_path = self.data_dir / "manifest.json"
        if not manifest_path.exists():
            raise RuntimeError(f"manifest missing at {manifest_path}")
        self.manifest = json.loads(manifest_path.read_text())
        self.snapshot_date = self.manifest.get("source_snapshot", "")
        self.pipeline_version = self.manifest.get("pipeline_version", "")
        # verify file checksums listed
        for fname, info in self.manifest.get("files", {}).items():
            fpath = self.data_dir / fname
            if not fpath.exists():
                raise RuntimeError(f"required file missing: {fname}")
            sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
            if sha != info["sha256"]:
                raise RuntimeError(f"checksum mismatch for {fname}: expected {info['sha256']} got {sha}")
            if "bytes" in info and info["bytes"] != fpath.stat().st_size:
                raise RuntimeError(f"size mismatch for {fname}")

        # 2. load songs
        songs_path = self.data_dir / "songs.json"
        self.songs = json.loads(songs_path.read_text())
        if len(self.songs) != 1500:
            raise RuntimeError(f"songs.json must contain 1500 records, got {len(self.songs)}")
        # indexes consecutive 0..1499 and recording_mbid unique
        seen_mbids = set()
        for rec in self.songs:
            mbid = rec.get("recording_mbid")
            idx = rec.get("embedding_index")
            if not mbid or idx is None:
                raise RuntimeError(f"song missing mbid or embedding_index: {rec}")
            if mbid in seen_mbids:
                raise RuntimeError(f"duplicate recording_mbid {mbid}")
            seen_mbids.add(mbid)
            self.uuid_to_index[mbid] = idx
            self.index_to_uuid[idx] = mbid
        if set(self.uuid_to_index.values()) != set(range(1500)):
            raise RuntimeError("embedding_index must be consecutive 0..1499")
        # ordering not necessarily sorted by uuid; we keep map

        # 3. features keyed by mbid
        feat_path = self.data_dir / "features.json"
        self.features = json.loads(feat_path.read_text())
        if len(self.features) != 1500:
            # manifest says 1500 but spec says 1499 high-level available; features.json still has 1500 keys
            # check that every song mbid has feature
            missing = [r["recording_mbid"] for r in self.songs if r["recording_mbid"] not in self.features]
            if missing:
                raise RuntimeError(f"features missing for {missing[:3]}")
        # validate required baseline
        for mbid in seen_mbids:
            f = self.features.get(mbid)
            if f is None:
                raise RuntimeError(f"feature missing for {mbid}")
            meas = f.get("measurements", {})
            for key in ["rhythm.bpm", "rhythm.onset_rate", "rhythm.danceability",
                        "lowlevel.mfcc.mean", "lowlevel.spectral_centroid.mean",
                        "lowlevel.spectral_rolloff.mean", "lowlevel.spectral_flux.mean",
                        "lowlevel.zerocrossingrate.mean"]:
                if key not in meas:
                    raise RuntimeError(f"missing measurement {key} for {mbid}")
            # mfcc dim consistent
            mfcc = meas.get("lowlevel.mfcc.mean")
            if not isinstance(mfcc, list) or len(mfcc) != 13:
                raise RuntimeError(f"mfcc dim unexpected for {mbid}: {mfcc}")

        # 4. embeddings
        emb_path = self.data_dir / "clap_embeddings.f32"
        expected_bytes = 1500*512*4
        if emb_path.stat().st_size != expected_bytes:
            raise RuntimeError(f"embedding file size mismatch: got {emb_path.stat().st_size} expected {expected_bytes}")
        if np is not None:
            arr = np.fromfile(str(emb_path), dtype="<f4")
            if arr.size != 1500*512:
                raise RuntimeError(f"embedding element count mismatch {arr.size}")
            mat = arr.reshape(1500, 512)
            # finite check
            if not np.all(np.isfinite(mat)):
                raise RuntimeError("embedding contains non-finite values")
            # unit norm roughly
            norms = np.linalg.norm(mat, axis=1)
            if not np.all(np.abs(norms - 1.0) < 1e-3):
                # allow small tolerance but log
                bad = np.where(np.abs(norms - 1.0) >= 1e-3)[0]
                raise RuntimeError(f"embeddings not unit-normalised at rows {bad[:3]}")
            self.embeddings = mat
        else:
            self.embeddings = None

        # dataset id from manifest content hash
        canon = json.dumps(self.manifest, sort_keys=True).encode()
        self.dataset_id = hashlib.sha256(canon).hexdigest()[:16]

        collaborative_dir = self.scoring_dir.parent / "collaborative-v1"
        if (collaborative_dir / "meta.json").exists():
            from .recommendation.collaborative import CollaborativeModel
            self.collaborative = CollaborativeModel(collaborative_dir, songs_path)
            if not set(self.collaborative.index).issubset(seen_mbids):
                raise RuntimeError("collaborative model contains unknown catalogue IDs")

        # Try load scoring artifacts if present
        try:
            self._load_scoring_artifacts()
        except FileNotFoundError:
            self.scoring_artifacts = None
            self.calibration = None

        # Try load language bank
        try:
            self._load_language()
        except FileNotFoundError:
            self.language_bank = None

    def _load_scoring_artifacts(self):
        meta = self.scoring_dir / "meta.json"
        if not meta.exists():
            raise FileNotFoundError("scoring meta missing")
        self.scoring_artifacts = json.loads(meta.read_text())
        cal_path = self.scoring_dir / "calibration.json"
        if cal_path.exists():
            self.calibration = json.loads(cal_path.read_text())

    def _load_language(self):
        # try artifacts first, then content — content path resolves robustly for local and /app container
        def _repo_root() -> Path:
            cand = Path(__file__).resolve().parents[2]
            if (cand / "backend" / "app" / "main.py").exists() or (cand / "frontend" / "package.json").exists():
                return cand
            for p in Path(__file__).resolve().parents:
                if (p / "backend" / "app" / "main.py").exists() or (p / "frontend" / "package.json").exists():
                    return p
            if Path("/app").exists() and (Path("/app") / "backend").exists():
                return Path("/app")
            return cand

        candidates = [
            self.language_dir / "prompts-v1.json",
            _repo_root() / "content" / "prompts-v1.json",
        ]
        for bank in candidates:
            if bank.exists():
                data = json.loads(bank.read_text())
                # handle both list and dict with prompts key
                if isinstance(data, dict) and "prompts" in data:
                    self.language_bank = data["prompts"]
                elif isinstance(data, list):
                    self.language_bank = data
                else:
                    self.language_bank = data
                self._load_prompt_embeddings(bank)
                return
        raise FileNotFoundError("prompt bank missing")

    def _load_prompt_embeddings(self, bank_path):
        """Fail closed for unavailable or incompatible optional description artifacts."""
        try:
            meta = json.loads((self.language_dir / "meta.json").read_text())
            raw = (self.language_dir / "prompt_embeddings.f32").read_bytes()
            if meta.get("placeholder") is not False:
                raise ValueError("Description embeddings are placeholders")
            if meta.get("pipeline_version") != self.pipeline_version:
                raise ValueError("Description encoder pipeline mismatch")
            if meta.get("prompt_bank_sha256") != hashlib.sha256(bank_path.read_bytes()).hexdigest():
                raise ValueError("Description bank checksum mismatch")
            if meta.get("embeddings_sha256") != hashlib.sha256(raw).hexdigest():
                raise ValueError("Description embeddings checksum mismatch")
            if meta.get("prompt_count") != len(self.language_bank):
                raise ValueError("Description count mismatch")
            mat = np.frombuffer(raw, dtype="<f4").reshape(len(self.language_bank), 512)
            if not np.isfinite(mat).all() or not np.allclose(np.linalg.norm(mat, axis=1), 1, atol=1e-3):
                raise ValueError("Invalid description vectors")
            if len({p["id"] for p in self.language_bank}) != len(self.language_bank):
                raise ValueError("Duplicate description IDs")
            from .recommendation.descriptions import build_reference, METHOD
            self.description_reference = build_reference(self.embeddings, mat)
            identity = json.dumps({"method": METHOD, "dataset": self.dataset_id,
                                   "prompts": meta["prompt_bank_sha256"],
                                   "vectors": meta["embeddings_sha256"]}, sort_keys=True)
            self.description_scoring_id = METHOD + "-" + hashlib.sha256(identity.encode()).hexdigest()[:12]
            self.prompt_embeddings, self.language_meta = mat, meta
            self.description_error = None
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            self.prompt_embeddings = None
            self.description_reference = None
            self.description_scoring_id = None
            self.description_error = str(exc)

    def bootstrap_payload(self):
        return {
            "dataset_id": self.dataset_id,
            "pipeline_version": self.pipeline_version,
            "snapshot_date": self.snapshot_date,
            "scoring_version": (self.scoring_artifacts or {}).get("version", "scoring-v1"),
            "calibration_version": (self.calibration or {}).get("version", "calibration-v1"),
            "language_status": self._lang_status(),
            "language_encoder": (self.language_meta or {}).get("encoder_id"),
            "live_text_search_status": "retired",
            "description_scoring_version": self.description_scoring_id,
            "description_categories": sorted({p.get("category", "") for p in (self.language_bank or [])}),
            "supported_methods": ["rhythm-v1", "texture-v1", "clap-v1"] + (["collaborative-v1"] if self.collaborative else []),
            "collaborative": ({"supported_count": len(self.collaborative.index),
                               "supported_ids": list(self.collaborative.index),
                               "model_id": self.collaborative.identity,
                               "source_snapshot": self.collaborative.meta["source_snapshot"]} if self.collaborative else None),
            "filter_vocab": {
                "style_families": [
                    "pop_smooth", "electronic_experimental", "electronic_dance", "jazz_blues",
                    "hiphop_reggae", "indie_alternative", "funk_soul_rnb", "country_folk_acoustic",
                    "classic_rock", "psychedelic", "ambient_instrumental"
                ],
                "familiarity_bands": ["recognisable_anchor", "established_artist_deeper_cut", "discovery_candidate"],
            },
            "year_bounds": {"min": 1960, "max": 2022},
            "score_help": "How strong this computed similarity is compared with reference comparisons in this collection. It is not the chance you will like the song.",
            "attribution_links": {
                "clapback": "https://clapback.seethroughlab.com/export",
                "musicbrainz": "https://musicbrainz.org/doc/About/Data_License",
                "acousticbrainz": "https://acousticbrainz.org/",
            },
        }

    def _lang_status(self):
        return "prepared" if self.prompt_embeddings is not None else "unavailable"

    # --- Catalogue ---
    def _public_song(self, rec: dict) -> dict:
        return {
            "recording_mbid": rec["recording_mbid"],
            "title": rec["title"],
            "artist": rec["artist"],
            "year": rec.get("year"),
            "primary_style_family": rec.get("primary_style_family"),
            "style_families": rec.get("style_families", []),
            "familiarity_band": rec.get("familiarity_band"),
            "is_editorial_anchor": rec.get("is_editorial_anchor", False),
            "tags": rec.get("tags", [])[:10],
            "musicbrainz_url": rec.get("musicbrainz_url"),
            "youtube_search_url": rec.get("youtube_search_url"),
            "spotify_search_url": rec.get("spotify_search_url"),
        }

    def query_songs(self, q=None, style=None, year_min=None, year_max=None, offset=0, limit=20, sort=None, collaborative_only=False, recording_ids=None):
        filtered = self.songs
        if recording_ids is not None:
            filtered = [r for r in filtered if r["recording_mbid"] in recording_ids]
        if collaborative_only:
            filtered = [r for r in filtered if self.collaborative and r["recording_mbid"] in self.collaborative.index]
        if q:
            nq = _norm_text(q)
            filtered = [r for r in filtered if nq in _norm_text(r["title"]) or nq in _norm_text(r["artist"])]
        if style:
            filtered = [r for r in filtered if style in r.get("style_families", []) or r.get("primary_style_family")==style]
        if year_min is not None:
            filtered = [r for r in filtered if r.get("year") is not None and r.get("year") >= year_min]
        if year_max is not None:
            filtered = [r for r in filtered if r.get("year") is not None and r.get("year") <= year_max]
        # deterministic sort: editorial anchors first, then artist/title/uuid
        if sort is None or sort == "default":
            filtered = sorted(filtered, key=lambda r: (0 if r.get("is_editorial_anchor") else 1, r.get("artist","").lower(), r.get("title","").lower(), r.get("recording_mbid")))
        elif sort == "year":
            filtered = sorted(filtered, key=lambda r: (r.get("year") or 9999, r.get("recording_mbid")))
        total = len(filtered)
        page = filtered[offset: offset+limit]
        return {
            "total": total,
            "offset": offset,
            "limit": limit,
            "items": [self._public_song(r) for r in page]
        }

    def get_examples(self):
        if self.language_bank:
            items = [{"id": e["id"], "query": e["text"], "category": e.get("category","")} for e in self.language_bank[:10]]
            return {"version": "prompts-v1", "items": items}
        # fallback static examples
        return {"version": "prompts-v1", "items": [
            {"id": "ex1", "query": "warm acoustic guitar with soft vocals", "category": "texture"},
            {"id": "ex2", "query": "fast energetic drums, danceable", "category": "rhythm"},
        ]}

    # --- Recommendations ---
    def recommend(self, req):
        # lazy import scoring
        from .recommendation.scoring import score_candidates
        from .recommendation.calibration import percentile_for_score
        seed_ids = req.seed_ids
        # canonical sorting for fingerprint determinism
        canonical = sorted(seed_ids)
        effective_filter = dict(req.candidate_filter or {})
        if req.method == "collaborative-v1":
            effective_filter["collaborative_only"] = True
        # validate ids
        for sid in canonical:
            if sid not in self.uuid_to_index:
                raise KeyError(f"unknown seed {sid}")
        if req.method == "collaborative-v1":
            if self.collaborative is None:
                raise RuntimeError("Listener patterns model is not installed")
            self.collaborative.validate_seeds(canonical)
        # candidate filtering
        candidates = [r for r in self.songs if r["recording_mbid"] not in set(canonical)]
        if req.method == "collaborative-v1":
            candidates = [r for r in candidates if r["recording_mbid"] in self.collaborative.index]
        if effective_filter:
            cf = effective_filter
            if cf.get("collaborative_only"):
                if self.collaborative is None:
                    raise RuntimeError("Listener patterns model is not installed")
                candidates = [r for r in candidates if r["recording_mbid"] in self.collaborative.index]
            sf = cf.get("style_family")
            ym = cf.get("year_min")
            yx = cf.get("year_max")
            if sf:
                candidates = [r for r in candidates if sf in r.get("style_families", []) or r.get("primary_style_family")==sf]
            if ym is not None:
                candidates = [r for r in candidates if r.get("year") is not None and r.get("year") >= ym]
            if yx is not None:
                candidates = [r for r in candidates if r.get("year") is not None and r.get("year") <= yx]
        if not candidates:
            raise ValueError("no candidates after filtering")
        # scoring
        scores = score_candidates(self, canonical, req.method, candidates, req.preferences)
        # calibration percentile
        results = []
        for rank, (rec, base_score, utility) in enumerate(scores[: req.limit], start=1):
            pct = percentile_for_score(self, req.method, len(canonical), base_score)
            results.append({
                "recording_mbid": rec["recording_mbid"],
                "title": rec["title"],
                "artist": rec["artist"],
                "year": rec.get("year"),
                "primary_style_family": rec.get("primary_style_family"),
                "rank": rank,
                "base_score": float(base_score),
                "match_percentile": float(pct),
                "youtube_search_url": rec.get("youtube_search_url"),
                "spotify_search_url": rec.get("spotify_search_url"),
            })
        # fingerprint run id
        import hashlib, json
        fp = hashlib.sha256(json.dumps({
            "seeds": canonical,
            "method": req.method,
            "filter": effective_filter or None,
            "prefs": req.preferences,
            "dataset": self.dataset_id,
            **({"model": self.collaborative.identity} if req.method == "collaborative-v1" else {}),
        }, sort_keys=True).encode()).hexdigest()[:12]
        return {
            "run_id": fp,
            "dataset_id": self.dataset_id,
            "scoring_version": self.collaborative.identity if req.method == "collaborative-v1" else (self.scoring_artifacts or {}).get("version", "scoring-v1"),
            "calibration_version": self.collaborative.identity if req.method == "collaborative-v1" else (self.calibration or {}).get("version", "calibration-v1"),
            "method": req.method,
            "seed_ids_canonical": canonical,
            "candidate_filter": effective_filter or None,
            "preferences_applied": req.preferences,
            "results": results,
        }

    def explain(self, req):
        from .recommendation.scoring import score_candidates, explain_result
        if req.result_id not in self.uuid_to_index:
            raise KeyError(f"unknown result {req.result_id}")
        if req.method not in ["rhythm-v1", "texture-v1", "clap-v1", "collaborative-v1"]:
            raise ValueError(f"unknown method {req.method}")
        if req.method == "collaborative-v1":
            if self.collaborative is None:
                raise RuntimeError("Listener patterns model is not installed")
            self.collaborative.validate_seeds(req.seed_ids)
            if req.result_id not in self.collaborative.index:
                raise ValueError("No listener-pattern embedding for this result")
        # recompute without trust
        canonical = sorted(req.seed_ids)
        for sid in canonical:
            if sid not in self.uuid_to_index:
                raise KeyError(f"unknown seed {sid}")
        candidates = [r for r in self.songs if r["recording_mbid"] == req.result_id]
        if not candidates:
            raise KeyError("result not found")
        return explain_result(self, canonical, req.method, req.result_id, req.candidate_filter, req.preferences)

    def text_search(self, req):
        # require live encoder
        from .config import settings
        if settings.language_mode == "disabled":
            raise RuntimeError("text search unavailable: encoder disabled")
        # if not live, use prepared fallback? For now return unavailable
        raise RuntimeError("text search unavailable: encoder not configured")

    def describe(self, req):
        if req.recording_mbid not in self.uuid_to_index:
            raise KeyError(f"unknown recording {req.recording_mbid}")
        if self.prompt_embeddings is None or self.embeddings is None:
            raise RuntimeError("Song description matching unavailable: " + str(self.description_error or "audio vectors missing"))
        audio = self.embeddings[self.uuid_to_index[req.recording_mbid]]
        from .recommendation.descriptions import standardized_scores
        raw_scores = np.asarray(self.prompt_embeddings, dtype=np.float64) @ audio.astype(np.float64)
        scores = standardized_scores(raw_scores, *self.description_reference)
        ranked = sorted((i for i in range(len(self.language_bank)) if np.isfinite(scores[i])),
                        key=lambda i: (-float(scores[i]), self.language_bank[i]["id"]))
        ranked = [i for i in ranked if not req.categories or self.language_bank[i].get("category") in req.categories]
        selected, deferred, seen = [], [], set()
        for i in ranked:
            group = self.language_bank[i].get("paraphrase_group") or self.language_bank[i]["id"]
            if group in seen:
                deferred.append(i)
            else:
                selected.append(i)
                seen.add(group)
        selected = (selected + deferred)[:req.limit]
        return {
            "recording_mbid": req.recording_mbid,
            "matches": [{**self.language_bank[i], "similarity": float(raw_scores[i]), "description_score": float(scores[i])} for i in selected],
            "scoring_version": self.description_scoring_id,
            "reference_dataset_id": self.dataset_id,
            "encoder_id": self.language_meta["encoder_id"],
            "prompt_version": self.language_meta["prompt_version"],
            "note": "Experimental discussion method: phrases ranked by how unusually well they match this song compared with their usual similarity across the full catalogue. Paraphrases are diversified. These are listening invitations, not verified descriptions, emotion predictions or confidence percentages.",
        }
