# Story G0-S1 — LO Canonical Schema + Transition Guard + Adapter

**Epic:** G0 Source-Content Enrichment (v1) — `_bmad-output/planning-artifacts/epics-g0-enrichment.md`
**Authority:** `_bmad-output/planning-artifacts/lo-schema-ratification-2026-06-26.md` (ratified schema §1-5; adequacy-advisory §3.1).
**Class:** S · **Type:** schema-shape · **Gate mode:** single-gate · **Status:** DONE (T11-closed 2026-06-26)

> **T11 outcome (3-layer bmad-code-review):** Acceptance Auditor CLEAN (all ACs PASS, no MUST/SHOULD-FIX). Blind + Edge Case Hunters raised 0 MUST-FIX, 3 SHOULD-FIX + NITs — ALL remediated RED-first: (1) `objective_id` `.match`→`fullmatch` (trailing-`\n` key-integrity); (2) `SourceRef` non-empty field validators (hollow refined+ provenance floor); (3) `source_refs`→`tuple` (closes in-place-mutation bypass) + honest docstrings re `model_copy`; (4) `advance_lo` docstring precision; (5) structural enum-array test (was tautological substring); (6) tejal swap test imports the real hoisted `TEJAL_OBJECTIVE_SEEDS` (was a re-declared copy); (7) graceful bloom case-coercion + fail-loud on non-Bloom. Final: 275 passed/1 skipped, ruff clean, lint-imports clean-of-S1, workbook regression unchanged. Deferred follow-ons filed: hoist `_validate_open_id` to shared helper; pre-existing `collateral_spec` `\n` gap; pre-existing 07W C3 import break; A8 re-confirm → S3 ratify-gate.
**Closes:** A7 (unify the LO schema). **Sequence:** S1 → S2 → S3 (S1 first).
**Required dev readings (T1, before any code):** `docs/dev-guide/pydantic-v2-schema-checklist.md` (all 14 idioms), `docs/dev-guide/scaffolds/schema-story/` (use the scaffold), `docs/dev-guide/dev-agent-anti-patterns.md`, the ratification doc §1-5.

## Goal
One canonical, provenance-anchored, lifecycle-aware `LearningObjective` entity that REPLACES the 3 in-code LO representations (Irene Pass-1 string; `LearningObjectiveBrief`; `WorkbookSection.learning_objective_id` content) and keys the `learning_objective_map` DB table by `objective_id`. **S1 is ADDITIVE + adapter-bridged:** the entity + guard + adapter land; existing consumers keep working through the adapter (no behavior change). Native producer/consumer rewiring is distributed into S2/S3 where those seams are already touched (ratification §5).

## Existing representations (DRY targets — map, don't fork)
1. Irene Pass-1 bare string `learning_objective` — `app/specialists/irene_pass1/_act.py:171`.
2. `LearningObjectiveBrief` `@dataclass(frozen=True)` {objective_id, bloom_level, statement} — `app/marcus/lesson_plan/workbook_producer.py:200`; consumed by `assert_learning_objective_bindings()`.
3. `WorkbookSection.learning_objective_id` open-id ref — `app/marcus/lesson_plan/collateral_spec.py:273` (reuse its `_validate_open_id` + `OPEN_ID_REGEX_PATTERN` — do NOT fork the regex).
4. `learning_objective_map` DB table (objective_id + validation_status) — keys to `objective_id`; role unchanged (alignment tracking).

## Canonical module
Place the entity at `app/marcus/lesson_plan/learning_objective.py` (co-located with `collateral_spec.py`, importable by the workbook producer). **Verify import-linter contracts first** — if `app/specialists/irene_pass1` cannot import from `app/marcus/lesson_plan` under the contracts, place the entity in the lowest shared importable module and record the choice in the story Dev Notes. Reuse `_validate_open_id`/`OPEN_ID_REGEX_PATTERN` from `collateral_spec` (import or shared-helper extraction; no regex fork).

## Acceptance Criteria

### AC-S1-1 — Canonical entity + value types (pydantic-v2 per checklist)
Implement exactly the ratified §1 shapes: `LearningObjective`, `SourceRef`, `SourceAdequacy`, and the closed enums `BloomLevel`, `LOStatus`, `Confidence`, `AdequacyVerdict`, `AdequacyFollowup`. Every model carries `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. `objective_id` is validated through the reused open-id validator. `statement`/`rationale` are free-text verbatim (NO `min_length`, no normalization — checklist §6). `origin` defaults `"g0"`; `recommendation` defaults `"keep"`.

### AC-S1-2 — Status-conditional invariant table via `model_validator(mode="after")`
Enforce the ratification §1 table as a single `@model_validator(mode="after")` (checklist §13 state-machine guard): `provisional` allows `source_refs` ≥0, `adequacy=None`, `bloom_level=None`; `refined`+ requires `source_refs` ≥1 AND `adequacy` non-null; `ratified` additionally requires `bloom_level` non-null. RED-first tests for every cell (valid + each violation). **`adequacy.verdict` value (thin/gap) is NEVER part of any invariant — only its PRESENCE is** (§3.1 advisory). `validate_assignment=True` so mutation re-checks the table.

### AC-S1-3 — `advance_lo()` transition guard (authority lives here, NOT in the model)
Module function `advance_lo(lo, target, *, actor) -> LearningObjective` with a closed `(from, to, actor)` edge map: `(mint→provisional, g0)`, `(provisional→refined, irene)`, `(refined→ratified, operator)`. Any other edge (skip, backward, wrong-actor — esp. `irene→ratified`) raises `IllegalTransition`. Idempotent replay of an already-applied edge is a no-op-or-hard-error (never a silent re-run — replay determinism). `ratified` is a forbidden output for `actor="irene"`. RED-first tests: every legal edge passes; the illegal matrix (≥8 cases incl. `irene→ratified`) raises.

### AC-S1-4 — Emitted JSON Schema + shape-pin / parity / no-leak tests
Emit JSON Schema; closed enums get all 3 red-rejection surfaces (Pydantic validator + JSON Schema `enum` array + `TypeAdapter` round-trip — checklist §4). Per-family shape-pin test (`test_learning_objective_shape_stable.py` — checklist §8). Bidirectional required↔optional JSON-Schema parity (§9). `additionalProperties:false` propagation (§14). No-leak grep test (§11): forbidden `intake`/`orchestrator` tokens absent from descriptions + dumps.

### AC-S1-5 — Adapter FUNCTIONS over the 4 representations (bridge, not persisted parallel entity)
Pure functions (no persisted shim class): `from_irene_statement(str, *, objective_id, source_refs=...) -> LearningObjective`; `from_workbook_brief(LearningObjectiveBrief) -> LearningObjective` and `to_workbook_brief(LearningObjective) -> LearningObjectiveBrief` (back-compat bridge so `assert_learning_objective_bindings` + `produce_tejal_workbook.py` keep working unchanged in S1); a binding helper resolving `WorkbookSection.learning_objective_id` ↔ `LearningObjective.objective_id`. Round-trip tests prove `to_workbook_brief(from_workbook_brief(x)) == x` on the subset fields. **The hard-coded Irene-string→brief mapping in `produce_tejal_workbook.py:500-520` is the first adapter target — replace its inline logic with a call to `from_irene_statement`, behavior-identical.**

### AC-S1-6 — DRY + import discipline
Reuse the open-id regex/validator; no duplicate regex. Respect import-linter (run `lint-imports`); if a new contract row is needed, add it minimally and note it. No new third-party deps.

### AC-S1-7 — Regression guard (no behavior change)
S1 is additive. `LearningObjectiveBrief` is NOT deleted in S1 (its deletion is S3 when the workbook is rewired). Existing consumers unchanged in observable behavior. Full relevant suites + `ruff` + `lint-imports` green. The workbook producer's existing tests (`tests/marcus/lesson_plan/test_workbook_s0_s7.py`) pass unchanged. `produce_tejal_workbook.py` produces a byte-identical workbook spec/brief set before vs after the AC-S1-5 inline-mapping swap (prove with a focused before/after assertion or existing producer test).

### AC-S1-8 — No expensive assets / offline
S1 has NO live LLM or external-API surface. No Gamma/video/audio. "Live-segment proof" for S1 = the full green test suite + a tiny demonstration script (or doctest) constructing a `provisional` LO, `advance_lo`-ing it `→refined→ratified` through the legal actors, and rejecting `irene→ratified`.

## Definition of Done
All ACs green; pydantic-v2 checklist idioms applied; JSON Schema + shape-pin/parity/no-leak/enum-surface/transition tests pass; adapter round-trips; full suite + ruff + lint-imports green; no behavior change to existing consumers; T11 `bmad-code-review` clean (or findings remediated); mini party-close.
