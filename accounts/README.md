# ACE Music accounts — ACE Music API (Node.js and Python)

Add an ACE Music account, read its live credits, and set how many requests it runs at once, through the [ACE Music API](https://useapi.net/docs/api-acemusic-v1?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) by [useapi.net](https://useapi.net/?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api).

Full walkthrough: **[How to Generate AI Songs with the ACE Music API](https://useapi.net/docs/articles/ace-music-api-tutorial?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api#several-ace-music-accounts)**

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
node accounts.mjs                                        # every account: plan, maxJobs, health
python3 accounts.py --credits --email you@example.com    # live plan, credits left, models and limits
ACEMUSIC_PASSWORD='…' node accounts.mjs --add --email you@example.com
python3 accounts.py --max-jobs 2 --email you@example.com
```

- [POST /accounts](https://useapi.net/docs/api-acemusic-v1/post-acemusic-accounts?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) signs in to ACE Music with the email and password you use at acemusic.ai, checks the account and stores it. The password is used only to sign in again when ACE Music ends the session and is never returned. The script reads it from `ACEMUSIC_PASSWORD`, never from the command line. Accounts made with Google or a phone number need a password first, see [Setup ACE Music](https://useapi.net/docs/start-here/setup-acemusic?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api).
- `maxJobs` (1 to 4, default 4, ACE Music's own limit) is how many requests the account runs at once. Posting `email` and `maxJobs` without a password changes only that.
- [GET /accounts/{email}](https://useapi.net/docs/api-acemusic-v1/get-acemusic-accounts-email?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api) reads the account live: plan, credits left, the models with their text limits, and the credit costs.
- Each useapi.net subscription connects 3 ACE Music accounts, up to 100 in total. Requests without `email` go to a healthy account with a free slot. Remove an account with [DELETE /accounts/{email}](https://useapi.net/docs/api-acemusic-v1/delete-acemusic-accounts-email?utm_source=github.com&utm_medium=referral&utm_campaign=acemusic-api).

---

Support: [Discord](https://discord.gg/w28uK3cnmF) · [Telegram](https://t.me/use_api) · [YouTube](https://www.youtube.com/@useapi-net)
