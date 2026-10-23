# Workshop data

This collection joins existing CLAP audio embeddings with MusicBrainz metadata and AcousticBrainz measurements. No audio is downloaded or distributed. All network activity in the preparation scripts reads public data; it does not submit anything to the source services.

## Layout

- `sources/clapback/`: pinned snapshot manifest, complete compressed vectors, and recording-identity claims. This larger source cache lets us revise selection without downloading the embeddings again.
- `sources/musicbrainz/`: compressed, cached recording-search responses. Each query contains up to 100 exact recording IDs. Requests are rate-limited and retried with backoff.
- `sources/acousticbrainz/`: cached low-level and high-level responses, individually keyed by recording ID. JSON `null` means a successful query found no matching submission; a fetch failure is logged separately.
- `catalogue/`: browsable source inventory and annotated candidate pool. These are preparation artifacts, not the final app catalogue.
- `workshop/`: compact app-ready collection, manifest, features, and vectors.

## Using the final collection

`songs.json` is the authoritative ordered list. `songs.csv` is a convenient browsing copy. `features.json` is keyed by MusicBrainz recording ID. `clap_embeddings.f32` is a row-major, little-endian float32 matrix with 512 columns, in `embedding_index` order from `songs.json`. The manifest records its shape and checksums. `clap_embeddings.json.gz` is a readable alternative containing the same vectors and explicit recording IDs.

The float matrix contains audio-derived CLAP vectors; no audio encoder is needed to use them for song similarity. New text queries require the text encoder paired with the exact recorded CLAP pipeline. These vectors cannot be mixed with a different CLAP checkpoint simply because both have 512 dimensions. This snapshot does not supply timestamped segment vectors.

Listening URLs are labelled **search links**, not verified links to an exact recording. Search results may present remixes, live versions, or covers. Recording IDs and disambiguation fields preserve the intended identity. Dates are MusicBrainz first-release dates for that recording, not guaranteed original-composition dates.

## Curation

Initial target: 1,500 recordings, from 1960 through 2022, with at most six per primary artist. The candidate pool is larger to allow for missing AcousticBrainz records. Selection uses broad style families, decade balancing, explicitly chosen familiar seed tracks, and artist diversity. It excludes missing dates/durations, very short/long tracks, explicitly labelled live recordings, interviews, commentary, karaoke, skits, and demos. Duplicate artist/title pairs are removed, preferring the earliest eligible dated recording. Explicitly identified spoken-comedy material is excluded. These heuristics do not guarantee every remaining recording is the canonical studio version.

`familiarity_band` is an editorial estimate: recognisable anchors, deeper cuts by established artists, and discovery candidates. It is **not measured popularity**, a chart ranking, or a prediction that a particular student knows the song. Discovery candidates can include artists popular within their communities. The catalogue is a curated sample of Clapback's available music, not a representative survey of Western music.

Broad style families are derived from MusicBrainz tags using positive tag-vote scores, with generic tags downweighted and a documented track override. Genres overlap, tags can be sparse or incorrect, and generic tags can mislead. Keep original tags alongside the assigned family; final coverage is reported rather than assumed. Shortfalls in country, jazz, soul, or older recordings should be addressed through explicit future additions, not relabelling unrelated tracks.

MusicBrainz recording IDs are joined to contributor-supplied Clapback identity claims. Conflicting tied claims are excluded. When several vectors name the same recording, choose the one with the strongest claim count, then contributor count, then fingerprint hash for deterministic ties. An identity claim is not independent verification of the source audio.

AcousticBrainz offset 0 is used consistently. It can describe a different rip/master from the CLAP contribution, even under the same recording ID. Full source records preserve extractor versions, audio properties, and metadata; the compact features retain selected measurements and classifier scores. Classifier labels are predictions, not objective emotions. Binary vocal-gender classification is excluded from the app-ready feature set.

## Licences and attribution

- **Clapback snapshot:** publisher-declared CC0 1.0 for vectors and identity claims. Source: <https://clapback.seethroughlab.com/export>. CC0: <https://creativecommons.org/publicdomain/zero/1.0/>. The manifest pins the source date and pipeline. This declaration does not grant rights to recordings, and none are included.
- **MusicBrainz:** core catalogue data is CC0; supplementary data, including user tags, is CC BY-NC-SA 3.0. This collection includes tags and preserves these conditions; do not describe the complete combined collection as CC0. Attribution: MusicBrainz contributors / MetaBrainz Foundation. <https://musicbrainz.org/doc/About/Data_License>, <https://creativecommons.org/licenses/by-nc-sa/3.0/>. Curation fields are modifications made for this workshop, not MusicBrainz endorsements.
- **AcousticBrainz:** publisher-declared CC0 for the data. Attribution retained for provenance: AcousticBrainz, MetaBrainz Foundation, and Music Technology Group, Universitat Pompeu Fabra. <https://acousticbrainz.org/>.
- Model software/checkpoints have separate terms. Selecting these vectors does not settle licensing for a text encoder we might deploy later.

The cached source responses may include supplementary metadata beyond what is used by the app. Keep source-specific terms with any redistributed extracts. No assertion is made that the publishers own rights to the underlying music.

## Reproducing preparation

Use Python 3; the preparation scripts use the standard library and do not install models.

```sh
python3 scripts/prepare_data.py all
python3 scripts/curate_data.py plan --target 1500
python3 scripts/curate_data.py features
python3 scripts/curate_data.py build --target 1500
python3 scripts/validate_data.py
```

Run these from the repository root. Preparation resumes from cached responses. The existing Clapback manifest is reused deliberately. For a new snapshot, archive the entire source directory and associated derived collection first; do not delete only the manifest, because weekly exports reuse filenames. Treat refreshed sources as a new collection version. Do not rerun `plan` midway through feature acquisition unless intentionally updating the candidate pool; rerunning `features` fills missing cached records for the new pool.

The final validation report (`validation.json`), human-readable audit (`CURATION.md`), and manifest describe what was actually obtained. The frozen `catalogue/candidates.json` is part of the curation record; intentionally rerunning `plan` can create a revised edition after policy edits. Do not infer that a missing file means a recording has no data; check fetch failures and unresolved-ID lists.
