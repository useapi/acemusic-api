# ACE-Step v1.5 XL with tempo, key, time signature, length, styles to avoid and thinking, by the ACE Music API (useapi.net).
# ACE-Step songs use no credits on any ACE Music plan, the Free plan included.
# Usage: python3 ace-step-options.py [--prompts prompts.json] [--only 1,3] [--email you@example.com]
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#control-tempo-key-and-time-signature-with-ace-step

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from acemusic import args, email_of, require_token, run_batch, log  # noqa: E402

a = args()
email = email_of(a)
require_token()

# bpm 30-200, timeSignature 2/4 3/4 4/4 6/8, key "C major" … "B minor", duration 10-240 s, negative up to 200
# characters, thinking 0-100: these options work in mode generate on ace-step-1.5-xl only
with open(a.get('prompts') or os.path.join(HERE, 'prompts.json'), encoding='utf-8') as f:
    prompts = json.load(f)
only = [int(x) for x in str(a['only']).split(',')] if a.get('only') else None

items = []
for n, p in enumerate(prompts, 1):
    if only and n not in only:
        continue
    body = {'model': 'ace-step-1.5-xl', **{k: v for k, v in p.items() if not k.startswith('_')}}
    if email:
        body['email'] = email
    items.append({'prefix': f'{n:02d}-' + re.sub(r'[^a-z0-9]+', '-', p.get('title', 'song').lower()), 'body': body})

results, _ = run_batch(items, os.path.join(HERE, 'output'), 'ace-step-options')
for r in results:
    b, job = r['item']['body'], r['job']
    lengths = ' / '.join(f'{round(s.get("duration") or 0)} s' for s in job.get('songs') or [])
    log(f'{b.get("title")}: asked {b.get("bpm")} bpm, {b.get("timeSignature")}, {b.get("key")}, {b.get("duration")} s → {lengths}')
