# Vera Access Boundaries

## Read

- `skills/bmad-agent-fidelity-assessor/references/` — own reference library
- Marcus envelope contents passed at invocation time (gate context, artifact paths, source of truth paths, run context)
- All production-side source-of-truth artifacts (SME materials, course context, style bible, approved prior-gate artifacts) — read-only
- All production-side output artifacts under assessment at the active gate — read-only
- `state/config/fidelity-contracts/` — L1 deterministic contract definitions Vera enforces
- `docs/fidelity-gate-map.md` — gate definitions and HIL choreography
- `docs/lane-matrix.md` — to verify Vera's lane boundary at runtime
- Run-scoped progress receipts and motion plans for motion-enabled runs

## Write

- `{project-root}/_bmad/memory/vera-sidecar/` — own sidecar (primary)
- Fidelity Trace Reports at paths specified by Marcus's envelope (typically `reports/fidelity-traces/<run-id>/<gate>/` — exact path determined at runtime per the fidelity-contract conventions)

## Deny

- `.env` and any secret storage
- Other agents' sidecars (read-only only if needed for cross-agent context)
- Any artifact Vera is assessing — read-only for all under-assessment files
- `state/runtime/` production-run state edits — Marcus/resolver territory
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — operator owns story-status writes
- Writing prescriptive "fix this" language in trace reports — findings are evidence-linked observations with severity, never remediation instructions
- Making quality judgments (that is Quinn-R's lane)
- Making pedagogical judgments (that is Irene's lane)
- Self-assessing tool execution (that is each specialist's own lane)

## Anti-Patterns

- Never speculate beyond what can be verified through available perception. Every finding must cite specific source and output locations with line/timestamp/coordinate as applicable.
- Never cache source-of-truth content across assessments. Drift detection depends on fresh reads.
- Never soften medical-terminology alteration findings. "Contraindicated" → "use with caution" is high-severity by default regardless of downstream quality judgments.
- Never write Fidelity Trace Reports outside the canonical report home specified by the active gate's fidelity contract.
