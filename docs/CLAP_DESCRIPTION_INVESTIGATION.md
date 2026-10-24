# Why one description dominates CLAP matches

> Historical prompts-v2 investigation. The active bank is now prompts-v3 (200
> descriptions); the overused phrase was retired with the rationale preserved.
> See [the bank revision and new measurements](DESCRIPTION_MATCHING.md).

Measured 24 October 2026 on dataset `e755bbd1cc5512d4`, 1,500 songs,
71 descriptions (`prompts-v2`), text checkpoint
`laion/clap-htsat-unfused@8fa0f1c6d0433df6e97c127f64b2a1d6c0dcda8a`.
No production ranking, prompt bank or model artifact was changed in this investigation.
The controlled experiments were performed locally and did not query a live interpreter.

## Conclusion and limits

The evidence does **not** identify a mistake in our text embedding or cosine-ranking
implementation. It supports a substantial common-direction/baseline effect in this
particular catalogue, plus sensitivity to wording and the choice of candidate
phrases. It does not prove that the upstream audio vectors are correctly identified
or that their checkpoint/preprocessing exactly match the text branch. It does not
establish a universal limitation of every CLAP model or corpus.

The right workshop description is a limitation of **our current CLAP description
retrieval setup**. It is not a claim that half the songs objectively contain funk
guitar, nor evidence that CLAP song-to-song recommendations are broken.

## Which descriptions are common?

Counts below are exact for the frozen catalogue, not population estimates. “Top 8”
corresponds to the unfiltered list length displayed by the activity. Each current
prompt has a distinct paraphrase group, so diversity selection does not change
these raw top-eight positions.

| Description | First | Share | In top 8 |
|---|---:|---:|---:|
| syncopated funk groove with off-beat guitar | 801 | 53.40% | 1,400 |
| laid-back half-time groove, relaxed drums | 148 | 9.87% | 1,363 |
| fast energetic drums with bright synths and uplifting mood | 143 | 9.53% | 1,167 |
| slow tempo with intimate vocals and sparse piano | 101 | 6.73% | 646 |
| lo-fi tape hiss with warm guitar and nostalgic feeling | 71 | 4.73% | 946 |
| dense wall of distorted guitars, loud and powerful | 53 | 3.53% | 374 |
| melancholic and wistful, bittersweet mood | 41 | 2.73% | 237 |
| bright brass horns, punchy and festive | 28 | 1.87% | 1,023 |
| steady four-on-the-floor beat, danceable | 21 | 1.40% | 684 |
| breakbeat, chopped drums with vinyl crackle | 20 | 1.33% | 607 |

Only 28 of the 71 prompts are ever first. In the default **182-song shared pool**,
the funk phrase is first for **118 songs (64.84%)**. Its first-place rates vary
substantially by editorial style family: pop 84.51%, funk/soul/R&B 79.78%, classic
rock 77.78%, electronic dance 33.51%, ambient/instrumental 17.24%. These broad tags
are not ground truth for syncopation or guitar presence.

Full results for all 71 prompts, including score distributions and category/style
breakdowns, are in [the frequency CSV](diagnostics/clap_prompt_frequencies.csv) and
[bank diagnostics JSON](diagnostics/clap_bank_diagnostics.json).

## Checks already performed

### Data and ranking integrity

- All 1,500 audio and 71 text vectors are finite and unit length. Maximum norm
  errors are approximately `7.7e-9` and `1.75e-7`, respectively.
- There are 1,500 distinct audio rows and 71 distinct text rows: no exact vector
  duplication explains the repeated description.
- Scalar Python dot products and the independent float64 matrix computation agree
  to approximately `6.1e-16` on 250 sampled song/prompt pairs.
- The runtime's full top-eight list agrees with independent raw cosine ranking
  for **all 1,500 songs**.
- Permuting the prompt bank does not change first-place identities for any song.
- The smallest top-one/top-two margin is about `0.0000317`; no margin is below
  `1e-6`. Numerical ties are not the explanation for the original bank.
- The existing data validator separately passed all 25 integrity checks, including
  JSON/binary vector agreement and embedding row order. These establish internal
  alignment; they do not authenticate an upstream recording claim against audio.

### Encoder reference comparison

Loaded the **full `ClapModel`** from the same cached pinned checkpoint and used its
`get_text_features` method, independently of the builder's
`ClapTextModelWithProjection(...).text_embeds` path.

- Maximum coordinate difference versus the stored vectors: **`2.98e-8`**.
- First-place descriptions agree for **all 1,500 songs**.
- Fixed-length 77-token padding versus dynamic padding differs by at most
  `3.76e-7`; single-item versus batch encoding by at most `1.64e-7`.
- Shuffling the encoding batch order produces identical restored rows in this run.
- The upstream reference's direct `tokenizers` token IDs match our tokenizer for
  all 71 phrases. The longest phrase occupies only 15 tokens including special
  tokens, so 77-token truncation is not affecting the bank.

This rules out an observed difference between these two local text paths. It is
not an independent comparison against an archived upstream ONNX artifact or an
original audio waveform.

For reference, inspected Clapback commit
`1675ae2c060879bdbfc829e4b62f4ca356cbfae9`: its
[text export](https://github.com/seethroughlab/clapback/blob/1675ae2c060879bdbfc829e4b62f4ca356cbfae9/packages/embed/scripts/export_models.py)
uses `ClapModel.get_text_features`; its
[tokenizer and artifact code](https://github.com/seethroughlab/clapback/blob/1675ae2c060879bdbfc829e4b62f4ca356cbfae9/packages/embed/src/clapback_embed/artifacts.py)
uses the RoBERTa tokenizer. Its
[audio pipeline](https://github.com/seethroughlab/clapback/blob/1675ae2c060879bdbfc829e4b62f4ca356cbfae9/packages/embed/src/clapback_embed/__init__.py)
pools window outputs before normalization. This is current source inspection;
we have not established that exact source commit and model bytes for every
contribution in the 18 October audio snapshot.

## What explains the concentration?

### A phrase can be close to the catalogue generally

The mean of the unit audio vectors has length **0.8086**. If these directions were
widely balanced, their mean would be much closer to zero. Here they share a large
common component. The largest singular direction accounts for about 66.7% of the
uncentered audio matrix's squared singular-value energy; after subtracting the
mean, the leading component accounts for about 18.1%. These describe the current
geometry; they do not diagnose its cause or establish semantic quality.

For audio vector `a_i`, text vector `t_j` and audio mean `mu`, the identity is:

`a_i · t_j = mu · t_j + (a_i − mu) · t_j`.

The first term is a **prompt-specific baseline shared by every song**. The second
is the song's deviation from that baseline. Our funk phrase has mean similarity
**0.4769**, versus 0.4274 for laid-back drums and 0.3811 for energetic drums/synths.
Thus it starts with a substantial advantage across the catalogue; winning need
not mean every named musical detail was separately detected.

As a geometry-only control, 50 banks of 71 random unit directions had a median
largest first-place share of **37.37%** (10th–90th percentiles 23.19–59.41%). These
are meaningless directions, not semantic prompts. This demonstrates that clustered
audio vectors can create a dominant candidate without any special funk semantics.
It is not a hypothesis-test p-value or an estimate of CLAP accuracy.

### Wording and candidate selection matter

Encoded **77 controlled phrases** with the full reference model, without changing
the real bank. Catalogue-wide mean similarities include:

| Diagnostic wording | Mean similarity |
|---|---:|
| syncopated funk groove with off-beat guitar | 0.4769 |
| Funky music with syncopated guitar playing. | 0.4636 |
| A recording of music with a syncopated funk groove and off-beat guitar. | 0.3758 |
| syncopated funk groove | 0.3637 |
| A recording of music. | 0.4517 |
| a dog barking | -0.0345 |
| a person speaking | -0.1122 |

Adding natural sentence framing lowers the original phrase's mean by about 0.10;
a completely generic music description scores highly. Nonmusic controls score
much lower on average. This is consistent with coarse music discrimination plus
wording-sensitive fine comparisons. It is not proof of audible correctness.

A separate balanced bank of ten concepts with four matched templates still has
concentration: “heavy metal” variants win for 588 songs (39.2%). With one identical
sentence template per concept, heavy-metal wins range from 481 to 754 songs across
templates. This does not mean those recordings are heavy metal. It demonstrates
that simply giving each concept the same number of phrases does not remove the
ranking/wording effect; the original bank also lacks a dedicated heavy-metal label.

Negation deserves explicit testing: “music with guitar” and “music without guitar”
have text-vector cosine **0.896** and catalogue score correlation **0.872**.
“Instrumental music” and “music without singing” have catalogue mean scores
0.353 and 0.115, despite their intended overlap. These are diagnostics of text
behavior, not measured negation error rates against labeled recordings.

### Removing one phrase will not resolve the mechanism

Remove only the funk candidate: laid-back drums becomes first for **527 songs
(35.13%)**. The candidate that wins changes, but broad concentration remains.

Experimental adjustments, leaving the underlying embeddings unchanged:

| Scoring policy | Funk first | Distinct winning prompts |
|---|---:|---:|
| Current raw cosine | 801 | 28 |
| Subtract each prompt's catalogue mean | 58 | 64 |
| Standardize each prompt by catalogue mean and standard deviation | 35 | 71 |

Mean subtraction changes 1,264 first-place results; standardization changes 1,357.
Neither is a validated improvement. They ask a different question: unusually high
similarity for this prompt relative to the chosen corpus, rather than highest raw
CLAP similarity. More varied output can still be less accurate. Any such change
needs held-out listening judgments, its own identity, and honest scoring labels.

The [encoder/control JSON](diagnostics/clap_encoder_diagnostics.json) contains all
control phrases, score summaries, template outcomes and numerical comparisons.
Duplicate wording is deduplicated in expanded-bank comparisons and score
improvements require a `1e-6` margin to avoid treating roundoff as an improvement.

## Permanent tests to implement: design brief

### Goal

Create a reproducible offline evaluation harness that separates encoding/ranking
bugs from prompt/corpus bias and semantic matching errors. Keep the production
raw-cosine method unchanged while gathering evidence.

### Constraints

Use pinned local artifacts; ordinary unit tests must not download model weights.
Separate lightweight integrity regressions from optional encoder/audio integration
tests and human evaluation. Do not require uniformly distributed winners, call
centering an improvement without labels, or use model predictions as human truth.
Do not retrain or modify catalogue/source audio for this investigation.

### Relevant files

- Must read: `scripts/build_description_artifacts.py`,
  `backend/app/data_store.py`, `backend/tests/test_descriptions.py`,
  `artifacts/language-v1/meta.json`, `content/prompts-v1.json`.
- Summarized context: vectors are 1,500×512 audio and 71×512 text; all groups are
  distinct; current method ranks cosine with optional category filtering.
- Read only if blocked: frozen source manifests and the upstream reference files
  linked above. Raw acquisition/curation and collaborative training are out of scope.

### Acceptance criteria

1. **Integrity regressions:** validate checksums, unit norms, finite values,
   dimensions, prompt IDs/order and row mapping. Verify scalar/matrix/API rankings,
   shuffled candidate order, batch permutations, and category filters. Altering a
   row or omitting projection/normalization must be detected by suitable fixtures.
2. **Pinned encoder parity:** optional integration suite compares full reference,
   projected text-only path and archived upstream ONNX fixtures on short/long
   prompts, batch sizes and padding; record checkpoint/tokenizer/weight hashes and
   library versions. Use explicit numerical tolerance, e.g. max coordinate error
   below `1e-5` for tested equivalent fp32 paths, not exact byte equality.
3. **Distribution diagnostics:** output top-1/3/5/8 frequency, margins, category
   coverage, prompt means/variance, centroid/PCA summaries, and winner concentration
   by style, decade, artist-balanced sample and shared pool. Compare to the pinned
   edition; surface changes for review rather than declaring concentration itself
   a universal failure. Histogram invariance under shuffled song metadata is not
   evidence of correct recording identity.
4. **Controlled text evaluation:** fixed paraphrases, single-word ablations,
   matched templates, generic/nonmusic/nonsense controls and negation pairs. Report
   score/rank sensitivity and concept-level aggregation, with balanced phrase
   counts. Keep comparison banks/version and duplicate/tie policy explicit.
5. **Audio reference tests:** where exact permitted source audio is available,
   re-encode representative clips/tracks through the publisher's matching pipeline
   and compare with archived fixtures. Test sample rate, mel path, windowing,
   pooling, precision and checkpoint separately. Silence/noise/click/tone controls
   can reveal gross failures but cannot establish music-description accuracy.
6. **Independent semantic evaluation:** prepare 30–50 verified recordings with
   two listeners, explicit observable labels (guitar presence, vocals, approximate
   tempo) and separate subjective mood judgments. Include difficult negatives.
   Freeze an artist-separated evaluation split before tuning. Report pairwise
   discrimination, top-k judged precision, agreement and coverage by subgroup.
   AcousticBrainz estimates/tags may be weak-reference diagnostics, not ground truth.
7. **Alternative-scoring comparison:** assess raw cosine, prompt-mean subtraction,
   standardization and template ensembles against the same held-out judgments.
   Fit reference statistics on the development split only. Promote a policy only
   when it improves the agreed semantic measures without hiding regressions;
   otherwise preserve raw cosine with the limitation disclosed.

### Verification

Lightweight fixtures run with backend tests. Optional encoder/audio tests require
explicit local model/reference paths and skip with a clear reason when absent.
An offline command should produce versioned JSON/CSV/Markdown with hashes, random
seeds, dependency versions, exact sample counts, tested settings and failures.
Store prompt fixtures and evaluation code so these one-off measurements can be
reproduced; the current report/JSON files alone are not a permanent test suite.

## Suggested workshop limitation wording

**Participant-facing:**

“CLAP compares this song with a limited set of phrases. Some phrases score highly
for many different songs, and changing the wording can change the ranking. A match
does not verify every musical detail in the phrase. Listen and decide what fits.”

**Facilitator note:**

“In this edition, ‘syncopated funk groove with off-beat guitar’ ranks first for
801 of 1,500 songs. Independent checks reproduced the embedding and ranking
calculations. The repeated phrase illustrates a limitation of this catalogue,
prompt bank and raw CLAP comparison: a broadly favored description can outrank a
more specific one. We have not established that all those songs contain the
named features, or that this describes every use of CLAP.”
