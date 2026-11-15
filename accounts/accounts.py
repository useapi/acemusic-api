# Your ACE Music accounts in the ACE Music API by useapi.net: list them, read the live credits, add one, set maxJobs.
# Usage: python3 accounts.py                                   list the accounts (plan, maxJobs, health)
#        python3 accounts.py --credits --email you@example.com  live plan, credits left, models and their limits
#        ACEMUSIC_PASSWORD=… python3 accounts.py --add --email you@example.com [--max-jobs 4]
#        python3 accounts.py --max-jobs 2 --email you@example.com
# The password is the one you sign in with at acemusic.ai. It is read from ACEMUSIC_PASSWORD, never from the command line.
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#several-ace-music-accounts

import os
import sys
import urllib.parse

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from acemusic import api, args, email_of, fail, log, require_token  # noqa: E402

a = args()
email = email_of(a)
require_token()
max_jobs = int(a['max-jobs']) if a.get('max-jobs') not in (None, True) else None


def need_email():
    if not email:
        sys.exit('Pass --email (or set ACEMUSIC_EMAIL)')


if a.get('add'):
    # POST /accounts {email, password, maxJobs?}: signs in to ACE Music, checks the account, then stores it
    need_email()
    if not os.environ.get('ACEMUSIC_PASSWORD'):
        sys.exit("Set ACEMUSIC_PASSWORD to the account's acemusic.ai password")
    r = api('POST', '/accounts', {'email': email, 'password': os.environ['ACEMUSIC_PASSWORD'], **({'maxJobs': max_jobs} if max_jobs else {})})
    if r.status != 200:
        fail('POST /accounts', r)
    log(f'added: {r.data.get("plan_name") or r.data.get("plan")} plan, {r.data.get("credits")} credits, maxJobs {r.data.get("maxJobs")}')
elif max_jobs:
    # POST /accounts {email, maxJobs}: changes only maxJobs (1 to 4), nothing is sent to ACE Music
    need_email()
    r = api('POST', '/accounts', {'email': email, 'maxJobs': max_jobs})
    if r.status != 200:
        fail('POST /accounts', r)
    log(f'maxJobs is now {r.data.get("maxJobs")}')
elif a.get('credits'):
    # GET /accounts/{email}: read live from ACE Music
    need_email()
    r = api('GET', '/accounts/' + urllib.parse.quote(email, safe=''))
    if r.status != 200:
        fail('GET /accounts/{email}', r)
    d = r.data
    costs = d.get('costs') or {}
    print(f'{d.get("plan_name")} ({d.get("cycle") or "free"}): {d.get("credits")} credits left, maxJobs {d.get("maxJobs")}, {d.get("health")}')
    print(f'costs: a request {costs.get("song")} credits, stems {(costs.get("stems") or {}).get("0")} (vocals) / {(costs.get("stems") or {}).get("2")} (all)')
    for m in d.get('models') or []:
        print(f'  {m["id"]}: {m["name"]}{", no credits" if m.get("free") else ""}, style up to {m["limits"]["style"]}, lyrics up to {m["limits"]["lyrics"]}')
else:
    # GET /accounts: every account you added, as stored
    r = api('GET', '/accounts')
    if r.status != 200:
        fail('GET /accounts', r)
    for acc in r.data.values():
        print(f'{acc["email"]}: {acc.get("plan")}, maxJobs {acc.get("maxJobs")}, {acc.get("health")}' + (f', error: {acc["error"]}' if acc.get('error') else ''))
