# ACE Music API examples (useapi.net)

Runnable Node.js and Python examples for the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api): two songs per request from a prompt or from your own lyrics on ACE Music v1, ACE Music v1.1 Preview and the free ACE-Step v1.5 XL, then covers, remixes, edits, mashups, stems, WAV, MIDI and MusicXML downloads and scores. It all runs through a REST API on your [ACE Music subscription](https://acemusic.ai/pricing/): Free, Creator $9.90 or Artist $29 a month (as of November 2026). ACE-Step v1.5 XL songs use no credits on any ACE Music plan.

ACE Music v1 ranks #1 on [Artificial Analysis' vocal music leaderboard](https://artificialanalysis.ai/music/leaderboard/vocals), ahead of Suno v6 (as of November 14, 2026).

Every example has a Node.js script (`.mjs`) and a Python twin (`.py`), with no dependencies to install, and most read their requests from a `prompts.json` you edit. Each one submits its requests, polls the jobs, downloads the songs into its own `output/` folder and prints what it made. Full walkthrough of every call: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api)**.

| Example | What it does | Tutorial section |
|---|---|---|
| [`songs-from-prompt/`](./songs-from-prompt) | Songs from a description on **ACE Music v1**, **v1.1 Preview** and **ACE-Step v1.5 XL**: ACE Music writes the style, lyrics and title | [Make songs from a prompt](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#make-songs-from-a-prompt) |
| [`custom-lyrics/`](./custom-lyrics) | Your own lyrics, style and title, an instrumental, Spanish lyrics, and lyrics and a style written by ACE Music's writers | [Sing your own lyrics](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#sing-your-own-lyrics) |
| [`ace-step-options/`](./ace-step-options) | **ACE-Step** at an exact tempo, key, time signature and length, for no credits | [Tempo, key and time signature](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#control-tempo-key-and-time-signature-with-ace-step) |
| [`covers-remix-edit/`](./covers-remix-edit) | Cover a song in a new style, remix it, or rewrite seconds 30 to 50 with new words | [Covers, remixes and edits](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#covers-remixes-and-edits) |
| [`mashup/`](./mashup) | Two or three songs into one on **ACE Music v1.1**, with `model` and `modelUsed` | [Mashups](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#mash-up-two-or-three-songs) |
| [`upload-reference/`](./upload-reference) | Upload your own audio or a picture and make songs guided by it | [Your own audio and images](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#guide-songs-with-your-own-audio-and-images) |
| [`stems-and-downloads/`](./stems-and-downloads) | Vocal and instrumental or every stem, MP3, WAV, MIDI, MusicXML and the score in ABC notation | [Stems](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#split-a-song-into-stems), [downloads](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#download-mp3-wav-midi-and-musicxml) |
| [`async-webhooks/`](./async-webhooks) | Sync and async requests, job polling, `replyUrl` webhooks and a small webhook receiver | [Sync, async and webhooks](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#sync-async-and-webhooks) |
| [`library/`](./library) | List an account's songs, read one with fresh links, delete one | [Your Library](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#your-library) |
| [`accounts/`](./accounts) | Add an ACE Music account, read its live credits, set `maxJobs` | [Several accounts](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#several-ace-music-accounts) |

## Quick start

You need [Node.js](https://nodejs.org) 21 or newer or [Python](https://www.python.org) 3.8 or newer, a useapi.net [API token](https://useapi.net/docs/start-here/setup-useapi?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api), and an ACE Music account added with [Setup ACE Music](https://useapi.net/docs/start-here/setup-acemusic?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) (one [$15/month subscription](https://useapi.net/docs/subscription?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) covers every useapi.net API and 3 ACE Music accounts):

```bash
git clone https://github.com/useapi/acemusic-api.git
cd acemusic-api
export USEAPI_TOKEN=user:12345-...        # your useapi.net API token
export ACEMUSIC_EMAIL=you@example.com     # optional: the ACE Music account to use
node songs-from-prompt/songs-from-prompt.mjs --only 3
# or, the same with Python:
python3 songs-from-prompt/songs-from-prompt.py --only 3
```

`--only 3` runs the third prompt, an ACE-Step song that uses no credits, so you can try it on a Free account. Then chain the examples: every job record a script saves in its `output/` folder holds the songs' `songId`s, and `--from <job>.json --pick 1` hands song 1 to the next script.

```bash
# your own lyrics on ACE Music v1 (4 credits)
node custom-lyrics/custom-lyrics.mjs --only 1
# cover it (4 credits), remix it and rewrite seconds 30 to 50 (no credits)
node covers-remix-edit/covers-remix-edit.mjs --from custom-lyrics/output/<job>.json --pick 1
# split it into vocal + instrumental (5 credits) and download WAV, MIDI, MusicXML and the score (paid ACE Music plans)
python3 stems-and-downloads/stems-and-downloads.py --from custom-lyrics/output/<job>.json --pick 1 --score
```

The scripts that start something new take `--email` to pick an account (a song, an upload or a job already names the account it is on), and the ones that read `prompts.json` take `--prompts` and `--only 1,3`. The shared helpers are in [`lib/`](./lib): one API call with retries on `429` and `503`, job polling, downloads and a spend ledger (`output/ledger.jsonl`).

## What it costs

ACE Music charges its own credits per request, from the plan you already pay for (as of November 2026):

| Request | Credits |
|---|---|
| Two songs on ACE Music v1 or v1.1 | 4 |
| Two songs on ACE-Step v1.5 XL | 0, on every plan |
| Stems: vocal + instrumental / every stem | 5 / 60, paid plans |
| Score of an ACE-Step song, first read | 1 |
| Lyrics and style writers, uploads, WAV, MIDI and MusicXML | 0 in our tests (WAV, MIDI and MusicXML need a paid plan) |

A song costs 2 credits, from $0.013 on Artist billed yearly to $0.023 on Artist monthly. The [API overview](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#pricing) has the price on every plan. Making every song for our tutorial with these scripts used 117 credits on an Artist account, 65 of them for the two stem splits.

## MCP server

useapi.net also runs a hosted [Model Context Protocol](https://modelcontextprotocol.io) server for ACE Music, so an AI assistant such as the Claude app, ChatGPT, Claude Code, Cursor or VS Code Copilot can make songs on your ACE Music account. It has 15 tools: songs from an idea or your own lyrics, covers, remixes, edits, mashups, stems, scores, downloads, the lyrics and style writers, uploads, jobs and accounts. Nothing to install or run locally.

- Endpoint: `https://api.useapi.net/v1/acemusic/mcp`
- Transport: Streamable HTTP
- Authorization: your useapi.net API token in the `Authorization: Bearer …` header. The Claude app and ChatGPT sign in with OAuth instead.

Claude Code:

```bash
claude mcp add --transport http useapi-acemusic https://api.useapi.net/v1/acemusic/mcp --header "Authorization: Bearer YOUR_API_TOKEN"
```

Cursor, VS Code, the Claude app, ChatGPT and the full tool list: [ACE Music MCP server docs](https://useapi.net/docs/api-acemusic-v1/mcp?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api).

## Common questions

<!-- Facts as of 2026-11-14, the same as the useapi.net ACE Music API overview (docs/api-acemusic-v1/index.md): acestep.io/pricing (API only on the $49 Studio plan, about 360 songs a month), acemusic.ai/pricing (Creator $9.90, Artist $29, yearly $94.80 and $199). -->

- **Is there an ACE Music API?** Through useapi.net, yes: the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) runs ACE Music v1, ACE Music v1.1 Preview and ACE-Step v1.5 XL over REST on your ACE Music account, and these examples call every part of it.
- **How much does an ACE Music song cost through an API?** Through useapi.net, an ACE-Step v1.5 XL song uses no credits on any ACE Music plan, the Free plan included, against the API of the third-party acestep.io, which needs its $49 a month Studio plan (about 360 songs a month, about $0.14 a song, as of November 2026). An ACE Music v1 song costs 2 credits, $0.013 on Artist billed yearly.
- **Can Claude or ChatGPT make songs with ACE Music?** Yes, through the useapi.net [ACE Music MCP server](https://useapi.net/docs/api-acemusic-v1/mcp?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api): 15 tools for songs, covers, mashups, stems and scores, connected with your API token or OAuth, nothing to install. Compared with ACE Music's own MCP server at `acemusic.ai/mcp` (as of November 18, 2026), it adds the free ACE-Step v1.5 XL model, MP3 downloads on the Free plan, stems, one-call covers, remixes, edits and mashups, MusicXML, style and lyrics written by ACE Music from a one-line idea, several accounts behind one token, and the same calls over REST. See the [full comparison](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#useapinet-vs-ace-musics-own-mcp-server).
- More answers: [How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#questions).

## About useapi.net

[useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) is a third-party REST API for AI websites, not affiliated with ACE Music or Timedomain. The ACE Music API runs on your [ACE Music subscription](https://acemusic.ai/pricing/), so you make songs at its plan credit prices. See the [model matrix](https://useapi.net/model-matrix?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) and pricing on the [API overview](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api).

Visit our [Discord Server](https://discord.gg/w28uK3cnmF) or [Telegram Channel](https://t.me/use_api) for any support questions and concerns.

We regularly post guides and tutorials on the [YouTube Channel](https://www.youtube.com/@useapi-net).

## License

The example code in this repository is released under the [MIT License](./LICENSE). It covers the example scripts only, not the useapi.net service or API.
