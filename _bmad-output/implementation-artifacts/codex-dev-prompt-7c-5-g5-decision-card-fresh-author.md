# Codex dev-story prompt — Story 7c.5.G5 (G5 DecisionCard Fresh-Author; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=1; predecessor 7c.4b CLOSED at `8b12970`; siblings G0+G2A in flight 2026-05-05) → Codex T1-T10 → drops `_codex-handoff/7c-5-g5.ready-for-review.md` → Claude T11 standard → commit + flip done.
**Wave:** 2 — slot 7 (third per-gate fresh-author; G5 final operator handoff).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **HELD-RELEASED 2026-05-05** — G0+G2A at `review` with all sibling pattern artifacts on disk (g0.py + g2a.py + schemas + shape-pins + goldens). Per operator-override pattern, Codex dispatches pre-T11-close. AMELIA-P2 freshness re-check at dispatch-time (re-read g0.py if any post-T11 patch lands first).

---

```
Run bmad-dev-story on Story 7c.5.G5 (Slab 7c Wave 2 slot 7; single-gate; fresh-author; standard T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-5-g5-decision-card-fresh-author.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8 contract).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-05.md` (T11 verdict; documents 2-class regime — fresh-author G* consume `_base.py:DecisionCardBase`; legacy G1/G2C/G3/G4 stay on `base.py:DecisionCard` until 7c.5.G1+ extend-and-audit migrates them).
4. `app/models/decision_cards/_base.py` (canonical `DecisionCardBase` + `DecisionCardMeta` + `CacheState` + `CacheStateLiteral`).
5. `app/models/decision_cards/g0.py` (sibling fresh-author canonical pattern; ~92 LOC; mirror its inheritance + Literal discriminators + field_validator chain + field_serializer for Path lists).
6. `tests/parity/test_decision_card_g0_shape.py` (sibling fresh-author shape-pin; pattern reference for closed-enum red-rejection + JSON-Schema byte-match + golden round-trip).
7. `tests/fixtures/decision_cards/g0_golden.json` (golden-fixture shape reference).
8. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK + FOUR_FILE_GLOBS; AMEND-7d-i — cite by reference; do NOT re-derive).
9. `tests/parity/test_decision_card_base_shape.py` (7c.4b D8 base-class shape-pin; structural pattern reference).
10. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G5 = final operator handoff gate; family-contract authoring target; in 18-ID PRODUCTION_GATE_IDS list).
11. `docs/dev-guide/pydantic-v2-schema-checklist.md` (AC-E 14-idiom conformance).
12. Governance JSON `7c-5-g5` (single-gate; cross_agent_review_required=false; pts=1; K=1.2; r_tier=R2; t11_tier=standard; lookahead_tier=1; prerequisite_stories=[7c-4b]).

## T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.4b status `done` (sprint-status.yaml).
- Sibling fresh-author pattern files exist on disk (relaxed from "done in sprint-status" per HELD-RELEASED operator-override): `app/models/decision_cards/g0.py` + `g2a.py` + their schemas + their shape-pins + their goldens.
- `DecisionCardBase` importable from `app.models.decision_cards._base` (NOT legacy `app.models.decision_cards.base.DecisionCard`).
- `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` importable from `app.parity.contracts.tw_7c_3_firing`.
- Class-conformance baseline: run validator at T1; current expected = 13 (11 activation + 2 decision-card shape-pins for G0+G2A); this story increments to 14.
- Broad-regression baseline: ~44 failed at G2A close (Codex T9 numbers); preserve at T9; delta ≤ 0.

## Files in scope

**New (4 files; STRICT four-file-lockstep co-commit):**
- `app/models/decision_cards/g5.py` — `G5Card(DecisionCardBase)`; `gate_id: Literal["G5"]` + `gate_focus: Literal["final_operator_handoff"]` + 3 G5-specific fields:
  - `bundle_run_id: UUID` (UUID4-validated)
  - `handoff_artifact_paths: list[Path]` (non-empty validated; field_serializer to posix string list — mirror G0's `_serialize_corpus_paths`)
  - `handoff_summary: str` (non-empty validated)
  - Plus standard fields per G0 pattern: `schema_version: Literal["v1"]`, `card_id`, `trial_id`, `created_at`, `verb`.
- `app/models/decision_cards/schema/g5.v1.schema.json` — JSON Schema regenerated from `G5Card.model_json_schema()` (deterministic; sort_keys; FR-7c-51 schema_version v1).
- `tests/parity/test_decision_card_g5_shape.py` — 8 test cases (12 fields presence + closed-enum red-rejection on gate_id + gate_focus + JSON-Schema byte-match + golden round-trip + non-empty handoff_artifact_paths + non-empty handoff_summary + frozen mutation rejection). MUST `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i).
- `tests/fixtures/decision_cards/g5_golden.json` — deterministic fixture with all 12 required fields.

**Modified (≤1 file):**
- `app/models/decision_cards/__init__.py` — flat-export of `G5Card` if pattern matches G0/G2A (mirror sibling).

**Do NOT modify:**
- 7c.4b's `_base.py` / `base.py` — this story consumes only.
- 7c.4b's `tw_7c_3_firing.py` — this story imports only.
- Sibling G0Card / G2ACard / G0/G2A schemas / fixtures / shape-pins (read-only pattern reference).
- Legacy G1/G2C/G3/G4 cards or schemas or fixtures.
- C4/C5/C6 import-linter contracts.

## Critical implementation notes

- **Strict four-file lockstep:** all 4 files MUST be co-committed in one diff. If any one is missing or out-of-sync at T9, TW-7c-3 fires (critical) and HALT.
- **AMEND-7d-i compliance:** the shape-pin imports `LOCKSTEP_CHECK` (and optionally `FOUR_FILE_GLOBS`) from `app.parity.contracts.tw_7c_3_firing`. Do NOT define a local `LOCKSTEP_CHECK` constant or re-derive the firing condition.
- **Closed-enum red-rejection:** `gate_id: Literal["G5"]` + `gate_focus: Literal["final_operator_handoff"]` + ConfigDict.extra=forbid (inherited from base) gives the triple-layer rejection.
- **Schema-version emission:** Pydantic emits `schema_version` automatically from the `Literal["v1"]` field declaration (per G0 pattern; verify via emitted JSON Schema).
- **Golden fixture determinism:** stable UUID4 with G5 in the last 4 digits (e.g., `00000000-0000-4000-8000-000000000005`) + tz-aware ISO 8601 (`2026-05-05T00:00:00+00:00`) + `meta.cache_state: "healthy"` + `meta.affected_nodes: []` + `meta.override_trail: []` + ≥1 deterministic path in `handoff_artifact_paths` (e.g., `course-content/courses/example-trial/assembly-bundle/`) + non-empty `handoff_summary` + valid 64-char lowercase hex `decision_card_digest`.
- **K-target 1.2× ≈ 300 LOC ceiling.** Estimate ~250 LOC actual.
- **R-tier R2:** focused parity tests + cross-gate non-regression + targeted broad regression. Full broad regression at T9 confirms delta=0.
- **Class-conformance increment:** validator should report T1-baseline + 1 after this story (T1-baseline depends on which siblings have landed; record at T1 and verify exact +1 increment).
- **2-class regime:** G5Card MUST inherit from `_base.py:DecisionCardBase` (NEW), NOT from `base.py:DecisionCard` (legacy used by G1/G2C/G3/G4).

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g5_shape.py -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ -p no:randomly -q --tb=short   # AC-D cross-gate

.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line   # R2 broad

.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

.venv/Scripts/lint-imports.exe   # Expect 12 KEPT (UNCHANGED)

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g5-decision-card-fresh-author.md

.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g5.py tests/parity/test_decision_card_g5_shape.py
```

Expected:
- Focused: 8 tests passed.
- AC-D cross-gate: PASS UNCHANGED (existing per-gate shape-pins green).
- Smoke: 200-nodeid baseline UNCHANGED.
- R2 broad: 39-41 inherited checkout-level failures preserved (delta ≤ 0).
- Class-conformance: T1-baseline + 1.
- Lint-imports: 12 KEPT (UNCHANGED).
- Sandbox-AC: PASS.
- Ruff: clean.

## T10 + T11

T10: dropbox at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g5.ready-for-review.md`. Include: 4-file lockstep verification + class-conformance delta (T1-baseline → +1) + AMEND-7d-i compliance evidence (LOCKSTEP_CHECK imported by reference; show import line) + AC-D cross-gate non-regression confirmation + 2-class regime confirmation (G5Card inherits `DecisionCardBase` from `_base.py`).

T11: Claude standard review. AC-A through E line-by-line; Pydantic-v2 14-idiom checklist conformance; closed-enum red-rejection verified; LOCKSTEP_CHECK citation pattern verified; sibling-pattern parity verified (G5Card structurally mirrors G0Card except for gate-specific fields). Verdict at `_bmad-output/implementation-artifacts/7c-5-g5-code-review-2026-05-NN.md`.

## Boundary

HALT on: 7c.4b not done; neither G0 nor G2A done at dispatch-time; LOCKSTEP_CHECK not importable; class-conformance baseline differs from validator output; any LOCKSTEP_CHECK re-derivation in shape-pin (would fail AMEND-7d-i); class-conformance count after this story ≠ T1-baseline + 1; broad-regression failure count > T1 baseline; G5Card inheriting from legacy `base.py:DecisionCard` (must inherit from `_base.py:DecisionCardBase`).

DO NOT touch: 7c.4b deliverables (read-only); sibling G0/G2A deliverables (read-only pattern reference); legacy G1/G2C/G3/G4 cards or fixtures; C4/C5/C6 contracts.

DO NOT introduce: new third-party deps; mock 7c.4b's DecisionCardBase; defensive enum widening (gate_id MUST be exactly Literal["G5"] not Literal["G5", "G5A"]); golden fixtures with non-deterministic timestamps or random UUIDs.
```

---

## Operator dispatch checklist

1. ☐ 7c.4b `done` (verified at sprint-status.yaml).
2. ☐ At least one of 7c.5.G0 / 7c.5.G2A `done` (sibling pattern available).
3. ☐ AMELIA-P2 freshness check: re-diff this spec against pre-authored prompt; regenerate spec section if sibling-close introduced pattern divergence.
4. ☐ Sandbox-AC validator PASS on spec.
5. ☐ Governance JSON entry current.
6. ☐ Sprint-status flip: `migration-7c-5-g5-decision-card-fresh-author: backlog → ready-for-dev`.
7. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

1. Codex drops dropbox notice.
2. Claude T11 standard review (~15-20 min).
3. Apply remediation cycles per HALT-AND-REMEDIATE if any.
4. Commit + flip done.
5. At 7c.5.G5 close: 7c.15 unblocks (subject to 7c.4b + 7c.5.G4 + 7c.5.G5 + 7c.3b + 7c.17b prereqs all closed).
