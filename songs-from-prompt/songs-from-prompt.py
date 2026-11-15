# Songs from a prompt with the ACE Music API by useapi.net: one request = two songs.
# Usage: python3 songs-from-prompt.py [--prompts prompts.json] [--only 1,3] [--email you@example.com] [--wav]
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#make-songs-from-a-prompt

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from acemusic import args, email_of, require_token, run_batch, credits_left, log  # noqa: E402

a = args()
email = email_of(a)
require_token()

with open(a.get('prompts') or os.path.join(HERE, 'prompts.json'), encoding='utf-8') as f:
    prompts = json.load(f)
only = [int(x) for x in str(a['only']).split(',')] if a.get('only') else None

# Every field of an entry goes to POST /music as is (prompt, model, references, images), except "_about" notes
items = []
for n, p in enumerate(prompts, 1):
    if only and n not in only:
        continue
    model = p.get('model', 'acemusic-v1')
    body = {k: v for k, v in p.items() if not k.startswith('_')}
    if email:
        body['email'] = email
    items.append({'prefix': f'{n:02d}-{model}', 'wav': bool(a.get('wav')) and model != 'ace-step-1.5-xl', 'body': body})

before = credits_left(email)
results, spent = run_batch(items, os.path.join(HERE, 'output'), 'songs-from-prompt')
done = sum(1 for r in results if r['job']['status'] == 'completed')
log(f'done: {done} of {len(items)} requests completed, about {spent} credits used'
    + (f' (credits before {before}, now {credits_left(email)})' if before is not None else ''))
for r in results:
    for s in r['job'].get('songs') or []:
        if s.get('status') == 'succeeded':
            print(f'{s["songId"]}  "{s.get("title")}"')
