"""Regression tests for deployment fixes: repo root resolution and SPA serving."""
from pathlib import Path
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.config import settings, _repo_root


def test_repo_root_resolves_to_project_root():
    root = _repo_root()
    # must contain backend and frontend markers in both local checkout and /app container
    assert (root / "backend" / "app" / "main.py").exists(), f"root {root} missing backend/app/main.py"
    assert (root / "frontend" / "package.json").exists(), f"root {root} missing frontend/package.json"
    # config defaults should point inside that root
    assert settings.data_dir.exists(), f"data_dir {settings.data_dir} missing"
    assert settings.scoring_artifact.exists()
    assert (settings.scoring_artifact / "meta.json").exists()
    assert settings.scoring_config.exists()


def test_frontend_dist_path_resolves():
    from backend.app.main import _frontend_dist
    # In local checkout with built frontend, dist should exist and contain index.html
    assert _frontend_dist.exists()
    assert (_frontend_dist / "index.html").exists()


def test_production_interface_serving():
    # Ensures / serves frontend, /assets serves file, /api and /health remain reachable,
    # SPA fallback returns HTML for client routes, missing API/assets return 404 not HTML.
    with TestClient(app) as c:
        # / serves HTML
        r = c.get("/")
        assert r.status_code == 200
        assert "text/html" in r.headers.get("content-type", "")
        assert "Music Recommendation Workshop" in r.text

        # referenced asset
        dist = Path("frontend/dist")
        assets = list((dist / "assets").glob("*.js"))
        assert assets, "no js asset found"
        r = c.get(f"/assets/{assets[0].name}")
        assert r.status_code == 200
        assert "javascript" in r.headers.get("content-type", "")

        # health/api still reachable
        assert c.get("/health/live").status_code == 200
        assert c.get("/health/ready").status_code == 200
        assert c.get("/api/bootstrap").status_code == 200
        assert c.get("/api/songs?limit=1").status_code == 200

        # SPA fallback: client routes return HTML
        for path in ["/describe", "/choose", "/listen", "/some/nested/path"]:
            r = c.get(path)
            assert r.status_code == 200, f"{path} should fallback to index.html"
            assert "text/html" in r.headers.get("content-type", "")

        # Missing API should be 404 JSON, not HTML
        r = c.get("/api/nonexistent")
        assert r.status_code == 404
        assert "text/html" not in r.headers.get("content-type", "")

        # Missing asset with extension -> 404 not HTML
        r = c.get("/assets/missing.js")
        assert r.status_code == 404
        assert "text/html" not in r.headers.get("content-type", "")

        # Missing static file with extension -> 404
        r = c.get("/missing.png")
        assert r.status_code == 404
