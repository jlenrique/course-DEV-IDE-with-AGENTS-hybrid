# T11 Standard Code Review — Story 7c.5.G0 (G0 DecisionCard Fresh-Author)

**Story key:** `migration-7c-5-g0-decision-card-fresh-author`
**Reviewer:** Claude (Opus 4.7) — T11 standard tier (single-gate; fresh-author)
**Diff size:** ~400 LOC G0-only (4 new files: 91 model + 194 schema + 92 shape-pin + 23 golden); ~3 modified shared files (co-owned with sibling 7c.5.G2A)
**Review date:** 2026-05-05

## Verdict: PASS

The G0 four-file lockstep set is correctly authored against the 7c.4b `DecisionCardBase` substrate, cites `LOCKSTEP_CHECK` by reference per AMEND-7d-i (no rederivation of `FOUR_FILE_GLOBS`), and adds a structurally well-formed shape-pin file that the extended class-conformance validator recognizes alongside G2A. All five focused-spec ACs (A–E) verify. Schema-emission and golden-fixture round-trips are byte-for-byte deterministic. §02A regression (AC-D) passes UNCHANGED. No MUST-FIX defects. Two minor non-blocking findings noted below.

Sibling 7c.5.G2A reviewer owns the modified shared files (`__init__.py`, validator extension, validator test extension); this verdict notes them as in-scope but defers cross-cuts to that reviewer.

## Verification Battery

| Check | Status | Evidence |
|---|---|---|
| Focused G0 shape-pin | PASS | `10 passed` (Codex claimed 10; observed 10 with 2 module-level @pytest.mark.parametrize fan-outs + 5 explicit test functions = 10 collected) |
| `tests/parity/` + `tests/parametrized_harness/` | PASS-modulo-inherited | `256 passed, 18 skipped, 1 failed` — sole failure is `test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]` checking governance JSON pinned at `2026-04-29-slab7b-twelve-stories` vs current `2026-05-04-velocity-amendments-bundle`; **inherited checkout-level surface, NOT G0-introduced** |
| §02A regression (AC-D) | PASS | `15 passed` matches Codex claim |
| AMEND-7d-i AST-scan structural test | PASS | `2 passed` — `test_decision_card_shape_pins_do_not_rederive_tw_7c_3_rule` confirms G0 does not contain `FOUR_FILE_GLOBS` or `all_four_present` literals |
| Class-conformance | PASS | `PASS: 13 parity contract file(s) conform (11 activation + 2 decision-card shape-pin)` — matches Codex claim; G0 contributes +1 of the +2 delta |
| Class-conformance validator extension test | PASS | `3 passed` — runtime-IDs frozenset still 18; G0 lockstep tmp-path probe fires TW-7c-3 cleanly |
| Lint-imports | PASS | `Contracts: 12 kept, 0 broken` (UNCHANGED) |
| Sandbox-AC validator | PASS | `PASS — no sandbox-AC violations across 1 story file(s)` |
| Ruff (in-scope files) | PASS | `All checks passed!` |
| Schema-emission determinism | PASS | In-Python byte comparison: on-disk schema == `json.dumps(G0Card.model_json_schema(), indent=2, sort_keys=True) + "\n"` (5581 chars match) |
| Golden-fixture round-trip determinism | PASS | In-Python byte comparison: source 825 chars == canonical-dump 825 chars; perfect round-trip |
| Discriminated-union dispatch | PASS | `AnyDecisionCardAdapter.validate_python(g0_golden)` returns `G0Card` with `gate_id == "G0"` |

## AC Compliance Verification

### AC-7c.5.G0-A — Four-file lockstep co-commit — PASS

All four files present, co-committed, structurally correct:
1. `app/models/decision_cards/g0.py` — `G0Card(DecisionCardBase)` with `Literal["G0"]` discriminator (line 33), `Literal["trial_open"]` closed marker (line 37), and the three G0-specific fields: `corpus_paths_confirmed: list[Path]` non-empty (lines 45–48 + validator lines 72–77), `directive_run_id: UUID` UUID4-enforced (lines 49–51 + validator lines 62–65), `corpus_confirmation_summary: str` non-empty (lines 53–56 + validator lines 79–84).
2. `app/models/decision_cards/schema/g0.v1.schema.json` — emits `additionalProperties: false`, `const: "G0"` for `gate_id`, `const: "trial_open"` for `gate_focus`, `const: "v1"` for `schema_version`. Required array correctly excludes the defaulted-Literal fields.
3. `tests/parity/test_decision_card_g0_shape.py` — 7 test specs (10 collected after parametrize fan-out): `test_g0_card_has_required_fields` (line 26), gate_id red-rejection on `["G1", "G99", 42]` (line 42), gate_focus red-rejection on `["directive_ratification", None]` (line 51), empty-list red-rejection (line 60), schema byte-equality (line 68), golden round-trip (line 74), LOCKSTEP_CHECK-cite-by-reference (line 83).
4. `tests/fixtures/decision_cards/g0_golden.json` — UUID4-shape `card_id`/`trial_id`/`directive_run_id`, tz-aware `created_at: "2026-05-05T00:00:00Z"`, `meta.cache_state: "healthy"`, all required fields populated, schema_version="v1".

The shape-pin imports `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (line 11) — does NOT re-derive.

### AC-7c.5.G0-B — TW-7c-3 firing on out-of-sync — PASS

`tests/parity/test_class_conformance_validator_extension.py::test_lockstep_check_reports_missing_g0_four_file_set` exercises this directly: an empty `tmp_path` repo_root yields `result.all_four_present is False` with all four file types in `files_present` and a populated `failure_reason`. AMEND-7d-i AST-scan structural test `tests/structural/test_tw_7c_3_firing_spec_single_source.py::test_decision_card_shape_pins_do_not_rederive_tw_7c_3_rule` confirms G0 does not pull `FOUR_FILE_GLOBS` into local scope.

### AC-7c.5.G0-C — Class-conformance recognition — PASS

The validator (`scripts/utilities/validate_parity_test_class_conformance.py`) was extended in this batch to count per-gate DecisionCard shape-pins separately from activation contracts. The output message format is:

> `PASS: 13 parity contract file(s) conform (11 activation + 2 decision-card shape-pin)`

Spec said "12 (was 11; +1 for new G0 shape-pin)"; observed is 13 (= 11 activation + G0 + G2A). The +1 G0 contribution is structurally isolated (the `_iter_decision_card_shape_files` glob picks up `test_decision_card_g0_shape.py` independently), so AC-C's intent (G0 is recognized as a structurally well-formed shape-pin) is satisfied. The validator's `_validate_decision_card_shape_pin` enforces: gate_id is in canonical runtime set, all 7 `DECISION_CARD_SHAPE_REQUIRED_TOKENS` are present, and the per-gate model module is imported by name.

### AC-7c.5.G0-D — §02A schema-stability non-regression — PASS

`tests/schemas/operator_verdict/test_section_02a_shape.py` reports `15 passed` with no changes to that file. The G0Card per-gate addition does not regress §02A's verdict-schema. The §02A poll-surface emits `Section02AOperatorVerdict` (not `G0Card`); G0 is the inbound DecisionCard payload type, distinct from the outbound verdict shape. Boundary is clean.

### AC-7c.5.G0-E — Pydantic-v2 14-idiom conformance — PASS

Per-idiom audit of `app/models/decision_cards/g0.py`:

| # | Idiom | G0 Status | Evidence |
|---|---|---|---|
| 1 | `extra="forbid"` + `validate_assignment=True` | PASS | Inherited from `DecisionCardBase.model_config` (`_base.py:58`); also `frozen=True` (immutable card) |
| 2 | tz-aware datetime | PASS | `enforce_tz_aware` validator at lines 67–70 ; default factory `datetime.now(UTC)` at line 42 |
| 3 | UUID4 enforcement | PASS | `enforce_uuid4_version` validator at lines 62–65 (covers card_id, trial_id, directive_run_id). See SHOULD-FIX #2 below for the `UUID` vs `UUID4` typing nuance |
| 4 | Closed-enum triple-rejection | PASS | `Literal["G0"]` + `Literal["trial_open"]` + `Literal["v1"]` + `DecisionCardVerb` Literal — Pydantic validator surface; JSON Schema emits `const`/`enum`; round-trip exercises both |
| 5 | Internal audit fields | N/A | G0Card has no audit-only fields |
| 6 | Free-text verbatim | Partial | `corpus_confirmation_summary` is a verbatim operator string but the validator rejects empty (per spec). See SHOULD-FIX #1 for whitespace-only nuance |
| 7 | Revision monotonicity | N/A | DecisionCards are immutable (`frozen=True`); no revision field |
| 8 | Per-family shape-pin | PASS | `tests/parity/test_decision_card_g0_shape.py` is its own file |
| 9 | Required-vs-optional bidirectional parity | PASS | Schema `required` array contains the 8 non-defaulted fields; `gate_id`/`gate_focus`/`schema_version`/`created_at` correctly excluded (they have defaults) |
| 10 | Digest determinism | Inherited | `decision_card_digest` validator on base enforces lowercase sha256 hex |
| 11 | No-leak grep | N/A | G0 fields don't traffic in intake/orchestrator vocabulary |
| 12 | Warn-once dedup | N/A | No warning paths in G0 |
| 13 | State-machine bypass guard | N/A | G0 has no internal state machine |
| 14 | `additionalProperties: false` round-trip | PASS | Emitted schema lines 14, 47, 101 — all object levels carry `additionalProperties: false` |

## Findings

### MUST-FIX
None.

### SHOULD-FIX
1. **`corpus_confirmation_summary` accepts whitespace-only strings.** The validator at `app/models/decision_cards/g0.py:79–84` checks `if not value` (rejects empty string only). Sibling G2A uses `if not value.strip()` for `plan_unit_summary` (`app/models/decision_cards/g2a.py:83–88`). Probe confirmed `G0Card.model_validate({..., "corpus_confirmation_summary": "   "})` accepts. Spec text says "non-empty" — strict reading allows this; pattern-parity with G2A would tighten it. Non-blocking; does not violate AC text. Documented for sibling-pattern alignment in a future polish pass.

2. **`UUID` vs `UUID4` typing inconsistency vs G2A.** `g0.py:8` imports bare `from uuid import UUID` and types fields as `UUID`; G2A uses `from pydantic import UUID4`. Both rely on `enforce_uuid4_version` for the runtime version-4 contract (correct). However, the emitted JSON Schema differs: G0 emits `"format": "uuid"` whereas G2A emits `"format": "uuid4"`. The runtime guarantee is identical (validator catches non-v4 UUIDs), but a downstream consumer reading only the JSON Schema sees less specificity. Idiom #3 in the Pydantic-v2 checklist describes the validator approach (which G0 satisfies); the `UUID4`-typed approach gives stronger schema-level signal. Non-blocking; the byte-frozen schema file matches the model emission so AC-A's byte-equality holds.

### NITs / DISMISSED
- The `field_serializer` for `corpus_paths_confirmed` (lines 86–88) using `path.as_posix()` is the correct Windows-portability fix, as noted in the Codex dropbox. Round-trip determinism verified with the golden fixture and a probe with synthetic backslash inputs.
- The `_canonical_json` helper in the shape-pin (line 22) appends `"\n"` to mirror Python's print/file-write trailing newline; without this the byte comparison would fail. Correct.
- Field descriptions present on every field — checklist idiom satisfied.
- `decision_card_digest` golden value `"a"*64` (line 9 of golden fixture) is a synthetic placeholder that passes the `[0-9a-f]{64}` regex on the base. Acceptable for fixture purposes.

## Patches Applied
None. Both findings are SHOULD-FIX-or-lower; neither blocks close. Operator may elect to address #1 (whitespace strip) in a follow-up touch-up alongside other Slab 7c gate-family alignments, or document the looser semantics if intentional.

## Sign-off

T11 standard review complete. Recommend: **COMMIT + FLIP DONE**.

The four-file lockstep set is structurally sound, AMEND-7d-i compliant, and verifies cleanly against all 5 ACs. Findings are minor pattern-parity items that are safe to defer.
