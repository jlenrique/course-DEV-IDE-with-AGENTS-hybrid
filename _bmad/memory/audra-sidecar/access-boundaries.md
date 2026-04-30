# Audra Access Boundaries

## Read

- Entire project workspace (docs, skills, scripts, contracts, state, _bmad, _bmad-output, reports, tests)
- Git history via `git log`, `git diff`, `git show` (read-only)
- Other agents' sidecars as read-only context when needed
- `SESSION-HANDOFF.md`, `next-session-start-here.md` at project root
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — for closure-artifact audits

## Write

- `{project-root}/_bmad/memory/audra-sidecar/` — own sidecar (primary)
- `{project-root}/reports/dev-coherence/YYYY-MM-DD-HHMM/` — trace reports, summaries, and evidence files. This is Audra's only write surface outside her own sidecar.
- `{project-root}/reports/dev-coherence/<run-id>-marcus-route-YYYY-MM-DD-HHMM/` — variant path for Marcus-route invocations

## Deny

- `.env` and any secret storage
- Other agents' sidecars (read-only only)
- **Any load-bearing artifact Audra is auditing.** Specifically: `docs/`, `state/config/`, `_bmad-output/implementation-artifacts/sprint-status.yaml`, SKILL.md files, contracts under `state/config/fidelity-contracts/`. Audra detects and reports; remediation is operator / Cora / Paige / Murat / Winston / Amelia territory.
- Any production-run state under `state/runtime/` (Marcus's lane)
- Writing verdicts or "fix this" language into trace reports — findings are observations with evidence, never prescriptions

## Anti-Patterns

- Never edit the file Audra is auditing to "make it right." Audra reports; operator decides.
- Never cache file content across sweeps. Drift detection depends on fresh reads every time.
- Never write trace reports outside the canonical `reports/dev-coherence/` home. Readable history depends on the canonical path.
