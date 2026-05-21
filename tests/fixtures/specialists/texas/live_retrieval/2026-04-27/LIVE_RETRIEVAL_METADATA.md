# M3 Live Retrieval Metadata - 2026-04-27

- **Provider:** scite (Texas provider directory; shape=retrieval, status=ready)
- **Transport:** MCP Streamable HTTP via OAuth 2.1 (Authorization Code + PKCE; browser-based)
- **Endpoint:** `https://api.scite.ai/mcp`
- **OAuth client_name:** course-content-production-m3-ceremony
- **Token cache:** `C:\Users\juanl\.cache\course-content-production\scite-mcp\token.json` (operator-local; not committed)
- **Tools discovered:** 1 (search_literature)
- **Tool invoked:** `search_literature` with arguments `{"term": "neuroplasticity adult learning evidence-based instructional design", "limit": 5}`
- **isError:** False
- **Content items returned:** 1
- **Evidence path:** `tests/fixtures/specialists/texas/live_retrieval/2026-04-27/0652e5bf5729136e11c6a7d3e224db9f8b72f97c90ace57caa77f5a7654fa3e4.json`
- **SHA256:** `0652e5bf5729136e11c6a7d3e224db9f8b72f97c90ace57caa77f5a7654fa3e4`
- **Captured at:** 2026-04-27T07:18:57.391151+00:00
- **Texas retrieval contract:** `skills/bmad-agent-texas/references/retrieval-contract.md`
- **Note:** existing `SciteProvider` is hardwired to HTTP Basic auth (legacy assumption);
  this ceremony bypasses it via the official `mcp` SDK's `OAuthClientProvider`. The
  SciteProvider auth-model defect is filed as deferred-inventory follow-on
  `5a-2-scite-mcp-oauth-integration` for proper migration of the production class.
