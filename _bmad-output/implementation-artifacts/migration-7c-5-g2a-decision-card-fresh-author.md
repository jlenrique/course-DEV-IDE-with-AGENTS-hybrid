# Migration Story 7c.5.G2A: G2A DecisionCard Fresh-Author (Plan-Unit-Ratification)

**Status:** review *(Codex worker + main-thread integration complete 2026-05-05; ready-for-review record posted at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g2a.ready-for-review.md`.)*
**Sprint key:** `migration-7c-5-g2a-decision-card-fresh-author`
**Epic:** Slab 7c â€” Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 2
**K-target:** 1.4Ã— (modest stretch; pattern-replication of 7c.5.G0 + same 4-file structure)
**Estimated LOC:** ~250 (4 new files: ~50 model + ~50 schema + ~110 shape-pin + ~40 golden)
**Gate-mode:** single-gate
**Cross-agent review:** false (per governance JSON)
**R-tier:** R2
**T11-tier:** standard
**Lookahead-tier:** 1 (author-ahead-aggressive; substrate LOCKED via 7c.4b D1-D8 contract pre-flight)
**files_touched:** 4 new + â‰¤1 modified (`__init__.py` flat-export if pattern matches)

---

## Story

As the dev-agent,
I want the G2A plan-unit-ratification DecisionCard authored as a four-file lockstep co-commit (model + schema + shape-pin + golden),
So that Marcus's Wave-3 Â§03 / Â§04A G2A-aliased poll-surfaces (downstream stories 7c.6 + 7c.7) have a per-gate DecisionCard model conforming to the 7c.4b shared base + LOCKSTEP_CHECK enforcement + class-conformance recognition.

---

## Predecessor / Dependency Context

- **7c.4b** (currently in dev as of 2026-05-05): provides shared `DecisionCardBase` (per D2; class name reconciled at 7c.4b T1) + `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` (per D4) + class-conformance validator extension recognizing 18 runtime IDs (per D6).
- **7c.5.G0** (sibling fresh-author; pattern reference): authored 2026-05-05; held alongside 7c.5.G2A on 7c-4b dependency.
- **Consumers:** Wave-3 stories `7c.6` (Â§04A G1A; predecessor 7c.5.G1) and `7c.7` (Â§04.5 G1.5; predecessor 7c.5.G1) â€” wait: G2A is a fresh-author per the alias map but its consumers are not directly in 7c.6/7c.7. Per epic Â§Stories 7c.6..7c.15, no Wave-3 story directly aliases to G2A â€” it is a fresh family contract for future post-Slab-7c plan-unit-ratification surfaces. **G2A is fresh-author standalone** (no Wave-3 follower in this slab).
- **Existing substrate:** `app/models/decision_cards/{g1,g2c,g3,g4}.py` shipped at Slab 7a; pattern-replicate with same import pattern.

---

## Acceptance Criteria

### AC-7c.5.G2A-A â€” Four-file lockstep co-commit (FR-7c-6 + FR-7c-7 + FR-7c-49)

**Given** 7c.4b's `DecisionCardBase` + `LOCKSTEP_CHECK` are LANDED + class-conformance validator recognizes G2A
**When** the dev-agent authors the four files atomically:
1. `app/models/decision_cards/g2a.py` â€” `G2ACard` Pydantic-v2 subclass; `gate_id: Literal["G2A"]`; `gate_focus: Literal["plan_unit_ratification"]`; G2A-specific fields (`plan_unit_id: UUID4` + `plan_unit_summary: str` non-empty + `ratification_evidence: list[dict[str, Any]]` non-empty + `prior_unit_ids: list[UUID4]` ordering-context).
2. `app/models/decision_cards/schema/g2a.v1.schema.json` â€” JSON Schema regenerated (deterministic; sort_keys; FR-7c-51 `schema_version: "v1"`).
3. `tests/parity/test_decision_card_g2a_shape.py` â€” shape-pin asserting field-presence (10 fields) + closed-enum red-rejection on `gate_id` + `gate_focus` + JSON-Schema byte-match + golden round-trip.
4. `tests/fixtures/decision_cards/g2a_golden.json` â€” deterministic golden fixture.

**Then** all four files are co-committed in one diff; the model imports from 7c.4b's shared base; the shape-pin imports `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (AMEND-7d-i).

### AC-7c.5.G2A-B â€” TW-7c-3 firing on out-of-sync (FR-7c-7 + AMEND-7d-i)

Identical to 7c.5.G0-B template: any of the four G2A files missing or out-of-sync fires TW-7c-3 critical; LOCKSTEP_CHECK cited by reference; no re-derivation.

### AC-7c.5.G2A-C â€” Class-conformance recognition (FR-7c-8 + 7c.4b D6)

`scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` confirms `tests/parity/test_decision_card_g2a_shape.py` is structurally well-formed AND class-conformance count = 12 (was 11; +1) when run in isolation OR 13 (was 12; +1) when run after 7c.5.G0 has landed. **T1 records the actual baseline at story-open.**

### AC-7c.5.G2A-D â€” Cross-gate non-regression on existing G1/G2C/G3/G4 shape-pins

**Given** existing per-gate cards G1/G2C/G3/G4 already shipped (Slab 7a) â€” but no shape-pins exist YET (7c.5.G0 + 7c.5.G2A author the first per-gate shape-pins for fresh-author gates; G1/G2C/G3/G4 shape-pins land at 7c.5.G1/G2C/G3/G4 extend-and-audit stories)
**When** this story lands
**Then** existing tests against G1Card / G2CCard / G3Card / G4Card construction continue to pass UNCHANGED (no model-side regression). **Verification:** focused tests targeting `app/models/decision_cards/g1.py` etc. construction (search via `grep -r "G1Card\|G2CCard\|G3Card\|G4Card" tests/`) PASS at T9.

### AC-7c.5.G2A-E â€” Pydantic-v2 14-idiom conformance (per `docs/dev-guide/pydantic-v2-schema-checklist.md`)

Identical to 7c.5.G0-E: `validate_assignment` + `extra="forbid"` + closed Literals on `gate_id` + `gate_focus` + tz-aware datetime via inherited helper + UUID4 on `plan_unit_id` + non-empty enforcement on `plan_unit_summary` + `ratification_evidence` + Field descriptions.

---

## Tasks / Subtasks

- [x] **T1 â€” Readiness checks**
  - [x] T1.1 Confirm 7c.4b `done`; shared base class importable; `LOCKSTEP_CHECK` importable.
  - [x] T1.2 Record class-conformance baseline (11 if 7c.5.G0 not yet landed; 12 if 7c.5.G0 landed first).
  - [x] T1.3 Read `app/models/decision_cards/g1.py` AND `g2c.py` for fresh-author pattern reference.
  - [x] T1.4 Read `tests/fixtures/decision_cards/g2c_golden.json` for golden-fixture shape reference.
  - [x] T1.5 Refresh broad-regression baseline.
  - [x] T1.6 Run sandbox-AC validator on this spec; expect PASS.
  - [x] T1.7 Document existing G1/G2C/G3/G4 model construction test inventory (AC-D baseline).

- [x] **T2 â€” Author G2ACard model (AC: 7c.5.G2A-A + 7c.5.G2A-E)**
  - [x] T2.1 Author `app/models/decision_cards/g2a.py` with `G2ACard` subclass; `gate_id: Literal["G2A"]` + `gate_focus: Literal["plan_unit_ratification"]` + 4 G2A-specific fields.
  - [x] T2.2 Field validators: non-empty `plan_unit_summary` + `ratification_evidence` (â‰¥1 item) + UUID4 enforcement on `plan_unit_id` + `prior_unit_ids`.
  - [x] T2.3 Update `app/models/decision_cards/__init__.py` exports if flat-import pattern.

- [x] **T3 â€” Generate JSON schema (AC: 7c.5.G2A-A)**
  - [x] T3.1 Generate `schema/g2a.v1.schema.json` via deterministic `model_json_schema()` emission.
  - [x] T3.2 Verify FR-7c-51 `schema_version: "v1"` field present.

- [x] **T4 â€” Author golden fixture (AC: 7c.5.G2A-A)**
  - [x] T4.1 Author `g2a_golden.json` with stable UUID4s + tz-aware `created_at` + `meta.cache_state: "healthy"` + â‰¥1 item in `ratification_evidence`.
  - [x] T4.2 Verify deterministic round-trip.

- [x] **T5 â€” Author shape-pin test (AC: 7c.5.G2A-A + 7c.5.G2A-B + 7c.5.G2A-C + 7c.5.G2A-E)**
  - [x] T5.1 Author `tests/parity/test_decision_card_g2a_shape.py` with 5+ test cases (field-presence + 2 closed-enum red-rejections + JSON-Schema byte-match + golden round-trip).
  - [x] T5.2 Import `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (AMEND-7d-i compliance).

- [x] **T6 â€” Verification battery (R-tier R2)**
  - [x] T6.1 Focused: `pytest tests/parity/test_decision_card_g2a_shape.py -p no:randomly -q --tb=short` PASS.
  - [x] T6.2 Smoke: 200-nodeid baseline UNCHANGED.
  - [x] T6.3 Cross-gate non-regression: existing G1/G2C/G3/G4 construction tests PASS UNCHANGED.
  - [x] T6.4 R2 broad regression: failure count â‰¤ T1 baseline (39 inherited).
  - [x] T6.5 Class-conformance: T1-baseline + 1 (12 if isolated; 13 if post-7c.5.G0).
  - [x] T6.6 Lint-imports: 12 KEPT (UNCHANGED).
  - [x] T6.7 Sandbox-AC: PASS.
  - [x] T6.8 Ruff: clean.

- [x] **T10 â€” Codex self-review**
  - [x] T10.1 Codex authors `_codex-handoff/7c-5-g2a.ready-for-review.md` with: 4-file lockstep verification + class-conformance delta + AMEND-7d-i compliance evidence + AC-D existing-card non-regression confirmation.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-NN.md` (T11 verdict).
4. `app/models/decision_cards/base.py` OR `_base.py` (whichever 7c.4b shipped).
5. `app/models/decision_cards/g1.py` AND `g2c.py` (fresh-author pattern).
6. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK).
7. `tests/fixtures/decision_cards/g2c_golden.json` (golden-fixture reference).
8. `_bmad-output/implementation-artifacts/migration-7c-5-g0-decision-card-fresh-author.md` (sibling fresh-author pattern).
9. `docs/dev-guide/pydantic-v2-schema-checklist.md`.
10. `docs/dev-guide/dev-agent-anti-patterns.md`.
11. `docs/dev-guide/story-cycle-efficiency.md`.

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. Sandbox-AC: PASS (verified at T0).

---

## Dispatch Hold

**HELD until 7c.4b closes.** AMELIA-P2 freshness re-check at dispatch-time.

---

## Dev Agent Record

### Completion Notes

- Implemented the G2A four-file lockstep set: model, schema, shape-pin, and golden fixture.
- Consumed `_base.py:DecisionCardBase` per 7c.4b D2 reconciliation and added G2A plan-unit-ratification fields explicitly.
- Added `G2ACard` to the flat DecisionCard export and discriminated union.
- Removed a direct `all_four_present` shape-pin assertion so AMEND-7d-i remains enforced by the single-source structural scan.

### Verification

- G0 + G2A + TW-7c-3 structural pins: `23 passed`
- DecisionCard model regression: `36 passed`
- Gate/DecisionCard integration slice: `27 passed`
- Smoke: `181 passed, 18 skipped`
- Class-conformance: `PASS: 13 parity contract file(s) conform (11 activation + 2 decision-card shape-pin)`
- Import-linter: `12 kept, 0 broken`
- Sandbox-AC: `PASS`
- Ruff: `All checks passed`
- Broad regression: `44 failed, 4132 passed, 27 skipped, 2 xfailed`; failures are inherited checkout-level surfaces.

### File List

- `app/models/decision_cards/g2a.py`
- `app/models/decision_cards/schema/g2a.v1.schema.json`
- `tests/parity/test_decision_card_g2a_shape.py`
- `tests/fixtures/decision_cards/g2a_golden.json`
- `app/models/decision_cards/__init__.py`
- `scripts/utilities/validate_parity_test_class_conformance.py`
- `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g2a.ready-for-review.md`

### Change Log

- 2026-05-05: Authored G2A DecisionCard four-file lockstep set and posted ready-for-review record.
