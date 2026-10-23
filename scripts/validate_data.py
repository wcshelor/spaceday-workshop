#!/usr/bin/env python3
"""Validate actual data integrity and write a human-readable coverage audit."""
import array
import collections
import csv
import gzip
import hashlib
import json
import math
import pathlib
import sys

from curate_data import DATA, norm


def main():
    out = DATA / 'workshop'
    manifest = json.loads((out / 'manifest.json').read_text())
    songs = json.loads((out / 'songs.json').read_text())
    features = json.loads((out / 'features.json').read_text())
    ids = [r['recording_mbid'] for r in songs]
    errors = []
    checks = []

    def check(condition, description):
        (checks if condition else errors).append(description)

    check(1000 <= len(songs) <= 2000, 'Workshop contains 1,000–2,000 songs')
    check(len(ids) == len(set(ids)), 'Recording IDs are unique')
    check(set(ids) == set(features), 'Every selected song has an aligned feature record')
    check([r['embedding_index'] for r in songs] == list(range(len(songs))), 'Embedding row indexes are consecutive')
    check(all(1960 <= r['year'] <= 2022 for r in songs), 'All recording dates are within the agreed range')
    counts = collections.Counter(r['primary_artist_mbid'] for r in songs)
    check(max(counts.values(), default=0) <= 6, 'No primary artist contributes more than six recordings')
    pairs = [(r['primary_artist_mbid'], norm(r['title'])) for r in songs]
    check(len(pairs) == len(set(pairs)), 'No duplicate primary-artist/title pairs')
    check(all(r['clap_pipeline_version'] == manifest['pipeline_version'] for r in songs), 'All vectors use the same declared pipeline')
    values = array.array('f')
    values.frombytes((out / 'clap_embeddings.f32').read_bytes())
    if sys.byteorder != 'little':
        values.byteswap()
    check(len(values) == len(songs) * 512, 'Binary matrix shape matches catalogue')
    check(all(math.isfinite(x) for x in values), 'All embedding values are finite')
    norms = [math.sqrt(sum(x*x for x in values[i*512:(i+1)*512])) for i in range(len(songs))]
    check(all(abs(n-1) < 1e-5 for n in norms), 'Stored float32 vectors remain unit-normalised')
    readable = json.loads(gzip.decompress((out / 'clap_embeddings.json.gz').read_bytes()))
    check([r['recording_mbid'] for r in readable] == ids, 'Readable-vector alternative uses the same recording order')
    check(all(abs(x-values[i*512+j]) < 1e-7 for i, r in enumerate(readable) for j, x in enumerate(r['embedding'])), 'Readable and binary vectors agree at float32 precision')
    for name, detail in manifest['files'].items():
        blob = (out / name).read_bytes()
        check(len(blob) == detail['bytes'] and hashlib.sha256(blob).hexdigest() == detail['sha256'], 'Checksum and size: ' + name)
    check(all(not r['exclusion_reasons'] for r in songs), 'All selected rows pass the documented eligibility filters')
    check(all('rhythm.bpm' in features[k]['measurements'] and 'lowlevel.mfcc.mean' in features[k]['measurements'] for k in ids), 'All selected rows contain baseline rhythm and timbre measurements')
    def finite(value):
        if isinstance(value, dict): return all(finite(v) for v in value.values())
        if isinstance(value, list): return all(finite(v) for v in value)
        if isinstance(value, (int, float)): return math.isfinite(value)
        return True
    check(all(finite(f) for f in features.values()), 'All stored numeric features and classifier outputs are finite')
    check(len({len(features[k]['measurements']['lowlevel.mfcc.mean']) for k in ids}) == 1, 'MFCC feature dimensions are consistent')
    check(not any('gender' in f['predictions'] for f in features.values()), 'Gender classifier is absent from app-ready features')
    no_audio = not any(p.suffix.lower() in {'.mp3','.wav','.flac','.ogg','.opus','.m4a','.aac','.aiff'} for p in DATA.rglob('*') if p.is_file())
    check(no_audio, 'No audio files were downloaded')
    versions = collections.Counter(json.dumps(f['analysis_version'], sort_keys=True) for f in features.values())
    families = collections.Counter(r['primary_style_family'] for r in songs)
    decades = collections.Counter(r['decade'] for r in songs)
    bands = collections.Counter(r['familiarity_band'] for r in songs)
    warnings = ['Familiarity bands are editorial estimates; there is no measured popularity ranking.',
                'Genre families derive from tags and require listening-based review.',
                'External listening links are searches, not verified exact-recording URLs.',
                'Clapback identities are contributor claims; matching audio was not independently verified.',
                'CLAP and AcousticBrainz can describe different masters/rips of a shared recording.',
                'No timestamps or segment embeddings are provided by this CLAP snapshot.',
                'Recommendation quality has not been validated through listening in this preparation task.']
    missing_highlevel = sum(not r['has_highlevel_predictions'] for r in songs)
    if missing_highlevel:
        warnings.append(f'{missing_highlevel} recording(s) have baseline features and CLAP vectors but no high-level classifier predictions; optional attribute filters must handle missing values.')
    if len(versions) > 1:
        warnings.append(f'AcousticBrainz contains {len(versions)} extractor-version signatures; account for compatibility before scoring.')
    for family in ['jazz_blues','country_folk_acoustic','funk_soul_rnb','classic_rock','hiphop_reggae']:
        if families[family] < 50:
            warnings.append(f'Limited source coverage for {family}: {families[family]} selected recordings.')
    report = {'passed': not errors, 'checks_passed': checks, 'errors': errors, 'warnings': warnings,
              'statistics': manifest['statistics'], 'extractor_version_signatures': len(versions),
              'runtime_bytes': sum(p.stat().st_size for p in out.iterdir() if p.is_file())}
    (DATA / 'validation.json').write_text(json.dumps(report, indent=2))
    text = ['# Workshop collection audit', '',
            f"Prepared from Clapback snapshot `{manifest['source_snapshot']}`. This is a data integrity and curation audit, not a listening-quality evaluation.", '',
            f"**{len(songs):,} recordings; {len(counts):,} primary artists.** App-ready files: {report['runtime_bytes']/1024/1024:.1f} MiB (includes readable and binary copies of vectors).", '',
            f"Validation: {'PASS' if not errors else 'FAIL'} — {len(checks)} checks passed; {len(errors)} failed.", '',
            '## Style coverage', '', '| Broad family | Songs |', '| --- | ---: |']
    text += [f'| {k.replace("_", " ")} | {v} |' for k, v in sorted(families.items())]
    text += ['', '## Decades', '', '| Decade | Songs |', '| --- | ---: |']
    text += [f'| {k}s | {v} |' for k, v in sorted(decades.items())]
    text += ['', '## Editorial familiarity bands', '', '| Band | Songs |', '| --- | ---: |']
    text += [f'| {k.replace("_", " ")} | {v} |' for k, v in sorted(bands.items())]
    text += ['', 'These are estimates for workshop curation, not empirical popularity measurements.', '', '## Limitations', '']
    text += ['- ' + w for w in warnings]
    text += ['', '## Familiar starting points', '', '| Artist | Recording | Year |', '| --- | --- | ---: |']
    anchors = sorted([r for r in songs if r['is_editorial_anchor']], key=lambda r: (r['artist'], r['title']))
    text += [f"| {r['artist'].replace('|','/')} | {r['title'].replace('|','/')} | {r['year']} |" for r in anchors]
    text += ['', '## Examples by style', '']
    for family in sorted(families):
        examples = sorted([r for r in songs if r['primary_style_family'] == family], key=lambda r: (r['familiarity_band'], r['artist'], r['title']))[:12]
        text += ['### ' + family.replace('_', ' '), '']
        text += [f"- {r['artist']} — {r['title']} ({r['year']})" for r in examples]
        text += ['']
    text += ['## Full list and provenance', '',
             'Browse `workshop/songs.csv` or `workshop/songs.json`. See `README.md` for licensing, field meanings, source caching, and reproduction commands.', '']
    (DATA / 'CURATION.md').write_text('\n'.join(text))
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
