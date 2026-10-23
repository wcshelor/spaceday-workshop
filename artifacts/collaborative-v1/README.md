# Listener patterns: collaborative-v1

Real 32-factor collaborative model trained offline from ListenBrainz song loves.
TF-IDF weighted, row-normalized truncated SVD; unit song factors `V sqrt(S)`;
mean seed cosine for 1–5 songs. No audio, CLAP, or workshop reactions train it.
A teaching model, not a replica of Spotify's production system.

## Coverage

- 219/1,500 songs have positive feedback with exactly matching recording MBIDs.
- 182/1,500 have usable factors after filtering: >=5 listeners per item,
  >=5 items per listener, then recheck item support.
- Training: 2,516 listeners, 10,082 songs, 152,036 positive listener/song pairs.
- `coverage.csv`: every catalogue song, raw distinct positive listeners,
  retained training listeners, and availability.
- Exact MBIDs only. Redirects/canonical versions were not merged; no title
  guesses. Coverage is a lower bound for this sample, not all ListenBrainz.
  Canonical mapping can combine live and studio versions, so it cannot be
  treated as an exact-audio identity join for comparison against CLAP.
- Unsupported songs are excluded; unsupported seeds return an explicit error.

## Source and reproduction

Official ListenBrainz sample, 2025-06-10; CC0-1.0. Parquet contains 204,429 rows:
200,739 loves and 3,690 dislikes. Dislikes are excluded; absence is not dislike.
Source download, license, and verified archive checksum:
`data/sources/listenbrainz/README.md`. `meta.json` pins parquet, catalogue and
vector checksums, parameters, random seed, calibration, and evaluation.

From the repository root, using the preparation dependencies in the backend's
`collaborative-build` extra (pandas, pyarrow, scipy):

```sh
python scripts/build_collaborative_artifacts.py
python -m pytest backend/tests/test_collaborative.py -q
```

Runtime needs only numpy. Deployable files contain song factors, aggregate
counts and reference percentiles, no listener IDs or feedback rows. The vector
file is 23,296 bytes. Source data is excluded from Docker. Without this artifact
directory, the app offers the original three methods. Original CLAP/catalogue
files remain untouched.

## Evaluation

Seed 20261023. Hide one workshop love per listener with >=3 workshop loves
BEFORE fitting; use up to five other workshop loves as seeds. Targets and seeds
must have >=5 remaining training listeners. Both models rank the same 182-song
pool, excluding seeds. 793 eligible listener cases:

| Model | Hit rate @10 | NDCG @10 |
|---|---:|---:|
| Collaborative SVD | 27.36% | 0.1529 |
| Train-only popularity | 23.58% | 0.1105 |

This random holdout is not temporal or evidence of participant enjoyment.
The historical, self-selected sample is small; same-artist results are common.
No significance claim. A human listening pilot remains necessary.

Percentiles use 512 sampled seed sets for each seed count 1–5 from this model's
supported catalogue. No CLAP calibration reuse; percentages are not enjoyment
odds or a comparison of model quality. For method comparisons, keep the shared
supported-song pool, seeds, restrictions and preferences unchanged.

Model identity is included in run fingerprints, response versions and exports.
