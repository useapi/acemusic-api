# Tempo, key and time signature with ACE-Step — ACE Music API (Node.js and Python)

Make songs with ACE-Step v1.5 XL at an exact tempo, key, time signature and length, with styles to avoid, through the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api). ACE-Step songs use no credits on any ACE Music plan, the Free plan included.

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#control-tempo-key-and-time-signature-with-ace-step)**

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
node ace-step-options.mjs
python3 ace-step-options.py --only 2
```

## prompts.json

| Song | `bpm` | `timeSignature` | `key` | `duration` | Also |
|---|---|---|---|---|---|
| Midnight Waltz, a dark cabaret waltz | 84 | 3/4 | D minor | 120 | `negative`, `thinking: 60` |
| Harbour Jig, a Celtic instrumental | 116 | 6/8 | G major | 90 | `instrumental: true` |
| Almost Home, liquid drum and bass | 174 | 4/4 | F minor | 150 | `thinking: 80` |

- `bpm`: 30 to 200. `timeSignature`: `2/4`, `3/4`, `4/4` or `6/8`. `key`: `C major` to `B minor`.
- `duration`: 10 to 240 seconds. Every song came back at exactly the length asked.
- `negative`: styles to avoid, up to 200 characters. `thinking`: 0 to 100, creative when low, steady when high.
- These options work in mode `generate` on `ace-step-1.5-xl`. The API answers `400` naming the option when it does not apply.

ACE-Step takes a style of up to 512 characters and lyrics of up to 2,000. Its songs are MP3 only (no WAV).

Everything lands in `output/` next to the script: each song's MP3 and cover art, the job record as JSON (with each `songId`, which the other examples take as `--song` or `--from`), and `ledger.jsonl`, one line per job with the model that ran and the credits it used.

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
