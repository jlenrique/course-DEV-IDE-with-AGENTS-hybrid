# Codex dev-story prompt — Story 7c.5.G6 (G6 DecisionCard Fresh-Author; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=1; predecessor 7c.4b CLOSED at `8b12970`; siblings G0+G2A in flight 2026-05-05) → Codex T1-T10 → drops `_codex-handoff/7c-5-g6.ready-for-review.md` → Claude T11 standard → commit + flip done.
**Wave:** 2 — slot 8 (fourth/final per-gate fresh-author; G6 slab-close ceremony).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **HELD-RELEASED 2026-05-05** — G0+G2A at `review` with all sibling pattern artifacts on disk. Per operator-override pattern, Codex dispatches pre-T11-close. AMELIA-P2 freshness re-check at dispatch-time.

---

```
Run bmad-dev-story on Story 7c.5.G6 (Slab 7c Wave 2 slot 8; single-gate; fresh-author; standard T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-5-g6-decision-card-fresh-author.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8 contract).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-05.md` (T11 verdict; documents 2-class regime).
4. `app/models/decision_cards/_base.py` (canonical `DecisionCardBase` + `DecisionCardMeta` + `CacheState`).
5. `app/models/decision_cards/g0.py` (sibling fresh-author canonical pattern; ~92 LOC).
6. `tests/parity/test_decision_card_g0_shape.py` (sibling shape-pin pattern reference).
7. `tests/fixtures/decision_cards/g0_golden.json` (golden-fixture shape reference).
8. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK + FOUR_FILE_GLOBS; AMEND-7d-i).
9. `tests/parity/test_decision_card_base_shape.py` (7c.4b D8 base-class shape-pin).
10. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G6 = slab-close ceremony; family-contract authoring target; NOT in 18-ID runtime list).
11. `docs/dev-guide/pydantic-v2-schema-checklist.md` (AC-E 14-idiom conformance).
12. Governance JSON `7c-5-g6` (single-gate; cross_agent_review_required=false; pts=1; K=1.2; r_tier=R2; t11_tier=standard; lookahead_tier=1; prerequisite_stories=[7c-4b]).

## T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.4b status `done`.
- Sibling fresh-author pattern files exist on disk (relaxed from "done in sprint-status" per HELD-RELEASED operator-override): g0.py + g2a.py + schemas + shape-pins + goldens.
- `DecisionCardBase` importable from `app.models.decision_cards._base` (NOT legacy `base.DecisionCard`).
- `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` importable.
- Class-conformance baseline: run validator at T1; current expected = 13 (or 14 if G5 already landed); this story increments by exactly +1.
- Broad-regression baseline: ~44 failed at G2A close (preserve at T9; delta ≤ 0).

## Files in scope

**New (4 files; STRICT four-file-lockstep co-commit):**
- `app/models/decision_cards/g6.py` — `G6Card(DecisionCardBase)`; `gate_id: Literal["G6"]` + `gate_focus: Literal["slab_close_ceremony"]` + 5 G6-specific fields:
  - `slab_id: str` (regex `^[0-9]+[a-z]?$` validated; e.g., "7c", "7", "12b")
  - `closing_run_id: UUID` (UUID4-validated)
  - `retrospective_path: Path` (single-value; field_serializer to posix string)
  - `closing_artifact_paths: list[Path]` (non-empty validated; field_serializer to posix string list — mirror G0)
  - `slab_close_summary: str` (non-empty validated)
  - Plus standard fields per G0 pattern: `schema_version: Literal["v1"]`, `card_id`, `trial_id`, `created_at`, `verb`.
- `app/models/decision_cards/schema/g6.v1.schema.json` — JSON Schema regenerated (deterministic; sort_keys; FR-7c-51 schema_version v1).
- `tests/parity/test_decision_card_g6_shape.py` — 9 test cases (14 fields presence + closed-enum red-rejection on gate_id + gate_focus + JSON-Schema byte-match + golden round-trip + non-empty closing_artifact_paths + non-empty slab_close_summary + slab_id regex pattern parametrize-accept/reject + frozen mutation rejection). MUST `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i).
- `tests/fixtures/decision_cards/g6_golden.json` — deterministic fixture with all 14 required fields.

**Modified (≤1 file):**
- `app/models/decision_cards/__init__.py` — flat-export of `G6Card` if pattern matches G0/G2A.

**Do NOT modify:**
- 7c.4b's `_base.py` / `base.py` — read-only.
- 7c.4b's `tw_7c_3_firing.py` — import-only.
- Sibling G0Card / G2ACard / G5Card or their schemas / fixtures / shape-pins — read-only pattern reference.
- Legacy G1/G2C/G3/G4 cards.
- C4/C5/C6 import-linter contracts.

## Critical implementation notes

- **Strict four-file lockstep:** all 4 files MUST be co-committed in one diff.
- **AMEND-7d-i compliance:** shape-pin imports `LOCKSTEP_CHECK` by reference; do NOT re-derive.
- **Closed-enum red-rejection:** `gate_id: Literal["G6"]` + `gate_focus: Literal["slab_close_ceremony"]` + ConfigDict.extra=forbid (inherited).
- **slab_id pattern:** `^[0-9]+[a-z]?$` — accepts `"7"`, `"7c"`, `"12"`, `"12b"`, `"5a"`; rejects `""`, `"slab-7c"`, `"7C"` (uppercase), `"7-c"` (hyphen), `"7cd"` (multi-letter), `"7ab"` (multi-letter). Use `field_validator("slab_id")` with `re.fullmatch`.
- **Schema-version emission:** Pydantic emits `schema_version` automatically from `Literal["v1"]`.
- **Golden fixture determinism:** stable UUID4 with G6 in last 4 digits (e.g., `00000000-0000-4000-8000-000000000006`) + tz-aware ISO 8601 + `meta.cache_state: "healthy"` + `slab_id: "7c"` + ≥1 deterministic path in `closing_artifact_paths` + non-empty `retrospective_path` + non-empty `slab_close_summary` + valid 64-char lowercase hex `decision_card_digest`.
- **K-target 1.2× ≈ 312 LOC ceiling.** Estimate ~260 LOC actual.
- **R-tier R2:** focused parity + cross-gate non-regression + targeted broad regression.
- **Class-conformance increment:** validator should report T1-baseline + 1.
- **2-class regime:** G6Card MUST inherit from `_base.py:DecisionCardBase`.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g6_shape.py -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ -p no:randomly -q --tb=short   # AC-D cross-gate

.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line   # R2 broad

.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

.venv/Scripts/lint-imports.exe   # Expect 12 KEPT (UNCHANGED)

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g6-decision-card-fresh-author.md

.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g6.py tests/parity/test_decision_card_g6_shape.py
```

Expected:
- Focused: 9 tests passed.
- AC-D cross-gate: PASS UNCHANGED.
- Smoke: 200-nodeid baseline UNCHANGED.
- R2 broad: 39-41 inherited preserved (delta ≤ 0).
- Class-conformance: T1-baseline + 1.
- Lint-imports: 12 KEPT.
- Sandbox-AC: PASS.
- Ruff: clean.

## T10 + T11

T10: dropbox at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g6.ready-for-review.md`. Include: 4-file lockstep verification + class-conformance delta + AMEND-7d-i compliance evidence + AC-D cross-gate non-regression + 2-class regime confirmation (G6Card inherits `DecisionCardBase` from `_base.py`) + slab_id regex parametrize evidence (accept/reject matrix).

T11: Claude standard review. AC-A through E line-by-line; Pydantic-v2 14-idiom checklist; closed-enum red-rejection; LOCKSTEP_CHECK citation pattern; sibling-pattern parity (G6Card structurally mirrors G0Card except gate-specific fields + slab_id regex). Verdict at `_bmad-output/implementation-artifacts/7c-5-g6-code-review-2026-05-NN.md`.

## Boundary

HALT on: 7c.4b not done; neither G0 nor G2A done at dispatch-time; LOCKSTEP_CHECK not importable; class-conformance baseline differs; any LOCKSTEP_CHECK re-derivation; class-conformance count after this story ≠ T1-baseline + 1; broad-regression failure count > T1 baseline; G6Card inheriting from legacy `base.py:DecisionCard`; slab_id regex too permissive (e.g., accepts uppercase or hyphenated forms).

DO NOT touch: 7c.4b deliverables; sibling G0/G2A/G5 deliverables; legacy G1/G2C/G3/G4 cards; C4/C5/C6 contracts.

DO NOT introduce: new third-party deps; defensive enum widening; golden fixtures with non-deterministic timestamps or random UUIDs; runtime promotion of G6 to PRODUCTION_GATE_IDS list (out-of-scope per ADR 0002 §1).
```

---

## Operator dispatch checklist

1. ☐ 7c.4b `done`.
2. ☐ At least one of 7c.5.G0 / 7c.5.G2A `done`.
3. ☐ AMELIA-P2 freshness check.
4. ☐ Sandbox-AC validator PASS on spec.
5. ☐ Governance JSON entry current.
6. ☐ Sprint-status flip: `migration-7c-5-g6-decision-card-fresh-author: backlog → ready-for-dev`.
7. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

1. Codex drops dropbox notice.
2. Claude T11 standard review (~15-20 min).
3. Apply remediation cycles per HALT-AND-REMEDIATE if any.
4. Commit + flip done.
5. At 7c.5.G6 close: 7c.21 incrementally unblocks (still gates on remaining Wave-2/3/4/5 closure).
