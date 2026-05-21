# T11 Standard-Tier Code Review — Story 7c.5.G2A (G2A DecisionCard Fresh-Author)

**Story key:** `migration-7c-5-g2a-decision-card-fresh-author`
**Reviewer:** Claude (Opus 4.7) — standard tier (single-gate; not cross-agent MANDATORY)
**T11 tier:** standard (per governance; pattern-replication of 7c.5.G0)
**Diff scope:** 4 new files (G2A-only) + 3 shared files (G0+G2A flat-export + validator extension)
**Review date:** 2026-05-05
**Predecessor:** 7c.4b (commit `8b12970`); sibling 7c.5.G0 (concurrent close)

---

## Verdict: **PASS — no patches applied**

Story 7c.5.G2A delivers the G2A plan-unit-ratification DecisionCard as a clean four-file lockstep co-commit. All five ACs (A-E) are directly satisfied by code/tests; the Pydantic-v2 14-idiom checklist is honored across `g2a.py`; the AMEND-7d-i AST-scan compliance is **structurally sound** (the Codex-flagged near-miss is fully cleaned up — see §AMEND-7d-i Residue Audit below); class-conformance correctly counts 13 (11 activation + 2 decision-card shape-pins for G0+G2A); cross-gate non-regression on G1/G2C/G3/G4 model construction is preserved; verification battery is fully green except for one pre-existing inherited NFR-CG6 governance-version-pin failure that is **demonstrably unrelated to G2A** (introduced at commit `d715927` two days before this story opened).

No MUST-FIX, no SHOULD-FIX, no NIT findings warrant remediation. Story is ready to commit + flip done.

---

## Verification Battery

| Check | Status | Observed | Codex-Claimed | Match |
|---|---|---|---|---|
| Focused: `pytest tests/parity/test_decision_card_g2a_shape.py` | PASS | **11 passed** | (combined with G0+TW-7c-3: "23 passed") | yes |
| AMEND-7d-i AST-scan (`test_tw_7c_3_firing_spec_single_source.py`) | PASS | **2 passed** | (implicit) | yes |
| Class-conformance validator | PASS | **13 (11 activation + 2 decision-card shape-pin)** | 13 | exact |
| Lint-imports | PASS | **12 kept, 0 broken** | 12 kept | exact |
| Sandbox-AC validator on spec | PASS | PASS, 0 violations | PASS | exact |
| Ruff (g2a.py + shape-pin) | PASS | All checks passed | clean | exact |
| Schema byte-for-byte determinism (manual) | PASS | 5887 bytes both sides; identical | (implicit) | yes |
| Golden round-trip (manual) | PASS | canonical-form match | (implicit) | yes |
| Existing G1/G2C/G3/G4 construction (`tests/unit/models/decision_cards/`) | PASS | **35 passed** (UNCHANGED) | (AC-D claim) | yes |
| Broad parity+parametrized regression | 1 inherited FAIL | 256 passed, 18 skipped, 1 failed | (claims inherited only) | yes |

The single broad-regression failure is `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]`: it asserts `governance["version"] == "2026-04-29-slab7b-twelve-stories"` but the file currently reads `2026-05-04-velocity-amendments-bundle`. `git log` confirms this version bump landed at commit `d715927` (Slab 7c velocity amendments bundle) — that is, **before this story was authored**, and is the documented inherited checkout-level baseline. Zero G2A code touches NFR-CG6.

---

## AC-by-AC Compliance

### AC-7c.5.G2A-A — Four-file lockstep co-commit — PASS

All four files exist and are co-committed in one diff:

1. `app/models/decision_cards/g2a.py` (101 LOC) — `G2ACard(DecisionCardBase)` with `gate_id: Literal["G2A"]` + `gate_focus: Literal["plan_unit_ratification"]` + 4 G2A-specific fields (`plan_unit_id: UUID4`, `plan_unit_summary: str` with `min_length=1` + non-blank validator, `ratification_evidence: list[dict[str, Any]]` with `min_length=1` + non-empty validator, `prior_unit_ids: list[UUID4]`).
2. `app/models/decision_cards/schema/g2a.v1.schema.json` (205 LOC; 5887 bytes) — deterministic JSON Schema with `sort_keys=True`, indent=2, trailing newline; `schema_version` const="v1" present at line 169-175 (FR-7c-51 ✓).
3. `tests/parity/test_decision_card_g2a_shape.py` (114 LOC) — 11-test shape-pin (field-presence + closed-enum red-rejections + JSON-Schema byte-match + golden round-trip + LOCKSTEP_CHECK invocation).
4. `tests/fixtures/decision_cards/g2a_golden.json` (44 LOC) — deterministic golden with stable v4 UUIDs + tz-aware ISO-8601 `created_at` + `meta.cache_state: "healthy"` + 1 ratification-evidence item + 2 prior_unit_ids.

The shape-pin imports `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (line 11) — AMEND-7d-i compliance by-reference, not re-derived.

### AC-7c.5.G2A-B — TW-7c-3 firing on out-of-sync — PASS

`test_g2a_four_file_lockstep_is_satisfied` invokes `LOCKSTEP_CHECK("G2A", repo_root=REPO_ROOT)` and asserts `result.failure_reason is None` AND `result.files_present` returns the canonical 4-key dict all-True. The shape-pin cites the rule by reference; on any of the 4 files going missing, `LOCKSTEP_CHECK` would report `failure_reason="missing four-file-lockstep artifact(s): ..."` — verified by inspecting `app/parity/contracts/tw_7c_3_firing.py:50-58`.

### AC-7c.5.G2A-C — Class-conformance recognition — PASS

`scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` reports `PASS: 13 parity contract file(s) conform (11 activation + 2 decision-card shape-pin)`. Spec said "12 if isolated, 13 if post-G0; both landed concurrently, so 13 is correct" — observed exactly. The validator extension at lines 207-213, 414-442 correctly counts G2A's shape-pin as a decision-card shape-pin (G2A-specific tokens: import statement matches `decision_cards.g2a` per line 434 check; required tokens `LOCKSTEP_CHECK`, `model_json_schema`, `model_validate`, `model_dump`, `ValidationError`, `_golden.json`, `.v1.schema.json` all present per line 119-129).

### AC-7c.5.G2A-D — Cross-gate non-regression — PASS

`tests/unit/models/decision_cards/`: **35 passed** UNCHANGED. The relevant test files (`test_per_gate_strict.py`, `test_manifest_dotted_reference_resolver.py`, `test_discriminated_union_routing.py`) all reference `G1Card / G2CCard / G3Card / G4Card` and pass without modification. The G2A model lives in its own module (`g2a.py`) and only adds itself to the `AnyDecisionCard` discriminated union in `__init__.py` line 39-43; no existing per-gate model or test was edited.

### AC-7c.5.G2A-E — Pydantic-v2 14-idiom conformance — PASS

Walking the checklist against `g2a.py`:

| Idiom | Honored | Evidence |
|---|---|---|
| 1. `extra="forbid"` + `validate_assignment=True` | ✓ | Inherited from `DecisionCardBase` (`_base.py:58`) |
| 2. `frozen=True` for value-objects | ✓ | Inherited from `DecisionCardBase`; verified: `card.verb = "reject"` raises `ValidationError` |
| 3. tz-aware datetime validator | ✓ | `_enforce_created_at_tz` field_validator (line 78-81) using shared `enforce_tz_aware` helper |
| 4. UUID4 version-check | ✓ | `_enforce_uuid4` for `card_id` + `trial_id` + `plan_unit_id` (line 66-69) + `_enforce_prior_unit_ids_uuid4` for the list (line 71-76); both delegate to shared `enforce_uuid4_version` helper |
| 5. Triple-layer red-rejection on closed enums | ✓ | (a) Pydantic `Literal["G2A"]` type layer; (b) Pydantic Literal validator runtime layer; (c) JSON Schema `const: "G2A"` at schema line 129 — verified red-rejection on "G1", "G99", 42 (non-string), `None` (gate_focus) |
| 6. Closed verb set | ✓ | `DecisionCardVerb = Literal["approve", "edit", "reject"]` at line 13; verified red-rejection on "maybe" |
| 7. `min_length=1` on non-empty string fields | ✓ | `plan_unit_summary` at line 49; reinforced by `_reject_blank_plan_unit_summary` for whitespace-only inputs (line 83-88) |
| 8. `min_length=1` on non-empty collection fields | ✓ | `ratification_evidence` at line 54; reinforced by `_reject_empty_ratification_evidence` (line 90-98) |
| 9. Field descriptions | ✓ | Every field carries a `description=` argument |
| 10. `default_factory` for safe defaults | ✓ | `created_at` uses `lambda: datetime.now(UTC)`; `prior_unit_ids` uses `default_factory=list` |
| 11. Schema deterministic emission | ✓ | `_schema_bytes()` test pins `json.dumps(..., indent=2, sort_keys=True) + "\n"` — verified byte-match (5887 == 5887) |
| 12. Golden round-trip | ✓ | `test_g2a_golden_fixture_round_trips` asserts canonical form parity |
| 13. Inheritance hygiene | ✓ | Single import-line from shared `_base.py`; helpers from `app.models.state._base` (matches G0 pattern); no duplicated config block |
| 14. JSON Schema closed-vocabulary assertion | ✓ | `test_g2a_json_schema_declares_version_and_closed_focus` pins `const`s and `additionalProperties: False` |

All 14 idioms honored.

---

## Findings

### MUST-FIX — none

### SHOULD-FIX — none

### NIT — none

The implementation is clean. Two observations are noted not as findings but for future-cycle awareness:

- **Sibling-style divergence (informational, NOT a finding):** G0 uses `from uuid import UUID; field: UUID` while G2A uses Pydantic's `UUID4` directly. Both ultimately enforce v4 via the shared `enforce_uuid4_version` helper. The `UUID4` import is more explicit at the type-system layer and arguably cleaner. No inconsistency that warrants change in this story; later G1/G2C/G3/G4 extend-and-audit stories may consolidate.
- **Shared `__init__.py` and validator-extension files are co-modified by G0 + G2A** (concurrent fresh-author stories). This review counts G2A's contribution but does not double-count the G0-shared portions; the parallel G0 reviewer is responsible for those lines from the G0 angle. End-state of both files is internally consistent: discriminated-union ordering at `__init__.py:40` lists G0 → G1 → G2A → G2C → G3 → G4 (alphabetic-with-G1-before-G2A — semantically gate-order); validator class-conformance count of 13 is the joint post-condition.

---

## AMEND-7d-i Residue Audit (Critical Concern from Codex Dropbox)

**Concern source:** Codex's `_codex-handoff/7c-5-g2a.ready-for-review.md` line 16: "The G2A worker produced the initial model/test/fixture; the main thread completed the missing schema, **removed an AMEND-7d-i AST-scan violation**, integrated shared exports, and ran verification."

**Verification approach:** AST-scan structural test at `tests/structural/test_tw_7c_3_firing_spec_single_source.py:30-37` scans `tests/parity/test_decision_card_*_shape.py` files for the substrings `"FOUR_FILE_GLOBS"` or `"all_four_present"`; any match outside-of-pure-import is an offender.

**Direct grep on the G2A shape-pin file:** zero matches for either substring. The shape-pin imports only `LOCKSTEP_CHECK` (line 11) — never `FOUR_FILE_GLOBS`, never references `all_four_present` directly. The lockstep-satisfied test (`test_g2a_four_file_lockstep_is_satisfied`, line 46-55) probes via `result.files_present == {...}` (the four file-key dict-shape) and `result.failure_reason is None` — both legitimate by-reference probes against the `LockstepResult` dataclass without re-deriving the rule.

**Structural test execution:** PASS (2 passed). Specifically `test_decision_card_shape_pins_do_not_rederive_tw_7c_3_rule` walks both G0 and G2A shape-pin files and reports an empty offenders list.

**Verdict:** AMEND-7d-i AST-scan residue is **fully resolved**. The Codex parallel-execution near-miss was caught and cleaned by the main thread before T10. No remediation needed at T11.

---

## Patches Applied

None.

---

## Sign-off

T11 standard-tier code review: **PASS**.

- All 5 ACs satisfied with direct code/test evidence.
- AMEND-7d-i AST-scan compliance structurally sound; near-miss resolved upstream.
- Pydantic-v2 14-idiom checklist fully honored.
- Verification battery fully green; broad-regression delta is one inherited NFR-CG6 governance-version-pin failure pre-dating this story.
- No MUST-FIX, no SHOULD-FIX, no NIT.

Recommend: commit + flip Story 7c.5.G2A status from `review` → `done`. Sprint-status.yaml entry should reflect closure; class-conformance baseline at close is 13 (joint with G0).
