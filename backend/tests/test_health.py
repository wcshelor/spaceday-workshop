from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_live():
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_bootstrap():
    r = client.get("/api/bootstrap")
    assert r.status_code == 200
    j = r.json()
    assert "dataset_id" in j
    assert "supported_methods" in j
