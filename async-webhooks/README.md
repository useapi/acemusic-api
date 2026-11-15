# Sync, async and webhooks — ACE Music API (Node.js and Python)

The three ways to get your songs from the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api): wait for them in one call, poll the job, or have the finished job record posted to your server.

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#sync-async-and-webhooks)**

## Before you run it

- [Node.js](https://nodejs.org) 21 or newer, or [Python](https://www.python.org) 3.8 or newer. Nothing to install: the scripts use built-in `fetch` and `urllib`, and the shared helpers in [`../lib`](../lib).
- A useapi.net [API token](https://useapi.net/docs/start-here/setup-useapi?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) in `USEAPI_TOKEN`.
- An ACE Music account added with [Setup ACE Music](https://useapi.net/docs/start-here/setup-acemusic?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api). Set `ACEMUSIC_EMAIL` (or pass `--email`) to pick one when you have several, otherwise the API picks a free one.

```bash
export USEAPI_TOKEN=user:12345-...
export ACEMUSIC_EMAIL=you@example.com   # optional
```

## Run it

```bash
node sync-and-async.mjs                       # sync: one call, 200 with the songs (37 seconds in our run)
python3 sync-and-async.py --mode async        # async: 201 at once, then GET /jobs/{jobid} every 10 seconds
node sync-and-async.mjs --mode async --reply-url https://your-server.example.com/hook --reply-ref lofi-1
```

- Sync (the default): [POST /music](https://useapi.net/docs/api-acemusic-v1/post-acemusic-music?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) waits up to 100 seconds and answers `200` with both songs. A request still running then answers `202` with the job: poll it like an async one.
- Async: `async: true` answers `201` at once with the `jobid`. Poll [GET /jobs/{jobid}](https://useapi.net/docs/api-acemusic-v1/get-acemusic-jobs-jobid?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) until `status` is `completed` or `failed`. [GET /jobs](https://useapi.net/docs/api-acemusic-v1/get-acemusic-jobs?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) lists the jobs running on all your accounts.
- `replyUrl`: a public `https` URL that receives one `POST` of the finished job record, the same JSON as `GET /jobs/{jobid}`, for sync and async requests alike. `replyRef` comes back in the record.

## A webhook receiver

`webhook-receiver.mjs` and `webhook-receiver.py` are minimal HTTP servers that print each job record they get and save it to `output/webhooks.jsonl`:

```bash
node webhook-receiver.mjs --port 8080
```

The API needs a public `https` address, so put the receiver behind a tunnel or a reverse proxy and pass that address as `--reply-url`. In our run the record arrived 12 seconds after ACE Music finished the songs.

The prompt in `prompts.json` uses ACE-Step v1.5 XL, so trying all three ways costs no credits.

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
