# Story 43-2 — Generic gate-content table + renderer registry

**Epic:** 43 (HIL Surface Tabular Coverage) · **Slab:** 1 · **Status:** ready-for-dev
**Dispatch position:** FIRST substantive story (rider R1 — scaffold before bespoke).
**Gate mode:** dual-gate (touches the operator HIL emit path — the 42-1 escape lived here).

## Story

As the **operator** driving a live trial, when the runtime **pauses at ANY gate**, I want the gate's content projected as a **human-readable table on stderr** (not a dense JSON blob), so every review/approve juncture is reviewable — even before bespoke per-gate renderers exist.

This is the load-bearing scaffold: a **renderer registry** + a **generic fallback renderer** that tables any paused gate's poll-surface content. Bespoke renderers (43-1, 43-3…43-9) become progressive enhancements that register against this scaffold. Once this merges, **no gate raw-dumps**, even if the epic stalls.

## T1 required readings (BEFORE any code — per "review guides before adding gates/agents/services")

- `_bmad-output/planning-artifacts/epic-43-hil-surface-tabular-coverage.md` — §2 audited inventory, §4b riders (R1/R2/R4/R5/R7 bind this story), §5 constraints.
- `app/marcus/cli/hil_tabular_projector.py` — `_md_table` (:47), `build_gate_surface` (:234), `emit_gate_surface` (:255), `render_hil_tables` (:192). This is where the registry + generic renderer land.
- `app/marcus/cli/trial.py` — `_emit_gate_surface_if_paused` (:265–330, esp. the `status != "paused-at-gate"` early-return at :279 and the `build_gate_surface(gate_identity=…, enrichment=…)` feed at :309); `recover_trial_cli` (:1243–1259) and `resume_batch_trial_cli` (:1372–1379) — the two front doors that never call the projector; the `start`/`resume` call sites at :1006/:1164 for the pattern to mirror.
- Two representative poll-surfaces to learn the dict shape: `app/gates/section_04a/poll_surface.py` (:145 `display_plan_unit`) and `app/gates/section_11/poll_surface.py` (:81 `display_voice_candidates`).
- `app/marcus/orchestrator/operator_surface_assembler.py` — `_summarize_context_entry` (:653–683, the 240-char bounded flatten to REUSE for nested values) and the `DecisionCardSection` build (:685–722). Confirm the operator_surface projection contract is **additive-within-v1** (AD-4 / 35.9 precedent) — no schema bump for this render feature.
- Fixtures (from 43-0): `tests/fixtures/hil_projector/` — `decision-card-{g0e,g0r,g1}-bc747b51.json`, `operator-surface-{5169a872,bc747b51}.json`, `g0-enrichment-bc747b51.json`, `directive-*.yaml`, plus `README.md`. These are your replay inputs (zero live spend).

## Acceptance criteria

**AC-1 — Renderer registry (pin 2 generalized).** A registry maps a gate **content-type key** → a renderer callable, exposed so it can be **enumerated/introspected** (43-10's coverage test will consume this). Registering a renderer is the single, obvious extension point for every later story.

**AC-2 — Generic fallback renderer.** A generic renderer projects **any** paused gate's poll-surface content into a stderr table (key/value or row form) via `_md_table`. Nested/complex values are **bounded-summarized** (reuse the `_summarize_context_entry` 240-char pattern — rider R2); never dump raw nested JSON. Paginate >~15 rows per Marcus HIL Display Standards.

**AC-3 — Every paused gate tables its content (pin 1: no raw human dump at ANY gate).** `_emit_gate_surface_if_paused` feeds the **paused gate's own content** (its poll-surface dict / decision card) into the projector — not only `g0-enrichment.json`. Named surfaces exercised in tests: **G1 decision card** and **G0E/G0R** from the fixtures render as tables via the generic path (G1 currently has no bespoke renderer — it MUST now table, not blob).

**AC-4 — Front-door coverage holes closed.** `recover_trial_cli` AND `resume_batch_trial_cli` call `_emit_gate_surface_if_paused` on a `paused-at-gate` payload, mirroring `start`/`resume`. Named surfaces: **"recover front door"**, **"resume-batch front door"**. Tests prove a paused recover/resume-batch payload emits a table.

**AC-5 — stdout/stderr split is a HARD INVARIANT (rider R4).** The human table goes to **stderr**; **stdout stays untouched machine JSON**. A test asserts stdout parses as JSON and stderr carries the table, on the same invocation.

**AC-6 — Epic-wide raw-access affordance (rider R5).** The machine JSON on stdout is the documented **raw form** at every gate; the stderr surface carries a consistent one-line pointer to it (e.g. "raw: full JSON on stdout / <artifact path>"). Consistent across gates, not a G0-only affordance. Width-aware/fixed-width columns (no ugly wrap at 80 cols).

**AC-7 — Additive-within-v1 (rider R7).** Any operator_surface projection addition is a new optional field/section — no operator_surface schema-version bump for this render feature.

## Test requirements

- Replay-only against `tests/fixtures/hil_projector/` — **zero live spend**.
- RED-anchored: a test that the **G1 decision card fixture renders as a table via the generic path** (fails before the wiring, passes after).
- stdout-JSON / stderr-table split test (AC-5).
- recover + resume-batch paused-payload emit tests (AC-4).
- Registry introspection test (AC-1) — the enumerable content-type set.
- Bounded-nested-summarize test (AC-2) — a deeply nested value does not dump raw.
- Run ONLY the new/touched test files with `.venv/Scripts/python.exe -m pytest <files>`. Do NOT run the full suite (it backgrounds/hangs). Do NOT `git stash` for the baseline-diff — report with-changes green and let the orchestrator run the consumer-wide baseline-diff.

## Constraints

- **Pure-render.** No production-walk behavior change beyond the operator-facing surface. No new gate, no manifest touch (confirm the diff does not hit `state/config/pipeline-manifest.yaml::block_mode_trigger_paths`; if it does, read `docs/dev-guide/pipeline-manifest-regime.md` at T1).
- ruff + import-linter clean on touched files.
- Leave the tree uncommitted for orchestrator review (no commit, no stash).

## Definition of done

Registry + generic renderer landed; every paused gate (incl. recover/resume-batch) tables its content on stderr with stdout JSON intact; RED-anchored + split + front-door + registry-introspection tests green; ruff/import-linter clean; ready for `bmad-code-review` (dual-gate).
