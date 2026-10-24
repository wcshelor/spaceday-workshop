"""Exercise actual retrieval and artifact integrity, not bank-order placeholders."""
import hashlib
import json

import numpy as np
import pytest
from fastapi.testclient import TestClient

from backend.app.config import settings
from backend.app.data_store import DataStore
from backend.app.main import app
from backend.app.schemas import DescriptionMatchRequest


@pytest.fixture(scope="module")
def ds():
    store = DataStore(settings.data_dir, settings.scoring_artifact, settings.language_artifact)
    store.load()
    return store


def test_real_bank_is_ranked_for_each_song(ds):
    assert ds.prompt_embeddings is not None, ds.description_error
    assert ds.language_meta["placeholder"] is False
    winners = set()
    for row in (0, 100, 300, 700):
        sid = ds.songs[row]["recording_mbid"]
        result = ds.describe(DescriptionMatchRequest(recording_mbid=sid, limit=8))
        scores = ds.prompt_embeddings @ ds.embeddings[row]
        best = sorted(range(len(scores)), key=lambda i: (-float(scores[i]), ds.language_bank[i]["id"]))[0]
        assert result["matches"][0]["id"] == ds.language_bank[best]["id"]
        assert result == ds.describe(DescriptionMatchRequest(recording_mbid=sid, limit=8))
        assert len({m["paraphrase_group"] for m in result["matches"]}) == 8
        winners.add(result["matches"][0]["id"])
    assert len(winners) > 1


def test_category_filter_is_applied_before_selection(ds):
    sid = ds.songs[0]["recording_mbid"]
    result = ds.describe(DescriptionMatchRequest(recording_mbid=sid, categories=["rhythm"], limit=8))
    assert result["matches"]
    assert all(m["category"] == "rhythm" for m in result["matches"])
    assert ds.describe(DescriptionMatchRequest(recording_mbid=sid, categories=["nonexistent"]))["matches"] == []
    with pytest.raises(KeyError):
        ds.describe(DescriptionMatchRequest(recording_mbid="missing"))


@pytest.mark.parametrize("damage", ["placeholder", "pipeline", "bank", "checksum", "shape", "nan", "norm"])
def test_invalid_artifacts_fail_closed(ds, tmp_path, damage):
    meta = dict(ds.language_meta)
    raw = (settings.language_artifact / "prompt_embeddings.f32").read_bytes()
    if damage == "placeholder":
        meta["placeholder"] = True
    elif damage == "pipeline":
        meta["pipeline_version"] = "different"
    elif damage == "bank":
        meta["prompt_bank_sha256"] = "wrong"
    elif damage == "checksum":
        meta["embeddings_sha256"] = "wrong"
    else:
        vectors = np.frombuffer(raw, dtype="<f4").copy()
        if damage == "shape":
            vectors = vectors[:-1]
        elif damage == "nan":
            vectors[0] = np.nan
        else:
            vectors[:512] = 0
        raw = vectors.tobytes()
        meta["embeddings_sha256"] = hashlib.sha256(raw).hexdigest()
    (tmp_path / "meta.json").write_text(json.dumps(meta))
    (tmp_path / "prompt_embeddings.f32").write_bytes(raw)
    store = DataStore(settings.data_dir, settings.scoring_artifact, tmp_path)
    store.pipeline_version = ds.pipeline_version
    store.language_bank = ds.language_bank
    store._load_prompt_embeddings(settings.data_dir.parents[1] / "content/prompts-v1.json")
    assert store.prompt_embeddings is None
    assert store.description_error


def test_description_api_and_retired_search():
    with TestClient(app) as client:
        info = client.get("/api/bootstrap").json()
        assert info["language_status"] == "prepared"
        assert info["live_text_search_status"] == "retired"
        sid = client.get("/api/songs?limit=1").json()["items"][0]["recording_mbid"]
        response = client.post("/api/descriptions", json={"recording_mbid": sid, "limit": 5})
        assert response.status_code == 200
        assert len(response.json()["matches"]) == 5
        assert client.post("/api/text-search", json={"query": "soft guitar"}).status_code == 503


def test_unavailable_descriptions_return_503_without_affecting_core(monkeypatch):
    from backend.app.main import STATE
    with TestClient(app) as client:
        store = STATE["data_store"]
        sid = store.songs[0]["recording_mbid"]
        monkeypatch.setattr(store, "prompt_embeddings", None)
        response = client.post("/api/descriptions", json={"recording_mbid": sid})
        assert response.status_code == 503
        assert "unavailable" in response.text
        assert client.post("/api/recommendations", json={"seed_ids": [sid], "method": "clap-v1", "limit": 1}).status_code == 200
