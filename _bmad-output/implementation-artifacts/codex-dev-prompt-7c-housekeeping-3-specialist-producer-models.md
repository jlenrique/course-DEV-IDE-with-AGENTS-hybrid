# Codex dev-story prompt — 7c-housekeeping-3 (specialist-side producer models + §09 lock wiring; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-housekeeping-3.ready-for-review.md` → Claude T11 standard → commit + flip done.

---

```
Run bmad-dev-story on Story 7c-housekeeping-3.

Spec: `_bmad-output/implementation-artifacts/migration-7c-housekeeping-3-specialist-producer-models.md`.

## Required reading

1. Story spec (4 ACs A-D).
2. `_bmad-output/implementation-artifacts/7c-19-code-review-2026-05-06.md` (origin).
3. `_bmad-output/implementation-artifacts/migration-7c-19-section-09-four-artifact-lock-semantics.md` (parent).
4. `app/marcus/orchestrator/section_09_lock.py` + `tests/marcus/orchestrator/test_section_09_lock.py` (current state — minimal-model fallback).
5. `app/marcus/orchestrator/writers/slide_content.py` (template — `GarySlideContent` producer model shape).
6. `app/specialists/{kira,vera,quinn_r}/state.py` (current LangGraph state shapes).

## T1 hard checkpoints

- 7c.19 done.
- Existing minimal lock model in `section_09_lock.py` (will be retired).
- `GarySlideContent` available at `app/marcus/orchestrator/writers/slide_content.py` (template reference).
- Slab-7b body-activation closes for Kira/Vera/Quinn-R complete (provides shape evidence).

## Files in scope

**New (9 files):**
- `app/specialists/kira/motion_plan.py` (~120 LOC; `KiraMotionPlan`)
- `app/specialists/kira/motion_plan.v1.schema.json`
- `app/specialists/vera/fidelity_verdict.py` (~120 LOC; `VeraFidelityVerdict`)
- `app/specialists/vera/fidelity_verdict.v1.schema.json`
- `app/specialists/quinn_r/qa_verdict.py` (~120 LOC; `QuinnRQAVerdict`)
- `app/specialists/quinn_r/qa_verdict.v1.schema.json`
- `tests/specialists/kira/test_motion_plan_shape.py` (~80 LOC; if `tests/specialists/kira/__init__.py` does not exist, create it)
- `tests/specialists/vera/test_fidelity_verdict_shape.py` (~80 LOC)
- `tests/specialists/quinn_r/test_qa_verdict_shape.py` (~80 LOC)

**Modified (2 files):**
- `app/marcus/orchestrator/section_09_lock.py` — remove minimal model; add 3 imports; rewire validation paths.
- `tests/marcus/orchestrator/test_section_09_lock.py` — extend with strict-model path coverage; re-pin Section09LockResult schema hash if needed.

**Do NOT modify:**
- `app/specialists/{kira,vera,quinn_r}/state.py` (LangGraph state stays unchanged; producer models are NEW SIBLINGS, not replacements)
- `app/marcus/orchestrator/writers/slide_content.py` (template; READ-ONLY)
- `pyproject.toml` (no contract changes)
- `app/audit/chain.py` + `app/models/tripwire_ledger.py` (READ-ONLY)

## Critical implementation notes

- **Producer model shapes (T1-T9 decisions)**: derive each shape from real specialist outputs surfaced in Slab-7b body-activation closes. Capture domain-essential fields:
  - `KiraMotionPlan`: `plan_unit_id`, `motion_clips: list[MotionClipRef]`, `duration_estimate_seconds`, `schema_version`. `MotionClipRef`: clip_id (UUID4) + asset_path + start_time + end_time.
  - `VeraFidelityVerdict`: `plan_unit_id`, `verdict_kind: Literal["pass","fail","conditional"]`, `criteria_evidence: list[CriterionEvidence]`, `schema_version`. `CriterionEvidence`: criterion_id + severity Literal["MUST","SHOULD","MAY"] + status Literal["pass","fail","skip"] + evidence_ref.
  - `QuinnRQAVerdict`: `plan_unit_id`, `rubric_score: float` (`ge=0.0, le=10.0`), `override_evidence: list[OverrideEvent] | None`, `schema_version`. `OverrideEvent`: event_at (tz-aware) + override_kind + rationale.
- **Pydantic-v2 14-idiom checklist** applies to all 3 models: ConfigDict(extra=forbid, validate_assignment=True) + Field-with-description + closed-enum Literal + strip-then-non-empty validators on string fields + UUID4 + tz-aware datetime + sha256-hex pattern where applicable + schema_version=1.
- **§09 lock wiring**: replace local minimal model with 3 structured imports. Preserve `plan_unit_id` cross-artifact consistency check. Preserve GateError-on-failure. Test failure-path: produce a `KiraMotionPlan` with invalid duration → assert `GateError` raised with structured failure context.
- **Section09LockResult schema hash**: may need re-pin if the strict validation changes any field shape. Codex confirms at T10.
- **No new parity_contract decorator** — class-conformance UNCHANGED at 19.
- **No pyproject.toml edit** — Marcus M1-M4 contracts inherited.
- **K-target 1.4× ≈ 980 LOC ceiling.** Estimate ~700 LOC.
- **T11 standard tier**: cross-specialist contract evolution + 3 new schema-shape models + lock-wiring change.

## Verification battery (T6)

```bash
.venv/Scripts/python.exe -m pytest tests/specialists/kira/ tests/specialists/vera/ tests/specialists/quinn_r/ tests/marcus/orchestrator/test_section_09_lock.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/marcus/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/audit/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-housekeeping-3-specialist-producer-models.md
.venv/Scripts/python.exe -m ruff check app/specialists/kira/motion_plan.py app/specialists/vera/fidelity_verdict.py app/specialists/quinn_r/qa_verdict.py app/marcus/orchestrator/section_09_lock.py tests/specialists/ tests/marcus/orchestrator/test_section_09_lock.py
```

## T10

T10: dropbox at `_codex-handoff/7c-housekeeping-3.ready-for-review.md`. Include: 3 producer-model schema hashes pinned + section_09_lock minimal-model retirement evidence + AC-2 happy/failure path test results + per-specialist shape-derivation rationale (from Slab-7b trial-2 evidence) + Section09LockResult schema-hash re-pin (if needed).

## Boundary

HALT on: 7c.19 not done; producer-model shapes drift from real specialist Trial-2 evidence (T1 should ground each model in actual outputs); §09 lock breaks any existing happy/failure path; class-conformance count change.

DO NOT introduce: new HIL surfaces or parity_contract decorators; new pyproject.toml contracts; changes to specialist LangGraph state files (`state.py`); changes to GarySlideContent (template only).
```

---

## Operator dispatch checklist

1. ☐ AMELIA-P2 PASS.
2. ☐ Sandbox-AC PASS.
3. ☐ Sprint-status: ready-for-dev.
4. ☐ Dispatch (solo; standard-tier review depth at T11).
