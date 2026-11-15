# Your own audio and images as references — ACE Music API (Node.js and Python)

Upload a recording or a picture with [POST /files](https://useapi.net/docs/api-acemusic-v1/post-acemusic-files?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) and make songs guided by it, through the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api). ACE Music transcribes uploaded audio into a Library song (lyrics, style, tempo, melody), so it also works with [`covers-remix-edit/`](../covers-remix-edit) and [`mashup/`](../mashup).

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#guide-songs-with-your-own-audio-and-images)**

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
node upload-reference.mjs --audio my-demo.mp3 --title "My demo" --only 1
# the picture from our run: a dancing robot mascot
curl -o robot-mascot.png https://media.useapi.net/blog/2026-09-07-260907/dreamina-longvideo-ref-robot-mascot.png
python3 upload-reference.py --image robot-mascot.png --only 2
```

- Audio: MP3, WAV, FLAC, OGG, M4A or AAC, up to 100 MB and 8 minutes. Transcribing took about 15 seconds for a 90-second file in our run. Uploads count against the account's upload allowance: 10 minutes of audio on Free, 30 on Creator, 60 on Artist.
- Image: JPEG, PNG or WebP, up to 10 MB.
- The file is sent as the raw request body with its `Content-Type`. Uploads, and every request that uses them, stay on the account they were uploaded to.

## prompts.json

1. A prompt with `references: [<your audio>]` on ACE Music v1. With a reference song ACE Music may run the request on v1.1 to keep the tune: in our run the job reported `model: acemusic-v1`, `modelUsed: acemusic-v1.1`.
2. A prompt with `images: [<your picture>]` on ACE Music v1: bouncy drum and bass for a dancing robot mascot. With the robot picture above, ACE Music titled it "Bleep Boop Bounce" and wrote lyrics about what it saw: the teal fur, the orange high-tops, the box head and its blinking bulb eyes. [Listen to it](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#your-audio-and-pictures).
   Watch and hear it: [Bleep Boop Bounce, the YouTube Short](https://youtube.com/shorts/z_aOmILvIng).

Each costs 4 credits. `useAudio` and `useImage` tell the script which upload to attach. Every upload's `songId` or `mediaId` is also saved to `output/uploads.jsonl`, so you can cover, remix or mash up your recording later with `--song`. `--only 0` uploads without making songs.

Everything lands in `output/` next to the script: each song's MP3 and cover art, the job record as JSON (with each `songId`, which the other examples take as `--song` or `--from`), and `ledger.jsonl`, one line per job with the model that ran and the credits it used.

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
