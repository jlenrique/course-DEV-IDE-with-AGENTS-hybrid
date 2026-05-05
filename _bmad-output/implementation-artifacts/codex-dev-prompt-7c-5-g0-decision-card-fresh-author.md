# Codex dev-story prompt — Story 7c.5.G0 (G0 DecisionCard Fresh-Author; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=1 author-ahead per AMEND-V5; HELD until 7c.4b closes) → Codex T1-T10 → drops `_codex-handoff/7c-5-g0.ready-for-review.md` → Claude T11 standard → commit + flip done.
**Wave:** 2 — slot 3 (first per-gate fresh-author; G0 trial-open / corpus-confirm).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **HELD** until 7c.4b closes; AMELIA-P2 freshness re-check at dispatch-time.

---

```
Run bmad-dev-story on Story 7c.5.G0 (Slab 7c Wave 2 slot 3; single-gate; fresh-author; standard T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-5-g0-decision-card-fresh-author.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8 contract — D2 DecisionCardBase + D4 LOCKSTEP_CHECK + D6 class-conformance).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-NN.md` (T11 verdict; verifies which class name shipped — `DecisionCardBase` per spec OR `DecisionCard` per existing substrate).
4. `app/models/decision_cards/base.py` AND `_base.py` (T1 reconciles — read whichever 7c.4b shipped).
5. `app/models/decision_cards/g1.py` (~30 LOC; fresh-author pattern reference).
6. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK + FOUR_FILE_GLOBS; AMEND-7d-i — cite by reference; do NOT re-derive).
7. `app/gates/section_02a/poll_surface.py` (consumer; AC-D regression baseline).
8. `tests/schemas/operator_verdict/test_section_02a_shape.py` (AC-D pre-existing PASS).
9. `tests/fixtures/decision_cards/g1_golden.json` (golden-fixture shape reference).
10. `docs/dev-guide/pydantic-v2-schema-checklist.md` (AC-E 14-idiom conformance).
11. Governance JSON `7c-5-g0` (single-gate; cross_agent_review_required=false; pts=2; K=1.4; r_tier=R2; t11_tier=standard; lookahead_tier=1; prerequisite_stories=[7c-4b]).

## T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.4b status `done` (sprint-status.yaml).
- 7c.4b's shared base class is importable (verify class name shipped: `DecisionCardBase` per spec OR `DecisionCard` per existing substrate; document the actual name in T10 dropbox).
- 7c.4b's `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` importable from `app.parity.contracts.tw_7c_3_firing`.
- 7c.4b's class-conformance validator extension recognizes G0 (run validator; baseline = 11 contracts).
- §02A regression baseline: `tests/schemas/operator_verdict/test_section_02a_shape.py` PASS pre-7c.5.G0 (AC-D verifies UNCHANGED post-7c.5.G0).
- Broad-regression baseline: 39 inherited checkout-level failures (preserve at T9; delta=0).

## Files in scope

**New (4 files; STRICT four-file-lockstep co-commit):**
- `app/models/decision_cards/g0.py` — `G0Card` Pydantic-v2 subclass; `gate_id: Literal["G0"]` + `gate_focus: Literal["trial_open"]` + 3 G0-specific fields (corpus_paths_confirmed + directive_run_id + corpus_confirmation_summary).
- `app/models/decision_cards/schema/g0.v1.schema.json` — JSON Schema regenerated from `G0Card.model_json_schema()` (deterministic; sort_keys; FR-7c-51 schema_version v1).
- `tests/parity/test_decision_card_g0_shape.py` — 5 test cases (field-presence + closed-enum red-rejection on gate_id + gate_focus + JSON-Schema byte-match + golden round-trip). MUST `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i; cite by reference).
- `tests/fixtures/decision_cards/g0_golden.json` — deterministic fixture with all required fields.

**Modified (≤1 file):**
- `app/models/decision_cards/__init__.py` — flat-export of `G0Card` if pattern matches G1/G2C/G3/G4 (mirror existing).

**Do NOT modify:**
- 7c.4b's `_base.py` / `base.py` (or whatever shipped) — this story consumes only.
- 7c.4b's `tw_7c_3_firing.py` — this story imports only.
- Existing G1/G2C/G3/G4 cards or schemas or fixtures.
- §02A poll-surface or operator-verdict model from 7c.3b.
- C4/C5/C6 import-linter contracts.

## Critical implementation notes

- **Strict four-file lockstep:** all 4 files MUST be co-committed in one diff. If any one is missing or out-of-sync at T9, TW-7c-3 fires (critical) and HALT.
- **AMEND-7d-i compliance:** the shape-pin imports `LOCKSTEP_CHECK` (and optionally `FOUR_FILE_GLOBS`) from `app.parity.contracts.tw_7c_3_firing`. Do NOT define a local `LOCKSTEP_CHECK` constant or re-derive the firing condition. 7c.4b's `tests/structural/test_tw_7c_3_firing_spec_single_source.py` AST-scans for any re-derivation and would fail.
- **Closed-enum red-rejection:** `gate_id: Literal["G0"]` + `gate_focus: Literal["trial_open"]` + ConfigDict.extra=forbid (inherited from base) gives the triple-layer rejection (Literal type + extra=forbid + Pydantic ValidationError on construction with non-G0 / non-trial_open value).
- **Schema-version emission:** verify the emitted JSON Schema includes `"schema_version": "v1"` (FR-7c-51). If the shared base does NOT auto-emit, add `model_config = ConfigDict(json_schema_extra={"schema_version": "v1"})` to G0Card.
- **Golden fixture determinism:** use stable UUIDs (e.g., `00000000-0000-4000-8000-00000000G000` style with G0 in last 4) + tz-aware `2026-05-05T00:00:00+00:00` + `meta.cache_state: "healthy"` + zero-population `meta.affected_nodes: []` + zero-population `meta.override_trail: []`.
- **K-target 1.4× ≈ 350 LOC ceiling.** Estimate ~250 LOC actual (50 model + 50 schema + 110 shape-pin + 40 golden).
- **R-tier R2:** focused parity tests + targeted broad regression on decision_cards lockstep. Full broad regression at T9 confirms delta=0.
- **Class-conformance increment:** validator should report 12 contracts after this story (was 11; +1 for `test_decision_card_g0_shape.py`). If validator returns 11, the new shape-pin is structurally non-conformant — debug.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g0_shape.py -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest tests/schemas/operator_verdict/test_section_02a_shape.py tests/gates/section_02a/ -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line   # R2 broad

.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

.venv/Scripts/lint-imports.exe   # Expect 12 KEPT (UNCHANGED)

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g0-decision-card-fresh-author.md

.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g0.py tests/parity/test_decision_card_g0_shape.py
```

Expected:
- Focused: 5 tests passed.
- Smoke: 200-nodeid baseline UNCHANGED (G0 not in smoke set).
- §02A: UNCHANGED (15 tests passed; AC-D regression check).
- R2 broad: 39 inherited checkout-level failures preserved (delta=0).
- Class-conformance: 12 (was 11).
- Lint-imports: 12 KEPT (UNCHANGED).
- Sandbox-AC: PASS.
- Ruff: clean.

## T10 + T11

T10: dropbox at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g0.ready-for-review.md`. Include: 4-file lockstep verification + class-conformance 11→12 delta + AMEND-7d-i compliance evidence (LOCKSTEP_CHECK imported by reference; show import line) + T1 decisions documented (especially which base-class name 7c.4b shipped) + §02A AC-D regression delta.

T11: Claude standard review. AC-A through E line-by-line; Pydantic-v2 14-idiom checklist conformance; closed-enum red-rejection verified; LOCKSTEP_CHECK citation pattern verified. Verdict at `_bmad-output/implementation-artifacts/7c-5-g0-code-review-2026-05-NN.md`.

## Boundary

HALT on: 7c.4b not done; LOCKSTEP_CHECK not importable; class-conformance baseline ≠ 11 pre-7c.5.G0; §02A regression baseline ≠ PASS at T1; any LOCKSTEP_CHECK re-derivation in shape-pin (would fail AMEND-7d-i); class-conformance count after this story ≠ 12; broad-regression failure count > T1 baseline.

DO NOT touch: 7c.4b deliverables (read-only); 7c.3b deliverables (read-only); existing G1/G2C/G3/G4 cards or fixtures; §02A poll-surface; C4/C5/C6 contracts.

DO NOT introduce: new third-party deps; mock 7c.4b's DecisionCardBase; defensive enum widening (gate_id MUST be exactly Literal["G0"] not Literal["G0", "G0a"]); golden fixtures with non-deterministic timestamps or random UUIDs.
```

---

## Operator dispatch checklist

1. ☐ 7c.4b `done` (verified at sprint-status.yaml).
2. ☐ AMELIA-P2 freshness check: re-diff this spec against pre-authored prompt; regenerate spec section if 7c.4b T11 introduced contract amendments.
3. ☐ Sandbox-AC validator PASS on spec.
4. ☐ Governance JSON entry current.
5. ☐ Sprint-status flip: `migration-7c-5-g0-decision-card-fresh-author: backlog → ready-for-dev`.
6. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

1. Codex drops dropbox notice.
2. Claude T11 standard review (~15-20 min).
3. Apply remediation cycles per HALT-AND-REMEDIATE if any.
4. Commit + flip done.
5. At 7c.5.G0 close: 0 stories unblock directly (other 7c.5.G* stories all gate on 7c.4b only; 7c.6..7c.15 wait on their per-gate predecessor).
