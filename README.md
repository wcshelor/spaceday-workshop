# Music Recommendation Workshop — App

**Listener patterns:** a real 32-factor collaborative SVD model is now available
for 182 catalogue songs, alongside the original three methods. It learns from
ListenBrainz song loves; switching to it shows supported songs and enables a
shared candidate pool for fair comparisons. See
[model, coverage and evaluation](artifacts/collaborative-v1/README.md).

One hosted browser app for two independent 45-minute workshops (University of Osnabrück, 15–20 adults per cohort). Students browse 1500 curated recordings (1960–2022), pick familiar seeds, compare recommendations, listen externally, reveal supporting information, and discuss reactions. An optional CLAP activity matches songs to 71 curated descriptions using real precomputed text vectors. Live free-form text search is retired from today’s demo; its code is preserved. See [description matching](docs/DESCRIPTION_MATCHING.md).

- [Product design](DESIGN.md)
- [Implementation plan](IMPLEMENTATION_PLAN.md)
- [Implementation status](docs/IMPLEMENTATION_STATUS.md)
- [Decisions](docs/DECISIONS.md)
- [API](docs/API.md)
- [Model setup](docs/MODEL_SETUP.md)
- [Works cited, data provenance, and model methods](docs/WORKS_CITED_AND_METHODS.md)
- [Presentation draft, intuition guide, and quiz bank](docs/PRESENTATION_DRAFT.md)
- [Listening pilot](docs/PILOT.md)
- [Deployment](docs/DEPLOYMENT.md)
- [Workshop runbook](docs/WORKSHOP_RUNBOOK.md)
- Data: `data/workshop/songs.json` (authoritative), `songs.csv`, `features.json`, `clap_embeddings.f32` (3,072,000 bytes, `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32`), `manifest.json`

## Guided listening flow

Choose up to five familiar songs, then carry one active starting song through
**Musical features → Listener patterns → CLAP sound → Compare**. Rhythm and texture
are two explicit feature formulas within the first step. When the listener model
is available, all methods use its supported candidate pool for a controlled
comparison; unsupported starting songs are flagged without substitution.

Each method invites prediction, external listening, separate enjoyment and
similarity reactions, and an optional explanation reveal. The optional taste
survey personalizes reflection prompts without changing rankings. Working sets,
experiments, survey answers and notes stay on the device and can be exported.
Phone layouts stack the activity; laptop layouts place the method and listening
panels alongside each other. Song-to-description matching is an optional CLAP extension using prepared
text vectors. Live text retrieval is retired from this demo.

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
# SPACEDAY_LANGUAGE_MODE=disabled  # live search retired; prepared descriptions work offline
```

### Generate / Verify Scoring Artifacts (once, after data freeze)
```sh
/Users/campshelor/miniconda3/bin/python scripts/build_app_artifacts.py   # writes artifacts/scoring-v1/meta.json + calibration.json
# Real description vectors are checked in; no encoder needed at runtime.
# To rebuild offline, see docs/DESCRIPTION_MATCHING.md.
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
- `config/scoring-v1.json` and `content/prompts-v1.json` (71 curated prompts, version `prompts-v2`; real text vectors in `artifacts/language-v1`)

### Licences
- Clapback vectors: CC0; MusicBrainz core CC0 + tags CC BY-NC-SA 3.0; AcousticBrainz CC0 — see `data/workshop/ATTRIBUTION.md`
- Model software/checkpoints have separate terms (see `docs/MODEL_SETUP.md`)
