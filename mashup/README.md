# Mashups of two or three songs — ACE Music API (Node.js and Python)

Combine 2 or 3 songs into one new song on ACE Music v1.1 Preview, through the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api). Without `lyrics`, ACE Music combines the songs' own words.

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#mash-up-two-or-three-songs)**

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
node mashup.mjs --songs "user:12345-you@example.com-song:so_…,user:12345-you@example.com-song:so_…"
# or song 1 of two jobs other examples saved
python3 mashup.py --from ../custom-lyrics/output/<job>.json,../songs-from-prompt/output/<job>.json --pick 1
# ask for another model to see the switch: the job reports model (asked) and modelUsed (ran)
node mashup.mjs --songs … --model acemusic-v1
```

Every song must be on the same ACE Music account, and the mashup runs there. A mashup always runs on `acemusic-v1.1`, whatever `model` you ask for, and costs 4 credits. The script reads each song's score first when it has none, as in [`covers-remix-edit/`](../covers-remix-edit).

## prompts.json

```json
{ "title": "Lanterns at the Bus Stop", "style": "upbeat neo-soul pop mashup, …", "audioInfluence": 60 }
```

`style`, `title` and `lyrics` are optional. `audioInfluence` (0-100, default 60) is how closely the songs are followed, `styleInfluence` (0-100, default 80) how strictly the style is.

Everything lands in `output/` next to the script: each song's MP3 and cover art, the job record as JSON (with each `songId`, which the other examples take as `--song` or `--from`), and `ledger.jsonl`, one line per job with the model that ran and the credits it used.

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
