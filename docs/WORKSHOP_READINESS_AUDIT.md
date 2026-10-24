# Workshop readiness audit

Audited 24 October 2026, against checkout `3581a46` and the live service at
https://spaceday-music-workshop.onrender.com. This is an assessment and implementation
brief; application code was not changed during this audit.

## Verdict

The workshop's main activities are implemented and the live service is running the
real description-matching edition. It is technically usable for a facilitated
trial. It is not yet supported by a complete release-readiness record: there are
confirmed reliability/data-integrity defects, a stale capacity harness, an older
failed capacity report, inconsistent teaching documents, and outstanding human
listening/device/venue checks. No model retraining is required for the current scope.

## Evidence gathered

- Backend: **50 tests passed** in the existing local environment.
- Frontend: **16 tests passed**.
- Browser checks: **20 passed**, covering Chromium and WebKit, desktop and emulated
  phone. The test server rebuilt the production frontend successfully.
- Data validation: **25 checks passed**, 1,500 recordings and 785 artists.
- Live `/`, `/health/ready`, and `/api/bootstrap`: HTTP 200. Dataset
  `e755bbd1cc5512d4`; description status `prepared`; live search `retired`; real
  pinned text-encoder identity present; all four recommendation methods available.
- Ordinary live smoke requests: five results returned by each of rhythm, texture,
  listener patterns, and CLAP, with the same supported seed and shared pool.
  Individual recommendation requests took about 0.21–0.22 seconds in this sample.
  Texture explanation and real description retrieval also returned 200. This was
  a light smoke check, not a current capacity certification.
- Stored `benchmark_report.json`, modified 23 October, targets the Render service:
  60-second sustained phase, zero unexpected HTTP failures, overall recommendation
  p95 **6.17 seconds**, five-seed CLAP p95 **9.17 seconds**. The script's recommendation
  target is 2 seconds. This predates the description change and does not represent
  a current successful load test or a realistic test of only the one-seed UI.
- No Docker executable was available for local image testing. Browser tests use
  the existing local Python environment, not the exact pinned container runtime.

## Implementation work required for a dependable release

### 1. Reject missing or mismatched scoring artifacts

**Priority: before declaring the release ready.**

`backend/app/data_store.py` permits absent scoring metadata/calibration and loads
without them. `backend/app/recommendation/calibration.py` then produces heuristic
percentages, or returns 50 for missing tables. `scoring.py` also catches calibration
errors and substitutes 0.5 for ranking utility. A probe loaded a store with no
scoring directory and obtained a 90.0 percentile for cosine 0.8.

Validate dataset/config/pipeline identity, required methods and seed-count tables,
finite numbers and monotonic calibration at startup. Required recommendation
artifacts must fail readiness rather than invent percentages. Treat description
availability as an explicit optional capability; a facilitator release check must
also require it for this workshop. Bind caches to the store/artifact identity;
currently module-global scoring/calibration caches can survive another store load.

**Acceptance:** missing, corrupt, wrong-dataset or incomplete scoring artifacts
cannot serve apparently calibrated recommendations. The normal frozen edition
continues to produce its existing rankings and percentiles.

### 2. Protect participant work and make storage status truthful

**Priority: before the workshop.**

`frontend/src/state/storage.ts` catches invalid JSON but does not validate the
shape of valid JSON. Probes returned `runs: null`, `myList: "oops"`, and
`descriptionJudgments: null` unchanged; the app assumes arrays/objects and can
crash. `saveState` silently prunes or fails; the footer nevertheless says work is
saved. Generating a 21st distinct run silently discards the oldest.

Validate/migrate nested persisted data; recover safely while preserving valid
notes. Expose storage failure and pruning status and offer export. Make reset work
when storage access is denied; `App.tsx` calls `removeItem` without handling failure.
Add a recoverable application error state so malformed saved state does not leave
participants with a blank page. Remove obsolete selected IDs from the active
working set on dataset changes while retaining historical information for export.

**Acceptance:** denied storage, quota exhaustion, malformed valid JSON, stale IDs,
and history limits do not crash or silently lose work. A fresh browser still starts
normally. Screen copy accurately distinguishes saved and memory-only work.

### 3. Restore the participant's actual place after app switching/reload

**Priority: before the workshop.**

`App.tsx` keeps the carousel position in component state initialized to zero;
`activeResultIndex` and `activeRunId` in storage are not used to restore it. The
storage unit test only round-trips those fields without exercising the app.
Prediction drafts before generation also live only in component state.

Persist the selected result per applicable run and unsubmitted predictions. Restore
safely after refresh or returning from a music app; reset the index when the setup
changes, not on ordinary restoration. Add bounded fetch timeouts/cancellation and
retry states to `frontend/src/api/client.ts`; all current fetches are unbounded at
the application level. A stalled request must not leave every method disabled by
an indefinitely true `generating` flag.

**Acceptance:** result 4/5, typed prediction, reactions, active song and stage survive
reload. Offline/hanging requests reach a clear retry state, and stale responses
cannot contaminate a new session/setup.

### 4. Make saved results and explanations respect model versions

**Priority: before further recipe/model updates; include in release hardening.**

Confirmed: requests supplying a wrong dataset and obsolete scoring version still
return 200; explanations with an obsolete version return 200 as well. Noncollaborative
run fingerprints omit scoring/calibration identity. `matchesSetup` checks dataset,
seed, filter and preferences, but not model/calibration versions. Regeneration
keeps the previous snapshot when its deterministic ID repeats.

Fingerprint all result-affecting artifacts and validate requested identities. Keep
old runs exportable but exclude them from the current comparison, or label them as
historical. Send/check identity when requesting explanations so new model evidence
cannot be attached to old results. Add prompt/encoder version to description judgments.

**Acceptance:** changing a scoring or encoder artifact cannot silently reuse an
old current result or judgment, and stale explanation requests have an explicit
version-conflict response.

### 5. Complete description judgment and export behavior

**Priority: before the description activity is used for recorded observations.**

`LanguageLab.tsx` assigns `fit: 'fits'` when someone types a reason without choosing
a verdict. This creates an endorsement the participant never made. It stores only
song ID + prompt ID + verdict/reason; the phrase, category and model version are
not in the export. Markdown exports show raw keys such as
`recording-uuid:ins-001`, making them hard to interpret outside the repository.
The description selector can choose a different song from the active starting
song, but the description panel has no matching listening links; the global links
continue to refer to the starting song.

Require an explicit verdict or support an unanswered value. Save self-contained
judgment snapshots: recording title/artist/ID, description ID/text/category,
prompt/encoder identity and user response. Export those in readable Markdown and
JSON. Include readable working-set names and useful result listening links.
Provide listening links for the song actually selected in the description panel.

**Acceptance:** typing a reason does not mark Fits; downloaded judgments are
understandable without source JSON files; switching the description song also
switches its displayed listening target.

### 6. Repair the capacity harness and address performance if reproduced

**Priority: before relying on a capacity claim.**

`benchmark_app.py` only accepts text-search 503 when `language_status == disabled`.
The real demo now reports `prepared` and separately reports retired live search.
A direct probe confirmed its expected-failure checker rejects this legitimate
response, so mixed phases will report failures for the current edition. The
`--hosted` flag is parsed but does not add the promised hosted checks.

Remove retired live search from normal workshop load, testing its unavailable
contract separately. Test the actual participant workload: one seed, 182-song
shared pool, all four formulas, explanations, real descriptions, catalogue,
bootstrap and assets. Report each phase/method separately. Retain five-seed/full
catalogue stress cases as a clearly separate supported-API stress profile.

Run fresh 20/30-session burst and 10-minute sustained checks on the live release,
with host CPU/memory and cold-start evidence. If the current workload misses the
chosen target, optimize using cached normalized feature matrices and batched
similarity operations before increasing hosting resources. Runtime scoring still
loops over candidates/seeds; documentation claiming it is fully vectorized is
inaccurate. Preserve exact score semantics and deterministic ties.

**Acceptance:** no unexpected failures; realistic workshop requests meet the
agreed p95 target; no method's poor latency is hidden by aggregation; results are
clearly dated and tied to a release. Do not call the old 60-second report a pass.

### 7. Finish API validation and startup failure behavior

**Priority: focused hardening; malformed inputs are not generated by the current UI.**

Confirmed: empty explanation seeds return 200 with base score zero; six duplicate
seeds are accepted; an invalid year filter type produces 500. Nested filters and
preferences are untyped dictionaries. Tighten schemas for seed counts, uniqueness,
method, ranges and finite bounded preference values; reject invalid requests with
4xx. Validate that an explanation result is eligible under the declared setup.

`/api/bootstrap` returns a success-shaped fallback advertising methods even after
startup failure. Routers are imported under a broad catch that can leave a partial
app running. Use explicit unavailable/startup behavior and ensure the participant
sees connection recovery rather than a plausible empty workshop. Request-ID error
responses should contain the server-generated ID, not only an incoming header.

**Acceptance:** invalid inputs cannot generate fake explanations or unhandled 500s;
an unready app cannot advertise a functioning workshop.

## Content and teaching readiness

### Description quality needs a real pilot

Across all 1,500 current audio vectors, the phrase **“syncopated funk groove with
off-beat guitar” ranks first for 801 recordings (53.4%)**. Only 28 of 71 descriptions
win a first position. This is a concentration diagnostic, not proof of a code bug
or proof of audible correctness. Aphex Twin's Avril 14th gives plausible piano
and mood matches in the live smoke check, while Nirvana's Lithium also ranks the
funk phrase first locally.

Before presenting this as a successful semantic demonstration, listen to a small
balanced set and document Fits/Partly/Misses. Check prompt wording and the upstream
audio/text compatibility assumptions; the upstream audio checkpoint hash is not
independently pinned. If changing the bank or scoring policy is warranted, version
and rebuild it. Category comparisons or a deliberately discussed mismatch can be
useful; do not manipulate rankings merely to make them look convincing. Retraining
is not the default remedy.

### Bring the facilitator materials into agreement

`docs/PRESENTATION_DRAFT.md` and `docs/WORKS_CITED_AND_METHODS.md` still describe the
current bank as synthetic. `PILOT.md`, `DEPLOYMENT.md`, `PHONE_TESTING.md` and parts
of the runbook still assume 400 prompts, a second tab/live queries, an older reveal
flow, or outstanding deployment. The runbook's storage-warning/recovery claims
exceed the implementation, and its pilot timing conflicts with the pilot document.

Use one source of truth: guided one-active-song flow; rhythm/texture formulas;
listener patterns; CLAP; optional 71-description activity; comparison and export.
The optional taste survey changes reflection prompts, not rankings. Live text
search is retired. Reference percentiles are not enjoyment probabilities.

Update the pilot to the actual four formulas and shared 182-song candidate pool.
ABBA's Dancing Queen, the runbook's opening example, is **not** in the supported
listener pool. Verified supported examples include Queen's Bicycle Race, Aphex
Twin's Avril 14th, Portishead's Glory Box and Daft Punk's Digital Love. Record exact
IDs/results and choose a rehearsed opening song available in the default view.

Provide a short presenter sequence and participant instructions that fit 45
minutes; the presentation is presently a Markdown draft, not a finished slide deck.
A slide deck is optional if the app is the projected teaching surface. Expose a
small About/Sources entry using the existing provenance and attribution content.
Explain external music services and browser-local storage in participant language.

## Operational checks still required

These require observation or access to the venue/hosting account; they cannot be
established by unit tests or invented listening judgments.

- [ ] Confirm the actual session times, final URL and QR code; fill the runbook.
- [ ] Verify hosting stays awake through both cohorts plus setup/buffer, record the
  serving release/image and rollback target, and freeze deployments during sessions.
- [ ] Verify exact container build/pinned dependencies or record the successful host
  build evidence. Live responses prove a working service, not every packaging claim.
- [ ] Run the repaired hosted capacity check; watch server CPU, memory and errors.
- [ ] Perform and record the human pilot, including description concentration and
  differences between similarity and enjoyment.
- [ ] Check the live URL on a real iPhone/Safari and Android/Chrome: keyboard,
  scrolling, external-app return, download/open exports, reload and session reset.
- [ ] Check actual screen-reader/keyboard use, focus visibility, zoom and contrast;
  browser emulation is not a completed accessibility review.
- [ ] Rehearse external listening on venue Wi-Fi, including no-login access,
  recording/version selection, blocked services, adverts and volume/headphones.
- [ ] Verify room Wi-Fi/projector/audio and have the URL available as text alongside
  the QR code. Confirm the laptop remains awake for any local-server fallback.
- [ ] Prepare an outage activity: saved screenshots/results and a discussion sheet;
  no service worker/offline catalogue is implemented. If all external listening is
  unavailable, use a prearranged permitted listening source or an explicit
  discussion-only fallback. The app does not distribute music.
- [ ] Rehearse voluntary export, shared-device reset and the changeover between
  cohorts. Data is browser-local; there is no central collection or cross-device sync.

## Focused verification additions

The passing tests do not cover the failures above. Add targeted tests for artifact
identity/missing tables, nested storage corruption/quota recovery, app-level result
restoration, version conflicts, semantic exports, explicit description judgments,
timeout/retry behavior and current benchmark capability detection. Add a real-backend
browser description test; current UI description tests use fixtures. Fix the
vacuous `assert pct >= prev or True` calibration assertion. The existing storage
history test manually slices before saving, so it does not verify the app's real
history-limit behavior. A small CI check would help keep the final release stable,
but manual evidence is sufficient for today's one-off release if frozen.

## Relevant files for downstream planning

**Must read for the matching area before editing:**

- Storage/recovery/exports: `frontend/src/state/storage.ts`,
  `frontend/src/app/App.tsx`, `frontend/src/app/LanguageLab.tsx`,
  `frontend/tests/storage.test.ts`, `frontend/tests/app.test.tsx`.
- Artifact/version/API behavior: `backend/app/data_store.py`,
  `backend/app/recommendation/{scoring,calibration}.py`, `backend/app/schemas.py`,
  `backend/app/main.py`, the affected router and focused backend tests.
- Capacity: `scripts/benchmark_app.py`, `backend/tests/test_benchmark.py`,
  `frontend/e2e/workshop.spec.ts`, `Dockerfile`, `backend/pyproject.toml`.
- Content: the specific facilitator document being revised; use this report for
  current behavior and recheck its live capabilities before release sign-off.

**Can use summarized context:** frozen catalogue has 1,500 songs; listener model
supports 182; all four recommenders already work; description bank has 71 real
vectors; no runtime encoder or retraining needed. Preserve catalogue/source data,
existing formulas, no taste reranking in the guided flow, and retired live-search code.

**Read only if blocked:** large raw source caches, acquisition/curation scripts,
full model-training implementation and old live-encoder setup. Do not perform
open-ended repository exploration; ask for the exact missing file/output if the
listed context is insufficient.

## Work outside today's required scope

No new recommender, CLAP training, collaborative retraining, catalogue expansion,
real-time text generation, accounts, central database, analytics, in-app audio
player, or full offline synchronization is needed to run the agreed workshop.
Those would introduce new scope without resolving the readiness issues above.
