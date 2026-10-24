# Song description matching — 24 October 2026

Today's demo keeps song-to-description matching and retires free-form live text search.

The 256 curated phrases are encoded offline with the text branch of
`laion/clap-htsat-unfused`, using the checkpoint revision recorded in
`artifacts/language-v1/meta.json`, 77-token truncation and L2 normalization.
The server compares each song's existing unit audio vector with the unit text
vectors using cosine similarity, then standardizes each phrase against its
full-catalogue mean and population standard deviation. It filters categories before selection and
prefers distinct paraphrase groups, filling from repeats only when needed.
Similarity values are not confidence percentages. Participant judgments do not
train the model.

Runtime uses only numpy and the prepared artifact files. No model download,
ONNX service, torch installation, or live inference is needed for the workshop.
Missing, placeholder, corrupt, or incompatible description artifacts return an
explicit unavailable response; they never fall back to prompt-bank order.
The upstream audio pipeline name identifies the paired model family; its exact
checkpoint hash/preprocessing cannot be independently recovered from these data.
A facilitator listening check remains appropriate before presenting results.

## Current discussion method: prompts-v4 and description-standardized-v1

The bank now adds **56 listening invitations**: 32 emotional phrases and 24
atmospheric/context phrases, for 256 descriptions total. Examples include quiet
anticipation, emotional release, vulnerability, resilience, a quiet evening alone,
rain through a window, a dreamscape and an empty echoing hall. Mood and atmosphere
are subjective possibilities to discuss; these are not predictions of a listener's
emotions or facts about where the recording was made.

For each prompt j, compute raw audio–text cosine for every one of the frozen
1,500 recordings, then cache its mean and **population** standard deviation at
startup. Rank a selected song i by:

`description_score(i,j) = (cosine(i,j) − mean_j) / std_j`.

This asks which phrases match the song unusually well relative to their usual
scores. It deliberately supports varied listening/discussion instead of claiming
the most accurate caption. No category filter, selected song list or collaborative
pool changes the reference. Prompts with standard deviation <= 1e-8 are excluded;
if all are constant the capability is unavailable. Paraphrase diversification and
deterministic ID tie-breaking remain in place.

API responses retain raw cosine as `similarity`, expose the ranking value as
`description_score`, and include the reference dataset and a scoring identity
binding the method, dataset, prompt-bank checksum and text-vector checksum. Neither
number is an enjoyment probability or confidence percentage. UI judgments use
this identity in their keys; earlier judgments remain saved without being silently
attached to the new method. Song-to-song recommendations retain their existing
scoring methods. No retraining or live encoder is needed.

### Same-bank comparison, measured on all 1,500 songs

| Policy on the 256-prompt bank | Distinct first-place phrases | Largest first-place count |
| --- | ---: | ---: |
| Raw cosine | 89 | 390 (26.0%, country arrangement) |
| Standardized discussion method | 201 | 38 (2.53%, gradual build) |

The shared 182-song pool's largest first-place count changes from 66 to 11.
These demonstrate diversity of outputs, not better semantic accuracy. A human
listening check remains outstanding; standardization can promote a low absolute
cosine that is merely unusual for a phrase.

Reproducible current reports:
[standardized JSON](diagnostics/prompts-v4-standardized.json),
[standardized CSV](diagnostics/prompts-v4-standardized.csv),
[raw comparison JSON](diagnostics/prompts-v4-raw.json),
[raw comparison CSV](diagnostics/prompts-v4-raw.csv).

```sh
python scripts/audit_description_bank.py --output docs/diagnostics/prompts-v4-standardized
python scripts/audit_description_bank.py --output docs/diagnostics/prompts-v4-raw --method raw
```

## Prompt-bank revision: prompts-v3

On 24 October 2026, the bank expanded from 71 to **200 descriptions**: 70 retained
phrases plus 130 additions about particular instruments, vocal techniques, drum
patterns, production effects, arrangements, melody and harmony. Examples include
brushed snare drums, walking upright bass, pedal steel guitar, slapback vocal echo,
palm-muted guitar, a repeating piano motif and suspended guitar chords. Melody
and harmony are new filter categories. These are candidate descriptions, not
verified annotations of the recordings.

We retired `rhy-002`, **“syncopated funk groove with off-beat guitar”**. In the
previous 71-prompt bank it ranked first for **801 of 1,500 songs (53.4%)**, appeared
in the top eight for **1,400 songs (93.3%)**, and ranked first for 118 of the shared
182-song pool. It was too broadly favored to be a useful distinguishing phrase
for this workshop, so we removed it as an editorial choice. Its ID, text, measured
coverage and rationale remain in `retired_prompts` in the bank JSON. Its ID will
not be reused. This observation refers to prompts-v2, not the expanded bank.

Removing the phrase and adding alternatives does not establish better musical
accuracy or remove CLAP's wording/corpus bias. This revision still used raw cosine scoring; prompts-v4 below replaces that
policy for the discussion activity.
See [the original investigation](CLAP_DESCRIPTION_INVESTIGATION.md) for the
numerical checks, historical measurements and limits of this conclusion.

### Measured result after expansion

The rebuilt prompts-v3 bank has 76 distinct first-place descriptions, compared
with 28 in prompts-v2. Its largest first-place share is **405 of 1,500 (27.0%)**:
“Country vocals with strummed guitar, pedal steel and a steady rhythm section.”
Next are the rap/sample description (233; 15.53%) and the synth-pop arrangement
(130; 8.67%). The country phrase also ranks first for 67 of the shared 182 songs.
These are coverage measurements, not accuracy scores or verified genre labels.
The remaining concentration is disclosed rather than treated as solved.

Historical prompts-v3 results: [JSON](diagnostics/prompts-v3.json) and
[CSV](diagnostics/prompts-v3.csv). Reproduce them without an encoder or network:

```sh
python scripts/audit_description_bank.py --output docs/diagnostics/prompts-v3 --method raw
```

## Rebuilding the prepared bank

Use a separate preparation environment with torch, transformers, and numpy.
The command below uses an already cached full checkpoint commit without network
access; omit `--local-files-only` when provisioning that checkpoint initially:

```sh
python scripts/build_description_artifacts.py --cache-dir /tmp/spaceday-clap-cache --revision REVISION_FROM_META --local-files-only
python -m pytest backend/tests/test_descriptions.py -q
```

Only the small `prompt_embeddings.f32` and `meta.json` files go into deployment.
The metadata records bank/vector checksums, the checkpoint revision, and build
library versions. The old `build_language_artifacts.py` refuses to overwrite a
real bank with its legacy placeholder flow.

## Retired experiment

`frontend/src/app/RetiredLanguageLab.tsx` preserves the former live-search UI but
is not imported by the demo. The API client, schemas, text history storage and
unavailable `/api/text-search` endpoint remain for future work. No live search
input, examples invoking searches, or query history are shown in today's UI.
Historical ONNX setup and implementation-status notes describe an older plan;
they do not describe the current demo's runtime requirements.
