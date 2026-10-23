# Workshop Runbook — 45 Minutes ×2 Cohorts

Venue: University of Osnabrück, 15–20 adults per cohort, working internet, students on own devices + facilitator laptop projected.

Final URL/QR: `______________________` (fill after deployment) — QR generated from provider hostname.

Release and data IDs:
- Dataset ID: `e755bbd1cc5512d4` (manifest `2026-10-18T05:12:18Z`)
- Pipeline: `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32`
- Scoring: `scoring-v1` (config `config/scoring-v1.json` sha256 `56fde13b...`)
- Calibration: `calibration-v1` (check `artifacts/scoring-v1/calibration.json` checksums)
- Prompt bank: `prompts-v1` (400 entries, `06b91c29...`)
- Language status: `disabled` (live pending ONNX) — app shows prepared examples

## Advance Check (day before)

- [ ] `GET /health/ready` returns 200 with expected IDs
- [ ] Browse catalogue, add 1 seed, generate per method (4 checks; Listener patterns uses supported songs)
- [ ] `POST /api/text-search` — expect 503 when disabled (prepared flow) or real results when live
- [ ] `GET /api/examples` returns 2+ prepared searches
- [ ] External listening search (YouTube/Spotify) opens with `noopener`
- [ ] Note export (JSON + Markdown) contains seeds, queries, results, notes
- [ ] Model warmup (if live) — first text query <5s, subsequent <1s due to cache

## Check Before Each Cohort (15 min before)

- Same 6 checks as advance, plus:
- [ ] Clear facilitator demo data but do not globally reset students (they keep own sessions)
- [ ] Verify “Start new session” clears only current browser
- [ ] Headphones available; venue Wi-Fi tested with 5 devices concurrently

## 45-Minute Facilitation Outline

| Min | Activity | App Tab | Notes |
|-----|----------|---------|-------|
|0–5 | Intro musical similarity, demo one recommendation | Song recommendations | Facilitator projects: pick Dancing Queen, generate clap-v1, show listening-first reveal |
|5–8 | Select familiar seed, note what you like | Catalogue + My List | “Choose one song you know.” Limit 5, but start with 1. Browse filters vs restrict recommendations explained |
|8–16| Explore song recommendations, listen to 2–3 results | Results | After Generate, show title/artist/percentage only; click I’ve Listened to reveal metadata/evidence. Optional Like/Connection reaction before reveal |
|16–21| Discuss in groups of 3–4 | Reflection prompts | What stayed similar: rhythm/voice/instruments/mood/production? Surprises? |
|21–25| Introduce audio–language embeddings | Describe and discover | Show Matching descriptions for selected song; explain prepared bank origin; category filter does not retrain |
|25–35| Inspect descriptions, write query, listen, revise one aspect | Text search | Describe what you like, retrieve, change 1 word (intimate→distant), compare retained vs new results (history) |
|35–42| Compare discoveries in same groups | Comparison | Compare two runs (controlled: same seeds/filter, different method) vs cross-modal (song vs text) |
|42–45| Share surprises, close | Export | Copy/download notes for discussion; students keep own session |

Facilitator can choose shorter path: only 1–2 methods; biases off for first comparison.

## Section one: miniature collaborative AI experiment

1. Select **Listener patterns (small AI model)**. The catalogue shows 182
   supported songs. Remove any seed marked “No listener model”.
2. Choose a familiar supported song, such as Daft Punk's **Digital Love**,
   and generate recommendations. Listen before revealing scoring evidence.
3. Explain: a 32-factor model learned shared tastes from real listeners' song
   loves. It never heard the audio; an artist or shared audience may drive the
   connection. Workshop reactions are reflections, not live training.
4. Keep the shared candidate pool enabled, the same seeds/restrictions, and
   preferences neutral. Switch to Rhythm or Texture and compare another run.
   CLAP can be used here or introduced in section two.
5. Add a second supported seed and repeat. Ask whether a shared audience and
   a shared sound lead to different discoveries. Missing-song coverage is a
   data limitation, not evidence that a song is unpopular.

Data: historical ListenBrainz feedback sample (2025-06-10), 2,516 training
listeners, 10,082 training songs. 182 of our 1,500 songs meet support rules.
Offline held-out hit rate @10: 27.36%, versus popularity's 23.58% (793 cases).
This is a teaching example, not Spotify's production system or a prediction of
participant satisfaction. Full audit: `artifacts/collaborative-v1/README.md`.

## Reflection Prompts (in-app + verbal)

- What do you like about your selected songs?
- What did you expect the method to preserve?
- What stayed similar: rhythm, voice, instrumentation, mood, production, or something else?
- Can you hear the connection even if you dislike the recommendation?
- Which result surprised you, and what connection did you eventually hear?
- Which method helped you discover something you liked, and why?
- For language: what did the model appear to understand? What did it miss?

## Prepared Fallback Activities (if live encoder down or network hiccup)

- Use **prepared examples** (“warm acoustic guitar…”, “fast energetic drums…”) — they work without live encoding
- Compare description category filtering (vocals vs rhythm) on same song
- Controlled method comparison (keep seeds same, change rhythm→texture→clap)

## Reset on Shared Device

- “Start a new session” button (with confirmation) clears local reflections, My List, runs, query history for that browser only.
- Students on own devices keep their own session; do not globally reset between cohorts.
- If a device is shared, export before reset and hand file to next student.

## Troubleshooting

| Issue | Action |
|-------|--------|
| Backend not ready (503) | Show `health/ready` error, check dataset mount, restart Docker, verify scoring artifact checksums |
| Text search 503/504 | Explain queue full or encoder busy; retry with prepared example; core recommendations still work |
| External listening blocked | Try alternative search link (YouTube vs Spotify); note that links are searches, not verified exact recording |
| Storage quota (localStorage full) | Prune oldest runs (app warns at 20), export before continue |
| Corrupted persisted state | App falls back to in-memory; offer to clear storage |
| No results after filtering | Loosen candidate filter (style/year) or add more diverse seeds |

## Hosting Stay-Awake

Configure provider to not sleep during both 45-min sessions. No deployment changes during a session.

## Post-Workshop

- Collect exports only if students volunteer (no central collection).
- Record pilot listening judgments in `docs/PILOT.md` if time allows.
- Note any scoring recipe surprises for `docs/DECISIONS.md`.
