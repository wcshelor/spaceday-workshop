# ListenBrainz model source

Source: https://data.metabrainz.org/pub/musicbrainz/listenbrainz/sample/listenbrainz-sample-20250610-094311-full/listenbrainz-sample-dump-20250610-094311.tar.zst

Snapshot 2025-06-10; retrieved 2026-10-23. CC0-1.0, publisher's `COPYING`
retained. Attribution: ListenBrainz contributors / MetaBrainz Foundation.

235 MiB archive verified against publisher's `.sha256`:
`509282544c50b324db8dfb4e33a5af4012f514c153da077a0fb07f093956168b`.
Only `lbdump/spark/recording_feedback.parquet` is used. These are real explicit
loves/dislikes, not play counts, synthetic data, or tag-derived embeddings.

To reproduce: download the URL above and its `.sha256` sibling, verify SHA256,
and extract `listenbrainz-sample-dump-20250610-094311/lbdump/spark/recording_feedback.parquet`
with `tar --zstd`. Copy to `data/sources/listenbrainz/recording_feedback.parquet`.
Run `python scripts/build_collaborative_artifacts.py` from the repository root.
The derived `meta.json` pins the extracted parquet's SHA256.

Other sources inspected:

- Full 2026-10-15 listening dump: 233 GB compressed.
- Compact 2026-10-22 feedback dump: 5,914,482 raw rows with recording MSIDs,
  not recording MBIDs; needs additional MessyBrainz mapping. Not used for model.
- MLHD+: large, non-commercial-only dataset. Not downloaded or incorporated.

The compact official sample already provides MBIDs. Joins here are exact-ID,
without canonical/redirect enrichment or title guesses. Coverage is specific
to this sample. Source contains public numeric listener IDs; source data stays
outside deployed assets. Exported artifacts contain only aggregate song data.
