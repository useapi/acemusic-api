# Sync and async requests, job polling and replyUrl webhooks with the ACE Music API by useapi.net.
# Usage: python3 sync-and-async.py [--mode sync|async] [--reply-url https://your-server/hook] [--reply-ref my-ref] [--email you@example.com]
#   sync (default): POST /music waits for the songs and answers 200, or 202 with the job if it runs past 100 seconds
#   async: POST /music answers 201 at once, then GET /jobs/{jobid} is polled until the job is completed or failed
#   --reply-url: the API also POSTs the finished job record to that public https URL (see webhook-receiver.py)
# Full walkthrough: https://useapi.net/docs/articles/ace-music-api-tutorial#sync-async-and-webhooks

import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'lib'))
from acemusic import api, args, credits_of, email_of, fail, ledger, log, require_token, save_songs, wait_for_job, run_stamp  # noqa: E402

OUT = os.path.join(HERE, 'output')
a = args()
email = email_of(a)
mode = 'async' if a.get('mode') == 'async' else 'sync'
require_token()

with open(a.get('prompts') or os.path.join(HERE, 'prompts.json'), encoding='utf-8') as f:
    p = json.load(f)[0]
body = {k: v for k, v in p.items() if not k.startswith('_')}
if email:
    body['email'] = email
if mode == 'async':
    body['async'] = True
if isinstance(a.get('reply-url'), str):
    body['replyUrl'] = a['reply-url']
    body['replyRef'] = a['reply-ref'] if isinstance(a.get('reply-ref'), str) else f'example-{run_stamp()}'

t0 = time.time()
secs = lambda: f'{round(time.time() - t0)} s'  # noqa: E731
log(f'POST /music ({mode}{", with replyUrl" if body.get("replyUrl") else ""})')
r = api('POST', '/music', body)
job = r.data
if r.status == 200:
    log(f'200 after {secs()}: the songs are ready')
elif r.status == 201:
    log(f'201 after {secs()}: the job is running, jobid {job["jobid"]}')
elif r.status == 202:
    log(f'202 after {secs()}: still running after 100 seconds, polling the job')
elif r.status == 422:
    log(f'422 after {secs()}: ACE Music could not make the songs: {job.get("error")}')
else:
    fail('POST /music', r)

if mode == 'async':
    # GET /jobs: every job running now on your ACE Music accounts
    running = api('GET', '/jobs')
    jobs = (running.data or {}).get('jobs') or []
    log(f'GET /jobs: {len(jobs)} job(s) running now: ' + ', '.join(f'{j.get("type")} {j.get("model") or j.get("stemsMode") or ""}' for j in jobs))
if job.get('status') == 'processing':
    job = wait_for_job(job, label='job')
log(f'{job["status"]} after {secs()}: {job.get("modelUsed")}, {credits_of(job)} credits')

prefix = f'{mode}-{run_stamp()}'
if job['status'] == 'completed':
    save_songs(job, OUT, prefix)
ledger(OUT, {'example': 'async-webhooks', 'prefix': prefix, 'mode': mode, 'status': job['status'], 'httpStatus': r.status,
             'seconds': round(time.time() - t0), 'modelUsed': job.get('modelUsed'), 'credits': credits_of(job), 'replyUrl': bool(body.get('replyUrl'))})
if body.get('replyUrl'):
    log(f'the finished record was also POSTed to your replyUrl (replyRef {body["replyRef"]})')
