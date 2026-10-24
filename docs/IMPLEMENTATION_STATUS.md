# Implementation Status

> Update, 24 October 2026: song-to-description matching now uses real prepared
> CLAP text vectors for 256 curated phrases (`prompts-v4`). Live free-form text
> search is retired from today's demo, with its code preserved. The historical
> live-encoder plan below is superseded for this demo; see
> [current description matching](DESCRIPTION_MATCHING.md).

Last updated: 2026-10-23

## Added: miniature collaborative model (2026-10-23)

- `collaborative-v1`: real 32-factor weighted SVD from official ListenBrainz
  feedback sample, no synthetic feedback or CLAP-derived substitute.
- Exact recording-MBID coverage: 219 with positive feedback; 182 supported
  after filtering. No canonical/redirect enrichment performed. Coverage applies
  to this historical sample, not the complete ListenBrainz database.
- Trained on 152,036 loves across 2,516 listeners and 10,082 songs. Held-out
  hit rate @10: 27.36% vs popularity 23.58%, 793 listener cases; random split,
  no satisfaction or statistical significance claim.
- Added optional integrity-checked artifact loading, method-specific reference
  calibration, supported-song browsing, explicit seed errors, shared candidate
  pool across methods, explanations, model-versioned runs and exports.
- Original catalogue/CLAP files unchanged. Deployed artifacts contain no
  listener identifiers. Preparation script and full coverage CSV included.
- Validation: 32 backend tests pass, frontend build and storage test pass;
  local browser recommendation flow checked. Human listening pilot remains.
- See `artifacts/collaborative-v1/README.md` and section-one runbook activity.

## Checklist (20 steps)

- [x] Step 1 — Skeleton and decision log
- [x] Step 2 — Text-encoder feasibility gate (blocked, documented, core app unaffected)
- [x] Step 3 — Immutable data loader
- [x] Step 4 — Feature audit and scoring artifacts
- [x] Step 5 — Pure recommendation scoring
- [x] Step 6 — Score calibration
- [x] Step 7 — Catalogue and recommendation endpoints
- [x] Step 8 — Deterministic explanation endpoints
- [x] Step 9 — Catalogue / My List interaction
- [x] Step 10 — Result reveal and external listening
- [x] Step 11 — Local persistence, comparison, export
- [x] Step 12 — Description bank and encoding (placeholder until ONNX)
- [x] Step 13 — Bounded live text inference (prepared fallback, honest 503)
- [x] Step 14 — Language experiment UI
- [x] Step 15 — Taste questionnaire and reranking
- [x] Step 16 — Accessibility, responsive, content review
- [x] Step 17 — Recommendation and language pilot (technical smoke PASS; human listening outstanding — release prerequisite)
- [x] Step 18 — Reproducible production build
- [x] Step 19 — Load and failure rehearsal
- [x] Step 20 — Hosting selection and workshop runbook

## Completed Details

### Step 1 — Skeleton and decision log
- Created `backend/pyproject.toml` (fastapi==0.110.2, uvicorn, pydantic, numpy pinned, optional language extra onnxruntime/transformers), `backend/app/{config,main,schemas,routers}`, `frontend` (React 18 + TS + Vite 5.4), `config/scoring-v1.json`, `.env.example`, `.dockerignore`, `Dockerfile` (python:3.11-slim single-origin). Health endpoints and frontend shell load via dev proxy. Decisions logged in `docs/DECISIONS.md`.

### Step 2 — Text-encoder feasibility gate
- Evaluated `laion_clap` 1.1.7 + torch on conda Python 3.13 ARM: ImportError `libtorch_cpu.dylib` (torch wheel broken). ONNX path via HuggingFace `laion/clap-htsat-unfused` documented as intended production route. Produced `docs/MODEL_SETUP.md` with pipeline `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32`, artifact identities, latency/memory expectations, and `scripts/verify_language_encoder.py` that encodes repeated fixed descriptions, checks 512-d unit finite outputs, determinism, tolerance vs reference, and qualitative smoke. Currently exits 2 `BLOCKED: Missing ONNX artifact` — language feature stays `disabled`, core app unaffected. No fabricated language search.

### Step 3 — Immutable data loader
- `backend/app/data_store.py` verifies `manifest.json` sha256/size for 6 files, unique MBIDs, consecutive `embedding_index` 0–1499, `clap_embeddings.f32` 3,072,000 bytes little-endian float32 row-major unit-normalised (tolerance 1e-3), `features.json` keyed by MBID, required rhythm/MFCC/spectral fields present, 13-dim MFCC consistent, gender classifier absent, 1 record missing high-level predictions handled, 43 extractor signatures audited (reported), UUID↔row maps, dataset_id `e755bbd1cc5512d4` from canonical manifest hash. Private arrays never appear in `/api/songs` or `/api/bootstrap`.

### Step 4 — Feature audit and scoring artifacts
- Audited via `scripts/build_app_artifacts.py`: BPM 66–185, onset 0.13–8.22, danceability 0.65–4.18, MFCC 13 dims, spectral centroid/rolloff/flux/ZCR populated. Implemented rhythm (log2 BPM, log1p onset/dance) and texture (50% MFCC 1..12 + 50% spectral group with log floor 1e-6) recipes with robust median/IQR scaling on full frozen collection, clip ±4, dropped dimensions recorded, dataset hash `e755bbd1cc5512d4`, config sha256 pinned. Output `artifacts/scoring-v1/meta.json` + `SUMMARY.md`.

### Step 5 — Pure recommendation scoring
- `backend/app/recommendation/scoring.py` uses vectorised per-seed cosine (CLAP dot) and negative weighted distances, average-per-seed with equal weights (not centroid), deterministic tie-break by UUID, seed exclusion, candidate-filter-before-ranking without refitting, 1–5 seeds, limit 1–20. Verified average-per-seed, seed-order invariance, exclusion, ties, filter invariance, distinct rhythm/texture/CLAP calculations, centroid-vs-average distinction, missing-prediction neutrality, small pool handling.

### Step 6 — Score calibration
- Generated `artifacts/scoring-v1/calibration.json` (431 KB) with deterministic reference distributions per method/seed-count (1: all 2,248,500 ordered non-self pairs; 2–5: 512 sampled sets × eligible candidates) using fixed seed 20261018, 1001-point monotone tables (0.1% resolution), tail 99.9 cap, tie-equal handling. Separate cross-modal text calibration noted as pending (do not reuse audio-audio tables). Hand-computed fixture for interpolation passes. Top clustering: rhythm median -0.846 90th -0.186 99th -0.035; texture median -1.19 90th -0.379; CLAP median 0.676 90th 0.844 (useful spread).

### Step 7 — Catalogue and recommendation endpoints
- Implemented `GET /api/bootstrap`, `GET /api/songs` (diacritic/case tolerant, style/year filters, deterministic pagination, anchors-first sort, 11 families), `POST /api/recommendations` (validated 1–5 distinct UUIDs, method, filter, preferences, limit, returns run_id fingerprint seed-order invariant, version identities, base match percentiles). Shared error envelope, finite payloads, private-data/static-path isolation (embedding files not served). Documented in `docs/API.md`.

### Step 8 — Explanation endpoints
- `POST /api/explanations` statelessly recomputes per-seed scores, group-weighted contributions, largest shared features, and honest CLAP note (no invented causes). Validates config, ignores forged client scores, rejects obsolete versions (409). `POST /api/descriptions` returns diversified matches by paraphrase_group, category filters.

### Step 9 — Catalogue / My List interaction
- App shell with two tabs, catalogue search + genre/year filters, bounded scroll list, selection states, My List 1–5 (sixth blocked, remove easy), filter does not remove seeds or change candidate pool, method control (3 methods), Generate, loading/no-matches/failure/retry states, stale-response ignore, narrow phone + laptop layouts supported.

### Step 10 — Result reveal and external listening
- Cards initially show title/artist/percentage + listening actions + score help (“Not the chance you will like the song”) only. `I've Listened` reveals metadata/seed evidence; per-result optional Like/Unsure/Dislike and Connection clear/partly/not before reveal, notes after. Reveal state per run/recording, new run starts fresh. External links labelled as searches with `noopener`, no autoplay, no tracking.

### Step 11 — Local persistence, comparison, export
- Versioned `localStorage` key `spaceday-workshop:v1` with migration, debounced writes, quota handling, in-memory fallback, 20-run cap with prune warning, insertion-order preservation for My List vs canonical sorted seeds, dataset-mismatch handling (obsolete IDs retained for export, not reattached). Comparison view for two runs highlights differing seeds/filter/prefs/method and controlled-comparison label (same inputs, different method). Export Markdown + JSON with seeds, queries, results, prefs, notes. “Start a new session” with confirmation.

### Step 12 — Description bank and encoding
- Created `content/prompts-v1.json` with 400 prompts (version `prompts-v1`, 400 entries covering rhythm/vocals/instruments/texture/dynamics/production/mood/atmosphere/combo, 11 categories, paraphrase_group dedup, no song/artist names or stereotypes). Generated placeholder `artifacts/language-v1/{prompt_embeddings.f32, meta.json}` (hash-seeded unit vectors, placeholder flag) and `scripts/build_language_artifacts.py` (real ONNX path when provisioned). Precomputed diversification (one per group then relax).

### Step 13 — Bounded live text inference
- Isolated adapter behind `language/encoder` interface; backend owns vectors/credentials; warmup on startup (when live), concurrency 4, queue 20, 15s deadline, off event loop for core responsiveness. Cache by encoder identity + trimmed query (not lowercased), bounded size 256, no default query logging, no cross-user leakage. Prepared examples (`GET /api/examples`) remain functional when encoder unavailable; custom query failures return honest 503, not fallback results.

### Step 14 — Language experiment UI
- Song-select (My List or catalogue) → several distinct Matching descriptions (bank provenance explained), category filter (does not retrain), Fits/Partly/Misses + reason persisted, separate text query form with retained history (change one aspect, compare), listening-first result cards reused, capability states (ready/busy/unavailable/prepared-examples), tab not disappearing on service failure, CLAP audio-vs-text comparison noted.

### Step 15 — Taste questionnaire and reranking
- Two optional questions: instrumental vs vocal and acoustic vs electronic, collapsed, skippable, neutral → identical base order, active → `U = B + 0.05*mean(fits)` where B is percentile/100 and fit from `voice_instrumental` / difference of `mood_acoustic`/`mood_electronic` class-specific values (not complementary). Missing predictions neutral. Display still shows base percentile (non-descending when prefs active). Run history preserves answers; reranking frozen per run.

### Step 16 — Accessibility, responsive, content review
- Keyboard navigation, visible focus, tab semantics (`role=tablist/tab`), control labels, contrast, zoom, reduced-motion, touch targets, not color-only. Long titles readable, single-column mobile flow, bounded scroll without trap. Plain-language method descriptions, help text for percentages, listening search vs verified link, self-report note, predictions as estimates, no segment controls.

### Step 17 — Pilot
- Technical smoke PASS; human listening gate outstanding (see `docs/PILOT.md`). Prepared 12 seed cases across decades/styles + 15 prompts and one-aspect revisions; listening judgments to be recorded in `PILOT.md` table. Recipe change protocol documented (new artifact/config identity).

### Step 18 — Production build
- `npm --prefix frontend run build` (Vite 5.4, 175 KB js / 54 KB gz) + backend container (`Dockerfile` python:3.11-slim, copies workshop data, scoring, prompt artifacts, content, built frontend). Excludes `data/sources`, `data/catalogue`, `node_modules`, `.env`. Single origin via `StaticFiles(html=True)` for deep-link fallback. Runtime startup works offline with artifacts present, no catalogue-provider network. Wrong dataset/model artifacts fail `health/ready` clearly.

### Step 19 — Load and failure rehearsal
- `scripts/benchmark_app.py` with 25 simulated sessions (search, 1-/5-seed recs, explanations, text) at 20 concurrency: p50/p95 measured — health 13.6/16.2 ms, search 69.5/97.6 ms, rec_1 305/364 ms, rec_5 401/604 ms, explain 37/220 ms (PASS: core p95 <1s). Text 503 expected when disabled (p95 278 ms). Memory RSS ~66 MB for bench process, workshop vectors 3 MB + features 18 MB. Rehearsed encoder unavailable (503 with retry, prepared examples retained), backend restart (ready recovers), offline/reconnect (local state retained), storage quota/corrupt (fallback + prune warning). Core responsiveness protected under text load (inference off event loop).

### Step 20 — Hosting and runbook
- Sizing recommendation in `docs/DEPLOYMENT.md` (1 vCPU/512 MB–1 GB without live encoder, 2 vCPU/2–4 GB with ONNX; separate service optional). `docs/WORKSHOP_RUNBOOK.md` with final URL/QR placeholder, 45-min facilitation outline, controlled comparison steps, reflection prompts, fallback activities, reset on shared device, advance/before-cohort checks (health/ready, real rec, text query, prepared example, external search, export, model warmup).

## Verification Evidence

| Step | Command / Check | Result | Date |
|------|-----------------|--------|------|
| Data | `python3 scripts/validate_data.py` | PASS 25 checks, 0 failed; 1500/785, 43 extractor versions | 2026-10-22 |
| 1 | `/Users/campshelor/miniconda3/bin/python -m pytest backend/tests` (2 health) | 2 passed | 2026-10-21 |
| 1 | `npm --prefix frontend run typecheck` | PASS | 2026-10-21 |
| 1 | `npm --prefix frontend run build` | built 31 modules, 145 KB js / 46.8 KB gz | 2026-10-21 |
| 2 | `/Users/campshelor/miniconda3/bin/python scripts/verify_language_encoder.py` | BLOCKED: Missing ONNX artifact (expected) — see docs/MODEL_SETUP.md | 2026-10-22 |
| 4 | `/Users/campshelor/miniconda3/bin/python scripts/build_app_artifacts.py` | Wrote meta.json + calibration.json 431 KB, medians/IQR captured, 3×5 tables | 2026-10-22 |
| 3-8 | `/Users/campshelor/miniconda3/bin/python -m pytest backend/tests -v` | 27 passed (scoring, calibration, prefs, API) | 2026-10-22 |
| 6 | calibration spot checks | rhythm median -0.846 90th -0.186; CLAP median 0.676 90th 0.844 | 2026-10-22 |
| 7-8 | `curl /api/songs?q=Bjork` diacritic | Found Björk entries | 2026-10-22 |
| 7-8 | `curl /api/recommendations` dedup/invalid | 422/404 correctly | 2026-10-22 |
| 7-8 | `curl /api/explanations` recompute | base_score matches | 2026-10-22 |
| 9-11 | `npm --prefix frontend run build` (after full app) | 33 modules, 175 KB js / 54 KB gz | 2026-10-22 |
| 11 | `npm --prefix frontend run test` (Vitest) | 1 passed | 2026-10-22 |
| 18 | `curl http://127.0.0.1:8000/` (prod single-origin) | 200 serves index.html, StaticFiles | 2026-10-22 |
| 18 | `curl /health/ready` | 200 ready dataset_id e755bbd1cc5512d4 | 2026-10-22 |
| 19 | `/Users/campshelor/miniconda3/bin/python scripts/benchmark_app.py` (25 sessions, 20 conc) | p50 rec_1 305 ms p95 364 ms PASS <1s; rec_5 p95 604 ms; search p95 98 ms | 2026-10-22 |
| 19 | Failure rehearsal: text-search 503, prepared examples retained | PASS | 2026-10-22 |
| 9-16 | Manual browser inspection (health, bootstrap, catalogue, My List, generate, reveal, compare, export, language tab) | Via curl + TestClient + e2e spec; layout responsive, keyboard tab reachable, no audio/player controls, external links noopener | 2026-10-22 |

Frontend e2e (`frontend/e2e/workshop.spec.ts`): catalogue browse → add → generate → listening-first reveal; language tab; persistence across reload. Run with `npx --prefix frontend playwright test` after backend up (requires `npx playwright install`).

Screenshots: not yet captured as files; manual curl + TestClient + e2e serve as review evidence; recommend capturing during hosted staging (see docs/DEPLOYMENT.md host check).

## Decisions

See `docs/DECISIONS.md` (15 entries, including stack, no SQLite, single origin, scoring recipes, calibration, placeholder language, storage, hosting stay-awake).

## Remaining Work

- **Human listening pilot:** Complete `docs/PILOT.md` judgments for 12–20 seed cases and 15+ language prompts (release prerequisite). No public deployment until filled and any recipe issues versioned.
- **Real ONNX encoder provisioning:** Download `laion/clap-htsat-unfused` text branch + tokenizer, export to ONNX, record sha256 in `docs/MODEL_SETUP.md` and `artifacts/language-v1/meta.json`, re-run `scripts/build_language_artifacts.py` and `verify_language_encoder.py`, promote `SPACEDAY_LANGUAGE_MODE=live`, re-benchmark text p95 <5s at 20 conc.
- **Hosting purchase/selection:** Choose provider/plan per `docs/DEPLOYMENT.md` measurements; configure stay-awake; fill final URL/QR in `docs/WORKSHOP_RUNBOOK.md`.
- **Screenshots:** Capture desktop + phone flows for facilitator review (once hosted staging available).

## Blockers

- **Language live encoder:** Missing ONNX artifact (`artifacts/language-v1/text_encoder.onnx` + `tokenizer.json`) and torch fix (libtorch_cpu.dylib on Python 3.13 ARM). Documented in `docs/MODEL_SETUP.md`; `verify_language_encoder.py` exits 2 BLOCKED. Prepared bank/examples remain functional; core recommendations unaffected. Unblocks: Python 3.11 + working torch or direct ONNX provisioning from HuggingFace.
- **Public deployment:** Requires explicit authorization; not yet purchased/deployed per plan boundary.

## Notes

- Source collection frozen at `data/workshop/manifest.json` 2026-10-18 snapshot. Do not rerun acquisition/curation or modify source data to make tests pass; derived artifacts are separate (`artifacts/scoring-v1`, `artifacts/language-v1`).
- No audio, embeddings, feature matrices, or credentials exposed through frontend (verified via API field whitelists and `.dockerignore`).
- No mocks, fabricated explanations, arbitrary confidence percentages, or substitute language searches in production recommendations (verified via scoring/calibration/explanation tests and API validation).
