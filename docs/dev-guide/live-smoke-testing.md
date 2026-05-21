# Live Smoke Testing

`tests/live/` is the opt-in provider-auth smoke suite for the migrated branch.
These tests are intentionally:

- read-only
- single-call
- no-retry
- latency-bounded (`<10s`)
- excluded from the default `pytest` run

## Run It

1. Set the provider env vars listed in [.env.example](../../.env.example).
2. Run:

```powershell
pytest tests/live/ -q -m live
```

If a required env var is absent or still carries a placeholder value, the test
skips with an explicit reason instead of failing.

## What It Covers

- OpenAI: `GET /v1/models`
- LangSmith: project listing
- Wondercraft: episode listing
- ElevenLabs: voice listing
- Gamma: theme listing
- Kling: non-billable status probe against a fake task id
- Canva: `GET /rest/v1/users/me` with a direct Connect API access token
- Qualtrics: survey listing
- Consensus: MCP `tools/list` capability probe
- Notion: `GET /v1/users/me`
- Botpress: bot listing

## Named Tradeoffs

- Canva: this smoke uses a direct Canva Connect API bearer token. That is
  separate from the currently blocked Cursor MCP OAuth path; the smoke test is
  meant to verify account auth/connectivity, not the MCP browser flow.
- Consensus: the current repo transport does not expose a separate quota
  endpoint, so the smoke uses MCP `tools/list` as the cheapest auth and
  capability check.
- Kling: the current repo client surface does not expose a free account-info
  endpoint, so the smoke uses a fake task-id status lookup to verify auth
  without starting a billable generation.
