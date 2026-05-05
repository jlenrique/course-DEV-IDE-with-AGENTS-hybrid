# Codex dev-story prompt — Story 7c.5.G2A (G2A DecisionCard Fresh-Author; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=1; HELD until 7c.4b closes) → Codex T1-T10 → drops `_codex-handoff/7c-5-g2a.ready-for-review.md` → Claude T11 standard → commit + flip done.
**Wave:** 2 — slot 4 (second per-gate fresh-author; G2A plan-unit-ratification).
**Pre-authored:** 2026-05-05 (sibling to 7c.5.G0; pattern-replicates).
**Dispatch state:** **HELD** until 7c.4b closes; AMELIA-P2 freshness re-check at dispatch-time.

---

```
Run bmad-dev-story on Story 7c.5.G2A (Slab 7c Wave 2 slot 4; single-gate; fresh-author; standard T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-5-g2a-decision-card-fresh-author.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8 contract).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-NN.md` (T11 verdict; verifies which class name shipped).
4. `app/models/decision_cards/base.py` OR `_base.py` (T1 reconciles).
5. `app/models/decision_cards/g1.py` AND `g2c.py` (~30 LOC each; fresh-author pattern).
6. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK; AMEND-7d-i — cite by reference; do NOT re-derive).
7. `tests/fixtures/decision_cards/g2c_golden.json` (golden-fixture reference).
8. `_bmad-output/implementation-artifacts/migration-7c-5-g0-decision-card-fresh-author.md` (sibling fresh-author; pattern-replicates).
9. `docs/dev-guide/pydantic-v2-schema-checklist.md` (AC-E).
10. Governance JSON `7c-5-g2a` (single-gate; cross_agent_review_required=false; pts=2; K=1.4; r_tier=R2; t11_tier=standard; lookahead_tier=1; prerequisite_stories=[7c-4b]).

## T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.4b status `done`.
- 7c.4b's shared base class importable.
- 7c.4b's `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` importable.
- Class-conformance baseline = 11 if isolated OR 12 if post-7c.5.G0 (record at T1).
- Existing G1/G2C/G3/G4 construction tests PASS pre-7c.5.G2A (AC-D regression check).

## Files in scope

**New (4 files; STRICT four-file-lockstep co-commit):**
- `app/models/decision_cards/g2a.py` — `G2ACard` subclass; `gate_id: Literal["G2A"]` + `gate_focus: Literal["plan_unit_ratification"]` + 4 G2A-specific fields (plan_unit_id UUID4 + plan_unit_summary str + ratification_evidence list[dict] + prior_unit_ids list[UUID4]).
- `app/models/decision_cards/schema/g2a.v1.schema.json` — JSON Schema; deterministic; sort_keys; FR-7c-51 v1.
- `tests/parity/test_decision_card_g2a_shape.py` — 5+ test cases. MUST `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i).
- `tests/fixtures/decision_cards/g2a_golden.json` — deterministic fixture with ≥1 ratification_evidence item.

**Modified (≤1 file):**
- `app/models/decision_cards/__init__.py` — flat-export of `G2ACard`.

**Do NOT modify:**
- 7c.4b deliverables (read-only).
- Existing G1/G2C/G3/G4 cards or fixtures.
- §02A poll-surface.
- C4/C5/C6 contracts.
- 7c.5.G0 deliverables (if landed first).

## Critical implementation notes

- **Strict four-file lockstep + AMEND-7d-i** (LOCKSTEP_CHECK by reference; identical to 7c.5.G0 pattern).
- **Closed-enum red-rejection** on `gate_id: Literal["G2A"]` + `gate_focus: Literal["plan_unit_ratification"]`.
- **Schema-version emission:** verify `"schema_version": "v1"` (FR-7c-51).
- **Golden fixture determinism:** stable UUID4s + tz-aware `2026-05-05T00:00:00+00:00` + ≥1 evidence item + ordered `prior_unit_ids`.
- **Cross-gate non-regression:** existing G1Card / G2CCard / G3Card / G4Card construction tests MUST continue to pass UNCHANGED (AC-D).
- **K-target 1.4× ≈ 350 LOC ceiling.** Estimate ~250 LOC.
- **Class-conformance:** baseline + 1 (12 if isolated; 13 if post-7c.5.G0).

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g2a_shape.py -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest -k "G1Card or G2CCard or G3Card or G4Card or g1_golden or g2c_golden or g3_golden or g4_golden" -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line   # R2 broad

.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

.venv/Scripts/lint-imports.exe   # Expect 12 KEPT (UNCHANGED)

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g2a-decision-card-fresh-author.md

.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g2a.py tests/parity/test_decision_card_g2a_shape.py
```

Expected:
- Focused: 5+ tests passed.
- Smoke: 200-nodeid baseline UNCHANGED.
- Cross-gate non-regression: existing G1/G2C/G3/G4 tests PASS UNCHANGED.
- R2 broad: 39 inherited checkout-level failures preserved.
- Class-conformance: T1-baseline + 1.
- Lint-imports: 12 KEPT (UNCHANGED).
- Sandbox-AC: PASS.
- Ruff: clean.

## T10 + T11

T10: dropbox at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g2a.ready-for-review.md`. Include: 4-file lockstep verification + class-conformance delta + AMEND-7d-i compliance evidence + cross-gate non-regression confirmation + T1 decisions documented.

T11: Claude standard review. AC-A through E line-by-line; Pydantic-v2 14-idiom checklist; closed-enum red-rejection on G2A discriminator; LOCKSTEP_CHECK citation pattern. Verdict at `_bmad-output/implementation-artifacts/7c-5-g2a-code-review-2026-05-NN.md`.

## Boundary

HALT on: 7c.4b not done; LOCKSTEP_CHECK not importable; cross-gate baseline regression; LOCKSTEP_CHECK re-derivation; class-conformance count anomaly; broad-regression failure count > T1 baseline.

DO NOT touch: 7c.4b deliverables; existing G1/G2C/G3/G4 cards/fixtures; §02A; 7c.5.G0 deliverables.

DO NOT introduce: new third-party deps; mock 7c.4b's base; defensive enum widening; non-deterministic fixtures.
```

---

## Operator dispatch checklist

1. ☐ 7c.4b `done`.
2. ☐ AMELIA-P2 freshness check.
3. ☐ Sandbox-AC PASS on spec.
4. ☐ Governance JSON entry current.
5. ☐ Sprint-status flip: `migration-7c-5-g2a-decision-card-fresh-author: backlog → ready-for-dev`.
6. ☐ Dispatch (can dispatch concurrently with 7c.5.G0 — both have lookahead_tier=1; both single-gate; both consume only 7c.4b read-only).

## Post-Codex-T10 dropbox-watch

1. Codex drops dropbox notice.
2. Claude T11 standard review (~15-20 min).
3. Apply remediation if any.
4. Commit + flip done.
5. At 7c.5.G2A close: 0 stories unblock directly (no Wave-3 follower; G2A is fresh family contract for post-Slab-7c surfaces).
