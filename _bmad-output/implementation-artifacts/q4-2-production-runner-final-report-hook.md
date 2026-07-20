# Story Q4.2 — production_runner standalone `quality-final-report.md` run-end hook

**Epic:** Q4 — Quality Scorecard Live-Wiring (R2) · **Status:** ready-for-dev · **Gate mode:** single-gate (a fail-soft run-end deliverable on a proven projector) · **Green-light:** `_bmad-output/planning-artifacts/epic-q4-party-greenlight-2026-07-20.md` (QLW-1…QLW-16).

## ⛔ T1 Readiness (read BEFORE any code — block-mode story)

`app/marcus/orchestrator/production_runner.py` is a **`block_mode_trigger_paths`** entry (pipeline-manifest line 106). Required T1 readings:

1. [`docs/dev-guide/pipeline-manifest-regime.md`](../../docs/dev-guide/pipeline-manifest-regime.md) — Cora's pre-closure hook runs `check_pipeline_manifest_lockstep.py` (must exit 0; orthogonal to this change — passes trivially since you touch NO manifest step/pack/node).
2. The two-walk structure of `production_runner.py`: the shared run-summary emitter **`_emit_run_summary_yaml` (~line 1559)** which **already computes `fence_state` as plain data (~line 1615)** and is inherited by all five terminal emit sites across BOTH walks (GL-5); AND the two duplicated terminal-completion blocks (~line 4367 and ~line 5652). See §"The seam" below.
3. `app/quality/report.py::render_scorecard_final_report(*, block, history, fence_state)` (already fail-soft, never-raises, wall-clock-free — AC4 of Q1.4b), `app/quality/scorecard.py::read_scorecard_block()`, `app/quality/history.py` history-path/read. GL-3 clean leaf.
4. `docs/quality/*` + `_bmad-output/implementation-artifacts/deferred-work.md` §"Deferred from: Story Q1.4b" (the `q1-4b-r2-final-report-projector-witness` entry you will UPDATE, not close) + the Q4 greenlight (QLW list).
5. The existing run-dir deliverable emitters in `production_runner` (run_summary.yaml, engagement report, cost-report) — mirror their fail-soft write pattern + atomic-write discipline.

## Story

**As** the operator (and the R2 audit trail), **I want** the full scorecard final report written to `state/config/runs/<trial_id>/quality-final-report.md` at run-end, **so that** every completed run carries a durable, honest Band + ranked-leaks + this-run `fence_state` artifact I can read and that the R2 witness can compare against independently-computed env truth.

This is WIRING the already-built, already-tested projector into the run-end seam. GL-15: no parallel plumbing — reuse `render_scorecard_final_report` verbatim.

## The seam (binding requirement; the exact site is the dev agent's call)

**BINDING (QLW-3):** the report renders **exactly once, only at genuine terminal completion, on BOTH node walks, and NEVER at the G1 start-walk pause / reject / resume-pause.**

Two candidate seams the party surfaced — pick whichever the code supports most cleanly, honoring the binding requirement:
- **(a) Shared emitter + terminal guard (Amelia):** wire inside/right-after `_emit_run_summary_yaml` (the single shared emitter both walks inherit, where `fence_state` is already in hand), GATED on a genuine terminal-completion condition (since `_emit_run_summary_yaml` also fires at pause/reject/resume — an unguarded call would emit at pauses, violating QLW-3).
- **(b) Shared helper called from both completion blocks (Winston):** a `_emit_quality_final_report(trial_id, runs_root, run_summary_path/fence_state)` helper called from BOTH duplicated terminal-completion blocks (~4367, ~5652).

Whichever you choose, the two-walk + terminal-only + exactly-once behavior is the AC — prove it with a test that exercises both walk entrypoints AND a pause path.

## Scope fence (binding)

**IN SCOPE:** render `render_scorecard_final_report(block=read_scorecard_block(), history=<history path>, fence_state=<the run's fence_state>)` → `state/config/runs/<trial_id>/quality-final-report.md`, fail-soft, idempotent, at terminal completion on both walks.

**OUT OF SCOPE / FORBIDDEN:** the operator-surface `quality` tile (that is Q4.1 — do NOT touch `operator_surface.py`/assembler/schema); redefining scoring; recomputing via `app.quality.signals.*` (QLW-4 — the projector already takes the committed `block`); editing `pipeline-manifest.yaml`/pack/generator/`PIPELINE_STEPS`/frozen packs; any `pack_version`/`schema_version` bump; running a live trial. If wiring needs a breaking change to the walk structure → 33-1 kill-switch: stop, escalate.

## Acceptance Criteria

**AC1 (the emit).** At terminal completion, `quality-final-report.md` is written under the run dir with the exact output of `render_scorecard_final_report(block=read_scorecard_block(), history=<history>, fence_state=<run fence_state>)`. The `fence_state` passed is the SAME one `_emit_run_summary_yaml` computed for that run (QLW-6 compute-once — do not recompute a second, possibly-divergent fence_state).

**AC2 (QLW-3 — two-walk, terminal-only, exactly-once).** RED-first pin: exercise BOTH walk entrypoints → the report is written once at terminal completion on each; exercise a non-terminal/pause path (e.g. the G1 start-walk pause) → the report is NOT written (no "final report" at a pause), and no double-emit occurs when both walks run over one trial.

**AC3 (QLW-8 — fail-soft, non-negotiable).** RED-first pin: inject (a) an absent/degraded scorecard block, (b) a corrupt run dir, (c) a degraded every-leaf `fence_state` → the walk is NEVER perturbed (the emit is exception-swallowed, mirroring `_emit_operator_surface`'s wrapper), and the `.md` still renders the projector's honest `unavailable`/`undetected` markers (never a fabricated Band). The run completes normally in every case.

**AC4 (QLW-10 — idempotent / rewind-safe).** A re-run / rewind-recover over the same `<trial_id>` overwrites cleanly (deterministic content for the same inputs); no double-append, no corruption. Pin two emits over the same dir → byte-identical, single file.

**AC5 (hermetic byte-match — QLW-2/Murat-A1).** RED-first: a synthetic run dir (`tmp_path`) with a known `run_summary.yaml` fence_state (both a healthy shape AND the degraded every-leaf shape), a committed scorecard block, and a small history ledger → assert the written `quality-final-report.md` is **byte-identical** to a direct `render_scorecard_final_report(...)` call on the same inputs (the hook adds/drops nothing). REUSE the existing goldens in `tests/quality/test_scorecard_final_report.py` as the input corpus — do NOT mint a parallel truth. Determinism carve-out: two emits with fixed inputs are byte-identical (the report is already wall-clock-free).

**AC6 (QLW-9 — no-Band-better-than-committed).** The report (via the projector) can never present a Band better than the committed block's worst posture — inherited from the projector, but add a guard test feeding a block with `open_leaks>0`.

**AC7 (QLW-14 — R2 witness updated, NOT closed).** UPDATE the `deferred-work.md` `q1-4b-r2-final-report-projector-witness` entry: its state moves from "wiring + witness both deferred" to **"wiring landed + offline byte-match-proven; the LIVE equality-against-env-truth witness still rides the operator R2 trial."** Update its `evidence` line to cite this story's hook + hermetic tests. Do NOT strike/close it (closing an unverified live path would be the exact silent-green lie the scorecard exists to prevent).

**AC8 (QLW-13 — block-mode closure).** `check_pipeline_manifest_lockstep.py` exits 0; ruff + import-linter clean; `tests/quality/` + the production_runner test suite green with no regression; completion notes cite the two-walk + fail-soft + byte-match pins.

## RED-first task hints

T1: readings + choose the seam (a/b) honoring QLW-3. T2: the emit helper (deferred `app.quality` import; reuse the run's fence_state). T3: the two-walk/terminal-only/exactly-once pin (RED first). T4: fail-soft + idempotent pins. T5: hermetic byte-match reusing goldens. T6: update the R2 witness entry. T7: ruff + import-linter + full suite + lockstep exit 0.

## Notes for the dev agent

- Do NOT touch `operator_surface.py`/assembler/schema (Q4.1's surface) — Q4.2 is disjoint.
- The projector is DONE and honest — this story is the hook + its pins, not projector changes.
- 3-layer adversarial review (Blind/Edge/Acceptance) follows dev; Edge walks the two-walk/double-emit boundary specifically (QLW-15).
