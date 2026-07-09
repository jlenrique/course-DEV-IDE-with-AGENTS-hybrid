---
title: 'Marcus planning ratification surface (CLI assess→elicit→ratify→write)'
type: 'feature'
created: '2026-07-09'
status: 'done'
story_key: 'marcus-planning-ratification-surface'
gate_mode: 'dual-gate'
baseline_commit: 'b69aa2de'
context:
  - '{project-root}/goal-marcus-planning-ratification-surface-2026-07-09.txt'
  - '{project-root}/_bmad-output/implementation-artifacts/marcus-planning-ratification-surface-claim-envelope-2026-07-09.md'
  - '{project-root}/_bmad-output/implementation-artifacts/phase2-evolutionary-planning-to-selection-bridge.md'
  - '{project-root}/_bmad-output/implementation-artifacts/planning-context-to-irene-pass1-handoff.md'
---

<!-- Party 2026-07-09: 4/4 GO-WITH-AMENDMENTS. AC-M5 OUT (majority).
     Impasse: Quinn → John → human. Live-test each major component as built. -->

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Purpose/audience/workflow/gap-fill can be recorded by library
functions, and Irene can consume `planning-ratification.json`, but an operator
cannot drive that recording through a Marcus-facing surface — only scripts.

**Approach:** Thin CLI `plan-ratify` under `python -m app.marcus.cli` that
assesses source, accepts non-interactive purpose/audience/workflow/gap-fill
flags, calls existing `ratify_planning_decision` / `write_ratification_artifacts`,
and writes companion JSON + S8 intent YAML into an operator-chosen directory
(typically a run_dir). Trial start continues to use
`--lesson-plan-collateral-intent`. No second planning engine. No Irene emit
change this slice (lesson-plan-as-pipe refs = next seed).

**Claim fence:** Does not claim full SPOC planning REPL, Gamma-spend published
deck walk, lecture ingestion, SME/projector, auto selection, planning_context
fan-out, or lesson_plan provenance refs (AC-M5 OUT).
**Operator amendment:** W5 local compose liveproof IS required for COMPLETE
(`compose_and_digest` + selection delta + trial `run_summary` threading).

## Party decisions (binding)

- Surface = real CLI subcommand (not library-only).
- Non-interactive flags are the test/liveproof contract.
- AC-M5 OUT; Winston dissent deferred.
- Dual-gate; write location must be loadable by `load_planning_context`.
- Trial-intent consumption required in liveproof.

## Boundaries

**Always:** reuse assess/ratify/write; fail-loud; AC-M6 absent path; live-test as built.  
**Never:** second engine; auto-wire into trial start; Irene `_act` emit changes; S8 reopen.

</frozen-after-approval>

## Code Map

| Area | Path |
|------|------|
| NEW | `app/marcus/cli/plan_ratify_cli.py` |
| MODIFY | `app/marcus/cli/__main__.py` |
| Tests | `tests/marcus/cli/test_plan_ratify_cli.py`, `tests/integration/marcus/test_plan_ratify_load_path.py` |
| DO NOT TOUCH | `planning_ratification.py`, `planning_context.py`, `irene_pass1/_act.py`, `trial.py` selection seam |

## Acceptance Criteria

### AC-M1 — CLI surface
`python -m app.marcus.cli plan-ratify` with required flags runs end-to-end.

### AC-M2 — Writes both artifacts
`planning-ratification.json` + `ratified-collateral-intent.yaml` under `--output-dir`.

### AC-M3 — Assessment required
Exactly one of `--corpus-dir` or `--course-root` (+ proposal/module as needed); missing → exit ≠ 0.

### AC-M4 — Loadable by existing consumers
`load_planning_context(output_dir)` returns framing; `resolve_intent_file` / trial intent path resolves `source=ratified`.

### AC-M5 — OUT (fenced)
No lesson_plan provenance refs this slice.

### AC-M6 — Absent path
No artifacts → `load_planning_context` is None; trial without intent flag unchanged.

### AC-M7 — Fail-loud + claim fence
Invalid gap-fill / overclaim / workbook-without-collateral → exit ≠ 0; evidence states non-claims.

### AC-M8 — W5 local compose liveproof (REQUIRED)
Plan-ratify intent → selection differs from baseline (delta) → `compose_and_digest`
succeeds on the ratified selection → `start_trial` with that intent threads
selection into `run_summary` / trial-start receipt. No Gamma spend required.

## Definition of Done

AC-M1..M4, M6, M7, **M8 (W5)** green; dual-gate party close; per-component live-tests banked; inventory/STATE/project-context updated; commit+push.

## Completion Notes (2026-07-09)

- Party CLOSE: COMPLETE-with-named-fenced-residuals (Claims A+B package).
- Evidence: `marcus-solicitation-success-20260709T230000/` + success definition doc.
- Claim B fenced: recording-handle Pass-1 emit (not live OpenAI); Claim A fenced: evidence live-run-dir (not `runs/<uuid>/`).
- `planning_provenance` landed on Irene lesson_plan when context present.
- Do not claim bespoke / live-model-informed plan.
