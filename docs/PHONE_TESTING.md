# Phone Testing — Manual Checklist & Local Preview

## Local preview from phone on same Wi-Fi

No authorized public URL exists yet. Use local preview:

1. On your Mac, find its Wi-Fi IP:
   ```sh
   ipconfig getifaddr en0   # e.g. 192.168.1.23
   ```
2. From repo root, run production single-origin:
   ```sh
   npm --prefix frontend run build
   PYTHONPATH=. /Users/campshelor/miniconda3/bin/python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 1
   ```
   Verify: `curl http://192.168.1.23:8000/health/ready` → 200.
3. On iPhone/Android, connect to same Wi-Fi, open Safari/Chrome to `http://192.168.1.23:8000`.
   - Allow “Local Network” permission if prompted.
   - Keep the Mac awake and not sleeping during the workshop.
4. If venue Wi-Fi isolates clients, use Mac’s Personal Hotspot or a travel router.

Backend health: `/health/live` (process) and `/health/ready` (dataset ready, language_status).

## Screenshots (emulated)

- `docs/screenshots/screenshot-phone-choose.png` — 390×844, Choose stage, long title wrapping, no overflow.
- `docs/screenshots/screenshot-desktop.png` — 1280×800, two-panel layout.
Browser emulation does not establish real-device behavior — see checklist below.

## Manual iPhone / Android checklist (perform on device)

Check each stage at 360–430 CSS px (narrow portrait and landscape):

- [ ] **Choose:** search, add 1 song, My List chip appears, remove works, filters do not remove My List.
- [ ] **Keyboard:** tap search input, keyboard appears, stage nav and bottom bar remain reachable, focused field not obscured, can scroll to Generate.
- [ ] **Listen:** Generate 5, carousel shows 1/5 with dots, Previous/Next (44 px) and keyboard ←→ work, all 5 reachable, indicator updates.
- [ ] **External handoff:** tap YouTube search, Spotify search — opens in YouTube/Spotify app or browser tab. Return via system Back / gesture — app still shows same run and stage (localStorage).
- [ ] **Reveal:** I’ve listened is large, tap reveals evidence, check that genre/year/evidence were hidden before, score and score-help were visible before, external link does not auto-mark as listened.
- [ ] **Reflect & notes:** enjoyment/connection selects persist per result and per run, run notes persist.
- [ ] **Compare:** two runs selectable, controlled comparison label correct, vertical comparison readable without horizontal scroll.
- [ ] **Describe:** song select, category filter, fits/partly/misses, prepared examples clearly labeled as prepared vs live (disabled shows prepared mode).
- [ ] **Text search:** when live disabled, shows “Live search isn’t available — showing prepared examples” and does not fabricate results.
- [ ] **Notes & export:** Download JSON/Markdown contains actual seeds, results, notes.
- [ ] **Refresh:** on any stage, pull-to-refresh or reload preserves My List, activeRun, activeResultIndex, stage; re-opening after YouTube/Spotify handoff preserves.
- [ ] **Overflow:** no horizontal page scroll at 360 px, long titles wrap, touch targets ≥44 px, text readable without zoom.
- [ ] **Accessibility:** VoiceOver/TalkBack reads stage tabs, Add buttons have full “Add Title by Artist to My List”, carousel has roledescription and keyboard.

Report physical-device checks as **pending** until performed. Current status: **pending** (emulated Chrome/WebKit passed, real devices not yet tested).

## Known phone considerations

- Bottom bar is `position: sticky` with `env(safe-area-inset-bottom)` so iPhone home indicator does not obscure primary action, and keyboard does not trap navigation.
- Stage nav is horizontally scrollable with snap, sticky top with blur, works at 360 px.
- All inputs use `inputMode` and proper types for numeric keyboards where appropriate.
