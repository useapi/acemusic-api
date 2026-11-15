# Your ACE Music Library with the ACE Music API by useapi.net: list songs, read one with fresh links, delete one.
# Usage: python3 library.py [--limit 20] [--all] [--email you@example.com]   list the Library, newest first
#        python3 library.py --song <songId>                                  one song with fresh links
#        python3 library.py --delete <songId>                                move a song to ACE Music's trash
# The Library holds every song of the account: made through the API or on acemusic.ai, and your uploads.
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#your-library

import os
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from acemusic import api, args, email_of, fail, log, require_token  # noqa: E402

a = args()
email = email_of(a)
require_token()

if isinstance(a.get('song'), str):
    # GET /music/{songId}: the song with fresh links (playUrl for players, its stems when it was split)
    r = api('GET', '/music/' + urllib.parse.quote(a['song'], safe=''))
    if r.status != 200:
        fail('GET /music/{songId}', r)
    s = r.data
    print(f'"{s.get("title")}" {s.get("status")}, {s.get("model") or "upload"}, {round(s.get("duration") or 0)} s, {s.get("kind")}'
          + (', has a score' if s.get('score') else ''))
    print(f'  style: {s.get("style")}')
    print(f'  audioUrl: {s.get("audioUrl")}')
    if s.get('playUrl'):
        print(f'  playUrl: until {s.get("playUrlExpires")}')
    for mode, st in (s.get('stems') or {}).items():
        print(f'  stems {mode}: {", ".join(t["type"] for t in st.get("tracks") or [])}')
elif isinstance(a.get('delete'), str):
    # DELETE /music/{songId}: 204, the song goes to the account's trash on acemusic.ai
    r = api('DELETE', '/music/' + urllib.parse.quote(a['delete'], safe=''))
    if r.status != 204:
        fail('DELETE /music/{songId}', r)
    log('deleted (moved to the ACE Music trash, restorable on acemusic.ai only)')
else:
    # GET /music: one page of the Library, and `next` for the following page (None on the last one)
    after, n = None, 0
    while True:
        r = api('GET', '/music', query={'email': email, 'limit': a.get('limit', 20), 'after': after})
        if r.status != 200:
            fail('GET /music', r)
        for s in r.data['songs']:
            n += 1
            print(f'{n}. "{s.get("title")}" {s.get("model") or "upload"} {round(s.get("duration") or 0)} s {s.get("kind")}  {s["songId"]}')
        after = r.data.get('next')
        if not (a.get('all') and after):
            break
    if after:
        log('more songs: --all lists every page')
