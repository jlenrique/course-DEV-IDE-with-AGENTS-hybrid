# Check Strategy Matrix

Determines which pre-flight validation method to use for each tool based on its access tier and current integration status.

## Decision Logic

```
Is MCP configured and verified in Cursor?
  YES → MCP config check + optional API heartbeat  → classify as MCP-ready
  NO  → Does the tool have a REST API?
          YES → Is there a focused smoke script?
                  YES → Run smoke script              → classify as API-ready
                  NO  → Run heartbeat_check.mjs entry  → classify as API-ready
          NO  → Is the tool manual-only?
                  YES →                                → classify as manual-only
                  NO  → Known blocker?
                          YES →                        → classify as blocked/deferred
```

## Current Tool Mapping

| Tool | Tier | MCP Status | Pre-Flight Method | Script |
|---|---|---|---|---|
| Gamma | 1 | Active in Cursor | MCP config + heartbeat | `heartbeat_check.mjs` |
| Canvas LMS | 1 | Active in Cursor | MCP config + heartbeat | `heartbeat_check.mjs` |
| ElevenLabs | 1 | Deferred (tool name length) | Smoke script | `smoke_elevenlabs.mjs` |
| Qualtrics | 1 | Deferred (npm build) | Smoke script | `smoke_qualtrics.mjs` |
| Canva | 1 | Deferred (OAuth redirect) | Report blocker | Static |
| Botpress | 2 | N/A | Heartbeat | `heartbeat_check.mjs` |
| Wondercraft | 2 | N/A | Heartbeat (env: `WONDERCRAFT_API_KEY`; Wanda specialist — Sprint 2 Story `wondercraft-specialist-agent`) | `heartbeat_check.mjs` |
| Kling | 2 | N/A | Config presence | `heartbeat_check.mjs` |
| Panopto | 2 | N/A | Config presence | `heartbeat_check.mjs` |
| Descript | 3 | N/A | Config presence | `heartbeat_check.mjs` |
| Vyond | 4 | N/A | Manual-only | Static |
| CourseArc | 4 | N/A | Manual-only | Static |
| Articulate | 4 | N/A | Manual-only | Static |

## When to Upgrade Check Methods

- When an MCP becomes verified in Cursor → move from API-only to MCP + API
- When a focused smoke script is created → move from heartbeat to smoke
- When a tool's API matures → move from config-only to active check
