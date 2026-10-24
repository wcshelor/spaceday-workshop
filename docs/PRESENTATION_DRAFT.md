# How the Workshop Recommenders Work

*A presentation draft and intuition-building study guide. Prepared 24 October 2026.*

For the short opening, use the [seven-slide introduction with numbered research and data citations](INTRO_SLIDES.md). Its references resolve to the [running numbered bibliography](WORKS_CITED_AND_METHODS.md#numbered-bibliography-for-presentations).

## How to use this guide

Read the speaker notes straight through for preparation. Each numbered section can become a slide, with **On screen** as the short slide copy and **Speaker notes** as the explanation. All invented song names, vectors and listener tables are teaching examples, not results from the actual catalogue. Actual project counts and formulas follow [Works Cited and Methods](WORKS_CITED_AND_METHODS.md), which contains provenance and paper references.

For a 45-minute workshop, use this pacing as a menu rather than reading every note aloud:

| Minutes | Topic |
| --- | --- |
| 0–5 | Industry context, then sections 1–2: similarity and the pipeline |
| 5–12 | Sections 3–5: rhythm and texture |
| 12–19 | Sections 6–7: CLAP and language |
| 19–26 | Sections 8–9: listener patterns |
| 26–36 | Sections 10–12: prediction, listening and comparison |
| 36–40 | Section 13: evaluation |
| 40–45 | Selected quiz questions and discussion |

The full notes and quiz bank support a longer preparation session. The mathematics appendix is optional presenter background.

## Learning goals

After reading, you should be able to explain what information each method sees, how it turns that information into a ranking, why methods disagree, and what a score can establish. You should also be able to distinguish model training from recommendation-time scoring and identify an unfair comparison.

## Industry context: how Spotify and Apple Music recommend music

**On screen**

- Spotify combines listener behaviour, patterns across listeners, content information, context and editorial curation.
- Apple Music uses listening history, play duration, library additions, favourites and other activity to personalise recommendations.
- Large services combine many signals. Our workshop separates a few building blocks so we can understand them.

**Speaker notes**

Start with a familiar question: “How does your music app decide what to play next?” Spotify and Apple Music have substantial data and engineering resources, allowing them to build personalised experiences around individual listeners. Their public descriptions provide useful clues, but neither source below gives a complete recipe for its current recommendation systems.

Spotify describes recommendations informed by a listener's behaviour, the behaviour of other listeners, information about the content and listening context. Human editors also shape recommendations. Different surfaces, such as Home, Search and playlists, can involve different approaches. This is broader than finding a song with a similar tempo. See [Spotify: Understanding recommendations](https://www.spotify.com/uk/safetyandprivacy/understanding-recommendations).

Apple confirms that it uses information including what you play, how long you play it, what you add to your library or playlists, and what you favourite or share to customise your experience. Its engineering description also confirms large-scale offline pipelines, model training and real-time personalised services. These sources establish the signals and engineering involved, but do not identify the exact recommendation algorithms or their weights. See [Apple Music & Privacy](https://www.apple.com/legal/privacy/data/en/apple-music/) and [Apple: Music Recommendation Engine engineering role](https://jobs.apple.com/en-il/details/200656273-2114/senior-machine-learning-engineer-music-recommendation-engine?team=SFTWR).

The teaching connection is that a useful recommendation can draw on several kinds of evidence: what a listener has enjoyed, what other listeners associate with it, and information about the music. Our rhythm, texture, CLAP and listener-pattern methods let us explore distinct kinds of evidence separately. They illustrate recommendation building blocks; they do not reproduce Spotify or Apple Music, and these public sources do not establish that either company uses our particular formulas or CLAP model.

**Opening prompt:** “If your app recommends a song you enjoy, what clues might have helped it choose?”

**Transition:** “The large services combine many clues. Let's explore some simpler methods one at a time: what does each notice, and what does it miss?”

*Source descriptions checked 24 October 2026; deployed systems can change.*

## 1. Musical similarity has several meanings

**On screen**

- Similar pulse and activity
- Similar timbre and spectral properties
- Similar learned sound representation
- Similar listener preferences

**Speaker notes**

Imagine recommending something after a quiet acoustic song. You could choose another recording with a similar tempo, another with a similarly soft sound, or a very different song loved by the same people. Each recommendation answers a different question.

Our app makes these choices visible through four methods: rhythm, texture, CLAP sound and listener patterns. “Similar” always depends on a representation and a comparison rule. A representation is the information about a song that a method keeps. The comparison rule decides what counts as close within that information.

Similarity and enjoyment also differ. You might hear a close match and dislike it, or enjoy an unexpected recommendation that sounds quite different. Ask participants about these reactions separately.

**Opening prompt:** “Think of two songs you associate with one another. Is the connection in their sound, their audience, a memory, or something else?”

**Transition:** “To understand a recommendation, we first need to know what information the method receives.”

## 2. What happens before and during the workshop

**On screen**

| Before the workshop | When someone requests recommendations |
| --- | --- |
| Collect metadata and existing audio representations | Select one to five seed songs |
| Curate the catalogue and prepare feature scales | Choose a method and eligible candidates |
| Fit the listener model | Score, rank and display results |
| Store versioned artifacts | Listen and record reactions |

**Speaker notes**

MusicBrainz provides recording identities and metadata. AcousticBrainz provides already extracted measurements and classifier predictions. Clapback supplies already computed CLAP audio vectors. ListenBrainz supplies explicit song loves for the locally fitted listener model.

The app's frozen catalogue has 1,500 recordings. We do not download audio or run an audio encoder when someone clicks a song. For most methods, the expensive audio analysis happened upstream. Our listener model learns offline from the feedback sample. At recommendation time, the app compares stored representations.

Participant reactions do not update the shipped models. Choosing a different seed changes the query. It does not retrain a neural network or refit the listener model.

Metadata also affects which songs enter the catalogue and which candidates filters allow. That influence differs from being a coordinate in the similarity formula. For example, a MusicBrainz genre tag can shape curation without directly contributing to CLAP cosine similarity.

**Check:** “If I give a recommendation a low enjoyment score, has the model learned my taste?” Pause before answering: the shipped models do not train on these reactions.

## 3. Rhythm: a musical measuring tape

**On screen**

Rhythm compares three measurements:

- BPM: estimated beat rate
- Onset rate: frequency of detected sound events
- Danceability: an extracted rhythm descriptor

**Speaker notes**

Picture a song as a point whose coordinates describe beat rate, event activity and danceability. The rhythm method recommends nearby points. It can tell that two recordings have similar measured rhythmic properties even when their instruments, lyrics and audiences differ.

BPM and onset rate have different roles. A slow beat can support many quick notes. A sparse song can have the same BPM as a busy arrangement. Keeping both measurements gives us more information than tempo alone.

Danceability is an algorithmic descriptor. It does not establish whether a participant wants to dance or enjoys the song. Tempo estimates can also have half-time or double-time ambiguity. Our formula does not explicitly search for equivalence between 70 and 140 BPM.

**Prediction prompt:** “A dance track and a guitar recording both have a steady, busy rhythm. Could rhythm recommend one from the other?” Yes, if the selected measurements are close. Their genre difference does not automatically prevent that.

## 4. Distance depends on the ruler

**On screen**

1. Transform each measurement
2. Put measurements on comparable scales
3. Square the differences and average them

Smaller distance gives a higher recommendation score.

**Speaker notes**

Raw units create a problem. A tempo difference of 20 and a descriptor difference of 0.2 cannot sensibly compete just because one number is larger. Our preparation first transforms the measurements, then scales each coordinate using the catalogue median and interquartile range, or IQR. IQR measures the spread of the middle half of the values.

BPM uses a base-two logarithm. Doubling from 60 to 120 BPM has the same transformed difference as doubling from 90 to 180. This treats proportional changes consistently, but it does not make a doubled tempo identical. The other rhythm measurements use log(1 + value), which compresses large values and handles zero.

After scaling, the method clips each coordinate to the range −4 to 4. Then it squares coordinate differences and averages them. Squaring gives a large mismatch more influence than a small one. We negate the distance so that all methods can follow the same display convention: higher score ranks first.

**Worked teaching example:** Suppose the seed's scaled rhythm vector is `[0, 0, 0]`. Candidate A is `[1, 0, 0]` and B is `[0.5, 0.5, 0.5]`.

- A has mean squared distance `(1 + 0 + 0)/3 = 0.333`.
- B has mean squared distance `(0.25 + 0.25 + 0.25)/3 = 0.25`.
- B ranks higher, despite differing on every coordinate.

This illustrates a design choice: several modest differences can cost less than one larger difference. The formula reflects our chosen ruler rather than a universal law of musical perception.

## 5. Texture: the sound's material

**On screen**

Texture gives equal total weight to:

- 12 MFCC means that summarize spectral shape
- Four spectral measurements

**Speaker notes**

Think about the difference between a flute and a distorted guitar playing a similar note. Timbre helps us distinguish their sound qualities. Texture tries to capture aspects of this through summary statistics.

MFCC stands for mel-frequency cepstral coefficient. The intuition is easier than the name: summarize how sound energy distributes across perceptually spaced frequency bands, compress the range, then express the resulting shape with a compact list of numbers. Our model uses mean coefficients 1–12 and leaves out coefficient 0. Individual coefficients do not correspond neatly to “guitar,” “warmth” or “happiness.”

The other group includes spectral centroid, rolloff, flux and zero-crossing rate. Roughly, these describe where spectral energy sits, how far it extends, how it changes, and how often the waveform changes sign. These descriptions suggest listening hypotheses, but they do not establish a unique perceptual cause.

We scale the coordinates and compute mean squared distance within each group. Each group gets 50% of the total distance. Giving every coordinate equal weight instead would give the 12-dimensional MFCC group 75% of the weight because it has more coordinates.

These features summarize whole recordings. A track with a quiet opening and loud ending can resemble a consistently moderate track in some averages. The representation loses the ordering of events. The texture score also does not compare the stored key or chord features.

**Check:** “Could two tracks score close on texture and have different melodies?” Yes. The chosen summaries do not uniquely describe melody.

## 6. CLAP: learning a map from audio and descriptions

**On screen**

CLAP learns from paired audio and text.

The workshop compares stored 512-dimensional audio vectors.

Nearby directions indicate similarity in that learned representation.

**Speaker notes**

Imagine a map where locations reflect recurring relationships between sounds and descriptions. During pretraining, an audio encoder turns a clip into a vector and a text encoder turns its description into another vector. The training objective encourages paired examples to align and distinguishes them from other pairings in the training batch. This is contrastive learning.

The resulting coordinates reflect learned patterns. They are not 512 labeled musical attributes. You cannot generally read coordinate 17 as “amount of piano.” Learned representations can capture richer combinations than our small hand-designed formulas, but the training data and objective also influence what they emphasize.

Our app imports vectors from the LAION CLAP pipeline via Clapback. It does not train CLAP on the workshop catalogue. Audio-to-audio recommendation compares two stored audio vectors, even though paired audio/text training helped create the representation.

The vectors have length approximately one. Their dot product therefore expresses cosine similarity: how closely their directions align. A two-dimensional analogy is arrows on a circle. Two arrows pointing in the same direction score 1, perpendicular arrows score 0, and opposite arrows score −1. In 512 dimensions we use the same comparison rule without being able to draw the full space.

A high CLAP score supports the statement “these audio representations are close.” It does not, by itself, justify “the system chose this because of the guitar.” Listening can suggest an explanation, but the embedding score does not prove it.

**Background reading:** LAION CLAP is P1 in the [methods reference](WORKS_CITED_AND_METHODS.md). P2 gives earlier CLAP context.

## 7. Language retrieval: a second entrance to the same space

**On screen**

CLAP's paired text encoder places descriptions in the audio representation space.

The workshop uses 200 real prepared text vectors; live free-form text search is retired.

**Speaker notes**

We curated 200 candidate descriptions and encoded them offline with the paired CLAP text branch. At runtime, the app compares these stored text vectors with stored audio vectors. Participants can judge Fits/Partly/Misses and explore categories without running or training an encoder. Current metadata records `placeholder: false` and the text checkpoint revision. Descriptions are editorial candidates, not verified annotations of songs.

The shared pipeline identifies a model family; it does not independently establish the exact checkpoint hash used for upstream audio vectors. Compatible dimensions alone do not prove compatible representations. Real embeddings can also produce biased or misleading matches, so plausible results need listening-based scrutiny. See [description-matching and curation notes](DESCRIPTION_MATCHING.md), and numbered sources [8], [9], [12] and [17] in the [works cited](WORKS_CITED_AND_METHODS.md#numbered-bibliography-for-presentations).

**Check:** “Does a high-ranked description prove the recording contains that instrument?” No: a similarity score is evidence of representation alignment, not verified instrumentation.

## 8. Listener patterns: connections through people

**On screen**

Listener patterns learns from explicit song loves.

It can connect recordings that sound different.

The deployed model supports 182 of the 1,500 catalogue songs.

**Speaker notes**

Imagine a table with listeners as rows and songs as columns. A 1 records an explicit love. A blank means we do not have that positive signal. A blank could reflect unfamiliarity, missing feedback or many other situations. It does not tell us the listener disliked the song.

Here is a deliberately tiny teaching table before weighting or factorization:

| Listener | Acoustic A | Dance B | Acoustic C |
| --- | ---: | ---: | ---: |
| Listener 1 | 1 | 1 | 0 |
| Listener 2 | 1 | 1 | 0 |
| Listener 3 | 0 | 0 | 1 |
| Listener 4 | 0 | 0 | 1 |

A and B share a preference pattern despite their different imagined sounds. C's acoustic label alone gives the listener model no reason to connect it to A. This example illustrates the signal, not the actual model's filtering or output.

The real model uses a historical ListenBrainz sample of explicit loves. After support filtering, it trains on 2,516 listeners, 10,082 songs and 152,036 positive pairs. Training on songs outside the workshop catalogue supplies additional context. Only 182 catalogue songs have retained factors, so support is a major practical constraint.

The app compares song representations learned from this table. It does not need to identify the participant as an existing ListenBrainz listener, and it does not search for a named “person just like you” during the request.

## 9. SVD: compressing a large preference table

**On screen**

- Weight common and less common items differently
- Normalize listener rows
- Keep 32 broad mathematical patterns
- Compare song directions in that smaller space

**Speaker notes**

A very common song tells us less about a particular preference grouping than a more distinctive shared favorite. Our IDF weighting gives songs with lower support larger multipliers. Row normalization then makes each listener's weighted row have unit length. This changes the influence of activity levels, though it does not remove all popularity or sampling effects.

Singular value decomposition, or SVD, approximates the weighted table using a limited number of patterns. A useful analogy is summarizing many overlapping shopping lists with a smaller set of recurring combinations. These combinations can describe associations spread across many items without requiring every pair to have identical users.

The implementation keeps 32 factors. It takes the song-side singular vectors, scales them by the square roots of the corresponding singular values, then normalizes each song vector. The resulting dot product compares directions, just as CLAP does. However, the coordinates come from feedback rather than audio/text pretraining. Using the same comparison operation does not make the models equivalent.

The factors are mathematical directions, not 32 human-readable listener types. More dimensions would allow a richer approximation but could also preserve noise. The repo does not establish 32 as the optimal choice through a dimension-search study.

**Cold start:** A new song can have perfectly usable audio while having too little feedback for this model. In this app it needs a retained collaborative factor before listener-pattern ranking can use it. CLAP can compare a new recording once a compatible vector exists, but the current app still needs that vector prepared and admitted to its catalogue.

**Background reading:** P5 in the [methods reference](WORKS_CITED_AND_METHODS.md) introduces recommender factorization. Our exact implementation is weighted truncated SVD.

## 10. Why the methods disagree

**On screen**

| Hypothetical candidate | Why it might rank well |
| --- | --- |
| Similar tempo, different instruments | Rhythm measurements are close |
| Similar timbre, different tempo | Texture measurements are close |
| Similar learned audio representation | CLAP directions align |
| Different sound, shared preferences | Listener factors align |

**Speaker notes**

Suppose the seed is a busy electronic track. Rhythm might retrieve something with similar pulse and event activity. Texture might favor a similar spectral character. CLAP might find a broader relationship in its learned representation. Listener patterns might surface a quieter track associated with the same audience.

These are hypotheses to test by listening, not guaranteed outputs or exclusive capabilities. CLAP may reflect rhythm, and texture can correlate with genre. Listener communities may form around shared sounds. The methods overlap because music and listening behavior overlap.

A revealing result is one where the methods separate. Ask which information could explain that separation. Avoid immediately declaring a winner. First establish the task: finding a similar sound, sustaining a mood, discovering something enjoyable, or understanding a community's preferences.

**Discussion:** “If the listener model recommends a song you love but hear as very different, did it fail?” A useful answer specifies the objective before judging the result.

## 11. Several seeds create a compromise

**On screen**

The app averages each candidate's similarity to the selected seeds.

Adding a seed changes the question.

**Speaker notes**

The implementation permits one to five seed songs. Each seed contributes equally to the base score. Here are invented similarity scores:

| Candidate | Similarity to seed A | Similarity to seed B | Average |
| --- | ---: | ---: | ---: |
| X | 0.9 | 0.1 | 0.5 |
| Y | 0.6 | 0.6 | 0.6 |

Y wins because it provides a better compromise, even though X is the strongest match to A. This calculation does not train a participant model. With cosine methods, averaging per-seed scores equals comparing each candidate against the arithmetic mean of seed vectors. That mean can have length below one. The implemented score does not normalize it into a new unit seed.

Widely separated seeds can weaken a clear direction. Adding more favorites can be useful, but it does not guarantee that every recommendation becomes better. For a teaching comparison, a single active seed makes differences easier to reason about.

## 12. A fair listening comparison

**On screen**

Keep the seed, candidate pool and restrictions fixed.

Record enjoyment and audible similarity separately.

**Speaker notes**

If CLAP searches 1,500 songs while listener patterns searches 182, different results reflect both the representation and the available choices. The guided comparison uses the shared supported pool when the listener model is available. This controls availability, but it also narrows the experiment to songs with sufficient feedback in this sample.

Keep the active seed and filters unchanged. Keep ranking preferences unchanged too, or leave them off for the clearest first comparison. The optional reflection survey in the guided flow does not itself change rankings. A separate optional preference mechanism can rerank results using classifier scores.

A short activity:

1. Choose a supported seed and predict which method will give the closest audible match.
2. Take a recommendation from two methods with the same candidate restrictions.
3. Listen, remembering that external search links may lead to another version.
4. Record enjoyment and perceived similarity separately, then describe what you heard.
5. Reveal the method information and revisit the prediction.

Listen before explanation when practical. A label such as “similar texture” can influence what someone attends to. Two example results can spark discussion but cannot establish general superiority.

## 13. Scores and evidence

**On screen**

A match percentage is a reference percentile.

Recorded evaluation: collaborative SVD hit rate @10 = 27.36%.

Both numbers need their reference conditions.

**Speaker notes**

A high match percentile means a score sits high in that method's prepared reference distribution for the relevant seed count. It does not mean a corresponding chance of enjoyment. Different methods have different score distributions and references. Equal displayed percentages do not establish equal quality.

The offline collaborative evaluation removes one known workshop love for each eligible listener before fitting the evaluation model. It uses up to five remaining workshop loves as seeds and asks whether the hidden song appears in the top ten. Both SVD and a training-only popularity baseline rank the same eligible songs and exclude seeds.

Across 793 eligible cases, SVD has a hit rate @10 of 27.36%, versus 23.58% for popularity. That is an observed difference of 3.78 percentage points. NDCG @10 also rewards placing the hidden song nearer the top: 0.1529 for SVD versus 0.1105 for popularity.

This is a fixed random holdout on historical positive feedback. It supports a limited reconstruction result for this protocol. It does not establish statistical significance, future participant enjoyment, or superiority over CLAP, rhythm or texture. The held-out model differs from the shipped final model, which fits all retained positive pairs.

**Check:** “Why remove the target before fitting?” Otherwise the training matrix already contains the positive interaction the test asks us to recover.

## 14. Presenter recap

**On screen**

| Method | Information it uses | How it defines closeness |
| --- | --- | --- |
| Rhythm | Selected rhythmic measurements | Negative mean squared distance |
| Texture | Selected timbral/spectral summaries | Negative weighted group distance |
| CLAP | Pretrained audio representations | Cosine similarity |
| Listener patterns | Factors learned from explicit loves | Cosine similarity |

**Speaker notes**

Every method retains some information and leaves other information out. Our designed feature formulas make the ruler visible. CLAP learns a richer representation upstream. Listener patterns learns associations through feedback. A recommendation becomes easier to interpret when we can name its evidence and its comparison rule.

Close by asking participants to explain one recommendation in their own words, then identify what evidence they would need before trusting a stronger claim about it.

## Quiz bank

Use questions 1, 3, 6, 9 and 12 for a quick group quiz. Use the full set for presenter preparation. Answers and explanations follow in a separate section so you can test yourself first.

### Recall and intuition

**1. Different similarity signals**

Two songs have similar tempo and onset activity but very different instrumentation. Which method most directly compares the stated evidence?

A. Rhythm  
B. Texture  
C. Listener patterns  
D. All methods must rank them equally

**2. Units and scaling**

Why transform and scale rhythm features before computing distance? Explain what could happen if raw numerical ranges determined the result.

**3. Texture weights**

Texture has 12 MFCC coordinates and four spectral coordinates. How much total weight does each group receive?

A. 75% MFCC and 25% spectral  
B. 50% each  
C. 25% MFCC and 75% spectral  
D. The weights change with every seed

**4. Features left out**

True or false: because `features.json` contains key and chord information, texture similarity directly compares those attributes. Explain.

**5. Learned dimensions**

A participant asks which CLAP coordinate represents “sadness.” What should you explain about learned dimensions?

**6. Deterministic placeholders**

A prepared text query repeatedly returns the same plausible-looking song. Does that prove that the paired CLAP text encoder is working? What would you inspect?

### Comparison and diagnosis

**7. Shared scoring operation**

Both CLAP and listener patterns use cosine similarity. Give two reasons why they can recommend different songs.

**8. Missing feedback**

A listener has no recorded love for a song. Which conclusion is justified?

A. They disliked it  
B. They never heard it  
C. The dataset lacks that positive signal  
D. Its audio vector is invalid

**9. Cold start**

A new song has a compatible CLAP vector but no listener feedback. Which method can use the vector, and what prevents the current collaborative method from doing the same?

**10. Several seeds**

X scores 0.9 and 0.1 against two seeds. Y scores 0.6 and 0.6. Which candidate ranks higher under the app's unmodified base-score average? Show the arithmetic.

**11. Fair comparison**

A presenter compares rhythm on 1,500 candidates with collaborative ranking on 182 candidates, then credits all differences to the algorithms. What is confounded, and how should the demonstration change?

**12. Percentiles**

CLAP and rhythm both display 99% for different recommendations. Which claim is justified?

A. Both songs have a 99% chance of enjoyment  
B. Both methods have 99% accuracy  
C. Both scores sit high in their respective reference distributions  
D. Both recordings must sound equally similar

### Reasoning and calculation

**13. Squared distance**

A seed has scaled rhythm vector `[0,0,0]`. A is `[1,0,0]`. B is `[0.5,0.5,0.5]`. Which has the better rhythm score? Why does “matching more coordinates exactly” fail as a shortcut?

**14. Meaning of a listener match**

A listener-pattern recommendation sounds different but the participant enjoys it. Give a plausible interpretation and identify one conclusion the result cannot establish.

**15. Evaluation leakage**

Why would fitting the SVD model before removing held-out loves weaken the evaluation?

**16. Reading the benchmark**

The recorded hit rates are 27.36% for SVD and 23.58% for popularity. State the difference in percentage points. Can this benchmark tell us that SVD beats CLAP or that most workshop participants will prefer it?

**17. Lost temporal structure**

Invent two recordings that could have similar whole-recording summary features but different musical development. What information would a time-aware representation need to preserve?

**18. Explanations**

A facilitator says, “CLAP recommended this because the guitars match.” How could you phrase the observation more accurately without losing its usefulness for discussion?

**19. Training or querying?**

Classify each action: changing a seed, recording an enjoyment reaction, fitting SVD from feedback, and running a paired text encoder on a query. Which changes the learned model parameters in this workflow?

**20. Objective before winner**

Design a comparison for either “closest audible rhythm” or “most enjoyable discovery.” Specify the outcome you would ask participants to rate, the controls you would hold fixed, and why one example per method would be insufficient for a broad claim.

## Answer key and teaching notes

**1. A.** Rhythm directly compares the named rhythmic measurements. Other methods may also retrieve the pair, but the information given cannot establish their rankings.

**2.** Units and numerical ranges can otherwise dominate distance. Transforms compress ranges, while median/IQR scaling makes deviations more comparable. Scaling encodes a choice of ruler and does not guarantee alignment with perception.

**3. B.** The method averages distance within each group, then assigns each group 50%. Equal weighting of all 16 coordinates would instead give the MFCC group 75%.

**4. False.** The texture formula uses MFCC means and four spectral measures. Availability in a stored feature record does not imply use in a particular score.

**5.** Coordinates form a learned representation. Meaning can spread across combinations of dimensions, and individual dimensions need not have stable everyday labels. A high similarity score does not identify a causal musical attribute.

**6. No.** Deterministic synthetic vectors can reproduce rankings. Inspect language metadata, encoder/tokenizer identity, verification results and whether the bank contains real encoded prompts. Current metadata records real prepared vectors; deterministic placeholders remain a useful hypothetical counterexample. Plausible anecdotes cannot substitute for checking the pipeline.

**7.** The vectors come from different signals and training procedures: upstream audio/text learning versus local listener feedback factorization. Their supported candidate pools also differ unless controlled. Equal dimensionality or the same comparison function would not equate their geometries.

**8. C.** Missing positive feedback leaves exposure and preference unresolved. Although zeros enter the matrix numerically, they are not observed dislike labels.

**9.** CLAP can compare a compatible audio vector once the song is available to the app. The current collaborative model needs a supported factor learned from feedback. Its coverage rules and frozen artifact prevent using an arbitrary new song directly.

**10. Y.** X averages to 0.5 and Y to 0.6. The app rewards average similarity across the chosen seeds, rather than taking the single best seed match.

**11.** Candidate availability and representation both change. Use the same supported candidate pool, seed, filters and ranking preferences to isolate method differences more clearly. Note that the smaller shared pool limits the scope of the experiment.

**12. C.** Each score has a method-specific reference distribution. The percentages establish neither enjoyment probabilities nor equal perceptual closeness.

**13. B.** A has distance 1/3 and score −1/3. B has distance 1/4 and score −1/4. Since −1/4 is higher, B wins. Squared magnitude matters, not just how many coordinates differ.

**14.** Shared historical preferences may connect the recordings even when they sound different. This single reaction cannot establish why the model formed the association or that it predicts participant enjoyment reliably.

**15.** The model would see the positive pair that the evaluation later treats as unknown. Removing it before fitting makes the reconstruction task more meaningful. The implemented evaluation still has the limits of a fixed random split.

**16.** The difference is 3.78 percentage points. The benchmark compares SVD with popularity under one holdout protocol. It includes neither a CLAP comparison nor participant preference measurements, and it makes no significance claim.

**17.** One example is a recording that alternates sparse and dense passages versus one that maintains intermediate activity. Some averages could coincide. A time-aware representation would need features tied to positions or segments, with information about their sequence. This example is conceptual, not an observed catalogue pair.

**18.** “I hear a guitar resemblance, and these recordings are close in CLAP space. The score alone does not show that guitars caused the ranking.” This separates the listening observation from the model evidence.

**19.** Changing a seed changes the query. Recording enjoyment stores a reaction without retraining. Fitting SVD changes the learned factor model. Running the text encoder performs inference with fixed parameters, when performed offline to build the prepared bank. Upstream CLAP pretraining changes parameters, but our workshop does not perform it.

**20.** A strong answer defines a relevant rating, such as perceived rhythmic resemblance or enjoyment of an unfamiliar recommendation. It holds seed and candidate eligibility fixed, controls preferences and listening conditions, and gathers several trials across songs and participants. Method order can be varied to reduce order effects. One example can illustrate a mechanism but is too sensitive to song choice for a broad ranking of methods.

## Optional mathematics notes for the presenter

### Robust scaling

`z = clip((transform(x) − median) / IQR, −4, 4)`

The median and IQR come from the frozen catalogue, not each new candidate filter. Near-zero IQR uses 1 as a fallback. Clipping limits a coordinate's range but can also make different extreme values identical after clipping.

### Cosine similarity

`cosine(a,b) = (a·b) / (||a|| ||b||)`

For unit vectors, this becomes `a·b`. Normalizing removes vector magnitude from pairwise comparison. The direction's meaning depends on how the representation was produced.

### Collaborative weighting and factors

`idf_i = log(1 + number_of_listeners / max(item_support_i, 1))`

Multiply each song column by its IDF weight, then normalize listener rows. Approximate the resulting matrix A with `A ≈ U_k Σ_k V_kᵀ`. Song vectors are normalized rows of `V_k sqrt(Σ_k)`, with 32 retained factors in this edition. This is a truncated-SVD construction rather than implicit alternating least squares or a neural recommender.

### Multi-seed geometry

For unit song vectors, the implemented mean cosine score is:

`score(c) = c · [(s_1 + ... + s_m)/m]`.

The seed mean generally has length below one. Normalizing that mean would preserve candidate order for a nonzero mean within the same fixed seed set, but change score magnitudes and their calibration. For feature methods, the average squared distance equals squared distance to the seed mean plus a candidate-independent seed-spread term. Thus their ranking also has a centroid interpretation, with the chosen scaling and group weights retained.

### Hit rate and NDCG

With one held-out target, hit rate @10 averages a 1 when the target appears in the first ten and 0 otherwise. NDCG @10 contributes `1/log2(rank + 1)` if it appears, where rank starts at 1, and 0 otherwise. Both metrics answer a specific retrieval question. Neither directly measures enjoyment.

## Presenter vocabulary

| Term | Plain explanation |
| --- | --- |
| Seed | A selected starting song |
| Candidate pool | Songs eligible to appear in this request |
| Feature | A measured or derived property used to represent a song |
| Embedding | A vector whose geometry provides a useful representation |
| Encoder | A model that turns input into a representation |
| Training | Fitting model parameters from data |
| Inference | Using a fitted model on an input |
| Cosine similarity | Alignment between vector directions |
| SVD | A matrix decomposition used here to retain a smaller set of patterns |
| Cold start | Insufficient relevant history to represent a new item or person |
| Percentile | Position relative to a specified reference distribution |
| Leakage | Test information entering model preparation in a way that undermines the intended test |

## Sources and further reading

The companion [Works Cited and Methods](WORKS_CITED_AND_METHODS.md) provides dataset editions, transformations, exact implementation references and the bibliography. For further preparation, start with its P1 for LAION CLAP, P3–P4 for AcousticBrainz/Essentia, and P5 for recommender factorization. The exact project formulas and coverage always take precedence over broad analogies in this teaching draft.

[Workshop runbook](WORKSHOP_RUNBOOK.md) covers facilitation. [Language model setup](MODEL_SETUP.md) documents the encoder blocker. [Collaborative model notes](../artifacts/collaborative-v1/README.md) give training coverage and evaluation details.
