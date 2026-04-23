# LangGraph Runtime Setup — Slab 1 Substrate (structural stub)

> **Status:** Slab 1 structural stub. Story 1.7 lands the final prose polish (intro,
> motivation, full operator setup steps, troubleshooting). This file's purpose at the
> end of Story 1.1c is to make the **inverted transport-parity matrix** grep-able so
> downstream stories (1.1d, 3.4, anyone reasoning about FR2) can see the contract at a
> glance.

## Transport Parity Contract — at-a-glance matrix

The migration runtime exposes the same minimal LangGraph node behind three transports
per architecture decision **D7** (Operator-surface contract — three-transport parity)
and **FR2** (compound MCP + FastAPI + CLI substrate). Each cell answers one question:
*does this transport have the corresponding artifact landed yet?*

|                          | FastAPI                | MCP                              | CLI                |
| ------------------------ | ---------------------- | -------------------------------- | ------------------ |
| **Code present**         | ✅ 1.1c                | ✅ 1.1c                          | ⏳ Slab 3          |
| **Smoke test (per-PR)**  | ✅ 1.1c                | — (not per-PR by design)         | ⏳ Slab 3          |
| **Smoke test (nightly / on-merge)** | — (covered per-PR) | ✅ 1.1d                          | ⏳ Slab 3          |
| **Parity acceptance**    | — (parity is two-transport at M1) | ✅ 1.1d (M1 gate green) | ⏳ Slab 3 (3.4) |

**Reading the matrix:** rows are artifact kinds; columns are transports. A `✅` means the
artifact is on disk and exercised at the cited story. A `—` means *N/A by design* (with
the design rationale in the cell). A `⏳` means deliberately deferred to a downstream slab.

## MCP transport — Slab 1 substrate vs production-ready

> **MCP code substrate landed in 1.1c; nightly / on-merge stdio smoke + FastAPI↔MCP
> byte-equivalent parity assertion landed in 1.1d. Both transports are now M1-substrate
> for the FR2 compound contract; CLI completes the three-transport claim in Slab 3
> Story 3.4. The "production-ready" qualifier still depends on Slab 2 specialist
> migrations exercising real workloads through these transports — Slab 1 closure is
> substrate, not feature-complete.**

What landed in 1.1c (this story):

- `app/mcp_server/protocol.py` — `MCP_PROTOCOL_VERSION` re-export from the shipped
  `mcp` SDK (`mcp.types.DEFAULT_NEGOTIATED_VERSION`). Pin lives here so an SDK upgrade
  cannot silently shift our protocol surface.
- `app/mcp_server/server.py` — `mcp.server.Server` instance plus `register()` for
  the `ping` tool.
- `app/mcp_server/tools/ping.py` — one real `list_tools` / `call_tool` handler pair
  that invokes the shared `app.runtime.minimal_node`.
- `app/mcp_server/__main__.py` — `uv run python -m app.mcp_server` boots the server
  over stdio.

What 1.1d will add:

- A subprocess stdio smoke that drives an actual MCP round-trip against
  `app.mcp_server.__main__`.
- A FastAPI↔MCP byte-equivalent parity assertion: invoke `/invoke` and the MCP `ping`
  tool with the same payload, then assert the response payloads are identical (both
  go through `app.runtime.minimal_node`).
- Flakiness budget: > 2% across the first 20 nightly runs reopens 1.1d.

## Why MCP smoke runs nightly, not per-PR

Origin: 2026-04-22 party-mode middle-path consensus on MCP-in-Slab-1 (5/5 vote).
Rationale and trade-offs are recorded in
[`_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md` §8](../../_bmad-output/planning-artifacts/slab1-story-set-A-t1-bundle.md#§8-middle-path-consensus-origin-preserve-for-forensic-value).

## Sections deferred to Story 1.7

1.7 owns the operator-facing prose: Postgres + DATABASE_URL setup, LangSmith project
naming, recommended `.env` structure, troubleshooting, and the worked-example walkthrough
that ties the matrix above to a real one-command boot.
