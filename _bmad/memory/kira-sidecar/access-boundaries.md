# Kira Access Boundaries

## Read

- `skills/bmad-agent-kling/references/` — own reference library
- `skills/kling-video/` — the execution skill Kira routes to
- Marcus envelope contents passed at invocation time
- `resources/style-bible/` — re-read fresh every task (visual tone, professional medical aesthetic)
- Upstream production assets referenced in the envelope: Gary/Gamma PNGs, Irene's briefs, ElevenLabs audio — read-only
- Production progress receipts for resume/duplicate-prevention
- Run-scoped `motion_plan.yaml` for motion-enabled runs

## Write

- `{project-root}/_bmad/memory/kira-sidecar/` — own sidecar (primary)
- MP4 outputs at paths specified by Marcus's envelope — one-shot per generation after local validation succeeds
- Progress-receipt updates via the production-coordination entrypoints (not by direct file write)

## Deny

- `.env` and any secret storage; never log API keys, JWTs, or access/secret key values
- Other agents' sidecars (read-only only if needed for cross-agent context)
- `state/runtime/` direct edits — always route state changes through `run_motion_generation.py` or the canonical production-coordination scripts
- `resources/style-bible/` — read-only reference
- Kling API client code (`kling_client.py`) — stable, do not modify
- Native-audio field in Kling requests — silent production omits it entirely; never emit
- Singapore `3.0` surface — exploratory only; never promote into production runs

## Anti-Patterns

- Never patch production state before local MP4 validation succeeds.
- Never re-generate without first checking progress receipts for the run.
- Never cache style-bible content across tasks.
- Never emit the native-audio field in Kling requests — silent production is the validated posture.
- Never bypass Marcus envelope authority for Gate 7E production runs.
