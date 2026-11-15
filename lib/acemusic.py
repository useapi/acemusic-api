# Shared helpers for the ACE Music API examples by useapi.net.
# Python 3.8 or newer, standard library only (urllib).
# API reference: https://useapi.net/docs/api-acemusic-v1

import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = (os.environ.get('USEAPI_BASE') or 'https://api.useapi.net/v1/acemusic').rstrip('/')
TOKEN = os.environ.get('USEAPI_TOKEN')
UA = 'acemusic-api-examples/1.0 (+https://github.com/useapi/acemusic-api)'

# Credits ACE Music charges per request (as of November 2026): 4 for two songs on ACE Music v1 and v1.1,
# nothing on ACE-Step v1.5 XL, 5 for a vocal + instrumental split and 60 for every stem.
PAID_MODELS = ('acemusic-v1', 'acemusic-v1.1')
STEMS_CREDITS = {'vocals': 5, 'all': 60}


def log(*a):
    print(datetime.now().strftime('%H:%M:%S'), *a, flush=True)


def args():
    """--name value and --flag from the command line"""
    out, argv, i = {}, sys.argv[1:], 0
    while i < len(argv):
        if argv[i].startswith('--'):
            key = argv[i][2:]
            if i + 1 < len(argv) and not argv[i + 1].startswith('--'):
                out[key] = argv[i + 1]
                i += 1
            else:
                out[key] = True
        i += 1
    return out


def email_of(a):
    """The ACE Music account to use: --email, else ACEMUSIC_EMAIL, else none (the API picks a healthy account)"""
    e = a.get('email')
    return (e.strip() if isinstance(e, str) and e.strip() else None) or os.environ.get('ACEMUSIC_EMAIL') or None


def songs_from(a, key='song'):
    """A songId from --song, or song N of a job record a script saved (--from ../custom-lyrics/output/<job>.json --pick 2)"""
    if isinstance(a.get(key), str):
        return [x.strip() for x in a[key].split(',') if x.strip()]
    if not isinstance(a.get('from'), str):
        return []
    picks = [int(x) for x in str(a.get('pick', '1')).split(',')]
    out = []
    for path in a['from'].split(','):
        with open(path.strip(), encoding='utf-8') as f:
            songs = json.load(f).get('songs') or []
        out += [songs[n - 1]['songId'] for n in picks if 0 < n <= len(songs) and songs[n - 1].get('songId')]
    return out


def require_token():
    if not TOKEN:
        sys.exit('Set USEAPI_TOKEN to your useapi.net API token, see https://useapi.net/docs/start-here/setup-useapi')


class Response:
    def __init__(self, status, data, headers):
        self.status, self.data, self.headers = status, data, headers


def api(method, path, json_body=None, query=None, body=None, headers=None, retries=10):
    """One API call. JSON in and out, a raw body for uploads. 429 (the account is running its maxJobs) and
    503 (ACE Music busy, nothing charged) are retried after Retry-After. Other answers are returned as they are."""
    url = API + path
    q = {k: v for k, v in (query or {}).items() if v not in (None, '')}
    if q:
        url += '?' + urllib.parse.urlencode(q)
    h = {'Authorization': f'Bearer {TOKEN}', 'User-Agent': UA, **(headers or {})}
    data = body
    if json_body is not None:
        h['Content-Type'] = 'application/json'
        data = json.dumps(json_body).encode()
    attempt = 0
    while True:
        req = urllib.request.Request(url, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(req, timeout=300) as res:
                status, raw, rh = res.status, res.read(), res.headers
        except urllib.error.HTTPError as e:
            status, raw, rh = e.code, e.read(), e.headers
        ctype = rh.get('Content-Type', '')
        parsed = json.loads(raw) if 'json' in ctype and raw else (None if status == 204 else raw)
        if status in (429, 503) and attempt < retries:
            wait = int(rh.get('Retry-After') or 30)
            log(f'{status} {(parsed or {}).get("error", "") if isinstance(parsed, dict) else ""} — retrying in {wait} s')
            time.sleep(wait)
            attempt += 1
            continue
        return Response(status, parsed, rh)


def fail(what, r):
    raise RuntimeError(f'{what}: HTTP {r.status} {json.dumps(r.data) if isinstance(r.data, (dict, list)) else ""}')


def create_songs(body):
    """POST /music in async mode: answers 201 at once with the job (status "processing")"""
    r = api('POST', '/music', {**body, 'async': True})
    if r.status not in (200, 201):
        fail('POST /music', r)
    return r.data


def split_stems(song_id, mode):
    """POST /music/stems in async mode"""
    r = api('POST', '/music/stems', {'songId': song_id, 'mode': mode, 'async': True})
    if r.status not in (200, 201):
        fail('POST /music/stems', r)
    return r.data


def wait_for_job(job, every=10, label=''):
    """Poll GET /jobs/{jobid} every 10 seconds until the job is completed or failed"""
    last = ''
    while job.get('status') == 'processing':
        time.sleep(every)
        r = api('GET', '/jobs/' + urllib.parse.quote(job['jobid'], safe=''))
        if r.status != 200:
            fail(f'GET /jobs/{job["jobid"]}', r)
        job = r.data
        now = job['status'] if job.get('type') == 'stems' else ', '.join(s['status'] for s in job.get('songs') or [])
        if now != last:
            log(f'{label} {job["status"]} ({now})')
        last = now
    return job


def credits_of(job):
    """Credits a finished job used, by the rule ACE Music charges (failed songs that were refunded cost nothing)"""
    if job.get('type') == 'stems':
        return STEMS_CREDITS.get((job.get('stems') or {}).get('mode'), 0) if job.get('status') == 'completed' else 0
    songs = job.get('songs') or []
    if songs and all(s.get('refunded') for s in songs):
        return 0
    return 4 if job.get('modelUsed') in PAID_MODELS else 0


def slug(s):
    s = unicodedata.normalize('NFKD', s or 'untitled').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:50] or 'untitled'


def download(url, path):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=300) as res, open(path, 'wb') as f:
        f.write(res.read())
    return path


def download_link(song_id, fmt, tries=5):
    """GET /music/download: JSON with a link (mp3, wav) or the file itself (midi, musicxml). ACE Music makes WAV,
    MIDI and MusicXML on the first request, so a 202 is asked again a minute later."""
    for _ in range(tries):
        r = api('GET', '/music/download', query={'songId': song_id, 'format': fmt})
        if r.status == 200:
            return {'file': r.data, 'headers': r.headers} if isinstance(r.data, bytes) else r.data
        if r.status != 202:
            log(f'GET /music/download {fmt}: HTTP {r.status} {(r.data or {}).get("error", "") if isinstance(r.data, dict) else ""}')
            return None
        log(f'{fmt}: ACE Music is still making it, asking again in 60 s')
        time.sleep(60)
    return None


def save_songs(job, folder, prefix, wav=False):
    """Save both songs of a finished job: the mp3 (playUrl when the API returns it, else audioUrl), the cover art,
    a WAV when asked (paid ACE Music plans, not for ACE-Step songs), and the job record as JSON"""
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, f'{prefix}.json'), 'w', encoding='utf-8') as f:
        json.dump(job, f, indent=2, ensure_ascii=False)
    files = []
    for i, song in enumerate(job.get('songs') or [], 1):
        if song.get('status') != 'succeeded':
            log(f'song {i}: {song.get("status")} {(song.get("error") or {}).get("message", "")}')
            continue
        base = os.path.join(folder, f'{prefix}-{i}-{slug(song.get("title"))}')
        files.append(download(song.get('playUrl') or song['audioUrl'], base + '.mp3'))
        if song.get('coverUrl'):
            try:
                files.append(download(song['coverUrl'], base + '.jpg'))
            except Exception:
                pass
        if wav:
            link = download_link(song['songId'], 'wav')
            if link and link.get('url'):
                files.append(download(link['url'], base + '.wav'))
        log(f'  {i}. "{song.get("title")}" {round(song.get("duration") or 0)} s → {base}.mp3')
    return files


def read_score(song_id, tries=5):
    """GET /music/score: the song's score in ABC notation. ACE Music reads it on the first request (free for ACE Music
    v1 songs, 1 credit for an ACE-Step song, already there for v1.1 songs and uploads). The API waits up to a minute,
    then answers 202: asked again a minute later."""
    for _ in range(tries):
        r = api('GET', '/music/score', query={'songId': song_id})
        if r.status == 200:
            return r.data
        if r.status != 202:
            fail('GET /music/score', r)
        log('ACE Music is still reading the score, asking again in 60 s')
        time.sleep(60)
    return None


def ensure_score(song_id):
    """ACE Music v1.1 follows a reference by its melody. A song without a score failed with ref_no_melody in our tests
    (credits refunded) and worked once its score was read, so read it first when the song has none."""
    r = api('GET', '/music/' + urllib.parse.quote(song_id, safe=''))
    if r.status != 200:
        fail(f'GET /music/{song_id}', r)
    if r.data.get('score'):
        return
    log(f'"{r.data.get("title")}" has no score yet: GET /music/score first (ACE Music v1.1 reads the melody from it)')
    read_score(song_id)


def credits_left(email):
    """GET /accounts/{email}: the account's live credits (None without an email)"""
    if not email:
        return None
    r = api('GET', '/accounts/' + urllib.parse.quote(email, safe=''))
    return r.data.get('credits') if r.status == 200 else None


def ledger(folder, entry):
    """One line per job in output/ledger.jsonl: what ran, on which model, what it cost"""
    os.makedirs(folder, exist_ok=True)
    with open(os.path.join(folder, 'ledger.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps({'at': datetime.now(timezone.utc).isoformat(), **entry}, ensure_ascii=False) + '\n')


def run_stamp():
    return datetime.now(timezone.utc).strftime('%m%d-%H%M')


def run_batch(items, folder, example, parallel=4):
    """Submit up to `parallel` requests, wait for them, save the songs. Each item: {body, prefix, wav}"""
    spent, results = 0, []
    run = run_stamp()  # file names carry the run's UTC time (MMDD-HHMM), so a new run never overwrites an old one
    items = [{**i, 'prefix': f'{i["prefix"]}-{run}'} for i in items]
    for start in range(0, len(items), parallel):
        jobs = []
        for item in items[start:start + parallel]:
            b = item['body']
            log(f'#{item["prefix"]} POST /music ({b.get("model", "acemusic-v1")}{", mode " + b["mode"] if b.get("mode") else ""})')
            try:
                jobs.append((item, create_songs(b)))
            except RuntimeError as e:
                log(f'#{item["prefix"]} {e}')
                ledger(folder, {'example': example, 'prefix': item['prefix'], 'status': 'refused', 'error': str(e), 'credits': 0})
        for item, started in jobs:
            job = wait_for_job(started, label=f'#{item["prefix"]}')
            credits = credits_of(job)
            spent += credits
            log(f'#{item["prefix"]} {job["status"]}: model {job.get("model")} → ran on {job.get("modelUsed")}, {credits} credits'
                + (f', {job["error"]}' if job.get('error') else ''))
            ok = job['status'] == 'completed' or any(s.get('status') == 'succeeded' for s in job.get('songs') or [])
            files = save_songs(job, folder, item['prefix'], wav=item.get('wav', False)) if ok else []
            ledger(folder, {'example': example, 'prefix': item['prefix'], 'status': job['status'], 'model': job.get('model'),
                            'modelUsed': job.get('modelUsed'), 'credits': credits, 'error': job.get('error'),
                            'songs': [{'title': s.get('title'), 'duration': s.get('duration'), 'status': s.get('status')} for s in job.get('songs') or []]})
            results.append({'item': item, 'job': job, 'files': files})
    return results, spent
