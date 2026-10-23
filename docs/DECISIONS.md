# Decision Log

Date format: YYYY-MM-DD. Record material changes, not silent defaults.

| Date | Decision | Rationale | Impact | Status |
|------|----------|-----------|--------|--------|
| 2026-10-21 | Stack: React 18 + TypeScript + Vite, FastAPI + Pydantic + NumPy | Recommended defaults in IMPLEMENTATION_PLAN §4; simplest for 1500-item in-memory serving | Frontend/backend scaffold | Accepted |
| 2026-10-21 | No SQLite at runtime; load JSON/F32 into memory | Plan §4: database unnecessary at 1500 rows; simplifies deployment | data_store design | Accepted |
| 2026-10-21 | Python 3.11+ required; Node 20 required | Compatibility with FastAPI/ONNX and Vite 5 | pyproject/package.json engines | Accepted |
| 2026-10-21 | Single origin in production (backend serves frontend) | Plan §4 recommended production topology | Dockerfile routing, StaticFiles | Accepted |
| 2026-10-21 | Language mode disabled by default until encoder verified | Plan §1 boundaries: do not claim language experiment ready with fake encoder | config.language_mode, bootstrap language_status | Accepted |
| 2026-10-21 | Scoring artifacts: robust median/IQR on full collection, clip ±4, no per-filter refit | Plan §5.2: fit once on frozen collection; no silent zero for missing required input | artifacts/scoring-v1/meta.json | Accepted |
| 2026-10-21 | Rhythm recipe: log2 BPM, log1p onset/dance, equal 3-group weight, negative MSE | Plan §5.2 proposed baseline; validated via feature audit (66–185 BPM, 0.13–8.22 onset, 0.65–4.18 danceability) | scoring.py | Accepted |
| 2026-10-21 | Texture recipe: 50% MFCC 1..12 (exclude 0) + 50% spectral (centroid/rolloff/flux log floor 1e-6 + ZCR log1p) | Prevents MFCC block dominance; spectral floor documented | scoring.py | Accepted |
| 2026-10-21 | Calibration: empirical reference percentiles per method/seed-count (1: all 1500×1499 pairs, 2–5: 512×samples), 1001-point tables, fixed seed 20261018, capped 99.9 | Plan §5.4 recommended convention; separate tables per seed count and per modality (text cross-modal pending) | artifacts/scoring-v1/calibration.json | Accepted |
| 2026-10-21 | Preference reranking: U = B + 0.05*mean(fits) where B is percentile/100, fits from voice_instrumental/mood_acoustic/mood_electronic class-specific values; neutral = exact base order | Plan §5.5 bounded reranker; missing predictions neutral, not exclusion | scoring.py | Accepted |
| 2026-10-21 | LAION CLAP text encoder: PyTorch laion_clap 1.1.7 blocked by broken torch libtorch_cpu.dylib on conda Python 3.13 ARM; ONNX path via HuggingFace laion/clap-htsat-unfused is intended production route | Gate in docs/MODEL_SETUP.md and verify_language_encoder.py; app remains disabled until ONNX weights provisioned | docs/MODEL_SETUP.md, language_mode | Accepted (blocker documented) |
| 2026-10-21 | Prompt bank: 400 entries (78 curated + 322 templated to meet 400–800 target), categories rhythm/vocals/instruments/texture/dynamics/production/mood/atmosphere/combo, paraphrase_group dedup | Plan §12: 400–800, cover facets, avoid Cartesian product, no stereotypes | content/prompts-v1.json, artifacts/language-v1/meta.json (placeholder) | Accepted |
| 2026-10-21 | Language artifacts: placeholder 512-d unit vectors (hash-seeded) for UI dev; real ONNX encoder separate immutable artifact with documented sha256, not downloaded at request time | Allows prepared descriptions/examples to work while live encoder blocked; no claims of real alignment | artifacts/language-v1/prompt_embeddings.f32, meta.json placeholder flag | Accepted |
| 2026-10-21 | Frontend state: single versioned localStorage adapter (key spaceday-workshop:v1), debounced writes, 20-run cap with prune warning, JSON/Markdown export, no server collection | Plan §11: one storage adapter, capped history, browser-local persistence | frontend/src/state/storage.ts | Accepted |
| 2026-10-21 | Production image excludes data/sources, data/catalogue, node_modules, caches via .dockerignore; single worker initially (memory duplication if multiple workers) | Plan §18: include only necessary workshop files + artifacts | Dockerfile, .dockerignore | Accepted |
| 2026-10-21 | Hosting: keep service awake during both 45-min sessions; provider not yet purchased; sizing based on benchmark (1 vCPU/512 MB without live encoder, 2 vCPU/2–4 GB with) | Allowance $25–50 not a guarantee; decision pending pilot + real ONNX measurement | docs/DEPLOYMENT.md | Provisional |

All material changes above were recorded promptly rather than silently changing the experiment.
