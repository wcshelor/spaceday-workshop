# Deployment

## Current Candidate

- **Backend:** FastAPI + Uvicorn, Python 3.11–3.13, NumPy 1.26+, single worker (`--workers 1`)
- **Frontend:** Vite-built static (189 KB js gz 57 KB, 9.7 KB css), served by backend at `/` (single origin)
- **Runtime data:** `data/workshop/{songs.json,features.json,clap_embeddings.f32,manifest.json}` (~3 MB + 3 MB vectors) + `artifacts/scoring-v1/{meta.json,calibration.json}` (~1 MB) + `artifacts/collaborative-v1/{meta.json,embeddings.f32}` (~0.5 MB) + `content/prompts-v1.json` (400 prompts) + `artifacts/language-v1/meta.json` (+ optional ONNX weights not in repo, excluded from image). Total image without ONNX ~50–60 MB; source caches `data/sources` and `data/catalogue` are excluded.
- **Container:** `Dockerfile` uses `python:3.11-slim` + `node:20-alpine` builder, installs backend via `pip install ./backend` from `backend/pyproject.toml` (pinned `fastapi==0.110.2`, `uvicorn[standard]==0.29.0`, `pydantic==2.7.1`, `pydantic-settings==2.3.4`, `numpy==1.26.4`, `python-multipart==0.0.9`; excludes `language` and `collaborative-build` extras). Copies backend app, config, workshop data, scoring/collaborative/language artifacts, prepared-language content, and frontend `dist`. No repository root served. `SPACEDAY_LANGUAGE_MODE=disabled` by default.
- **SPA serving:** `GET /` serves `frontend/dist/index.html`; `/assets/*` serves hashed assets; `/api/*` and `/health/*` are API/health only (never return HTML); any other path without extension (e.g., `/describe`) falls back to `index.html` for client navigation; missing assets with extensions return 404, not HTML.

## Render Settings (container and hosted verification pending)

Deploy as a **single Docker Web Service** (not static site, not native Python).

| Field | Value |
|-------|-------|
| **Service Type** | Web Service |
| **Runtime** | Docker |
| **Build Context** | Repository root (`/`) |
| **Root Directory** | blank (leave empty) |
| **Dockerfile Path** | `./Dockerfile` |
| **Start Command Override** | blank (use `Dockerfile` CMD) |
| **CMD** | `exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1` (exec forwards SIGTERM) |
| **Instances** | 1 |
| **Plan** | 1 CPU / 2 GB RAM initially (see sizing note) |
| **Health Check Path** | `/health/ready` (expects 200 when `dataset_id e755bbd1cc5512d4` loaded; 503 until ready) |
| **Environment** | `SPACEDAY_LANGUAGE_MODE=disabled` (preserve prepared descriptions/examples and all recommendation methods) |
| **Other Env** | `PYTHONPATH=/app` (set in Dockerfile), `SPACEDAY_DATA_DIR=/app/data/workshop`, `SPACEDAY_SCORING_ARTIFACT=/app/artifacts/scoring-v1`, `SPACEDAY_LANGUAGE_ARTIFACT=/app/artifacts/language-v1` (already set in image; override only if custom mount) |
| **Database / Disk** | **None required** — current browser-local session design stores state in `localStorage`; no central DB or persistent disk |
| **Port** | Honor `PORT` provided by Render; default `8000` locally (`EXPOSE 8000`) |
| **CORS** | Backend `SPACEDAY_CORS_ALLOW_ORIGINS` defaults to `http://localhost:5173,http://localhost:3000` (dev only; single-origin production does not need CORS) |

Leave **Auto-Deploy** on for the tracked branch or set to manual per team preference; do not add a separate Render `Docker Command` — the `Dockerfile` `CMD` already handles port and signal forwarding.

## Environment Variables

See `.env.example`; all prefixed `SPACEDAY_`.

| Var | Default | Purpose |
|-----|---------|---------|
| `SPACEDAY_DATA_DIR` | `./data/workshop` (`/app/data/workshop` in image) | frozen workshop files |
| `SPACEDAY_SCORING_ARTIFACT` | `./artifacts/scoring-v1` | scoring + calibration |
| `SPACEDAY_LANGUAGE_ARTIFACT` | `./artifacts/language-v1` | prompt vectors / ONNX (placeholder) |
| `SPACEDAY_SCORING_CONFIG` | `./config/scoring-v1.json` | scoring recipe |
| `SPACEDAY_LANGUAGE_MODE` | `disabled` | `disabled`/`prepared`/`live` — Render: `disabled` |
| `SPACEDAY_ENCODER_ENDPOINT` | unset | private text service URL if separate |
| `SPACEDAY_CORS_ALLOW_ORIGINS` | `http://localhost:5173,...` | dev only |
| `SPACEDAY_REQUEST_DEADLINE_SECONDS` | `15` | per-request timeout |

Model ONNX weights are separately provisioned immutable artifacts with documented sha256 (see `docs/MODEL_SETUP.md`). Do not download at request time. Mount at `artifacts/language-v1/` with `SPACEDAY_LANGUAGE_MODE=live` only after `verify_language_encoder.py` passes on host. Current deployment excludes ONNX; image is `disabled` only.

## Build & Run Locally (Production Mode)

```sh
# backend deps (use conda python 3.13 or system 3.11)
# Install from authoritative pinned declarations (do not use unpinned ad-hoc pip install)
pip install ./backend

# frontend — reproducible install from committed lockfile (no fallback)
npm ci --prefix frontend
# or: cd frontend && npm ci
npm --prefix frontend run build

# scoring artifacts (once, after data freeze)
python scripts/build_app_artifacts.py

# run backend (serves frontend dist if present)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 1

# health checks
curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready
curl http://localhost:8000/api/bootstrap | jq
```

SPA fallback: requests for `/`, `/assets/*`, `/health/*`, `/api/*` behave as described above; direct loads of client paths such as `/describe` return `index.html` (verified locally via `TestClient`; `StaticFiles(html=True)` alone does not provide this). Reverse-proxy deployments must also configure fallback to `index.html` for non-API routes.

## Docker

```sh
docker build -t spaceday-workshop:rc .
docker run --rm -p 8000:8000 -e SPACEDAY_LANGUAGE_MODE=disabled spaceday-workshop:rc
# custom PORT
docker run --rm -p 8001:8001 -e PORT=8001 -e SPACEDAY_LANGUAGE_MODE=disabled spaceday-workshop:rc
# with ONNX weights mounted (only after verify_language_encoder.py passes)
docker run --rm -p 8000:8000 -v $(pwd)/artifacts/language-v1:/app/artifacts/language-v1:ro -e SPACEDAY_LANGUAGE_MODE=live spaceday-workshop:rc
```

`.dockerignore` excludes `data/sources`, `data/catalogue`, `frontend/node_modules`, `frontend/dist`, `backend/tests`, `frontend/tests`, `frontend/e2e`, caches (`__pycache__`, `.pytest_cache`, `.mypy_cache`), `.env`, logs, and large unused model weights (`*.onnx`, `*.pt`, `*.bin`, `artifacts/language-v1/*.onnx`). Image includes `frontend/dist`, `config`, `data/workshop`, `artifacts/{scoring-v1,collaborative-v1,language-v1}` (without ONNX), and `content/prompts-v1.json`.

## Hosting Selection

Earlier allowance $25–50/month is not a capacity guarantee. Choose after real hosted measurements.

**Target host:** Render Web Service (Docker), 1 CPU / 2 GB RAM, 1 instance, health check `/health/ready`. Keep service awake during both 45-minute workshops + 30-minute buffer (disable sleep/auto-suspend).

**Previous placeholder measurements (NOT verified on Render; do not treat as capacity proof):**

- Core recommendation (warm) p95 <1s at 20 concurrency (single worker) — local bench only, not on target host
- Text search (warm, if live) p95 <5s at 20 conc with bounded queue 20 and 15s deadline — not yet measured with real ONNX (blocked)
- Full page usable <3s on venue internet — needs real hosting test
- Memory: embeddings 1500×512×4 = 3 MB + features ~18 MB + scoring overhead <100 MB; plus ONNX text encoder ~200 MB if live (estimate, not measured in container)

**Remaining hosted capacity tests (post-deployment, required before workshop):**
- Cold start time and readiness (`/health/ready` latency)
- Warm recommendation latency at 20/30 concurrent sessions (all methods: `rhythm-v1`, `texture-v1`, `clap-v1`, `collaborative-v1`)
- Concurrent frontend asset serving + API under load
- Memory at steady state and under 30 concurrent recommendation batches
- Live text-search throughput only if/when ONNX is provisioned (queue 20, timeout 15 s)

Provider options to re-check before purchase (prices change):
- Render.com: https://render.com/pricing (keep service awake)
- Fly.io: https://fly.io/plans
- Railway: https://railway.app/pricing

Custom domain optional; use provider hostname initially.

## Startup, Shutdown, Rollback

- Startup: load `data/workshop/manifest.json` checksums, validate 1500 consecutive indexes, unit norms, required features; load `artifacts/scoring-v1/meta.json`+`calibration.json`; load collaborative model if `artifacts/collaborative-v1/meta.json` present; load prompt bank from `artifacts/language-v1` or `content/prompts-v1.json`; warm ONNX only if `SPACEDAY_LANGUAGE_MODE=live`. Fail fast with clear log on incompatible artifact; `health/ready` 503 until ready.
- Deep-link fallback: `/` and any non-API path without extension (e.g., `/describe`) serve `index.html`; verified locally.
- Graceful shutdown: `exec uvicorn` in `Dockerfile` `CMD` forwards `SIGTERM` correctly; Uvicorn handles shutdown.
- Rollback: keep previous image tag + previous `artifacts/scoring-v1` directory; redeploy prior tag if new config fails readiness.

## Log Redaction & Privacy

- Do not log query bodies by default; do not expose one student's cached text to another.
- Browser state is localStorage only; no central collection.

## Post-Deployment Smoke Checks

Run immediately after each Render deploy (both on provider host and after promotion):

```sh
BASE=https://<your-render-host>.onrender.com
curl $BASE/health/live
curl $BASE/health/ready | jq             # expect {"status":"ready","dataset_id":"e755bbd1cc5512d4","language_status":"disabled"}
curl $BASE/api/bootstrap | jq            # supported_methods includes collaborative-v1 when artifacts present
curl "$BASE/api/songs?limit=3" | jq
curl $BASE/ | head -c 200                # should be HTML with <title>Music Recommendation Workshop</title>
# referenced frontend asset (hash changes on rebuild; get from HTML)
ASSET=$(curl -s $BASE/ | grep -o 'assets/index-[^"]*\.js' | head -1)
curl -I $BASE/$ASSET                      # 200
curl $BASE/describe | head -c 200        # SPA fallback — 200 HTML, not 404
curl -i $BASE/api/nonexistent | head    # 404 JSON, not HTML
curl -i $BASE/assets/missing.js | head  # 404, not HTML
```

Then exercise via UI or `curl` POSTs:
- `POST /api/recommendations` for each method (`rhythm-v1`, `texture-v1`, `clap-v1`, `collaborative-v1` with `supported_ids` from bootstrap), with valid seeds, optional `candidate_filter` and `preferences`.
- `POST /api/explanations` for a returned `result_id` (each method).
- `GET /api/examples` and `POST /api/descriptions` (prepared-language functionality; note documents prepared matches are placeholders until ONNX verified).
- `POST /api/text-search` should return 503 `encoder disabled` when `SPACEDAY_LANGUAGE_MODE=disabled` (expected).

## Hosting Requirements Checklist

- [ ] Provider selected (Render Web Service + Docker) and kept awake for both 45-min sessions + 30 min buffer
- [ ] Build context = repository root, root directory blank, Dockerfile `./Dockerfile`, start command blank
- [ ] Image built from pinned `backend/pyproject.toml` via `pip install ./backend`; frontend via `npm ci` (no fallback) — installation commands reviewed; image build not verified
- [ ] `SPACEDAY_LANGUAGE_MODE=disabled` (do not set `live` without verified ONNX)
- [ ] ONNX weights not baked into image (excluded via `.dockerignore`)
- [ ] `health/ready` passes with expected `dataset_id` `e755bbd1cc5512d4`
- [ ] Manual checks: `/` serves HTML, asset loads, `/health/ready`, `/api/bootstrap`, catalogue search, recommendations for all methods including collaborative-v1 with supported seeds, explanations, prepared-language descriptions/examples, SPA refresh (`/describe`), missing API/asset 404s
- [ ] Remaining hosted capacity tests re-run on Render (not just local placeholder bench) before workshop
- [ ] Previous placeholder benchmark not treated as measured capacity

## Remaining Hosting Decisions

- Whether to provision separate live text-encoder service vs. in-process ONNX (pending `verify_language_encoder.py` and hosted measurement)
- Custom domain vs. provider hostname
- Keep-alive config for 90 minutes (Render: disable auto-suspend, set health check)

Do not publish, push, or purchase without explicit authorization.

## Hosted load-test handoff

Docker is not needed on the developer Mac: Render builds the root Dockerfile.
The local test suite does not verify the container image or hosted capacity.
After deployment, run from the repository root (replace the example hostname):

```sh
BENCH_BASE_URL=https://YOUR-SERVICE.onrender.com python3 scripts/benchmark_app.py --hosted --burst 30 --sustained 600
```

The harness requires successful readiness before starting. Mixed phases submit
multiple waves at 20 and 30 concurrency; the sustained phase keeps at most 30
tasks in flight and drains and records all remaining work after its deadline.
Only a text-search 503 explicitly indicating a disabled encoder is expected
when bootstrap reports disabled language mode. Recommendation/search latency
failures also cause a nonzero exit status. Reports are written to
`benchmark_report.json`; check server CPU and memory separately in Render.
A short local test or mocked concurrency test is not a ten-minute hosted pass.
