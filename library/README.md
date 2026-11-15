# Your ACE Music Library — ACE Music API (Node.js and Python)

List the songs of an ACE Music account, read one with fresh links, or delete one, through the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api). The Library holds every song of the account: made through the API or on acemusic.ai, and your uploads.

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#your-library)**

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
node library.mjs --limit 20               # newest first, one page
python3 library.py --all                  # every page
node library.mjs --song "user:12345-you@example.com-song:so_…"
python3 library.py --delete "user:12345-you@example.com-song:so_…"
```

- [GET /music](https://useapi.net/docs/api-acemusic-v1/get-acemusic-music?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) returns a page of songs and `next` for the following page (`null` on the last one). With several accounts, pass `--email`.
- [GET /music/{songId}](https://useapi.net/docs/api-acemusic-v1/get-acemusic-music-songid?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) returns one song with fresh links: `audioUrl`, `playUrl` (a direct link for players, until `playUrlExpires`) and its stems when it was split.
- [DELETE /music/{songId}](https://useapi.net/docs/api-acemusic-v1/delete-acemusic-music-songid?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) moves the song to the account's trash on acemusic.ai. Through the API it is gone: its `songId` answers `404`.

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
