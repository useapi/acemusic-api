# ACE Music via useapi.net

This extension connects the hosted useapi.net ACE Music MCP server (`useapi-acemusic`, 15 tools). The tools make songs from an idea or the user's own lyrics, cover, remix, edit and mash up songs, split stems and get scores, on the user's own ACE Music accounts. Every request makes two songs.

- Endpoint: https://api.useapi.net/v1/acemusic/mcp (Streamable HTTP), authorized with the user's useapi.net API token in `USEAPI_TOKEN`.
- Before the tools work, the user needs a useapi.net API token (https://useapi.net/docs/start-here/setup-useapi) and an account connected at https://useapi.net/docs/start-here/setup-acemusic.
- If a tool returns 401, ask the user to check `USEAPI_TOKEN` (`gemini extensions config useapi-acemusic`). If it says no account is configured, point them to the setup page above.
- Generations spend the credits of the user's ACE Music plan (the free ace-step-1.5-xl model uses none). Ask before starting paid jobs, and report job status and links when they finish.
- Full tool list and limits: https://useapi.net/docs/api-acemusic-v1/mcp

useapi.net is a paid third-party API service ($15/month, covers every useapi.net API), not affiliated with ACE Music or Timedomain.
