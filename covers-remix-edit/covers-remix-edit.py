# Cover, remix or edit a song with the ACE Music API by useapi.net.
# Usage: python3 covers-remix-edit.py --song <songId> [--only 1,3] [--prompts prompts.json]
#        python3 covers-remix-edit.py --from ../custom-lyrics/output/<job>.json [--pick 1]
# The song can be any songId: one the API made, one from your Library (GET /music), or your own upload (POST /files).
# The request runs on the ACE Music account that holds the song.
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#covers-remixes-and-edits

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from acemusic import args, ensure_score, require_token, run_batch, songs_from, log  # noqa: E402

a = args()
require_token()
songs = songs_from(a)
if not songs:
    sys.exit('Pass the song to work on: --song <songId>, or --from <a job .json the other examples saved> [--pick 2]')

# mode cover: acemusic-v1.1, or ACE-Step on ace-step-1.5-xl (key, coverStrength, remixStrength)
# mode remix and edit: ace-step-1.5-xl only. edit needs start and end (seconds) and the new lyrics of that part
with open(a.get('prompts') or os.path.join(HERE, 'prompts.json'), encoding='utf-8') as f:
    prompts = json.load(f)
only = [int(x) for x in str(a['only']).split(',')] if a.get('only') else None

items = []
for n, p in enumerate(prompts, 1):
    if only and n not in only:
        continue
    body = {'references': [songs[0]], **{k: v for k, v in p.items() if not k.startswith('_')}}
    items.append({'prefix': f'{n:02d}-{p["mode"]}-{p.get("model", "acemusic-v1")}', 'body': body})

# A cover on ACE Music v1 or v1.1 runs on v1.1, which follows the song's melody. The API reads an ACE Music v1 song's
# score by itself (free); an ACE-Step song's score must be read first (1 credit), so make sure the song has its score
if any(i['body'].get('mode') == 'cover' and i['body'].get('model') != 'ace-step-1.5-xl' for i in items):
    ensure_score(songs[0])

results, spent = run_batch(items, os.path.join(HERE, 'output'), 'covers-remix-edit')
done = sum(1 for r in results if r['job']['status'] == 'completed')
log(f'done: {done} of {len(items)} requests completed, about {spent} credits used')
for r in results:
    for s in r['job'].get('songs') or []:
        if s.get('status') == 'succeeded':
            print(f'{s["songId"]}  "{s.get("title")}" ({s.get("kind")})')
