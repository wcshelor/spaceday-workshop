# Music Recommendation Workshop: Sources, Provenance, and Methods

*Repository documentation reviewed 24 October 2026. Dataset versions below describe the frozen repository artifacts, not the latest upstream releases.*

## Numbered bibliography for presentations

Use these stable numbers in slide footers. Append new sources without renumbering existing entries. Reviews and handbook chapters provide field context; method papers do not independently document our local formulas or a company's current production systems. Online sources accessed 24 October 2026. Legacy P/D labels below remain valid aliases.

<a id="ref-1"></a>
**[1]** Deldjoo, Y., Schedl, M., & Knees, P. (2024). Content-driven music recommendation: Evolution, state of the art, and challenges. *Computer Science Review, 51*, 100618. https://doi.org/10.1016/j.cosrev.2024.100618. **Review:** content-based and hybrid music recommendation.

<a id="ref-2"></a>
**[2]** Schedl, M., Zamani, H., Chen, C.-W., Deldjoo, Y., & Elahi, M. (2018). Current challenges and visions in music recommender systems research. *International Journal of Multimedia Information Retrieval, 7*, 95–116. https://doi.org/10.1007/s13735-018-0154-2. **Review:** listener needs, cold start, playlists and evaluation beyond accuracy.

<a id="ref-3"></a>
**[3]** Schedl, M., Knees, P., McFee, B., & Bogdanov, D. (2022). Music recommendation systems: Techniques, use cases, and challenges. In *Recommender Systems Handbook* (3rd ed.). Springer. [Author-group publication record](https://hcai.test.cp.jku.at/publications/2022_musicrsbook/). **Handbook review:** music recommendation approaches and listening use cases.

<a id="ref-4"></a>
**[4]** Spotify Engineering. (2021, November). *The rise (and lessons learned) of ML models to personalize content on Home (Part I).* [Engineering article](https://www.engineering.atspotify.com/2021/11/the-rise-and-lessons-learned-of-ml-models-to-personalize-content-on-home-part-i). **First-party historical architecture:** candidate generation, ranking and multiple recommendation models; not a complete current system specification.

<a id="ref-5"></a>
**[5]** Apple. (n.d.). *Apple Music & Privacy.* [Privacy documentation](https://www.apple.com/legal/privacy/data/en/apple-music/). **First-party disclosure:** personalisation inputs including listening duration, library additions and favourites; does not specify model architecture.

<a id="ref-6"></a>
**[6]** Schedl, M. (2019). Deep learning in music recommendation systems. *Frontiers in Applied Mathematics and Statistics, 5*, Article 44. https://doi.org/10.3389/fams.2019.00044. **Mini-review:** audio features, learned representations, hybrid and sequential approaches.

<a id="ref-7"></a>
**[7]** Koren, Y., Rendle, S., & Bell, R. (2022). Advances in collaborative filtering. In *Recommender Systems Handbook* (3rd ed., pp. 91–142). Springer. https://doi.org/10.1007/978-1-0716-2197-4_3. **Handbook review:** neighbourhood methods, factorisation, implicit feedback and temporal models.

<a id="ref-8"></a>
**[8]** Li, W., et al. (2024). *A survey of foundation models for music understanding.* arXiv:2409.09601. https://doi.org/10.48550/arXiv.2409.09601. **Survey preprint:** broader music understanding and music–language representations, not specifically recommendation evaluation.

<a id="ref-9"></a>
**[9]** Wu, Y., Chen, K., Zhang, T., Hui, Y., Berg-Kirkpatrick, T., & Dubnov, S. (2023). Large-scale contrastive language-audio pretraining with feature fusion and keyword-to-caption augmentation. In *Proceedings of ICASSP 2023*. https://doi.org/10.1109/ICASSP49357.2023.10095969. [Open preprint, revised 2024](https://arxiv.org/abs/2211.06687) adds Marianna Nezhurina to the author list. **Method paper; P1:** LAION CLAP and upstream LAION-Audio-630K training data. Our vectors use the unfused pipeline, not every paper variant. We did not download this training corpus.

<a id="ref-10"></a>
**[10]** Porter, A., Bogdanov, D., Kaye, R., Tsukanov, R., & Serra, X. (2015). AcousticBrainz: A community platform for gathering music information obtained from audio. In *Proceedings of ISMIR 2015* (pp. 786–792). [Author-institution paper](https://www.upf.edu/documents/223346843/0/porter2015acousticbrainz.pdf/b07e89e6-6cf1-89ea-47e0-4dabf81b2978). **Dataset/platform paper; P3.**

<a id="ref-11"></a>
**[11]** Bogdanov, D., et al. (2013). Essentia: An audio analysis library for music information retrieval. In *Proceedings of ISMIR 2013* (pp. 493–498). [Author-institution publication record](https://mtg.upf.edu/node/2793). **Extractor method; P4:** upstream audio analysis, not extraction performed locally in this workshop.

<a id="ref-12"></a>
**[12]** Clapback / SeeThroughLab and contributors. (2026, October 18). *CLAP audio embeddings and recording identity claims* [Data export; snapshot 2026-10-18T05:12:18Z]. [Export documentation](https://clapback.seethroughlab.com/export). Pipeline: `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32`. CC0. **D1:** exact pinned files and identity-selection rules are documented in §2; local manifest identifies the edition used.

<a id="ref-13"></a>
**[13]** MusicBrainz contributors / MetaBrainz Foundation. (n.d.). *MusicBrainz recording metadata and community tags* [Database; cached recording-level API responses]. [API](https://musicbrainz.org/doc/MusicBrainz_API); [licenses](https://musicbrainz.org/doc/About/Data_License). Core metadata: CC0; supplementary tags: CC BY-NC-SA 3.0. **D2:** no single snapshot date is established for all cached responses; see §2 and local catalogue manifest.

<a id="ref-14"></a>
**[14]** AcousticBrainz contributors / MetaBrainz Foundation and Music Technology Group, Universitat Pompeu Fabra. (n.d.). *AcousticBrainz low-level descriptors and high-level predictions* [Database; cached submission-offset-0 responses]. [Project](https://acousticbrainz.org/). CC0. **D3:** our selected descriptor data, distinct from the platform paper [10]; no uniform response-retrieval date is recorded.

<a id="ref-15"></a>
**[15]** ListenBrainz contributors / MetaBrainz Foundation. (2025, June 10). *ListenBrainz sample dump, 20250610-094311* [Data set; `recording_feedback.parquet` subset]. [Sample archive](https://data.metabrainz.org/pub/musicbrainz/listenbrainz/sample/listenbrainz-sample-20250610-094311-full/listenbrainz-sample-dump-20250610-094311.tar.zst); [dump documentation](https://listenbrainz.readthedocs.io/en/latest/users/listenbrainz-dumps.html). CC0-1.0. Retrieved 23 October 2026 per local source record. **D4:** archive checksum and exact feedback filtering are recorded in §2.

<a id="ref-16"></a>
**[16]** Music Recommendation Workshop project. (2026). *Curated workshop catalogue and selection audit* [Derived data set; 1,500 recordings]. [Curation audit](../data/CURATION.md); [release manifest](../data/workshop/manifest.json); [attribution](../data/workshop/ATTRIBUTION.md). Derived from [12]–[14], with editorial style/familiarity labels. Preserve source-specific licenses; familiarity is estimated, not measured popularity.

<a id="ref-17"></a>
**[17]** Music Recommendation Workshop project. (2026, October 24). *Prepared description bank, prompts-v3* [Editorial text data and paired CLAP text embeddings; 200 phrases]. [Bank](../content/prompts-v1.json); [artifact metadata](../artifacts/language-v1/meta.json); [curation and matching notes](DESCRIPTION_MATCHING.md). Local candidate descriptions, not verified song annotations. The retired phrase and curation rationale remain recorded. See [9] for the encoder method.

<a id="ref-18"></a>
**[18]** Spotify. (2026, October 20). *Understanding recommendations on Spotify.* [Official explanation](https://www.spotify.com/uk/safetyandprivacy/understanding-recommendations). **Current first-party inputs:** taste profile, other listeners' behaviour, content, context and editorial curation. Selected disclosures do not establish the full current pipeline or a blanket claim of secrecy.

<a id="ref-19"></a>
**[19]** Elizalde, B., Deshmukh, S., Al Ismail, M., & Wang, H. (2022). *CLAP: Learning audio concepts from natural language supervision.* arXiv:2206.04769. https://arxiv.org/abs/2206.04769. **P2:** earlier CLAP background; not the LAION checkpoint identity.

<a id="ref-20"></a>
**[20]** Koren, Y., Bell, R., & Volinsky, C. (2009). Matrix factorization techniques for recommender systems. *Computer, 42*(8), 30–37. https://doi.org/10.1109/MC.2009.263. **P5:** factorisation background; not the exact weighted truncated SVD implemented here.

<a id="ref-21"></a>
**[21]** Spotify. (n.d.). *Find playlists on Spotify.* [Official support](https://support.spotify.com/sc-en/article/find-playlists/). Discover Weekly, Release Radar and Spotify Mixes; accessed 24 October 2026.

<a id="ref-22"></a>
**[22]** Apple. (n.d.). *Find new music with Apple Music on iPhone.* [Official support](https://support.apple.com/en-ie/guide/iphone/iph2c41e6189/27/ios/27). Discovery Station recommends music not previously played using listening history and taste profile; accessed 24 October 2026.

<a id="ref-23"></a>
**[23]** Apple. (n.d.). *Discover new music on Apple TV 4K.* [Official support](https://support.apple.com/en-gb/guide/tv/atvbc6334c54/tvos). Made for You mixes combine new music with songs the listener loves; accessed 24 October 2026.

## 1. Presentation overview

The workshop explores three different meanings of musical similarity: **similar measured properties**, **similar learned sound representations**, and **shared listener preferences**. It implements four song-to-song scoring methods. Rhythm and texture are deliberately designed distance formulas; CLAP uses pretrained neural representations; listener patterns uses a factor model fitted locally to real feedback.

| Workshop method | Question it asks | Representation | Coverage in this edition | Main strength | Main limitation |
| --- | --- | --- | --- | --- | --- |
| Rhythm (`rhythm-v1`) | Which songs have similar pulse and activity? | Three transformed AcousticBrainz measurements | 1,500 songs | Small, inspectable formula | Similar tempo/activity can conceal very different music |
| Texture (`texture-v1`) | Which songs have similar timbre and spectral properties? | 12 MFCC means plus four spectral measurements | 1,500 songs | Explicit contributions from two feature groups | Whole-recording summaries lose musical development |
| CLAP sound (`clap-v1`) | Which songs are close in an audio–language representation? | 512-dimensional pretrained audio vectors | 1,500 songs | Richer learned representation without local audio processing | Embedding proximity does not explain an audible cause |
| Listener patterns (`collaborative-v1`) | Which songs occupy similar positions in shared preferences? | 32-dimensional song factors learned from loves | 182 songs (12.1% of catalogue) | Captures associations beyond sound | Sparse, community-specific feedback and cold-start gaps |
| Text/description extension | Which audio vectors match a written description? | Real paired CLAP text vectors | 200 prepared descriptions | Offers a language-based way to explore sound | Descriptions are candidates, not verified annotations; live search is retired |

**Presentation takeaway:** agreement across methods can be informative, and disagreement is a useful discussion prompt. None of these scores establishes musical identity, enjoyment, or a universally correct recommendation. The project is a teaching system, not a reconstruction of a commercial streaming recommender.

## 2. Source register: what came from where

### D1. Clapback: existing audio embeddings and recording claims

**Credit:** Clapback / SeeThroughLab and contributors. **Source:** [export documentation](https://clapback.seethroughlab.com/export). **Pinned snapshot:** `2026-10-18T05:12:18Z`, recorded in [`data/sources/clapback/manifest.json`](../data/sources/clapback/manifest.json).

The manifest describes 26,290 embedding rows and 23,589 recording-claim rows, under publisher-declared **CC0 1.0**. These are distinct row types, not counts of verified unique songs. The frozen export base is `https://clapback-export.s3.us-east-1.amazonaws.com/exports/2026-10-18/`; the two inputs used are `embeddings-laion_clap_htsat_unfused_frontend1_artifact1_pool1_fp32.csv.gz` and `claims.csv.gz`.

**We used:** existing audio vectors, pipeline identity, fingerprint hashes, contributor counts, and recording identity claims. **We did:** join claims to vectors by fingerprint hash; reject tied conflicting top recording claims; choose among vectors for a recording by descending claim count, descending contributor count, then fingerprint hash. Selected vectors must contain 512 finite values and have norm within 0.999–1.001. They are serialized as little-endian float32; the build checks unit length rather than training an encoder or recomputing vectors.

The exact pipeline is `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32`. This identifier must travel with the vectors. A common dimensionality alone does not make embeddings from different pipelines comparable. The upstream page is mutable; its displayed latest export is not evidence for the date of this repository's pinned snapshot.

### D2. MusicBrainz: recording metadata and community tags

**Credit:** MusicBrainz contributors / MetaBrainz Foundation. **Source:** [MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API). **Terms:** [official data-license page](https://musicbrainz.org/doc/About/Data_License): core data is **CC0**; supplementary data, including tags, is **CC BY-NC-SA 3.0**.

**We used:** recording MBIDs, titles, artist credits/IDs, durations, disambiguation, first-release dates, release metadata, and tags. **We did:** query exact recording IDs in batches of up to 100, cache compressed responses, derive a browsable inventory, and select a balanced workshop catalogue. Positive tag votes inform broad style families; generic tags are downweighted and a documented editorial override is applied. Original tags remain available. Familiarity bands and familiar-song anchors are workshop editorial judgments, not measured popularity or MusicBrainz annotations.

Recording first-release dates are not guaranteed original-composition or canonical studio-release dates. Retrieval timestamps are not centrally pinned for every API response; the cache is the historical evidence. Do not describe this mixed, tag-containing collection as wholly CC0.

### D3. AcousticBrainz: measured descriptors and classifier predictions

**Credit:** AcousticBrainz, MetaBrainz Foundation, and Music Technology Group, Universitat Pompeu Fabra. **Source and terms:** [AcousticBrainz](https://acousticbrainz.org/), publisher-declared **CC0**. Research references: P3–P4 below.

**We used:** cached low-level and high-level JSON for recording MBIDs, consistently at **submission offset 0**. **We did:** retain selected rhythm, loudness, spectral, MFCC, and tonal descriptors; preserve available high-level predictions, extractor-version metadata and audio properties; omit the binary gender classifier. The baseline rankers use only the feature subsets in §4, not every stored measurement. High-level predictions support optional attributes/preferences; they are model outputs rather than objective musical or emotional facts.

Final coverage is 1,500 usable baseline feature records and 1,499 records with high-level predictions. The audit records 43 extractor-version signatures. Matching MBIDs do not guarantee that AcousticBrainz and Clapback analyzed the same rip or master. AcousticBrainz stopped accepting contributions in 2022, according to its [project page](https://acousticbrainz.org/).

### D4. ListenBrainz: explicit recording feedback

**Credit:** ListenBrainz contributors / MetaBrainz Foundation. **Source:** [official sample archive](https://data.metabrainz.org/pub/musicbrainz/listenbrainz/sample/listenbrainz-sample-20250610-094311-full/listenbrainz-sample-dump-20250610-094311.tar.zst). **Snapshot:** 10 June 2025; repository source notes report retrieval on 23 October 2026. **License:** CC0-1.0, with publisher `COPYING` retained.

**We used:** only the extracted `lbdump/spark/recording_feedback.parquet`: 204,429 rows, comprising 200,739 loves and 3,690 dislikes. **We did:** keep `feedback == 1`, deduplicate listener/recording pairs, retain items with at least five positive listeners, retain listeners with at least five remaining items, then recheck item support. This is the implemented sequence, not an iterative convergence-to-a-core procedure. Dislikes are excluded, and absent feedback is not treated as expressed dislike.

The resulting training matrix contains **2,516 listeners × 10,082 songs**, with **152,036 positive pairs**. Training includes surrounding songs beyond the workshop catalogue. Exact recording-MBID joins find feedback for 219 catalogue songs; 182 survive support filtering. No title matching, redirect resolution, or canonical-version merging is used.

Archive SHA256: `509282544c50b324db8dfb4e33a5af4012f514c153da077a0fb07f093956168b`. The extracted parquet checksum is separately recorded as `source_sha256` in [`artifacts/collaborative-v1/meta.json`](../artifacts/collaborative-v1/meta.json). These identify different files. Deployment contains song factors and aggregate counts, not listener IDs or raw feedback. See the [source record](../data/sources/listenbrainz/README.md) and [official dump documentation](https://listenbrainz.readthedocs.io/en/latest/users/listenbrainz-dumps.html).

### D5. Locally authored material and research-only sources

The 200 descriptions in [`content/prompts-v1.json`](../content/prompts-v1.json) are labeled as editorial workshop curation, updated 24 October 2026 (prompts-v3). They are not an externally collected caption dataset. Prompt-bank hashes are recorded in language metadata. Participant seeds, reactions, survey responses and notes are workshop interaction data; they do not train the shipped models.

The [post-2000 research report](POST_2000_SONG_RESEARCH.md) and [2015-onward supplement](SONG_RESEARCH_2015_ONWARD.md), with companion CSVs, are **candidate research**, not catalogue imports or retraining results. They use cached MusicBrainz/Clapback evidence, the ListenBrainz sample, live feedback probes, and aggregate popularity API results. The reports state that popularity totals combine ListenBrainz and MLHD counts; these are not globally deduplicated people. One-row feedback probes establish accessibility, not a fully downloaded training dataset. Sample and live counts overlap and must not be added.

MLHD+ was considered but not downloaded or incorporated into model training. The full 2026 listening dump and compact MSID-based feedback dump were also considered but not used. Thus these are not additional training datasets; MLHD-derived aggregate statistics do appear indirectly in the expansion research. Preserve the research CSVs' per-recording URLs and evidence labels when presenting those proposals.

## 3. Provenance map and audit trail

```text
Clapback vectors + claims ─┐
                          ├─ exact recording MBID ─ curated songs + ordered CLAP matrix
MusicBrainz metadata ─────┘                         │
AcousticBrainz offset-0 descriptors ────────────────┴─ compact features → rhythm/texture
ListenBrainz sample → positive-pair support filters → weighted SVD → supported song factors
Editorial descriptions → paired text encoder offline → 200 prepared text vectors
```

The catalogue contains **1,500 recordings, 785 primary artists, years 1960–2022**, with a maximum of six recordings per primary artist. A 2,250-recording candidate pool yielded 2,195 usable AcousticBrainz candidates before final selection. Curation balances decades, style families, familiarity estimates and artist diversity. It removes duplicate primary-artist/normalized-title pairs, preferring earlier eligible recordings, and filters missing dates/durations, unsuitable lengths and explicitly identified live/demo/karaoke/spoken material. These are heuristics, not independent verification of every studio recording. See [`data/CURATION.md`](../data/CURATION.md).

| Trace question | Repository evidence |
| --- | --- |
| Which exact recording and CLAP contribution produced this row? | `songs.json`: `recording_mbid`, `embedding_index`, `clap_fingerprint_hash`, `clap_pipeline_version`, `recording_claim_count`, `vector_contributor_count` |
| Which acoustic submission and extractor produced its descriptors? | `features.json`: MBID key, `source_submission_offset`, `analysis_version`, `audio_properties`; cached low/high-level JSON |
| What selection rules were applied? | `scripts/curate_data.py`, frozen `data/catalogue/candidates.json`, `data/CURATION.md` |
| Which bytes were distributed? | `data/workshop/manifest.json`: per-file sizes and SHA256; matrix shape and row-order definition |
| How were distances and displayed percentiles built? | `config/scoring-v1.json`, `scripts/build_app_artifacts.py`, `artifacts/scoring-v1/{meta,calibration}.json` |
| Which feedback, factors and evaluation belong together? | `scripts/build_collaborative_artifacts.py`, `artifacts/collaborative-v1/{meta.json,coverage.csv,embeddings.f32}` |
| Which descriptions and encoder were used? | `content/prompts-v1.json`, `artifacts/language-v1/meta.json`, language build/verification scripts |

To trace a result, start with its recording MBID, find the authoritative `songs.json` row, follow the CLAP fingerprint into the pinned claim/vector files, and follow the same MBID into cached MusicBrainz and offset-0 AcousticBrainz records. For listener-pattern results, also check `coverage.csv` and collaborative artifact hashes. Search URLs for Spotify/YouTube are generated conveniences, not verified exact-recording sources.

### Current traceability limits

The final manifest pins derived catalogue files; it does not supply a complete checksum inventory of every raw API response. MusicBrainz and AcousticBrainz lack a uniform per-response retrieval-time ledger. The CLAP pipeline name is pinned, but a checkpoint revision/hash and complete upstream preprocessing implementation are not established by that name alone. Historical source caches may be excluded from Git or deployment and must be preserved separately for reconstruction. These are open provenance gaps, not evidence of incorrect data.

## 4. Mathematical background and implemented scoring

### Shared scoring convention

For seed set S (one to five songs), the base score is the arithmetic mean of per-seed scores:

`score(c | S) = (1 / |S|) Σ[s ∈ S] similarity(s, c)`.

Higher is better. Rhythm/texture use negative distance; CLAP/collaborative use cosine similarity. A multi-seed score is a compromise across seeds, not a learned participant profile.

### Rhythm: interpretable distance in three dimensions

Start with `x = [log2(BPM), log(1 + onset_rate), log(1 + danceability)]`. BPM estimates beat rate; onset rate summarizes event activity; danceability is an extracted descriptor, not a human preference rating.

For each dimension, use the frozen catalogue median and interquartile range:

`z_d = clip((x_d − median_d) / IQR_d, −4, 4)`.

The builder uses sorted-array quartile positions `n//4` and `3*n//4`; a near-zero IQR is replaced with 1. The score is `−(1/3) Σ[d=1..3] (z_sd − z_cd)^2`. Log transforms compress large ranges; robust scaling reduces dependence on units; clipping bounds extreme coordinates. This locally designed formula has no single original model paper to cite. Credit the underlying descriptors through AcousticBrainz and Essentia (P3–P4).

### Texture: two equally weighted feature groups

MFCCs summarize the spectral envelope through mel-spaced frequency bands, logarithmic compression and a cosine transform; see the [Essentia MFCC documentation](https://essentia.upf.edu/reference/std_MFCC.html). The app retains mean coefficients 1–12 and excludes coefficient 0. It does not recompute MFCCs from audio.

The spectral group comprises centroid (spectral center of mass), rolloff (spectral-energy boundary), flux (spectral change), and zero-crossing rate (waveform sign changes). Centroid, rolloff and flux use `log(max(value, 10^-6))`; zero-crossing rate uses `log(1 + value)`. All coordinates use the same median/IQR scaling and clipping policy as rhythm.

`similarity(s,c) = −[0.5 × MSE(MFCC_s, MFCC_c) + 0.5 × MSE(spectral_s, spectral_c)]`.

Each group contributes half the distance despite having different dimensionality. Texture is not a full model of harmony, melody, arrangement or production. Stored tonal features are not inputs to this baseline score.

### CLAP: learned audio–language geometry

CLAP trains audio and text encoders to place paired examples near one another. An illustrative one-direction contrastive objective is:

`L_audio→text = −(1/N) Σ_i log[ exp(a_i·t_i / τ) / Σ_j exp(a_i·t_j / τ) ]`.

Here unit vectors `a_i` and `t_i` represent paired audio/text and `τ` is a temperature. Training also uses the reverse direction. This explains the model family; the repository does not train CLAP or reproduce its loss. Cite the LAION method/checkpoint (P1) and, for historical context, the earlier CLAP paper (P2).

Runtime song similarity is simply `a_s·a_c`, the cosine of unit audio vectors. The repository imports the embeddings from Clapback. It does not locally acquire LAION's training corpus. LAION-Audio-630K is upstream model-training context described by P1, not a fifth directly processed external dataset here. The unfused checkpoint name should not be presented as enabling the paper's feature-fusion variant.

### Listener patterns: TF-IDF weighting and truncated SVD

Let `X_ui = 1` for a retained positive listener/song pair and 0 otherwise. Zeros enter the factorization numerically but are not labeled dislikes. For `U` listeners and item support `n_i`:

`idf_i = log(1 + U / max(n_i, 1))`.

Multiply columns of X by IDF and L2-normalize each listener row to obtain A. Then compute:

`A ≈ U_k Σ_k V_kᵀ`, with `k = 32`.

Song representations are rows of `V_k sqrt(Σ_k)`, subsequently L2-normalized. Runtime similarity is their dot product. This compresses shared preference structure while reducing the dominance of frequent items and normalizing listener activity. The builder uses [SciPy's sparse partial SVD](https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.svds.html), sorts singular values descending, and fixes random seed `20261023`.

P5 gives broader recommender-factorization background. This implementation is specifically a weighted truncated SVD, not a reproduction of biased rating factorization, SVD++, implicit ALS or a deep collaborative model. Its latent dimensions are not named genres or interpretable listener traits.

### Text retrieval and auxiliary predictions: status matters

Prepared song-to-description retrieval compares stored unit audio vectors with 200 real unit text vectors encoded offline using the paired CLAP text branch. Current metadata records `placeholder: false` and checkpoint revision `8fa0f1c6d0433df6e97c127f64b2a1d6c0dcda8a`. Free-form live text search is retired. The upstream audio checkpoint hash is not independently established by its pipeline name, so exact upstream audio/text revision equivalence is not proven. The descriptions are editorial candidates, not ground-truth song captions. See [17] and [description-matching notes](DESCRIPTION_MATCHING.md).

AcousticBrainz high-level classifiers are auxiliary pretrained models, not separately trained workshop recommenders. The compact extract retains predicted values, probabilities and class scores but does not comprehensively pin every classifier's training corpus/model revision. Use P3–P4 for platform/method context; do not claim a complete classifier-training lineage from the compact data alone.

## 5. Fair comparison, calibration, and evaluation

### Displayed match percentages

Percentages are reference percentiles, not predicted enjoyment probabilities or accuracy. Rhythm, texture and CLAP use the full frozen catalogue as reference: all non-self pairs for one seed; 512 sampled seed sets per count for two to five seeds, with random seed `20261018`. Collaborative calibration independently samples 512 seed sets for each count one through five over supported songs, with seed `20261023`. Tables use 1,001 quantile points before any collaborative tie collapse; runtime tails are capped at 99.9.

These distributions are method-specific. A 99th-percentile rhythm match and a 99th-percentile CLAP match do not establish equal quality or equal audible similarity. Filtering candidates does not refit the calibration. For a controlled comparison, hold seeds, restrictions and preferences fixed and use the shared 182-song supported pool; unsupported collaborative seeds must be flagged.

The optional ranking preference formula is `utility = percentile/100 + 0.05 × preference_fit`, using available vocal/instrumental and acoustic/electronic classifier scores, with missing information neutral. This is distinct from the guided flow's reflection-only taste survey. Preferences are a reranking policy, not retraining. The popularity baseline below is used for evaluation, not exposed as another main recommendation method.

### Recorded collaborative holdout

| Model | Hit rate @10 | NDCG @10 |
| --- | ---: | ---: |
| Collaborative SVD | 27.36% | 0.1529 |
| Training-only popularity | 23.58% | 0.1105 |

The fixed random evaluation hides one workshop love for listeners with at least three workshop loves **before fitting**, using up to five remaining loves as seeds. Targets/seeds need at least five training listeners after removal. There are 793 eligible cases and a shared 182-song candidate pool; seeds are excluded. The held-out model is fitted separately from the final model trained on all retained pairs. Results and protocol are pinned in [collaborative metadata](../artifacts/collaborative-v1/meta.json).

Hit rate measures whether the held-out target is in the first ten results. With one relevant target, NDCG contributes `1/log2(rank + 1)` when the target appears and 0 otherwise. These numbers measure reconstruction in this historical sample. They are not temporal validation, a significance claim, participant enjoyment evidence, or a comparison against rhythm/texture/CLAP. A listening pilot remains necessary.

## 6. Reproduction and preservation

From the repository root, the documented preparation sequence is:

```sh
python3 scripts/prepare_data.py all
python3 scripts/curate_data.py plan --target 1500
python3 scripts/curate_data.py features
python3 scripts/curate_data.py build --target 1500
python3 scripts/validate_data.py
python3 scripts/build_app_artifacts.py
python3 scripts/build_collaborative_artifacts.py
```

These are preparation instructions, not steps performed to author this document. Builders require their documented dependencies and cached/downloaded inputs. Re-running a live API fetch is not guaranteed to reproduce historical metadata. Preserve the entire pinned source snapshot, cached responses, frozen candidates, scripts/configuration, dependency versions and derived artifacts together. Archive a source edition before refreshing; do not combine old weekly-export files with a new manifest. The current prepared text artifact is real; preserve its recorded checkpoint revision and hashes when rebuilding.

For future editions, add raw-file checksums and retrieval timestamps, a pinned CLAP checkpoint revision and preprocessing reference, a named editor/version for manual curation, and complete encoder/tokenizer hashes alongside the existing text checkpoint revision. The existing final-data validation report supports integrity checks, not listening quality.

## 7. Works cited

Dataset/source entries D1–D4 above are the primary data citations; preserve their snapshot dates and licenses when reusing this document. Web references were checked on 24 October 2026. The pinned local manifests remain authoritative for which edition was used.

### Papers and method references

**P1 — LAION CLAP; primary neural-method citation.** Wu, Yusong, Ke Chen, Tianyu Zhang, Yuchen Hui, Marianna Nezhurina, Taylor Berg-Kirkpatrick, and Shlomo Dubnov. “Large-scale Contrastive Language-Audio Pretraining with Feature Fusion and Keyword-to-Caption Augmentation.” arXiv:2211.06687, first submitted 2022, revised 2024. [Paper](https://arxiv.org/abs/2211.06687). Cite alongside the [LAION `clap-htsat-unfused` model card](https://huggingface.co/laion/clap-htsat-unfused) and the Clapback snapshot, since a method paper alone does not identify the vectors used. The model card currently declares Apache-2.0; record the exact downloaded revision and its terms if provisioning an encoder. This is more specific than the speculative checkpoint-license language in the older setup notes.

**P2 — Earlier CLAP background.** Elizalde, Benjamin, Soham Deshmukh, Mahmoud Al Ismail, and Huaming Wang. “CLAP: Learning Audio Concepts From Natural Language Supervision.” 2022 preprint, arXiv:2206.04769. [Paper](https://arxiv.org/abs/2206.04769). Historical context for joint audio/text encoders; this is not the identity of the LAION checkpoint used here.

**P3 — AcousticBrainz dataset/platform.** Porter, Alastair, Dmitry Bogdanov, Robert Kaye, Roman Tsukanov, and Xavier Serra. “AcousticBrainz: A Community Platform for Gathering Music Information Obtained from Audio.” *Proceedings of the 16th International Society for Music Information Retrieval Conference*, 2015, pp. 786–792. [Author-institution paper](https://www.upf.edu/documents/223346843/0/porter2015acousticbrainz.pdf/b07e89e6-6cf1-89ea-47e0-4dabf81b2978).

**P4 — Descriptor extraction library.** Bogdanov, Dmitry, Nicolas Wack, Emilia Gómez, Sankalp Gulati, Perfecto Herrera, Oscar Mayor, Gerard Roma, Justin Salamon, José R. Zapata, and Xavier Serra. “Essentia: An Audio Analysis Library for Music Information Retrieval.” *Proceedings of the 14th International Society for Music Information Retrieval Conference*, 2013, pp. 493–498. [Author-institution publication record](https://mtg.upf.edu/node/2793). Supports the upstream extractor, not a claim that this repository reruns it.

**P5 — Collaborative-factorization background.** Koren, Yehuda, Robert Bell, and Chris Volinsky. “Matrix Factorization Techniques for Recommender Systems.” *Computer* 42(8), 2009, pp. 30–37. [DOI: 10.1109/MC.2009.263](https://doi.org/10.1109/MC.2009.263). Cite as background; use the local build script for the exact weighted-SVD specification.

### Reuse and attribution statement

This workshop combines Clapback embeddings and identity claims (CC0), MusicBrainz core metadata (CC0) and supplementary tags (CC BY-NC-SA 3.0), AcousticBrainz descriptors/predictions (CC0), and a ListenBrainz feedback sample (CC0). Catalogue selection, broad style families, familiarity bands, distance formulas and local factor-model fitting are workshop modifications. Preserve source-specific attribution and terms; do not assign one blanket CC0 label to the complete collection. Data licenses do not grant rights to underlying recordings, which the preparation workflow does not download or distribute. Model/checkpoint terms are separate from dataset terms. The existing [distributed attribution file](../data/workshop/ATTRIBUTION.md) remains part of the data release.
