# Song description matching — 24 October 2026

Today's demo keeps song-to-description matching and retires free-form live text search.

The 71 curated phrases are encoded offline with the text branch of
`laion/clap-htsat-unfused`, using the checkpoint revision recorded in
`artifacts/language-v1/meta.json`, 77-token truncation and L2 normalization.
The server compares each song's existing unit audio vector with the unit text
vectors using cosine similarity. It filters categories before selection and
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

## Rebuilding the prepared bank

Use a separate preparation environment with torch, transformers, and numpy:

```sh
python scripts/build_description_artifacts.py --cache-dir /tmp/spaceday-clap-cache --revision REVISION_FROM_META
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
