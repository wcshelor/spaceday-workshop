#!/usr/bin/env python3
"""Prepare a cached, reproducible workshop collection. Never downloads audio."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
UA = 'SpacedayWorkshopData/0.1 (https://github.com/campshelor)'
LAST = {}


def fetch(url, path, interval=1.2):
    path = pathlib.Path(path)
    if path.exists():
        return path.read_bytes()
    path.parent.mkdir(parents=True, exist_ok=True)
    host = urllib.parse.urlsplit(url).netloc
    for attempt in range(6):
        time.sleep(max(0, interval - (time.monotonic() - LAST.get(host, 0))))
        LAST[host] = time.monotonic()
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA})
            with urllib.request.urlopen(req, timeout=45) as response:
                blob = response.read()
            temp = path.with_suffix(path.suffix + '.part')
            temp.write_bytes(blob)
            temp.replace(path)
            return blob
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if isinstance(exc, urllib.error.HTTPError) and exc.code in (400, 404, 414):
                raise
            if attempt == 5:
                raise
            delay = min(30, 2 ** (attempt + 1))
            print(f'Retrying {host}: {exc}; waiting {delay}s', flush=True)
            time.sleep(delay)


def source():
    location = DATA / 'sources' / 'clapback'
    if not (location / 'manifest.json').exists() and any(location.glob('*.gz')):
        raise ValueError('Source files exist without their snapshot manifest. Archive the whole Clapback source directory before starting a new snapshot.')
    manifest = json.loads(fetch('https://clapback.seethroughlab.com/export/latest.json', location / 'manifest.json'))
    base = manifest['url']
    for item in [manifest['claims'], *manifest['embeddings']]:
        blob = fetch(base + item['file'], location / item['file'])
        print(f"Cached {item['file']}: {len(blob):,} bytes", flush=True)
    claim_path = location / manifest['claims']['file']
    with gzip.open(claim_path, 'rt') as handle:
        claims = list(csv.DictReader(handle))
    ids = sorted({row['recording_mbid'] for row in claims})
    (DATA / 'sources' / 'recording_ids.json').write_text(json.dumps(ids))
    print(f'{len(ids):,} distinct claimed recording IDs', flush=True)
    return ids


def metadata(ids):
    directory = DATA / 'sources' / 'musicbrainz'
    index = {}
    for start in range(0, len(ids), 100):
        batch = ids[start:start + 100]
        name = hashlib.sha256('\n'.join(batch).encode()).hexdigest()[:16]
        path = directory / f'{start:05d}-{name}.json.gz'
        if path.exists():
            result = json.loads(gzip.decompress(path.read_bytes()))
        else:
            params = {'query': 'rid:(' + ' OR '.join(batch) + ')', 'fmt': 'json', 'limit': 100}
            url = 'https://musicbrainz.org/ws/2/recording/?' + urllib.parse.urlencode(params)
            temporary = directory / (name + '.response')
            result = json.loads(fetch(url, temporary, interval=2.5))
            returned = result.get('recordings', [])
            if result.get('count', len(returned)) > 100:
                raise ValueError('Unexpected paginated ID query')
            path.write_bytes(gzip.compress(json.dumps(result, ensure_ascii=False).encode()))
            temporary.unlink()
        for recording in result.get('recordings', []):
            if recording['id'] in batch:
                index[recording['id']] = recording
        if start % 1000 == 0 or start + 100 >= len(ids):
            print(f'MusicBrainz: {min(start + 100, len(ids)):,}/{len(ids):,} IDs; {len(index):,} records resolved', flush=True)
    out = DATA / 'catalogue'
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for mbid, item in index.items():
        credit = item.get('artist-credit', [])
        artists = [c['artist'] for c in credit if isinstance(c, dict) and 'artist' in c]
        date = item.get('first-release-date', '')
        rows.append({'recording_mbid': mbid, 'title': item['title'],
                     'artist': ''.join(c.get('name', c.get('artist', {}).get('name', '')) + c.get('joinphrase', '') for c in credit if isinstance(c, dict)),
                     'artist_ids': [a['id'] for a in artists],
                     'first_release_date': date, 'year': int(date[:4]) if date[:4].isdigit() else None,
                     'length_ms': item.get('length'), 'disambiguation': item.get('disambiguation', ''),
                     'tags': item.get('tags', []), 'release_count': len(item.get('releases', [])),
                     'release_titles': list(dict.fromkeys(r.get('title', '') for r in item.get('releases', []))),
                     'musicbrainz_url': 'https://musicbrainz.org/recording/' + mbid})
    (out / 'clapback_inventory.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2))
    with (out / 'clapback_inventory.csv').open('w', newline='') as handle:
        fields = ['recording_mbid', 'artist', 'title', 'year', 'length_ms', 'disambiguation', 'tags', 'musicbrainz_url']
        writer = csv.DictWriter(handle, fields, extrasaction='ignore')
        writer.writeheader()
        for row in rows:
            writer.writerow({**row, 'tags': '; '.join(t['name'] for t in row['tags'])})
    (out / 'unresolved_musicbrainz_ids.json').write_text(json.dumps(sorted(set(ids) - set(index)), indent=2))
    print(f'Wrote browsable inventory: {len(rows):,} recordings', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['source', 'metadata', 'all'])
    args = parser.parse_args()
    if args.stage in ('source', 'all'):
        ids = source()
    else:
        ids = json.loads((DATA / 'sources' / 'recording_ids.json').read_text())
    if args.stage in ('metadata', 'all'):
        metadata(ids)
