# A minimal replyUrl receiver for the ACE Music API by useapi.net: prints each job record it gets and saves it to
# output/webhooks.jsonl. The API POSTs the finished job record (the same JSON as GET /jobs/{jobid}) once per job.
# Usage: python3 webhook-receiver.py [--port 8080]
# The replyUrl must be a public https URL: put this behind a tunnel or a reverse proxy, then pass that URL as
# --reply-url to sync-and-async.py (or replyUrl to POST /music).

import json
import os
import sys
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
PORT = int(sys.argv[sys.argv.index('--port') + 1]) if '--port' in sys.argv else 8080
os.makedirs(os.path.join(HERE, 'output'), exist_ok=True)


class Hook(BaseHTTPRequestHandler):
    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get('Content-Length') or 0)).decode('utf-8', 'replace')
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"ok":true}')
        try:
            job = json.loads(raw)
        except ValueError:
            print('not JSON:', raw[:200])
            return
        print(f'{datetime.now(timezone.utc).isoformat()} {job.get("type")} job {job.get("status")} (replyRef {job.get("replyRef", "-")})')
        for s in job.get('songs') or []:
            print(f'  "{s.get("title")}" {s.get("status")} {s.get("audioUrl") or ""}')
        for t in (job.get('stems') or {}).get('tracks') or []:
            print(f'  {t.get("type")} {"ready" if t.get("url") else "-"}')
        if job.get('error'):
            print(f'  error {job.get("code")}: {job["error"]}')
        with open(os.path.join(HERE, 'output', 'webhooks.jsonl'), 'a', encoding='utf-8') as f:
            f.write(raw.replace('\n', ' ') + '\n')

    def log_message(self, *a):
        pass


print(f'listening on http://localhost:{PORT} — expose it as https and pass that URL as replyUrl')
HTTPServer(('', PORT), Hook).serve_forever()
