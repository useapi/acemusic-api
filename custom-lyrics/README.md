# Your own lyrics, instrumentals and written lyrics — ACE Music API (Node.js and Python)

Sing your own lyrics in your own style, make an instrumental, or let ACE Music write the lyrics and the style first, with the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api). Uses [POST /music](https://useapi.net/docs/api-acemusic-v1/post-acemusic-music?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api), [POST /music/lyrics](https://useapi.net/docs/api-acemusic-v1/post-acemusic-music-lyrics?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) and [POST /music/style](https://useapi.net/docs/api-acemusic-v1/post-acemusic-music-style?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api).

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#sing-your-own-lyrics)**

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
node custom-lyrics.mjs                     # every entry in prompts.json
python3 custom-lyrics.py --only 1 --wav    # "Paper Lanterns", with WAV files (paid plans)
```

## prompts.json

Four entries, one per way:

1. "Paper Lanterns": your own `lyrics` with `[Verse]`, `[Chorus]` and `[Bridge]` tags, a `style`, a `title` and `duration: 210` on ACE Music v1.
2. "Neon Overpass": `instrumental: true`, `duration: 150` and `negative` (styles to avoid) on ACE Music v1.
3. "Bailando en la Azotea": lyrics in Spanish on ACE Music v1.
4. `writeLyrics` and `improveStyle`: the script asks [POST /music/lyrics](https://useapi.net/docs/api-acemusic-v1/post-acemusic-music-lyrics?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) for lyrics and a title and [POST /music/style](https://useapi.net/docs/api-acemusic-v1/post-acemusic-music-style?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) for a full style, then sings them on ACE-Step v1.5 XL, for no credits. A style for ACE-Step is cut to its 512-character limit.

Every other field goes to `POST /music` as it is: `title`, `style`, `lyrics`, `instrumental`, `model`, `duration` (30-600 s on ACE Music v1, 10-240 s on ACE-Step), `negative`, `styleInfluence` and the rest of the [options](https://useapi.net/docs/api-acemusic-v1/post-acemusic-music?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#options).

## What it costs

Entries 1 to 3 use 4 credits each on ACE Music v1. Entry 4 uses none: the writers charged nothing in our tests, and ACE-Step songs are free.

Everything lands in `output/` next to the script: each song's MP3 and cover art, the job record as JSON (with each `songId`, which the other examples take as `--song` or `--from`), and `ledger.jsonl`, one line per job with the model that ran and the credits it used.

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
