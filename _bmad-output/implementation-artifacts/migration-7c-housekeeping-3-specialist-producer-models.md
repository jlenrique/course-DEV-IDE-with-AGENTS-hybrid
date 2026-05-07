# Migration Story 7c-housekeeping-3: Specialist-Side Producer Models for Kira / Vera / Quinn-R + §09 Lock Wiring Hardening

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=1; predecessor 7c.19 closed with the spec-anticipated minimal-lock-model fallback honored. This story replaces the fallback with structured specialist-side Pydantic-v2 producer models.)*
**Sprint key:** `migration-7c-housekeeping-3-specialist-producer-models`
**Source:** Story 7c.19 review SHOULD-FIX-DEFERRED (`_bmad-output/implementation-artifacts/7c-19-code-review-2026-05-06.md`); deferred-inventory entry `seven-c-nineteen-specialist-producer-models-future-hardening`.
**Pts:** 3
**K-target:** 1.4×
**Estimated LOC:** ~700 (3 producer Pydantic-v2 models ~120 each = 360 + 3 JSON schema regen ~50 each = 150 + section_09_lock wiring update ~50 + 3 shape-pin tests ~80 each = 240; offset by ~50 LOC removed from local minimal lock model)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** standard
**Lookahead-tier:** 1
**files_touched:** ~9 new + ~2 modified

---

## Story

As the dev-agent,
I want structured Pydantic-v2 producer models for Kira motion-plan + Vera fidelity-verdict + Quinn-R QA-verdict landing alongside `app/specialists/{kira,vera,quinn_r}/state.py`, AND `app/marcus/orchestrator/section_09_lock.py` rewired to validate via these structured models instead of the local minimal lock model fallback,
So that §09 lock semantics enforce richer structural invariants on producer outputs (vs the current `plan_unit_id`-only minimal check) — closing the 7c.19 SHOULD-FIX-DEFERRED follow-on filed in `7c-19-code-review-2026-05-06.md`.

This is **standard-tier T11** because the work touches:
- 3 new Pydantic-v2 schema-shape models (FR-7c-51 schema_version + JSON Schema regen + shape-pin tests)
- Cross-specialist contract evolution (Kira's motion-plan / Vera's fidelity-verdict / Quinn-R's QA-verdict shapes are now first-class Pydantic-v2 contracts)
- Marcus-side lock wiring change (replaces minimal fallback with strict validation)

---

## Predecessor / Dependency Context

- **7c.19** (CLOSED): Marcus-side `enforce_section_09_lock` shipped with local minimal lock model fallback for Kira/Vera/Quinn-R artifacts (specialist-side producer Pydantic-v2 models did not exist). GarySlideContent (7c.17a) is consumed structurally.
- **`app/specialists/{kira,vera,quinn_r}/state.py`** (existing): each defines `<Specialist>Envelope` + `<Specialist>Return` LangGraph state shapes; current return fields are loose-typed (`vera_finding: dict[str, Any]`, `kira_motion_plan: dict[str, Any]`-ish, `quinn_r_qa_verdict: dict[str, Any]`-ish). Story tightens these.
- **`app/marcus/orchestrator/section_09_lock.py`** (existing; from 7c.19): contains local minimal lock model. This story replaces with structured-model imports.
- **Trial-2 evidence base**: per `7b.7` (Kira) + `7b.3` (Vera) + `7b.2` (Quinn-R) closes, real specialist outputs landed during Slab-7b body activation. The shape of those outputs informs what the producer models must capture.

---

## Acceptance Criteria

### AC-1 — Author 3 specialist-side producer models

**Given** the LangGraph state files at `app/specialists/{kira,vera,quinn_r}/state.py`
**When** the dev-agent authors NEW Pydantic-v2 producer models alongside (NOT in state.py — keep state shape distinct from artifact shape):
- `app/specialists/kira/motion_plan.py` (~120 LOC) — defines `KiraMotionPlan` Pydantic-v2 model
- `app/specialists/vera/fidelity_verdict.py` (~120 LOC) — defines `VeraFidelityVerdict` Pydantic-v2 model
- `app/specialists/quinn_r/qa_verdict.py` (~120 LOC) — defines `QuinnRQAVerdict` Pydantic-v2 model

**Then** each model:
1. Declares `model_config = ConfigDict(extra="forbid", validate_assignment=True)`.
2. Carries `plan_unit_id: str` (`min_length=1` + strip-then-non-empty validator) for §09 lock cross-artifact consistency check.
3. Declares producer-specific structured fields (T1-T9 decision: derive shape from real specialist outputs in Slab-7b trial-2 evidence + per-specialist domain semantics — Kira motion-plan = motion clip refs + duration estimates; Vera fidelity = pass/fail + criteria evidence; Quinn-R QA = rubric scores + override evidence).
4. Has `schema_version: int = 1` per FR-7c-51.
5. Closed-enum Literal types on enumerated fields where applicable.
6. JSON Schema regenerated via Path.write_text per A18 + LF-only + NO BOM.

### AC-2 — Update `enforce_section_09_lock` to consume structured models

**When** the dev-agent edits `app/marcus/orchestrator/section_09_lock.py`:
**Then**:
1. Imports added: `from app.specialists.kira.motion_plan import KiraMotionPlan`, `from app.specialists.vera.fidelity_verdict import VeraFidelityVerdict`, `from app.specialists.quinn_r.qa_verdict import QuinnRQAVerdict`.
2. Local minimal lock model REMOVED (Codex's 7c.19 fallback retired).
3. Validation paths use the three structured models for Kira/Vera/Quinn-R artifacts (parallel to existing `GarySlideContent` validation).
4. The `plan_unit_id` consistency check across all 4 artifacts is preserved.
5. GateError-on-validation-error semantics preserved.
6. Existing tests continue to PASS unchanged (lock semantics unchanged; just stricter parsing).

### AC-3 — JSON schemas + shape-pin tests for 3 producer models

**Then**:
1. JSON schemas land at `app/specialists/{kira,vera,quinn_r}/{motion_plan,fidelity_verdict,qa_verdict}.v1.schema.json`.
2. Shape-pin tests under `tests/specialists/{kira,vera,quinn_r}/test_{motion_plan,fidelity_verdict,qa_verdict}_shape.py` (~80 LOC each):
   - Schema hash STABLE pin.
   - Closed-enum red-rejection.
   - strip-then-non-empty red-rejection.
   - Round-trip via `model_validate` + `model_dump`.

### AC-4 — Update §09 lock test to verify strict-model path

**Then** existing `tests/marcus/orchestrator/test_section_09_lock.py` is extended:
1. Happy path: assert all 4 artifacts now validate via their producer models (not minimal fallback).
2. Schema-hash STABLE pin for `Section09LockResult` may need re-pin (since artifact_kind enum unchanged but strict validation changes failure paths).
3. New test: assert validation_error from a producer model (e.g., `KiraMotionPlan` with invalid duration) raises `GateError` with structured failure context.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Read `app/specialists/{kira,vera,quinn_r}/state.py` for current `<Specialist>Return` shapes.
  - [ ] T1.2 Read `app/marcus/orchestrator/section_09_lock.py` for current minimal lock model + lock function structure.
  - [ ] T1.3 Read `app/marcus/orchestrator/writers/slide_content.py` (`GarySlideContent`) for the producer-model template.
  - [ ] T1.4 Inventory Slab-7b trial-2 evidence per specialist for shape derivation.
  - [ ] T1.5 Refresh broad-regression baseline.

- [ ] **T2 — Author 3 producer models (AC-1)**
  - [ ] T2.1 `app/specialists/kira/motion_plan.py` — `KiraMotionPlan` Pydantic-v2.
  - [ ] T2.2 `app/specialists/vera/fidelity_verdict.py` — `VeraFidelityVerdict` Pydantic-v2.
  - [ ] T2.3 `app/specialists/quinn_r/qa_verdict.py` — `QuinnRQAVerdict` Pydantic-v2.

- [ ] **T3 — Generate 3 JSON schemas (AC-1)**
  - [ ] T3.1 Path.write_text per A18 for each.

- [ ] **T4 — Author 3 shape-pin tests (AC-3)**
  - [ ] T4.1 `tests/specialists/kira/test_motion_plan_shape.py`.
  - [ ] T4.2 `tests/specialists/vera/test_fidelity_verdict_shape.py`.
  - [ ] T4.3 `tests/specialists/quinn_r/test_qa_verdict_shape.py`.

- [ ] **T5 — Update section_09_lock.py + extend test (AC-2 + AC-4)**
  - [ ] T5.1 Replace local minimal lock model with structured-model imports in `app/marcus/orchestrator/section_09_lock.py`.
  - [ ] T5.2 Update `tests/marcus/orchestrator/test_section_09_lock.py` for strict-model path coverage.

- [ ] **T6 — Verification battery (R-tier R2; T11-tier standard)**
  - [ ] T6.1 Focused: `pytest tests/specialists/kira/ tests/specialists/vera/ tests/specialists/quinn_r/ tests/marcus/orchestrator/test_section_09_lock.py -p no:randomly -q --tb=short` PASS.
  - [ ] T6.2 Smoke 181/18 UNCHANGED.
  - [ ] T6.3 R2 broad: failure count delta ≤ 0.
  - [ ] T6.4 Class-conformance UNCHANGED at 19 (these are NOT new HIL surfaces; no parity_contract added).
  - [ ] T6.5 Lint-imports 12 KEPT UNCHANGED (no pyproject.toml edit).
  - [ ] T6.6 Sandbox-AC PASS.
  - [ ] T6.7 Ruff clean.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-housekeeping-3.ready-for-review.md` with: 3 producer-model schema hashes + section_09_lock minimal-model retirement evidence + AC-2 happy/failure path test results + Trial-2 evidence-derivation rationale per specialist.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/7c-19-code-review-2026-05-06.md` (origin SHOULD-FIX-DEFERRED).
3. `_bmad-output/implementation-artifacts/migration-7c-19-section-09-four-artifact-lock-semantics.md` (parent story; minimal-fallback context).
4. `app/marcus/orchestrator/section_09_lock.py` + `tests/marcus/orchestrator/test_section_09_lock.py` (current state; lock function + minimal model).
5. `app/marcus/orchestrator/writers/slide_content.py` (`GarySlideContent` producer-model template).
6. `app/specialists/kira/state.py` + `vera/state.py` + `quinn_r/state.py` (current LangGraph state).
7. `_bmad-output/planning-artifacts/slab-7b-retrospective.md` for Slab-7b body-activation evidence on real specialist outputs.

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

## Dispatch state

**DISPATCH-READY** post-AMELIA-P2 PASS. Solo dispatch (cross-specialist contract evolution; standard-tier review depth required).
