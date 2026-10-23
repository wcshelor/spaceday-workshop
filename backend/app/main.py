from __future__ import annotations

import uuid
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .config import settings
from .schemas import ErrorEnvelope

app = FastAPI(title="Spaceday Workshop API", version="0.1.0")

origins = [o.strip() for o in settings.cors_allow_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Will be populated at startup
STATE: dict = {
    "ready": False,
    "ready_error": None,
    "dataset_id": None,
    "data_store": None,
}


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    # Log to server console (simple)
    print(f"Unhandled exception for {request.url.path}: {exc}")
    envelope = ErrorEnvelope(code="internal_error", message="Internal server error", retryable=True, request_id=request.headers.get("X-Request-ID"))
    return JSONResponse(status_code=500, content=envelope.model_dump())


@app.get("/health/live")
def health_live():
    return {"status": "ok"}


@app.get("/health/ready")
def health_ready():
    # readiness checks data/artifacts
    if STATE["ready"]:
        return {
            "status": "ready",
            "dataset_id": STATE["dataset_id"],
            "language_status": _language_status(),
        }
    return JSONResponse(
        status_code=503,
        content={
            "status": "not_ready",
            "error": STATE["ready_error"],
            "language_status": _language_status(),
        },
    )


def _language_status() -> str:
    mode = settings.language_mode
    if mode == "disabled":
        return "disabled"
    # If enabled but artifacts missing, report prepared vs live
    # For now return mode
    return mode


@app.get("/api/bootstrap")
def bootstrap():
    # Minimal bootstrap that works even before full data_store ready
    ds = STATE.get("data_store")
    if ds is not None:
        return ds.bootstrap_payload()
    # fallback minimal
    return {
        "dataset_id": STATE.get("dataset_id") or "unknown",
        "pipeline_version": "laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32",
        "snapshot_date": "2026-10-18T05:12:18Z",
        "scoring_version": "scoring-v1",
        "calibration_version": "calibration-v1",
        "language_status": _language_status(),
        "language_encoder": None,
        "supported_methods": ["rhythm-v1", "texture-v1", "clap-v1"],
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


# Lazy import routers to avoid circular
try:
    from .routers import catalogue as catalogue_router
    from .routers import recommendations as rec_router
    from .routers import explanations as exp_router
    from .routers import language as lang_router
    app.include_router(catalogue_router.router, prefix="/api")
    app.include_router(rec_router.router, prefix="/api")
    app.include_router(exp_router.router, prefix="/api")
    app.include_router(lang_router.router, prefix="/api")
except Exception as e:
    print(f"Routers not yet available: {e}")


@app.on_event("startup")
def on_startup():
    try:
        from .data_store import DataStore

        ds = DataStore(settings.data_dir, settings.scoring_artifact, settings.language_artifact)
        ds.load()
        STATE["data_store"] = ds
        STATE["dataset_id"] = ds.dataset_id
        STATE["ready"] = True
        STATE["ready_error"] = None
        print(f"DataStore ready: dataset_id={ds.dataset_id}")
    except Exception as e:
        STATE["ready"] = False
        STATE["ready_error"] = str(e)
        print(f"DataStore failed to load: {e}")
        # Do not crash; health/ready will report 503


def _repo_root() -> Path:
    candidate = Path(__file__).resolve().parents[2]
    if (candidate / "backend" / "app" / "main.py").exists() or (candidate / "frontend" / "package.json").exists():
        return candidate
    for parent in Path(__file__).resolve().parents:
        if (parent / "backend" / "app" / "main.py").exists() or (parent / "frontend" / "package.json").exists():
            return parent
    if Path("/app").exists() and (Path("/app") / "backend").exists():
        return Path("/app")
    return candidate


# Serve frontend static if present (production single-origin)
_frontend_dist = _repo_root() / "frontend" / "dist"
if _frontend_dist.exists():
    assets_dir = _frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/", include_in_schema=False)
    async def serve_root():
        return FileResponse(str(_frontend_dist / "index.html"))

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        # Never turn missing API/health/docs into HTML
        if full_path.startswith("api/") or full_path.startswith("health/"):
            raise HTTPException(status_code=404, detail="Not Found")
        if full_path.startswith("docs") or full_path.startswith("openapi") or full_path.startswith("redoc"):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = _frontend_dist / full_path
        try:
            resolved = file_path.resolve()
            if not resolved.is_relative_to(_frontend_dist.resolve()):
                raise HTTPException(status_code=404, detail="Not Found")
        except HTTPException:
            raise
        except Exception:
            raise HTTPException(status_code=404, detail="Not Found")
        if file_path.is_file():
            return FileResponse(str(file_path))
        # Missing static asset with extension -> 404, not SPA
        if "." in full_path.split("/")[-1]:
            raise HTTPException(status_code=404, detail="Not Found")
        index = _frontend_dist / "index.html"
        if index.is_file():
            return FileResponse(str(index))
        raise HTTPException(status_code=404, detail="Not Found")
