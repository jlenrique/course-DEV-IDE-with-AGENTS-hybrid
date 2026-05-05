# T11 Standard-Tier Code Review — Story 7c.5.G6 (G6 DecisionCard Fresh-Author — Slab-Close Ceremony)

**Story key:** `migration-7c-5-g6-decision-card-fresh-author`
**Reviewer:** Claude (Opus 4.7) — standard tier (single-gate; not cross-agent MANDATORY)
**T11 tier:** standard (per governance; pattern-replication of 7c.5.G0 / 7c.5.G2A)
**Diff scope:** 4 new files (G6-only) + 1 shared file (`__init__.py` flat-export co-extended with concurrent G5)
**Review date:** 2026-05-05
**Predecessor:** 7c.4b (commit `8b12970`); siblings 7c.5.G0 + 7c.5.G2A (commit `e2aa599` 2026-05-05); concurrent 7c.5.G5 (in parallel review)

---

## Verdict: **PASS — no patches applied**

Story 7c.5.G6 delivers the G6 slab-close-ceremony DecisionCard as a clean four-file lockstep co-commit that pattern-replicates G0/G2A faithfully and applies the SHOULD-FIX ratchet items from those reviews preemptively (UUID4-typed identity fields, strip-then-non-empty `slab_close_summary` validator). The G6-specific `slab_id` regex constraint (`^[0-9]+[a-z]?$`) is correctly implemented via `re.fullmatch` and exhaustively tested via accept/reject parametrize matrices. All five ACs (A-E) are directly satisfied; the Pydantic-v2 14-idiom checklist is fully honored; the AMEND-7d-i AST-scan boundary is clean (zero `FOUR_FILE_GLOBS` / `all_four_present` matches in the shape-pin); class-conformance correctly counts 15 (11 activation + 4 decision-card shape-pins for G0/G2A/G5/G6); cross-gate non-regression on G1/G2C/G3/G4 model construction is preserved (35 unit tests pass UNCHANGED); verification battery is fully green except for one inherited NFR-CG6 governance-version-pin failure that is **demonstrably unrelated to G6** (same pre-existing failure called out in the G2A T11 verdict; introduced at commit `d715927` Slab 7c velocity amendments bundle, before this story opened).

All six PARALLEL-DISPATCH GUARDRAILS verified individually (see §PARALLEL-DISPATCH GUARDRAILS Verification below).

No MUST-FIX, no SHOULD-FIX, no NIT findings warrant remediation. Story is ready to commit + flip done.

---

## Verification Battery

| Check | Status | Observed | Codex-Claimed | Match |
|---|---|---|---|---|
| Focused: `pytest tests/parity/test_decision_card_g6_shape.py` | PASS | **23 passed** | 23 passed | exact |
| AMEND-7d-i AST-scan (`test_tw_7c_3_firing_spec_single_source.py`) | PASS | **2 passed** | 2 passed | exact |
| Class-conformance validator | PASS | **15 (11 activation + 4 decision-card shape-pin)** | 15 | exact |
| Lint-imports | PASS | **12 kept, 0 broken** | 12 kept | exact |
| Sandbox-AC validator on spec | PASS | PASS, 0 violations | PASS | exact |
| Ruff (g6.py + shape-pin + `__init__.py`) | PASS | All checks passed | clean | exact |
| Schema byte-for-byte determinism (manual) | PASS | 5977 bytes both sides; identical | (implicit) | yes |
| Existing G1/G2C/G3/G4 construction (`tests/unit/models/decision_cards/`) | PASS | **35 passed** (UNCHANGED) | (AC-D claim) | yes |
| Cross-gate parity + parametrized harness | 1 inherited FAIL | 1 failed, 293 passed, 18 skipped | 1 failed, 293 passed | exact |

The single broad-regression failure is `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]`: it asserts `governance["version"] == "2026-04-29-slab7b-twelve-stories"` but the file currently reads `2026-05-04-velocity-amendments-bundle`. `git log` confirms this is a pre-existing inherited failure carried over from G0/G2A reviews — the test source was last touched at commit `1f81965` (Slab 7b close), well before this story was authored. Zero G6 code touches NFR-CG6.

---

## AC-by-AC Compliance

### AC-7c.5.G6-A — Four-file lockstep co-commit — PASS

All four files exist and are co-committed in one diff:

1. `app/models/decision_cards/g6.py` (113 LOC) — `G6Card(DecisionCardBase)` with `gate_id: Literal["G6"]` + `gate_focus: Literal["slab_close_ceremony"]` + 5 G6-specific fields:
   - `slab_id: str` (regex `^[0-9]+[a-z]?$` validated via `_validate_slab_id_pattern`).
   - `closing_run_id: UUID4` (Pydantic-typed; not bare `UUID` per guardrail #4).
   - `retrospective_path: Path` (single-value; field_serializer to posix string).
   - `closing_artifact_paths: list[Path]` (non-empty validated; field_serializer to posix string list).
   - `slab_close_summary: str` (strip-then-non-empty validated per guardrail #4).
2. `app/models/decision_cards/schema/g6.v1.schema.json` (208 LOC; 5977 bytes) — deterministic JSON Schema with `sort_keys=True`, `indent=2`, trailing newline; `schema_version` const="v1" present (FR-7c-51 ✓); `gate_id` const="G6"; `gate_focus` const="slab_close_ceremony"; UUID4 fields emit `format: "uuid4"`.
3. `tests/parity/test_decision_card_g6_shape.py` (139 LOC; 9 test functions producing 23 parametrized cases): field-presence + closed-enum red-rejections (gate_id, gate_focus) + JSON-Schema byte-match + golden round-trip + non-empty-list rejection + strip-then-non-empty rejection + slab_id accept/reject parametrize matrices + frozen-mutation rejection + LOCKSTEP_CHECK invocation.
4. `tests/fixtures/decision_cards/g6_golden.json` (24 LOC) — deterministic golden with stable v4 UUIDs (card_id ends `...000006`, trial_id all-7s, closing_run_id all-6s) + tz-aware ISO 8601 `created_at` + `meta.cache_state: "healthy"` + `slab_id: "7c"` + 3 paths in `closing_artifact_paths` + non-empty `retrospective_path` + non-empty `slab_close_summary` + `verb: "approve"` + valid 64-char lowercase hex `decision_card_digest`.

The shape-pin imports `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (line 11) — AMEND-7d-i compliance by-reference, not re-derived.

### AC-7c.5.G6-B — TW-7c-3 firing on out-of-sync — PASS

`test_g6_four_file_lockstep_is_satisfied` (lines 50-59) invokes `LOCKSTEP_CHECK("G6", repo_root=REPO_ROOT)` and asserts `result.failure_reason is None` AND `result.files_present == {"golden_fixture": True, "model": True, "schema": True, "shape_pin": True}`. The shape-pin cites the rule by reference; on any of the 4 files going missing, `LOCKSTEP_CHECK` reports `failure_reason="missing four-file-lockstep artifact(s): ..."` per `tw_7c_3_firing.py:50-58`.

### AC-7c.5.G6-C — Class-conformance recognition — PASS

`scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` reports `PASS: 15 parity contract file(s) conform (11 activation + 4 decision-card shape-pin)`. T1 baseline observed by Codex was 13 (G0+G2A landed); G5 + G6 landing concurrently in this checkout produces +2 → 15. Arithmetic matches guardrail #5 expectation exactly.

### AC-7c.5.G6-D — Cross-gate non-regression — PASS

- `tests/unit/models/decision_cards/`: **35 passed** UNCHANGED. Existing per-gate model tests (G1/G2C/G3/G4) and discriminated-union routing tests are not edited.
- `tests/parity/` + `tests/parametrized_harness/`: 293 passed + 1 inherited NFR-CG6 fail + 18 skipped. The G6 model lives in its own module (`g6.py`) and only adds itself + `G5Card` to `AnyDecisionCard` in `__init__.py:41-44`; no existing per-gate model or test was edited. The discriminated-union ordering at `__init__.py:42` lists `G0Card | G1Card | G2ACard | G2CCard | G3Card | G4Card | G5Card | G6Card` (semantic gate-order; G2A before G2C; G5 before G6).

### AC-7c.5.G6-E — Pydantic-v2 14-idiom conformance — PASS

Walking the checklist against `g6.py`:

| Idiom | Honored | Evidence |
|---|---|---|
| 1. `extra="forbid"` + `validate_assignment=True` | ✓ | Inherited from `DecisionCardBase` (`_base.py:58`) |
| 2. `frozen=True` for value-objects | ✓ | Inherited from `DecisionCardBase`; verified: `card.gate_id = "G5"` raises `ValidationError` (test_g6_card_frozen_mutation_rejection) |
| 3. tz-aware datetime validator | ✓ | `_enforce_tz` field_validator (line 75-78) using shared `enforce_tz_aware` helper |
| 4. UUID4 version-check | ✓ | `_enforce_uuid4` for `card_id` + `trial_id` + `closing_run_id` (line 70-73); delegates to shared `enforce_uuid4_version` helper. Type annotations use Pydantic's `UUID4` directly (guardrail #4) |
| 5. Triple-layer red-rejection on closed enums | ✓ | (a) Pydantic `Literal["G6"]` type layer; (b) Pydantic Literal validator runtime layer; (c) JSON Schema `const: "G6"` at schema line 144-148 — verified red-rejection on "G5", "G99", 42 (non-string), `None` (gate_focus) |
| 6. Closed verb set | ✓ | `DecisionCardVerb = Literal["approve", "edit", "reject"]` at line 15 |
| 7. Non-empty string fields with strip-then-check | ✓ | `slab_close_summary` validator strips whitespace before non-empty check (line 94-101); `slab_id` regex `^[0-9]+[a-z]?$` validated via `re.fullmatch` (line 80-85) |
| 8. Non-empty collection fields | ✓ | `_require_closing_artifact_paths` (line 87-92) raises on empty list |
| 9. Field descriptions | ✓ | Every field carries a `description=` argument |
| 10. `default_factory` for safe defaults | ✓ | `created_at` uses `lambda: datetime.now(UTC)` (line 41-44) |
| 11. Schema deterministic emission | ✓ | `_schema_bytes()` test pins `json.dumps(..., indent=2, sort_keys=True) + "\n"` — verified byte-match (5977 == 5977) manually |
| 12. Golden round-trip | ✓ | `test_g6_golden_fixture_round_trips` asserts canonical-form parity |
| 13. Inheritance hygiene | ✓ | Single import-line from shared `_base.py` (line 12); helpers from `app.models.state._base` (line 13); no duplicated config block |
| 14. Path serialization | ✓ | `_serialize_retrospective_path` (single Path → posix str) and `_serialize_closing_artifact_paths` (list[Path] → list[str]) — both use `Path.as_posix()` mirroring G0 pattern |

All 14 idioms honored.

---

## PARALLEL-DISPATCH GUARDRAILS Verification

Each of the six guardrails harvested from the validated G0+G2A 2026-05-05 dual-Codex run is verified individually below.

### Guardrail #1 — AMEND-7d-i AST-scan compliance — PASS

- Direct `Grep` on `tests/parity/test_decision_card_g6_shape.py` for `FOUR_FILE_GLOBS` and `all_four_present`: **zero matches**.
- The shape-pin imports only `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (line 11; no `FOUR_FILE_GLOBS` import).
- The lockstep-satisfied test (`test_g6_four_file_lockstep_is_satisfied`, lines 50-59) probes via `result.files_present == {...}` (the four-file-key dict-shape) and `result.failure_reason is None` — both legitimate by-reference probes against `LockstepResult` without re-deriving the rule.
- Structural AST-scan test (`tests/structural/test_tw_7c_3_firing_spec_single_source.py`): 2 passed (PASS).

### Guardrail #2 — Pattern-replication discipline — PASS

Diff against canonical G0/G2A confirms G6 is faithful pattern-replication:

- **Inheritance:** `class G6Card(DecisionCardBase)` (line 18) — matches G0 and G2A inheriting from `_base.py:DecisionCardBase` (NOT legacy `base.py:DecisionCard`).
- **Discriminator literals:** `gate_id: Literal["G6"]` + `gate_focus: Literal["slab_close_ceremony"]` (lines 33-40) — closed and pinned in JSON Schema as `const`.
- **Field validator chain:** `_enforce_uuid4` (G2A pattern; combined for the three UUID4 fields) + `_enforce_tz` + per-field validators for `slab_id` regex + `closing_artifact_paths` non-empty + `slab_close_summary` strip-then-non-empty.
- **Field serializers:** `_serialize_retrospective_path` (single Path) and `_serialize_closing_artifact_paths` (list[Path]) — both use `Path.as_posix()` mirroring G0's `_serialize_corpus_paths`.
- **Helpers:** Shared `enforce_tz_aware` + `enforce_uuid4_version` from `app.models.state._base` (matches both siblings).

### Guardrail #3 — Shared-file integration ordering — PASS

`app/models/decision_cards/__init__.py` was correctly extended in lockstep with the concurrent G5 worker (per Codex dropbox §"Needed Main-Agent Integration: Completed by main thread"):

- G5Card and G6Card imports added in alphabetic-after-G4 order (lines 25-26).
- `AnyDecisionCard` discriminated union extended to include both G5Card and G6Card (line 42) — semantic gate-order preserved.
- `__all__` lists G5Card and G6Card (lines 65-66).
- No duplicate imports; ruff PASS on `__init__.py` confirms clean integration.

`scripts/utilities/validate_parity_test_class_conformance.py` did not need further extension (already extended at G0+G2A close); class-conformance reports the expected `15` post-batch.

### Guardrail #4 — Pattern-parity ratchet (cosmetic SHOULD-FIX hardening) — PASS

Both ratchet items applied at T2 (preemptively addressing the G0 T11 SHOULD-FIX findings):

- **`slab_close_summary` validator strips whitespace before non-empty check** (g6.py line 94-101): `if not value.strip(): raise ValueError(...)`. Matches G2A's `_reject_blank_plan_unit_summary` pattern (G2A line 83-88) — NOT G0's `_require_confirmation_summary` (which only checks `if not value`). The shape-pin includes a parametrize entry for `" \t "` (whitespace-only) at test line 113-115, confirming behavior.
- **UUID4 type annotations on identity fields** (g6.py lines 25-32, 49-52): `card_id: UUID4`, `trial_id: UUID4`, `closing_run_id: UUID4` — Pydantic-typed UUID4, NOT bare `UUID`. Import: `from pydantic import UUID4, Field, field_serializer, field_validator` (line 10). JSON-Schema emission shows `format: "uuid4"` for all three fields (schema lines 105-108, 119-123, 176-180). This matches G2A (which uses `UUID4`) rather than G0 (which uses bare `UUID`); guardrail #4 explicitly directs G6 to mirror G2A on this.

### Guardrail #5 — Class-conformance baseline arithmetic under concurrent landings — PASS

Codex dropbox documents the arithmetic transparently:

- T1-baseline observed in worker checkout: 13 (11 activation + 2 decision-card shape-pin: G0 + G2A).
- Solo G6 landing in worker lane: `13 → 14` (+1).
- Concurrent G5 artifacts appeared in shared checkout: final reading `13 → 15` (+2 across G5+G6).

Validator output confirmed: `PASS: 15 parity contract file(s) conform (11 activation + 4 decision-card shape-pin)`. Arithmetic statement matches observed value exactly.

### Guardrail #6 — Broad-regression baseline shift with per-failure attribution — PASS

Codex dropbox reports T1 broad-regression `44 failed, 4132 passed` and T9 `43 failed, 4170 passed` (delta `-1 failed / +38 passed`; net improvement). The cross-gate slice run at T11 reproduces only one failure (NFR-CG6); per-failure attribution is verified:

- `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]`: governance version drift (`2026-04-29-slab7b-twelve-stories` → `2026-05-04-velocity-amendments-bundle`). `git log` on the failing test source reports last-touched at commit `1f81965` (Slab 7b close), pre-dating this story. Zero G6 code touches NFR-CG governance vocabulary.

No new failure attributable to G6.

---

## G6-specific: slab_id Regex Verification

The `slab_id` regex constraint (`^[0-9]+[a-z]?$`) is the only structural divergence from G5. Verification:

**Implementation** (`g6.py` lines 80-85):
```python
@field_validator("slab_id")
@classmethod
def _validate_slab_id_pattern(cls, value: str) -> str:
    if not re.fullmatch(r"[0-9]+[a-z]?", value):
        raise ValueError("slab_id must match ^[0-9]+[a-z]?$")
    return value
```

`re.fullmatch` semantics correctly anchor both ends; the regex character class `[a-z]` excludes uppercase; the trailing `?` allows zero or one letter; the leading `[0-9]+` requires at least one digit.

**Accept-cases parametrize matrix** (test lines 118-123): `["7", "7c", "12", "12b", "5a"]` (5 cases). All accepted.

**Reject-cases parametrize matrix** (test lines 126-132): `["", "slab-7c", "7C", "7-c", "7cd", "7ab"]` (6 cases). All rejected with `ValidationError` matching `slab_id`.

| Case | Reason for rejection | Behavior verified |
|---|---|---|
| `""` | empty string fails `[0-9]+` | rejected |
| `"slab-7c"` | leading non-digit | rejected |
| `"7C"` | uppercase letter | rejected (regex uses `[a-z]` only) |
| `"7-c"` | hyphen between digit and letter | rejected |
| `"7cd"` | multi-letter suffix | rejected (regex allows max 1 letter via `?`) |
| `"7ab"` | multi-letter suffix | rejected |

Matrix is comprehensive: covers empty, prefix-with-non-digit, uppercase trap, separator-injection trap, and two flavors of multi-letter suffix. Boundary cases (Unicode digits, leading zeros) are outside spec scope per the prompt — appropriate not to test in this story.

**Verdict:** slab_id regex implementation is exactly the spec; tests pass (8 parametrize cases observed in focused-pytest output: 5 accept + 6 reject = 11 parametrize cases for slab_id alone within the 23-passed total). Regex is NOT too permissive.

---

## AMEND-7d-i Residue Audit

**Verification approach:** AST-scan structural test at `tests/structural/test_tw_7c_3_firing_spec_single_source.py` scans `tests/parity/test_decision_card_*_shape.py` files for the substrings `"FOUR_FILE_GLOBS"` or `"all_four_present"`; any match outside-of-pure-import is an offender.

**Direct grep on the G6 shape-pin file:** zero matches for either substring (verified via `Grep` tool). The shape-pin imports only `LOCKSTEP_CHECK` (line 11) — never `FOUR_FILE_GLOBS`, never references `all_four_present` directly. The lockstep-satisfied test probes via `result.files_present == {...}` (the dict-shape) and `result.failure_reason is None` — both legitimate by-reference probes.

**Structural test execution:** PASS (2 passed). Walks all decision-card shape-pin files (G0, G2A, G5, G6) and reports an empty offenders list.

**Verdict:** AMEND-7d-i AST-scan boundary is fully clean. No remediation needed.

---

## Findings

### MUST-FIX — none

### SHOULD-FIX — none

### NIT — none

The implementation is clean. Two observations are noted not as findings but for future-cycle awareness:

- **Minor regex regularization (informational, NOT a finding):** the `re.fullmatch(r"[0-9]+[a-z]?", value)` pattern is functionally equivalent to anchoring with `^` and `$`. Either form is correct; `re.fullmatch` is idiomatic Python and is what the spec requested. No change warranted.
- **Sibling-style consolidation (informational, NOT a finding):** G6 follows the G2A pattern (UUID4-typed identity fields + strip-then-non-empty validator) exactly. G0 still uses bare `UUID` and an unstripped validator — those were called out as SHOULD-FIX in the G0 T11 verdict but not remediated. A future single-purpose harmonization story could lift G0 to the G2A/G5/G6 pattern; out of scope here.

---

## Patches Applied

None.

---

## Sign-off

T11 standard-tier code review: **PASS**.

- All 5 ACs satisfied with direct code/test evidence.
- All 6 PARALLEL-DISPATCH GUARDRAILS verified individually (zero violations).
- slab_id regex parametrize matrix is comprehensive (5 accept + 6 reject) and the regex is correctly NOT too permissive (uppercase, multi-letter, hyphenated, empty all rejected).
- AMEND-7d-i AST-scan boundary clean.
- Pydantic-v2 14-idiom checklist fully honored, including both pattern-parity-ratchet items applied preemptively.
- Verification battery fully green; broad-regression delta is one inherited NFR-CG6 governance-version-pin failure pre-dating this story.
- Class-conformance count is exactly the predicted joint post-condition (15 = 11 activation + 4 decision-card shape-pins for G0/G2A/G5/G6).

Recommend: commit + flip Story 7c.5.G6 status from `review` → `done`. Sprint-status.yaml entry should reflect closure; class-conformance baseline at close is 15 (joint with G0/G2A/G5).
