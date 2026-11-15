# Songs from a prompt — ACE Music API (Node.js and Python)

Describe a song in your own words and ACE Music writes the style, lyrics and title, then makes **two songs** per request, on ACE Music v1, ACE Music v1.1 Preview or ACE-Step v1.5 XL, through the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api). Each entry of `prompts.json` goes to [POST /music](https://useapi.net/docs/api-acemusic-v1/post-acemusic-music?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) in async mode, the script polls [GET /jobs/{jobid}](https://useapi.net/docs/api-acemusic-v1/get-acemusic-jobs-jobid?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) every 10 seconds and downloads both songs.

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#make-songs-from-a-prompt)**

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
node songs-from-prompt.mjs                 # every prompt in prompts.json
python3 songs-from-prompt.py --only 3      # just the third one
node songs-from-prompt.mjs --wav           # also save WAV (paid ACE Music plans, not ACE-Step songs)
```

Up to 4 requests run at once, ACE Music's own limit per account. A request that has to wait for a free slot is retried after the `Retry-After` the API sends.

## prompts.json

```json
{ "prompt": "A late-night neo-soul slow jam about two strangers sharing an umbrella…", "model": "acemusic-v1" }
```

- `prompt`: the song in your own words, up to 2,000 characters.
- `model`: `acemusic-v1` (default), `acemusic-v1.1` or `ace-step-1.5-xl`.
- `references`: up to 3 `songId`s that guide the songs, see [`upload-reference/`](../upload-reference).
- `images`: up to 3 image ids from `POST /files`, see [`upload-reference/`](../upload-reference).
- Keys that start with `_` are notes and are not sent.

## What it costs

ACE Music charges per request: 4 credits for two songs on ACE Music v1 or v1.1, nothing on ACE-Step v1.5 XL, which runs even on the Free plan with no credits left (as of November 2026). The three prompts here use 8 credits.

Everything lands in `output/` next to the script: each song's MP3 and cover art, the job record as JSON (with each `songId`, which the other examples take as `--song` or `--from`), and `ledger.jsonl`, one line per job with the model that ran and the credits it used.

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
