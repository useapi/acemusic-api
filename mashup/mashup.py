# Mash up 2 or 3 songs into one with the ACE Music API by useapi.net (ACE Music v1.1 Preview, 4 credits).
# Usage: python3 mashup.py --songs <songId>,<songId>[,<songId>] [--prompts prompts.json] [--model acemusic-v1]
#        python3 mashup.py --from <job1.json>,<job2.json> [--pick 1]
# Every song must be on the same ACE Music account. A mashup always runs on acemusic-v1.1: the job reports the
# model you asked for (model) and the one that ran (modelUsed).
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#mash-up-two-or-three-songs

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from acemusic import args, ensure_score, require_token, run_batch, songs_from, log  # noqa: E402

a = args()
require_token()
songs = songs_from(a, 'songs')
if not 2 <= len(songs) <= 3:
    sys.exit('Pass 2 or 3 songs: --songs <songId>,<songId>, or --from <job1.json>,<job2.json> [--pick 1]')

# ACE Music v1.1 follows each song's melody: make sure every song has its score
for s in songs:
    ensure_score(s)

with open(a.get('prompts') or os.path.join(HERE, 'prompts.json'), encoding='utf-8') as f:
    prompts = json.load(f)
items = [{'prefix': f'{n:02d}-mashup',
          'body': {'mode': 'mashup', 'model': a.get('model') or 'acemusic-v1.1', 'references': songs, **{k: v for k, v in p.items() if not k.startswith('_')}}}
         for n, p in enumerate(prompts, 1)]

results, spent = run_batch(items, os.path.join(HERE, 'output'), 'mashup')
done = sum(1 for r in results if r['job']['status'] == 'completed')
log(f'done: {done} of {len(items)} mashups completed, about {spent} credits used')
for r in results:
    for s in r['job'].get('songs') or []:
        if s.get('status') == 'succeeded':
            print(f'{s["songId"]}  "{s.get("title")}"')
