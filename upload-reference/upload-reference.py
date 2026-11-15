# Upload your own audio and an image with the ACE Music API by useapi.net (POST /files), then make songs guided by them.
# Usage: python3 upload-reference.py --audio my-song.mp3 [--image robot-mascot.png] [--title "My demo"] [--only 1,2] [--email you@example.com]
# Audio: MP3, WAV, FLAC, OGG, M4A or AAC, up to 100 MB and 8 minutes. ACE Music transcribes it into a Library song
# (lyrics, style, tempo, melody), usable as a reference: in a prompt, or to cover, remix, edit or mash up.
# Image: JPEG, PNG or WebP, up to 10 MB, for a prompt's images.
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#guide-songs-with-your-own-audio-and-images

import json
import os
import sys
import time
import urllib.parse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from acemusic import api, args, email_of, fail, require_token, run_batch, log  # noqa: E402

a = args()
email = email_of(a)
require_token()
if not isinstance(a.get('audio'), str) and not isinstance(a.get('image'), str):
    sys.exit('Pass --audio <file> and/or --image <file>')

TYPES = {'.mp3': 'audio/mpeg', '.wav': 'audio/wav', '.flac': 'audio/flac', '.ogg': 'audio/ogg', '.m4a': 'audio/mp4', '.aac': 'audio/aac',
         '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}


def upload(path, title=None):
    """POST /files: the file as the raw request body with its Content-Type (urllib sends Content-Length)"""
    ctype = TYPES.get(os.path.splitext(path)[1].lower())
    if not ctype:
        sys.exit(f'unsupported file type: {path}')
    log(f'POST /files {os.path.basename(path)} ({ctype})')
    with open(path, 'rb') as f:
        r = api('POST', '/files', query={'email': email, 'title': title}, body=f.read(), headers={'Content-Type': ctype})
    if r.status not in (200, 202):
        fail('POST /files', r)
    item = r.data
    # audio still being transcribed after 90 s answers 202: read the song until it is done
    while item.get('songId') and item.get('status') not in ('succeeded', 'failed'):
        time.sleep(10)
        g = api('GET', '/music/' + urllib.parse.quote(item['songId'], safe=''))
        if g.status != 200:
            fail('GET /music/{songId}', g)
        item = g.data
    if item.get('status') == 'failed':
        sys.exit(f'ACE Music could not read {path}: {(item.get("error") or {}).get("message", "")}')
    # keep the ids: a songId works with covers-remix-edit and mashup (--song), a mediaId in a prompt's images
    os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)
    with open(os.path.join(HERE, 'output', 'uploads.jsonl'), 'a', encoding='utf-8') as f:
        f.write(json.dumps({'at': datetime.now(timezone.utc).isoformat(), 'file': os.path.basename(path), 'songId': item.get('songId'),
                            'mediaId': item.get('mediaId'), 'title': item.get('title'), 'seconds': item.get('duration'),
                            'bpm': (item.get('upload') or {}).get('bpm')}) + '\n')
    return item


audio = upload(a['audio'], a.get('title') if isinstance(a.get('title'), str) else None) if isinstance(a.get('audio'), str) else None
if audio:
    log(f'  songId {audio["songId"]}\n  heard: {(audio.get("upload") or {}).get("bpm", "?")} bpm, {audio.get("duration")} s, "{(audio.get("style") or "")[:120]}…"')
image = upload(a['image']) if isinstance(a.get('image'), str) else None
if image:
    log(f'  mediaId {image["mediaId"]}')

with open(a.get('prompts') or os.path.join(HERE, 'prompts.json'), encoding='utf-8') as f:
    prompts = json.load(f)
only = [int(x) for x in str(a['only']).split(',')] if a.get('only') else None

items = []
for n, p in enumerate(prompts, 1):
    if only and n not in only:
        continue
    if (p.get('useAudio') and not audio) or (p.get('useImage') and not image):
        log(f'#{n} skipped: it needs {"--audio" if p.get("useAudio") else "--image"}')
        continue
    body = {k: v for k, v in p.items() if not k.startswith('_') and k not in ('useAudio', 'useImage')}
    # the request runs on the account that holds the upload, so no email is needed here
    if p.get('useAudio'):
        body['references'] = [audio['songId']]
    if p.get('useImage'):
        body['images'] = [image['mediaId']]
    items.append({'prefix': f'{n:02d}-{"audio" if p.get("useAudio") else "image"}-{p.get("model", "acemusic-v1")}', 'body': body})

results, spent = run_batch(items, os.path.join(HERE, 'output'), 'upload-reference')
done = sum(1 for r in results if r['job']['status'] == 'completed')
log(f'done: {done} of {len(items)} requests completed, about {spent} credits used')
for r in results:
    for s in r['job'].get('songs') or []:
        if s.get('status') == 'succeeded':
            print(f'{s["songId"]}  "{s.get("title")}"')
