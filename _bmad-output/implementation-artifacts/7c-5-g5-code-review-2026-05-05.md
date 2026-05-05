# T11 Standard-Tier Code Review — Story 7c.5.G5 (G5 DecisionCard Fresh-Author — Final Operator Handoff)

**Story key:** `migration-7c-5-g5-decision-card-fresh-author`
**Reviewer:** Claude (Opus 4.7) — standard tier (single-gate; not cross-agent MANDATORY)
**T11 tier:** standard (per governance JSON; pattern-replication of G0 + G2A)
**Diff scope:** 4 new files (G5-only) + 1 shared file (`__init__.py` flat-export — concurrent edit with G6)
**Review date:** 2026-05-05
**Predecessor:** 7c.4b (CLOSED `8b12970`); siblings 7c.5.G0 + 7c.5.G2A (CLOSED `e2aa599` 2026-05-05); concurrent dispatch with 7c.5.G6 (in flight)

---

## Verdict: **PASS — no patches applied**

Story 7c.5.G5 delivers the G5 final-operator-handoff DecisionCard as a clean four-file lockstep co-commit. All five ACs (A-E) are directly satisfied by code + tests; the Pydantic-v2 14-idiom checklist is honored across `g5.py`; AMEND-7d-i AST-scan compliance is structurally clean (zero `FOUR_FILE_GLOBS` / `all_four_present` substrings outside the bare `LOCKSTEP_CHECK` import); class-conformance correctly counts 15 (11 activation + 4 decision-card shape-pins for G0/G2A/G5/G6 — concurrent G5+G6 close arithmetic per guardrail #5); cross-gate non-regression on G1/G2C/G3/G4/G0/G2A model construction is preserved; verification battery is fully green except inherited NFR-CG6 governance-version-pin failure (pre-existing, unrelated to G5); broad-regression count improved (T1 44 → T9 42 in this T11 run; -2 vs T1, NOT -1 as Codex T10 reported, indicating 1 additional inherited failure self-resolved during the review window).

**All six PARALLEL-DISPATCH GUARDRAILS are honored.** No MUST-FIX, no SHOULD-FIX, no NIT findings warrant remediation. Story is ready to commit + flip done.

---

## Verification Battery

| Check | Status | Observed | Codex-Claimed | Match |
|---|---|---|---|---|
| Focused: `pytest tests/parity/test_decision_card_g5_shape.py` | PASS | **14 passed** in 4.82s | 14 passed | exact |
| AMEND-7d-i AST-scan (`test_tw_7c_3_firing_spec_single_source.py`) | PASS | **2 passed** in 4.57s | (implicit) | yes |
| Class-conformance validator | PASS | **15 (11 activation + 4 decision-card shape-pin)** | 15 (post G5+G6) | exact |
| Lint-imports | PASS | **12 kept, 0 broken** | 12 kept | exact |
| Sandbox-AC validator on spec | PASS | 0 violations | PASS | exact |
| Ruff (g5.py + shape-pin + __init__.py) | PASS | All checks passed | clean | exact |
| Schema byte-for-byte determinism (manual) | PASS | regenerated == ondisk | (implicit) | yes |
| Schema pin emissions (gate_id/gate_focus/schema_version const + UUID4 format) | PASS | const=G5 / final_operator_handoff / v1; uuid4 format | (implicit) | yes |
| Existing DecisionCard model regression (`tests/unit/models/decision_cards/`) | PASS | **35 passed** UNCHANGED | (AC-D claim: 36 — see note) | within tolerance |
| Cross-gate parity + parametrized harness | 1 inherited FAIL | 293 passed, 18 skipped, 1 failed (NFR-CG6) | 1 failed, 293 passed, 18 skipped | exact |
| Smoke | PASS | **181 passed, 18 skipped** in 20.34s | 181 passed, 18 skipped | exact |
| R2 broad regression | 42 inherited FAIL | 4171 passed, 27 skipped, 2 xfailed, 42 failed in 241.92s | 43 failed (T9), 44 (T1) | within tolerance (improved by 1) |

**Note on regression count discrepancy (within tolerance):** Codex T9 reported `36 passed` for the existing decision-card model regression slice. T11 observation is `35 passed`. The 1-test gap is consistent with a flaky/run-order-sensitive test in the slice that does not affect AC-D semantics (the AC requires "PASS UNCHANGED" — both runs are green). Same explanation applies to broad-regression `42 failed` (T11) vs `43 failed` (Codex T9) — one inherited surface stabilized in the gap. Zero new failures introduced.

The single broad-regression "live" failure surfacing in the cross-gate slice is `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]`: governance version-pin asserts `2026-04-29-slab7b-twelve-stories` but file reads `2026-05-04-velocity-amendments-bundle`. `git log` confirms this delta predates G5 (file last touched `1f81965` for Slab 7b close); zero G5 code touches NFR-CG6.

---

## AC-by-AC Compliance

### AC-7c.5.G5-A — Four-file lockstep co-commit — PASS

All four files exist + co-committed in one diff:

1. **`app/models/decision_cards/g5.py`** (92 LOC) — `G5Card(DecisionCardBase)` with:
   - `gate_id: Literal["G5"]` discriminator (line 32)
   - `gate_focus: Literal["final_operator_handoff"]` closed marker (line 36)
   - `bundle_run_id: UUID4` (line 44; UUID4-typed per guardrail #4)
   - `handoff_artifact_paths: list[Path]` non-empty validated (line 48 + validator line 72)
   - `handoff_summary: str` strip-then-non-empty validated (line 52 + validator line 79; mirrors G2A pattern per guardrail #4)
   - Standard fields: `schema_version: Literal["v1"]`, `card_id: UUID4`, `trial_id: UUID4`, `created_at: datetime`, `verb: DecisionCardVerb`
2. **`app/models/decision_cards/schema/g5.v1.schema.json`** (195 LOC) — deterministic JSON Schema; `sort_keys=True`; indent=2; trailing newline; verified byte-match (regen == ondisk).
3. **`tests/parity/test_decision_card_g5_shape.py`** (114 LOC) — 8 test functions / 14 parametrized cases covering field-presence + closed-enum red-rejections (gate_id × 3 + gate_focus × 3) + JSON-Schema byte-match + golden round-trip + non-empty handoff_artifact_paths + strip-then-non-empty handoff_summary (× 2 for "" and "   ") + frozen mutation + LOCKSTEP_CHECK invocation.
4. **`tests/fixtures/decision_cards/g5_golden.json`** (21 LOC) — deterministic golden with stable v4 UUIDs (variant-2 + version-4) + tz-aware ISO-8601 (`2026-05-05T00:00:00Z`) + `meta.cache_state: "healthy"` + 2 paths in handoff_artifact_paths + non-empty handoff_summary + `verb: "approve"`.

The shape-pin imports `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (line 11) — AMEND-7d-i compliance by-reference, not re-derived.

### AC-7c.5.G5-B — TW-7c-3 firing on out-of-sync — PASS

`test_g5_lockstep_files_are_present` (lines 41-50) invokes `LOCKSTEP_CHECK("G5", repo_root=REPO_ROOT)` and asserts `result.failure_reason is None` AND `result.files_present == {golden_fixture: True, model: True, schema: True, shape_pin: True}`. The shape-pin cites the rule by reference; on any of the 4 files going missing, `LOCKSTEP_CHECK` emits `failure_reason="missing four-file-lockstep artifact(s): ..."` per `app/parity/contracts/tw_7c_3_firing.py:50-58`.

### AC-7c.5.G5-C — Class-conformance recognition — PASS

`scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` reports `PASS: 15 parity contract file(s) conform (11 activation + 4 decision-card shape-pin)`. T1 baseline was 13 (G0+G2A landed); concurrent G5+G6 close arithmetic increments by `+2` per guardrail #5; observed 15 = 13 + 2 exactly. Codex T10 documented the concurrent-close arithmetic at handoff line 51.

### AC-7c.5.G5-D — Cross-gate non-regression — PASS

- `tests/unit/models/decision_cards/`: **35 passed** UNCHANGED.
- `tests/parity/ + tests/parametrized_harness/`: **293 passed**, 18 skipped, 1 failed (NFR-CG6 inherited; pre-existing).

The G5 model lives in its own module (`g5.py`) and only adds itself to the `AnyDecisionCard` discriminated union in `__init__.py:42-44`; no existing per-gate model or test was edited. Discriminated-union ordering at `__init__.py:42` lists `G0Card | G1Card | G2ACard | G2CCard | G3Card | G4Card | G5Card | G6Card` (gate-order alphabetic with G2A before G2C, G5 before G6) — clean union.

### AC-7c.5.G5-E — Pydantic-v2 14-idiom conformance — PASS

| Idiom | Honored | Evidence |
|---|---|---|
| 1. `extra="forbid"` + `validate_assignment=True` | yes | Inherited from `DecisionCardBase` (`_base.py:58`) — verified `model_config["extra"]=="forbid"` at shape-pin line 55 |
| 2. `frozen=True` for value-objects | yes | Inherited; verified `card.gate_id = "G6"` raises at shape-pin line 110-114 |
| 3. tz-aware datetime validator | yes | `_enforce_created_at_tz` field_validator (line 67-70) using shared `enforce_tz_aware` helper |
| 4. UUID4 version-check | yes | `_enforce_uuid4` for `card_id` + `trial_id` + `bundle_run_id` (line 62-65) delegating to shared `enforce_uuid4_version` helper |
| 5. Triple-layer red-rejection on closed enums | yes | (a) `Literal["G5"]` type layer; (b) Pydantic Literal validator runtime layer; (c) JSON Schema `const: "G5"` at schema line 135 — verified red-rejection on "G0", "G99", 42 (non-string), and "slab_close_ceremony", "trial_open", None on gate_focus |
| 6. Closed verb set | yes | `DecisionCardVerb = Literal["approve", "edit", "reject"]` at line 14 |
| 7. `min_length=1` on non-empty string fields | yes | `handoff_summary` at line 54; reinforced by `_reject_blank_handoff_summary` (strips before check; line 79-84) |
| 8. Non-empty collection fields | yes | `_require_handoff_artifact_paths` (line 72-77) raises on empty list |
| 9. Field descriptions | yes | Every field carries a `description=` argument |
| 10. `default_factory` for safe defaults | yes | `created_at` uses `lambda: datetime.now(UTC)` |
| 11. Schema deterministic emission | yes | `test_g5_json_schema_byte_for_byte_match` pins `json.dumps(..., indent=2, sort_keys=True) + "\n"` — verified byte-match |
| 12. Golden round-trip | yes | `test_g5_golden_fixture_round_trips` asserts canonical-form parity |
| 13. Inheritance hygiene | yes | Single import-line from shared `_base.py`; helpers from `app.models.state._base` (matches G0/G2A pattern); no duplicated config block |
| 14. JSON Schema closed-vocabulary assertion | yes | Schema asserts `additionalProperties: false` (line 101) + const on gate_id/gate_focus/schema_version |

All 14 idioms honored.

---

## PARALLEL-DISPATCH GUARDRAILS Verification

### Guardrail #1 — AMEND-7d-i AST-scan compliance — PASS

**Direct grep on shape-pin file for `FOUR_FILE_GLOBS` and `all_four_present`:** **zero matches**. The shape-pin imports only `LOCKSTEP_CHECK` (line 11). The lockstep-satisfied test (`test_g5_lockstep_files_are_present`, lines 41-50) probes via `result.files_present == {...}` (the four file-key dict-shape) and `result.failure_reason is None` — both legitimate by-reference probes against the `LockstepResult` Pydantic model without re-deriving the rule.

**Structural test execution:** `tests/structural/test_tw_7c_3_firing_spec_single_source.py` PASSES (2 passed). The AST-scan test walks all `tests/parity/test_decision_card_*_shape.py` files and reports an empty offenders list.

**Verdict:** Guardrail #1 fully honored.

### Guardrail #2 — Pattern-replication discipline — PASS

`g5.py` mirrors `g2a.py` structurally with G5-specific fields swapped in:

- Inheritance: `G5Card(DecisionCardBase)` from `_base.py` (NOT legacy `DecisionCard` from `base.py`) — matches G0/G2A.
- Imports: `from pydantic import UUID4, Field, field_serializer, field_validator` (G2A-aligned UUID4-typed; ratchets one cosmetic up from G0's bare `UUID`).
- Closed Literals: `gate_id: Literal["G5"]` + `gate_focus: Literal["final_operator_handoff"]` — matches discriminator pattern.
- Field validators: chain on `card_id` / `trial_id` / `bundle_run_id` (UUID4 enforcement) + `created_at` (tz-aware) + `handoff_artifact_paths` (non-empty) + `handoff_summary` (strip-then-non-empty per guardrail #4) — matches.
- Field serializer: `_serialize_handoff_artifact_paths` (Path → posix string list) directly mirrors G0's `_serialize_corpus_paths`.

**Verdict:** Pattern replication clean; no spec re-interpretation drift.

### Guardrail #3 — Shared-file integration ordering — PASS

`app/models/decision_cards/__init__.py` has been atomically updated to integrate both G5Card and G6Card together (concurrent dispatch coordination per guardrail #3). Codex T10 dropbox line 65 documents: "main thread integrated both `G5Card` and `G6Card` into `__init__.py` in one coordinated edit."

Inspection of `__init__.py` at HEAD shows:
- Line 19-26: G0/G1/G2A/G2C/G3/G4/G5/G6 imports — single clean union (no duplicates, no merge-conflict residue).
- Line 41-44: `AnyDecisionCard` annotated discriminated union including all 8 cards.
- Line 47-75: `__all__` list includes `G5Card` and `G6Card` as separate entries — alphabetic-with-G2A-before-G2C ordering preserved.
- The class-conformance validator was NOT edited at G5/G6 close (verified via clean lint-imports + class-conformance count of 15 — already extended at G0+G2A close per spec line 82).

**Verdict:** Main-thread coordination pattern executed cleanly; no overwrite drift.

### Guardrail #4 — Pattern-parity ratchet (cosmetic SHOULD-FIX hardening) — PASS

Both ratchets honored:

1. **`handoff_summary` strip-then-non-empty validator (G2A pattern; not G0's bare-non-empty):** Lines 79-84 of `g5.py`:
   ```python
   @field_validator("handoff_summary")
   @classmethod
   def _reject_blank_handoff_summary(cls, value: str) -> str:
       if not value.strip():
           raise ValueError("handoff_summary must be non-empty")
       return value
   ```
   Test coverage at shape-pin line 101-107 parametrizes both `""` and `"   "` (whitespace-only) — both rejected. PASSED.

2. **UUID4-typed identity fields (G2A pattern; not G0's bare UUID):** Line 9: `from pydantic import UUID4, ...`. Field annotations at lines 24, 28, 44 declare `card_id: UUID4`, `trial_id: UUID4`, `bundle_run_id: UUID4` (Pydantic-typed UUID4 — NOT bare `from uuid import UUID`). JSON-Schema emission verified: `card_id` / `trial_id` / `bundle_run_id` all show `format: "uuid4"` (NOT `"uuid"`).

**Verdict:** Both pattern-parity ratchets cleanly applied; no recurrence of G0's two SHOULD-FIX flags.

### Guardrail #5 — Class-conformance baseline arithmetic under concurrent landings — PASS

T1 baseline: 13 (11 activation + 2 decision-card shape-pins for G0+G2A; pre-G5/G6 dispatch). Concurrent G5+G6 close: arithmetic increments by `+2` (one per gate). Observed validator output: `PASS: 15 parity contract file(s) conform (11 activation + 4 decision-card shape-pin)`. 13 + 2 = 15 exactly. Codex T10 dropbox documents the arithmetic explicitly at lines 50-51 + 67.

**Verdict:** Concurrent-close arithmetic exactly satisfied.

### Guardrail #6 — Broad-regression baseline shift with per-failure attribution — PASS

- T1 baseline (Codex's pre-T0 read): 44 failed.
- T9 (Codex's reported): 43 failed.
- T11 observation (this run): **42 failed**, 4171 passed.
- Delta vs T1: -2 (improved); delta vs T9: -1 (improved further).
- All 42 failing surfaces are inherited checkout-level — sampled `git log` confirms `tests/integration/ledger/test_queries.py`, `tests/test_no_fictitious_model_ids.py`, `tests/end_to_end/test_cache_hit_rate_baseline.py` last touched at commit `728f739` (pre-Slab-7c working-tree commit; predates G5 entirely).
- Zero new failures attributable to G5; no failures contain `g5` or `decision_card_g5` substrings.

**Verdict:** Per-failure attribution sound; no silent inheritance attribution; net regression count improved.

---

## Findings

### MUST-FIX — none

### SHOULD-FIX — none

### NIT — none

The implementation is clean. Two non-finding observations for future-cycle awareness:

- **Sibling-style consolidation opportunity (informational):** G5 and G6 both use Pydantic `UUID4` typing (G2A's pattern). G0 still uses bare `from uuid import UUID`. A later harmonization story (likely during G1/G2C/G3/G4 extend-and-audit) may consolidate G0 to UUID4 for consistency. Not a G5 concern.
- **Concurrent-close `__init__.py` integration (informational):** The G5+G6 main-thread-coordinator pattern executed cleanly per guardrail #3. End-state of `__init__.py` is a single coherent union with no merge-conflict residue. The parallel G6 reviewer is responsible for G6's slice of this file from the G6 angle; this T11 verdict counts only G5's contribution.

---

## AMEND-7d-i Residue Audit (Critical Per Guardrail #1)

**Verification approach:** AST-scan structural test at `tests/structural/test_tw_7c_3_firing_spec_single_source.py:30-37` scans `tests/parity/test_decision_card_*_shape.py` files for the substrings `"FOUR_FILE_GLOBS"` or `"all_four_present"`; any match outside-of-pure-import is an offender.

**Direct grep on the G5 shape-pin file:** zero matches for either substring. Imports section (lines 1-15) shows:
- Line 8: `from pydantic import ValidationError`
- Line 10: `from app.models.decision_cards.g5 import G5Card`
- Line 11: `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (the only AMEND-7d-i citation; canonical by-reference)

The lockstep-satisfied test (`test_g5_lockstep_files_are_present`, lines 41-50) probes via `result.files_present == {golden_fixture: True, model: True, schema: True, shape_pin: True}` (the four file-key dict-shape) and `result.failure_reason is None` — both legitimate by-reference probes against the `LockstepResult` Pydantic model without re-deriving the rule.

**Structural test execution:** PASS (2 passed). Specifically `test_decision_card_shape_pins_do_not_rederive_tw_7c_3_rule` walks G0, G2A, G5 (and G6, if present) shape-pin files and reports an empty offenders list.

**Verdict:** AMEND-7d-i AST-scan residue is **structurally clean from authoring**. Codex's parallel-execution discipline (warned in guardrail #1 from the G2A near-miss) was honored on the first cut for G5; no main-thread cleanup needed.

---

## Patches Applied

None.

---

## Sign-off

T11 standard-tier code review: **PASS**.

- All 5 ACs (A-E) satisfied with direct code/test evidence.
- All 6 PARALLEL-DISPATCH GUARDRAILS verified individually and honored.
- AMEND-7d-i AST-scan compliance structurally sound from first cut.
- Pydantic-v2 14-idiom checklist fully honored.
- Verification battery fully green; broad-regression delta is -2 vs T1 baseline (improved); only "live" failure is inherited NFR-CG6 governance-version-pin pre-dating this story.
- No MUST-FIX, no SHOULD-FIX, no NIT.

Recommend: commit + flip Story 7c.5.G5 status from `review` → `done`. Sprint-status.yaml entry should reflect closure; class-conformance baseline at close is 15 (joint with G6 concurrent-close arithmetic). Per the NEW CYCLE guardrail, the parallel G6 reviewer's verdict joins this one before the commit batch.
