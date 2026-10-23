"""Runtime for the optional, offline-trained listener-feedback model."""
import hashlib
import json

import numpy as np


class CollaborativeModel:
    def __init__(self, directory, catalogue_path):
        meta_bytes = (directory / "meta.json").read_bytes()
        self.meta = json.loads(meta_bytes)
        self.identity = "collaborative-v1-" + hashlib.sha256(meta_bytes).hexdigest()[:12]
        if hashlib.sha256(catalogue_path.read_bytes()).hexdigest() != self.meta["catalogue_sha256"]:
            raise RuntimeError("collaborative model catalogue checksum mismatch")
        raw = (directory / "embeddings.f32").read_bytes()
        if hashlib.sha256(raw).hexdigest() != self.meta["embeddings_sha256"]:
            raise RuntimeError("collaborative embeddings checksum mismatch")
        ids = self.meta["recording_mbids"]
        if len(set(ids)) != len(ids):
            raise RuntimeError("duplicate collaborative recording IDs")
        self.index = {mbid: i for i, mbid in enumerate(ids)}
        self.vectors = np.frombuffer(raw, dtype="<f4").reshape(len(ids), self.meta["dimensions"])
        if not np.all(np.isfinite(self.vectors)) or not np.allclose(np.linalg.norm(self.vectors, axis=1), 1, atol=1e-4):
            raise RuntimeError("invalid collaborative vectors")
        self.tables = {}
        for count in range(1, 6):
            points = np.array(self.meta["calibration_tables"][str(count)], dtype=float)
            if points.ndim != 2 or points.shape[1] != 2 or not np.all(np.isfinite(points)) or np.any(np.diff(points[:, 0]) <= 0) or np.any(np.diff(points[:, 1]) < 0):
                raise RuntimeError("invalid collaborative calibration")
            self.tables[count] = points

    def score(self, seed, candidate):
        return float(self.vectors[self.index[seed]] @ self.vectors[self.index[candidate]])

    def percentile(self, seed_count, score):
        points = self.tables[seed_count]
        return round(float(np.interp(score, points[:, 0], points[:, 1])), 1)

    def validate_seeds(self, seeds):
        if not 1 <= len(seeds) <= 5 or len(set(seeds)) != len(seeds):
            raise ValueError("Choose 1–5 distinct songs")
        missing = [s for s in seeds if s not in self.index]
        if missing:
            raise ValueError("Listener patterns needs songs with enough feedback. Remove unsupported songs from My List and choose from the supported catalogue. Unsupported IDs: " + ", ".join(missing))
