# Consensus MCP live smoke (Cursor OAuth) — 2026-07-10

**Server:** `project-0-course-DEV-IDE-with-AGENTS-hybrid-Consensus`  
**Status:** ready (1 tool: `search`)  
**Auth:** mcp-remote OAuth as `jcph@jefferson.edu` (token cached under `~/.mcp-auth`)

## Query

`worked examples improve novice transfer introductory instruction`

## Result

- **PASS** — 20 papers returned via Cursor MCP `search`
- Top hits include worked-example / transfer literature (Chen 2023; van Gog 2004; Likourezos 2017; etc.)
- Inline citations available from tool payload

## Bridge to Texas / R2

- OAuth `access_token` reused as Bearer `CONSENSUS_API_KEY` for Python `ConsensusProvider`
- Live MCP markdown response parser added (`_parse_markdown_papers`)
- Wrong host `api.consensus.app/mcp` remapped → `mcp.consensus.app/mcp`
- R2 dual-provider live witness: `../research-r2-20260710T215111Z/` **PASS**
