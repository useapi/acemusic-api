# Stems, MP3, WAV, MIDI, MusicXML and the score — ACE Music API (Node.js and Python)

Split a song into stems and download it in every format ACE Music makes, through the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api): [POST /music/stems](https://useapi.net/docs/api-acemusic-v1/post-acemusic-music-stems?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api), [GET /music/download](https://useapi.net/docs/api-acemusic-v1/get-acemusic-music-download?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) and [GET /music/score](https://useapi.net/docs/api-acemusic-v1/get-acemusic-music-score?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api).

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#split-a-song-into-stems)**

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
node stems-and-downloads.mjs --song "user:12345-you@example.com-song:so_…" --stems vocals,all --score
python3 stems-and-downloads.py --from ../custom-lyrics/output/<job>.json --pick 1 --stems none --formats mp3,midi
```

| Option | Values | Default |
|---|---|---|
| `--stems` | `vocals` (vocal + instrumental, 5 credits), `all` (every stem, 60 credits), both, or `none` | `vocals` |
| `--formats` | `mp3`, `wav`, `midi`, `musicxml` | all four |
| `--score` | save the score in ABC notation (`.abc`) | off |

- Stems, WAV, MIDI and MusicXML need a paid ACE Music plan (Creator or Artist). MP3 and the score work on every plan.
- `all` returns the stems ACE Music finds, such as vocals, backing vocals, drums, bass, guitar, keyboard, strings, synth and fx, each an MP3. A song already split in that mode answers at once, with no credits charged again.
- WAV is not made for ACE-Step songs (MP3 only). MIDI and MusicXML come back as the files themselves.
- The score of an ACE Music v1 song cost nothing in our tests, an ACE-Step song's first read costs 1 credit, and ACE Music v1.1 songs come with theirs.

Files land in `output/`, named after the song.

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
