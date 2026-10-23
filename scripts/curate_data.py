#!/usr/bin/env python3
"""Curate an explainable workshop subset from cached public metadata and vectors."""
import argparse
import array
import collections
import csv
import gzip
import hashlib
import json
import math
import pathlib
import re
import sys
import unicodedata
import urllib.parse

from prepare_data import DATA, ROOT, fetch


def norm(s):
    return re.sub(r'[^a-z0-9]+', ' ', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()).strip()


# Editorial seed anchors, not chart statistics. Exact track matches are preferred.
ANCHORS = {
    'The Beatles': 'Come Together|Here Comes the Sun|Let It Be|Hey Jude|Yesterday|Something|Help!|A Day in the Life|Eleanor Rigby|Tomorrow Never Knows',
    'The Rolling Stones': 'Paint It Black|Gimme Shelter|Satisfaction|Angie',
    'David Bowie': 'Heroes|Space Oddity|Life on Mars?|Let’s Dance|Starman',
    'Fleetwood Mac': 'Dreams|The Chain|Go Your Own Way',
    'Pink Floyd': 'Wish You Were Here|Money|Comfortably Numb|Time',
    'Queen': 'Bohemian Rhapsody|Another One Bites the Dust|Don’t Stop Me Now',
    'ABBA': 'Dancing Queen|Gimme! Gimme! Gimme! (A Man After Midnight)',
    'Stevie Wonder': 'Superstition|Sir Duke|Isn’t She Lovely',
    'Marvin Gaye': 'What’s Going On|Sexual Healing',
    'Aretha Franklin': 'Respect|Think',
    'Nina Simone': 'Feeling Good|Sinnerman|I Put a Spell on You',
    'Miles Davis': 'So What|Blue in Green',
    'Dave Brubeck': 'Take Five', 'The Dave Brubeck Quartet': 'Take Five',
    'John Coltrane': 'My Favorite Things|Naima',
    'Johnny Cash': 'Hurt|Ring of Fire|Folsom Prison Blues',
    'Dolly Parton': 'Jolene|9 to 5', 'Bob Dylan': 'Like a Rolling Stone|Knockin’ on Heaven’s Door',
    'Simon & Garfunkel': 'The Sound of Silence|Mrs. Robinson|The Boxer',
    'Joni Mitchell': 'A Case of You|Big Yellow Taxi', 'Neil Young': 'Heart of Gold|Harvest Moon',
    'Michael Jackson': 'Billie Jean|Beat It|Thriller', 'Prince': 'Purple Rain|Kiss|When Doves Cry',
    'Madonna': 'Like a Prayer|Vogue|Frozen', 'Whitney Houston': 'I Wanna Dance with Somebody',
    'Wham!': 'Wake Me Up Before You Go-Go|Careless Whisper|Everything She Wants',
    'George Michael': 'Careless Whisper|Faith|Freedom! ’90',
    'Tears for Fears': 'Everybody Wants to Rule the World|Mad World|Shout',
    'Depeche Mode': 'Enjoy the Silence|Personal Jesus|Just Can’t Get Enough',
    'The Cure': 'Friday I’m in Love|Just Like Heaven|Boys Don’t Cry|Lovesong',
    'New Order': 'Blue Monday|Bizarre Love Triangle', 'Joy Division': 'Love Will Tear Us Apart',
    'Nirvana': 'Smells Like Teen Spirit|Come as You Are|Lithium',
    'Radiohead': 'Creep|No Surprises|Karma Police|Everything in Its Right Place|Idioteque',
    'Pixies': 'Where Is My Mind?|Here Comes Your Man|Debaser',
    'R.E.M.': 'Losing My Religion|Everybody Hurts',
    'Oasis': 'Wonderwall|Don’t Look Back in Anger', 'Blur': 'Song 2|Girls & Boys',
    'Red Hot Chili Peppers': 'Under the Bridge|Californication',
    'Daft Punk': 'Get Lucky|One More Time|Around the World|Harder Better Faster Stronger',
    'Massive Attack': 'Teardrop|Unfinished Sympathy|Angel', 'Portishead': 'Glory Box|Sour Times',
    'Air': 'All I Need|Sexy Boy|La femme d’argent', 'Moby': 'Porcelain|Natural Blues',
    'The Chemical Brothers': 'Hey Boy Hey Girl|Galvanize|Block Rockin’ Beats',
    'The Prodigy': 'Firestarter|Breathe|Smack My Bitch Up', 'Fatboy Slim': 'Praise You|Right Here Right Now',
    'Kraftwerk': 'The Model|Das Model|Autobahn|Computer Love',
    'Aphex Twin': 'Avril 14th|Windowlicker|Xtal|Alberto Balsalm',
    'Björk': 'Army of Me|Hyperballad|It’s Oh So Quiet|Jóga',
    'Gorillaz': 'Feel Good Inc.|Clint Eastwood|On Melancholy Hill',
    'MGMT': 'Kids|Electric Feel|Time to Pretend', 'M83': 'Midnight City|Wait',
    'Tame Impala': 'The Less I Know the Better|Let It Happen',
    'Arctic Monkeys': 'Do I Wanna Know?|I Bet You Look Good on the Dancefloor',
    'The White Stripes': 'Seven Nation Army|Fell in Love with a Girl',
    'The Killers': 'Mr. Brightside|Somebody Told Me',
    'Amy Winehouse': 'Back to Black|Rehab|You Know I’m No Good',
    'Adele': 'Rolling in the Deep|Someone Like You',
    'Billie Eilish': 'bad guy|everything i wanted', 'Lana Del Rey': 'Video Games|Summertime Sadness',
    'Taylor Swift': 'Shake It Off|Anti-Hero|Blank Space',
    'OutKast': 'Hey Ya!|Ms. Jackson', 'Eminem': 'Lose Yourself|Stan',
    'Gnarls Barkley': 'Crazy', 'Beastie Boys': 'Sabotage|Intergalactic',
    'The xx': 'Intro|Crystalised', 'LCD Soundsystem': 'Dance Yrself Clean|Someone Great',
    'Bon Iver': 'Skinny Love|Holocene', 'Sufjan Stevens': 'Chicago|Mystery of Love',
}
for _artist, _tracks in {
    'The Police': 'Roxanne|Message in a Bottle|Every Breath You Take|Every Little Thing She Does Is Magic|Don’t Stand So Close to Me|King of Pain',
    'Talking Heads': 'Once in a Lifetime|Burning Down the House|This Must Be the Place (Naive Melody)|Road to Nowhere|Take Me to the River',
    'David Bowie': 'Fame|Fashion|Golden Years|China Girl|Moonage Daydream',
    'Queen': 'Somebody to Love|Killer Queen|Under Pressure|We Are the Champions|I Want to Break Free|Bicycle Race',
    'The Beatles': 'A Hard Day’s Night|All You Need Is Love|Blackbird|Get Back|Day Tripper|Can’t Buy Me Love|All My Loving|Eight Days a Week',
    'Michael Jackson': 'Rock With You|Off the Wall|Human Nature|Wanna Be Startin’ Somethin’',
    'Prince': 'Let’s Go Crazy|Sign o’ the Times|1999|Little Red Corvette',
    'Earth, Wind & Fire': 'September|Boogie Wonderland|Let’s Groove|Shining Star|Sing a Song',
    'Stevie Wonder': 'I Just Called to Say I Love You', 'The Rolling Stones': 'She’s a Rainbow',
    'Fleetwood Mac': 'Little Lies|Big Love|Tusk|Sara',
    'Pink Floyd': 'Welcome to the Machine|One of These Days|Goodbye Blue Sky',
    'Gorillaz': '19-2000|Tomorrow Comes Today|Dare|Dirty Harry|Rhinestone Eyes',
    'Beck': 'Loser|Where It’s At|Devils Haircut|The New Pollution',
    'Radiohead': 'Paranoid Android|Fake Plastic Trees|High and Dry|Exit Music (for a Film)|Weird Fishes/Arpeggi|Reckoner',
    'The Cure': 'A Forest|Close to Me|In Between Days|Lullaby|Pictures of You',
    'Depeche Mode': 'Everything Counts|Never Let Me Down Again|Policy of Truth|Walking in My Shoes|Precious|It’s No Good',
    'New Order': 'True Faith|Age of Consent|Regret|Temptation',
    'Pet Shop Boys': 'West End Girls|It’s a Sin|Always on My Mind|Go West|What Have I Done to Deserve This?',
    'Erasure': 'A Little Respect|Always|Sometimes|Chains of Love|Chorus',
    'Moby': 'Why Does My Heart Feel So Bad?|Extreme Ways|Go|We Are All Made of Stars',
    'Massive Attack': 'Protection|Safe From Harm|Paradise Circus|Risingson',
    'Portishead': 'All Mine|The Rip|Wandering Star|Machine Gun',
    'Daft Punk': 'Da Funk|Digital Love|Technologic|Lose Yourself to Dance|Doin’ It Right',
    'The Chemical Brothers': 'Star Guitar|Setting Sun|Let Forever Be|Believe',
    'The Prodigy': 'Spitfire|Out of Space|No Good (Start the Dance)|Voodoo People',
    'Fatboy Slim': 'Weapon of Choice|The Rockafeller Skank|Gangster Trippin’|Sunset (Bird of Prey)',
    'Röyksopp': 'Eple|Poor Leno|Remind Me|What Else Is There?|Happy Up Here',
    'Air': 'Cherry Blossom Girl|Kelly Watch the Stars|Kelly Watch the Stars!',
    'Aphex Twin': 'Flim|Digeridoo|Come to Daddy (Pappy mix)',
    'Björk': 'Bachelorette|Isobel|All Is Full of Love|Big Time Sensuality|Hidden Place',
    'M83': 'Kim & Jessie|We Own the Sky|Outro',
    'Nirvana': 'Rape Me|Heart-Shaped Box|All Apologies|In Bloom|About a Girl',
    'The White Stripes': 'Fell in Love With a Girl|Hotel Yorba|We’re Going to Be Friends|Dead Leaves and the Dirty Ground',
    'LCD Soundsystem': 'All My Friends|Daft Punk Is Playing at My House|Losing My Edge|I Can Change',
    'Bob Marley & The Wailers': 'Three Little Birds|Is This Love|Could You Be Loved|Redemption Song|Jamming|Buffalo Soldier',
    'Tears for Fears': 'Head Over Heels|Sowing the Seeds of Love|Pale Shelter',
    'Genesis': 'Invisible Touch|Land of Confusion|I Can’t Dance|Carpet Crawlers',
    'Phil Collins': 'In the Air Tonight|Another Day in Paradise|You Can’t Hurry Love|Sussudio|One More Night',
    'The xx': 'Islands|VCR|Shelter',
    'The Clash': 'London Calling|Should I Stay or Should I Go|Rock the Casbah|Train in Vain',
    'The Smiths': 'There Is a Light That Never Goes Out|This Charming Man|How Soon Is Now?',
    'Nine Inch Nails': 'Closer|Hurt|Head Like a Hole|The Hand That Feeds',
    'Cocteau Twins': 'Heaven or Las Vegas|Cherry-Coloured Funk',
    'Kate Bush': 'Running Up That Hill (A Deal with God)|Wuthering Heights|Cloudbusting',
    'Soft Cell': 'Tainted Love', 'Gary Numan': 'Cars',
    'Snoop Dogg': 'Who Am I (What’s My Name)?|Gin and Juice|Drop It Like It’s Hot',
    'Etta James': 'At Last', 'Stan Getz': 'The Girl From Ipanema|Corcovado (Quiet Nights of Quiet Stars)',
    'Astrud Gilberto': 'Fly Me to the Moon', 'Herb Alpert & the Tijuana Brass': 'A Taste of Honey|Spanish Flea',
    'Patsy Cline': 'Back in Baby’s Arms|Crazy', 'Cat Stevens': 'The Wind|Here Comes My Baby',
    'Donovan': 'Season of the Witch', 'Jefferson Airplane': 'White Rabbit',
    'The Doors': 'People Are Strange|Light My Fire|The End',
    'Creedence Clearwater Revival': 'Bad Moon Rising|I Put a Spell on You',
    'Commodores': 'Nightshift|Machine Gun', 'Donna Summer': 'I Feel Love',
    'Bee Gees': 'Stayin’ Alive', 'Dusty Springfield': 'Son of a Preacher Man',
}.items():
    ANCHORS[_artist] = ANCHORS.get(_artist, '') + '|' + _tracks

KNOWN = {norm(x) for x in ANCHORS} | {norm(x) for x in '''Led Zeppelin|AC/DC|Elton John|Billy Joel|Elvis Presley|The Beach Boys|The Doors|Jimi Hendrix|Janis Joplin|Santana|Eric Clapton|Eagles|Dire Straits|The Police|Sting|Genesis|Phil Collins|Peter Gabriel|Paul Simon|Paul McCartney|John Lennon|George Harrison|Lou Reed|Leonard Cohen|Tom Waits|Nick Cave & the Bad Seeds|Talking Heads|Duran Duran|Pet Shop Boys|Eurythmics|Erasure|a-ha|Tina Turner|Sade|Seal|Simply Red|Norah Jones|Diana Krall|Ella Fitzgerald|Louis Armstrong|Herbie Hancock|Duke Ellington|Chet Baker|Bill Evans|B.B. King|Muddy Waters|Ray Charles|James Brown|Al Green|Otis Redding|Curtis Mayfield|Earth, Wind & Fire|Chic|Parliament|Funkadelic|Donna Summer|Bee Gees|Bob Marley & The Wailers|Bob Marley|Willie Nelson|Patsy Cline|John Denver|Emmylou Harris|Tracy Chapman|Cat Stevens|James Taylor|Carole King|Nick Drake|Fleet Foxes|Beck|Wilco|Bright Eyes|Belle and Sebastian|The Smiths|Morrissey|The Smashing Pumpkins|Pearl Jam|Soundgarden|Foo Fighters|Green Day|The Offspring|Weezer|No Doubt|Garbage|Nine Inch Nails|Marilyn Manson|Rage Against the Machine|Metallica|Black Sabbath|Iron Maiden|Judas Priest|The Clash|Ramones|Sex Pistols|Iggy Pop|Sonic Youth|Pavement|Pulp|Suede|The Strokes|Interpol|Yeah Yeah Yeahs|Franz Ferdinand|Bloc Party|The National|Arcade Fire|Florence + the Machine|Muse|Coldplay|U2|Keane|Snow Patrol|Placebo|Editors|Vampire Weekend|Phoenix|Foster the People|Alt-J|alt-J|The Black Keys|Jack White|PJ Harvey|Tori Amos|Alanis Morissette|Kate Bush|Siouxsie and the Banshees|Cocteau Twins|Slowdive|My Bloody Valentine|The Jesus and Mary Chain|Mazzy Star|Sigur Rós|Mogwai|Godspeed You! Black Emperor|Explosions in the Sky|Brian Eno|Vangelis|Jean-Michel Jarre|Tangerine Dream|Enya|Enigma|Hans Zimmer|Ludovico Einaudi|Max Richter|Ólafur Arnalds|Nils Frahm|Philip Glass|Steve Reich|Ryuichi Sakamoto|Yann Tiersen|Boards of Canada|Autechre|Squarepusher|Four Tet|Caribou|Bonobo|Tycho|Jon Hopkins|Röyksopp|Bicep|Disclosure|Justice|Simian Mobile Disco|Basement Jaxx|Groove Armada|Faithless|Underworld|Orbital|The Orb|808 State|Leftfield|The Future Sound of London|Goldie|Roni Size|Pendulum|Chase & Status|The Crystal Method|Deadmau5|deadmau5|Avicii|Calvin Harris|David Guetta|Tiësto|Armin van Buuren|Paul van Dyk|Paul Oakenfold|Skrillex|Diplo|The Knife|Fever Ray|Hot Chip|Cut Copy|Metronomy|Little Dragon|CHVRCHES|Purity Ring|Grimes|FKA twigs|James Blake|Jamie xx|Jamie Lidell|Thievery Corporation|DJ Shadow|UNKLE|Tricky|Morcheeba|Zero 7|Beyoncé|Rihanna|Britney Spears|Lady Gaga|Katy Perry|Dua Lipa|Lorde|Robyn|Justin Timberlake|Justin Bieber|The Weeknd|Frank Ocean|SZA|Kendrick Lamar|Kanye West|JAY-Z|Nas|2Pac|The Notorious B.I.G.|Wu-Tang Clan|A Tribe Called Quest|De La Soul|Public Enemy|N.W.A|Dr. Dre|Snoop Dogg|Missy Elliott|Lauryn Hill|The Fugees|Fugees|M.I.A.|Run-D.M.C.|Nujabes|J Dilla|Flying Lotus|Nicolas Jaar|Ninja Tune|Tosca|Kruder & Dorfmeister'''.split('|')}

ANCHOR_KEYS = {(norm(a), norm(t)) for a, ts in ANCHORS.items() for t in ts.split('|')}

FAMILIES = {
    'jazz_blues': ['jazz', 'blues', 'swing', 'bebop', 'bossa nova', 'soul-jazz', 'cool jazz', 'jazz fusion', 'acid jazz', 'vocal jazz', 'jazz-funk'],
    'country_folk_acoustic': ['country', 'folk', 'americana', 'bluegrass', 'singer-songwriter', 'contemporary folk', 'folk rock', 'acoustic'],
    'funk_soul_rnb': ['funk', 'soul', 'r&b', 'rhythm and blues', 'neo-soul', 'disco', 'motown'],
    'psychedelic': ['psychedelic', 'psychedelic rock', 'psychedelic pop', 'space rock', 'neo-psychedelia', 'psychedelic folk'],
    'classic_rock': ['classic rock', 'rock and roll', 'rock & roll', 'hard rock', 'progressive rock', 'blues rock', 'glam rock', 'heavy metal', 'metal', 'progressive metal'],
    'indie_alternative': ['indie rock', 'alternative rock', 'indie pop', 'post-punk', 'punk', 'shoegaze', 'dream pop', 'grunge', 'post-rock', 'industrial rock', 'gothic rock'],
    'pop_smooth': ['pop', 'pop rock', 'synth-pop', 'synthpop', 'new wave', 'soft rock', 'art pop', 'chamber pop', 'baroque pop'],
    'electronic_dance': ['house', 'techno', 'trance', 'drum and bass', 'drum n bass', 'breakbeat', 'big beat', 'edm', 'dance', 'electro house', 'dubstep', 'electro', 'electropop'],
    'electronic_experimental': ['idm', 'electronica', 'experimental', 'electronic', 'glitch', 'indietronica', 'trip hop', 'downtempo', 'leftfield'],
    'ambient_instrumental': ['ambient', 'classical', 'modern classical', 'contemporary classical', 'minimalism', 'new age', 'soundtrack', 'score'],
    'hiphop_reggae': ['hip hop', 'hip-hop', 'rap', 'reggae', 'dub', 'ska', 'ska punk'],
}
QUOTAS = {'jazz_blues': 100, 'country_folk_acoustic': 110, 'funk_soul_rnb': 110,
          'psychedelic': 100, 'classic_rock': 140, 'indie_alternative': 200,
          'pop_smooth': 130, 'electronic_dance': 170, 'electronic_experimental': 180,
          'ambient_instrumental': 160, 'hiphop_reggae': 100}
DECADE_WEIGHTS = {1960: .12, 1970: .15, 1980: .15, 1990: .18, 2000: .19, 2010: .18, 2020: .03}


def inventory():
    rows = []
    for path in sorted((DATA / 'sources' / 'musicbrainz').glob('*.gz')):
        try:
            rows.extend(json.loads(gzip.decompress(path.read_bytes())).get('recordings', []))
        except (EOFError, OSError):
            continue
    return {r['id']: r for r in rows}


def describe(raw):
    credit = [c for c in raw.get('artist-credit', []) if isinstance(c, dict) and 'artist' in c]
    artist = ''.join(c.get('name', c['artist']['name']) + c.get('joinphrase', '') for c in credit)
    primary = credit[0]['artist'] if credit else {}
    date = raw.get('first-release-date', '')
    year = int(date[:4]) if date[:4].isdigit() else None
    votes = {t['name'].lower(): max(0, t.get('count', 0)) for t in raw.get('tags', []) if t.get('count', 0) > 0}
    tags = sorted(votes)
    # Isolated low-vote tags must not override stronger genre evidence.
    def evidence(terms):
        scores = [votes[t] * (.55 if t in ('pop', 'electronic', 'experimental', 'dance', 'soundtrack', 'score') else 1) for t in terms if t in votes]
        return max(scores, default=0) + .2 * sum(scores)
    matches = {family: evidence(terms) for family, terms in FAMILIES.items()}
    matches = {k: v for k, v in matches.items() if v}
    family = max(matches, key=matches.get) if matches else 'unclassified'
    basis = 'positive MusicBrainz tag votes, with generic tags downweighted'
    if family == 'unclassified' and 'rock' in votes:
        family = 'classic_rock' if year and year < 1980 else 'indie_alternative'
        matches[family] = votes['rock']
        basis = 'generic rock tag and recording decade; broad grouping only'
    if norm(primary.get('name', artist)) == norm('Björk') and norm(raw['title']) == norm('It’s Oh So Quiet'):
        family = 'jazz_blues'
        matches[family] = max(matches.values(), default=1)
        basis = 'editorial track override: swing/big-band arrangement'
    primary_name = primary.get('name', artist)
    anchor = (norm(primary_name), norm(raw['title'])) in ANCHOR_KEYS
    familiarity = 'recognisable_anchor' if anchor else ('established_artist_deeper_cut' if norm(primary_name) in KNOWN else 'discovery_candidate')
    title_text = norm(raw['title'] + ' ' + raw.get('disambiguation', ''))
    reasons = []
    if year is None or not 1960 <= year <= 2022:
        reasons.append('outside_1960_2022_or_unknown_date')
    length = raw.get('length')
    if length is None or not 75000 <= length <= 720000:
        reasons.append('duration_outside_75s_12min_or_missing')
    if not primary or primary.get('name') in ('[unknown]', '[no artist]', 'Various Artists'):
        reasons.append('missing_or_unsuitable_artist')
    if primary.get('name') in {'Monty Python', 'George Carlin', 'Richard Pryor', 'Bill Hicks', 'Eddie Izzard'}:
        if norm(raw['title']) != norm('Always Look on the Bright Side of Life'):
            reasons.append('spoken_comedy_catalogue_excluded')
    if re.search(r'\b(interview|commentary|karaoke|spoken word|podcast|rehearsal|demo|skit)\b', title_text):
        reasons.append('nonstandard_or_spoken_recording')
    if (re.search(r'\b(live|concert)\b', norm(raw.get('disambiguation', '')))
            or re.search(r'[\[(][^\])]*\b(live|concert)\b', raw['title'], re.I)):
        reasons.append('live_version_excluded_for_consistency')
    return {'recording_mbid': raw['id'], 'title': raw['title'], 'artist': artist,
            'primary_artist': primary_name, 'primary_artist_mbid': primary.get('id'),
            'year': year, 'first_release_date': date, 'duration_seconds': round(length / 1000, 3) if length else None,
            'decade': (year // 10) * 10 if year else None,
            'tags': tags, 'tag_votes': votes, 'style_families': list(matches), 'style_family_scores': matches, 'primary_style_family': family,
            'style_assignment_basis': basis,
            'familiarity_band': familiarity, 'is_editorial_anchor': anchor,
            'familiarity_basis': 'editorial estimate; not measured popularity or listener familiarity',
            'disambiguation': raw.get('disambiguation', ''), 'exclusion_reasons': reasons,
            'musicbrainz_url': 'https://musicbrainz.org/recording/' + raw['id'],
            'youtube_search_url': 'https://www.youtube.com/results?' + urllib.parse.urlencode({'search_query': artist + ' ' + raw['title']}),
            'spotify_search_url': 'https://open.spotify.com/search/' + urllib.parse.quote(artist + ' ' + raw['title'], safe='')}


def choose(rows, target, artist_cap=6):
    pool = [r for r in rows if not r['exclusion_reasons'] and r['primary_style_family'] != 'unclassified']
    # Prefer the earliest eligible dated recording for duplicate artist/title pairs.
    unique = {}
    for row in sorted(pool, key=lambda r: (r['year'], r['recording_mbid'])):
        unique.setdefault((row['primary_artist_mbid'], norm(row['title'])), row)
    pool = list(unique.values())
    selected = []
    used = set()
    artists = collections.Counter()
    decades = collections.Counter()
    families = collections.Counter()
    bands = collections.Counter()
    titles = set()
    total_quota = sum(QUOTAS.values())
    prepared = [(r, r['recording_mbid'], r['primary_artist_mbid'],
                 (r['primary_artist_mbid'], norm(r['title'])),
                 hashlib.sha256(r['recording_mbid'].encode()).hexdigest()) for r in pool]
    # Preserve recognisable entry points before filling diversity quotas.
    anchors = sorted([r for r in pool if r['is_editorial_anchor']], key=lambda r: (r['primary_artist'], r['title'], r['year'], r['recording_mbid']))
    for row in anchors:
        aid = row['primary_artist_mbid']
        key = (aid, norm(row['title']))
        if artists[aid] >= artist_cap or key in titles or len(selected) >= target:
            continue
        selected.append(row)
        used.add(row['recording_mbid'])
        artists[aid] += 1
        decades[row['decade']] += 1
        families[row['primary_style_family']] += 1
        bands[row['familiarity_band']] += 1
        titles.add(key)
    # Deterministic greedy balancing; musical coverage and artist variety are explicit.
    while pool and len(selected) < target:
        candidates = []
        for row, mbid, aid, duplicate_key, tie in prepared:
            if mbid in used or artists[aid] >= artist_cap or duplicate_key in titles:
                continue
            family = row['primary_style_family']
            fquota = target * QUOTAS[family] / total_quota
            dquota = target * DECADE_WEIGHTS.get(row['decade'], .01)
            bquota = target * {'recognisable_anchor': .18, 'established_artist_deeper_cut': .42, 'discovery_candidate': .40}[row['familiarity_band']]
            score = (4 * max(-1, (fquota - families[family]) / fquota)
                     + 2 * max(-1, (dquota - decades[row['decade']]) / dquota)
                     + 1.5 * max(-1, (bquota - bands[row['familiarity_band']]) / bquota)
                     + (1 if row['is_editorial_anchor'] else 0) - artists[aid] * .25)
            candidates.append((score, tie, row))
        if not candidates:
            break
        row = max(candidates, key=lambda x: (x[0], x[1]))[2]
        selected.append(row)
        used.add(row['recording_mbid'])
        artists[row['primary_artist_mbid']] += 1
        decades[row['decade']] += 1
        families[row['primary_style_family']] += 1
        bands[row['familiarity_band']] += 1
        titles.add((row['primary_artist_mbid'], norm(row['title'])))
    return selected


def plan(target):
    records = [describe(r) for r in inventory().values()]
    directory = DATA / 'catalogue'
    directory.mkdir(parents=True, exist_ok=True)
    (directory / 'annotated_inventory.json').write_text(json.dumps(records, ensure_ascii=False, indent=2))
    # More candidates than final tracks permits missing AcousticBrainz data.
    candidates = choose(records, math.ceil(target * 1.5), artist_cap=6)
    (directory / 'candidates.json').write_text(json.dumps(candidates, ensure_ascii=False, indent=2))
    print('Inventory:', len(records), 'eligible:', sum(not r['exclusion_reasons'] for r in records), 'candidates:', len(candidates), flush=True)
    for field in ['primary_style_family', 'decade', 'familiarity_band']:
        print(field, dict(collections.Counter(r[field] for r in candidates)), flush=True)


def features():
    candidates = json.loads((DATA / 'catalogue' / 'candidates.json').read_text())
    directory = DATA / 'sources' / 'acousticbrainz'
    directory.mkdir(parents=True, exist_ok=True)
    failures = []
    for start in range(0, len(candidates), 25):
        batch = [r['recording_mbid'] for r in candidates[start:start+25]]
        for kind in ['low-level', 'high-level']:
            missing = [mbid for mbid in batch if not (directory / kind / (mbid + '.json.gz')).exists()]
            if not missing:
                continue
            params = {'recording_ids': ';'.join(missing)}
            url = 'https://acousticbrainz.org/api/v1/' + kind + '?' + urllib.parse.urlencode(params)
            name = hashlib.sha256(url.encode()).hexdigest()[:20]
            temporary = directory / 'batches' / (name + '.json')
            try:
                result = json.loads(fetch(url, temporary, interval=1.5))
                dest = directory / kind
                dest.mkdir(parents=True, exist_ok=True)
                for mbid in missing:
                    documents = result.get(mbid, {})
                    record = documents.get('0') or next(iter(documents.values()), None)
                    (dest / (mbid + '.json.gz')).write_bytes(gzip.compress(json.dumps(record, ensure_ascii=False).encode()))
                temporary.unlink()
            except Exception as exc:
                failures.append({'ids': missing, 'kind': kind, 'error': str(exc)})
                print('Feature batch failure:', kind, str(exc), flush=True)
        if start % 250 == 0 or start + 25 >= len(candidates):
            print(f'AcousticBrainz: {min(start+25, len(candidates))}/{len(candidates)} candidates checked', flush=True)
    (directory / 'fetch_failures.json').write_text(json.dumps(failures, indent=2))


def getpath(obj, path):
    for part in path.split('.'):
        if not isinstance(obj, dict):
            return None
        obj = obj.get(part)
    return obj


def compact(low, high):
    paths = ['rhythm.bpm', 'rhythm.danceability', 'rhythm.onset_rate',
             'rhythm.bpm_histogram_first_peak_bpm', 'rhythm.bpm_histogram_second_peak_bpm',
             'lowlevel.average_loudness', 'lowlevel.dynamic_complexity',
             'lowlevel.spectral_centroid.mean', 'lowlevel.spectral_centroid.var',
             'lowlevel.spectral_rolloff.mean', 'lowlevel.spectral_flux.mean',
             'lowlevel.zerocrossingrate.mean', 'lowlevel.spectral_complexity.mean',
             'lowlevel.dissonance.mean', 'lowlevel.mfcc.mean', 'lowlevel.mfcc.cov',
             'tonal.hpcp.mean', 'tonal.chords_changes_rate', 'tonal.chords_strength.mean',
             'tonal.key_key', 'tonal.key_scale', 'tonal.key_strength',
             'tonal.key_edma.key', 'tonal.key_edma.scale', 'tonal.key_edma.strength']
    measurements = {p: getpath(low, p) for p in paths if getpath(low, p) is not None}
    predictions = {k: {'value': v.get('value'), 'probability': v.get('probability'), 'all': v.get('all')}
                   for k, v in (high or {}).get('highlevel', {}).items() if k != 'gender'}
    return {'measurements': measurements, 'predictions': predictions,
            'analysis_version': low.get('metadata', {}).get('version'),
            'audio_properties': low.get('metadata', {}).get('audio_properties'),
            'source_submission_offset': 0}


def build(target):
    rows = json.loads((DATA / 'catalogue' / 'candidates.json').read_text())
    usable = []
    features_by_id = {}
    quality_exclusions = []
    for row in rows:
        mbid = row['recording_mbid']
        path = DATA / 'sources' / 'acousticbrainz' / 'low-level' / (mbid + '.json.gz')
        if not path.exists():
            continue
        low = json.loads(gzip.decompress(path.read_bytes()))
        if not low:
            continue
        high_path = DATA / 'sources' / 'acousticbrainz' / 'high-level' / (mbid + '.json.gz')
        high = json.loads(gzip.decompress(high_path.read_bytes())) if high_path.exists() else None
        f = compact(low, high)
        audio_length = (f['audio_properties'] or {}).get('length')
        if audio_length and abs(audio_length - row['duration_seconds']) > max(15, row['duration_seconds'] * .15):
            quality_exclusions.append({'recording_mbid': mbid, 'reason': 'AcousticBrainz duration differs from catalogue by over 15 seconds and 15%', 'metadata_seconds': row['duration_seconds'], 'analysis_seconds': audio_length})
            continue
        if not all(p in f['measurements'] for p in ['rhythm.bpm', 'rhythm.onset_rate', 'lowlevel.mfcc.mean']):
            continue
        features_by_id[mbid] = f
        usable.append({**row, 'has_highlevel_predictions': bool(f['predictions'])})
    selected = choose(usable, target)
    (DATA / 'catalogue' / 'quality_exclusions.json').write_text(json.dumps(quality_exclusions, indent=2))
    out = DATA / 'workshop'
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((DATA / 'sources' / 'clapback' / 'manifest.json').read_text())
    claim_path = DATA / 'sources' / 'clapback' / manifest['claims']['file']
    with gzip.open(claim_path, 'rt') as handle:
        claims = list(csv.DictReader(handle))
    chosen_ids = {r['recording_mbid'] for r in selected}
    hash_claims = collections.defaultdict(list)
    for c in claims:
        hash_claims[c['fingerprint_hash']].append(c)
    options = collections.defaultdict(list)
    with gzip.open(DATA / 'sources' / 'clapback' / manifest['embeddings'][0]['file'], 'rt') as handle:
        for v in csv.DictReader(handle):
            cs = hash_claims[v['fingerprint_hash']]
            if not cs:
                continue
            # Reject tied conflicting recording claims rather than silently choosing a name.
            cs = sorted(cs, key=lambda c: (-int(c['claim_count']), c['recording_mbid']))
            if len(cs) > 1 and int(cs[0]['claim_count']) == int(cs[1]['claim_count']):
                continue
            c = cs[0]
            if c['recording_mbid'] in chosen_ids:
                options[c['recording_mbid']].append((int(c['claim_count']), int(v['contributor_count']), v))
    final = []
    matrix = array.array('f')
    full = []
    for row in selected:
        mbid = row['recording_mbid']
        if not options[mbid]:
            continue
        claim_count, contributor_count, v = sorted(options[mbid], key=lambda x: (-x[0], -x[1], x[2]['fingerprint_hash']))[0]
        vector = json.loads(v['embedding'])
        if len(vector) != 512 or not all(math.isfinite(x) for x in vector):
            raise ValueError('Invalid vector for ' + mbid)
        length = math.sqrt(sum(x*x for x in vector))
        if not .999 <= length <= 1.001:
            raise ValueError('Non-unit vector for ' + mbid)
        final.append({**row, 'embedding_index': len(final), 'clap_fingerprint_hash': v['fingerprint_hash'],
                      'clap_pipeline_version': v['pipeline_version'], 'recording_claim_count': claim_count,
                      'vector_contributor_count': contributor_count,
                      'acousticbrainz_lowlevel_url': f'https://acousticbrainz.org/api/v1/{mbid}/low-level?n=0'})
        matrix.extend(vector)
        full.append({'recording_mbid': mbid, 'embedding': vector})
    if sys.byteorder != 'little':
        matrix.byteswap()
    (out / 'clap_embeddings.f32').write_bytes(matrix.tobytes())
    (out / 'songs.json').write_text(json.dumps(final, ensure_ascii=False, indent=2))
    with (out / 'songs.csv').open('w', newline='') as handle:
        fields = ['embedding_index', 'recording_mbid', 'artist', 'title', 'year', 'primary_style_family', 'familiarity_band', 'tags', 'has_highlevel_predictions', 'youtube_search_url', 'spotify_search_url']
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction='ignore');writer.writeheader()
        for row in final:
            writer.writerow({**row, 'tags': '; '.join(row['tags'])})
    (out / 'features.json').write_text(json.dumps({r['recording_mbid']: features_by_id[r['recording_mbid']] for r in final}, ensure_ascii=False, indent=2))
    (out / 'clap_embeddings.json.gz').write_bytes(gzip.compress(json.dumps(full).encode()))
    licence_text = (DATA / 'README.md').read_text().split('## Licences and attribution\n', 1)[1].split('## Reproducing preparation', 1)[0]
    (out / 'ATTRIBUTION.md').write_text('# Workshop data attribution\n\n' + licence_text.strip() + '\n')
    stats = {'songs': len(final), 'artists': len({r['primary_artist_mbid'] for r in final}),
             'highlevel_available': sum(r['has_highlevel_predictions'] for r in final),
             'styles': dict(collections.Counter(r['primary_style_family'] for r in final)),
             'decades': dict(collections.Counter(r['decade'] for r in final)),
             'familiarity_bands': dict(collections.Counter(r['familiarity_band'] for r in final)),
             'max_tracks_per_artist': max(collections.Counter(r['primary_artist_mbid'] for r in final).values(), default=0),
             'candidate_count': len(rows), 'candidates_with_usable_acousticbrainz': len(usable)}
    files = {p.name: {'bytes': p.stat().st_size, 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()} for p in out.iterdir() if p.is_file() and p.name != 'manifest.json'}
    release = {'schema_version': 1, 'source_snapshot': manifest['generated'],
               'pipeline_version': manifest['embeddings'][0]['pipeline_version'],
               'embedding_format': {'file': 'clap_embeddings.f32', 'dtype': 'float32', 'byte_order': 'little', 'shape': [len(final), 512], 'row_order': 'songs.json embedding_index'},
               'selection': {'target': target, 'artist_cap': 6, 'year_range': [1960, 2022], 'method': 'deterministic editorial anchors and genre/decade/familiarity balancing'},
               'statistics': stats, 'files': files}
    (out / 'manifest.json').write_text(json.dumps(release, indent=2))
    print(json.dumps(stats, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['plan', 'features', 'build'])
    parser.add_argument('--target', type=int, default=1500)
    args = parser.parse_args()
    if args.stage == 'plan': plan(args.target)
    elif args.stage == 'features': features()
    else: build(args.target)
