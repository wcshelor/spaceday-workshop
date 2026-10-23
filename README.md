# Music Recommendation Workshop — App

**Listener patterns:** a real 32-factor collaborative SVD model is now available
for 182 catalogue songs, alongside the original three methods. It learns from
ListenBrainz song loves; switching to it shows supported songs and enables a
shared candidate pool for fair comparisons. See
[model, coverage and evaluation](artifacts/collaborative-v1/README.md).

One hosted browser app for two independent 45-minute workshops (University of Osnabrück, 15–20 adults per cohort). Students browse 1500 curated recordings (1960–2022), pick familiar seeds, compare recommendations, listen externally, reveal supporting information, and discuss reactions. A second tab supports CLAP description matching and student-written text-to-music retrieval (prepared bank + live text encoder when provisioned).

- [Product design](DESIGN.md)
- [Implementation plan](IMPLEMENTATION_PLAN.md)
- [Implementation status](docs/IMPLEMENTATION_STATUS.md)
- [Decisions](docs/DECISIONS.md)
- [API](docs/API.md)
- [Model setup](docs/MODEL_SETUP.md)
- [Listening pilot](docs/PILOT.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Workshop runbook](docs/WORKSHOP_RUNBOOK.md)
- Data: `data/workshop/songs.json` (authoritative), `songs.csv`, `features.json`, `clap_embeddings.f32` (3,072,000 bytes, `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32`), `manifest.json`

## Install, Configure, Run, Test

### Prerequisites
- Node 20+ and Python 3.11–3.13
- `/Users/campshelor/miniconda3/bin/python` (or system `python3` with `pip`)
- No audio downloads; no runtime catalogue calls to MusicBrainz/AcousticBrainz/Clapback

### Install
```sh
# backend deps
/Users/campshelor/miniconda3/bin/pip install fastapi uvicorn pydantic pydantic-settings numpy python-multipart httpx pytest pytest-asyncio anyio
# optional language extra (ONNX)
# /Users/campshelor/miniconda3/bin/pip install onnxruntime transformers tokenizers

# frontend
npm --prefix frontend install
```

### Configure
```sh
cp .env.example .env
# Edit .env if needed; defaults work for local dev:
# SPACEDAY_DATA_DIR=./data/workshop
# SPACEDAY_SCORING_ARTIFACT=./artifacts/scoring-v1
# SPACEDAY_LANGUAGE_MODE=disabled  # set to live after verify_language_encoder.py passes
```

### Generate / Verify Scoring Artifacts (once, after data freeze)
```sh
/Users/campshelor/miniconda3/bin/python scripts/build_app_artifacts.py   # writes artifacts/scoring-v1/meta.json + calibration.json
/Users/campshelor/miniconda3/bin/python scripts/build_language_artifacts.py  # writes placeholder or real ONNX artifacts
/Users/campshelor/miniconda3/bin/python scripts/verify_language_encoder.py   # BLOCKED until ONNX weights provisioned; logs precise blocker
```

### Run (development, two servers with proxy)
```sh
# terminal 1: backend
/Users/campshelor/miniconda3/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# terminal 2: frontend dev (proxies /api to backend)
npm --prefix frontend run dev   # http://localhost:5173
```

### Run (production single-origin)
```sh
npm --prefix frontend run build
/Users/campshelor/miniconda3/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 1
# open http://localhost:8000/  (frontend served by backend)
# direct routes /describe etc survive refresh via html=True mount
```

### Docker (production candidate)
```sh
docker build -t spaceday-workshop:rc .
docker run --rm -p 8000:8000 spaceday-workshop:rc
# with live ONNX (after provisioning)
docker run --rm -p 8000:8000 -v $(pwd)/artifacts/language-v1:/app/artifacts/language-v1:ro -e SPACEDAY_LANGUAGE_MODE=live spaceday-workshop:rc
```

### Test
```sh
# prepared-data validation
python3 scripts/validate_data.py

# backend (deterministic, hand-calculated fixtures)
 /Users/campshelor/miniconda3/bin/python -m pytest backend/tests -v

# frontend typecheck + build
npm --prefix frontend run typecheck
npm --prefix frontend run build
npm --prefix frontend run test   # Vitest

# browser acceptance (requires built frontend + running backend)
npx --prefix frontend playwright test   # or npm --prefix frontend run e2e

# production smoke (run after build)
/Users/campshelor/miniconda3/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 &
curl -s http://127.0.0.1:8000/health/ready | jq
curl -s http://127.0.0.1:8000/api/bootstrap | jq
# benchmark (25 sessions, 20 concurrency)
/Users/campshelor/miniconda3/bin/python scripts/benchmark_app.py
```

### External Configuration Required

- **Model artifacts:** `artifacts/language-v1/text_encoder.onnx` + `tokenizer.json` (separately provisioned, not in repo). See `docs/MODEL_SETUP.md` for download/export, sha256, and `verify_language_encoder.py` steps. Until then language mode stays `disabled`; prepared descriptions/examples still work.
- **Hosting:** No public deployment without explicit authorization. See `docs/DEPLOYMENT.md` for sizing and checklist.

### Repository Layout
- `backend/app/{main,config,schemas,data_store,recommendation,language}`
- `frontend/src/{app,api,state,components}`
- `data/workshop/` frozen collection (29 MB, excluded from image: `data/sources`, `data/catalogue`)
- `artifacts/scoring-v1/` versioned scoring + calibration
- `config/scoring-v1.json` and `content/prompts-v1.json` (400 prompts, `artifacts/language-v1` placeholder)

### Licences
- Clapback vectors: CC0; MusicBrainz core CC0 + tags CC BY-NC-SA 3.0; AcousticBrainz CC0 — see `data/workshop/ATTRIBUTION.md`
- Model software/checkpoints have separate terms (see `docs/MODEL_SETUP.md`)
