# Story 43-11 — SPOC narration ↔ projector anti-drift

**Epic:** 43 · **Slab:** 4 · **Status:** ready-for-dev · **Gate mode:** dual-gate (touches the SPOC driver + a new parity guard).

## Story

The SPOC driver (`app/marcus/cli/marcus_spoc.py`) hand-formats the same G0E/G0R/gate review material as **prose**, independently of the tabular projector (`hil_tabular_projector.py`). Two independent renderings of the same data can **silently diverge** (rider R5 / the audit's drift-debt finding). This story installs an **anti-drift guard** so they can't.

## Approach (choose the lower-risk that holds)

**Preferred — a parity/anti-drift test** (default): a test that, given the SAME gate data (the 43-0 fixtures: `g0-enrichment-bc747b51.json`, `decision-card-{g0e,g0r}-bc747b51.json`, `operator-surface-*.json`), asserts the SPOC narration and the projector surface the SAME load-bearing facts (e.g. the same LO count / statements, the same flagged-ungrounded component set, the same enrichment counts). If they diverge, the test fails — pinning the invariant without a risky refactor.

**Optional — shared builder** (only if clean): route the SPOC narration's tabular/enumerated sections through a shared data-extraction helper (or the projector's builders) so there is a single source of truth. Do this ONLY if it does not disturb the SPOC prose voice or the `run_marcus_spoc` loop; otherwise stop at the parity test.

## T1 required readings

- `app/marcus/cli/marcus_spoc.py` — `narrate_gate` (~1219–1271), `_narrate_g0_enrichment` (~1086–1131), `_narrate_g0_refinement` (~1185–1216). What each emits + from what source data.
- `app/marcus/cli/hil_tabular_projector.py` — `render_enrichment_metrics`, `render_ungrounded_advisories`, `render_learning_objectives`, `build_gate_surface`.
- `tests/fixtures/hil_projector/` (the 43-0 fixtures) — the shared replay inputs.
- `tests/marcus/cli/test_marcus_spoc_narration.py` (existing SPOC narration tests — do not regress).

## Acceptance criteria

**AC-1 — anti-drift parity test.** A new test asserts the SPOC narration and the projector, fed the SAME gate data, agree on the load-bearing facts (LO set, ungrounded-component set, enrichment counts). Names the surfaces (G0E enrichment, G0R refinement). Deterministic / replay-only, zero spend.

**AC-2 — no SPOC regression.** `tests/marcus/cli/test_marcus_spoc_narration.py` (and any SPOC narration tests) stay green. If the optional shared-builder route is taken, the SPOC prose voice is preserved.

**AC-3 — invariants.** projector stays stdlib-pure; additive-within-v1; TW-7c-4 register any new test .py; ruff + import-linter clean; no manifest touch. Do NOT run the full suite (`-n 0`, touched files only). No commit/stash.

## Definition of done

Anti-drift guard installed (parity test, + optional shared builder if clean); SPOC narration tests green; ruff/import-linter clean; ready for orchestrator review → `bmad-code-review`.
