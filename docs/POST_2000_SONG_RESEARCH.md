# Post-2000 song expansion: eligibility research

Research date: 23 October 2026. Research only; no catalogue, application code, embeddings, or recommender model changed.

## Result and how to read this list

**101 recordings have confirmed accessible user-level feedback plus a ready-made CLAP vector and an exact MusicBrainz recording ID.** Another **399 recordings** have the vector, MusicBrainz identity and measured listening activity, but their underlying user rows were not verified. Those are explicitly conditional, not fully eligible recommendations. There are 500 distinct artist/title candidates in total, across 186 primary artists, with no more than four per primary artist; 409 exact recording IDs are outside the current 1,500-song catalogue.

This is not evidence of 500 new mainstream hits. The CLAP source is still heavily indie/electronic, and a popular artist's album track is not necessarily a recognizable song. Start with the rows marked **★**, an editorial selection of recognizable anchors and pop/funk-adjacent priorities, then inspect the broader options. Popularity here measures the source communities, not familiarity among workshop participants. Rows without ★ are expansion options, including deeper cuts, rather than claims of mainstream recognition.

Years are cached MusicBrainz **recording first-release dates**, restricted to 2001–2026. Known later editions of pre-2001 originals were removed, along with explicitly labelled remixes, live recordings, versions and remasters. The remaining dates have not each been independently checked against the original composition/studio release; a later recording ID can still describe older music. This matters before approving final additions.

**The strict list is shorter than 500 on purpose:** padding it with unverified identity joins or aggregate-only counts would hide the very requirement that makes these songs useful for retraining.

## Eligibility and training evidence

Every table row has an exact recording MBID in the cached MusicBrainz inventory and a corresponding vector physically checked in the 18 October 2026 Clapback export: 512 finite values, with conflicting tied identity claims excluded. All use `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32`, matching the current workshop. The [companion CSV](POST_2000_SONG_RESEARCH.csv) gives the fingerprint hash, pipeline, exact download files, dates, counts, source links and existing-catalogue status for every row. A contributor's MusicBrainz claim is not independent verification of the source audio.

There are two kinds of confirmed user evidence:

- **S n**: n distinct positive listeners actually counted from the existing 10 June 2025 ListenBrainz sample, using exact recording MBIDs. The archive and `recording_feedback.parquet` are already in `data/sources/listenbrainz/`. This is directly accessible training input today.
- **L n**: the current public recording-feedback API returned user-level positive feedback and reported n positive rows. This proves retrievable interactions for that MBID; only a one-row probe was read. All pages still need retrieving before training. It is not a claim that n distinct users survived deduplication or the model's filtering.

Where both exist, both counts are shown; they are not additive. Missing sample support means absent from this sample, not absent from ListenBrainz. Current feedback counts are not listen counts. For the existing model, at least five listeners per song and five songs per listener, followed by a second song-support check, are needed. The CSV separately records support after those existing filters. A song with one love is data-eligible but may not produce a usable collaborative factor. No retraining or model-quality claim was made.

**Popularity provenance:** `POST /1/popularity/recording` was queried for all 13,464 cached post-2000, otherwise eligible recordings. Its `total_user_count` and `total_listen_count` combine ListenBrainz and MLHD tables by summing counts. They must not be described as globally deduplicated ListenBrainz listeners. I inspected the publisher's [implementation](https://github.com/metabrainz/listenbrainz-server/blob/master/listenbrainz/db/popularity.py), specifically `get_counts`, to establish this. Counts only rank research candidates; they are not inputs for collaborative training. The selected list uses a 1,000 combined-user floor, an artist cap and an explicit preference for more recent dates. It is not a statistically representative sample.

Further live feedback lookups encountered repeated TLS connection failures after 30 successful probes. Failures were not converted to zero feedback. Conditional rows need a successful feedback fetch, or a verified user-level listening-data join, before being called retraining-ready.

## Coverage of the proposed list

| Measure | Count |
|---|---:|
| Confirmed user-feedback matches | 101 |
| Conditional: aggregate listening evidence only | 399 |
| Primary artists | 186 |
| 2001–2009 | 230 |
| 2010–2019 | 260 |
| 2020–2026 | 10 |
| Exact recording already in app catalogue | 91 |
| Exact recording outside app catalogue | 409 |
| Confirmed rows supported by existing sample training filters | 83 |

The current source is particularly weak on contemporary mainstream pop, modern funk, Latin pop, Afrobeats and K-pop. This report does not pretend that broad artist diversity alone fixes those genre and geographic gaps. Existing rows are marked **Already** so they are not mistaken for additions; the CSV also flags artist/title matches under a different recording MBID.

## 1. Confirmed data-eligible recordings (101)

★ = editorial priority, not measured chart status. “Source users” is the combined popularity API figure described above. Click the title for the exact MusicBrainz recording. **S/L** is the training evidence; **Already/New** compares exact recording IDs only.

| # | Priority | Artist | Song / recording identity | Year | Source users | User feedback | Catalogue |
|---:|:---:|---|---|---:|---:|---|---|
| 1 | ★ | M83 | [Midnight City](https://musicbrainz.org/recording/e83bc6ba-eff9-412c-8c11-5153672f25e7) | 2011 | 188,675 | S 75; L 232 | Already |
| 2 | ★ | Foster the People | [Pumped Up Kicks](https://musicbrainz.org/recording/55cfb83f-adc1-4730-a71b-90b369fd3f84) | 2010 | 182,806 | L 470 | Already |
| 3 | ★ | Two Door Cinema Club | [What You Know](https://musicbrainz.org/recording/cadde50b-8c42-4a16-af00-185fcc3827f4) | 2010 | 147,432 | L 220 | New |
| 4 | ★ | Two Door Cinema Club | [Something Good Can Work](https://musicbrainz.org/recording/4c9f771c-289c-47a6-b58d-1cd302b47b3f) | 2010 | 143,311 | L 57 | New |
| 5 | ★ | Gorillaz | [Rhinestone Eyes](https://musicbrainz.org/recording/a44db450-2b09-4eca-936f-a939ad56ae16) | 2010 | 130,583 | S 38; L 108 | Already |
| 6 | ★ | Japanese Breakfast | [Be Sweet](https://musicbrainz.org/recording/e94e4013-4236-4106-be51-1f37437936b6) | 2021 | 4,895 | L 105 | Already |
| 7 | ★ | M83 | [Wait](https://musicbrainz.org/recording/9bfa18fd-2dbc-44f9-8048-d86f39dc354c) | 2011 | 108,403 | S 51; L 137 | Already |
| 8 | ★ | MGMT | [Kids](https://musicbrainz.org/recording/c741a7ef-dd33-4c79-a4d4-8745d9675620) | 2007 | 271,665 | S 114; L 467 | Already |
| 9 | ★ | The Killers | [Mr. Brightside](https://musicbrainz.org/recording/560062d0-e122-46be-9d89-0f3b44077fdf) | 2003 | 260,133 | S 159; L 662 | Already |
| 10 | ★ | LCD Soundsystem | [Dance Yrself Clean](https://musicbrainz.org/recording/2351cd90-50cc-4862-bba0-6fa8b807b4e3) | 2010 | 99,331 | L 171 | Already |
| 11 | ★ | MGMT | [Electric Feel](https://musicbrainz.org/recording/987a88ef-6f47-479c-a0ad-1a17aa85e8ed) | 2007 | 240,852 | S 48 | Already |
| 12 | ★ | Daft Punk | [Harder, Better, Faster, Stronger](https://musicbrainz.org/recording/f1a6a40f-78f5-4918-968d-f64363bae94c) | 2001 | 221,392 | S 93 | Already |
| 13 | ★ | Tame Impala | [Elephant](https://musicbrainz.org/recording/920be16d-e040-433d-b941-39bef05543b0) | 2012 | 78,426 | S 44 | New |
| 14 | ★ | Tame Impala | [The Less I Know the Better](https://musicbrainz.org/recording/78be434c-0908-458f-9693-f16cdebb68ef) | 2015 | 18,236 | S 134 | Already |
| 15 | ★ | The Strokes | [Reptilia](https://musicbrainz.org/recording/8f9dec01-c479-4ad4-96b5-0950a97c1a91) | 2003 | 178,918 | S 58 | New |
| 16 | ★ | Johnny Cash | [Hurt](https://musicbrainz.org/recording/25d8de5e-3662-4ffd-8dea-511a696ac3e7) | 2002 | 174,872 | S 178 | Already |
| 17 | ★ | The White Stripes | [Fell in Love With a Girl](https://musicbrainz.org/recording/e9d46dd9-1b5c-4378-a571-5d18fec0917e) | 2001 | 145,301 | S 25 | Already |
| 18 | ★ | Gorillaz | [19-2000](https://musicbrainz.org/recording/b766a7b6-5b8f-4805-ae83-420231c0ec76) | 2001 | 133,605 | S 35 | Already |
| 19 | ★ | Tame Impala | [Let It Happen](https://musicbrainz.org/recording/b85f7f6d-813a-4ebc-8a1d-5998ab02be9a) | 2015 | 13,206 | S 77 | Already |
| 20 | ★ | Tame Impala | [New Person, Same Old Mistakes](https://musicbrainz.org/recording/f078699c-9b68-4040-9ba4-b1e4f7d86598) | 2015 | 10,250 | S 36 | New |
| 21 | ★ | The Strokes | [Last Nite](https://musicbrainz.org/recording/c988fa34-8382-43f3-87af-49dc94018c1e) | 2001 | 91,439 | S 29 | New |
| 22 | ★ | Lady Gaga | [Bad Romance](https://musicbrainz.org/recording/d76057c6-c29c-41f7-b83e-751b4269851d) | 2009 | 90,586 | S 62 | Already |
| 23 | ★ | Beyoncé | [Single Ladies (Put a Ring on It)](https://musicbrainz.org/recording/67dc066b-d84e-444c-b250-82917db7281e) | 2008 | 68,043 | S 14 | Already |
| 24 | ★ | Daft Punk feat. Pharrell Williams & Nile Rodgers | [Get Lucky](https://musicbrainz.org/recording/833f00e1-781f-4edd-90e4-e52712618862) | 2013 | 15,091 | S 177 | Already |
| 25 | ★ | Daft Punk feat. Pharrell Williams | [Lose Yourself to Dance](https://musicbrainz.org/recording/9f381fef-7bbd-4f2a-be8b-2acd072bb7e1) | 2013 | 11,076 | S 45 | New |
| 26 | ★ | The Strokes | [Someday](https://musicbrainz.org/recording/e8d5c3f6-494f-439a-8f6c-889df2b7a4b8) | 2001 | 11,387 | S 33 | New |
| 27 |  | Arcade Fire | [The Suburbs](https://musicbrainz.org/recording/a0c8a6b4-74bf-4c12-b8b7-8f81df881061) | 2010 | 162,173 | S 28; L 153 | New |
| 28 |  | Arcade Fire | [Ready to Start](https://musicbrainz.org/recording/ab205556-92b9-4c89-adec-0a9dbce7b43f) | 2010 | 147,509 | S 39; L 120 | New |
| 29 |  | Radiohead | [Lotus Flower](https://musicbrainz.org/recording/46c13c78-8a42-42f9-8b55-c98f7de025a6) | 2011 | 147,178 | S 11; L 24 | New |
| 30 |  | Arcade Fire | [Modern Man](https://musicbrainz.org/recording/1a38bdc5-ec0f-45a6-970d-a7939343862d) | 2010 | 140,750 | S 6; L 16 | Already |
| 31 |  | Two Door Cinema Club | [Undercover Martyn](https://musicbrainz.org/recording/64bca479-8a95-4ebd-a1db-bff355892b62) | 2010 | 137,044 | L 155 | New |
| 32 |  | Arcade Fire | [Rococo](https://musicbrainz.org/recording/f6de5637-70a0-4a53-952b-410606c41114) | 2010 | 136,822 | S 23; L 49 | New |
| 33 |  | The xx | [Angels](https://musicbrainz.org/recording/fde95c39-ee51-48f6-a7f9-b5631c2ed156) | 2012 | 135,177 | L 57 | New |
| 34 |  | Radiohead | [Bloom](https://musicbrainz.org/recording/54ca7385-2470-4f19-82d4-37a9fae86aa0) | 2011 | 127,841 | S 6; L 17 | New |
| 35 |  | Radiohead | [Codex](https://musicbrainz.org/recording/9e32c01b-bd6d-4d8d-a996-efeb749a8eab) | 2011 | 125,857 | S 18; L 59 | New |
| 36 |  | Radiohead | [Morning Mr Magpie](https://musicbrainz.org/recording/a82cc912-974a-42bc-9b35-f42780090039) | 2011 | 123,959 | S 5; L 14 | New |
| 37 |  | M83 | [Reunion](https://musicbrainz.org/recording/c4423a70-1e8e-45c8-98ad-c51bb25de925) | 2011 | 118,217 | S 9; L 49 | New |
| 38 |  | Massive Attack | [Paradise Circus](https://musicbrainz.org/recording/b350a371-25ea-410d-8c3e-c138503a7cee) | 2010 | 115,110 | S 31; L 139 | Already |
| 39 |  | The xx | [Chained](https://musicbrainz.org/recording/35caf354-44ca-4943-b192-eb5b938e86f8) | 2012 | 113,855 | L 15 | New |
| 40 |  | Crystal Castles | [Not in Love](https://musicbrainz.org/recording/485c9f24-d738-4786-b590-f83865becd74) | 2010 | 110,866 | L 123 | New |
| 41 |  | Crystal Castles | [Celestica](https://musicbrainz.org/recording/8bc9f388-a084-4943-88a6-b2721201da3c) | 2010 | 110,266 | L 91 | New |
| 42 |  | Two Door Cinema Club | [Cigarettes in the Theatre](https://musicbrainz.org/recording/0248fb48-e884-4358-b0e2-74c8fe9c8d92) | 2010 | 110,140 | L 16 | New |
| 43 |  | Crystal Castles | [Baptism](https://musicbrainz.org/recording/ae4f6009-ffe6-472f-bfd2-8868ca9638ac) | 2010 | 108,771 | L 103 | New |
| 44 |  | The xx | [Fiction](https://musicbrainz.org/recording/c60693eb-0624-4847-968b-f80c745f4505) | 2012 | 106,814 | L 22 | New |
| 45 |  | The xx | [Sunset](https://musicbrainz.org/recording/bd4d3e90-37d4-4a44-9eb3-4fb2584414fe) | 2012 | 101,187 | L 18 | New |
| 46 |  | M83 | [Where the Boats Go](https://musicbrainz.org/recording/5d32705b-db0c-4490-9b11-15c4d32620c7) | 2011 | 101,104 | S 7; L 21 | New |
| 47 |  | MGMT | [Flash Delirium](https://musicbrainz.org/recording/e11b7b45-8bb1-4cdf-8c2e-f30abc73d5b5) | 2010 | 99,023 | S 9 | New |
| 48 |  | MGMT | [It’s Working](https://musicbrainz.org/recording/cf09595c-37bc-49e7-b1bf-139ee766c891) | 2010 | 96,211 | S 12 | New |
| 49 |  | Daft Punk | [End of Line](https://musicbrainz.org/recording/c25aba65-17ae-4f2e-a8a8-5aefa4e1348b) | 2010 | 87,152 | S 29 | New |
| 50 |  | Massive Attack | [Rush Minute](https://musicbrainz.org/recording/f4a1d305-dfb1-4ae1-a5d1-a99b384e51ac) | 2010 | 69,783 | S 7 | New |
| 51 |  | Massive Attack | [Saturday Come Slow](https://musicbrainz.org/recording/b22f3988-9bf0-44ec-9230-3728295c57bf) | 2010 | 64,600 | S 7 | New |
| 52 |  | Massive Attack | [Atlas Air](https://musicbrainz.org/recording/1979c223-cb46-4908-bcac-5e9d20cbe83e) | 2010 | 64,263 | S 25 | New |
| 53 |  | Grimes | [Circumambient](https://musicbrainz.org/recording/a057f37e-b84b-4a07-ab18-050015e56ad9) | 2012 | 63,991 | S 21 | New |
| 54 |  | Grimes | [Eight](https://musicbrainz.org/recording/8e7e59b4-ae49-4b90-9597-83e4ec0cf635) | 2012 | 63,725 | S 7 | Already |
| 55 |  | The Strokes | [The Modern Age](https://musicbrainz.org/recording/51e15585-2a4d-4243-b1d6-32ec4fda85ff) | 2001 | 156,922 | S 8 | New |
| 56 |  | Beastie Boys | [Make Some Noise](https://musicbrainz.org/recording/7f4e34a6-e632-40eb-aa2b-3f995ef1bf88) | 2011 | 59,278 | S 21 | New |
| 57 |  | Grimes | [Visiting Statue](https://musicbrainz.org/recording/d77f0e2e-ba44-47f9-b436-621017b2b1c8) | 2012 | 57,999 | S 10 | Already |
| 58 |  | Gorillaz feat. Little Dragon | [Empire Ants](https://musicbrainz.org/recording/a0481faf-70de-41de-95d6-315735ef8aea) | 2010 | 53,842 | S 22 | New |
| 59 |  | Grimes | [Symphonia IX (My Wait Is U)](https://musicbrainz.org/recording/7b8fb58b-833b-4edc-9829-280dbd296b60) | 2012 | 53,336 | S 16 | New |
| 60 |  | Hans Zimmer | [Time](https://musicbrainz.org/recording/e1748d2a-8315-4577-9196-b6a6b96fec3b) | 2010 | 51,399 | S 40 | Already |
| 61 |  | Weezer | [Island in the Sun](https://musicbrainz.org/recording/58044028-9a7e-4da6-9ca8-e5322a25d9a2) | 2001 | 125,729 | S 63 | New |
| 62 |  | Portishead | [The Rip](https://musicbrainz.org/recording/a7ed3365-affa-4331-8bd9-1ececaf9ae77) | 2008 | 118,817 | S 9 | Already |
| 63 |  | Portishead | [Silence](https://musicbrainz.org/recording/83b416db-4ee1-4560-a3b3-52fd453eb285) | 2008 | 108,910 | S 21 | New |
| 64 |  | Portishead | [Machine Gun](https://musicbrainz.org/recording/a4eaf9db-a183-4b55-8ea0-05a18f18368f) | 2008 | 108,452 | S 8 | Already |
| 65 |  | Portishead | [Hunter](https://musicbrainz.org/recording/82f19edd-6d1c-415e-9fe2-876435663cef) | 2008 | 104,706 | S 15 | New |
| 66 |  | The White Stripes | [Dead Leaves and the Dirty Ground](https://musicbrainz.org/recording/b2d95fa8-e3d5-45f7-b915-a8a4b82f6f67) | 2001 | 102,284 | S 6 | Already |
| 67 |  | The White Stripes | [Hotel Yorba](https://musicbrainz.org/recording/1eadd3de-044f-4901-8c0e-3ff4f944e197) | 2001 | 100,571 | S 13 | Already |
| 68 |  | Moby | [Extreme Ways](https://musicbrainz.org/recording/45864691-1ce9-46d2-bc36-1bb606640b10) | 2002 | 97,849 | S 46 | Already |
| 69 |  | The White Stripes | [We’re Going to Be Friends](https://musicbrainz.org/recording/0dcd21fc-fbd6-415f-a2f3-69c1bad432ab) | 2001 | 97,562 | S 19 | Already |
| 70 |  | Beastie Boys | [Nonstop Disco Powerpack](https://musicbrainz.org/recording/2c074a33-1869-470f-9dc9-a9bda95e3449) | 2011 | 38,038 | S 6 | Already |
| 71 |  | Beastie Boys | [OK](https://musicbrainz.org/recording/76fef164-6157-46f0-b888-5be044f10a40) | 2011 | 36,212 | S 4 | Already |
| 72 |  | Gorillaz | [Punk](https://musicbrainz.org/recording/c7bd8ff1-9e4e-4980-988f-1a489f60475e) | 2001 | 89,553 | S 2 | New |
| 73 |  | Moby | [In This World](https://musicbrainz.org/recording/3b35596d-0a87-4863-a87a-e24fbbb6055a) | 2002 | 88,160 | S 12 | New |
| 74 |  | Björk | [Pagan Poetry](https://musicbrainz.org/recording/66dd332c-d163-4dd6-8b3d-7f5900112e99) | 2001 | 87,195 | S 40 | New |
| 75 |  | Beastie Boys | [Say It](https://musicbrainz.org/recording/760de0ff-06a7-453f-ad4e-7aa39d321a53) | 2011 | 32,950 | S 5 | New |
| 76 |  | Björk | [Hidden Place](https://musicbrainz.org/recording/b37ac7fc-4866-497b-b6cb-7fc643cf40fe) | 2001 | 81,006 | S 32 | Already |
| 77 |  | Boards of Canada | [Dayvan Cowboy](https://musicbrainz.org/recording/ef756a43-0905-4e59-8f05-a6b2bd977aa8) | 2005 | 79,549 | S 42 | New |
| 78 |  | Nine Inch Nails | [Only](https://musicbrainz.org/recording/55844e7e-eed5-4533-b429-681da9c81616) | 2005 | 78,688 | S 15 | New |
| 79 |  | The Prodigy | [Spitfire](https://musicbrainz.org/recording/334b90ba-0130-46ba-8e0f-8ffda04a9aa6) | 2004 | 77,783 | S 21 | Already |
| 80 |  | Beck | [Gamma Ray](https://musicbrainz.org/recording/09e7f2c0-249d-481b-b37c-d590a7e77bc8) | 2008 | 74,805 | S 3 | New |
| 81 |  | Moby | [We Are All Made of Stars](https://musicbrainz.org/recording/bb7dcc7a-0b4e-413f-89a3-c3e4ba2d7ff3) | 2002 | 74,537 | S 12 | Already |
| 82 |  | Moby | [In My Heart](https://musicbrainz.org/recording/e47dacc4-dabc-4a39-b3aa-624ea8208fb4) | 2002 | 72,117 | S 6 | New |
| 83 |  | Aphex Twin | [Avril 14th](https://musicbrainz.org/recording/856d081d-320b-4b6b-8dac-4427e308296d) | 2001 | 70,566 | S 57 | Already |
| 84 |  | Nine Inch Nails | [All the Love in the World](https://musicbrainz.org/recording/b2e0a60a-19f3-4a11-8adf-1827e68257d4) | 2005 | 63,997 | S 28 | New |
| 85 |  | Nine Inch Nails | [Right Where It Belongs](https://musicbrainz.org/recording/9e6474b8-96a4-4328-86fd-e9070610687a) | 2005 | 63,206 | S 42 | New |
| 86 |  | Beck | [Scarecrow](https://musicbrainz.org/recording/420e5c2c-9dd1-4401-a6ee-5a84a823d81a) | 2005 | 62,755 | S 7 | New |
| 87 |  | Nine Inch Nails | [Survivalism](https://musicbrainz.org/recording/97d09e1b-8812-45fd-830f-0200a3c0e3b8) | 2007 | 61,901 | S 13 | New |
| 88 |  | Björk | [Earth Intruders](https://musicbrainz.org/recording/e65ddfe1-8b2c-492f-a734-dafaa3cc7322) | 2007 | 58,529 | S 1 | New |
| 89 |  | Beck | [Modern Guilt](https://musicbrainz.org/recording/0d123258-08b5-40fb-87bc-c63d2af5eb75) | 2008 | 56,654 | S 11 | New |
| 90 |  | Boards of Canada | [Music Is Math](https://musicbrainz.org/recording/f0a4be92-bf11-43e3-90eb-6a47e9bcba0c) | 2002 | 56,415 | S 12 | New |
| 91 |  | Beck | [Chemtrails](https://musicbrainz.org/recording/5994cb3b-d680-480e-bbed-576d662e7789) | 2008 | 54,997 | S 15 | New |
| 92 |  | Björk | [Cocoon](https://musicbrainz.org/recording/01737b34-e7de-46f1-91bb-8918efaf8efd) | 2001 | 54,605 | S 7 | New |
| 93 |  | Boards of Canada | [Peacock Tail](https://musicbrainz.org/recording/93fa1eb2-dd7c-4e0e-8174-360d32176586) | 2005 | 54,328 | S 27 | New |
| 94 |  | Weezer | [Don’t Let Go](https://musicbrainz.org/recording/129d60a4-6d2a-4728-aac6-4a61f150aef1) | 2001 | 53,282 | S 14 | New |
| 95 |  | Boards of Canada | [Reach for the Dead](https://musicbrainz.org/recording/70e5da97-00e8-4afe-87dc-1edf94dd022c) | 2013 | 21,081 | S 10 | New |
| 96 |  | Jay‐Z | [Dirt Off Your Shoulder](https://musicbrainz.org/recording/9d4c57fe-ba72-40d5-8bf0-c9c85825bee0) | 2003 | 50,718 | S 8 | Already |
| 97 |  | Aphex Twin | [Jynweythek](https://musicbrainz.org/recording/293ea1b0-9ce4-44af-a46e-ad699975ba74) | 2001 | 50,157 | S 12 | New |
| 98 |  | Weezer | [Simple Pages](https://musicbrainz.org/recording/2c623d93-4e45-4886-86af-a153db6da6b5) | 2001 | 46,324 | S 10 | New |
| 99 |  | Weezer | [Glorious Day](https://musicbrainz.org/recording/b855eea9-ca26-43e2-8304-0e83e3f9b46a) | 2001 | 45,686 | S 8 | New |
| 100 |  | Sufjan Stevens | [They Are Night Zombies!! They Are Neighbors!! They Have Come Back From the Dead!! Ahhhh!](https://musicbrainz.org/recording/a7a2f951-5aa0-4771-9539-88ba52eafc96) | 2005 | 45,146 | S 16 | Already |
| 101 |  | Aphex Twin | [Vordhosbn](https://musicbrainz.org/recording/c639a9a0-ebf8-4d5c-a0c1-4b7a406c1d64) | 2001 | 44,735 | S 54 | New |

## 2. Conditional expansion candidates (399)

These have a verified cached CLAP vector and MusicBrainz ID, plus positive aggregate listening counts. **They do not yet satisfy the verified user-level training-data requirement.** The linked feedback URL in the CSV is the next read-only check. Alternatively, obtain the official ListenBrainz listening dump or permitted MLHD+ data and verify actual user rows. MLHD+ canonicalization can combine recording versions, so an exact audio-version join must be reviewed.

| # | Priority | Artist | Song / recording identity | Year | Source users | User feedback | Catalogue |
|---:|:---:|---|---|---:|---:|---|---|
| 102 | ★ | M.I.A. | [Paper Planes](https://musicbrainz.org/recording/09f03130-4b30-46d8-a2cd-81f8ef9bb97b) | 2007 | 191,196 | Unverified | Already |
| 103 | ★ | Phoenix | [1901](https://musicbrainz.org/recording/8e20739e-0dcc-45b7-ad13-6b5548f0523a) | 2009 | 181,009 | Unverified | New |
| 104 | ★ | Modest Mouse | [Float On](https://musicbrainz.org/recording/2be922c8-1250-47f6-895e-c4da99a93fde) | 2003 | 177,055 | Unverified | New |
| 105 | ★ | The Postal Service | [Such Great Heights](https://musicbrainz.org/recording/276942c0-bbad-4e14-ac8e-6be5154c2d1a) | 2003 | 176,837 | Unverified | New |
| 106 | ★ | Japanese Breakfast | [Paprika](https://musicbrainz.org/recording/0abc4e9a-af0b-4e6b-b21c-df91889b870d) | 2021 | 2,653 | Unverified | New |
| 107 | ★ | Yeah Yeah Yeahs | [Maps](https://musicbrainz.org/recording/2d06f1ff-41e5-4e53-913a-c670b99c9d1e) | 2003 | 165,833 | Unverified | New |
| 108 | ★ | Snow Patrol | [Chasing Cars](https://musicbrainz.org/recording/72e52e92-c273-4b19-9821-5f812484d76d) | 2006 | 163,042 | Unverified | New |
| 109 | ★ | Yeah Yeah Yeahs | [Heads Will Roll](https://musicbrainz.org/recording/493b4b13-f3a3-4ba6-8ae1-7667035dcc16) | 2009 | 157,867 | Unverified | New |
| 110 | ★ | Peter Bjorn and John | [Young Folks](https://musicbrainz.org/recording/e30269b3-eb85-4881-a0fc-ef18be37e89b) | 2006 | 157,101 | Unverified | New |
| 111 | ★ | Passion Pit | [Sleepyhead](https://musicbrainz.org/recording/13e8816a-68f4-4eef-ae5f-b06955477b8f) | 2008 | 152,517 | Unverified | New |
| 112 | ★ | Empire of the Sun | [Walking on a Dream](https://musicbrainz.org/recording/170dfa5d-0235-446d-9f3d-d235c01abc91) | 2008 | 145,749 | Unverified | New |
| 113 | ★ | La Roux | [Bulletproof](https://musicbrainz.org/recording/bf3e215f-40b3-495c-b782-42bf65e5e254) | 2009 | 145,319 | Unverified | New |
| 114 | ★ | Jimmy Eat World | [The Middle](https://musicbrainz.org/recording/e3b7cd96-c41d-497a-b401-dc7494f638db) | 2001 | 139,906 | Unverified | New |
| 115 | ★ | Passion Pit | [Little Secrets](https://musicbrainz.org/recording/a5b60e48-2026-4b9a-b7c6-3a2193e3e08d) | 2009 | 123,085 | Unverified | New |
| 116 | ★ | Empire of the Sun | [We Are the People](https://musicbrainz.org/recording/35b424ed-5524-45dc-a463-679374a53620) | 2008 | 108,596 | Unverified | New |
| 117 | ★ | Miike Snow | [Animal](https://musicbrainz.org/recording/1b2e2cb6-b3cf-42ca-8780-b413f8b2cb59) | 2009 | 106,818 | Unverified | New |
| 118 | ★ | Metric | [Help I’m Alive](https://musicbrainz.org/recording/03adc808-c5c3-4110-a8d0-341134eeb6f8) | 2009 | 105,670 | Unverified | New |
| 119 | ★ | LCD Soundsystem | [All My Friends](https://musicbrainz.org/recording/722b0851-8793-4df7-9aff-835cd3770a8c) | 2007 | 103,660 | Unverified | Already |
| 120 | ★ | Röyksopp | [Eple](https://musicbrainz.org/recording/df53e8c6-3665-43fb-8324-a9306cb88c20) | 2001 | 103,288 | Unverified | Already |
| 121 | ★ | Hot Chip | [Ready for the Floor](https://musicbrainz.org/recording/9fd2fce7-0886-4138-9c57-6b1d8360ab95) | 2007 | 102,443 | Unverified | New |
| 122 | ★ | Capital Cities | [Safe and Sound](https://musicbrainz.org/recording/759d5190-97a4-48b8-90d4-c298dab9c72e) | 2011 | 40,561 | Unverified | New |
| 123 | ★ | Röyksopp | [What Else Is There?](https://musicbrainz.org/recording/9ab4b741-1953-48cd-9cea-8539edaf11bb) | 2005 | 96,868 | Unverified | Already |
| 124 | ★ | Metric | [Gold Guns Girls](https://musicbrainz.org/recording/51533967-56d0-431f-aa00-12cb953d4d42) | 2009 | 86,348 | Unverified | New |
| 125 | ★ | Men I Trust | [Show Me How](https://musicbrainz.org/recording/dbad831a-7a9d-416e-9ef0-11e740fef6a0) | 2017 | 7,801 | Unverified | New |
| 126 | ★ | Justin Timberlake | [Rock Your Body](https://musicbrainz.org/recording/fc4df577-131b-4b88-b468-37a1b9a69570) | 2002 | 76,801 | Unverified | Already |
| 127 | ★ | MIKA | [Love Today](https://musicbrainz.org/recording/c0c2de43-a2fc-45ea-84ca-7873d57fb330) | 2007 | 76,227 | Unverified | Already |
| 128 | ★ | Friendly Fires | [Jump in the Pool](https://musicbrainz.org/recording/96ebbc7c-e935-4d26-a2d7-a2371a92bf48) | 2008 | 70,924 | Unverified | New |
| 129 | ★ | Goldfrapp | [Strict Machine](https://musicbrainz.org/recording/72428053-d408-4314-a41d-7871942f51d5) | 2003 | 67,269 | Unverified | New |
| 130 | ★ | Scissor Sisters | [I Don’t Feel Like Dancin’](https://musicbrainz.org/recording/3725ce95-2158-4565-9c7c-f29f8df3f3a9) | 2006 | 65,585 | Unverified | Already |
| 131 | ★ | CHVRCHES | [The Mother We Share](https://musicbrainz.org/recording/a655a9d6-2438-4405-b72b-a74ad7f58249) | 2012 | 24,307 | Unverified | New |
| 132 | ★ | TV Girl | [Cigarettes Out the Window](https://musicbrainz.org/recording/b589b70d-e156-4276-9c15-55b9398d4a0f) | 2016 | 5,509 | Unverified | New |
| 133 | ★ | Todd Terje | [Inspector Norse](https://musicbrainz.org/recording/295ea5a4-ec43-46ba-b8b1-227fdcd3ec25) | 2014 | 20,771 | Unverified | New |
| 134 | ★ | TV Girl | [Not Allowed](https://musicbrainz.org/recording/75d28825-110a-46b7-b08b-8001f7aacfd8) | 2016 | 5,204 | Unverified | New |
| 135 | ★ | Calvin Harris | [Acceptable in the 80s](https://musicbrainz.org/recording/24295d5e-9f97-45a3-9c53-cb158cb87332) | 2007 | 50,366 | Unverified | New |
| 136 | ★ | Little Boots | [Remedy](https://musicbrainz.org/recording/d422732b-72d2-4425-9916-c0f7fb292e7a) | 2008 | 46,168 | Unverified | New |
| 137 | ★ | Justin Timberlake feat. Clipse | [Like I Love You](https://musicbrainz.org/recording/d8089ed7-eccc-4753-b70f-728f318f3b64) | 2002 | 35,880 | Unverified | Already |
| 138 | ★ | Chromeo | [Needy Girl](https://musicbrainz.org/recording/54e891f4-4e13-4e1d-88f5-3e9815b6d53c) | 2004 | 33,354 | Unverified | Already |
| 139 | ★ | Little Boots | [New in Town](https://musicbrainz.org/recording/25fe9e24-90bd-48fb-9831-79fb7efcf8c3) | 2008 | 32,598 | Unverified | New |
| 140 | ★ | Future Islands | [Seasons (Waiting on You)](https://musicbrainz.org/recording/db025af4-8c37-43ff-9a1c-e1d87b3440bb) | 2014 | 4,574 | Unverified | New |
| 141 | ★ | Hot Chip | [Over and Over](https://musicbrainz.org/recording/e92ce0b9-031c-451d-aee9-c6a248f93cf3) | 2005 | 3,003 | Unverified | New |
| 142 |  | Beach House | [Myth](https://musicbrainz.org/recording/eea564f4-4dc5-4115-adad-d03edb631e8c) | 2012 | 95,283 | Unverified | New |
| 143 |  | Broken Bells | [The Ghost Inside](https://musicbrainz.org/recording/c618a091-e850-44a1-9e7e-ec90dfd0f312) | 2010 | 92,473 | Unverified | New |
| 144 |  | Crystal Castles | [Empathy](https://musicbrainz.org/recording/e494b493-0ba9-43de-9637-fbd224133850) | 2010 | 92,285 | Unverified | New |
| 145 |  | LCD Soundsystem | [I Can Change](https://musicbrainz.org/recording/9465afb3-adb5-49a1-81f6-df750771601b) | 2010 | 88,025 | Unverified | Already |
| 146 |  | LCD Soundsystem | [Drunk Girls](https://musicbrainz.org/recording/cb0dd1dd-ea2f-401f-8b2d-d4e8a5ea632f) | 2010 | 86,436 | Unverified | New |
| 147 |  | Fontaines D.C. | [I Love You](https://musicbrainz.org/recording/be9db312-2af0-4770-a56a-81fd382e802a) | 2022 | 3,251 | Unverified | New |
| 148 |  | Broken Bells | [Vaporize](https://musicbrainz.org/recording/1ab79466-00b5-46b0-be2a-c2d395003bf9) | 2010 | 81,353 | Unverified | Already |
| 149 |  | Caribou | [Sun](https://musicbrainz.org/recording/f29b6114-8ffa-415f-b39d-0578d12e5cab) | 2010 | 79,331 | Unverified | New |
| 150 |  | Bonobo | [Kong](https://musicbrainz.org/recording/325735b0-a7a7-4193-83a7-25ec0c856c06) | 2010 | 75,454 | Unverified | New |
| 151 |  | Beach House | [Lazuli](https://musicbrainz.org/recording/2360ddae-451c-49f9-a0ee-01487ee4b351) | 2012 | 74,506 | Unverified | New |
| 152 |  | Yeasayer | [Madder Red](https://musicbrainz.org/recording/c724149f-8b79-4072-a7a3-97d0181bb262) | 2010 | 74,181 | Unverified | New |
| 153 |  | Japanese Breakfast | [Kokomo, IN](https://musicbrainz.org/recording/f0ab30a9-9994-4645-921c-626c3a7e44e4) | 2021 | 2,876 | Unverified | New |
| 154 |  | Fontaines D.C. | [Roman Holiday](https://musicbrainz.org/recording/60cf268e-d6e2-4902-8000-d6eeddcf74be) | 2022 | 2,862 | Unverified | New |
| 155 |  | Broken Bells | [Your Head Is on Fire](https://musicbrainz.org/recording/0d3e516c-bc7a-4b7c-b98f-9ea9e068d2b2) | 2010 | 71,264 | Unverified | New |
| 156 |  | Beach House | [Wild](https://musicbrainz.org/recording/74553607-fac3-401b-9858-0fd9b3c8fa41) | 2012 | 71,180 | Unverified | New |
| 157 |  | Broken Bells | [Sailing to Nowhere](https://musicbrainz.org/recording/91a725e2-214f-4a84-bdbb-54dca40e5d7a) | 2010 | 69,228 | Unverified | New |
| 158 |  | Caribou | [Kaili](https://musicbrainz.org/recording/91952613-ae75-4681-a458-db6812542a72) | 2010 | 68,739 | Unverified | Already |
| 159 |  | Neon Indian | [Polish Girl](https://musicbrainz.org/recording/66dca858-cd4f-45f2-8dea-3a0e020f1fd7) | 2011 | 68,492 | Unverified | New |
| 160 |  | Washed Out | [Amor Fati](https://musicbrainz.org/recording/82b24507-85c1-47b9-9560-5e3ab34167e3) | 2011 | 68,075 | Unverified | New |
| 161 |  | Beach House | [Other People](https://musicbrainz.org/recording/3133af34-28f0-4f79-97a9-d929b9f553a3) | 2012 | 67,966 | Unverified | New |
| 162 |  | Bombay Bicycle Club | [Shuffle](https://musicbrainz.org/recording/00a30da1-f256-4f91-ad40-262835625f08) | 2011 | 67,775 | Unverified | New |
| 163 |  | Caribou | [Found Out](https://musicbrainz.org/recording/86a984bc-7c6d-4194-85c4-35a0f79bcff5) | 2010 | 66,681 | Unverified | New |
| 164 |  | Metronomy | [The Bay](https://musicbrainz.org/recording/4bb3577e-1c98-4a32-b5eb-534df23ffdac) | 2011 | 66,335 | Unverified | Already |
| 165 |  | Bonobo | [Prelude](https://musicbrainz.org/recording/7aa3af75-2641-460a-98d0-d88badf91a6b) | 2010 | 65,109 | Unverified | Already |
| 166 |  | Deerhunter | [Revival](https://musicbrainz.org/recording/9cd0c752-ae79-4fe7-8381-c8cb03d93fa6) | 2010 | 64,892 | Unverified | New |
| 167 |  | Japanese Breakfast | [Posing in Bondage](https://musicbrainz.org/recording/b895e437-a233-4f69-ab04-e482417a5c46) | 2021 | 2,566 | Unverified | Already |
| 168 |  | Cults | [You Know What I Mean](https://musicbrainz.org/recording/dc21d437-8ebc-48ae-a0f8-e2ec6c88592e) | 2011 | 63,826 | Unverified | New |
| 169 |  | Caribou | [Leave House](https://musicbrainz.org/recording/ed79a864-1bc1-4e22-aee9-2b03367c1eb1) | 2010 | 63,595 | Unverified | New |
| 170 |  | Bonobo | [El Toro](https://musicbrainz.org/recording/be8a4025-164b-458d-a0ef-5e6a54a597d3) | 2010 | 63,524 | Unverified | Already |
| 171 |  | Yeasayer | [I Remember](https://musicbrainz.org/recording/64cde14b-dd79-4dd4-b995-7ccd50c5408f) | 2010 | 63,283 | Unverified | New |
| 172 |  | Bonobo | [We Could Forever](https://musicbrainz.org/recording/50d06859-a535-4bf9-ac01-77a960e1b590) | 2010 | 62,926 | Unverified | New |
| 173 |  | Toro y Moi | [Blessa](https://musicbrainz.org/recording/45ce50f8-a84b-4ec8-971e-6c0b2bfcc054) | 2010 | 60,729 | Unverified | New |
| 174 |  | Yeasayer | [The Children](https://musicbrainz.org/recording/0da83ffb-2fe6-4e51-8537-7a032f84861d) | 2010 | 59,298 | Unverified | New |
| 175 |  | TV on the Radio | [Will Do](https://musicbrainz.org/recording/41eff432-373f-4b3e-89c5-bfe0ac987459) | 2011 | 58,659 | Unverified | New |
| 176 |  | Deerhunter | [Desire Lines](https://musicbrainz.org/recording/fb976a61-21fb-4567-bb01-9aa023fef9f1) | 2010 | 58,318 | Unverified | New |
| 177 |  | Toro y Moi | [New Beat](https://musicbrainz.org/recording/fa117e37-a278-47e0-a835-9f12415a6b38) | 2011 | 56,619 | Unverified | New |
| 178 |  | Interpol | [Evil](https://musicbrainz.org/recording/6c450822-41ca-444e-8be5-10ee5a9ea53a) | 2004 | 142,068 | Unverified | New |
| 179 |  | M.I.A. | [XXXO](https://musicbrainz.org/recording/cfc00462-3d92-4e1e-8e64-edd59b67bbd4) | 2010 | 56,316 | Unverified | New |
| 180 |  | Passion Pit | [Take a Walk](https://musicbrainz.org/recording/080d1de1-d1d0-4818-b25d-49f9451ab7cb) | 2012 | 56,276 | Unverified | New |
| 181 |  | Yeasayer | [Love Me Girl](https://musicbrainz.org/recording/2271c923-3d9a-4835-b14d-7cc6c31200c6) | 2010 | 56,112 | Unverified | New |
| 182 |  | Sigur Rós | [Glósóli](https://musicbrainz.org/recording/af21eaa4-45a5-4868-a924-26042cc9bf78) | 2005 | 137,920 | Unverified | New |
| 183 |  | Bombay Bicycle Club | [How Can You Swallow So Much Sleep](https://musicbrainz.org/recording/a6ec16e6-e314-4fc6-a742-f3162fd9117f) | 2010 | 54,860 | Unverified | New |
| 184 |  | Passion Pit | [Carried Away](https://musicbrainz.org/recording/87dbc086-4144-4ff9-8465-05a1371166f1) | 2012 | 54,672 | Unverified | New |
| 185 |  | Yeah Yeah Yeahs | [Gold Lion](https://musicbrainz.org/recording/7f29e3ad-50f1-499d-9811-566e490852cc) | 2006 | 137,064 | Unverified | New |
| 186 |  | Purity Ring | [Obedear](https://musicbrainz.org/recording/cc53cadd-a2dc-43db-9db5-c1628ad0d3cb) | 2012 | 54,436 | Unverified | New |
| 187 |  | Cut Copy | [Where I’m Going](https://musicbrainz.org/recording/4745b1a7-4dfa-4b31-b379-099e855c82eb) | 2010 | 54,256 | Unverified | New |
| 188 |  | Toro y Moi | [Still Sound](https://musicbrainz.org/recording/69d87ce4-7bf6-4328-a006-d0652726639a) | 2011 | 52,527 | Unverified | New |
| 189 |  | Washed Out | [Echoes](https://musicbrainz.org/recording/e2e0c0a5-243d-4ca2-9883-43e52ec72d02) | 2011 | 52,482 | Unverified | Already |
| 190 |  | The Knife | [Heartbeats](https://musicbrainz.org/recording/db4c9220-df76-4b42-b6f5-8bf52cc80f77) | 2002 | 131,779 | Unverified | Already |
| 191 |  | Phoenix | [Fences](https://musicbrainz.org/recording/87972a3c-dcda-4d34-aa8a-613eb092232e) | 2009 | 131,262 | Unverified | New |
| 192 |  | Purity Ring | [Ungirthed](https://musicbrainz.org/recording/b34ab174-da7d-4276-9982-81364985a0fe) | 2011 | 52,167 | Unverified | Already |
| 193 |  | The Drums | [Money](https://musicbrainz.org/recording/a4fc3d78-6520-4663-82bd-10393bb0af2b) | 2011 | 52,075 | Unverified | New |
| 194 |  | Phoenix | [Countdown (Sick For The Big Sun)](https://musicbrainz.org/recording/49524821-bb59-481b-bcfb-c6dcc917f42e) | 2010 | 51,917 | Unverified | New |
| 195 |  | Yeah Yeah Yeahs | [Zero](https://musicbrainz.org/recording/01f6b5dd-a25f-4789-b1b8-2ded99a26f57) | 2009 | 130,395 | Unverified | New |
| 196 |  | Washed Out | [You and I](https://musicbrainz.org/recording/07c2bb6a-ae02-49db-b599-8bda5e719334) | 2011 | 51,849 | Unverified | New |
| 197 |  | Youth Lagoon | [Afternoon](https://musicbrainz.org/recording/49f8b4dd-ceae-434c-9065-f0c37028152d) | 2011 | 51,769 | Unverified | New |
| 198 |  | Interpol | [Obstacle 1](https://musicbrainz.org/recording/1612c91a-f7f3-4727-901d-bb338987132d) | 2002 | 129,409 | Unverified | New |
| 199 |  | Phoenix | [Lasso](https://musicbrainz.org/recording/dfdc251c-1efa-43de-83d3-1ac105bf8e6a) | 2009 | 128,985 | Unverified | New |
| 200 |  | Purity Ring | [Lofticries](https://musicbrainz.org/recording/0af7ec4e-bcf5-41bc-a2aa-24719112f869) | 2011 | 51,267 | Unverified | New |
| 201 |  | Franz Ferdinand | [Jacqueline](https://musicbrainz.org/recording/046e4951-5daa-4bd0-8b6a-5b47b27583c9) | 2004 | 128,330 | Unverified | Already |
| 202 |  | Washed Out | [Soft](https://musicbrainz.org/recording/a6d89cd5-3051-4f50-852f-6369d794f5ed) | 2011 | 50,879 | Unverified | New |
| 203 |  | Justice | [On’n’On](https://musicbrainz.org/recording/0e5d05c8-f89d-4420-99a7-f4e9a0c68fff) | 2011 | 50,855 | Unverified | Already |
| 204 |  | Ariel Pink’s Haunted Graffiti | [Round and Round](https://musicbrainz.org/recording/94bcf949-6831-4b06-a356-6d085788912e) | 2010 | 50,689 | Unverified | New |
| 205 |  | The Postal Service | [The District Sleeps Alone Tonight](https://musicbrainz.org/recording/e6def49c-c92d-4f94-a842-ab38f0b14e52) | 2003 | 123,886 | Unverified | New |
| 206 |  | Sigur Rós | [Varúð](https://musicbrainz.org/recording/14a2d45e-01d1-41bd-b791-98ed6ea4dc7d) | 2012 | 48,431 | Unverified | Already |
| 207 |  | Purity Ring | [Belispeak](https://musicbrainz.org/recording/a8b75334-1476-4bda-a805-1eaa23f184a6) | 2011 | 48,028 | Unverified | New |
| 208 |  | Beirut | [Port of Call](https://musicbrainz.org/recording/9bccee07-11f1-4b24-80f0-00773e62cb30) | 2011 | 47,957 | Unverified | Already |
| 209 |  | The Shins | [Australia](https://musicbrainz.org/recording/5de7df64-b83a-4f05-9c3c-bfeb0a0bf0d2) | 2007 | 119,816 | Unverified | New |
| 210 |  | Ratatat | [Drugs](https://musicbrainz.org/recording/70df4f21-e321-4d48-ba34-fbe48104aa7d) | 2010 | 47,650 | Unverified | New |
| 211 |  | Toro y Moi | [Talamak](https://musicbrainz.org/recording/957673a0-6a9a-4de1-8c33-f26538c0b74a) | 2010 | 47,566 | Unverified | New |
| 212 |  | Bombay Bicycle Club | [Lights Out, Words Gone](https://musicbrainz.org/recording/c408314f-cb43-4ee4-8ccc-a44dcb81d8b2) | 2011 | 47,417 | Unverified | New |
| 213 |  | The Horrors | [Still Life](https://musicbrainz.org/recording/41999e4f-9a3c-4684-b7f4-429d651f91b0) | 2011 | 47,205 | Unverified | New |
| 214 |  | Justice | [Genesis](https://musicbrainz.org/recording/a405352d-6f33-482c-a1be-0b5b2c966b63) | 2007 | 117,941 | Unverified | New |
| 215 |  | The Postal Service | [Nothing Better](https://musicbrainz.org/recording/a73e9515-0d9b-480d-a7c0-188aa566522d) | 2003 | 117,645 | Unverified | New |
| 216 |  | Youth Lagoon | [17](https://musicbrainz.org/recording/097d48da-bacd-45cf-9747-d9862237c030) | 2011 | 46,771 | Unverified | New |
| 217 |  | The Postal Service | [Sleeping In](https://musicbrainz.org/recording/d143e43e-c0bb-4c5a-a6f0-ccfc448d66b5) | 2003 | 117,256 | Unverified | New |
| 218 |  | Miike Snow | [Paddling Out](https://musicbrainz.org/recording/bb0201ea-acc3-4f6d-be59-390c64dea954) | 2012 | 46,528 | Unverified | New |
| 219 |  | The Radio Dept. | [Heaven’s on Fire](https://musicbrainz.org/recording/21d2aeac-424b-416c-bb22-21d37fd027ea) | 2010 | 46,040 | Unverified | New |
| 220 |  | Snow Patrol | [Open Your Eyes](https://musicbrainz.org/recording/0fd83fb8-a117-4787-ba46-de4046c423e4) | 2006 | 115,004 | Unverified | New |
| 221 |  | Youth Lagoon | [Daydream](https://musicbrainz.org/recording/f044c3c2-a0dc-4ce2-ac3f-d1d95cfe3d50) | 2011 | 45,737 | Unverified | New |
| 222 |  | Interpol | [PDA](https://musicbrainz.org/recording/1c4eab85-b124-45f4-b953-c90a7340aaea) | 2002 | 114,185 | Unverified | New |
| 223 |  | Youth Lagoon | [Posters](https://musicbrainz.org/recording/42ecdeda-bc55-426f-8b52-3c4e023f51a8) | 2011 | 45,383 | Unverified | New |
| 224 |  | TV on the Radio | [Second Song](https://musicbrainz.org/recording/5559e9ad-0db9-4b95-b310-8b84286f5ce2) | 2011 | 44,697 | Unverified | New |
| 225 |  | Tenacious D | [Tribute](https://musicbrainz.org/recording/61630ff2-b63f-4d50-9a0a-bef5d0dcbfe2) | 2001 | 112,166 | Unverified | Already |
| 226 |  | Modest Mouse | [The World at Large](https://musicbrainz.org/recording/bd27c9e5-42d7-4191-a6d5-65013a2d6fd3) | 2004 | 111,084 | Unverified | New |
| 227 |  | The Shins | [Phantom Limb](https://musicbrainz.org/recording/c47c0641-3658-4f9b-80f8-50fdfbfe3b56) | 2006 | 110,887 | Unverified | Already |
| 228 |  | Röyksopp | [Happy Up Here](https://musicbrainz.org/recording/04175385-dc10-4c35-9767-4120818d1a09) | 2009 | 110,511 | Unverified | Already |
| 229 |  | Real Estate | [Green Aisles](https://musicbrainz.org/recording/128cdeff-0e9e-4547-a405-f482bbbc5dcf) | 2011 | 43,843 | Unverified | New |
| 230 |  | Destroyer | [Kaputt](https://musicbrainz.org/recording/9f0507de-2c1c-4acb-a22d-804b638beb3e) | 2011 | 43,714 | Unverified | New |
| 231 |  | Sigur Rós | [Heysátan](https://musicbrainz.org/recording/694a8c8b-a19f-4eb5-891c-50e934a7cf01) | 2005 | 109,073 | Unverified | New |
| 232 |  | The Shins | [Sleeping Lessons](https://musicbrainz.org/recording/ae14ac35-439d-45a8-8844-087b466211cd) | 2007 | 108,756 | Unverified | New |
| 233 |  | Tycho | [A Walk](https://musicbrainz.org/recording/b9a7e199-effd-4abf-98a2-74f17f1b8974) | 2011 | 43,201 | Unverified | Already |
| 234 |  | Interpol | [Untitled](https://musicbrainz.org/recording/5025349a-bd35-42c9-9742-ea682ddc50b9) | 2002 | 107,725 | Unverified | New |
| 235 |  | Ratatat | [Neckbrace](https://musicbrainz.org/recording/2772b0ac-c244-400a-a04e-c96da477572b) | 2010 | 42,841 | Unverified | New |
| 236 |  | Twin Shadow | [Castles in the Snow](https://musicbrainz.org/recording/3299c489-a02f-439e-8ac9-b34eba8e4a2e) | 2010 | 42,782 | Unverified | New |
| 237 |  | Fontaines D.C. | [Skinty Fia](https://musicbrainz.org/recording/47719cbe-db76-41ce-bde8-e1dcce51df84) | 2022 | 1,662 | Unverified | New |
| 238 |  | The Flaming Lips | [Do You Realize??](https://musicbrainz.org/recording/238a3a15-b98f-4149-9e15-c954d43e20cb) | 2002 | 104,316 | Unverified | New |
| 239 |  | TV on the Radio | [Wolf Like Me](https://musicbrainz.org/recording/a8618514-577d-4bc2-b810-eac5f7f1e542) | 2006 | 103,819 | Unverified | New |
| 240 |  | Austra | [Lose It](https://musicbrainz.org/recording/849a2562-2fa3-4e59-af30-4f5880030d45) | 2011 | 41,279 | Unverified | New |
| 241 |  | Sigur Rós | [Inní mér syngur vitleysingur](https://musicbrainz.org/recording/2141dacc-feb8-48e8-b2d4-513d305f3250) | 2008 | 102,851 | Unverified | New |
| 242 |  | Fontaines D.C. | [Big Shot](https://musicbrainz.org/recording/6143a372-f662-43af-9179-f11bd7da491e) | 2022 | 1,624 | Unverified | New |
| 243 |  | Hot Chip | [Motion Sickness](https://musicbrainz.org/recording/5fb82d42-9c25-462d-858f-82dc682a81eb) | 2012 | 40,748 | Unverified | New |
| 244 |  | Twin Shadow | [Five Seconds](https://musicbrainz.org/recording/f797d197-e9b0-42d2-810b-c08049ecb1c8) | 2012 | 40,673 | Unverified | New |
| 245 |  | Hot Chip | [Flutes](https://musicbrainz.org/recording/c3d63b46-6bfc-422d-b420-dad8443ad17c) | 2012 | 40,362 | Unverified | New |
| 246 |  | Kavinsky & Lovefoxxx | [Nightcall](https://musicbrainz.org/recording/3a2f5805-565f-433f-a92d-d1ac7aee6575) | 2010 | 40,237 | Unverified | New |
| 247 |  | Modest Mouse | [Ocean Breathes Salty](https://musicbrainz.org/recording/cc7e3ca6-abed-42af-89b1-12b78d7b296b) | 2004 | 100,189 | Unverified | New |
| 248 |  | TV on the Radio | [You](https://musicbrainz.org/recording/083cba42-a300-4635-9b8e-77dd5ea654e3) | 2011 | 39,330 | Unverified | New |
| 249 |  | Snow Patrol | [Shut Your Eyes](https://musicbrainz.org/recording/fce2420a-a17c-4b66-99cc-677059aef05f) | 2006 | 98,541 | Unverified | New |
| 250 |  | Death Cab for Cutie | [The New Year](https://musicbrainz.org/recording/2aefb5c8-f137-4289-b9f9-e78d23695468) | 2003 | 98,484 | Unverified | New |
| 251 |  | Twin Shadow | [When We’re Dancing](https://musicbrainz.org/recording/e6804774-ef33-4f93-8104-05c92564413c) | 2010 | 39,080 | Unverified | New |
| 252 |  | Fever Ray | [If I Had a Heart](https://musicbrainz.org/recording/55a6d83f-af43-449e-a6b4-1b8fa24b4039) | 2008 | 97,997 | Unverified | New |
| 253 |  | Modest Mouse | [The View](https://musicbrainz.org/recording/00759cc9-9a2f-43b5-b6a2-516fcd20ee64) | 2004 | 97,827 | Unverified | New |
| 254 |  | The Glitch Mob | [Animus Vox](https://musicbrainz.org/recording/328612c3-cfe6-4230-9bc7-aacade1ff657) | 2010 | 38,711 | Unverified | Already |
| 255 |  | Ratatat | [Bilar](https://musicbrainz.org/recording/645d383c-6f14-4414-a137-06d5f9b25f45) | 2010 | 38,678 | Unverified | New |
| 256 |  | Oh Land | [Sun of a Gun](https://musicbrainz.org/recording/33236bdb-89bd-4df2-9174-8a01b402ca0a) | 2011 | 38,517 | Unverified | New |
| 257 |  | Digitalism | [2 Hearts](https://musicbrainz.org/recording/267c4d4f-7d62-407d-9e3d-32dfbdaeeb53) | 2011 | 38,491 | Unverified | New |
| 258 |  | The Knife | [Silent Shout](https://musicbrainz.org/recording/61267686-d9d4-4c68-b08a-ab356ea49cae) | 2006 | 96,681 | Unverified | Already |
| 259 |  | Tycho | [Hours](https://musicbrainz.org/recording/a5b7507a-8f3e-4a1f-a7f0-5c82f4b37a9f) | 2011 | 38,447 | Unverified | New |
| 260 |  | Air | [Cherry Blossom Girl](https://musicbrainz.org/recording/833769db-6c5b-4a08-82ff-4fb0ab6ab1dc) | 2004 | 96,104 | Unverified | Already |
| 261 |  | Fever Ray | [When I Grow Up](https://musicbrainz.org/recording/a62817d2-a7d2-4e1a-8c64-b225076eef8d) | 2009 | 95,828 | Unverified | New |
| 262 |  | Snow Patrol | [Hands Open](https://musicbrainz.org/recording/97f04e5e-abf0-4741-8072-925bbb7e85fb) | 2006 | 95,547 | Unverified | New |
| 263 |  | The Shins | [Turn on Me](https://musicbrainz.org/recording/926591d8-8843-40fe-9f28-d2ff122245ea) | 2007 | 94,925 | Unverified | New |
| 264 |  | Air | [Alone in Kyoto](https://musicbrainz.org/recording/f900f8e2-7d49-4cca-a9a9-ee67dda88e6e) | 2003 | 94,691 | Unverified | New |
| 265 |  | Röyksopp | [So Easy](https://musicbrainz.org/recording/fccb716f-1ee2-4134-8a63-d2ac3f3dc01e) | 2001 | 94,516 | Unverified | New |
| 266 |  | Miike Snow | [The Wave](https://musicbrainz.org/recording/0a6a3549-2178-41b4-bc91-6883ab5f9b82) | 2012 | 37,575 | Unverified | New |
| 267 |  | The Knife | [Pass This On](https://musicbrainz.org/recording/8eb06790-2cd6-4793-87f5-0d4f95acda28) | 2003 | 93,955 | Unverified | New |
| 268 |  | Death Cab for Cutie | [I Will Possess Your Heart](https://musicbrainz.org/recording/46fc7c5f-e5e2-46e5-8989-222ea7453f7e) | 2008 | 93,220 | Unverified | New |
| 269 |  | Miike Snow | [Devil’s Work](https://musicbrainz.org/recording/818bd437-1a7b-40bc-a4fa-b471cacebfe4) | 2011 | 36,988 | Unverified | New |
| 270 |  | Bombay Bicycle Club | [Bad Timing](https://musicbrainz.org/recording/47993054-8438-4519-b07c-8f1910ea81b2) | 2011 | 36,924 | Unverified | New |
| 271 |  | Tenacious D | [Fuck Her Gently](https://musicbrainz.org/recording/8d9c4da0-f615-4606-b12a-d9ec1fcbbd6b) | 2001 | 92,013 | Unverified | Already |
| 272 |  | Death Cab for Cutie | [Lightness](https://musicbrainz.org/recording/60d3363b-7cc4-4675-a85b-692683054ff2) | 2003 | 91,869 | Unverified | New |
| 273 |  | Scissor Sisters | [Fire With Fire](https://musicbrainz.org/recording/e4a98994-f610-4c61-8ff9-73cb98516615) | 2010 | 36,056 | Unverified | New |
| 274 |  | Ratatat | [Loud Pipes](https://musicbrainz.org/recording/69d8064a-1b6e-49af-933d-3e689b380af0) | 2006 | 90,292 | Unverified | New |
| 275 |  | How to Dress Well | [Ready for the World](https://musicbrainz.org/recording/ff353eca-627d-4e1e-84eb-f4da2fffea70) | 2010 | 35,943 | Unverified | Already |
| 276 |  | Battles | [Africastle](https://musicbrainz.org/recording/863b7e49-7a82-4fb5-a45b-3b9e506242b7) | 2011 | 35,906 | Unverified | New |
| 277 |  | Klaxons | [It’s Not Over Yet](https://musicbrainz.org/recording/087a2f12-9a5d-479c-9b21-ea549ad9497e) | 2007 | 89,850 | Unverified | New |
| 278 |  | Matt & Kim | [Daylight](https://musicbrainz.org/recording/ef1d24a7-177e-4784-b423-6cec2ef63548) | 2008 | 88,667 | Unverified | New |
| 279 |  | The Horrors | [Changing the Rain](https://musicbrainz.org/recording/2747b250-dbd1-49fc-a0f4-466ba1cb2576) | 2011 | 35,231 | Unverified | New |
| 280 |  | Broken Social Scene | [Anthems for a Seventeen Year‐Old Girl](https://musicbrainz.org/recording/12bdd6cc-0b5d-43d6-936f-caf18797141a) | 2002 | 88,160 | Unverified | New |
| 281 |  | Death Cab for Cutie | [No Sunlight](https://musicbrainz.org/recording/e77221ef-5081-41cc-96ce-c0f72c540d13) | 2008 | 86,888 | Unverified | New |
| 282 |  | Battles | [Futura](https://musicbrainz.org/recording/8015ccd2-8ce9-4e5f-a68e-51ab6c4a30f9) | 2011 | 34,418 | Unverified | New |
| 283 |  | Trent Reznor and Atticus Ross | [Hand Covers Bruise](https://musicbrainz.org/recording/bf79b95d-2752-4a98-bfaa-e30094790a6d) | 2010 | 34,267 | Unverified | New |
| 284 |  | Spoon | [The Way We Get By](https://musicbrainz.org/recording/1654ff85-f9fa-440a-bb32-112eea28e2fc) | 2002 | 85,699 | Unverified | New |
| 285 |  | The Kooks | [Always Where I Need to Be](https://musicbrainz.org/recording/ebc2fc14-0fc6-4e16-800e-e0bd9d5e7ac3) | 2008 | 85,019 | Unverified | Already |
| 286 |  | Trent Reznor and Atticus Ross | [In Motion](https://musicbrainz.org/recording/40e05adb-465a-49d5-8a77-d99c47dd5e70) | 2010 | 33,807 | Unverified | New |
| 287 |  | Girl Talk | [Oh No](https://musicbrainz.org/recording/0901c0ef-8719-4632-a37a-cf8e1de156c2) | 2010 | 33,806 | Unverified | New |
| 288 |  | Delorean | [Stay Close](https://musicbrainz.org/recording/b879954f-57f9-4640-97f4-a6fa84773179) | 2010 | 33,683 | Unverified | Already |
| 289 |  | Empire of the Sun | [Standing on the Shore](https://musicbrainz.org/recording/c6c6cc5d-1fe7-452d-a203-e36c5a0353a6) | 2008 | 84,169 | Unverified | New |
| 290 |  | The Moldy Peaches | [Anyone Else but You](https://musicbrainz.org/recording/a2453d3b-4468-4ef3-8ea8-f7e6a883a4a5) | 2001 | 83,599 | Unverified | New |
| 291 |  | DIIV | [(Druun)](https://musicbrainz.org/recording/0881253c-21c3-4814-b469-fa1f2cd1eebd) | 2012 | 33,280 | Unverified | New |
| 292 |  | Active Child | [Hanging On](https://musicbrainz.org/recording/3b1f5b8b-8ad6-4606-bc77-b61c396fb639) | 2011 | 33,243 | Unverified | Already |
| 293 |  | Doves | [There Goes the Fear](https://musicbrainz.org/recording/1edae9b3-2709-4e02-8a30-82ee3a1cbeb5) | 2002 | 83,497 | Unverified | New |
| 294 |  | Fever Ray | [Keep the Streets Empty for Me](https://musicbrainz.org/recording/f6e286e2-c99b-4608-bd5f-5901855a3cd1) | 2009 | 83,370 | Unverified | New |
| 295 |  | Neon Indian | [Fallout](https://musicbrainz.org/recording/b7229549-b306-4fb1-8b11-f23980dee9d8) | 2011 | 33,054 | Unverified | New |
| 296 |  | Cut Copy | [Hearts on Fire](https://musicbrainz.org/recording/1f5a338f-f8ca-4ef1-bc7b-5aaa2a13396e) | 2008 | 82,616 | Unverified | New |
| 297 |  | DIIV | [Past Lives](https://musicbrainz.org/recording/5d91cc38-4215-4ea1-98ec-82a8b762a4ed) | 2012 | 32,818 | Unverified | New |
| 298 |  | Gil Scott‐Heron and Jamie xx | [NY Is Killing Me](https://musicbrainz.org/recording/dc0a56ce-15e8-4bfa-ab75-06026172b822) | 2010 | 32,596 | Unverified | New |
| 299 |  | Salem | [King Night](https://musicbrainz.org/recording/58647ff6-caf7-48c4-93de-67553d6c4a4a) | 2010 | 32,561 | Unverified | New |
| 300 |  | Ariel Pink’s Haunted Graffiti | [Fright Night (Nevermore)](https://musicbrainz.org/recording/70af6315-865b-4238-8a13-aa31c1fb81c1) | 2010 | 32,058 | Unverified | New |
| 301 |  | Tycho | [Daydream](https://musicbrainz.org/recording/1e733373-3daf-42c8-9272-e7f1fa96c0fc) | 2011 | 32,026 | Unverified | New |
| 302 |  | The Bravery | [An Honest Mistake](https://musicbrainz.org/recording/adc1a7d3-7054-4912-86a6-4e61fac5be3a) | 2005 | 80,332 | Unverified | New |
| 303 |  | Apparat | [Black Water](https://musicbrainz.org/recording/5e6a1263-9d5d-48e7-a668-433e4f89e7e3) | 2011 | 31,909 | Unverified | New |
| 304 |  | Girl Talk | [Let It Out](https://musicbrainz.org/recording/263fed60-34b6-478b-9c34-37190e177c7e) | 2010 | 31,879 | Unverified | Already |
| 305 |  | Digitalism | [Blitz](https://musicbrainz.org/recording/db9b7e9c-1cbe-40ce-b6d0-9c3be4b769f5) | 2010 | 31,749 | Unverified | New |
| 306 |  | Fever Ray | [Seven](https://musicbrainz.org/recording/57788eb8-c221-4ca0-b0b0-2fe7da11de23) | 2009 | 78,694 | Unverified | New |
| 307 |  | Architecture in Helsinki | [Contact High](https://musicbrainz.org/recording/7b34c333-89ff-43f0-9ba3-c3ef14e87ece) | 2011 | 30,950 | Unverified | New |
| 308 |  | Empire of the Sun | [Half Mast](https://musicbrainz.org/recording/7560a276-05b4-4333-ae0a-f631b13011f7) | 2008 | 77,730 | Unverified | New |
| 309 |  | DIIV | [Human](https://musicbrainz.org/recording/2edb74e3-92d2-4240-a7b4-c85cc8a03f16) | 2012 | 30,901 | Unverified | New |
| 310 |  | Battles | [Inchworm](https://musicbrainz.org/recording/5c835831-c066-42c4-bcbe-9a15b15fac64) | 2011 | 30,861 | Unverified | New |
| 311 |  | Holy Fuck feat. Angus Andrew | [Deleters](https://musicbrainz.org/recording/109a3cdf-9cc6-41fa-a7e3-d80d0db56779) | 2020 | 1,225 | Unverified | New |
| 312 |  | Architecture in Helsinki | [Escapee](https://musicbrainz.org/recording/859fb6f0-b541-4df3-adc5-6baa047c27a2) | 2011 | 30,730 | Unverified | New |
| 313 |  | Trent Reznor and Atticus Ross | [Pieces Form the Whole](https://musicbrainz.org/recording/b69c931f-b48c-4584-90cc-7fa7fd8c6d03) | 2010 | 30,651 | Unverified | New |
| 314 |  | Tenacious D | [Wonderboy](https://musicbrainz.org/recording/0dd6bfb1-7856-4607-bed9-5adaec850d71) | 2001 | 76,140 | Unverified | New |
| 315 |  | Digitalism | [Circles](https://musicbrainz.org/recording/fe22a33c-422e-4ff8-b13e-4731c8cab023) | 2011 | 30,262 | Unverified | New |
| 316 |  | Jamie xx | [Far Nearer](https://musicbrainz.org/recording/10c1c126-a79d-4e45-8012-351410863401) | 2011 | 30,167 | Unverified | New |
| 317 |  | Girl Talk | [That’s Right](https://musicbrainz.org/recording/0611d601-4e11-4e17-b36e-ed523468090a) | 2010 | 30,081 | Unverified | New |
| 318 |  | Digitalism | [Pogo](https://musicbrainz.org/recording/95d15dc9-9bd8-4273-8140-6cc4f94ba2c7) | 2007 | 75,540 | Unverified | New |
| 319 |  | Tycho | [Dive](https://musicbrainz.org/recording/f35804dc-4fbc-407f-9e97-3d27c32eab5b) | 2011 | 30,059 | Unverified | New |
| 320 |  | Bat for Lashes | [What’s a Girl to Do?](https://musicbrainz.org/recording/86ede2e5-8203-4d99-ad90-eb107f7fe620) | 2006 | 75,415 | Unverified | New |
| 321 |  | Ladytron | [Destroy Everything You Touch](https://musicbrainz.org/recording/067e8d88-5188-4fd2-8c2e-d3439c82152f) | 2005 | 75,373 | Unverified | New |
| 322 |  | Dan Deacon | [Become a Mountain](https://musicbrainz.org/recording/5a4b4219-afba-46ec-868b-c6e4fdfcab07) | 2020 | 1,193 | Unverified | New |
| 323 |  | Girl Talk | [Jump on Stage](https://musicbrainz.org/recording/78fc505a-5bfe-4136-98f3-bb6a50e7b6b9) | 2010 | 29,889 | Unverified | New |
| 324 |  | The Coral | [Dreaming of You](https://musicbrainz.org/recording/31474bde-a7e1-470b-af93-fc560a4d63bc) | 2002 | 74,977 | Unverified | New |
| 325 |  | Air | [Venus](https://musicbrainz.org/recording/f703d7dd-ba12-48dc-a54b-cb0d71a3910e) | 2004 | 74,332 | Unverified | New |
| 326 |  | The Dandy Warhols | [We Used to Be Friends](https://musicbrainz.org/recording/b81b0aba-49c4-45ae-abc3-29d44744a8ba) | 2003 | 74,116 | Unverified | New |
| 327 |  | M.I.A. | [Boyz](https://musicbrainz.org/recording/e161a616-c022-4782-b87c-86c8e846cd05) | 2007 | 74,101 | Unverified | Already |
| 328 |  | Air | [Run](https://musicbrainz.org/recording/09cb1175-4f16-4e0e-b389-4b1b37d9118f) | 2004 | 74,088 | Unverified | New |
| 329 |  | Spoon | [The Underdog](https://musicbrainz.org/recording/0201b1b1-82d5-472d-8fa7-5b84c42b20cb) | 2007 | 73,827 | Unverified | New |
| 330 |  | The Horrors | [I Can See Through You](https://musicbrainz.org/recording/9b58b799-8181-4850-a915-020d3cd0e7ca) | 2011 | 29,379 | Unverified | New |
| 331 |  | M.I.A. | [Jimmy](https://musicbrainz.org/recording/9e070507-16bc-417a-8689-f6b6050cb9e8) | 2007 | 73,528 | Unverified | New |
| 332 |  | The Knife | [Neverland](https://musicbrainz.org/recording/5eb6ecca-2e04-4dcb-92ce-9ff82c54abf0) | 2006 | 73,334 | Unverified | New |
| 333 |  | Cut Copy | [Feel the Love](https://musicbrainz.org/recording/94dead8b-ce5f-4cf2-90d0-e9426e4d88bb) | 2008 | 72,916 | Unverified | Already |
| 334 |  | Delorean | [Real Love](https://musicbrainz.org/recording/577daf64-3380-4ebe-82c2-32e41ddb4f18) | 2010 | 28,993 | Unverified | New |
| 335 |  | Trent Reznor and Atticus Ross | [A Familiar Taste](https://musicbrainz.org/recording/5b2fb051-484e-400d-a098-4ca564fae299) | 2010 | 28,867 | Unverified | New |
| 336 |  | Cliff Martinez | [Rubber Head](https://musicbrainz.org/recording/2e0b540c-2866-48ad-bfde-687f373b4b46) | 2011 | 28,785 | Unverified | New |
| 337 |  | The Horrors | [You Said](https://musicbrainz.org/recording/988fdb39-19da-4f6f-932c-b77e17d51190) | 2011 | 28,732 | Unverified | New |
| 338 |  | Gil Scott‐Heron and Jamie xx | [Running](https://musicbrainz.org/recording/0abb065f-af93-4e97-b937-a03a0df63740) | 2011 | 28,722 | Unverified | New |
| 339 |  | Matt and Kim | [Cameras](https://musicbrainz.org/recording/3a270d40-3365-47f0-85e8-a5c4c9accbc4) | 2010 | 28,593 | Unverified | New |
| 340 |  | Yann Tiersen | [La Valse d’Amélie](https://musicbrainz.org/recording/70e1f203-f7f8-4bbb-beae-a4ee72a2bd2d) | 2001 | 71,573 | Unverified | New |
| 341 |  | DIIV | [Air Conditioning](https://musicbrainz.org/recording/3dd62a3a-b403-4ac9-a85a-bb7d3ef1c7c8) | 2012 | 28,468 | Unverified | New |
| 342 |  | Oh Land | [White Nights](https://musicbrainz.org/recording/f9c0e2ef-4f53-4b9d-b2ed-ea34790810f2) | 2011 | 28,440 | Unverified | New |
| 343 |  | Cliff Martinez | [I Drive](https://musicbrainz.org/recording/86cf7eec-7623-4e41-84cb-0b130930834f) | 2011 | 28,437 | Unverified | New |
| 344 |  | CAKE | [Short Skirt/Long Jacket](https://musicbrainz.org/recording/96d80e5a-9055-432e-b3c2-f9180adab3c9) | 2001 | 71,403 | Unverified | New |
| 345 |  | Yann Tiersen | [Le Moulin](https://musicbrainz.org/recording/d6fd86a4-2f45-4b35-bebc-2361d87b0b33) | 2001 | 71,031 | Unverified | New |
| 346 |  | Clap Your Hands Say Yeah | [The Skin of My Yellow Country Teeth](https://musicbrainz.org/recording/ffc9d3fd-8153-4ccf-b6e9-06d9f5df72b2) | 2005 | 70,860 | Unverified | New |
| 347 |  | Oh Land | [Wolf & I](https://musicbrainz.org/recording/6d897ff0-4dcf-4554-9b0b-c175a515430d) | 2011 | 28,160 | Unverified | New |
| 348 |  | Metric | [Sick Muse](https://musicbrainz.org/recording/c0d01e0d-c2b2-4b4c-aef1-b8f486c297ec) | 2009 | 70,642 | Unverified | New |
| 349 |  | Ariel Pink’s Haunted Graffiti | [Only in My Dreams](https://musicbrainz.org/recording/3e44a36f-5c97-44c4-9d62-a180e36fc65f) | 2012 | 28,042 | Unverified | Already |
| 350 |  | Twin Shadow | [Golden Light](https://musicbrainz.org/recording/27107b32-1a10-4d24-bd83-2bb93f9f6ec1) | 2012 | 27,977 | Unverified | New |
| 351 |  | Battles | [Dominican Fade](https://musicbrainz.org/recording/9936ae9f-0134-42a9-a8a8-60914edae94e) | 2011 | 27,826 | Unverified | New |
| 352 |  | jj | [Let Go](https://musicbrainz.org/recording/f9d2bb02-8ef8-4e58-88c1-7aa0e8658675) | 2010 | 27,800 | Unverified | New |
| 353 |  | Fang Island | [Daisy](https://musicbrainz.org/recording/f9f8d314-4a3b-4eff-a80e-593b2fd3fe60) | 2010 | 27,505 | Unverified | New |
| 354 |  | Neon Indian | [Deadbeat Summer](https://musicbrainz.org/recording/50609d39-d6be-4923-94cb-80923e99ba54) | 2009 | 68,927 | Unverified | New |
| 355 |  | Ariel Pink’s Haunted Graffiti | [Menopause Man](https://musicbrainz.org/recording/254d7f61-b0f6-4405-80fb-e2222cb3883e) | 2010 | 27,426 | Unverified | New |
| 356 |  | Justice | [New Lands](https://musicbrainz.org/recording/025c4072-c5ec-4167-8b3e-9fa8cd4ad32f) | 2011 | 27,269 | Unverified | Already |
| 357 |  | Gang Gang Dance | [Glass Jar](https://musicbrainz.org/recording/0ad5e60f-9cf7-4a84-9736-12f6e18c4f72) | 2011 | 27,241 | Unverified | New |
| 358 |  | Gil Scott‐Heron and Jamie xx | [Home](https://musicbrainz.org/recording/d39534da-f4c0-45d0-8a35-bccdd030ffe2) | 2011 | 27,104 | Unverified | New |
| 359 |  | Chairlift | [Bruises](https://musicbrainz.org/recording/d502ef8f-2d4e-49a7-8576-3cef44d06d0a) | 2008 | 68,072 | Unverified | New |
| 360 |  | YELLE | [Safari Disco Club](https://musicbrainz.org/recording/1781938b-4510-45d6-b3db-fac49d045104) | 2011 | 27,093 | Unverified | New |
| 361 |  | The Chemical Brothers | [Star Guitar](https://musicbrainz.org/recording/93411521-d7b4-4c87-9bce-a4ba5e6b95fa) | 2002 | 68,013 | Unverified | Already |
| 362 |  | Future Islands | [Balance](https://musicbrainz.org/recording/6c32db0a-5d54-4a11-93e4-fdf1aa43184c) | 2011 | 26,963 | Unverified | New |
| 363 |  | Starfucker | [Bury Us Alive](https://musicbrainz.org/recording/770a2a6e-e97a-4a8b-9d29-c7d36343f943) | 2011 | 26,899 | Unverified | New |
| 364 |  | Apparat | [Song of Los](https://musicbrainz.org/recording/b3b6c47b-2823-450c-a5c6-f72bcc9437c1) | 2011 | 26,714 | Unverified | New |
| 365 |  | CSS | [Alala](https://musicbrainz.org/recording/b2038f2c-08ba-44d7-a620-e2f7fdd4e11b) | 2005 | 66,996 | Unverified | New |
| 366 |  | Yann Tiersen | [L’Autre Valse d’Amélie](https://musicbrainz.org/recording/19a07892-30f3-4102-80e8-e2a516910609) | 2001 | 66,509 | Unverified | Already |
| 367 |  | Zola Jesus | [Vessel](https://musicbrainz.org/recording/e1fe70c2-4484-4248-8b00-ba7c56dcec2d) | 2011 | 26,441 | Unverified | New |
| 368 |  | HAIM | [Forever](https://musicbrainz.org/recording/76cb0082-e0e8-4b36-a4b5-af9825a4d6bf) | 2012 | 26,395 | Unverified | New |
| 369 |  | The Chemical Brothers | [Galvanize](https://musicbrainz.org/recording/bac8e50d-d899-4518-9268-b2a8b384eb92) | 2004 | 66,002 | Unverified | New |
| 370 |  | The Flaming Lips | [Ego Tripping at the Gates of Hell](https://musicbrainz.org/recording/591821c9-f231-4988-b1f5-2ffe2cd23350) | 2002 | 65,840 | Unverified | New |
| 371 |  | Bat for Lashes | [Horse and I](https://musicbrainz.org/recording/e4a30c3a-c4db-450c-b8ae-220f59e12e4b) | 2006 | 65,517 | Unverified | New |
| 372 |  | Gogol Bordello | [Start Wearing Purple](https://musicbrainz.org/recording/8230efe0-df43-4599-956f-74f08a6bc747) | 2005 | 65,405 | Unverified | New |
| 373 |  | Yann Tiersen | [La Valse des vieux os](https://musicbrainz.org/recording/1dbbd8fc-3f22-4bae-8e0e-0e5a67625943) | 2001 | 65,400 | Unverified | New |
| 374 |  | Cliff Martinez | [He Had a Good Time](https://musicbrainz.org/recording/c9d1b697-89ca-4e55-b902-0c00678f59ea) | 2011 | 25,963 | Unverified | New |
| 375 |  | Cliff Martinez | [They Broke His Pelvis](https://musicbrainz.org/recording/5cac564d-ea75-4181-a0b9-c7738d4984ab) | 2011 | 25,813 | Unverified | New |
| 376 |  | El Guincho | [Bombay](https://musicbrainz.org/recording/66c3c25c-3e96-4865-8290-5891a115a311) | 2010 | 25,771 | Unverified | New |
| 377 |  | Gang Gang Dance | [MindKilla](https://musicbrainz.org/recording/090cb370-d00d-4147-bfc7-1a05560a5d1a) | 2011 | 25,538 | Unverified | New |
| 378 |  | Gil Scott‐Heron and Jamie xx | [My Cloud](https://musicbrainz.org/recording/38f5f878-426d-4abe-84ea-7fc313b429ee) | 2011 | 25,533 | Unverified | New |
| 379 |  | Metric | [Satellite Mind](https://musicbrainz.org/recording/9a1279f7-0725-4da2-af82-178a264318dc) | 2009 | 63,734 | Unverified | New |
| 380 |  | Peter Bjorn and John | [Amsterdam](https://musicbrainz.org/recording/d1c5e945-1b94-432e-b78f-2170d8b5aac5) | 2006 | 63,719 | Unverified | New |
| 381 |  | Cut Copy | [Out There on the Ice](https://musicbrainz.org/recording/8bcff9d0-1960-4613-b356-ca406d036898) | 2008 | 63,672 | Unverified | New |
| 382 |  | Holy Ghost! | [Do It Again](https://musicbrainz.org/recording/792878d8-73b3-475f-9e14-348048abc4be) | 2011 | 25,087 | Unverified | New |
| 383 |  | Kavinsky | [Grand Canyon](https://musicbrainz.org/recording/5b86f058-3931-4233-a8a9-3bac314506e2) | 2013 | 24,985 | Unverified | New |
| 384 |  | Apparat | [Sweet Unrest](https://musicbrainz.org/recording/4dda2de4-bf5a-4177-92bd-39cdc8c0d7e0) | 2011 | 24,900 | Unverified | New |
| 385 |  | ceo | [Come With Me](https://musicbrainz.org/recording/69a7315d-7e07-4603-bc86-46711552e61f) | 2010 | 24,573 | Unverified | Already |
| 386 |  | Clap Your Hands Say Yeah | [Over and Over Again (Lost and Found)](https://musicbrainz.org/recording/5739db14-3b37-4e33-af55-994e8a4e2197) | 2005 | 61,717 | Unverified | New |
| 387 |  | Tenacious D | [Kielbasa](https://musicbrainz.org/recording/abf3df98-5e97-49b8-97a8-ac710145dc88) | 2001 | 61,521 | Unverified | New |
| 388 |  | The Flaming Lips | [It’s Summertime](https://musicbrainz.org/recording/1e071206-f21b-4917-a926-52091a8d1a02) | 2002 | 61,414 | Unverified | New |
| 389 |  | Oh Land | [Perfection](https://musicbrainz.org/recording/ec8e5f38-0722-43ae-9b63-fc5420953041) | 2011 | 24,410 | Unverified | New |
| 390 |  | John Maus | [Hey Moon](https://musicbrainz.org/recording/bd5b09d5-f8a6-4ee7-8ea9-d94c736e1126) | 2011 | 24,302 | Unverified | New |
| 391 |  | Starfucker | [Julius](https://musicbrainz.org/recording/e850b2e3-b01d-4b8b-961d-a3a125d62b0e) | 2011 | 24,215 | Unverified | New |
| 392 |  | Simian Mobile Disco | [I Believe](https://musicbrainz.org/recording/7a1837e6-d7ee-4b51-8be4-4e70d84793b3) | 2007 | 60,813 | Unverified | New |
| 393 |  | Scissor Sisters | [Any Which Way](https://musicbrainz.org/recording/afb7a32d-1c3a-47a8-b106-820a4337bca0) | 2010 | 24,123 | Unverified | Already |
| 394 |  | Patrick Wolf | [The City](https://musicbrainz.org/recording/37b4c4ea-691f-4d73-a8d6-8d901f334f50) | 2011 | 24,075 | Unverified | New |
| 395 |  | The Lonely Island | [Jizz in My Pants](https://musicbrainz.org/recording/e8faf732-01e9-4b6a-8873-65911b38ca6f) | 2008 | 60,207 | Unverified | New |
| 396 |  | John Maus | [Believer](https://musicbrainz.org/recording/26466cf3-4e94-4fb9-9511-2271104d1ec6) | 2011 | 23,908 | Unverified | New |
| 397 |  | Nouvelle Vague | [In a Manner of Speaking](https://musicbrainz.org/recording/f205db8c-505d-456a-bc78-f43609a8cb2e) | 2004 | 60,025 | Unverified | New |
| 398 |  | Electric Six | [Gay Bar](https://musicbrainz.org/recording/fdfe742a-cf4d-45a8-b094-855b5a94340a) | 2003 | 59,861 | Unverified | New |
| 399 |  | Holy Ghost! | [Say My Name](https://musicbrainz.org/recording/2b549ff2-8221-475a-9c74-331b967acaa6) | 2011 | 23,770 | Unverified | New |
| 400 |  | Neon Indian | [Future Sick](https://musicbrainz.org/recording/c7d7b0bc-5406-41b3-8dc1-0aa10c04d1ca) | 2011 | 23,742 | Unverified | Already |
| 401 |  | Bat for Lashes | [Prescilla](https://musicbrainz.org/recording/9bd0c316-b553-4eaa-86ad-e145633870d5) | 2006 | 59,228 | Unverified | New |
| 402 |  | The Walkmen | [The Rat](https://musicbrainz.org/recording/73b4af05-80ff-439d-bfa4-91255d3c681a) | 2004 | 59,223 | Unverified | New |
| 403 |  | Nouvelle Vague | [Love Will Tear Us Apart](https://musicbrainz.org/recording/04dbb940-6f46-4298-8c82-e3bda2cdeacb) | 2004 | 58,670 | Unverified | New |
| 404 |  | Future Islands | [Tin Man](https://musicbrainz.org/recording/d3d45dac-b4c2-4448-8c10-fbdfdce325a5) | 2010 | 23,270 | Unverified | New |
| 405 |  | Clap Your Hands Say Yeah | [Is This Love?](https://musicbrainz.org/recording/29e0acbe-5dae-4a4c-a7fa-3eb8a8741d61) | 2005 | 58,421 | Unverified | New |
| 406 |  | Bat for Lashes | [Trophy](https://musicbrainz.org/recording/6d011598-b272-4923-9bbf-3a2bf413dc67) | 2006 | 58,389 | Unverified | New |
| 407 |  | Apparat | [Candil de la calle](https://musicbrainz.org/recording/0bbcb38c-d8d6-453f-8f64-7f8cfa55257d) | 2011 | 23,181 | Unverified | New |
| 408 |  | Architecture in Helsinki | [Do the Whirlwind](https://musicbrainz.org/recording/efcf0862-9628-48d8-9d77-01ea1563e1a4) | 2004 | 58,220 | Unverified | New |
| 409 |  | Deerhunter | [Never Stops](https://musicbrainz.org/recording/cd00e155-f0c1-442e-b2a3-e5cc0ea6bc83) | 2008 | 58,013 | Unverified | New |
| 410 |  | Spoon | [You Got Yr. Cherry Bomb](https://musicbrainz.org/recording/4b25128d-4280-4f7f-9ea4-30206d6606b6) | 2007 | 57,805 | Unverified | New |
| 411 |  | Is Tropical | [The Greeks](https://musicbrainz.org/recording/c008efef-1a9c-4f6c-b152-1e5ef6ad13be) | 2011 | 22,986 | Unverified | New |
| 412 |  | John Talabot | [Depak Ine](https://musicbrainz.org/recording/8fe08993-7f4a-468d-b99f-4368b9567895) | 2012 | 22,885 | Unverified | New |
| 413 |  | jj | [My Life](https://musicbrainz.org/recording/ff4520e8-57e4-43fb-b644-acb5ccb586fb) | 2010 | 22,853 | Unverified | New |
| 414 |  | múm | [Green Grass of Tunnel](https://musicbrainz.org/recording/74fa9d38-398c-4209-816c-073ebe395d67) | 2002 | 57,096 | Unverified | New |
| 415 |  | Clap Your Hands Say Yeah | [Let the Cool Goddess Rust Away](https://musicbrainz.org/recording/43e221da-08a3-4443-b3cd-f566322a65c1) | 2005 | 57,089 | Unverified | New |
| 416 |  | Scissor Sisters | [Invisible Light](https://musicbrainz.org/recording/ea3406f1-679b-4429-b57e-dd21bf5896cb) | 2010 | 22,590 | Unverified | Already |
| 417 |  | Blood Orange | [Sutphin Boulevard](https://musicbrainz.org/recording/59d8f6e7-cc3a-494f-8fe1-eb8cb00e49cf) | 2011 | 22,393 | Unverified | New |
| 418 |  | Holy Ghost! | [Wait and See](https://musicbrainz.org/recording/2f0a74d3-e4df-4c21-b32f-ab907cd91717) | 2011 | 22,380 | Unverified | New |
| 419 |  | Elbow | [Grounds for Divorce](https://musicbrainz.org/recording/e32f730d-8950-44ca-8709-0e99893e28c7) | 2001 | 55,944 | Unverified | New |
| 420 |  | Amon Tobin | [Journeyman](https://musicbrainz.org/recording/e8dfe81f-80c7-4768-b801-8b5d74043d91) | 2011 | 22,231 | Unverified | New |
| 421 |  | Ladytron | [Seventeen](https://musicbrainz.org/recording/77c78737-7712-45eb-831e-ba36f1e2b524) | 2002 | 55,696 | Unverified | New |
| 422 |  | Blonde Redhead | [23](https://musicbrainz.org/recording/8efe590a-0db0-4336-b711-b235851d1144) | 2007 | 55,483 | Unverified | New |
| 423 |  | Black Rebel Motorcycle Club | [Spread Your Love](https://musicbrainz.org/recording/8d555b93-a5d8-4959-b3e1-c50bcd27fabc) | 2001 | 55,481 | Unverified | New |
| 424 |  | Goldfrapp | [Happiness](https://musicbrainz.org/recording/c6a410f1-7f25-4c50-9977-616f3fc1caa8) | 2008 | 55,394 | Unverified | New |
| 425 |  | The Lonely Island | [Like a Boss](https://musicbrainz.org/recording/ababcf6c-224a-466b-8a9e-5cc2038e1a0c) | 2009 | 55,340 | Unverified | New |
| 426 |  | CSS | [Let’s Make Love and Listen to Death From Above](https://musicbrainz.org/recording/a020c468-e6fc-43bb-b30f-00264f73c015) | 2005 | 54,951 | Unverified | New |
| 427 |  | Spoon | [Don’t You Evah](https://musicbrainz.org/recording/1027ed7e-6512-4655-a676-32fd12357c7f) | 2007 | 54,773 | Unverified | New |
| 428 |  | Goldfrapp | [Ride a White Horse](https://musicbrainz.org/recording/67e5c5e3-a77b-4768-805c-030fb31bcda6) | 2005 | 54,410 | Unverified | New |
| 429 |  | John Maus | [Quantum Leap](https://musicbrainz.org/recording/0f35b62e-77df-4568-9f46-a2be86ba53ba) | 2011 | 21,577 | Unverified | New |
| 430 |  | Cat Power | [Werewolf](https://musicbrainz.org/recording/c71f5199-e16a-4c6c-98b7-9a941a4a6542) | 2003 | 53,807 | Unverified | Already |
| 431 |  | Gang Gang Dance | [Adult Goth](https://musicbrainz.org/recording/294ba331-1f2f-45af-b7d7-f13947b196f0) | 2011 | 21,402 | Unverified | New |
| 432 |  | Zero 7 | [I Have Seen](https://musicbrainz.org/recording/7f65d430-6636-4a6a-902d-3c84a7248407) | 2001 | 53,361 | Unverified | Already |
| 433 |  | Nouvelle Vague | [Too Drunk to Fuck](https://musicbrainz.org/recording/3fae541d-e7fc-414c-bcf9-ea01f8f54108) | 2004 | 52,766 | Unverified | New |
| 434 |  | Zola Jesus | [Avalanche](https://musicbrainz.org/recording/a159b00e-9129-4b9c-9d15-6e238e9e96de) | 2011 | 21,003 | Unverified | New |
| 435 |  | Com Truise | [VHS Sex](https://musicbrainz.org/recording/d4b83b80-0239-4e94-884e-e88096db9eca) | 2011 | 20,817 | Unverified | New |
| 436 |  | John Talabot | [Oro y sangre](https://musicbrainz.org/recording/9a022516-73f1-4362-995e-67ff01831eea) | 2012 | 20,722 | Unverified | New |
| 437 |  | Electric Six | [Danger! High Voltage](https://musicbrainz.org/recording/790fc70a-ceab-4faa-a2a6-7599cb5a3e6e) | 2003 | 51,686 | Unverified | New |
| 438 |  | John Talabot | [El oeste](https://musicbrainz.org/recording/eb5e0203-1e99-402d-9cea-c23c21cc6aba) | 2012 | 20,553 | Unverified | New |
| 439 |  | Black Rebel Motorcycle Club | [Love Burns](https://musicbrainz.org/recording/125ddb15-c87b-45ae-b374-ec885f2320a5) | 2001 | 51,566 | Unverified | New |
| 440 |  | Crumb | [Ghostride](https://musicbrainz.org/recording/9b792b2a-df4d-407e-aa19-532c4b9e0c81) | 2019 | 5,119 | Unverified | New |
| 441 |  | Little Boots | [Stuck on Repeat](https://musicbrainz.org/recording/10a92ad0-20a8-48ed-a780-99757bd66cc5) | 2008 | 51,148 | Unverified | New |
| 442 |  | Peter Bjorn and John | [Objects of My Affection](https://musicbrainz.org/recording/d14ec570-83e0-474b-ae60-453addc16525) | 2006 | 51,123 | Unverified | New |
| 443 |  | Future Islands | [Before the Bridge](https://musicbrainz.org/recording/c530f382-7a04-4a21-8627-280b7ce9d6f4) | 2011 | 20,311 | Unverified | New |
| 444 |  | Bibio | [Take Off Your Shirt](https://musicbrainz.org/recording/93cf9c4b-6dfe-48d7-bbf7-a2adb1f8b9fb) | 2010 | 20,287 | Unverified | New |
| 445 |  | Small Black | [Photojournalist](https://musicbrainz.org/recording/f912c902-821b-482f-ad6a-9a64088f1a53) | 2010 | 20,263 | Unverified | New |
| 446 |  | Simian Mobile Disco | [Hustler](https://musicbrainz.org/recording/ae13eeb9-2e0d-4683-a191-26afa18e1953) | 2007 | 50,876 | Unverified | New |
| 447 |  | John Maus | [Streetlight](https://musicbrainz.org/recording/820316d9-18ae-416c-ac22-23b47c0ed965) | 2011 | 20,207 | Unverified | New |
| 448 |  | CHVRCHES | [Recover](https://musicbrainz.org/recording/68d4e448-175b-4e3e-8976-52ea5fe70479) | 2013 | 20,199 | Unverified | New |
| 449 |  | Peter Bjorn and John | [Up Against the Wall](https://musicbrainz.org/recording/fd916914-44dd-41af-b969-b12628bf60c7) | 2006 | 50,685 | Unverified | New |
| 450 |  | Elbow | [One Day Like This](https://musicbrainz.org/recording/626a77c0-6fb4-42f9-9448-5d4d144ee5fe) | 2008 | 50,564 | Unverified | New |
| 451 |  | Cat Power | [Free](https://musicbrainz.org/recording/908af1de-35f5-4a78-8eb0-2e296a86c5ae) | 2003 | 50,462 | Unverified | New |
| 452 |  | Delorean | [Endless Sunset](https://musicbrainz.org/recording/c141c04a-3d4b-45a6-9dcd-503eb610e8a8) | 2010 | 19,875 | Unverified | New |
| 453 |  | Patrick Wolf | [The Magic Position](https://musicbrainz.org/recording/6025ab62-b934-4f37-b6d6-e44a515f7d18) | 2007 | 49,863 | Unverified | New |
| 454 |  | Aqualung | [Brighter Than Sunshine](https://musicbrainz.org/recording/3685eeb2-a3f3-44c8-8802-b9a271847e39) | 2003 | 49,396 | Unverified | New |
| 455 |  | Com Truise | [Cathode Girls](https://musicbrainz.org/recording/98e05067-385b-4ed7-a227-df5455edc1ea) | 2011 | 19,625 | Unverified | New |
| 456 |  | Jamie xx featuring Romy | [Loud Places](https://musicbrainz.org/recording/0d47d151-b206-438b-8aba-11984f031614) | 2015 | 4,923 | Unverified | New |
| 457 |  | Kavinsky | [ProtoVision](https://musicbrainz.org/recording/6785c107-a6dd-4bdc-a11b-3705230f3855) | 2012 | 19,593 | Unverified | New |
| 458 |  | Zola Jesus | [Seekir](https://musicbrainz.org/recording/5f71df71-9a75-4f5d-a7ef-b06bfb1a8c91) | 2011 | 19,562 | Unverified | New |
| 459 |  | Nouvelle Vague | [I Melt With You](https://musicbrainz.org/recording/f0e4adae-6c2a-437a-9b43-4cbba23eda70) | 2004 | 49,093 | Unverified | New |
| 460 |  | Cat Power | [He War](https://musicbrainz.org/recording/1601c29b-7753-4b75-afd0-d1c12d249d68) | 2003 | 48,907 | Unverified | New |
| 461 |  | The Chemical Brothers | [Saturate](https://musicbrainz.org/recording/9559e30a-efed-476d-9b86-1fa6dd52d940) | 2007 | 48,887 | Unverified | New |
| 462 |  | The Chemical Brothers | [Believe](https://musicbrainz.org/recording/6db56e37-00ff-4a9f-9ced-7b5b8655447e) | 2004 | 48,878 | Unverified | Already |
| 463 |  | Cat Power | [I Don’t Blame You](https://musicbrainz.org/recording/36867bd1-6348-4733-8763-683216c19ae2) | 2003 | 48,704 | Unverified | New |
| 464 |  | Delorean | [Grow](https://musicbrainz.org/recording/e573f583-4979-4a7b-8d0a-cb34f23d4c1e) | 2010 | 19,387 | Unverified | New |
| 465 |  | The Go! Team | [Huddle Formation](https://musicbrainz.org/recording/cb985c64-f3a4-461a-a286-f20a9a82f1a9) | 2004 | 48,689 | Unverified | New |
| 466 |  | Blackbird Blackbird | [Sunspray](https://musicbrainz.org/recording/4e652c71-c9e1-455e-83fc-f453b0a56f75) | 2010 | 19,316 | Unverified | Already |
| 467 |  | Architecture in Helsinki | [Heart It Races](https://musicbrainz.org/recording/a9c3f225-9a2a-478b-89f7-2c6e2d900688) | 2007 | 48,381 | Unverified | New |
| 468 |  | Zola Jesus | [Hikikomori](https://musicbrainz.org/recording/c3e6340f-b41b-44fe-91ab-4b2d9fe1d39d) | 2011 | 19,243 | Unverified | New |
| 469 |  | Gang Gang Dance | [Chinese High](https://musicbrainz.org/recording/f74b4843-a1f2-4c80-8f7c-ce4032a541e9) | 2011 | 19,202 | Unverified | New |
| 470 |  | Goldfrapp | [Number 1](https://musicbrainz.org/recording/7764fa5d-ebb1-4664-ab57-2b5233c07bab) | 2005 | 47,894 | Unverified | New |
| 471 |  | Flight of the Conchords | [Business Time](https://musicbrainz.org/recording/0ce88e6d-910e-437b-ba2e-97651d3f893f) | 2007 | 47,825 | Unverified | Already |
| 472 |  | The Flaming Lips | [Are You a Hypnotist??](https://musicbrainz.org/recording/8f61c330-79e0-4340-833b-4edb7703ed84) | 2002 | 47,449 | Unverified | New |
| 473 |  | Everything Everything | [Cough Cough](https://musicbrainz.org/recording/73e97624-436b-420e-b98a-c50111567375) | 2012 | 18,848 | Unverified | New |
| 474 |  | Joanna Newsom | [Sprout and the Bean](https://musicbrainz.org/recording/61f96993-e00f-4701-8bdc-902040b184da) | 2004 | 46,950 | Unverified | New |
| 475 |  | The Go! Team | [Ladyflash](https://musicbrainz.org/recording/87a72a5a-0d2f-43a8-9b1a-bf8154d6fdfa) | 2004 | 46,920 | Unverified | New |
| 476 |  | John Talabot | [Last Land](https://musicbrainz.org/recording/af2256bc-b954-4ec3-8569-131a6acf998e) | 2012 | 18,588 | Unverified | New |
| 477 |  | Com Truise | [Terminal](https://musicbrainz.org/recording/656aff2f-f35c-4eb9-a25a-493d1499b6a8) | 2011 | 18,581 | Unverified | Already |
| 478 |  | Porcelain Raft | [Unless You Speak From Your Heart](https://musicbrainz.org/recording/253593eb-a4a0-43d4-8285-c2ef00acb7c9) | 2012 | 18,571 | Unverified | New |
| 479 |  | Amon Tobin | [Piece of Paper](https://musicbrainz.org/recording/36e07314-d365-466a-aec4-d7b188edc7a5) | 2011 | 18,506 | Unverified | New |
| 480 |  | Danger Mouse & Daniele Luppi | [The Matador Has Fallen](https://musicbrainz.org/recording/10cbc6bd-c3e1-4255-921c-af8718dac4f7) | 2011 | 18,482 | Unverified | New |
| 481 |  | Com Truise | [Brokendate](https://musicbrainz.org/recording/df529f64-f930-4b89-ba37-9d839667188d) | 2011 | 18,426 | Unverified | New |
| 482 |  | Bibio | [Anything New](https://musicbrainz.org/recording/77ce7279-65fb-4aec-a344-e853658a812f) | 2010 | 18,425 | Unverified | New |
| 483 |  | Little Boots | [Meddle](https://musicbrainz.org/recording/573c2463-d259-497c-858d-fd4ce27b5184) | 2008 | 46,245 | Unverified | New |
| 484 |  | David Lynch | [Good Day Today](https://musicbrainz.org/recording/ae83f573-b206-4cd8-ac30-546943791b80) | 2010 | 18,383 | Unverified | Already |
| 485 |  | Black Rebel Motorcycle Club | [Red Eyes and Tears](https://musicbrainz.org/recording/3990d709-539b-4270-9515-b46ac7c7251e) | 2001 | 46,063 | Unverified | New |
| 486 |  | Four Tet | [As Serious as Your Life](https://musicbrainz.org/recording/929c01ff-3c63-447f-b1f0-8f96426ccb5a) | 2003 | 45,535 | Unverified | New |
| 487 |  | UNKLE | [Ablivion](https://musicbrainz.org/recording/a552fd56-49c2-4abb-8be5-27c79c77f957) | 2010 | 18,125 | Unverified | New |
| 488 |  | DJ Shadow | [Six Days](https://musicbrainz.org/recording/6237809d-1741-401e-884c-8451b6eb510e) | 2002 | 45,282 | Unverified | New |
| 489 |  | The Sounds | [Tony the Beat](https://musicbrainz.org/recording/b58d53b4-7dd9-44b1-aacb-67f6a8361253) | 2006 | 45,120 | Unverified | New |
| 490 |  | Doves | [Black and White Town](https://musicbrainz.org/recording/39a2f790-6e3e-4558-9a6b-6fb4f9337f8d) | 2005 | 45,065 | Unverified | New |
| 491 |  | Holy Ghost! | [Jam for Jerry](https://musicbrainz.org/recording/97622972-1bdb-4158-8ae0-03b390ea895b) | 2011 | 17,936 | Unverified | New |
| 492 |  | Joanna Newsom | [The Book of Right-On](https://musicbrainz.org/recording/1476f562-1d05-4fd4-ab13-0ab58bf2d2ce) | 2004 | 44,816 | Unverified | Already |
| 493 |  | YELLE | [Que veux-tu](https://musicbrainz.org/recording/7c0ab15e-be64-44b4-a738-d3f13c913e2c) | 2011 | 17,835 | Unverified | New |
| 494 |  | Four Tet | [She Moves She](https://musicbrainz.org/recording/9c7120b9-f968-4d13-8d05-8a1922ae6d8b) | 2003 | 44,644 | Unverified | New |
| 495 |  | Danger Mouse & Daniele Luppi | [Her Hollow Ways](https://musicbrainz.org/recording/9f423de4-4e74-4138-8a47-c821a45a0cfd) | 2011 | 17,729 | Unverified | New |
| 496 |  | Calvin Harris | [The Girls](https://musicbrainz.org/recording/93e6fc14-cbfe-41ae-8199-4fd1ef29b8d0) | 2007 | 44,425 | Unverified | New |
| 497 |  | Junior Boys | [Banana Ripple](https://musicbrainz.org/recording/56166ec9-a839-4ae6-8233-ceab6f3ed063) | 2011 | 17,673 | Unverified | New |
| 498 |  | jj | [And Now](https://musicbrainz.org/recording/8cdcbcb5-d9cd-4cc3-b2b2-0a5b3055ebf3) | 2010 | 17,662 | Unverified | New |
| 499 |  | Alvvays | [Dreams Tonite](https://musicbrainz.org/recording/62d151f7-7639-470b-909b-7cb2c2b603d4) | 2017 | 4,423 | Unverified | New |
| 500 |  | Amon Tobin | [Goto 10](https://musicbrainz.org/recording/b28480ff-5584-40cb-b31d-546f81f0f2aa) | 2011 | 17,596 | Unverified | New |

## Other datasets checked

| Dataset | What is useful | Decision for this report |
|---|---|---|
| [Clapback export](https://clapback.seethroughlab.com/export) | Downloadable vectors, pipeline labels and MusicBrainz recording claims; publisher declares CC0. | Main embedding source; the repo already holds this exact snapshot. [API contract](https://clapback.seethroughlab.com/api). |
| [ListenBrainz sample](https://data.metabrainz.org/pub/musicbrainz/listenbrainz/sample/listenbrainz-sample-20250610-094311-full/) | Real user/song loves with recording MBIDs, already downloaded and checksummed in this repo. | Strongest immediately usable evidence. Narrow artist coverage in the sample cannot establish coverage of all ListenBrainz. |
| [ListenBrainz feedback API](https://listenbrainz.readthedocs.io/en/latest/users/api/recordings.html) | User-level loves/dislikes by exact recording MBID with count/offset pagination. | Successfully probed for 30 candidates. Confirms additional current interactions; remaining bulk checks failed at the connection layer. |
| [ListenBrainz full listening dumps](https://listenbrainz.readthedocs.io/en/latest/users/listenbrainz-dumps.html) | User listening events, rather than only explicit preferences. | Accessible source for future play-history training; not downloaded or joined in this research. [Publisher dataset terms](https://metabrainz.org/datasets/postgres-dumps) declare CC0 for ListenBrainz. |
| [MLHD+](https://metabrainz.org/datasets/derived-dumps) | Large user-level listening histories reconciled with canonical MusicBrainz identifiers. | Conditional option; non-commercial only. Its raw interactions were not downloaded or joined. API popularity counts partly originate here. |
| [ARC Music Embeddings](https://huggingface.co/datasets/orwelian84/arc-music-embeddings) | Published CLAP archive and a 5,050-row track index; substantially more mainstream pop appears in the index. | Downloaded/read the track index and card. No MBID/user-interaction bridge is supplied. Its `laion/larger_clap_music` vectors use a different model from our bank. Not counted as fully eligible additions. |
| [Music4All-Onion](https://zenodo.org/records/15394646) | Listening interactions and multimodal song features. | Publisher's file listing does not establish a ready-made CLAP bank with a verified MusicBrainz join. Useful research lead, not a qualifying song source on present evidence. |
| [LFM-2b](https://www.cp.jku.at/datasets/LFM-2b/) | Previously offered large Last.fm histories. | Publisher says downloads were withdrawn over licensing issues. Not treated as accessible. |
| [Million Song Dataset](https://millionsongdataset.com/) | Popular-music metadata/features and complementary listening resources. | These audio features are not CLAP vectors; no verified three-way song join was established here. |
| [DISCO-10M paper](https://arxiv.org/abs/2306.13512) | Describes precomputed CLAP vectors for popular-music matches. | A paper's existence does not establish a currently downloadable vector bank or MusicBrainz/user-history join. Not counted. |
| [LAION-DISCO-12M](https://huggingface.co/datasets/laion/LAION-DISCO-12M) | Large published song/video metadata index. | Inspected schema does not supply the required ready CLAP vector + recording MBID + user interactions. Do not assume this is the original DISCO-10M embedding release. |
| [MusicBenchEmbedded](https://huggingface.co/datasets/Xenova/MusicBenchEmbedded) | Audio/text embeddings attached to captioned excerpts. | No verified recognizable-song MusicBrainz/user-listening join. Different embedding model; not an expansion source established here. |
| [500k-user listening dataset](https://github.com/Gabriel-Kahen/user_music_listening_dataset) | Publisher describes per-user top tracks/playcounts and MBIDs where available. | An additional listening-data lead; no CLAP vectors and no row-level overlap or reuse-term verification performed. Not used to label a song eligible. |

### Most promising separate route for newer mainstream pop

ARC's published index includes Bruno Mars “24K Magic”, Billie Eilish “bad guy” and “LUNCH”, Beyoncé “TEXAS HOLD ’EM”, ROSÉ & Bruno Mars “APT.”, Adele “Rolling in the Deep”, and Lady Gaga “Abracadabra”. These are **leads, not confirmed eligible songs** in the tables above. Several index entries refer to music videos or lyric uploads, which can differ from the album recording.

The published `segment_embeddings.npz` contains track-level pooled vectors and segment vectors according to the card, but this research inspected the index, not that large archive's individual vector rows. Before admitting these songs, verify the actual vector entry, identify the exact recording/version, check post-2000 original release, and obtain matching user-level interactions. Keep the ARC embedding bank and its paired text encoder separate from the existing Clapback bank, or prepare a consistently encoded replacement bank; equal 512-dimensional shapes do not make the spaces compatible. No such migration is proposed or implemented here.

## Source terms and reproducibility

Clapback vectors/claims and ListenBrainz data carry publisher-declared CC0 terms. MusicBrainz core IDs/titles/dates are CC0; its supplementary tags have separate CC BY-NC-SA terms. Genre labels were deliberately omitted from the exported shortlist. MLHD+ is explicitly non-commercial; the combined popularity figures should not be promoted as an unrestricted standalone training corpus. No audio is included, and dataset availability does not grant audio rights. ARC's card declares MIT for its dataset, separately from the music it names.

Local inputs used: `data/catalogue/annotated_inventory.json`, `data/catalogue/clapback_inventory.json`, `data/workshop/songs.json`, `data/sources/clapback/manifest.json`, the Clapback vectors and claims, and `data/sources/listenbrainz/recording_feedback.parquet`. The sample's two popularity CSVs were inspected and contained headers only, so no counts were inferred from them.

The CSV preserves the aggregate API results used for these 500 rows and the successful feedback probe totals; raw listener identifiers were not retained in the report. The popularity request body is `{"recording_mbids": ["<recording_mbid>"]}` to `https://api.listenbrainz.org/1/popularity/recording`. The per-recording feedback URL is included in each CSV row. Current counts may change; cached metadata dates to 19 October 2026 and the sample to 10 June 2025.

Input SHA256 values:

- `data/catalogue/annotated_inventory.json`: `b4a44024032c544bf38aa568ebdb578bf12edb413899fc2d19cd7fc315263bc1`
- `data/sources/clapback/manifest.json`: `87be52ff1494944ad81312fca48df9567c6a56cbe6c9104b7c80caea45d0c954`
- `data/sources/clapback/claims.csv.gz`: `4148558155e48354ba9f31d8b38968e50b58e8796d30f46203aa9aa0db965704`
- `data/sources/clapback/embeddings-laion_clap_htsat_unfused_frontend1_artifact1_pool1_fp32.csv.gz`: `801d6810fd771ffc20bb839ce266b60c8ba09a11622df10538569e87642a14a6`
- `data/sources/listenbrainz/recording_feedback.parquet`: `8e0f51a253af4ec35d42d83bd00cb6a7baf1493a54c4a8630b3f4d73e6c05df9`
- `data/workshop/songs.json`: `61c3aacb32b4429cdab37739f61bbe91622bf0b1eefa39cce2c91149ced0c645`
