# 5a.2 Parity Evidence

## Scope
- Primary frozen baseline: `C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid/course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion`
- Clone reference surface: `C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid/state/config/runs/C1-M1-PRES-20260419B`
- Deterministic local harness reference: `C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid/tests/fixtures/marcus/baseline_envelope/2026-04-26/envelope.json`
- Compared at: `2026-04-26T21:46:57.497231+00:00`
- AC-A remains operator-window conditional as of 2026-04-26 because `app.marcus.cli trial start --preset production --input <corpus-path>` does not exist on `dev/langchain-langgraph-foundation`. The parity report below measures only the comparable control-plane artifacts that do exist on the current branch.
- Deterministic local harness reference is present at `C:/Users/juanl/Documents/GitHub/course-DEV-IDE-with-AGENTS-hybrid/tests/fixtures/marcus/baseline_envelope/2026-04-26/envelope.json` and is cited as the local replayable surface alongside the frozen primary bundle.

## Tier 1
TIER 1 Score: 100% (4/4 comparable artifact families present; threshold: 80%)

Tier 1 measures whether the actual branch substrate exposes the same comparable control-plane artifact families on both sides of the parity boundary.

## Tier 2
TIER 2 Score: 100% (4/4 comparable families structurally matched after run-id, path, and timestamp normalization; threshold: 60%)

Tier 2 measures semantic parity across the comparable artifact families that exist on both sides. This is actual-substrate control-plane parity, not a claim that a full production clone trial was launched on this branch.

## Artifact Results

| Artifact family | Primary path | Clone path | Structural match | Verdict | Rationale |
| --- | --- | --- | --- | --- | --- |
| course_context | `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/run-constants.yaml` | `state/config/runs/C1-M1-PRES-20260419B/course_context.yaml` | 100% | parity-or-better | Canonical shared-control-plane fields matched after run-id, path, and timestamp normalization. |
| module_context | `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/run-constants.yaml` | `state/config/runs/C1-M1-PRES-20260419B/module_context.yaml` | 100% | parity-or-better | Canonical shared-control-plane fields matched after run-id, path, and timestamp normalization. |
| asset_specs | `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/gary-outbound-envelope.yaml` | `state/config/runs/C1-M1-PRES-20260419B/asset_specs.yaml` | 100% | parity-or-better | Canonical shared-control-plane fields matched after run-id, path, and timestamp normalization. |
| motion_plan | `course-content/staging/tracked/source-bundles/apc-c1m1-tejal-20260419b-motion/motion_plan.yaml` | `state/config/runs/C1-M1-PRES-20260419B/motion_plan.yaml` | 100% | parity-or-better | Canonical shared-control-plane fields matched after run-id, path, and timestamp normalization. |

## Operator-Window Status

- AC-A remains conditional because no runnable `app.marcus.cli trial start --preset production --input <corpus-path>` subcommand exists on this branch as of 2026-04-26.
- No artifact in this report should be read as evidence that a new production clone trial was launched end-to-end.
- To retire the conditional state, a future story or follow-on must land a real clone-trial launcher and re-run the same corpus against the same frozen primary baseline.
