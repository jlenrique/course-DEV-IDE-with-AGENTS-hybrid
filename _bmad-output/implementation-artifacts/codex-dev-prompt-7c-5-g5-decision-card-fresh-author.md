# Codex dev-story prompt — Story 7c.5.G5 (G5 DecisionCard Fresh-Author; single-gate; standard T11)

**Cycle:** Claude spec (lookahead_tier=1; predecessor 7c.4b CLOSED at `8b12970`; siblings G0+G2A CLOSED at `e2aa599` 2026-05-05 — Codex T1-T10 + Claude T11 standard PASS zero-patches) → Codex T1-T10 → drops `_codex-handoff/7c-5-g5.ready-for-review.md` → Claude T11 standard → commit + flip done.
**Wave:** 2 — slot 7 (third per-gate fresh-author; G5 final operator handoff).
**Pre-authored:** 2026-05-05.
**Dispatch state:** **DISPATCH-READY 2026-05-05 post-G0+G2A T11 close** — sibling pattern committed at `e2aa599`. AMELIA-P2 freshness check at dispatch-time (re-read on-disk g0.py / g2a.py for canonical post-T11 pattern).

**Parallel-dispatch context:** This story is expected to dispatch concurrently with 7c.5.G6 (path-disjoint fresh-author pair). The fenced prompt block below contains a binding **PARALLEL-DISPATCH GUARDRAILS** section harvested from the validated G0+G2A 2026-05-05 dual-Codex run.

---

```
Run bmad-dev-story on Story 7c.5.G5 (Slab 7c Wave 2 slot 7; single-gate; fresh-author; standard T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-5-g5-decision-card-fresh-author.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8 contract).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-05.md` (T11 verdict; 2-class regime — fresh-author G* consume `_base.py:DecisionCardBase`; legacy G1/G2C/G3/G4 stay on `base.py:DecisionCard`).
4. `_bmad-output/implementation-artifacts/7c-5-g0-code-review-2026-05-05.md` AND `_bmad-output/implementation-artifacts/7c-5-g2a-code-review-2026-05-05.md` (sibling T11 verdicts; PARALLEL-DISPATCH GUARDRAILS below cite these).
5. `app/models/decision_cards/_base.py` (canonical `DecisionCardBase` + `DecisionCardMeta` + `CacheState` + `CacheStateLiteral`).
6. `app/models/decision_cards/g0.py` (sibling fresh-author canonical pattern; ~92 LOC; mirror inheritance + Literal discriminators + field_validator chain + field_serializer for Path lists).
7. `app/models/decision_cards/g2a.py` (sibling fresh-author; reference for `UUID4`-typed fields + strip-then-non-empty validator pattern — guardrail #4 below requires G5 mirror G2A on these two cosmetic ratchets).
8. `tests/parity/test_decision_card_g0_shape.py` AND `tests/parity/test_decision_card_g2a_shape.py` (sibling shape-pin patterns; closed-enum red-rejection + JSON-Schema byte-match + golden round-trip).
9. `tests/fixtures/decision_cards/g0_golden.json` AND `g2a_golden.json` (golden-fixture shape references).
10. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK + FOUR_FILE_GLOBS; AMEND-7d-i — cite by reference; do NOT re-derive).
11. `tests/structural/test_tw_7c_3_firing_spec_single_source.py` (AMEND-7d-i AST-scan boundary; this test scans your shape-pin for `FOUR_FILE_GLOBS` / `all_four_present` substrings outside import lines — must be clean).
12. `tests/parity/test_decision_card_base_shape.py` (7c.4b D8 base-class shape-pin; structural pattern reference).
13. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G5 = final operator handoff gate; family-contract authoring target; in 18-ID PRODUCTION_GATE_IDS list).
14. `docs/dev-guide/pydantic-v2-schema-checklist.md` (AC-E 14-idiom conformance).
15. Governance JSON `7c-5-g5` (single-gate; cross_agent_review_required=false; pts=1; K=1.2; r_tier=R2; t11_tier=standard; lookahead_tier=1; prerequisite_stories=[7c-4b]).

## T1 hard checkpoints (HALT-AND-SURFACE)

- 7c.4b status `done` (sprint-status.yaml).
- 7c.5.G0 + 7c.5.G2A status `done` (sibling pattern committed at `e2aa599`).
- `DecisionCardBase` importable from `app.models.decision_cards._base` (NOT legacy `app.models.decision_cards.base.DecisionCard`).
- `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` importable from `app.parity.contracts.tw_7c_3_firing`.
- Class-conformance baseline at T1: `13` (11 activation + 2 decision-card shape-pins for G0+G2A). If concurrent G6 dispatch lands first this number may be 14 — record observed baseline.
- Broad-regression baseline: re-run at T1; expect ~44 inherited checkout-level failures (governance-version drift on NFR-CG6 etc.). Record for T9 delta-compare.

## PARALLEL-DISPATCH GUARDRAILS (binding; harvested from G0+G2A 2026-05-05 dual-Codex run)

These six rules are derived from a real validated parallel run, not theoretical hazards. Treat as binding constraints alongside the standard ACs.

1. **AMEND-7d-i AST-scan compliance — the dominant parallel-dispatch failure mode.** During the G2A parallel run, a worker thread initially shipped `tests/parity/test_decision_card_g2a_shape.py` with a re-derivation of `all_four_present` from `FOUR_FILE_GLOBS` (instead of importing `LOCKSTEP_CHECK` and probing via the canonical `files_present` dict-shape). The structural test would have caught this at T6, but parallel dispatch increases the risk that a worker's local view thinks the problem is solved while the AST-scan boundary is invisibly violated. **MANDATORY CHECK at T5.2:** after authoring the shape-pin, grep your own file for `FOUR_FILE_GLOBS` and `all_four_present`. ZERO matches outside bare `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` import lines. If any match exists in test-body code, REWRITE — do NOT silence the AST scan.

2. **Pattern-replication discipline — read the canonical sibling, not the spec hedging.** The pre-authored G5/G6 specs were written before G0/G2A T11 closed. Codex's actual shipped `app/models/decision_cards/g0.py` AND `g2a.py` ARE the canonical patterns (validated through cross-agent + standard T11 reviews). When in doubt about field shapes, validators, or serializer signatures: **prefer reading `g0.py` / `g2a.py` over re-interpreting the spec's natural-language description.**

3. **Shared-file integration ordering — main-thread-coordinator pattern.** `app/models/decision_cards/__init__.py` flat-export was extended for G0+G2A (shipped at `e2aa599`). Both G5 and G6 will need flat-export updates to `__init__.py`. **If running concurrently with G6:** coordinate or sequence the integration. The main thread (or whichever worker integrates first) writes the union of G0/G2A/G5/G6 exports; the second worker rebases its local edit before commit. Do NOT have both workers blindly overwrite `__init__.py` in independent diffs — git will see the conflict but it's avoidable. Same applies to `scripts/utilities/validate_parity_test_class_conformance.py` (already extended for shape-pin counting; should NOT need further changes for G5+G6 — verify at T1).

4. **Pattern-parity ratchet (cosmetic — but apply at T2).** The G0 T11 review flagged two SHOULD-FIX items that should NOT recur in G5:
   - **Non-empty-string validators:** strip whitespace before non-empty check. G2A's `plan_unit_summary` validator strips; G0's `corpus_confirmation_summary` does not (G0 accepts `"   "`). For G5's `handoff_summary`, use the G2A strip-then-check pattern: `if not value.strip(): raise ValueError("handoff_summary must be non-empty (excluding whitespace)")`.
   - **UUID type annotation:** use Pydantic-typed `UUID4` in field annotations (mirror G2A), NOT bare `UUID` (G0's choice). Runtime contract is identical via `enforce_uuid4_version`, but JSON-Schema emission shows `format: "uuid4"` (preferred) vs `"uuid"`. Apply to G5's `card_id` / `trial_id` / `bundle_run_id`. Import: `from pydantic import UUID4` (typed) — keep `from uuid import UUID` only if needed for non-field usage.

5. **Class-conformance baseline arithmetic under concurrent landings.** If G5 and G6 land in the same commit batch (concurrent close), the validator should report `15` (11 activation + 4 decision-card shape-pins for G0/G2A/G5/G6). T1 records baseline (likely 13 if G6 not yet landed; could be 14 if G6 landed first); T6.5 expects exactly `+1` if landing alone, or `+2` if landing in the same batch as the sibling. **Document at T10 which arithmetic applies** so T11 can verify exact increment.

6. **Broad-regression baseline shift.** Codex's G0+G2A T9 reported `44 failed, 4132 passed`. T11 verified all 44 are inherited checkout-level (NFR-CG6 governance-version drift + 43 others predating this session). **At T1, record the post-G0+G2A baseline** (re-run broad regression; expect ~44). At T9, delta MUST be ≤ 0; ≥1 new failure attributable to G5 is HALT-AND-SURFACE. Do NOT attribute new failures to "inherited" without verifying via `git log` on the failing test or its source.

## Files in scope

**New (4 files; STRICT four-file-lockstep co-commit):**
- `app/models/decision_cards/g5.py` — `G5Card(DecisionCardBase)`; `gate_id: Literal["G5"]` + `gate_focus: Literal["final_operator_handoff"]` + 3 G5-specific fields:
  - `bundle_run_id: UUID4` (Pydantic-typed UUID4 per guardrail #4; NOT bare `UUID`)
  - `handoff_artifact_paths: list[Path]` (non-empty validated; field_serializer to posix string list — mirror G0's `_serialize_corpus_paths`)
  - `handoff_summary: str` (strip-then-non-empty validated per guardrail #4)
  - Plus standard fields per G2A pattern: `schema_version: Literal["v1"]`, `card_id: UUID4`, `trial_id: UUID4`, `created_at`, `verb`.
- `app/models/decision_cards/schema/g5.v1.schema.json` — JSON Schema regenerated from `G5Card.model_json_schema()` (deterministic; sort_keys; FR-7c-51 schema_version v1; UUID4 fields emit `format: "uuid4"`).
- `tests/parity/test_decision_card_g5_shape.py` — 8 test cases (12 fields presence + closed-enum red-rejection on gate_id + gate_focus + JSON-Schema byte-match + golden round-trip + non-empty handoff_artifact_paths + strip-then-non-empty handoff_summary [include test for whitespace-only rejection per guardrail #4] + frozen mutation rejection). MUST `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i; only this import; NO `FOUR_FILE_GLOBS` / `all_four_present` references in test body).
- `tests/fixtures/decision_cards/g5_golden.json` — deterministic fixture with all 12 required fields.

**Modified (≤1 file):**
- `app/models/decision_cards/__init__.py` — flat-export of `G5Card` (mirror G0/G2A union extension; per guardrail #3, coordinate with G6 if concurrent).

**Do NOT modify:**
- 7c.4b's `_base.py` / `base.py` — read-only.
- 7c.4b's `tw_7c_3_firing.py` — import-only.
- Sibling G0Card / G2ACard or their schemas / fixtures / shape-pins — read-only pattern reference.
- Legacy G1/G2C/G3/G4 cards.
- `scripts/utilities/validate_parity_test_class_conformance.py` (already extended at G0+G2A close; G5 should not require further extension — verify at T1).
- C4/C5/C6 import-linter contracts.

## Critical implementation notes

- **Strict four-file lockstep:** all 4 files MUST be co-committed in one diff. If any one is missing or out-of-sync at T9, TW-7c-3 fires (critical) and HALT.
- **AMEND-7d-i compliance (+ guardrail #1):** the shape-pin imports `LOCKSTEP_CHECK` only; do NOT define a local `LOCKSTEP_CHECK`, do NOT import `FOUR_FILE_GLOBS`, do NOT re-derive `all_four_present`.
- **Closed-enum red-rejection:** `gate_id: Literal["G5"]` + `gate_focus: Literal["final_operator_handoff"]` + ConfigDict.extra=forbid (inherited).
- **Schema-version emission:** Pydantic emits `schema_version` automatically from `Literal["v1"]`.
- **Golden fixture determinism:** stable UUID4 with G5 in last 4 digits (e.g., `00000000-0000-4000-8000-000000000005`) + tz-aware ISO 8601 (`2026-05-05T00:00:00+00:00`) + `meta.cache_state: "healthy"` + `meta.affected_nodes: []` + `meta.override_trail: []` + ≥1 deterministic path in `handoff_artifact_paths` + non-empty `handoff_summary` + valid 64-char lowercase hex `decision_card_digest`.
- **K-target 1.2× ≈ 300 LOC ceiling.** Estimate ~250 LOC actual.
- **R-tier R2:** focused parity + cross-gate non-regression + targeted broad regression.
- **Class-conformance increment:** validator reports T1-baseline `+1` (or `+2` if G6 lands in same batch per guardrail #5).
- **2-class regime:** G5Card MUST inherit from `_base.py:DecisionCardBase`.

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g5_shape.py -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest tests/structural/test_tw_7c_3_firing_spec_single_source.py -p no:randomly -q --tb=short   # AMEND-7d-i AST-scan; guardrail #1

.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ -p no:randomly -q --tb=short   # AC-D cross-gate

.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short

.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line   # R2 broad

.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

.venv/Scripts/lint-imports.exe   # Expect 12 KEPT (UNCHANGED)

.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g5-decision-card-fresh-author.md

.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g5.py tests/parity/test_decision_card_g5_shape.py app/models/decision_cards/__init__.py
```

Expected:
- Focused: 8 tests passed.
- AMEND-7d-i AST-scan: PASS (guardrail #1 verified clean).
- AC-D cross-gate: PASS UNCHANGED.
- Smoke: 200-nodeid baseline UNCHANGED.
- R2 broad: ~44 inherited preserved (delta ≤ 0; per guardrail #6).
- Class-conformance: T1-baseline + 1 (or +2 if concurrent G6 close per guardrail #5; document at T10).
- Lint-imports: 12 KEPT.
- Sandbox-AC: PASS.
- Ruff: clean.

## T10 + T11

T10: dropbox at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g5.ready-for-review.md`. Include:
- 4-file lockstep verification.
- Class-conformance delta WITH arithmetic statement (T1-baseline observed N → +K; document whether sibling G6 landed first).
- AMEND-7d-i compliance evidence: paste the exact `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` line from the shape-pin AND state "ZERO matches for FOUR_FILE_GLOBS / all_four_present in test body" (per guardrail #1).
- AC-D cross-gate non-regression confirmation.
- 2-class regime confirmation (G5Card inherits `DecisionCardBase` from `_base.py`).
- Pattern-parity-ratchet confirmation: "handoff_summary uses strip-then-non-empty per G2A pattern" + "card_id / trial_id / bundle_run_id typed as UUID4 not bare UUID per guardrail #4".
- Broad-regression delta WITH per-failure attribution (per guardrail #6).
- If concurrent G6 dispatch detected: note any `__init__.py` integration coordination (per guardrail #3).

T11: Claude standard review. AC-A through E line-by-line; Pydantic-v2 14-idiom checklist; closed-enum red-rejection; LOCKSTEP_CHECK citation pattern; sibling-pattern parity; **all six PARALLEL-DISPATCH GUARDRAILS verified**. Verdict at `_bmad-output/implementation-artifacts/7c-5-g5-code-review-2026-05-NN.md`.

## Boundary

HALT on:
- 7c.4b not done; G0 or G2A not done.
- LOCKSTEP_CHECK not importable.
- Class-conformance baseline differs from validator output.
- Any LOCKSTEP_CHECK re-derivation, `FOUR_FILE_GLOBS` import, or `all_four_present` reference in test body (guardrail #1).
- Class-conformance count after this story ≠ T1-baseline + 1 (or +2 if concurrent G6 close).
- Broad-regression failure count > T1 baseline AND any new failure not demonstrably inherited (guardrail #6).
- G5Card inheriting from legacy `base.py:DecisionCard` (must inherit from `_base.py:DecisionCardBase`).
- `__init__.py` integration conflict with concurrent G6 worker (guardrail #3) — coordinate or sequence; do NOT silently overwrite.

DO NOT touch: 7c.4b deliverables; sibling G0/G2A deliverables; legacy G1/G2C/G3/G4 cards; C4/C5/C6 contracts; class-conformance validator (already extended).

DO NOT introduce: new third-party deps; mock 7c.4b's DecisionCardBase; defensive enum widening; golden fixtures with non-deterministic timestamps or random UUIDs.
```

---

## Operator dispatch checklist

1. ☐ 7c.4b `done`.
2. ☐ G0 + G2A `done` (committed at `e2aa599`).
3. ☐ AMELIA-P2 freshness check: re-diff this prompt against on-disk g0.py / g2a.py for any post-T11 pattern divergence.
4. ☐ Sandbox-AC validator PASS on spec.
5. ☐ Governance JSON entry current.
6. ☐ Sprint-status: `migration-7c-5-g5-decision-card-fresh-author: ready-for-dev`.
7. ☐ If dispatching concurrently with G6: confirm both Codex workers are aware of guardrail #3 (`__init__.py` integration coordination).
8. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

1. Codex drops dropbox notice with all six PARALLEL-DISPATCH GUARDRAILS evidence.
2. Claude T11 standard review (~15-20 min); verify all six guardrails specifically.
3. Apply remediation cycles per HALT-AND-REMEDIATE if any.
4. Commit + flip done.
5. At 7c.5.G5 close: 7c.15 incrementally unblocks (still gates on remaining prereqs).
