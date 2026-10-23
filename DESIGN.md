# Music Recommendation Workshop — Product and System Design

Status: agreed design baseline, 19 October 2026. This document records the workshop concept and accepted product decisions. Proposed defaults and unresolved choices are explicitly identified. It is a design specification, not an atomic implementation plan.

## 1. Purpose and learning goals

Build a browser-based workshop in which students investigate music recommendation through listening, experimentation, and small-group discussion.

Students should discover that musical similarity has multiple meanings, that different methods preserve different qualities, and that a plausible similarity is not necessarily a recommendation they enjoy. They should practise describing the musical qualities they like, identifying unexpected connections, disagreeing with model interpretations, and revising their hypotheses.

Curiosity and musicological listening are the central activities. The interface should support them without requiring programming or prior machine-learning knowledge. Familiarity, memory, mood, social identity, and listening context can enter the discussion of musical taste without becoming a separate lecture.

## 2. Workshop format

The event has a fixed 90-minute allocation: two independent 45-minute sessions for different cohorts, each approximately 15–20 participants. Participants are adults aged roughly 20–50, likely skewing toward university-student ages. The workshop takes place at the University of Osnabrück, Germany. Device mix and prior technical knowledge remain to be confirmed.

The app supports more exploration than the facilitated schedule requires. Having three recommendation methods does not mean every student must explore all three during one session.

Proposed 45-minute schedule:

| Minutes | Activity |
| --- | --- |
| 0–5 | Introduce musical similarity and demonstrate one recommendation |
| 5–8 | Select familiar seed songs and record what students like about them |
| 8–16 | Explore song-based recommendations and listen to a few results |
| 16–21 | Discuss connections and disagreements in groups of 3–4 |
| 21–25 | Introduce audio–language embeddings and matching descriptions |
| 25–35 | Inspect descriptions, write a query, listen, and revise one aspect |
| 35–42 | Compare discoveries in the same groups |
| 42–45 | Share surprises and close |

Allow the facilitator to choose a shorter guided path through the available methods. Avoid accounts, installation, and mandatory questionnaires at entry.

## 3. Agreed product structure

One web app has two primary tabs:

1. **Song recommendations:** browse the catalogue, build My List, select a method, generate recommendations, and reflect.
2. **Describe and discover:** inspect prepared descriptions matching a song, disagree or propose alternatives, and retrieve songs using students’ own text.

Both tabs share the song catalogue, stable song identities, listening links, and access to My List. Switching tabs must preserve working state. Students can use external YouTube or Spotify links for full recordings. There is no in-app audio playback or hosted audio. Students listen externally and self-report completion. Embeddings stay behind the app backend.

The workshop is hosted online. Working internet is available at the venue. Students should not need to connect to a facilitator’s laptop or a local server.

## 4. Song recommendations tab

### Catalogue and My List

Provide a clean, scrollable catalogue with text search, genre filters, and year ranges. Display title, artist, year, and genre information. Support multiple genre tags and visibly missing or uncertain metadata rather than inventing precision.

Students add and remove songs in a persistent My List. The agreed initial limit is 1–5 songs. The guided activity starts with one seed; students try additional seeds later. Explain the limit and prevent generating results with an empty list.

Catalogue filters affect browsing only. A separate, explicitly labelled control can restrict the recommendation candidate pool. Changing a browsing filter must not silently change recommendation eligibility or remove selected seeds.

### Recommendation methods

Offer 2–3 contrasting methods. The following is the recommended technical shortlist, pending a small listening pilot and dependency/checkpoint licence checks; these implementations are not yet committed:

| Method | Input information | Educational comparison |
| --- | --- | --- |
| Rhythm and movement | Fixed, scaled AcousticBrainz rhythm/energy descriptors; nearest neighbours using a documented distance | Do rhythmic connections survive changes in genre and instrumentation? |
| Sound and texture | AcousticBrainz timbral/spectral descriptors, such as MFCC summaries, using a documented distance | Does similar production or texture predict enjoyment? |
| Audio–language embeddings | Existing Clapback CLAP vectors, used for audio-to-audio cosine similarity | What does a representation learned to align sound and language preserve? |

Each method needs a short plain-language explanation of its information source. These are content-based systems; they do not use community listening histories. Exact features, scaling, embedding layer, checkpoint, and distance conventions must be validated. Genre/era similarity remains a possible simple fallback rather than a required fourth method. Essentia documents both descriptor extraction and pretrained music embeddings: https://essentia.upf.edu/documentation.html and https://essentia.upf.edu/models.html.

CLAP is the preferred initial audio–language candidate. Original CLaMP targets symbolic music rather than recordings; CLaMP 3 supports audio through MERT preprocessing and is a possible alternative, not a drop-in replacement. Avoid supporting multiple language models unless the pilot establishes a clear benefit. Sources: https://github.com/LAION-AI/CLAP, https://github.com/microsoft/muzic/tree/main/clamp, and https://github.com/sanderwood/clamp3.

For a comparison run, retain the same seeds, candidate pool, and recording representation. Exclude seed songs from recommendations. Group alternate versions or duplicates consistently so they do not dominate results; the exact grouping policy remains to be specified.

### Scoring and results

The initial multi-seed rule is to calculate a candidate’s similarity to each seed and average those similarities with equal weight. Display the strongest seed connections behind that score. This is deliberately understandable and can expose compromise results for a varied seed list.

Methods must define their own similarity calculation. The requested interface displays a percentage, labelled **Match score**, not confidence or probability of enjoyment. The mapping to 0–100 must be specified and documented before implementation. Proposed approach: an empirical percentile against a fixed, versioned reference distribution of non-self scores for each method and seed-count setting. For example, 90% means a stronger computed match than roughly 90% of reference comparisons, not a 90% chance of enjoyment. Show that meaning in accessible help before listening. Preserve raw scores internally. Do not merely multiply arbitrary cosine similarities by 100 or rescale against the currently visible results. Percentiles normalise presentation, not perceptual quality across methods. A pilot must establish whether this convention is understandable before finalising it.

Results use a listening-first reveal. Initially the musical information shown is title, artist, and percentage match score. Necessary listening controls, links, score help, and an **I've Listened** button remain available. Hide genre, year, descriptive labels, seed connections, and explanations until the student explicitly reveals them.

After **I've Listened**, reveal additional metadata, strongest seed connections and individual scores, supported feature comparisons or labelled matching descriptions, and supported source information. Clicking an external link is not proof of listening; use the student's self-report without tracking Spotify or YouTube activity. Preserve reveal state per result and run, and allow replay and revisiting the initial view.

The initial percentage itself can influence expectations, so facilitator materials should not call this a blind experiment.

Seed connections explain the ranking calculation, not the audible reason for similarity. Only claim specific musical causes where supported by explicit feature comparisons. Avoid invented explanations for embedding matches.

Preserve the previous run when students switch methods so they can compare results and reflections without reconstructing their setup. Proposed default: show five results initially, with more available on demand.

### Reflection

Success primarily means the student likes the recommendation. Separately record whether they can hear a plausible connection to their seeds. Suggested lightweight responses are Like / Unsure / Dislike and Connection clear / Partly / Not clear, with optional text. Ask for an initial reaction before opening detailed explanations, without making the reflection mandatory or blocking the reveal.

Provide optional prompts before and after listening, including:

- What do you like about your selected songs?
- What did you expect the method to preserve?
- What stayed similar: rhythm, voice, instrumentation, mood, production, or something else?
- Can you hear the connection even if you dislike the recommendation?
- Which result surprised you, and what connection did you eventually hear?
- Which method helped you discover something you liked, and why?

Preserve answers separately for each run. Proposed default: save session state and notes in the browser without student accounts. Provide a simple copy or download of notes for group discussion. Server-side research collection or facilitator monitoring is outside the agreed scope.

### Optional taste questions

Offer a short optional taste questionnaire that can bias recommendations. Skipping it must preserve the seed-only method. Proposed questions concern instrumental versus vocal music, calmer versus more energetic sound, acoustic versus electronic textures, and familiar versus exploratory listening. Wording and the final question set remain to be tested.

Apply answers only where a defensible scoring signal exists. Do not pretend an audio embedding exposes independent controls for every preference, or treat obscurity as personal unfamiliarity. Define and version each supported reranking rule, label active biases, and expose their role after the listening reveal. The same survey answers and bias setting must remain fixed during a method comparison; default the first guided comparison to biases off. Save the answers and effective scoring configuration with each run. Avoid training a new model from 15–20 participants.

## 5. Describe and discover tab

### Matching descriptions for a song

A contrastive audio–language model maps audio and text into a shared space. It does not directly decode an audio embedding into a unique sentence. The agreed design is to construct a large, curated bank of descriptions, embed it beforehand, and retrieve descriptions closest to the selected song.

The interface should say **Matching descriptions**, not “the song’s true description” or “decoded embedding.” Explain that these are matches from a prepared collection. A mismatch is a useful discussion opportunity.

The bank should cover instrumentation, vocals, rhythm, tempo, texture, production, dynamics, perceived emotion, mood, atmosphere, and everyday “vibe” language. Include both short focused phrases and coherent combinations. Retain category and provenance metadata for every description.

Generate candidate descriptions offline if useful, then review them for clarity, variety, contradictions, stereotypes, and repetition. Do not exhaustively enumerate every combination: catalogue size and wording can bias which descriptions appear. Broad coverage is the aim; “everything possible” is not an achievable completeness criterion.

Precompute text embeddings with the exact text encoder and checkpoint paired with the audio embeddings. For standard song representations, matching-description results can also be precomputed.

Students can select a song from My List or the full catalogue, view several distinct close descriptions, and optionally focus on categories such as vocals, rhythm, mood, or production. Category selection filters the prepared descriptions; it does not retrain the model. Avoid filling the screen with near-identical phrasings.

Invite students to mark descriptions as fitting, partly fitting, or missing the point, and explain why. These responses are reflections, not model training data by default.

### Student-written text search

Students write a description of qualities they enjoy. The backend encodes that new text, compares it with the prepared audio representations, and returns matching songs. Keep the original query and results available when students revise the wording.

Encourage changing one aspect at a time, for example replacing “intimate vocals” with “distant vocals” while keeping the rest fixed. Do not imply that a whole-recording match identifies a particular passage.

The same listening links, result conventions, and reflection tools apply. Ask whether the query expressed what mattered, what the model appeared to understand, and what surprised the student.

Catalogue audio analysis is reused from published data; prompt-bank encoding happens beforehand. Arbitrary student text still requires live text encoding. Keep that service ready before the session, cache repeated queries, and offer prepared example searches if live encoding becomes unavailable. Do not present a fallback example as the result of a failed custom query.

### Comparison limits

Comparing song queries under one model with text queries under another compares discovery experiences, not isolated algorithm quality. If a controlled input comparison is desired, support audio-to-audio and text-to-audio retrieval within the same audio–language model. Retain this distinction in facilitator materials.

## 6. Available song representations and future segments

The current data-first approach reuses a frozen Clapback snapshot of recording-level CLAP vectors, MusicBrainz identities/metadata, and existing AcousticBrainz features. We do not obtain audio, calculate new audio embeddings, or expose vector files to students through the app.

Timestamped segment embeddings remain a desirable future extension, not an initial requirement: the selected Clapback export does not contain them. Do not present section controls, matching timestamps, or configurable pooling without actual compatible segment data. Preserve the original recording-level vectors and exact pipeline identity. The language tab can use these audio-derived vectors with their paired text encoder; it does not need recordings at runtime.

The feature-based methods reuse measured descriptors and learned attribute predictions. Their exact comparison rules remain subject to listening validation. The earlier Discogs-EffNet proposal is optional future work because these newly downloaded data do not supply those embeddings. The revised method shortlist should be based on the actual prepared feature coverage and CLAP results.

## 7. Song bank and offline preparation

Current target: approximately 1,000–2,000 curated songs (initial build target 1,500), from the 1960s through 2022. The 2022 cutoff is accepted to accommodate AcousticBrainz coverage. Include familiar classics and less popular recordings, vocal and instrumental music. Agreed coverage includes rock and roll, smoother styles, funk, jazz, country, acoustic music, psychedelic music, indie electronic music, and EDM. Use overlapping tags rather than forcing each song into one category. Expand adjacent styles where they strengthen coverage and useful connections.

Build a curation matrix crossing decades and broad style families, and track popularity/familiarity proxies and artist concentration. Exact quotas remain open; seek broad meaningful coverage rather than promising exhaustive representation. Identify useful clusters with multiple neighbours so obscure styles are not represented by one isolated song.

Select material for useful cross-genre and cross-era connections as well as breadth. Include similarities in groove, texture, production, mood, and instrumentation that cut across labels. Prevent a few artists or recordings from overwhelming results.

Offline preparation produces a versioned, frozen workshop release:

1. Curated recording catalogue, source IDs, tags, first-release dates, and external search/listening links.
2. Existing AcousticBrainz feature records, retaining provenance and analysis versions.
3. Existing CLAP vectors linked through MusicBrainz recording claims, with an exact pipeline identity.
4. Selection policy, coverage audit, data manifest, checksums, and licensing notes.
5. Later: reviewed description bank and compatible text embeddings, scoring configuration, and prepared recommendation results.

Use stable recording IDs to join all artifacts. Recording-name claims can be wrong; report that limitation, deduplicate carefully, and distinguish exact recording identities from unverified external search links. Genre groupings and familiarity bands are editorial aids, not objective or exhaustive classifications.

### Data rights and sourcing

The current build downloads existing analysis and metadata, not recordings. Retain the publisher-declared licences and provenance for each source: Clapback and AcousticBrainz data are declared CC0; MusicBrainz core data is CC0 while supplementary tags have CC BY-NC-SA terms. The combined collection must not be labelled entirely CC0. See `data/README.md` for details.

Any future acquisition or processing of audio is a separate scope decision requiring appropriate lawful access and an applicable legal basis. No blanket exemption follows from educational or non-commercial purpose. The earlier discussions of excerpt hosting and teaching-use access controls do not apply to this audio-free application.

## 8. Hosting and runtime architecture

Recommended initial architecture, subject to model benchmarking:

- Hosted browser frontend.
- Small hosted backend serving catalogue search and recommendation requests.
- SQLite catalogue packaged with the frozen release; embedding matrices loaded into backend memory.
- A live text encoder, either within the backend or on a separate model service.

No dedicated vector database is required initially at the proposed collection size. Students interact through the app, never directly with a shared database file. Read-only catalogue and analysis artifacts simplify deployment; student notes can remain browser-local.

The backend owns scoring and model configuration. Keep service credentials off student devices. Handle loading, empty results, unavailable audio, and failed text queries explicitly without discarding working state.

The previous hosting discussion established a provisional $25–50 monthly planning allowance, not a committed quote or capacity guarantee. Final costs depend on the text encoder, concurrent attendance, storage, and hosting choices. Offline audio-analysis computing is a separate preparation cost.

## 9. Reliability and usability requirements

- Use hosting configured to remain running during the workshop, with the text encoder loaded in advance.
- Validate expected concurrent attendance and agree a responsive latency target before selecting server capacity.
- Precompute standard results and retain a prepared language-search fallback.
- Freeze and test the workshop release before delivery; avoid deployment changes during a session.
- Test entry from a fresh browser and multiple devices, external listening links and headphones.
- Preserve My List, run history, queries, and notes across navigation and recoverable failures.
- Support keyboard navigation, readable contrast, clear controls, and clear external listening actions.
- Make the guided path obvious while keeping optional settings available for independent exploration.

## 10. Acceptance criteria and verification

- Students can find songs by title/artist, genre, and year, build a valid list, and generate results without an account.
- Browsing filters do not silently change the candidate pool or seeds.
- Method comparisons retain identical inputs and record the method and representation used.
- Multi-seed aggregate scores reproduce the documented rule and displayed seed contributions.
- Seeds are excluded, duplicate handling is consistent, and scores are not presented as enjoyment probabilities.
- Initial results reveal only title, artist, match percentage, and necessary listening controls; explanations appear after the student's explicit listening confirmation.
- Percentage mapping is fixed, documented, and reproducible; filtering visible candidates does not change the reference distribution.
- Optional survey answers can be skipped, supported biases are identified, and comparison runs preserve their configuration.
- Matching descriptions come from the versioned bank and use a compatible audio/text model pair.
- A student can disagree, enter a new description, revise it, and compare the resulting songs and notes.
- No segment controls or timestamps are shown unless a future dataset actually supplies compatible segment analysis.
- No custom text result is fabricated when encoding fails; prepared searches remain usable.
- A complete rehearsal at expected concurrency verifies catalogue access, recommendation latency, text-search latency, external listening, state persistence, and fallback behaviour.

## 11. Open decisions before implementation

- Device mix and technical background; capacity testing should cover at least 20 simultaneous participants plus facilitator access.
- Final catalogue review and recording/version policy; metadata completeness and source-claim reliability.
- Pilot and final selection of feature recipes, validation of the paired text encoder for the downloaded CLAP pipeline, and supported query languages.
- Whether future compatible segment data justifies extending the initial whole-recording collection.
- Final method count, match-percentage reference/mapping, survey questions, and supported bias formulas.
- Hosting provider, runtime size, latency targets, and whether text encoding needs a separate service.
- Reflection export format and whether any intentional cross-device sharing is needed.

## 12. Focused downstream handoff

This repository was empty when this document was created. No application code or technology stack has been implemented or selected beyond the recommendations above.

Must read: `DESIGN.md`. Summarised context: there is no existing application structure to preserve yet. Read only if blocked: selected models’ official input/preprocessing documentation and chosen hosting documentation.

The current task is to prepare and audit the local data collection. After that, resolve the remaining model/scoring choices for a minimal vertical slice, then translate this design into tightly scoped implementation tasks. Do not perform open-ended repository exploration. If the listed context is insufficient, identify the additional file, decision, or output needed. Implementers must read the exact files they will modify and focused tests they will run.

## References

- CLAP research: https://arxiv.org/abs/2206.04769
- LAION CLAP implementation: https://github.com/LAION-AI/CLAP
- SQLite deployment guidance: https://www.sqlite.org/whentouse.html
- Hosting pricing discussed, to recheck before purchase: https://render.com/pricing
- Current data sources: https://clapback.seethroughlab.com/export and https://acousticbrainz.org/
