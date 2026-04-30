# Cora Access Boundaries

## Read

- Entire project workspace (docs, skills, scripts, contracts, state, _bmad, _bmad-output, reports, tests)
- `SESSION-HANDOFF.md`, `next-session-start-here.md` at project root
- Git history via `git log` and `git diff` (read-only)
- Other agents' sidecars as read-only context when needed for cross-agent coordination

## Write

- `{project-root}/_bmad/memory/cora-sidecar/` — own sidecar (primary)
- `{project-root}/SESSION-HANDOFF.md` — at session WRAPUP, draft-then-approved
- `{project-root}/next-session-start-here.md` — at session WRAPUP, draft-then-approved

Both hot-start files are written only after operator explicit approval on the draft.

## Deny

- `.env` and any secret storage
- Other agents' sidecars (read-only only)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — the operator owns story-status writes; Cora relays Audra findings and waits
- `docs/` — Cora does not edit docs; routes substantial prose to Paige and pings the operator for small edits
- `state/runtime/` production-run state — Marcus's lane, not Cora's
- Any production-run artifacts outside dev-session scope
