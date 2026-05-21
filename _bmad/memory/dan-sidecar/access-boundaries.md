> **DEPRECATED 2026-04-17** — see `index.md`. Dan's live sanctum is `_bmad/memory/bmad-agent-cd/`.

# Dan Access Boundaries

## Read

- `skills/bmad-agent-cd/references/` — own reference library, including `creative-directive-contract.md`
- Marcus envelope contents passed at invocation time (run context, upstream artifacts, constraints)
- `docs/lane-matrix.md`, `docs/fidelity-gate-map.md` — to verify the CD lane boundary at runtime
- `state/config/parameter-registry-schema.yaml` — to verify `slide_mode_proportions` and `narration_profile_controls` schema compliance before emitting output

## Write

- `{project-root}/_bmad/memory/dan-sidecar/` — own sidecar (primary)
- Creative directive artifact at the path specified by Marcus's envelope (one-shot output per invocation; path determined at runtime)

## Deny

- `.env` and any secret storage
- Other agents' sidecars (read-only only if needed for cross-agent context)
- `state/runtime/` production-run state — Marcus/resolver territory
- Run constants (`run_constants.py`) — Marcus/resolver territory
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — operator owns story-status writes
- Any narration script output — Irene's lane
- Any quality verdicts — Quinn-R's lane
- Any fidelity verdicts — Vera's lane

## Anti-Patterns

- Never emit ad-hoc mode keys. Only `literal-text`, `literal-visual`, `creative` are valid mode keys per SKILL.md guardrails.
- Never emit `slide_mode_proportions` that fail the numeric sum check (`sum = 1.0 ±0.001`).
- Never mutate run constants directly. Dan's output is advisory input for the resolver; the resolver persists.
- Never create alternate operator-facing intake surfaces. Dan is invoked only through Marcus's envelope.
