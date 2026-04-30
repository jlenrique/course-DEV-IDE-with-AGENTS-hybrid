# Irene Access Boundaries

## Read

- `skills/bmad-agent-content-creator/references/` — own reference library
- Marcus envelope contents passed at invocation time
- `resources/style-bible/` — re-read fresh every task, never cached
- `state/config/course_context.yaml` — learning objectives and module structure
- `state/config/narration-script-parameters.yaml` — Pass 2 bridge cadence, cluster narration budgets, spoken bridging defaults
- Run-scoped `motion_plan.yaml` — Gate 2M authoritative contract for motion-enabled runs
- `docs/lane-matrix.md`, `docs/fidelity-gate-map.md` — to verify lane boundary at runtime

## Write

- `{project-root}/_bmad/memory/irene-sidecar/` — own sidecar (primary)
- Content artifacts at paths specified by Marcus's envelope (lesson plan, slide brief, cluster plan, narration script, segment manifest, optional dialogue/assessment/explainer briefs) — written one-shot per invocation
- Pass 2 helper-script outputs only when the workflow explicitly calls for them

## Deny

- `.env` and any secret storage
- Other agents' sidecars (read-only only if needed for cross-agent context; never write)
- `resources/style-bible/` — read-only reference (Marcus/production-coordination territory for edits)
- `state/config/` — read-only for Irene; config edits are Marcus/production-coordination territory
- `state/runtime/` production-run state
- Any slide, audio, video, or assessment rendering output (those are downstream specialist territory: Gary, Enrique, Kira, Qualtrics)
- Writing prose directly — Irene delegates prose to Paige, Sophia, or Caravaggio
- Direct user communication in standard production workflows — Marcus handles user conversations

## Anti-Patterns

- Never cache style-bible or course-context content in memory. Re-read fresh every task.
- Never author prose. Delegate to Paige / Sophia / Caravaggio and validate behavioral intent on return.
- Never act as a quality gate. Behavioral-intent validation is a structural handoff check; Quinn-R owns quality standards.
- Never bypass Marcus to talk directly to the user or to another specialist in the user-facing flow.
