# Your own lyrics, style and title with the ACE Music API by useapi.net, instrumentals, and lyrics written for you.
# Usage: python3 custom-lyrics.py [--prompts prompts.json] [--only 1,3] [--email you@example.com] [--wav]
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#sing-your-own-lyrics

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from acemusic import api, args, email_of, fail, require_token, run_batch, credits_left, log  # noqa: E402

a = args()
email = email_of(a)
require_token()

# ACE-Step v1.5 XL takes a style of up to 512 characters and lyrics of up to 2,000 (ACE Music v1 / v1.1: 1,000 and 5,000)
LIMITS = {'ace-step-1.5-xl': {'style': 512, 'lyrics': 2000}}


def fit(text, limit):
    if not limit or len(text) <= limit:
        return text
    cut = text[:limit]
    return cut[:max(cut.rfind('. ') + 1, cut.rfind(', '))] or cut


def write(p):
    """writeLyrics → POST /music/lyrics, improveStyle → POST /music/style: ACE Music's writers, no song made yet"""
    model = p.get('model', 'acemusic-v1')
    acct = {'email': email} if email else {}
    out = {}
    if p.get('writeLyrics'):
        log(f'POST /music/lyrics "{p["writeLyrics"][:60]}…"')
        r = api('POST', '/music/lyrics', {'prompt': p['writeLyrics'], 'model': model, **({'style': p['improveStyle']} if p.get('improveStyle') else {}), **acct})
        if r.status != 200:
            fail('POST /music/lyrics', r)
        out['title'], out['lyrics'] = r.data['title'], r.data['lyrics']
        log(f'  "{r.data["title"]}", {len(r.data["lyrics"].splitlines())} lines')
    if 'improveStyle' in p:
        log(f'POST /music/style "{p["improveStyle"]}"')
        r = api('POST', '/music/style', {'style': p['improveStyle'], 'model': model, **acct})
        if r.status != 200:
            fail('POST /music/style', r)
        out['style'] = r.data['style']
        log(f'  {r.data["style"][:100]}…')
    for key in ('style', 'lyrics'):
        if out.get(key):
            out[key] = fit(out[key], LIMITS.get(model, {}).get(key))
    return out


with open(a.get('prompts') or os.path.join(HERE, 'prompts.json'), encoding='utf-8') as f:
    prompts = json.load(f)
only = [int(x) for x in str(a['only']).split(',')] if a.get('only') else None

items = []
for n, p in enumerate(prompts, 1):
    if only and n not in only:
        continue
    fields = {k: v for k, v in p.items() if not k.startswith('_') and k not in ('writeLyrics', 'improveStyle')}
    written = write(p) if p.get('writeLyrics') or 'improveStyle' in p else {}
    model = p.get('model', 'acemusic-v1')
    # title, style, lyrics (or instrumental: true), model and the options go to POST /music as they are
    body = {**written, **fields, **({'email': email} if email else {})}
    items.append({'prefix': f'{n:02d}-{model}', 'wav': bool(a.get('wav')) and model != 'ace-step-1.5-xl', 'body': body})

before = credits_left(email)
results, spent = run_batch(items, os.path.join(HERE, 'output'), 'custom-lyrics')
done = sum(1 for r in results if r['job']['status'] == 'completed')
log(f'done: {done} of {len(items)} requests completed, about {spent} credits used'
    + (f' (credits before {before}, now {credits_left(email)})' if before is not None else ''))
for r in results:
    for s in r['job'].get('songs') or []:
        if s.get('status') == 'succeeded':
            print(f'{s["songId"]}  "{s.get("title")}"')
