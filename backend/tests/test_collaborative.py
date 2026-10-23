import hashlib
import json
import shutil

import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app.config import settings
from backend.app.data_store import DataStore
from backend.app.main import app, STATE
from backend.app.recommendation.collaborative import CollaborativeModel
from backend.app.schemas import RecommendationRequest


@pytest.fixture(scope="module")
def ds():
    store = DataStore(settings.data_dir, settings.scoring_artifact, settings.language_artifact)
    store.load()
    return store


def test_average_profile_and_shared_pool(ds):
    model = ds.collaborative
    seeds = list(model.index)[:2]
    request = RecommendationRequest(seed_ids=seeds, method="collaborative-v1", limit=20)
    result = ds.recommend(request)
    assert result["candidate_filter"] == {"collaborative_only": True}
    assert result["scoring_version"] == model.identity
    expected = []
    for mbid, index in model.index.items():
        if mbid not in seeds:
            score = float(model.vectors[index] @ model.vectors[[model.index[s] for s in seeds]].mean(axis=0))
            expected.append((mbid, score))
    expected.sort(key=lambda pair: (-pair[1], pair[0]))
    assert [r["recording_mbid"] for r in result["results"]] == [r[0] for r in expected[:20]]
    assert np.allclose([r["base_score"] for r in result["results"]], [r[1] for r in expected[:20]], atol=1e-6)
    reverse = ds.recommend(request.model_copy(update={"seed_ids": seeds[::-1]}))
    assert result == reverse
    # The shared filter works with existing methods, without changing their scores.
    shared = ds.recommend(RecommendationRequest(seed_ids=seeds, method="clap-v1", candidate_filter={"collaborative_only": True}, limit=20))
    assert all(r["recording_mbid"] in model.index for r in shared["results"])
    assert not set(seeds).intersection(r["recording_mbid"] for r in shared["results"])


def test_api_coverage_errors_and_explanations():
    with TestClient(app) as client:
        bootstrap = client.get("/api/bootstrap").json()
        supported = set(bootstrap["collaborative"]["supported_ids"])
        page = client.get("/api/songs?collaborative_only=true&limit=100").json()
        assert page["total"] == len(supported)
        assert all(s["recording_mbid"] in supported for s in page["items"])
        seed = page["items"][0]["recording_mbid"]
        restored = client.get("/api/songs", params={"ids": seed}).json()
        assert restored["total"] == 1
        assert restored["items"][0]["recording_mbid"] == seed
        body = {"seed_ids": [seed], "method": "collaborative-v1"}
        response = client.post("/api/recommendations", json=body)
        assert response.status_code == 200
        result = response.json()["results"][0]
        explanation = client.post("/api/explanations", json={**body, "result_id": result["recording_mbid"]})
        assert explanation.status_code == 200
        assert explanation.json()["base_score"] == pytest.approx(result["base_score"])
        assert explanation.json()["detail"]["result_positive_listeners"] >= 5
        unsupported = next(s["recording_mbid"] for s in STATE["data_store"].songs if s["recording_mbid"] not in supported)
        invalid = client.post("/api/recommendations", json={**body, "seed_ids": [seed, unsupported]})
        assert invalid.status_code == 422
        assert "unsupported" in invalid.json()["detail"].lower()
        for path in ["/artifacts/collaborative-v1/embeddings.f32", "/data/sources/listenbrainz/recording_feedback.parquet"]:
            assert client.get(path).status_code == 404


def test_independent_calibration_and_optional_model(ds, monkeypatch):
    model = ds.collaborative
    for count in range(1, 6):
        table = model.tables[count]
        scores = np.linspace(-1, 1, 100)
        percentiles = [model.percentile(count, float(s)) for s in scores]
        assert all(0 <= p <= 99.9 for p in percentiles)
        assert percentiles == sorted(percentiles)
        assert model.percentile(count, table[200, 0]) == pytest.approx(table[200, 1])
    seed = next(iter(model.index))
    monkeypatch.setattr(ds, "collaborative", None)
    assert "collaborative-v1" not in ds.bootstrap_payload()["supported_methods"]
    with pytest.raises(RuntimeError, match="not installed"):
        ds.recommend(RecommendationRequest(seed_ids=[seed], method="collaborative-v1"))
    assert ds.recommend(RecommendationRequest(seed_ids=[seed], method="clap-v1"))["results"]


def test_corrupt_artifacts_rejected(tmp_path):
    source = settings.scoring_artifact.parent / "collaborative-v1"
    for name in ["meta.json", "embeddings.f32"]:
        shutil.copyfile(source / name, tmp_path / name)
    raw = bytearray((tmp_path / "embeddings.f32").read_bytes())
    raw[0] ^= 1
    (tmp_path / "embeddings.f32").write_bytes(raw)
    with pytest.raises(RuntimeError, match="checksum"):
        CollaborativeModel(tmp_path, settings.data_dir / "songs.json")


def test_trained_artifact_provenance(ds):
    meta = ds.collaborative.meta
    source = settings.data_dir.parent / "sources/listenbrainz/recording_feedback.parquet"
    assert hashlib.sha256(source.read_bytes()).hexdigest() == meta["source_sha256"]
    assert meta["coverage"]["supported"] == len(ds.collaborative.index)
    assert min(meta["listener_counts"].values()) >= 5
    evaluation = meta["evaluation"]
    assert evaluation["cases"] > 0
    assert evaluation["results"]["svd"]["hit_rate_at_10"] > evaluation["results"]["popularity"]["hit_rate_at_10"]
    # Deployment artifacts contain aggregate song factors/counts, no listener IDs.
    assert "user_id" not in json.dumps(meta)
