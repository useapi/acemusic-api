# Covers, remixes and edits — ACE Music API (Node.js and Python)

Cover a song in a new style, remix it, or rewrite one part of it with new words, through the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api). The song can be one the API made, one from your Library, or your own audio uploaded with [`upload-reference/`](../upload-reference).

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#covers-remixes-and-edits)**

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
node covers-remix-edit.mjs --song "user:12345-you@example.com-song:so_…"
# or take song 1 of a job another example saved
python3 covers-remix-edit.py --from ../custom-lyrics/output/<job>.json --pick 1 --only 1
```

The request runs on the ACE Music account that holds the song, so `--email` is not needed.

## prompts.json

| # | `mode` | Model | Credits | What it does |
|---|---|---|---|---|
| 1 | `cover` | `acemusic-v1.1` | 4 | The song in a new style, following its melody, chords and structure |
| 2 | `remix` | `ace-step-1.5-xl` | 0 | ACE-Step's remix: `coverStrength` keeps the original, `remixStrength` moves away from it |
| 3 | `edit` | `ace-step-1.5-xl` | 0 | Rewrites seconds `start` to `end` with new `lyrics`, keeps the rest |

ACE Music v1.1 follows the song's melody, which it reads from the song's score. In our tests a v1.1 cover of an ACE Music v1 song that had no score yet failed with `ref_no_melody` (the credits came back), and the same cover worked once the score was read. So before a v1.1 cover the script reads the song with [GET /music/{songId}](https://useapi.net/docs/api-acemusic-v1/get-acemusic-music-songid?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) and, when `score` is `false`, calls [GET /music/score](https://useapi.net/docs/api-acemusic-v1/get-acemusic-music-score?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) first. That is free for ACE Music v1 songs and costs 1 credit for an ACE-Step song.

Everything lands in `output/` next to the script: each song's MP3 and cover art, the job record as JSON (with each `songId`, which the other examples take as `--song` or `--from`), and `ledger.jsonl`, one line per job with the model that ran and the credits it used.

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
