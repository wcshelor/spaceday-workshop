# How Does a Music App Choose Your Next Song?

Seven slides · approximately 6 minutes 30 seconds. Numbered sources link to the [running works cited document](WORKS_CITED_AND_METHODS.md#numbered-bibliography-for-presentations). Research footers contain one or two readings; separate data credits identify our actual inputs. Readings are optional follow-up, not material to read aloud.

## Slide 1 — What should play next?

**45 seconds · On screen**

- Millions of songs. One next choice.
- Something familiar—or something surprising?
- Similar music doesn't always mean music you enjoy.

**Say:** “Imagine you've just finished a favourite song. What should come next? Something with the same beat? The same mood? Something completely different that you might love? Music recommendation means choosing among an enormous number of possibilities—and deciding what makes a recommendation good.”

**Research footer:** [1](WORKS_CITED_AND_METHODS.md#ref-1), [2](WORKS_CITED_AND_METHODS.md#ref-2). Recent content-driven review plus foundational challenges/evaluation review; these are not a claim to exhaustively cover the latest research.

## Slide 2 — Three approaches we'll explore

**45 seconds · On screen**

- **Musical features:** Do songs share measurable properties?
- **Listener patterns:** Do people enjoy them together?
- **Learned audio representations:** Has a model learned a connection between their sounds?

**Say:** “We can compare properties of music, learn from listening preferences, or use models that learn richer representations of sound. Each sees different evidence, so each can suggest a different next song. These approaches overlap: learned audio representations are also content-based, and larger systems can combine them.”

**Research footer:** [3](WORKS_CITED_AND_METHODS.md#ref-3), [1](WORKS_CITED_AND_METHODS.md#ref-1).

## Slide 3 — How the big services approach it

**60 seconds · On screen**

- **Spotify:** Discover Weekly (discovery), Release Radar (new releases), Spotify Mixes (familiar songs + recommendations).
- **Apple Music:** Discovery Station (unheard music) and Made for You mixes (favourites + discoveries).
- Personalised services draw on many clues.

**Say:** “You may already use recommendations through Spotify's Discover Weekly, Release Radar or Mixes, or Apple Music's Discovery Station and Made for You mixes. They serve different goals: discovery, new releases, or a blend of familiar and unfamiliar music. Spotify publicly describes using your behaviour, other listeners' behaviour, content information, context and editorial curation. Apple confirms using listening activity, play duration, favourites and library additions. These sources disclose selected inputs rather than a complete current pipeline. We shouldn't assume both companies use the same algorithms, or that either uses our particular models. We'll separate a few understandable building blocks and investigate what each contributes.”

**Source footer:** Spotify [18](WORKS_CITED_AND_METHODS.md#ref-18); Apple [5](WORKS_CITED_AND_METHODS.md#ref-5). Feature examples: [21](WORKS_CITED_AND_METHODS.md#ref-21)–[23](WORKS_CITED_AND_METHODS.md#ref-23). These are first-party disclosures, not research papers.

**Presenter background:** Spotify's historical Home architecture [4](WORKS_CITED_AND_METHODS.md#ref-4) describes candidate generation followed by ranking and multiple models. Avoid presenting a 2021 description as the complete current service. No blanket claim that the algorithms are “secret” is established by these references.

## Slide 4 — Part 1: Describe the music with measurements

**60 seconds · On screen**

- **Rhythm:** tempo, activity and danceability.
- **Texture:** summaries of tone and spectrum.
- **Our data:** 1,500 recordings, selected across decades and styles; existing AcousticBrainz measurements.

**Say:** “We'll start with explicit measurements. Rhythm compares tempo and activity; texture compares the sound's character. We curated 1,500 recordings using MusicBrainz metadata and available audio data, balancing decades, broad styles and estimated familiarity while limiting repeated artists. We reused AcousticBrainz measurements rather than analysing audio ourselves. Choose a familiar song, predict what a method will preserve, then listen. This shows how choosing measurements changes the meaning of similarity.”

**Research footer:** review [1](WORKS_CITED_AND_METHODS.md#ref-1); audio-data platform paper [10](WORKS_CITED_AND_METHODS.md#ref-10).

**Data credits:** MusicBrainz [13](WORKS_CITED_AND_METHODS.md#ref-13), AcousticBrainz [14](WORKS_CITED_AND_METHODS.md#ref-14), local selection audit [16](WORKS_CITED_AND_METHODS.md#ref-16). Familiarity bands are editorial estimates. The exact distance formulas are locally designed, not reproduced from the review.

## Slide 5 — Part 2: Learn from listeners

**60 seconds · On screen**

- A small model learns patterns in real song favourites.
- Shared audiences can connect different sounds.
- **Our data:** filtered ListenBrainz loves; 2,516 listeners; 182 supported catalogue songs.

**Say:** “Next, we'll use a model that hasn't heard the audio. We took a historical ListenBrainz feedback sample, kept positive favourites, removed duplicate listener–song pairs and filtered for sufficient listener and song support. The resulting training data cover 2,516 listeners and about 10,000 songs, including songs outside our catalogue. Only 182 catalogue songs have supported model representations. This introduces collaborative filtering—and shows why sparse data limits what a model can recommend. Your workshop reactions won't retrain it.”

**Research footer:** collaborative-filtering review [7](WORKS_CITED_AND_METHODS.md#ref-7); music-specific challenges [2](WORKS_CITED_AND_METHODS.md#ref-2).

**Data credit:** ListenBrainz sample, 10 June 2025 [15](WORKS_CITED_AND_METHODS.md#ref-15). Exact retained training counts: 10,082 songs and 152,036 positive pairs. Filtering is the documented sequence in the source register, not an iterative core procedure. Missing feedback is not a dislike.

## Slide 6 — Part 3: Use a learned map of sound

**65 seconds · On screen**

- CLAP learns from paired audio and descriptions.
- **Our data:** existing Clapback audio vectors, matched to recording IDs.
- Optional: explore 200 locally curated descriptions encoded with CLAP.

**Say:** “Finally, we'll explore CLAP: a model trained using audio and text together. We didn't train it. We selected existing Clapback audio vectors, checked their numerical validity and matched them to MusicBrainz recording IDs. That gives the same curated catalogue a richer learned representation. We also prepared 200 candidate descriptions and encoded them offline with CLAP's text branch. We'll compare sound matches and optionally judge which descriptions fit. This introduces embeddings—and lets us investigate both useful connections and mistakes.”

**Research footer:** foundation-model survey [8](WORKS_CITED_AND_METHODS.md#ref-8); LAION CLAP method [9](WORKS_CITED_AND_METHODS.md#ref-9).

**Data credits:** Clapback snapshot, 18 October 2026 [12](WORKS_CITED_AND_METHODS.md#ref-12); MusicBrainz [13](WORKS_CITED_AND_METHODS.md#ref-13); local description bank [17](WORKS_CITED_AND_METHODS.md#ref-17). LAION-Audio-630K is upstream pretraining data described in [9], not a corpus downloaded for this workshop. Descriptions are editorial candidates, not verified captions. Current prepared vectors are real; live free-form text search is retired. Exact upstream audio checkpoint equivalence is not independently established.

## Slide 7 — Your task: predict, listen, compare

**55 seconds · On screen**

1. Choose a familiar starting song.
2. Predict, then listen before revealing the explanation.
3. Rate **similarity** and **enjoyment** separately.
4. Keep the starting song and available choices fixed when comparing methods.

**Say:** “You don't need the maths to investigate these systems. Predict, listen and describe what you hear. A song can sound similar without being enjoyable, or sound different and become a favourite. For a fair comparison, keep the starting song and filters fixed and use the shared supported song pool. By the end, we want to explain how different evidence produces different recommendations—and what we'd need to know before calling one method better.”

**Research footer:** [2](WORKS_CITED_AND_METHODS.md#ref-2), [1](WORKS_CITED_AND_METHODS.md#ref-1). These motivate evaluating listener experience and multiple objectives; our short activity illustrates differences rather than establishing general superiority.
