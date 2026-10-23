# Listening Pilot — Ready-to-Run Sheet

Status: 2026-10-21 — Technical smoke tests PASS; human listening gate **outstanding** (release prerequisite).

## Purpose
Validate whether rhythm-v1, texture-v1, clap-v1 produce musically distinct, useful contrasts and whether language descriptions/retrievals are plausible. High cosine or HTTP 200 alone does not prove enjoyable recommendations.

## 12–20 Seed Cases (across decades/styles)

Use these recording_mbid seeds (titles for reference):

1. `a502f559-f70c-4e0d-a5e5-e0cc319d0bd7` ABBA — Dancing Queen (1976, pop_smooth) — vs. same-artist risk
2. `e9759a5a-5efc-4030-8168-f08790ae4ddc` (second catalogue entry, check via /api/songs) — 2000s electronic dance
3. Classic rock anchor: Queen — Bicycle Race (1978)
4. Jazz blues: Stan Getz / João Gilberto — The Girl From Ipanema (1964)
5. Hiphop: Snoop Doggy Dogg — Who Am I (1993)
6. Ambient instrumental: Brian Eno-style (search ambient_instrumental, pick 2010s)
7. Rhythmically similar but timbrally different pair: Daft Punk — Around the World (1996) vs James Brown-style funk (find funk_soul_rnb, 1970s)
8. Instrumental/vocal contrast: Aphex Twin — Avril 14th (instrumental) vs Portishead — Glory Box (vocal)
9. Subtle acoustic/electronic blend: Beirut — Port of Call (acoustic) vs Röyksopp — Eple (electronic) — same year window
10. Deliberately mixed seed list: Dancing Queen + Aphex Twin — Xtal + The xx — Intro (3 seeds, cross-genre)
11. 5-seed list for calibration stress: pick 5 recognisable anchors across decades
12. Country/folk acoustic: Patsy Cline — Back in Baby’s Arms (1963) vs Moby — Porcelain (1999) (texture contrast)

Add 3–5 facilitator-chosen modern indie/psychedelic seeds to reach 15+ cases.

For each case:
- Generate 5 results per method (15 total per seed case)
- Inspect top-5 overlap between methods (Jaccard) and whether each method gives distinct perspective
- Listen externally via YouTube/Spotify search links (use headphones)
- Record judgments below

## Listening Judgment Template (per method, per seed)

```
Seed: <title> — <artist> (<recording_mbid>)
Method: rhythm-v1 / texture-v1 / clap-v1
Candidate: <title> — <artist> (<mbid>) rank 1..5 match 98.2%
Verdict:
- Like / Unsure / Dislike: ___
- Connection clear / Partly / Not clear: ___
- What stayed similar (rhythm/voice/instruments/mood/production): ___
- Surprise: ___
```

Copy this for each result. Keep notes local; no upload.

## Language Pilot (≥15 reviewed prompts + one-aspect revisions)

Prepared prompts to test (from content/prompts-v1.json):
- `rhy-001` steady four-on-the-floor beat, danceable
- `voc-001` intimate close-miked vocals
- `voc-004` no vocals, instrumental
- `ins-001` warm acoustic guitar, fingerpicked
- `tex-002` crisp and clean production
- `mood-002` joyful and uplifting
- `atm-005` underground club, dark room
- `combo-001` slow tempo with intimate vocals and sparse piano

For each prompt:
- Retrieve description matches for a known song (e.g., Dancing Queen) — judge repetitive/vague/misleading
- For text search (when live): query prompt verbatim, note top-5 songs
- Revise one aspect: e.g., “intimate vocals” → “distant vocals” keep rest fixed, compare results overlap
- Judge whether category matches repeat (e.g., all “rhythm” duplicates) and whether cross-modal scores are presented intelligibly

Document unsupported/ambiguous queries:
- “music that feels like a rainy Tuesday with existential dread but also hopeful” — expect honest failure or vague results, not fabricated
- Non-English German query (if app states English-only, should not claim German support)

## Scoring Recipe Change Protocol

If pilot shows poor contrasts or bunching:
1. Edit `config/scoring-v1.json` and create new version id `scoring-v2`
2. Regenerate `artifacts/scoring-v1/` → `artifacts/scoring-v2/` via `scripts/build_app_artifacts.py`
3. Regenerate calibration and re-run explanations
4. Update `docs/DECISIONS.md` and re-run full test suite

## Current Technical Smoke (pre-human)

- Data integrity: PASS (25 checks, 1500/785, unit norms, 43 extractor versions noted)
- Scoring artifacts: generated, 3 methods × 5 seed counts, 1001-point tables, checksums recorded
- API: bootstrap, catalogue, 1–5 seeds, candidate filters, preferences, explanations all PASS via `pytest backend/tests`
- Frontend: catalogue → My List → method → generate → listening-first reveal → compare/export works; reload restores via localStorage
- Language: prompt bank 400 entries; placeholder vectors (fake) for UI; real ONNX encoder BLOCKED (see docs/MODEL_SETUP.md) — prepared bank and examples functional
- Calibration clustering: CLAP median 0.676, 90th 0.844; rhythm median -0.846, 90th -0.186 (useful spread, not all 99.9+). Top results for Dancing Queen: rhythm top -0.009 (99.9), texture -0.111 (99.8), clap 0.98+ (99.8) — some bunching at top but distinguishable by listening
- Cross-modal calibration: separate tables not yet built (text reference requires live encoder); do not reuse audio-audio tables for text

## Release Prerequisite

Human listening judgments for the above seed cases **must** be completed and recorded in this file before hosted deployment is declared ready. No public deployment until pilot sheet is filled with actual judgments and any recipe issues are versioned and re-tested.

Template to fill after listening:

| Seed | Method | Top-3 overlap with other methods | Distinct perspective? | Like rate (n/5) | Connection clear rate | Notes |
|------|--------|----------------------------------|------------------------|------------------|-----------------------|-------|
| ABBA Dancing Queen | rhythm-v1 | 1/5 shared with texture |  |  |  |  |
| ... | ... | ... | ... | ... | ... | ... |

Surprises, failures, and unresolved issues:

- (to be filled)

## Re-run Commands

```
# validation
python3 scripts/validate_data.py
# scoring
/Users/campshelor/miniconda3/bin/python scripts/build_app_artifacts.py
# tests
/Users/campshelor/miniconda3/bin/python -m pytest backend/tests -v
npm --prefix frontend run typecheck && npm --prefix frontend run build
# benchmark
BENCH_BASE_URL=http://127.0.0.1:8000 /Users/campshelor/miniconda3/bin/python scripts/benchmark_app.py
```

## Sign-off

- [ ] Pilot listener 1 (name/date):
- [ ] Pilot listener 2 (name/date):
- [ ] Recipe/revision decision logged in docs/DECISIONS.md
