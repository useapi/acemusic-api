# Stems, downloads (MP3, WAV, MIDI, MusicXML) and the score of a song with the ACE Music API by useapi.net.
# Usage: python3 stems-and-downloads.py --song <songId> [--stems vocals,all|none] [--formats mp3,wav,midi,musicxml] [--score]
#        python3 stems-and-downloads.py --from ../custom-lyrics/output/<job>.json [--pick 1] …
# Stems (5 credits for vocals, 60 for every stem), WAV, MIDI and MusicXML need a paid ACE Music plan (Creator or
# Artist). MP3 and the score work on every plan. ACE-Step songs are MP3 only (no WAV).
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#split-a-song-into-stems

import os
import sys
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from acemusic import (  # noqa: E402
    api, args, credits_of, download, download_link, fail, ledger, log, read_score, require_token, run_stamp, slug, songs_from,
    split_stems, wait_for_job,
)

OUT = os.path.join(HERE, 'output')
a = args()
require_token()
songs = songs_from(a)
if not songs:
    sys.exit('Pass the song: --song <songId>, or --from <a job .json the other examples saved> [--pick 2]')
song_id = songs[0]
stem_modes = [m for m in str(a.get('stems', 'vocals')).split(',') if m and m != 'none']
formats = [f for f in str(a.get('formats', 'mp3,wav,midi,musicxml')).split(',') if f]
os.makedirs(OUT, exist_ok=True)

# GET /music/{songId}: the song with fresh links
r = api('GET', '/music/' + urllib.parse.quote(song_id, safe=''))
if r.status != 200:
    fail('GET /music/{songId}', r)
song = r.data
base = os.path.join(OUT, f'{slug(song.get("title"))}-{run_stamp()}')
log(f'"{song.get("title")}" ({song.get("model")}, {round(song.get("duration") or 0)} s)')

# POST /music/stems for each mode at once (async), then wait for each job and save every track
jobs = []
for mode in stem_modes:
    log(f'POST /music/stems mode {mode}')
    jobs.append(split_stems(song_id, mode))
for started in jobs:
    job = wait_for_job(started, label=f'stems {started["stems"]["mode"]}')
    if job['status'] != 'completed':
        log(f'stems {job["stems"]["mode"]} {job["status"]}: {job.get("error", "")}')
        continue
    for t in job['stems']['tracks']:
        if t.get('url'):
            path = f'{base}-stems-{job["stems"]["mode"]}-{t["type"]}.mp3'
            download(t['url'], path)
            log(f'  {job["stems"]["mode"]}: {t["type"]} → {path}')
    # a song already split in that mode answers at once with its tracks, and no credits are charged again
    credits = 0 if started['status'] == 'completed' else credits_of(job)
    ledger(OUT, {'example': 'stems-and-downloads', 'what': f'stems {job["stems"]["mode"]}', 'status': job['status'],
                 'credits': credits, 'tracks': [t['type'] for t in job['stems']['tracks']]})

# GET /music/download: mp3 and wav come back as links (wav valid 24 hours), midi and musicxml as the file itself
EXT = {'mp3': 'mp3', 'wav': 'wav', 'midi': 'mid', 'musicxml': 'musicxml'}
for fmt in formats:
    got = download_link(song_id, fmt)
    if not got:
        continue
    path = f'{base}.{EXT[fmt]}'
    if got.get('file') is not None:
        with open(path, 'wb') as f:
            f.write(got['file'])
    else:
        download(got.get('playUrl') or got['url'], path)
    log(f'  {fmt} → {path}')

# GET /music/score: ABC notation, every plan (1 credit the first time for an ACE-Step song)
if a.get('score'):
    score = read_score(song_id)
    if score and score.get('abc'):
        with open(f'{base}.abc', 'w', encoding='utf-8') as f:
            f.write(score['abc'])
        log(f'  score (ABC, {len(score["abc"].splitlines())} lines) → {base}.abc')
