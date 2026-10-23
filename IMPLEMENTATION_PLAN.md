# Workshop app — detailed implementation plan

Prepared 21 October 2026. Audience: the OpenCode architect and implementation agent, or another coding agent working in this repository.

This is the requested full implementation handoff. `DESIGN.md` describes the product; this document defines a concrete implementation sequence and recommended defaults. Existing user decisions take precedence. Recommendations below fill implementation gaps; they must not be presented as previously user-approved choices. Record material changes in a small decision log rather than silently changing the experiment.

## 1. Objective and boundaries

Deliver a hosted browser app for two independent 45-minute workshops, each with 15–20 adults, approximately ages 20–50, at the University of Osnabrück. Students browse a fixed collection, select familiar seeds, compare recommendations, listen externally, reveal supporting information, and discuss their reactions. A second tab supports genuine CLAP description matching and student-written text-to-music retrieval.

The final app must support both tabs. Build and verify the song-recommendation path first, while resolving text-encoder feasibility early. A working first milestone is not a substitute for completing the language experiment.

Non-negotiable boundaries:

- No audio uploads, downloads, hosting, embedded players, or Spotify/YouTube extraction.
- No new audio analysis, segment reconstruction, Discogs embeddings, or retraining.
- No runtime catalogue calls to MusicBrainz, AcousticBrainz, or Clapback.
- No accounts, central collection of student answers, or facilitator surveillance dashboard.
- No browser access to raw vectors, full feature matrices, source caches, or model credentials.
- No claims that similarity percentages are probabilities of enjoyment.
- No fabricated causal explanations for CLAP choices or fallback results for failed custom queries.
- No public deployment or paid purchase as an incidental part of implementation. Prepare a reviewable deployment package and select the actual hosting target separately.

The source collection is frozen. Do not rerun the acquisition or curation commands during app development. New derived scoring/model artifacts belong in separate directories.

## 2. Read this context, then stay focused

### Must read before architecture or implementation

1. `DESIGN.md`.
2. `data/README.md`.
3. `data/workshop/manifest.json` and `data/workshop/ATTRIBUTION.md`.
4. `data/validation.json` and the coverage/limitations sections of `data/CURATION.md`.
5. Representative records from `data/workshop/songs.json` and `features.json`; inspect schemas and statistics programmatically instead of opening the entire files in context.

### Can use the following summaries

- `scripts/prepare_data.py`: downloads and caches the frozen source snapshot and batched MusicBrainz metadata. Not part of runtime.
- `scripts/curate_data.py`: selects recordings, joins existing vectors/features, and writes the final package. Not a recommendation engine. Its editorial familiarity bands are not measured popularity.
- `scripts/validate_data.py`: verifies the prepared collection and writes the data audit. It currently passes 25 integrity checks. Running it rewrites the audit; it does not evaluate recommendation quality.
- `data/catalogue/` and `data/sources/`: larger preparation caches. Do not ship or index them for the app.

### Read only if blocked

- Exact preparation-script functions relevant to an identified schema/provenance question.
- A particular source record when investigating a concrete anomaly.
- Official documentation for the selected text encoder, frontend/backend tools, and deployment platform.

Do not perform open-ended repository exploration. If the listed context is insufficient, identify the additional file, decision, or output needed. Every agent editing code must read the exact files it will modify and the focused tests it will run. The architect should split the steps below into small tasks; an implementer should not receive the entire repository as mandatory context for every task.

## 3. Verified starting point

There is no application skeleton or package setup yet. Existing code consists of Python data-preparation and validation scripts.

| Item | Current value |
| --- | --- |
| Recordings / primary artists | 1,500 / 785 |
| Date range | 1960–2022 |
| Broad style groups | 11, with overlapping original tags retained |
| Editorial familiarity bands | 232 recognisable anchors; 445 established-artist deeper cuts; 823 discovery candidates |
| Recording identity | MusicBrainz recording UUID |
| Audio embeddings | 1,500 × 512, little-endian float32, row-major, unit-normalised |
| Vector file | `data/workshop/clap_embeddings.f32`, 3,072,000 bytes |
| Pipeline | `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32` |
| Musical measurements | Baseline rhythm/timbre descriptors available for all recordings |
| High-level predictions | Available for 1,499 recordings; one must remain usable without them |
| Extractor-version signatures | 43; a compatibility audit is required before scoring |
| App-ready package | Approximately 29 MB, including duplicate readable vector representation |

The binary row number is `songs.json[*].embedding_index`, not an arbitrary sorted UUID order. `features.json` is keyed by recording UUID. Do not independently sort one file and assume alignment survives.

Actual measurements inspected on 21 October:

- `rhythm.bpm`: approximately 66–185 BPM; all 1,500 populated. This narrow observed range does not guarantee correct beat tracking or absence of half/double-time ambiguity.
- `rhythm.onset_rate`: approximately 0.13–8.22 onsets/second; all populated.
- `rhythm.danceability`: approximately 0.65–4.18. It is a measured descriptor, **not a 0–1 classifier probability**.
- MFCC mean and covariance, spectral centroid/rolloff/flux, zero-crossing rate, spectral complexity, average loudness, and dynamic complexity are populated for all recordings.
- Scalar tonal key fields occur on 1,499 recordings; one uses nested `tonal.key_edma.*`. Tonal similarity is not required for the initial methods.
- High-level predictions include voice/instrumental, acoustic, electronic, several moods, timbre, and genre classifiers. Read a named class from `.all`; `.probability` refers to the winning class, which may be its opposite.

Integrity passing does not establish musical quality, source-identity correctness, or calibration of classifier scores. Retain the documented limitations.

## 4. Recommended architecture and repository layout

Recommended implementation defaults:

- **Frontend:** React + TypeScript + Vite, ordinary CSS with reusable tokens/components. Use a small accessible component dependency only where it solves a real interaction need.
- **Backend:** FastAPI, Pydantic request/response schemas, NumPy for vectorised scoring.
- **Runtime data:** load the frozen catalogue, features, scoring artifacts, and vectors into memory once per application process. At 1,500 recordings, a database is not necessary. This intentionally simplifies the earlier provisional SQLite suggestion; add SQLite only if a concrete runtime requirement justifies it.
- **Student state:** browser-local persistence through one versioned storage adapter.
- **Language encoder:** an isolated adapter, optionally a separately deployed private service. Backend owns retrieval and access to song vectors.
- **Production:** one public origin. Backend serves the built frontend or a reverse proxy routes `/api` and static assets. Separate dev servers are fine with a development proxy.

Pin compatible dependency versions and commit lockfiles during scaffolding. Select a Python version compatible with the encoder toolchain; do not assume the laptop's current Python is supported by all model dependencies. Check the installed Node version against the selected Vite release. Do not install heavyweight inference packages in the core backend environment before the encoder feasibility check.

Proposed layout, to establish in Step 1:

```text
backend/
  pyproject.toml
  app/
    main.py, config.py, schemas.py
    data_store.py
    catalogue.py
    recommendation/{registry,features,scoring,calibration,explanations,preferences}.py
    language/{encoder,service,prompts}.py
  tests/
frontend/
  package.json
  src/
    app/, api/, state/, components/, features/
  tests/
  e2e/
config/
  scoring-v1.json
content/
  prompts-v1.json
artifacts/
  scoring-v1/
  language-v1/
scripts/
  build_app_artifacts.py
  build_language_artifacts.py
  verify_language_encoder.py
  benchmark_app.py
docs/
  DECISIONS.md
  API.md
  MODEL_SETUP.md
  PILOT.md
  DEPLOYMENT.md
  WORKSHOP_RUNBOOK.md
Dockerfile, .dockerignore, .env.example
```

These are proposed files, not existing ones. Avoid creating empty modules just to reproduce the tree. Keep related code together until a step genuinely needs separation.

Proposed language default: English interface and prepared prompts, with Unicode-safe artist/title display and input. Do not add a translation service. State the supported query language honestly; German retrieval or a German interface can be added only with corresponding content and model evaluation, rather than assumed from the venue location.

## 5. Scoring contract to implement

### 5.1 Shared rules

Use method IDs `rhythm-v1`, `texture-v1`, and `clap-v1`. Every method provides per-seed candidate scores. For seeds `S`, the base score is the arithmetic mean of those scores, with equal seed weights. Do not substitute a centroid distance for the average of distances, or normalise an averaged CLAP seed vector and call the result equivalent to average cosine similarity.

Default candidate pool: all 1,500 recordings except seeds. Optional recommendation filters are explicit and separate from catalogue browsing. Apply candidate eligibility before returning results, without refitting normalisers or percentile references. Use descending base score, then recording UUID as a deterministic tie-break. Initially return five results; support a bounded limit up to 20 from the same ranking.

Different songs by the same artist may appear. Do not silently introduce an artist-diversity reranker in the controlled comparison. The collection already caps artist concentration. Exact selected seeds are excluded by UUID; the collection's artist/title deduplication is retained rather than inventing broader cover-song equivalence.

### 5.2 Feature preprocessing

Fit normalisation once on the complete frozen collection. For each selected scalar dimension, apply its configured transform, then robust scale `(x - median) / IQR`. Drop a dimension with effectively zero IQR and record that choice. Clip scaled values to ±4 as an initial outlier policy. Persist medians, IQRs, transforms, clipping bounds, feature order, and dimension weights.

Do not refit based on seeds, visible rows, recommendation filters, or current users. Do not silently treat a missing value as zero. Current required dimensions are populated, so missing required input indicates an incompatible release and should fail artifact validation.

Initial **rhythm** recipe: equally weight three groups—`log2(BPM)`, `log1p(onset_rate)`, and `log1p(rhythm.danceability)`. Calculate mean squared scaled difference across those three groups; the per-seed similarity is its negative. Do not include loudness as a hidden proxy for rhythmic energy. Describe the method as rhythm/activity similarity and mention tempo-estimation limitations. Do not implement octave-equivalent tempo matching unless the pilot deliberately selects and versions that change.

Initial **texture** recipe: 50% weight to a timbral group and 50% to a spectral group. The timbral group is the mean squared scaled difference of MFCC mean coefficients 1 onward, excluding coefficient 0 as a starting choice to reduce level dominance. Determine and freeze the actual coefficient count in the audit. The spectral group is the mean squared scaled difference of log-transformed spectral centroid, rolloff, and flux plus `log1p` zero-crossing rate. Use a documented positive floor for log inputs. The overall similarity is the negative weighted distance. This grouping prevents a many-dimensional MFCC block from dominating accidentally.

These are proposed baseline recipes, not validated musical truths. Step 4 audits compatibility; Step 17 evaluates whether they produce useful contrasts. Any recipe change creates a new artifact/config identity and updates explanations and calibration together.

### 5.3 CLAP similarity

Use dot products of the existing unit vectors for per-seed cosine similarity. For text retrieval, L2-normalise the compatible text output and dot it against the same audio matrix. Reject non-finite, wrong-sized, or zero-norm text output. Preserve raw scores internally and their model/pipeline identities.

### 5.4 Match percentages

Recommended implementation of the design's proposed convention: an empirical reference percentile, displayed to one decimal place as **Match score**. Help text: “How strong this computed similarity is compared with reference comparisons in this collection. It is not the chance you will like the song.” Different methods' percentages are not interchangeable perceptual quality measurements.

For one seed, use the fixed distribution of all distinct non-self unordered song pairs for that method. For seed counts 2–5, use 512 deterministic, uniformly sampled sets of distinct catalogue IDs for each count, average per-seed similarities, and collect eligible candidate scores excluding the sampled seeds. Use a fixed documented random seed. Persist compact monotone percentile tables, sample parameters, and tail/tie handling. A small exact fixture should test the percentile implementation independently of the production table approximation.

Percentile interpolation must be monotone; equal scores get equal percentiles. Filtering results must not alter the score mapping. Round for display only, cap non-self displayed values at 99.9%, and do not manufacture separation when top results tie. Inspect whether useful results all bunch near the top; discuss the convention in the pilot rather than replacing it with arbitrary percentages.

Text queries have a different cross-modal score distribution. Do not use the audio-to-audio percentile table for text-to-audio or audio-to-description results. Build separate, explicitly named text reference tables from the frozen prompt bank. Explain that these percentiles are relative to that prompt reference, not a universal calibration for arbitrary language.

### 5.5 Optional taste questions

First guided comparison defaults to biases off. Proposed first release supports two defensible questions: preference for instrumental versus vocal music, and acoustic versus electronic sound. Answers are optional and skippable; neutral answers produce the identical seed-only ranking. Defer familiarity/novelty and generic “energy” controls until there is a defensible signal. Editorial obscurity is not personal unfamiliarity.

Use class-specific values from `voice_instrumental.all` and `mood_acoustic.all` / `mood_electronic.all`. Read and test the actual class names. Missing predictions produce a neutral contribution and a visible explanation after reveal, not exclusion of that recording.

Recommended bounded reranker: convert the base similarity to its fixed reference percentile `B` in [0,1]. Define each active preference fit in [-1,1]; use the sign of the student's answer to favour the requested class. For the acoustic/electronic question, use the difference of the two corresponding class scores; they are separate classifiers, not complementary probabilities. Rank by `U = B + 0.05 * mean(active preference fits)`, with the strength versioned. No active answers means `U = B` exactly.

Bypass reranking entirely when no preference is active, preserving the exact base ordering even if a percentile table maps distinct raw scores to the same value. For active preferences, break equal utilities by raw base score and then recording UUID. Display rounding never participates in ranking.

Continue displaying the **base** match percentile, with global copy explaining that active preferences can reorder results. Therefore percentages need not be descending when preferences are enabled. Reveal the preference contribution separately. Do not call `U` a probability or silently change the match-percentage definition. This is a proposed default to validate in the pilot.

### 5.6 Explanations

Feature methods can expose exact scoring components: selected seed, measured values, transformed differences, group weights, largest shared features, and meaningful differences. Numerical evidence should agree with the ranking calculation. A dimension with the smallest distance is an arithmetic similarity, not proof it caused enjoyment.

CLAP explanations show strongest seed connections and explicitly labelled matching descriptions once available. They must not say “recommended because of warm vocals” merely because a retrieved description mentions them. Additional acoustic observations may be shown as observations, clearly distinct from CLAP's scoring mechanism. No language model is needed to write the feature explanations; use accurate templates.

## 6. UI and API contracts

### Public API outline

| Endpoint | Responsibility |
| --- | --- |
| `GET /api/bootstrap` | Dataset/scoring versions, supported methods, filter vocabulary, year bounds, score help, attribution links, language capability status |
| `GET /api/songs` | Whitelisted catalogue fields; search, genre/year filters, deterministic pagination/sorting |
| `POST /api/recommendations` | Validated 1–5 seed IDs, method, explicit candidate filter, preference snapshot, limit; return ranked public results and run/config identities |
| `POST /api/explanations` | Recompute explanation for a requested result using its immutable run configuration; do not require server-side student storage |
| `POST /api/descriptions` | Closest prepared descriptions for a selected recording and optional description categories |
| `POST /api/text-search` | Encode a bounded text query and retrieve audio neighbours; return actual query/config identities |
| `GET /api/examples` | Versioned prepared language searches usable without live encoding |
| `GET /health/live`, `GET /health/ready` | Process health versus validated data/artifact readiness; return language status separately |

Recommended request bounds: distinct seed UUIDs, 1–5 items; result limit 1–20; query 1–500 Unicode characters after trimming; reject rather than silently truncate a model-token overflow. Keep pagination bounds finite. Unknown IDs/methods, inverted year ranges, duplicate seeds, malformed preference values, and inconsistent version references produce structured errors.

Define one shared error envelope, for example `{code, message, retryable, request_id}`. Use suitable HTTP statuses: validation 422, missing resource 404, incompatible release/run 409, throttling 429, unavailable encoder 503, and upstream deadline 504. Never return an empty successful recommendation response to disguise a failure.

Public result cards initially need only recording ID, title, artist, match percentile, rank, and the existing listening search URLs. The API may also return opaque reproducibility/config identifiers. Do not return raw embedding arrays or the full source song object. The catalogue endpoint can expose metadata for browsing; the listening-first reveal prevents priming in the result UI, not cryptographic secrecy from students who inspect network requests.

Explanations must validate/recompute the submitted run configuration rather than trusting client-supplied scores. A canonical configuration fingerprint identifies seed IDs, method, dataset/scoring/calibration versions, candidate filters, and active preferences. Seed-order permutations must not change rankings or fingerprints, even if My List preserves an insertion order visually.

Text and prepared-example queries need a query hash and encoder/prompt versions as applicable. If later explanation requests need an already-computed text vector, use a bounded backend query cache with explicit expiry; on a cache miss, recompute from the original query or return an honest availability error. Do not send the vector to the browser or label a newly computed search as an unchanged old run.

### Interface structure

Desktop: catalogue/search and filters, a persistent My List panel, and a result/comparison area. Keep the list scroll area bounded without trapping keyboard users. Mobile: catalogue, selected-list drawer or section, and results in a readable single-column flow. Avoid a dense spreadsheet appearance, tiny targets, or horizontal result tables on phones.

Use two clearly named tabs: **Song recommendations** and **Describe and discover**. Keep the method controls explicit and the technical detail expandable. Start with a short instruction to pick one song. Do not autoplay or open external services automatically.

After generating a result, show title/artist/percentage and listening actions only. Clicking **I've Listened** reveals metadata and evidence; the student may optionally record a reaction first but is never forced to answer. External links open with appropriate `noopener` protections and are labelled as searches. A self-report click does not claim playback verification.

Display retrieval errors alongside retained results/state, with a retry action. While a new request runs, prevent duplicate submissions and ignore stale responses. Do not overwrite an existing run when seeds, method, or filters change; make the current setup and the saved result's setup visibly distinguishable.

## 7. Ordered implementation tasks

Each step specifies its prerequisites, focused context, deliverable, and verification. Complete a coherent task, report evidence, then continue. If a step needs changes in an earlier component, update its relevant tests and versioned artifacts; do not broaden unrelated work.

### Step 1 — Establish the application skeleton and decision log

**Depends on:** documentation review only.

**Read:** this document Sections 1–6, `DESIGN.md`, root `README.md`, `.gitignore`.

Create minimal frontend/backend projects using the recommended architecture, unless a concrete compatibility check requires a different choice. Pin dependencies and runtime requirements. Add `.env.example` with documented names and harmless values. Define backend settings for dataset/artifact paths, language mode, encoder endpoint, request deadlines, and allowed development origins. Default language mode should be explicitly disabled until verified.

Add development instructions and a concise decision log stating architecture choices, what remains provisional, and why runtime SQLite is omitted initially. Preserve existing data scripts and files. Do not put `data/workshop` inside the frontend public directory.

**Done when:** the backend serves health and a frontend shell loads through the dev proxy; clean installation and frontend typecheck/build succeed; no runtime source-data downloads occur. Proposed checks: `python -m pytest backend/tests`, `npm --prefix frontend run typecheck`, and `npm --prefix frontend run build`, with actual package commands recorded.

### Step 2 — Prove the text-encoder route early

**Depends on:** Step 1's settings and isolated environment convention; can precede most UI work.

**Read:** `data/workshop/manifest.json`, `data/README.md`, current official Clapback encoder documentation/source. Do not open the source-data caches.

Inspect the reference `clapback-embed` implementation at a pinned release/commit. Determine how to obtain or export the paired **text** encoder and tokenizer for this exact pipeline. Check software/checkpoint terms, required Python/ONNX libraries, artifact identities, tokenisation, text truncation behaviour, normalisation, memory, and CPU latency. Do not assume installing the tiny Python package downloads runnable model artifacts.

The publisher currently documents separate exported model artifacts and a verification/export workflow; treat this as a feasibility gate, not a promise that the installed package is production-ready. We only need text inference, not audio inference. Evaluate whether the reference package or a small adapter to verified exported text artifacts is the simpler deployment choice.

Produce `docs/MODEL_SETUP.md`, `scripts/verify_language_encoder.py`, and a small adapter interface. The check should encode repeated fixed descriptions, verify finite 512-dimensional unit outputs, compare against the pinned reference's text outputs within a documented tolerance, and record hashes/versions. Also perform a qualitative text-to-song smoke test on a small named set; a successful shape check alone does not establish useful alignment. Do not claim perfect checkpoint compatibility from arbitrary semantic matches.

**Done when:** the encoder can be reproduced in its documented environment, model/tokenizer artifacts and identity are recorded, and memory/latency are measured. If blocked, record the precise missing artifact or licence/compatibility issue and continue independent core steps. The language feature stays explicitly unavailable until this gate passes; do not substitute text embeddings of catalogue tags.

### Step 3 — Implement the immutable data loader

**Depends on:** Step 1.

**Read:** manifest, representative songs/features, relevant checks in `scripts/validate_data.py`.

Implement `data_store.py` to verify manifest hashes, catalogue/feature identities, consecutive indexes, matrix byte length/dtype/endianness, finite values, unit norms, and required feature presence. Build explicit UUID↔row maps. Load read-only structures once at startup. Derive a dataset ID from canonical manifest content or its hash, not just the snapshot date. Report a clear readiness failure on corruption or incompatible artifacts.

Expose a whitelisted public catalogue representation; retain vectors, raw hashes, prediction payloads, and source paths privately. Set up a small independent fixture with known UUIDs/vectors for tests.

**Done when:** reordered catalogue rows are handled by explicit indexes, corrupted/missing data fails readiness, a wrong-size matrix cannot start, and private arrays never appear in catalogue JSON. The frozen source checksums remain unchanged.

### Step 4 — Audit features and build the scoring artifacts

**Depends on:** Step 3.

**Read:** required measurement/prediction schemas, this document Section 5.2, `data/validation.json`. Read individual source records only for identified compatibility anomalies.

Generate a focused feature audit: coverage, vector dimensions, ranges, non-finite/missing/constant dimensions, and distributions by sufficiently populated extractor version. Compare feature units and names across signatures. Tiny version groups are reported without pretending to support meaningful statistical comparisons. Inspect obvious outliers and the exceptional tonal-key shape. Do not fix scale problems by changing the frozen source files.

Implement the initial rhythm and texture recipes. Persist transformed matrices, normalisers, group/dimension weights, dropped dimensions, dataset hash, config identity, and a human-readable summary under `artifacts/scoring-v1/`. If units are demonstrably incompatible, use a coherent supported subset of features or document explicit conversions. Do not silently normalise each extractor version separately and erase potential real musical differences.

**Done when:** all 1,500 rows are represented for both baseline methods; independently calculated small-fixture distances match; scaling is invariant to runtime filters; artifact/model/source mismatches fail loading. Freeze the chosen recipe before generating calibration.

### Step 5 — Implement pure recommendation scoring

**Depends on:** Steps 3–4.

**Read:** scoring config/artifact schema, Section 5.1–5.3, data-loader interface.

Implement method registry and deterministic scoring functions without HTTP or UI dependencies. Use exact vectorised comparisons; approximate vector indexes are unnecessary. Return per-seed scores, aggregate base scores, and ordered candidate IDs. Validate seed count/identity and filter state. Exclude seeds and use the fixed tie-break.

**Done when:** an independent fixture proves average-per-seed behaviour, seed order invariance, exclusion, deterministic ties, candidate-filter invariance for retained items, and distinct rhythm/texture/CLAP calculations. Include a fixture where centroid distance would give a different answer to catch that substitution. Handle a candidate pool smaller than the requested limit honestly.

### Step 6 — Build and test score calibration

**Depends on:** Step 5; language calibration follows Step 12.

**Read:** Section 5.4 and the scoring artifact contract.

Generate and version reference distributions/tables for each song method and seed count 1–5, using the specified deterministic sampling. Exclude self comparisons correctly. Store generation parameters, table approximation, ties, and checksums. Add explicit API score metadata explaining the reference and display convention.

**Done when:** calibration is reproducible, monotone, independent of current result filters, and correct on a hand-computed fixture. No UI shows `cosine × 100` or a random confidence value. Record top-result percentage clustering for the pilot.

### Step 7 — Implement catalogue and recommendation endpoints

**Depends on:** Steps 3, 5, 6.

**Read:** proposed API contracts and public field whitelist.

Implement bootstrap, catalogue, and recommendations routes with schema validation and shared errors. Catalogue text search should be case/diacritic tolerant and include title and artist. Default sort can put editorial anchors first, then artist/title/UUID, with an explicit “Familiar starting points” description rather than a popularity claim. Pagination is deterministic. Genre filtering uses the 11 broad primary style groups initially; expose original overlapping tags as supplementary metadata without promising an exhaustive genre taxonomy.

Return immutable run configuration, version identities, base match scores, and necessary public result fields. Never return full internal song dictionaries directly. Document filters and boolean combination semantics in `docs/API.md`.

**Done when:** invalid input, empty catalogue matches, insufficient candidates, dataset mismatch, and normal recommendations have focused API tests. Browser-accessible routes do not serve embedding files or source caches.

### Step 8 — Implement deterministic explanation endpoints

**Depends on:** Step 7.

**Read:** Section 5.6, scorer output, and run identity rules.

Add stateless recomputation of feature explanations and strongest seed links. Return readable units and carefully worded comparisons, plus optional expandable arithmetic. For a group with several dimensions, preserve its configured group weight when presenting contributions. Report both a strong connection and an important difference where supported.

For CLAP, return exact seed similarities and an honest explanation of audio embedding proximity; attach matching descriptions only after Step 12. Do not fabricate labels to fill a missing prompt bank.

**Done when:** explanations reconcile with independent score calculations; forged client scores have no effect; obsolete versions are rejected rather than reinterpreted; no response claims specific audible CLAP causes that were not measured by that scorer.

### Step 9 — Build the main catalogue/My List interaction

**Depends on:** Steps 1 and 7.

**Read:** public catalogue/bootstrap schemas, design Sections 3–4.

Build the app shell, tabs, search, genre/year filters, bounded scrolling list, selection states, My List, method control, and Generate action. Support 1–5 distinct songs; the sixth cannot be added and removing a song is easy. Begin with “Choose one song you know.” Preserve selected songs when catalogue filters hide them. Use actual data from the API, with fixtures limited to development/tests.

Keep “Filter the catalogue” separate from collapsed “Restrict recommendations.” Default recommendations use the full collection. Show an explicit summary of candidate restrictions when active. Add loading, no matches, request failure, and retry states. A missing/offline backend must not look like an empty song collection.

**Done when:** keyboard and pointer flows work, seeds survive filter/tab changes, bad year ranges are prevented or explained, and stale search responses cannot replace newer ones. Verify narrow phone and laptop layouts using representative catalogue entries with long titles and multiple artists.

### Step 10 — Add result reveal and external listening

**Depends on:** Steps 8–9.

Implement result cards with initial title/artist/percentage, labelled search links, score help, and **I've Listened**. Hide genre/year/descriptions/seed evidence until reveal, including from incidental tooltips and accessible card text. Provide optional initial reaction controls without blocking access. Preserve reveal state per run and recording; a new algorithm run starts fresh rather than inheriting another run's revealed explanation.

After reveal, render explanation data from the backend and allow revisiting the initial view. Do not use external-link clicks as a listening tracker. New requests retain the previous results while clearly labelling their saved setup.

**Done when:** browser tests establish pre-/post-reveal content, external-link safety, user-controlled reveal, and no accidental generation of audio/player controls. UI text never describes search URLs as verified recording links.

### Step 11 — Add local session persistence, comparisons, and reflection export

**Depends on:** Steps 9–10.

Define a versioned browser state schema containing dataset version, My List, browse filters, separately stored candidate restrictions, preference draft, immutable run snapshots/results, per-result reactions/reveal states, notes, text-query history, and description judgments. Preserve insertion order for the visible list while canonicalising seeds for scoring.

Use one storage adapter with migration/validation, debounced writes, storage-quota failure handling, and a small in-memory fallback. Cap detailed run history (proposed default: 20), warn before pruning and offer export. Do not silently discard reflections. On dataset mismatch, retain/export old notes and clearly identify obsolete song IDs; do not reattach them by title.

Build a comparison view for two runs. Highlight differing seeds, filters, preference settings, method/scoring versions, or query modality; only call it a controlled comparison when relevant inputs agree. Keep notes and ratings independent across runs. Export a readable Markdown/text summary and a structured JSON file, including context and versions. No answers are uploaded to a server.

Add a deliberate “Start a new session” action with confirmation because it clears local reflections. Explain that browser/device changes do not synchronise notes.

**Done when:** reload restores a working session, corrupted storage does not crash, two runs cannot overwrite each other's answers, old versions are handled safely, and the export contains the actual seeds, queries, results, preferences, and notes. Test quota failure and history limits meaningfully rather than writing snapshot tests for every component.

### Step 12 — Create and encode the prepared description bank

**Depends on:** Step 2 passing and Step 3's CLAP matrix. Does not depend on all main-tab UI tasks.

Create `content/prompts-v1.json` with a first reviewed bank of approximately 400–800 descriptions. Cover rhythm, vocals, instruments, texture, dynamics, production, mood, and everyday atmosphere. Include both focused phrases and coherent combinations, with contrastive alternatives. Avoid song/artist names, demographic stereotypes, lyrics, and unsupported claims of exhaustive coverage. Do not construct a giant Cartesian product.

Every entry needs stable ID, text, category/facets, optional paraphrase-group ID, editorial provenance, and version. Store entries in an editable text format. Generated drafts, if used, require review before inclusion; no paid generation service is assumed or required.

Encode with the exact verified text adapter. Save vectors, IDs/order, encoder/tokenizer hashes, prompt-bank hash, dataset identity, and text-reference calibration artifacts under `artifacts/language-v1/`. Precompute each song's closest descriptions or calculate them cheaply at runtime. Diversify displayed matches by keeping one entry per paraphrase group initially, then relaxing only if necessary; record when the category has too few distinct descriptions.

**Done when:** prompt IDs and vectors align, incompatible artifacts are rejected, category filters work without retraining, results are genuine audio–text similarities, and a small manual review identifies repetitive, vague, or misleading prompts. No derived description is presented as a unique decoding of a song vector.

### Step 13 — Implement bounded live text inference

**Depends on:** Steps 2, 3, 12.

Implement local-process and/or private-HTTP adapters behind the same text-encoding interface; support one verified production path rather than maintaining two unnecessarily. The API backend holds model credentials and audio vectors. Reject arbitrary upstream URLs from clients. A separate service accepts text only and returns the validated vector/model identity privately.

Warm the encoder during service startup. Bound concurrency and queue size, use a measured deadline, and keep inference off the API event loop so catalogue and song recommendations remain responsive. Cache text outputs by encoder identity and trimmed query with a bounded cache; do not lowercase text or otherwise alter wording silently. Do not log query bodies by default or expose one student's cached text to another user.

Create prepared example queries and genuine precomputed result/explanation artifacts. Encoder unavailability must leave song recommendations, prepared descriptions, and examples functional. Clearly distinguish “Try a prepared example” from a custom query that failed. Do not replace failures with results based on a loosely similar prompt.

**Done when:** actual compatible live inference works; timeout, invalid vectors, incompatible identity, throttling, and encoder outage are covered; core endpoints remain responsive under text load; cache keys separate model versions.

### Step 14 — Build the language experiment UI

**Depends on:** Steps 11–13.

Allow choosing a song from My List or catalogue and viewing several distinct **Matching descriptions**. Explain their prepared-bank origin. Category controls filter descriptions, not songs. Support Fits / Partly / Misses the point and an optional reason, with browser-local persistence.

Provide a separate text query form and retained query/result history. Encourage a student to describe what they like, then change one aspect. Make prior/new query comparison easy without replacing the original. Reuse listening-first result cards and reaction controls. Do not show descriptive match evidence on result cards before reveal.

Expose meaningful capability states: ready, temporarily busy/unavailable, and prepared-examples mode. A selected song's description matches can work even when live encoding is down because the bank is pre-encoded. Do not make the entire tab disappear on a temporary service failure.

**Done when:** select-song → inspect descriptions → disagree → write query → listen → revise → compare works end to end and survives refresh. The app states when the comparison changes both input modality and recommendation model; it can also compare CLAP song queries with CLAP text queries on the same candidate collection.

### Step 15 — Add the optional taste questionnaire and reranking

**Depends on:** Steps 5–8, 11; language ranking can remain unbiased initially unless deliberately extended and versioned.

Implement the two proposed questions and bounded reranking policy from Section 5.5. Keep the questionnaire collapsed and optional. Clearly show active preferences at the setup/run level, with an easy neutral/reset option. Freeze answers into each run and use identical settings across a controlled comparison.

Test the one missing-prediction recording explicitly. Do not interpret “most probable class probability” as the requested class. Missing optional attributes are neutral, not a reason to remove a song. The explanation identifies preference effects separately from base similarity.

**Done when:** skipped/neutral surveys reproduce the base order exactly, preferences can change suitable candidates without refitting the method, active reranking and match-score meaning are clear, and run history preserves previous answers. Unsupported novelty/energy controls are not displayed as if implemented.

### Step 16 — Complete accessibility, responsive behaviour, and content review

**Depends on:** both tabs and shared session components.

Check keyboard navigation, visible focus, tab semantics, control labels, screen-reader announcements, touch targets, contrast, zoom, and reduced-motion preferences. Do not encode match quality solely by colour. Keep long names readable. Use plain-language method descriptions and short instructions; technical arithmetic is expandable.

Review all copy for false certainty: genre labels and predictions are estimates; match percentages are reference similarities; links are searches; “I've Listened” is self-report. Keep consent-like questions out of the main path unless they serve an actual implemented data collection; the app does not collect answers centrally.

**Done when:** representative laptop and phone flows pass manual review and targeted browser checks. Record any supported-browser limitations. Avoid broad visual snapshot suites that merely duplicate styling; use screenshots as review evidence for the main states.

### Step 17 — Run a focused recommendation and language pilot

**Depends on:** all functional steps. This gate requires real human listening externally; do not mark it complete from metadata or automated tests alone.

Prepare 12–20 seed cases across decades/styles, including rhythmically similar but timbrally different tracks, same-artist risks, instrumental/vocal contrast, subtle acoustic/electronic blends, and deliberately mixed seed lists. Record overlap between methods and inspect whether each method actually gives a distinct perspective. Evaluate top five results, not only the single best anecdote.

For language, use at least 15 reviewed prompts and several one-aspect revisions. Judge whether descriptions retrieve plausible music, whether category matches repeat, and whether cross-modal scores are presented intelligibly. Test unsupported/ambiguous descriptions and document failures rather than teaching students that the model understands every sentence.

Write `docs/PILOT.md` with seed IDs/query texts, version identities, results, listening judgments, surprises, and unresolved issues. If a recipe changes, regenerate its artifacts, calibrations, explanations, and affected examples together. If no human is available, produce a ready-to-run pilot sheet and state that the listening gate remains outstanding; do not stop independent technical work merely because that review has not happened.

**Done when:** technical smoke tests pass and the human pilot has either been completed with evidence or explicitly remains a release prerequisite. Do not treat high cosine values or successful HTTP responses as proof of enjoyable recommendations.

### Step 18 — Package a reproducible production build

**Depends on:** application and artifact interfaces stabilised; can precede final human pilot.

Create a production frontend build and backend container. Include only necessary `data/workshop` files, attribution, scoring/prompt artifacts, and application code. Exclude source/catalogue caches, preparation environments, local notes, test recordings, and unused readable duplicate embeddings from the runtime image. Use a `.dockerignore` and explicit copy paths; never serve the repository root.

Treat text-model weights as separately provisioned immutable artifacts with documented checksums and mount/path settings. Do not depend on downloading weights at request time. Prefer a single backend worker initially; additional workers duplicate model/data memory and need measurement before enabling. Keep health/readiness useful when the text service is unavailable.

Document startup, environment variables, asset base paths, deep-link fallback, graceful shutdown, private-service configuration, log redaction, and rollback in `docs/DEPLOYMENT.md`. Use the provider's hostname initially; a custom domain is optional. Do not choose a paid plan or publish without the actual hosting decision.

**Done when:** a clean production build runs locally, both tab routes survive direct navigation/refresh, wrong dataset/model artifacts fail clearly, and the image does not expose caches/vectors via static URLs. Runtime startup can work with model artifacts already present and no catalogue-provider network access.

### Step 19 — Measure load and rehearse failure modes

**Depends on:** production build and a verified encoder path.

Initial engineering targets, to validate rather than promise: warm core recommendation requests p95 under one second; warm text searches p95 under five seconds at 20 concurrent users with a bounded queue and an approximately 15-second request deadline. A full browser page should be usable within roughly three seconds on normal venue internet. Adjust server capacity or document a realistic queue experience if measurements miss these targets; do not hide failures behind unbounded waits.

Use 25 simulated sessions to allow facilitator/headroom, exercising search, one-/five-seed recommendations, explanations, and text requests. Record error rate, p50/p95 latency, queue behaviour, memory, CPU, and warm/cold startup. Test 20 simultaneous **distinct** text prompts as well as cache hits. Ensure browser-local states do not leak between real browser contexts.

Rehearse unavailable encoder, blocked external listening service, backend restart, offline/reconnect, storage unavailable, corrupt persisted state, and failed version validation. Preserve the student's notes and offer genuine prepared examples. Do not conduct load tests against MusicBrainz, Clapback, Spotify, or YouTube; only our app and provisioned encoder are test targets.

**Done when:** `scripts/benchmark_app.py` and a recorded report establish capacity, protected core responsiveness, and bounded failure behaviour. Re-run after significant inference/concurrency or scoring changes, not after unrelated wording edits.

### Step 20 — Prepare hosting selection and workshop operations

**Depends on:** Step 19 measurements and the pilot status.

Recommend host size and whether the encoder should share a process/service based on measured memory and latency. Present current pricing separately when a provider is selected; the earlier $25–50/month allowance is not a capacity guarantee. Keep public access simple and configure the service to stay awake during both sessions.

Create `docs/WORKSHOP_RUNBOOK.md`: final URL/QR placeholder until deployment, release and data IDs, 45-minute facilitation outline, one-seed start, controlled method comparison, reflection prompts, language demonstration, prepared fallback activities, and how to reset on a shared device without losing another person's notes accidentally.

Include an advance check and a check before each cohort: health/readiness, real recommendation, real text query, prepared example, external listening search, note export, expected release IDs, and model warmup. Students using their own devices should keep their own session; do not globally reset state between cohorts.

**Done when:** the owner can review a concrete deployable package, measured hosting recommendation, remaining listening/model gates, and runbook. Deployment proceeds only within the user's actual authorization and selected environment.

## 8. Test and verification strategy

Use independent small fixtures for arithmetic and protocol tests; use the real frozen collection for startup/integration validation and a small number of named smoke cases. Avoid asserting that a particular song must always be the “best” recommendation without a justified frozen-version reason.

Required coverage:

| Layer | Important regressions |
| --- | --- |
| Data/artifacts | UUID/index misalignment, hash/shape mismatch, incompatible model/config, missing required descriptors |
| Scoring | Independent expected distances/cosines, average per-seed rule, seed permutation invariance, exclusion, ties, fixed scaling |
| Percentiles | Monotonicity, ties, correct seed-count reference, unchanged scores under filtering, separate cross-modal reference |
| Preferences | Neutral identity, class-specific scores, bounded effects, missing-prediction neutrality, visible config |
| Explanations | Arithmetic reconciliation, no forged-score trust, no invented CLAP causes |
| Language | Real adapter compatibility, invalid-vector rejection, deadlines, queue bounds, honest fallbacks, versioned cache |
| API | Input bounds, field whitelists, errors, finite payloads, private-data/static-path isolation |
| Browser | One-seed flow, five-seed limit, filters, listening reveal, two-run comparison, language revision, persistence/export |
| Operations | Fresh production startup, direct routes, missing weights, model outage, core responsiveness under load |

Recommended test tools: pytest for backend/artifact contracts, Vitest/Testing Library for meaningful state/component logic, and Playwright for a compact set of end-to-end journeys. Pin versions during setup. Do not add tests for every reversible styling change or mirror implementation loops with identical test logic.

Document exact runnable commands in the root README once scripts exist. A release check should run prepared-data validation, focused backend tests, frontend typecheck/build, browser acceptance journeys, model verification where artifacts are present, and the production smoke test. Unit CI may use a deterministic fake encoder to test error handling, but at least one explicitly labelled integration check must exercise the real paired model before language readiness is claimed.

## 9. Milestones and review points

1. **Architecture and feasibility:** Steps 1–4; data loading and encoder route established, feature compatibility documented.
2. **Core recommendation experience:** Steps 5–11; real catalogue → seeds → methods → listening reveal → compare/export works.
3. **Full language experiment:** Steps 12–14; prepared descriptions and genuine live text retrieval verified.
4. **Optional preferences and usability:** Steps 15–16; controlled defaults retained and accessibility checked.
5. **Release candidate:** Steps 17–20; technical verification, human listening gate status, production package, load evidence, hosting recommendation, and runbook.

Do not bundle all UI, backend, and model work into one atomic implementer task. Keep the model-feasibility work early, and keep model/runtime failures isolated so they do not prevent core recommendation development.

For each completed task report: files changed; observable behaviour added; focused checks and outcomes; source/artifact version changes; unresolved blockers or decisions; and the next step. Update the task checklist/decision log without rewriting the product history. Do not declare the full app complete merely because the first tab works.

## 10. Definition of complete

- Real frozen data drives all three song methods and both tabs; no production mock recommendations.
- Students select 1–5 seeds, preserve a controlled setup, and compare actual method differences.
- Results honour the listening-first reveal and provide supported evidence after listening.
- Match-score definitions are documented and versioned; scoring/explanations/calibration agree.
- Optional preferences are skippable, explicit, and reproducible.
- The description bank is reviewed, pre-encoded, and correctly labelled; students can disagree.
- Live text search uses a verified compatible text encoder, with honest prepared fallback options.
- Notes, reactions, runs, and query revisions persist locally and export intelligibly.
- No audio, vector downloads, raw feature matrices, credentials, or source caches are exposed to students.
- Source attribution accompanies the packaged data and is reachable in the app.
- Automated integrity/protocol/browser checks pass; real-model and human-listening gate statuses are explicit.
- Capacity for the cohorts is measured in a production-like build; deployment and workshop operation are documented.
- The owner receives a reviewable deployment candidate and clear remaining actions, rather than an untested claim of workshop readiness.

## References checked while preparing this plan

- Existing repo design/data documentation is the primary authority for product scope and dataset facts.
- [Clapback encoder package](https://pypi.org/project/clapback-embed/): reference audio/text interface and artifact setup. Recheck the pinned source during Step 2; package publication is not verification of our deployment.
- [FastAPI deployment documentation](https://fastapi.tiangolo.com/deployment/): framework deployment guidance.
- [Vite getting started](https://vite.dev/guide/): supported scaffolding and runtime requirements; pin the actual chosen release during Step 1.
