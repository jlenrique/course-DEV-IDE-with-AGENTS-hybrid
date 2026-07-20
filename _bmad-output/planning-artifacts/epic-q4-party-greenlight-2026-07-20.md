# Epic Q4 — Quality Scorecard Live-Wiring (R2): Party Green-Light

**Date:** 2026-07-20 · **Facilitator:** orchestrator (autonomous per operator direction "proceed with the live-wiring") · **Branch:** `dev/quality-scorecard-epic-2026-07-19`.

**Decision:** live-wire the completed 8-dimension Project Quality Scorecard into the production runtime at run-end, on BOTH surfaces the operator chose: (1) a standalone `state/config/runs/<trial_id>/quality-final-report.md` (full report via `app/quality/report.py::render_scorecard_final_report`), and (2) a compact `quality` tile folded into the per-run `operator-surface.json` for the HUD flight deck.

## Votes — 6/6 GO-WITH-AMENDMENTS (unanimous; no dissent, no impasse)

| Voice | Role | Vote | Headline |
|---|---|---|---|
| Winston | Architect | GO-WITH-AMENDMENTS | Assembler imports `app.quality` (deferred local); model gains a typed `QualitySection` — both layer rules + clean-leaf intact. Tile rides `assembler.emit()` at `completed`; `.md` is a run-end deliverable helper. **Kill the /100 score.** |
| Cora | Governance-envelope / block-mode | GO-WITH-AMENDMENTS | **Additive `operator-surface.v1` in-place — NO schema-version bump, NO pack bump** (Epic-35 additive-row precedent). Block-mode fires but L1 passes trivially; shape-pin + parity are the real arbiters. Nothing frozen touched. |
| Audra | Lockstep / deterministic-neck | GO-WITH-AMENDMENTS | L1 (10 checks) orthogonal to operator-surface. **Emit reads the COMMITTED doc, never `app.quality.signals.*` live recompute** (Q3.2 determinism trap). 6-file coupled commit; `unknown == None`. |
| Murat | Test Architect | GO-WITH-AMENDMENTS | Projector already fail-soft + wall-clock-free → pure emit plumbing. Byte-match hermetic fixture proves the BUILD; **two-walk/no-double-emit is the top-risk pin**; R2 witness **updated, not closed**. |
| Amelia | Developer | GO-WITH-AMENDMENTS | Wire at the shared `_emit_run_summary_yaml` seam + sole-writer assembler → two-walk gotcha dissolved. 2 core stories + 1 conditional HUD; Q4.1∥Q4.2 (disjoint block-mode files) if assembler self-populates. |
| John | PM | GO-WITH-AMENDMENTS | Guardrail **PASS** (per-run trust signal at the decision moment = genuine SPOC value). Small 2-story epic; build/close now vs live-equality witnesses **deferred to operator R2**. |

## Scope — Epic Q4, 2 core stories (+1 conditional)

- **Q4.1 — operator-surface `quality` tile.** New OPTIONAL `QualitySection` on `OperatorSurfaceProjection` (additive-within-v1); regenerated `operator-surface.v1.schema.json` byte-pin; assembler self-populates via deferred `app.quality` import at the completion choke-point. Block-mode files: `operator_surface.py`, `operator_surface_assembler.py`, `operator-surface.v1.schema.json` + parity/shape-pin tests.
- **Q4.2 — production_runner standalone report hook.** At the shared `_emit_run_summary_yaml` seam (terminal-completion), render `render_scorecard_final_report(block=read_scorecard_block(), history=history_path(), fence_state=fence_state)` → `quality-final-report.md`, fail-soft. Block-mode file: `production_runner.py` + new run-dir artifact.
- **Q4.3 — HUD tile render (CONDITIONAL).** Render the tile in `app/hud/**`. Collapses into Q4.1 if the HUD auto-renders present optional sections; kept separate only if it has a real render surface + tests. Serializes after Q4.1.

**Serialization:** Q4.1 ∥ Q4.2 (disjoint block-mode files; both only READ the `app.quality` clean leaf) — contingent on QLW-1 (assembler self-populates). Q4.3 after Q4.1.

## Binding amendments (QLW-1 … QLW-16) — consolidated from all six voices

1. **QLW-1 — Assembler self-populates the tile** (deferred local `app.quality` import), NOT runner-threaded — preserves sole-writer + keeps Q4.1/Q4.2 disjoint. [Amelia-1, Winston-1]
2. **QLW-2 — Wire at the shared choke-points, never per-walk:** `.md` at `_emit_run_summary_yaml` (fence_state already computed there, GL-5); tile at the assembler completion choke-point. [Amelia load-bearing, Winston-3, John-J2]
3. **QLW-3 — Terminal-completion trigger only:** both surfaces render only at genuine terminal completion (mirror `deliverables`' verb-condition), NEVER at the G1 start-walk pause / reject / resume-pause. Dedicated two-walk + no-double-emit + not-at-pause pin. [Murat-A3, Amelia-2, Winston-3]
4. **QLW-4 — Emit reads the COMMITTED doc** (`read_scorecard_block()` / `dimension_ref()`), NEVER `app.quality.signals.*` live recompute; substantive fields carry the doc's `as_of`, not emit-time `now()`. Determinism-as-honesty (Q3.2). [Audra-A2]
5. **QLW-5 — Additive-within-v1, no schema_version/pack_version bump.** The coupled file set lands in one commit per story. [Cora, Audra-A1, John-J3, Amelia-4]
6. **QLW-6 — Compute-once / project-twice:** tile scores can never disagree with the standalone report for the same run (shared computed result); test it. [Cora-A1]
7. **QLW-7 — Kill the /100 score.** Tile carries: `available` marker, `band` (worst-across-dimensions), `ranked_leak_count`, `top_leaks` (top-N), `coverage_gaps`, `trend`. Band-aggregation rule pinned now. [Winston-1/A2]
8. **QLW-8 — Zero-lie / fail-soft (non-negotiable):** absent/corrupt/degraded scorecard → walk never perturbed (exception-swallowed); `.md` renders honest `unavailable` markers; tile renders `available=False`/`None`, never a fabricated band/green. Optionality at section + per-field level so `unknown == None` under `extra="forbid"`. Fail-soft pin on both surfaces. [Winston-3, Murat-A2, Audra-A4, John-J4, Amelia-6]
9. **QLW-9 — "No Band better than committed block" adversarial pin** (feed a block with open_leaks>0 → tile/report cannot render a clean/higher posture). [Murat-A5]
10. **QLW-10 — Idempotent / rewind-recover safe emit** (deterministic overwrite-clean, no double-append over the same trial_id). [Cora-A2]
11. **QLW-11 — Closed vocabularies re-declared VERBATIM** in model `Literal` + schema `enum` + a set-equality test; else no enum (no over-constraint). [Audra-A3]
12. **QLW-12 — Calibration honesty on the surface:** report + tile render the OWED/uncalibrated posture honestly, NEVER a fresh-naive number. [John-J7]
13. **QLW-13 — Block-mode governance:** each story's dev agent reads `docs/dev-guide/pipeline-manifest-regime.md` at T1; Cora's block-mode hook passes; `check_pipeline_manifest_lockstep.py` exit 0 (trivially — L1 orthogonal); **shape-pin + parity green in completion notes are the real arbiters**. [Cora-A3/A4, Audra-A1, Murat-A7, Amelia-3]
14. **QLW-14 — R2 witnesses updated-not-closed:** update `q1-4b-r2-final-report-projector-witness` → "wired + offline-proven; live-equality witness rides R2"; file NEW `q4-2-r2-hud-quality-tile-witness`. Do NOT run a live trial. [Murat-A6, John-J5/J6]
15. **QLW-15 — 3-layer adversarial review** (Blind/Edge/Acceptance) on each story diff; Edge walks the two-walk/double-emit boundary. [Murat-A8]
16. **QLW-16 — GL-4 re-coupling ACCEPTED** (re-reading the governance doc at run-end partially reverses Q1.4a/GL-4's decoupling) — acceptable ONLY because the projector is fail-soft by contract: the run must NEVER fail or vary because the governance doc is missing/edited. Recorded as an explicit accepted decision. [Audra governance note]

## Build/close vs deferred boundary

**Ships + closes autonomously now:** all offline-testable wiring — projector→`.md` at the emit seam, the additive tile + assembler population + (conditional) HUD render, fail-soft on both, block-mode-lockstep-clean, hermetic byte-match + fail-soft + two-walk + no-Band-inflation pins.

**Honestly deferred to the operator's R2 trial (operator-gated — CANNOT close without it):** the LIVE equality witnesses — `q1-4b-r2-final-report-projector-witness` (report == independently-computed env truth) + NEW `q4-2-r2-hud-quality-tile-witness` (tile == env truth). Named so nothing is silently skipped.

**Independent of** merge-to-master and the fresh-naive-holdout measurement; neither is preempted.
