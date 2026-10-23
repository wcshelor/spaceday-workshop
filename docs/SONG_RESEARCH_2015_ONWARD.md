# Another 180 songs from 2015 onward

Research date: 23 October 2026. Supplement to [the first 500-song report](POST_2000_SONG_RESEARCH.md). Research only; no songs imported and no application, model or embedding changes made.

## Result

**180 additional songs across 89 primary artists**, with no recording-ID repeats or repeated primary-artist/title pairs from the previous 500 recommendations. No artist contributes more than three tracks in this supplement. **172 have confirmed accessible user-level positive feedback**, alongside a checked, ready-made CLAP vector and exact MusicBrainz recording ID. **8 remain conditional** because their user-level data was not established. 170 exact recordings are outside the current app catalogue; 10 are already present there, and are marked accordingly. “Additional” means additional to the previous recommendation document, not necessarily absent from the app.

All selected cached recording dates are **2015–2022**. The source did not provide qualifying later releases for this selection. This is a larger recent-music selection, not evidence of 180 mainstream hits: the accessible compatible CLAP pool remains strongest in indie pop, synth-pop, alternative rock and electronic music. The **★** marks the editorial starting points; the other entries include deeper cuts, instrumental electronic tracks and soundtrack cues. Familiarity depends on the audience.

The [detailed CSV](SONG_RESEARCH_2015_ONWARD.csv) contains the exact vector fingerprint, pipeline, identity-claim strength, full dates, API totals, user-data checks, existing-catalogue flags and per-recording feedback URLs. Both confirmed and conditional tables are sorted in the research's initial priority order, which favors higher source listening counts and gives 2020+ releases a boost. ★ is an editorial choice, not a chart statistic.

## What was verified

- **MusicBrainz + audio embeddings:** every selected recording ID appears in the cached MusicBrainz inventory and has a checked 512-dimensional, finite CLAP vector in the pinned 18 October 2026 export. Conflicting tied identity claims were rejected. All selected vectors use `laion/clap-htsat-unfused+frontend1+artifact1+pool1+fp32`, matching the existing app. MusicBrainz associations remain contributor claims, not independently verified audio fingerprints against official masters.
- **S n:** n distinct positive listeners counted directly from the existing ListenBrainz sample `recording_feedback.parquet`, joined by exact recording MBID.
- **L n:** the current public ListenBrainz feedback endpoint returned user-level feedback and reported n positive rows. A one-row probe confirmed accessibility; the full paginated set still needs collecting. Live totals are feedback rows, not independently deduplicated listener counts or play counts. S and L overlap and must not be added.
- **Popularity:** source-user totals reuse the earlier research's aggregate API responses, not a fresh popularity scrape. These counts sum ListenBrainz and MLHD figures and are not globally deduplicated people. Here the research floor is 100 source users, lower than the previous report's 1,000, to find more recent artists without relaxing the artist cap. This expands choice but includes less widely known material.
- **Release dates:** selection uses MusicBrainz recording first-release dates, not original composition dates. Known misleading later-edition matches were removed, including older DJ Shadow, Tricky and Alison's Halo material; Jamie xx “Sleep Sound” and Twin Shadow “To the Top” were excluded as pre-2015 releases. AFX archival material and a later cover of “Laid” were also omitted. Remaining original-release dates have not all been independently re-established; final admission should verify version/date where ambiguous. Some album dates can differ from earlier singles, while still falling within the requested window.

This is data-eligibility research, not a guarantee of usable collaborative factors. The existing model requires at least five listeners per item and five items per listener followed by another support check. Even a song with several loves can fall out of that shared-user network. No retraining, support-filter result or recommendation-quality claim is made for these new songs.

## Coverage

| Measure | Count |
|---|---:|
| Additional songs | 180 |
| Primary artists | 89 |
| Confirmed accessible positive user feedback | 172 |
| Conditional user-data evidence | 8 |
| 2015–2019 | 134 |
| 2020–2022 | 46 |
| Exact recordings outside current app | 170 |
| Existing app recordings | 10 |

## Confirmed data-eligible songs (172)

Click a song to inspect its exact MusicBrainz recording. “Source users” means the combined aggregate described above. S/L means confirmed sample/live feedback. ★ marks editorial starting points.

| # | Priority | Artist | Song | Year | Source users | User feedback | App catalogue |
|---:|:---:|---|---|---:|---:|---|---|
| 1 | ★ | Beach House | [Space Song](https://musicbrainz.org/recording/5a8f7959-6906-4672-ac64-f994e98976ae) | 2015 | 11,322 | L 200 | New |
| 2 | ★ | Tame Impala | [Eventually](https://musicbrainz.org/recording/9db8c054-4379-4f1a-8b5e-5d6b1c2b0f3a) | 2015 | 9,287 | S 49; L 148 | New |
| 3 |  | Tame Impala | [Nangs](https://musicbrainz.org/recording/c9f0e0e0-3789-4a78-a91e-03bc0c3ea998) | 2015 | 8,409 | S 24; L 83 | Already |
| 4 |  | Tame Impala | [Yes I’m Changing](https://musicbrainz.org/recording/173324ec-808e-467a-bab8-0fa3a78bf90d) | 2015 | 8,083 | S 39; L 115 | New |
| 5 | ★ | Beach House | [Once Twice Melody](https://musicbrainz.org/recording/499e5323-8f00-40a5-a354-2d0b2af55d1e) | 2021 | 2,553 | L 33 | Already |
| 6 | ★ | Japanese Breakfast | [Slide Tackle](https://musicbrainz.org/recording/5ef0009d-a585-4bf3-bce7-3698ec0d33ce) | 2021 | 2,121 | L 24 | New |
| 7 | ★ | Beach House | [Superstar](https://musicbrainz.org/recording/5d66ab14-1ed0-423c-b4b2-892f3c1885e0) | 2021 | 2,080 | L 29 | New |
| 8 | ★ | Japanese Breakfast | [Savage Good Boy](https://musicbrainz.org/recording/c371f4ad-f288-4db7-be6c-ad836ebea901) | 2021 | 1,948 | L 18 | New |
| 9 |  | Japanese Breakfast | [Posing for Cars](https://musicbrainz.org/recording/019a961c-04af-4745-9406-d931cf13cc7d) | 2021 | 1,634 | L 25 | New |
| 10 |  | Fontaines D.C. | [In ár gCroíthe go deo](https://musicbrainz.org/recording/e702e2ea-e1b3-4339-b0cd-b784c1781472) | 2022 | 1,552 | L 22 | New |
| 11 |  | Four Tet | [Two Thousand and Seventeen](https://musicbrainz.org/recording/59feedf2-8212-4352-80c9-820b00bd36ce) | 2017 | 4,190 | L 36 | Already |
| 12 | ★ | LCD Soundsystem | [Oh Baby](https://musicbrainz.org/recording/88b29d0a-2dd8-46cb-8111-99c3d169639d) | 2017 | 4,123 | L 47 | New |
| 13 | ★ | Jamie xx | [Gosh](https://musicbrainz.org/recording/d87da388-bbcb-4fff-aa3a-6088d4105f58) | 2015 | 4,059 | L 55 | New |
| 14 |  | Fontaines D.C. | [How Cold Love Is](https://musicbrainz.org/recording/afda387f-e400-4342-9db2-134bb4438779) | 2022 | 1,419 | L 16 | New |
| 15 | ★ | Men I Trust | [Numb](https://musicbrainz.org/recording/9f7415d2-6838-4a8b-827c-4af7b87890cc) | 2019 | 3,857 | L 63 | New |
| 16 |  | Pixies | [All I Think About Now](https://musicbrainz.org/recording/874d598c-61ea-4068-9cd1-e304691eb94e) | 2016 | 3,545 | S 13; L 42 | New |
| 17 | ★ | Courtney Barnett | [Pedestrian at Best](https://musicbrainz.org/recording/1fc6ee4c-f9f3-4be3-9ddb-d6b4cbfc7825) | 2015 | 3,498 | L 44 | New |
| 18 |  | Fontaines D.C. | [Bloomsday](https://musicbrainz.org/recording/b38f6454-6524-4522-a6fe-2673de91aab3) | 2022 | 1,238 | L 13 | New |
| 19 | ★ | TV Girl | [Taking What’s Not Yours](https://musicbrainz.org/recording/d45b3548-31b4-428e-9c6c-5546cac71cf6) | 2016 | 3,365 | L 36 | New |
| 20 |  | Interpol | [Toni](https://musicbrainz.org/recording/e95c9af4-b100-4944-8a9f-c022a0b81d93) | 2022 | 1,137 | L 3 | New |
| 21 |  | Jamie xx | [Obvs](https://musicbrainz.org/recording/e29880b8-0bc6-4daf-bb43-41ecef41c41c) | 2015 | 3,122 | L 30 | New |
| 22 |  | Jamie xx featuring Romy | [SeeSaw](https://musicbrainz.org/recording/a1703196-10db-4772-8bf4-cc046c320e09) | 2015 | 3,083 | L 51 | New |
| 23 |  | Washed Out | [Time to Walk Away](https://musicbrainz.org/recording/00b23576-e8f9-4421-b251-f7d2aa5190a4) | 2020 | 1,049 | L 6 | New |
| 24 | ★ | Men I Trust | [Seven](https://musicbrainz.org/recording/5232159f-ded9-48cb-8ddc-093cfde4c20a) | 2018 | 2,915 | L 37 | New |
| 25 | ★ | Men I Trust | [I Hope to Be Around](https://musicbrainz.org/recording/120aa4a5-7dc4-4ffa-ac4b-a7ae946d23b8) | 2017 | 2,873 | L 32 | New |
| 26 | ★ | Cults | [Gilded Lily](https://musicbrainz.org/recording/1c8e3e41-0d90-4573-8528-e809cce46c39) | 2017 | 2,847 | L 24 | New |
| 27 |  | Молчат Дома | [Клетка](https://musicbrainz.org/recording/0e32b55b-668e-46dd-ad05-85bbbe3eb045) | 2018 | 2,825 | L 41 | New |
| 28 | ★ | Purity Ring | [begin again](https://musicbrainz.org/recording/8793749c-a8fe-48a0-a03d-b20ef9a393bf) | 2015 | 2,789 | L 45 | New |
| 29 |  | Oliver Buckland | [backroom labyrinth](https://musicbrainz.org/recording/5d1c8108-1581-4421-835d-0c3742598667) | 2020 | 983 | L 24 | New |
| 30 |  | TV Girl | [Loving Machine](https://musicbrainz.org/recording/f0d7f6b7-33b1-49a6-abcc-8e1344645748) | 2016 | 2,755 | L 42 | New |
| 31 |  | Nation of Language | [The Wall & I](https://musicbrainz.org/recording/a35b19d0-790a-4a2a-a537-b1ec49c848f9) | 2020 | 931 | L 6 | New |
| 32 |  | Tycho | [Epoch](https://musicbrainz.org/recording/41efd3f2-e9b6-4911-ac1c-fea150a2bd3c) | 2016 | 2,486 | L 8 | New |
| 33 | ★ | Purity Ring | [bodyache](https://musicbrainz.org/recording/7344aad3-4c04-4e0b-a70e-ceb40433eb7b) | 2015 | 2,471 | L 14 | New |
| 34 |  | Planet 1999 | [Party](https://musicbrainz.org/recording/06d1673c-cfa1-449d-8723-87b696ccb872) | 2020 | 868 | L 3 | New |
| 35 | ★ | Viagra Boys | [Sports](https://musicbrainz.org/recording/0489fc23-42c8-4937-a1db-a0b29fb14117) | 2018 | 2,436 | L 34 | New |
| 36 | ★ | Courtney Barnett | [Depreston](https://musicbrainz.org/recording/88743e80-5814-47bb-82dc-e039c388e4f7) | 2015 | 2,432 | L 24 | New |
| 37 |  | Cults | [Monolithic](https://musicbrainz.org/recording/470584d6-2b9d-45aa-875c-0fc60b5bcde7) | 2020 | 860 | L 4 | Already |
| 38 |  | Interpol | [Fables](https://musicbrainz.org/recording/d36f3203-2d97-4d65-934d-b4dd8badec26) | 2022 | 856 | L 7 | New |
| 39 |  | Interpol | [Something Changed](https://musicbrainz.org/recording/46e5443b-ef66-430b-91c1-6ca414425c6f) | 2022 | 842 | L 5 | New |
| 40 | ★ | LCD Soundsystem | [American Dream](https://musicbrainz.org/recording/7eeeb7c0-4083-48e8-89b0-0a2f6ecdbe20) | 2017 | 2,263 | L 11 | New |
| 41 | ★ | Dan Deacon | [When I Was Done Dying](https://musicbrainz.org/recording/99b441a2-9071-405f-a5ce-c432bf450d65) | 2015 | 2,196 | L 11 | New |
| 42 |  | Kyle Dixon & Michael Stein | [Kids](https://musicbrainz.org/recording/05110d96-58bf-4b13-a12b-8d703254768f) | 2016 | 2,195 | L 16 | New |
| 43 |  | Courtney Barnett | [Elevator Operator](https://musicbrainz.org/recording/5be82111-9f29-461e-8191-dbb733d0b252) | 2015 | 2,186 | L 37 | New |
| 44 |  | Dan Deacon | [Sat by a Tree](https://musicbrainz.org/recording/cf11709c-6ca2-4818-9118-72ba4d14d5ba) | 2020 | 770 | L 2 | New |
| 45 | ★ | Phoenix | [J‐Boy](https://musicbrainz.org/recording/ca409fcc-740b-4dfc-8692-afbd734e43d4) | 2017 | 2,160 | L 22 | New |
| 46 | ★ | LCD Soundsystem | [Tonite](https://musicbrainz.org/recording/bcd98960-9c26-4d53-97d7-592c57d713a6) | 2017 | 2,156 | L 30 | New |
| 47 |  | Oneohtrix Point Never | [Babylon](https://musicbrainz.org/recording/f561b3d9-dd68-48c8-ace1-1738bd7f4c31) | 2018 | 2,108 | L 17 | New |
| 48 | ★ | Com Truise | [Propagation](https://musicbrainz.org/recording/7996ddc3-2d83-4cff-8c39-01fdcef55848) | 2017 | 2,078 | L 11 | New |
| 49 |  | Nation of Language | [September Again](https://musicbrainz.org/recording/ae8d7beb-39a7-4237-bda9-8ee80630972f) | 2020 | 727 | L 3 | New |
| 50 | ★ | Future Islands | [Ran](https://musicbrainz.org/recording/3c751bd0-6e93-46ab-9635-a5170b1231aa) | 2017 | 1,981 | L 17 | New |
| 51 |  | Plaid | [Do Matter](https://musicbrainz.org/recording/d932f53a-8528-49d7-b5e2-4f5b44b11cdb) | 2016 | 1,970 | L 24 | New |
| 52 |  | Dan Deacon | [Fell Into the Ocean](https://musicbrainz.org/recording/24518587-881a-4ad1-a1b5-e79ffc5b1e99) | 2020 | 685 | L 3 | New |
| 53 |  | Nation of Language | [Across That Fine Line](https://musicbrainz.org/recording/a9bd6c05-0b11-4056-b89d-7ed0c7d60613) | 2021 | 684 | L 3 | New |
| 54 |  | Hans Zimmer & Benjamin Wallfisch | [2049](https://musicbrainz.org/recording/4a060ef7-1e55-4265-be4b-c51a7f7dced4) | 2017 | 1,905 | S 2; L 11 | New |
| 55 |  | Tycho | [Division](https://musicbrainz.org/recording/17c31dbd-fee1-4451-90d7-11dd6b88e059) | 2016 | 1,891 | L 10 | New |
| 56 |  | Modest Mouse | [The Sun Hasn’t Left](https://musicbrainz.org/recording/cd1ec0bf-cc97-47f8-9166-2a4152769133) | 2021 | 661 | L 13 | New |
| 57 |  | Purity Ring | [heartsigh](https://musicbrainz.org/recording/b24c87bb-f87c-49cd-aa4d-780c2c3b1d66) | 2015 | 1,842 | L 20 | New |
| 58 | ★ | Neon Indian | [Annie](https://musicbrainz.org/recording/e1d8d920-dba6-4f13-b761-88bc5dce0182) | 2015 | 1,829 | L 27 | New |
| 59 |  | George Clanton | [Livin’ Loose](https://musicbrainz.org/recording/b02c4b56-754c-46bc-89f0-a7748eabb944) | 2018 | 1,827 | L 35 | New |
| 60 |  | TV Girl feat. Maddie Acid | [Song About Me](https://musicbrainz.org/recording/808f530c-e71a-4ace-9f9c-6d362bd7e458) | 2016 | 1,798 | L 28 | New |
| 61 |  | Tycho | [Horizon](https://musicbrainz.org/recording/cf2f38f4-cf2a-42e1-a0e7-bd330856a4bd) | 2016 | 1,702 | L 15 | New |
| 62 |  | Rival Consoles | [Still Here](https://musicbrainz.org/recording/74a8c3d0-c304-4fc1-b55d-6a48f96b70ff) | 2020 | 593 | L 1 | Already |
| 63 |  | Persona La Ave | [Going Deaf](https://musicbrainz.org/recording/91ff1260-cdc7-4148-a2dd-0a2d7d5a2eec) | 2020 | 589 | L 4 | New |
| 64 |  | Toro y Moi | [Lilly](https://musicbrainz.org/recording/4721a7b7-d03c-4729-a607-f9ac3ccf81f8) | 2015 | 1,546 | L 11 | New |
| 65 |  | Washed Out | [Hard to Say Goodbye](https://musicbrainz.org/recording/15ccf9f0-87c6-43f7-95c4-99be921443ed) | 2017 | 1,540 | L 13 | New |
| 66 |  | Ben Lukas Boysen | [Love](https://musicbrainz.org/recording/753bbc8e-b640-4477-8703-11b150d4cb18) | 2020 | 542 | L 2 | New |
| 67 |  | DIIV | [Blankenship](https://musicbrainz.org/recording/05207368-c1cc-4b02-8d43-1e37dc879b2c) | 2019 | 1,525 | L 19 | New |
| 68 |  | Oliver Buckland | [Hourglass Meadow](https://musicbrainz.org/recording/55640ab8-b736-4871-93c5-3353ac9191e8) | 2021 | 535 | L 11 | New |
| 69 |  | Com Truise | [Memory](https://musicbrainz.org/recording/c7083a18-8a24-48a1-a278-cfe2834a48d8) | 2017 | 1,479 | L 9 | New |
| 70 |  | Lusine feat. Vilja Larjosto | [Just a Cloud](https://musicbrainz.org/recording/b9069a7d-43b0-4dec-aa10-a856c15315c5) | 2017 | 1,478 | L 22 | New |
| 71 |  | 憂鬱 | [Sun](https://musicbrainz.org/recording/1a0902b8-1141-4040-90e3-040c3f5081c1) | 2018 | 1,464 | L 14 | New |
| 72 |  | Perfume Genius | [Die 4 You](https://musicbrainz.org/recording/14df68e6-8324-42fd-b9e8-db27b70e3879) | 2017 | 1,452 | L 16 | New |
| 73 |  | Oliver Buckland | [espial](https://musicbrainz.org/recording/816fa97e-b291-40dd-9b5a-66f3baeedbc1) | 2021 | 513 | L 14 | New |
| 74 |  | Oneohtrix Point Never | [Ezra](https://musicbrainz.org/recording/d7236bca-ca1e-40a8-98ca-ac19b1c94bab) | 2015 | 1,435 | L 25 | New |
| 75 |  | DIIV | [Skin Game](https://musicbrainz.org/recording/e629d752-61b1-472e-95c9-14ba3c0dc8f1) | 2019 | 1,433 | L 14 | New |
| 76 |  | Com Truise | [Ultrafiche of You](https://musicbrainz.org/recording/3f32d49d-6ea5-4073-9e73-2d4290b3d0ff) | 2019 | 1,427 | L 12 | New |
| 77 |  | S U R V I V E | [A.H.B.](https://musicbrainz.org/recording/afa7d42e-1a32-4d67-a65c-00a68eb67e74) | 2016 | 1,350 | L 4 | New |
| 78 |  | M83 | [Road Blaster](https://musicbrainz.org/recording/3ff4c64c-8c20-48cd-932a-896834020dfb) | 2016 | 1,342 | S 4; L 13 | New |
| 79 |  | Tamaryn | [Cranekiss](https://musicbrainz.org/recording/94cef2a6-3fd3-4087-ada9-606274224f3f) | 2015 | 1,333 | L 20 | New |
| 80 |  | A.L.I.S.O.N | [Space Echo](https://musicbrainz.org/recording/efdc1926-daed-4b3c-bb13-8910a1c5e00f) | 2018 | 1,330 | L 15 | New |
| 81 |  | The Horrors | [Press Enter to Exit](https://musicbrainz.org/recording/234e400a-20e4-4670-91b0-ad917c4fad4e) | 2017 | 1,327 | L 11 | New |
| 82 |  | Ought | [Beautiful Blue Sky](https://musicbrainz.org/recording/ca1ce69c-5416-4c84-81ab-d70f449f3681) | 2015 | 1,319 | L 27 | New |
| 83 |  | Kyle Dixon & Michael Stein | [This Isn’t You](https://musicbrainz.org/recording/4b36abc3-ba13-4d70-a066-d95a3c4d9125) | 2016 | 1,310 | L 2 | New |
| 84 |  | Cults | [Trials](https://musicbrainz.org/recording/85399bc9-d680-4c89-aa97-0c8ca42b01f7) | 2020 | 462 | L 2 | New |
| 85 | ★ | Phoenix | [Ti amo](https://musicbrainz.org/recording/57c573a7-1f9f-42fb-99db-6ad1dd96046c) | 2017 | 1,302 | L 12 | Already |
| 86 |  | DIIV | [Taker](https://musicbrainz.org/recording/d16877fd-38ee-4480-b124-cda9a15b4eb0) | 2019 | 1,302 | L 4 | New |
| 87 |  | Oneohtrix Point Never | [Sticky Drama](https://musicbrainz.org/recording/81de24c4-358e-45ce-848a-04f47840c0ca) | 2015 | 1,284 | L 2 | New |
| 88 |  | Neon Indian | [Slumlord](https://musicbrainz.org/recording/eb537564-e920-4fce-b42b-69663e9ef35b) | 2015 | 1,284 | L 28 | New |
| 89 |  | Puma Blue | [Opiate](https://musicbrainz.org/recording/ac593128-1344-46cf-9b59-96d6c16e1470) | 2021 | 451 | L 6 | New |
| 90 |  | George Clanton | [It Makes the Babies Want to Cry](https://musicbrainz.org/recording/c5acee8e-3c87-465e-908b-54c6bf9f81ed) | 2015 | 1,264 | L 11 | New |
| 91 |  | George Clanton | [Dumb](https://musicbrainz.org/recording/f2bf56ce-a671-4c16-af40-899ff2ca8d33) | 2018 | 1,262 | L 19 | New |
| 92 |  | Hans Zimmer & Benjamin Wallfisch | [Flight to LAPD](https://musicbrainz.org/recording/4cdfa334-4adf-4986-8e8a-2b672508cc66) | 2017 | 1,258 | S 1; L 6 | New |
| 93 |  | Hans Zimmer & Benjamin Wallfisch | [Sapper’s Tree](https://musicbrainz.org/recording/2ffca35b-7b3d-47ef-9d24-93cf0c2e4887) | 2017 | 1,241 | L 4 | New |
| 94 |  | Small Black | [Boys Life](https://musicbrainz.org/recording/5ca39940-24c4-4c7a-aefb-0a284ad209b5) | 2015 | 1,219 | L 11 | New |
| 95 | ★ | Sevdaliza | [Human](https://musicbrainz.org/recording/ec308d5e-4c24-4bba-870d-6282ed8c80f6) | 2017 | 1,214 | L 22 | New |
| 96 |  | M83 feat. Mai Lan | [Laser Gun](https://musicbrainz.org/recording/8ff5cce2-41f4-404e-9252-bea02e270b36) | 2016 | 1,196 | S 6; L 18 | New |
| 97 | ★ | Young Fathers | [In My View](https://musicbrainz.org/recording/8dfae998-efd4-4ebe-a482-1523ff687362) | 2018 | 1,193 | L 16 | New |
| 98 |  | Washed Out | [Floating By](https://musicbrainz.org/recording/b0cb6f30-87d6-4ace-894b-5c3ee42f7e41) | 2017 | 1,183 | L 8 | New |
| 99 |  | Drab Majesty | [Dot in the Sky](https://musicbrainz.org/recording/1a6cffed-20ba-4380-973b-ec301a66b6b2) | 2017 | 1,132 | L 5 | New |
| 100 |  | Gardens & Villa | [Disco Kitchen](https://musicbrainz.org/recording/f7666f17-32d8-4b58-9724-341b5745686c) | 2020 | 396 | L 1 | New |
| 101 |  | Future Islands | [Ancient Water](https://musicbrainz.org/recording/296ff2f8-4c1e-41d7-aca0-522d79b9dae8) | 2017 | 1,100 | L 9 | New |
| 102 |  | loscil | [Red Tide](https://musicbrainz.org/recording/1881fe60-39da-4056-bffe-66e8ebecf642) | 2016 | 1,088 | L 11 | New |
| 103 |  | Protomartyr | [A Private Understanding](https://musicbrainz.org/recording/564c681d-b1bc-4953-91f2-4f052aac4f58) | 2017 | 1,087 | L 12 | New |
| 104 |  | CCFX | [The One to Wait](https://musicbrainz.org/recording/62cc8136-bc1a-4274-a7f5-a3af708fd355) | 2017 | 1,085 | L 11 | New |
| 105 |  | Perfume Genius | [Just Like Love](https://musicbrainz.org/recording/54da40c6-522c-43ea-9a8a-8fd4373ca72a) | 2017 | 1,075 | L 6 | New |
| 106 |  | Kyle Dixon & Michael Stein | [Eleven](https://musicbrainz.org/recording/30104010-ba66-4e98-9ef9-8097de58aaf4) | 2016 | 1,062 | L 2 | New |
| 107 |  | Phoenix | [Goodbye Soleil](https://musicbrainz.org/recording/54ee14a7-026e-4dc6-925e-ffaf0329fae6) | 2017 | 1,044 | L 11 | New |
| 108 |  | Future Islands | [Time on Her Side](https://musicbrainz.org/recording/7f19beca-87a8-46f4-b014-92d7bd35caaa) | 2017 | 1,037 | L 8 | New |
| 109 |  | Toro y Moi | [Buffalo](https://musicbrainz.org/recording/84da23df-d90d-4fac-8f9f-7c4319d74480) | 2015 | 1,032 | L 9 | New |
| 110 |  | 憂鬱 | [Slow](https://musicbrainz.org/recording/7bbf1f00-056d-4bcc-afb7-34cc18aa08ad) | 2018 | 1,021 | L 11 | New |
| 111 |  | Amen Dunes | [Blue Rose](https://musicbrainz.org/recording/2e25fde7-de9e-46a2-a604-5cb1ef28012d) | 2018 | 1,016 | L 9 | New |
| 112 |  | Planet 1999 | [Devotion](https://musicbrainz.org/recording/e3c55d0d-d22a-417c-bcf4-637674fb1b75) | 2020 | 355 | L 2 | New |
| 113 |  | Windows彡96 | [Deep Swim](https://musicbrainz.org/recording/93b3e416-90ae-4752-8bf0-954dda596d27) | 2019 | 996 | L 7 | New |
| 114 |  | Amen Dunes | [Believe](https://musicbrainz.org/recording/ee047ece-a8c5-4a28-84d6-e05ec83ddbae) | 2018 | 990 | L 9 | New |
| 115 |  | Amen Dunes | [Miki Dora](https://musicbrainz.org/recording/d8f3dd85-0c54-429f-8794-6bc1048327d1) | 2018 | 970 | L 12 | New |
| 116 | ★ | M83 feat. Mai Lan | [Go!](https://musicbrainz.org/recording/8371ad41-20ee-4aee-975d-c4ae6c5084fd) | 2016 | 961 | S 5; L 15 | New |
| 117 |  | Yppah | [Bushmills](https://musicbrainz.org/recording/0ba74eac-7068-4898-bbc4-6f687ed71645) | 2015 | 960 | L 3 | New |
| 118 |  | Junie & TheHutFriends | [Drown Me!](https://musicbrainz.org/recording/3553488c-be48-44a8-930c-f19aa1b96476) | 2022 | 339 | L 5 | New |
| 119 |  | HEALTH | [NEW COKE](https://musicbrainz.org/recording/2f9da670-4462-444b-abbe-102c4472c160) | 2015 | 954 | L 14 | New |
| 120 |  | Tirzah | [Gladly](https://musicbrainz.org/recording/f30f6628-aa47-48af-9ef8-13433a339f8a) | 2018 | 953 | L 13 | New |
| 121 |  | Protomartyr | [The Chuckler](https://musicbrainz.org/recording/68bf7ad2-8c1b-4268-89ca-72dd352694f6) | 2017 | 951 | L 6 | New |
| 122 |  | death’s dynamic shroud | [Fade Persona](https://musicbrainz.org/recording/35d0e8fa-6327-45e8-ac68-b87e0d1f5391) | 2022 | 323 | L 5 | New |
| 123 |  | S U R V I V E | [Wardenclyffe](https://musicbrainz.org/recording/187cd69f-feec-423e-b836-81fbc83abddf) | 2016 | 910 | L 5 | New |
| 124 |  | Underworld | [I Exhale](https://musicbrainz.org/recording/691c05b0-c68a-4482-bb32-fdcd4e8ec7fb) | 2016 | 909 | L 2 | Already |
| 125 |  | Planet 1999 | [Spell](https://musicbrainz.org/recording/96d11782-881d-48ff-97bc-7e0d17636145) | 2019 | 905 | L 2 | New |
| 126 |  | Neon Indian | [Baby’s Eyes](https://musicbrainz.org/recording/ef83a250-eeab-4945-9286-02c305db32b2) | 2015 | 895 | L 9 | New |
| 127 |  | Young Fathers | [Toy](https://musicbrainz.org/recording/53598b31-2e95-4ff0-a09e-7f79745555f0) | 2018 | 887 | L 11 | New |
| 128 |  | Protomartyr | [My Children](https://musicbrainz.org/recording/d89d1c85-fe45-42d6-808b-ae17c6e0a454) | 2017 | 882 | L 6 | New |
| 129 |  | Drab Majesty | [39 by Design](https://musicbrainz.org/recording/63ede919-738a-4f76-aec2-ec2589807eba) | 2017 | 878 | L 5 | New |
| 130 |  | Drab Majesty | [Too Soon to Tell](https://musicbrainz.org/recording/62ab07ae-14c9-4ec0-b0bf-b9a78156fae2) | 2017 | 876 | L 8 | New |
| 131 |  | Holy Fuck | [Endless](https://musicbrainz.org/recording/db7d365b-b18c-44af-ba39-6ab8878b62be) | 2020 | 309 | L 1 | New |
| 132 |  | TR/ST | [Bicep](https://musicbrainz.org/recording/a3955408-ace9-4ff9-9f29-9de06ea1671f) | 2017 | 868 | L 14 | New |
| 133 |  | HEALTH | [VICTIM](https://musicbrainz.org/recording/bba8ff8f-e123-4c8e-97f8-fc8ccd469388) | 2015 | 864 | L 8 | New |
| 134 |  | Brothertiger | [High Tide](https://musicbrainz.org/recording/452f41c8-ae40-409d-85b5-f2aee9b16121) | 2015 | 855 | L 9 | New |
| 135 |  | Shook | [You Were Bigger Than Life](https://musicbrainz.org/recording/964e265a-9d7b-4751-89a6-2077fa3b8f3f) | 2016 | 831 | L 2 | New |
| 136 |  | Nabihah Iqbal | [Is This Where It Ends](https://musicbrainz.org/recording/81684a96-805c-4000-854b-f8ce75f5b83a) | 2020 | 289 | L 1 | New |
| 137 |  | Ochre | [Anaphora](https://musicbrainz.org/recording/62613882-6097-4496-99e3-9a2fde9c6481) | 2017 | 811 | L 8 | New |
| 138 |  | HEALTH | [L.A. LOOKS](https://musicbrainz.org/recording/50a184d1-5f94-436d-9e40-9400bf9b7c88) | 2015 | 805 | L 12 | New |
| 139 |  | Holy Fuck | [Moment](https://musicbrainz.org/recording/c6eec851-8104-48ac-86e4-cfe2c5e7e9e3) | 2020 | 280 | L 1 | New |
| 140 |  | Viet Cong | [Silhouettes](https://musicbrainz.org/recording/00f6e2c0-3a01-42c4-85a4-347309c8dfa0) | 2015 | 789 | L 15 | New |
| 141 |  | Young Fathers | [Wow](https://musicbrainz.org/recording/a81c88e8-e668-47c7-98b5-6ce9561ba0a5) | 2018 | 775 | L 6 | New |
| 142 | ★ | Squarepusher | [Stor Eiglass](https://musicbrainz.org/recording/ff0a3bdc-a2e6-464b-961f-8216a56b5d6d) | 2015 | 770 | L 11 | New |
| 143 |  | Pixies | [Head Carrier](https://musicbrainz.org/recording/ded755f7-94e9-4403-9659-e26fb9fbad7f) | 2016 | 767 | S 2; L 7 | New |
| 144 |  | Pixies | [Tenement Song](https://musicbrainz.org/recording/c7c8f2a9-cc7b-4611-94d5-5053e4394f92) | 2016 | 750 | S 5; L 8 | New |
| 145 |  | Bat for Lashes | [Vampires](https://musicbrainz.org/recording/a7638aad-b6c5-4f52-93cd-0df5218fd91a) | 2019 | 749 | L 7 | New |
| 146 |  | Skinshape | [After Midnight](https://musicbrainz.org/recording/013c2289-42a2-42e6-9b94-bbea46b01834) | 2018 | 729 | L 6 | New |
| 147 |  | Guerilla Toss | [Betty Dreams of Green Men](https://musicbrainz.org/recording/6210a62c-a90b-4eec-bc73-1fa0af5eacc1) | 2017 | 724 | L 1 | New |
| 148 |  | Colin Stetson | [Reborn](https://musicbrainz.org/recording/7ab3dd55-e927-401b-882f-9f3c9d3b6623) | 2018 | 720 | L 13 | New |
| 149 |  | Brainwaltzera | [Fwd: Re: late (Ref.: karoshi)](https://musicbrainz.org/recording/93f85dfa-4604-4092-be09-66889cfe1347) | 2022 | 255 | L 2 | New |
| 150 |  | Graham Kartna | [chiltonWALK.temp](https://musicbrainz.org/recording/eb217f5e-51cb-45e3-a877-cde472f0cdfc) | 2018 | 714 | L 8 | New |
| 151 |  | Goat Girl | [Where Do We Go From Here?](https://musicbrainz.org/recording/7eb09ecd-54d2-40e4-849f-4a0ed0c18488) | 2021 | 247 | L 2 | New |
| 152 |  | TVAM | [Porsche Majeure](https://musicbrainz.org/recording/40cb3bbf-efbb-4886-9a0e-5c87f73d41d1) | 2018 | 696 | L 6 | New |
| 153 |  | Viet Cong | [Newspaper Spoons](https://musicbrainz.org/recording/2fd632b7-f90c-4fc6-b263-eb40656f853d) | 2015 | 692 | L 5 | New |
| 154 |  | Viet Cong | [Pointless Experience](https://musicbrainz.org/recording/2295f65d-8f23-4f17-9eed-9024f724bbc5) | 2015 | 676 | L 8 | New |
| 155 |  | Passion Pit | [Until We Can’t (Let’s Go)](https://musicbrainz.org/recording/2d09a64e-f2a4-494a-be5e-a9edfd2c45b1) | 2015 | 662 | L 5 | Already |
| 156 |  | Twin Shadow | [Half Life](https://musicbrainz.org/recording/750586c9-4305-4be1-958e-fab1b8326085) | 2015 | 662 | L 5 | New |
| 157 |  | Eyeliner | [Toy Dog](https://musicbrainz.org/recording/bc7d8138-09a8-4b40-869f-e3297bd4b731) | 2015 | 644 | L 7 | New |
| 158 |  | BEAK> | [The Brazilian](https://musicbrainz.org/recording/520fe4a0-c9e8-454c-ab82-9a33526c9b79) | 2018 | 643 | L 4 | New |
| 159 |  | Sevdaliza | [Amandine Insensible](https://musicbrainz.org/recording/ca685fad-58fe-4ccd-81fa-45f9ff568b20) | 2015 | 635 | L 13 | New |
| 160 |  | Ben Lukas Boysen | [Golden Times 1](https://musicbrainz.org/recording/d3d062d2-6e80-4b59-913b-a6469fd58ef7) | 2016 | 626 | L 1 | New |
| 161 |  | Eyeliner | [Pinot Noir](https://musicbrainz.org/recording/7ee47b2e-cf54-40e2-b8b6-ef969a73e39d) | 2015 | 617 | L 7 | New |
| 162 |  | Puma Blue | [Already Falling](https://musicbrainz.org/recording/3fbabc16-e87e-43d0-b355-691c5a964c3a) | 2021 | 218 | L 2 | New |
| 163 |  | Ought | [Men for Miles](https://musicbrainz.org/recording/8ed385f7-469b-48c6-aa1f-6517acb30066) | 2015 | 614 | L 6 | New |
| 164 |  | Sevdaliza | [Hubris](https://musicbrainz.org/recording/2e9ba695-f16a-4d41-bac4-9bd0e1c4888f) | 2017 | 608 | L 10 | New |
| 165 |  | BEAK> | [When We Fall](https://musicbrainz.org/recording/20d20717-15a4-459e-bd89-e01bce4d3914) | 2018 | 597 | L 4 | New |
| 166 |  | Tirzah ft. Coby Sey | [Devotion](https://musicbrainz.org/recording/1aabd490-0b2c-4021-ba83-f3c2e8fefeb0) | 2018 | 573 | L 9 | New |
| 167 |  | Puma Blue | [Cherish (Furs)](https://musicbrainz.org/recording/94c78a28-f89c-43bc-8cb5-176f1f3e31b2) | 2021 | 202 | L 1 | New |
| 168 |  | The Flashbulb | [Starlight](https://musicbrainz.org/recording/439ba4fe-403e-4767-ae8d-1d951077404a) | 2017 | 568 | L 5 | New |
| 169 |  | μ‐Ziq | [Hello](https://musicbrainz.org/recording/2bda7799-3cbf-4330-bfb2-8bc912801038) | 2022 | 201 | L 5 | New |
| 170 |  | Lauren Daigle | [Almost Human](https://musicbrainz.org/recording/beabf80d-3fc2-46a3-8cc0-0f349368622f) | 2017 | 553 | L 6 | Already |
| 171 |  | TR/ST | [Iris](https://musicbrainz.org/recording/9ecf96f5-dbba-4fda-a5cf-7728837fb1b6) | 2019 | 526 | L 9 | New |
| 172 |  | bl00dwave | [Encounters](https://musicbrainz.org/recording/a45c9893-306f-4546-88a8-3d0d25666871) | 2016 | 518 | L 7 | Already |

## Conditional candidates (8)

These have checked CLAP vectors, MusicBrainz IDs and aggregate listening evidence, but **are not confirmed retraining-ready**. A successful lookup returning zero loves is distinct from a failed request; the CSV preserves both. For zero-love recordings, real listening-event histories may still supply training data, but that join was not verified here. Request failures are never counted as zero.

| # | Priority | Artist | Song | Year | Source users | User feedback | App catalogue |
|---:|:---:|---|---|---:|---:|---|---|
| 173 |  | Casino Versus Japan | [Coromiak](https://musicbrainz.org/recording/552a87d0-a325-4ade-9e48-acd0241243b6) | 2020 | 585 | L 0 | New |
| 174 |  | Ben Lukas Boysen | [Sleepers Beat Theme](https://musicbrainz.org/recording/27c00327-8bac-497b-a925-b73c281ae5e3) | 2016 | 1,542 | L 0 | New |
| 175 |  | Plaid | [C.A.](https://musicbrainz.org/recording/c66d849e-3b2c-4936-a6a6-5dda4a880ee2) | 2022 | 508 | L 0 | New |
| 176 |  | Plaid | [Perspex](https://musicbrainz.org/recording/e4fbe149-1d99-4c31-9983-605d7529be2a) | 2022 | 464 | L 0 | New |
| 177 | ★ | Toro y Moi | [Empty Nesters](https://musicbrainz.org/recording/a46fed4b-796d-48b1-a24b-831b8d718b5e) | 2015 | 984 | L 0 | New |
| 178 |  | Holy Fuck | [Near Mint](https://musicbrainz.org/recording/1d587902-48c6-420b-a8d4-ac65f48b97ea) | 2020 | 268 | L 0 | New |
| 179 |  | Brainwaltzera | [tracing Rays [reality glo]](https://musicbrainz.org/recording/8c7099bd-42a9-4cdb-8c70-cc539d7c9bb2) | 2022 | 196 | L 0 | New |
| 180 |  | The Besnard Lakes | [Raindrops](https://musicbrainz.org/recording/5f2dfbd2-5387-4c93-aa31-0e9f0009897e) | 2020 | 189 | L 0 | New |

## Sources, access and reuse

- [Pinned Clapback export](https://clapback-export.s3.us-east-1.amazonaws.com/exports/2026-10-18/manifest.json), [export documentation](https://clapback.seethroughlab.com/export). This report checks the repo's existing pinned files; it does not infer a new export from a search-engine cached “latest” page. Publisher-declared CC0 for vectors and claims; underlying music rights are separate.
- [ListenBrainz feedback API](https://listenbrainz.readthedocs.io/en/latest/users/api/recordings.html). Each CSV feedback URL retrieves positive user feedback for that exact recording, using count/offset pagination. Low-concurrency read-only probes were used; initial rate-limited reads were distinguished from successful reads and retried separately. No listener IDs are retained in these documents.
- [ListenBrainz sample archive](https://data.metabrainz.org/pub/musicbrainz/listenbrainz/sample/listenbrainz-sample-20250610-094311-full/), already downloaded and checksummed in `data/sources/listenbrainz/README.md`. Sample date: 10 June 2025. Positive feedback is preference data, not listening history.
- [ListenBrainz full dumps](https://listenbrainz.readthedocs.io/en/latest/users/listenbrainz-dumps.html) and [dataset terms](https://metabrainz.org/datasets/postgres-dumps): source for future listening-history training; not downloaded/joined for these candidates. Publisher declares CC0 for ListenBrainz.
- [Popularity API documentation](https://listenbrainz.readthedocs.io/en/latest/users/api/popularity.html), and [publisher implementation](https://github.com/metabrainz/listenbrainz-server/blob/master/listenbrainz/db/popularity.py): aggregate popularity combines ListenBrainz and MLHD. [MLHD+ terms](https://metabrainz.org/datasets/derived-dumps) restrict that listening corpus to non-commercial use. Combined counts are selection evidence, not an unrestricted user-item training matrix.
- [MusicBrainz data terms](https://musicbrainz.org/doc/About/Data_License): core metadata is CC0; supplementary tags have separate terms. Genre tags are not copied into this shortlist.

For retraining, use the actual sample or fetched user-level feedback and check the shared-user/item support thresholds. Prefer those verified sources over assuming an aggregate count proves that a compatible listening matrix is ready. The external alternative embedding datasets and their compatibility gaps are documented in the [original report](POST_2000_SONG_RESEARCH.md#other-datasets-checked); none was silently mixed into the existing CLAP bank.

Local inputs: the cached annotated and MusicBrainz inventories; the pinned Clapback vectors/claims/manifest; the existing app catalogue; the original recommendation CSV; the earlier popularity-response cache; and the ListenBrainz sample. The accompanying CSV preserves the candidate-specific count/probe results for this supplement. No application or training code was added.

Input checksums (SHA256):

- `docs/POST_2000_SONG_RESEARCH.csv`: `e7edae743766265dc53a5a57b127dcf22547af45117f642961c64a811fa755e1`
- `data/sources/clapback/manifest.json`: `87be52ff1494944ad81312fca48df9567c6a56cbe6c9104b7c80caea45d0c954`
- `data/sources/listenbrainz/recording_feedback.parquet`: `8e0f51a253af4ec35d42d83bd00cb6a7baf1493a54c4a8630b3f4d73e6c05df9`
- `data/catalogue/annotated_inventory.json`: `b4a44024032c544bf38aa568ebdb578bf12edb413899fc2d19cd7fc315263bc1`
