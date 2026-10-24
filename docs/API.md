# API Documentation

Base URL: `/api` (proxied to backend in dev; same origin in production)

All errors use envelope `{code, message, retryable, request_id}` and appropriate HTTP status:
- 422 validation error
- 404 unknown ID/method
- 409 incompatible dataset/config
- 429 throttling (not yet enforced)
- 503 encoder unavailable
- 504 deadline (not yet, but planned)

## `GET /health/live`
Process health. Always 200 `{status:"ok"}`.

## `GET /health/ready`
Validated data/artifact readiness. 200 `{status:"ready", dataset_id, language_status}` or 503 `{status:"not_ready", error}`.

## `GET /api/bootstrap`
Public capabilities, versions, vocabularies, score help, attribution.

When the optional model is installed, `supported_methods` also includes
`collaborative-v1`; `collaborative` supplies `supported_count`, `supported_ids`,
`model_id` and `source_snapshot`. Otherwise `collaborative` is null.

Response:
```json
{
  "dataset_id": "e755bbd1cc5512d4",
  "pipeline_version": "laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32",
  "snapshot_date": "2026-10-18T05:12:18Z",
  "scoring_version": "scoring-v1",
  "calibration_version": "calibration-v1",
  "language_status": "disabled|prepared|live",
  "supported_methods": ["rhythm-v1","texture-v1","clap-v1"],
  "filter_vocab": {"style_families": [...], "familiarity_bands": [...]},
  "year_bounds": {"min":1960,"max":2022},
  "score_help": "How strong this computed similarity is compared with reference comparisons... It is not the chance you will like the song.",
  "attribution_links": {"clapback":"...","musicbrainz":"...","acousticbrainz":"..."}
}
```

## `GET /api/songs`
Whitelisted catalogue fields; search, genre/year filters, deterministic pagination/sorting.

Query params:
- `q` (optional, 1–200 chars, case/diacritic tolerant, matches title/artist)
- `style` (optional, one of 11 primary families)
- `year_min`, `year_max` (1960–2022, must satisfy min<=max)
- `offset` 0–10000, `limit` 1–100 (default 20)
- `sort` = `default` (anchors first, then artist/title/uuid) or `year`
- `collaborative_only=true` limits browsing to supported listener-model songs.
- `ids` accepts up to five comma-separated recording MBIDs to restore saved
  selections regardless of the current catalogue page.

Response:
```json
{"total":123, "offset":0, "limit":20, "items":[{"recording_mbid":"...","title":"...","artist":"...","year":1976,"primary_style_family":"pop_smooth","style_families":[...],"familiarity_band":"...","is_editorial_anchor":true,"tags":[...],"musicbrainz_url":"...","youtube_search_url":"...","spotify_search_url":"..."}]}
```

Public result never includes embeddings, raw hashes, feature matrices.

### Collaborative recommendations

`POST /api/recommendations` accepts `method: "collaborative-v1"`. All seeds
must have trained factors (422 with guidance otherwise); absent model returns
409. Candidates are supported songs only. The response's effective
`candidate_filter` records `collaborative_only: true`. Pass this same filter to
other methods for a shared candidate pool. Scoring/calibration versions and
run fingerprints include the model artifact identity. Percentiles use a
separate model-specific reference distribution. Existing optional preferences
can rerank results; neutral preferences preserve the pure model ranking.

`POST /api/explanations` supports this method and returns aggregate seed/result
listener counts and the model description, never individual listener records.

## `POST /api/recommendations`
Validated 1–5 distinct seed IDs, method, explicit candidate filter, preference snapshot, limit.

```json
{
  "seed_ids": ["a502f559-f70c-4e0d-a5e5-e0cc319d0bd7"],
  "method": "clap-v1",
  "limit": 5,
  "candidate_filter": {"style_family":"pop_smooth","year_min":1980,"year_max":1990},
  "preferences": {"instrumental":1, "acoustic_electronic":-1}
}
```

Bounds: seed count 1–5 distinct UUIDs; limit 1–20; candidate_filter style must be known family; year bounds same as songs.

Returns immutable run config + version identities + base match percentiles (0–99.9, one decimal, capped).

```json
{
  "run_id":"abc123def456",
  "dataset_id":"e755bbd1cc5512d4",
  "scoring_version":"scoring-v1",
  "calibration_version":"calibration-v1",
  "method":"clap-v1",
  "seed_ids_canonical":["..."],
  "candidate_filter":null,
  "preferences_applied":null,
  "results":[{"recording_mbid":"...","title":"...","artist":"...","year":1983,"primary_style_family":"...","rank":1,"base_score":0.82,"match_percentile":99.8,"youtube_search_url":"...","spotify_search_url":"..."}]
}
```

Candidate eligibility applied before ranking without refitting normalisers. Sorting: base_score desc, then recording UUID tie-break. With active preferences, rank by `U = B + 0.05*mean(fits)` where B is reference percentile in [0,1]; else `U=B`. Preferences do not change displayed match percentile.

Errors: 422 duplicate seeds, inverted years, malformed prefs; 404 unknown ID; 409 dataset mismatch.

## `POST /api/explanations`
Recompute explanation for a result using its immutable run config; do not trust client scores.

```json
{"seed_ids":["..."],"method":"clap-v1","result_id":"...","candidate_filter":null,"preferences":null}
```

Returns per-seed scores, aggregate base_score, group contributions, and notes. For CLAP, shows exact seed similarities and honest note about embedding proximity.

Errors: 404 unknown result, 422 unknown method.

## `POST /api/descriptions`
Experimental discussion descriptions for a selected recording and optional category filter.
The 256-phrase bank includes musical, emotional and atmospheric candidates.
Ranking uses `description-standardized-v1`: raw CLAP cosine minus the phrase's
full-catalogue mean, divided by its population standard deviation. The reference
is always the frozen 1,500-song catalogue, independent of category/candidate filters.

```json
{"recording_mbid":"...","categories":["rhythm"],"limit":5}
```

Returns:
```json
{"recording_mbid":"...","matches":[{"id":"rhy-001","text":"...","category":"rhythm","similarity":0.3,"description_score":1.2}],"scoring_version":"description-standardized-v1-...","reference_dataset_id":"...","prompt_version":"prompts-v4","encoder_id":"...","note":"Experimental discussion method..."}
```

Diversified by paraphrase_group (one per group initially), with ID tie-breaking.
`similarity` retains raw cosine; `description_score` is the standardized ranking
value. Neither is a probability. Constant-score phrases (std <= 1e-8) are excluded.
The scoring identity binds method, reference dataset, prompt bank and vectors.
Unknown recording: 404; unavailable/invalid description artifacts: 503.

## `POST /api/text-search`
Encode bounded text query and retrieve audio neighbours. Requires live encoder.

```json
{"query":"warm acoustic guitar with soft vocals","limit":5,"candidate_filter":null}
```

Bounds: 1–500 chars after trim; reject model-token overflow (not yet measured; reject >500 chars). Same candidate filtering as recommendations.

Returns query hash, encoder/prompt versions, results with same percentile convention but from text-to-audio reference calibration (separate from audio-to-audio). If encoder unavailable, 503 with `retryable:true`; UI shows prepared examples.

## `GET /api/examples`
Versioned prepared language searches usable without live encoding.

```json
{"version":"prompts-v1","items":[{"id":"ex1","query":"warm acoustic guitar with soft vocals","category":"texture"}]}
```

## Field Whitelists & Privacy

- Public: only `recording_mbid`, title, artist, year, style families, familiarity_band, anchor flag, tags (10), listening search URLs.
- Never: `clap_embeddings.f32`, `clap_embeddings.json.gz`, raw `features.json` predictions, source caches, raw hashes, model credentials.
- Browser state is localStorage only; no server-side collection.

## Versioning & Fingerprints

- `run_id` is truncated SHA256 of `{seeds canonical sorted, method, filter, prefs, dataset}` — seed-order permutations produce same ranking and fingerprint.
- Scoring/calibration versions are in `meta.json`/`calibration.json`; mismatched dataset fails readiness.
- Query hash is SHA256 of trimmed query + encoder identity.
