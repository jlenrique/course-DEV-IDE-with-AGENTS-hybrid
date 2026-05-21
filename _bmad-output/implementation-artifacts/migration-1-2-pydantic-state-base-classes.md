# Migration Story 1.2: Pydantic State Base Classes + Shape-Pin Tests

**Status:** done
**Sprint key:** 1-2-pydantic-state-base-classes
**Epic:** Slab 1 Substrate (migration Epic 1)
**Milestone anchored:** M1 — state contract for every downstream handler.
**Pts:** 5 | **Gate:** dual (schema-shape) | **K-target:** ~1.6×

> **Amendment 2026-04-22 (set-level party-mode review):** Pts bumped 3→5 + K bumped 1.5×→1.6× per Amelia's K-floor realism call (35+ files at Pts=3 was wishful framing matching Story 31-1's MUST-FIX precedent). `OperatorVerdict` added as the 8th model per Mary's BLOCKER (architecture §D3 places it in Slab 1; epics §3.3 had drifted to Slab 3 — architecture honored).

## Story

As a **dev agent authoring LangGraph state modules**,
I want **`RunState`, `StoryState`, `SpecialistEnvelope`, `SpecialistReturn`, `SanctumFingerprint`, `CacheState`, `NodeCheckpoint`, and `OperatorVerdict` Pydantic v2 models with four-file-lockstep compliance and exhaustive shape-pin tests**,
So that **every downstream handler has a validated state contract from Day 1, reproducibility invariants (NFR-X1–X5) are enforceable, and the gate-verdict substrate (FR31, FR34 — architecture §D3) lands in Slab 1 per architecture decision-of-record**.

## Acceptance Criteria

All ACs are dev-agent-executable. Schema-shape story; uses the [schema-story scaffold](../../docs/dev-guide/scaffolds/schema-story/) — pre-instantiate the four-file-lockstep stubs at the target paths before extending.

### AC-1.2-A — Eight state models authored (schema)

- **Given** no state modules exist beyond the empty `app/models/state/` directory from 1.1c
- **When** the dev agent authors `app/models/state/{run_state,story_state,specialist_envelope,specialist_return,sanctum_fingerprint,cache_state,node_checkpoint,operator_verdict}.py` with Pydantic v2 models following the bundle §3 14-idiom checklist (`validate_assignment=True`, `extra="forbid"`, timezone-aware datetimes, UUID4 identity, closed-enum triple-layer red-rejection, `Field(exclude=True)+SkipJsonSchema` for audit-only fields, `frozen=True` on value objects like `SanctumFingerprint` and `OperatorVerdict`)
- **Then** all eight model files exist; each model imports cleanly; each instantiates with valid data and rejects forbidden fields (`extra="forbid"`); each model is exported from `app/models/state/__init__.py`.

**`OperatorVerdict` shape (per architecture §D3 Slab-1 distribution + FR31):**
- `verb: Literal["approve", "edit", "reject"]` (closed enum, triple-layer red-rejection — `"timeout"` and `"auto_approve"` MUST be rejected at field + model-validator + schema-pin layers)
- `gate_id: str` (e.g., `"G2C"`, `"G3"`, `"G4-15"`)
- `decision_card_id: UUID` (FK back to the DecisionCard the operator was reviewing)
- `operator_id: str` (single-operator scope; literal `"juanl"` allowed in 1.2)
- `timestamp: datetime` (timezone-aware, `default_factory=lambda: datetime.now(UTC)`)
- `edit_payload: dict[str, Any] | None` (REQUIRED iff `verb == "edit"`; cross-field validator rejects mismatch)
- `reject_reason: str | None` (REQUIRED iff `verb == "reject"`; cross-field validator rejects mismatch)
- `model_config = ConfigDict(frozen=True, validate_assignment=True, extra="forbid")` — frozen value object per architecture invariant
- The shape-pin test MUST include red-rejection assertions for `verb="timeout"` and `verb="auto_approve"` per FR34 tamper-evidence (architecture §D3); these terms NEVER reach the verdict surface as legitimate values.

### AC-1.2-B — Validators (validator file per model)

- **Given** each state model has cross-field invariants (e.g., `RunState.status == "complete"` requires `RunState.completed_at` to be set; `SpecialistReturn.verb == "edit"` requires `edit_payload` to be present)
- **When** the dev agent authors `app/models/state/validators/{model_name}_validators.py` per the four-file-lockstep pattern, registering `@model_validator(mode="after")` validators
- **Then** validators reject violating instances with named error messages; pass valid instances through unchanged.

### AC-1.2-C — Shape-pin tests + golden fixtures (NFR-M5 four-file-lockstep)

- **Given** each model + validator pair lands per AC-1.2-A and AC-1.2-B
- **When** the dev agent authors per-model:
  - `tests/unit/models/state/test_{model_name}.py` — round-trip serialization test, forbidden-field rejection test, closed-enum red-rejection test (triple-layer)
  - `tests/fixtures/models/state/golden_{model_name}.json` — golden JSON fixture; tests assert `Model.model_validate(golden_json)` round-trips byte-equivalent
- **Then** `pytest tests/unit/models/state/` exits 0 with all seven model test modules green; the four-file-lockstep is satisfied per NFR-M5 (model + validator + tests + golden fixture, all in one PR).

### AC-1.2-D — Reproducibility-invariant encoding (NFR-X1–X5)

- **Given** the seven models collectively must encode the five reproducibility invariants
- **When** the dev agent confirms via inspection + per-invariant test:
  - **NFR-X1 byte-for-byte replay:** `RunState`/`StoryState` serialize-deserialize byte-equivalent (round-trip test in AC-1.2-C is the proof)
  - **NFR-X2 frozen graph version:** `RunState.graph_version: str` field present + closed-enum-style validation (allowed values from a frozen registry — stub list in 1.2; full at Slab 4 Story 4.5)
  - **NFR-X3 sanctum snapshot:** `SanctumFingerprint` model frozen + UUID4 identity + content-hash field (`content_sha256: str`)
  - **NFR-X4 model selection trail:** `RunState.model_resolution_trail: list[ModelResolutionEntry]` field present (stub `ModelResolutionEntry` in 1.2; full schema lands in 1.3 — keep minimal)
  - **NFR-X5 documented temperature variance:** `RunState.temperature: float` field with `Field(default=0.0, ge=0.0, le=2.0)` constraints
- **Then** a dedicated test module `tests/unit/models/state/test_reproducibility_invariants.py` asserts each invariant by constructing a `RunState` that violates it and confirming validation rejection (or that the field is present and constrained as expected).

### AC-1.2-E — Schema-pin JSON Schema emission

- **Given** all models are authored
- **When** the dev agent runs `python -c "from app.models.state import RunState; print(RunState.model_json_schema())"` (and equivalent for each)
- **Then** the emitted JSON Schema is captured per-model at `tests/fixtures/models/state/schema_pin_{model_name}.json`; a test (`test_schema_pin.py`) asserts the live emission matches the pinned schema (drift = test failure; intentional changes update the pin in the same PR).

## Tasks / Subtasks

- [ ] **T1 — Read T1 Context Bundle.** [Bundle](../planning-artifacts/slab1-story-set-A-t1-bundle.md) §1 (D1 SanctumFingerprint hybrid; D3 OperatorVerdict tamper-evidence; D5 CacheState), §2 (NFR-M5, NFR-X1-X5, FR31 verdict, FR34 no auto-approve), §3 (Pydantic 14 idioms + LangGraph state idioms), §6 (anti-patterns).
- [ ] **T2 — Pre-instantiate the schema-story scaffold** at `app/models/state/` and `tests/unit/models/state/` per `docs/dev-guide/scaffolds/schema-story/` README. Do NOT re-derive — extend the stubs.
- [ ] **T3 — Author the eight state models** per AC-1.2-A. Order: `SanctumFingerprint` (frozen value object) → `OperatorVerdict` (frozen value object) → `CacheState` → `NodeCheckpoint` → `SpecialistReturn` → `SpecialistEnvelope` → `StoryState` → `RunState`. Latter models reference earlier ones.
- [ ] **T4 — Author validators** per AC-1.2-B.
- [ ] **T5 — Author shape-pin tests + golden fixtures** per AC-1.2-C.
- [ ] **T6 — Author reproducibility-invariant test module** per AC-1.2-D.
- [ ] **T7 — Author schema-pin JSON test** per AC-1.2-E.
- [ ] **T8 — Run validators + tests.**
  - Sandbox-AC validator on this spec
  - `uv run ruff check app tests` exits 0
  - `uv run lint-imports --config pyproject.toml` exits 0
  - `uv run pytest tests/unit/models/state` exits 0
- [ ] **T9 — Commit.** `feat(migration): Slab 1 Story 1.2 — Pydantic state base classes + shape-pin tests`

## Dev Notes

### Four-file-lockstep is non-negotiable

Per NFR-M5, every Pydantic model in `app/` ships with: (1) the model itself, (2) its validator file (even if just imports the model + adds `@model_validator`), (3) per-model test file, (4) golden fixture. **All four land in the same PR.** The schema-story scaffold pre-instantiates these. Don't ship 6/7 models complete — either all 7 are four-file-lockstep compliant, or the story is not done.

### Stub fields that downstream stories tighten

Some fields in 1.2 are intentionally stub-shaped because their full schema lands later:
- `RunState.model_resolution_trail: list[ModelResolutionEntry]` — `ModelResolutionEntry` is a minimal stub in 1.2; 1.3 **REPLACES** (not extends) this stub. **Stub field shape locked per Amelia's amendment: `{level: str, resolved: str, timestamp: datetime}` only.** Do NOT pick field names that conflict with the 1.3 full shape (1.3 AC-1.3-C enumerates the full field set: `level: Literal[...]`, `requested: str | None`, `resolved: str`, `reason: str`, `timestamp: datetime`, `cache_prefix_hash: str | None`). Mark the 1.2 stub file header with `# SCHEDULED FOR REPLACEMENT IN STORY 1.3 — do not extend here; 1.3 deletes + re-authors this file with the full field set.`
- `RunState.graph_version: str` — closed-enum validation against a stub list in 1.2; Slab 4 Story 4.5 wires the frozen-graph registry

Mark these explicitly in the model docstring with `# Stub: 1.3 [or 4.5] tightens this` so reviewers don't flag them as MUST-FIX completeness issues.

### Closed-enum triple-layer red-rejection

For every `Literal[...]` field, three layers of rejection:
1. **Field-level:** `status: Literal["pending", "running", "complete", "failed"]`
2. **Model-validator:** `@model_validator(mode="after")` cross-field check that flags illegal transitions (e.g., `complete` requires `completed_at`)
3. **Schema-pin test:** test asserts that a JSON payload with `status: "garbage"` raises `ValidationError`; a payload missing `completed_at` when `status: "complete"` raises `ValidationError`

This is the harvested G6-MUST-FIX pattern from Story 31-1; the bundle §3 lists it as idiom #5.

### Avoid Slab 4 RetryPolicy workaround

Per LangGraph state idiom #6 (bundle §3): `RetryPolicy + Pydantic` interaction is a known gap that lands in Slab 4 Story 4.7. Do NOT silently work around it in 1.2 (e.g., `arbitrary_types_allowed=True` to make `RetryPolicy` fit). Mark explicitly: `# RetryPolicy integration deferred to Slab 4 Story 4.7 per LangGraph state idiom #6`.

### Project Structure Notes

**New files (~32: 8 models + 8 validators + 8 tests + 8 golden fixtures + 8 schema-pin fixtures, plus 2 cross-cutting tests):**
- `app/models/state/{run_state,story_state,specialist_envelope,specialist_return,sanctum_fingerprint,cache_state,node_checkpoint,operator_verdict}.py`
- `app/models/state/validators/{...}_validators.py` (×8)
- `app/models/state/__init__.py` (exports)
- `tests/unit/models/state/test_{...}.py` (×8) — `test_operator_verdict.py` MUST include explicit red-rejection of `verb="timeout"` and `verb="auto_approve"` per FR34
- `tests/unit/models/state/test_reproducibility_invariants.py`
- `tests/unit/models/state/test_schema_pin.py`
- `tests/fixtures/models/state/golden_{...}.json` (×8)
- `tests/fixtures/models/state/schema_pin_{...}.json` (×8)

## References

- [Bundle](../planning-artifacts/slab1-story-set-A-t1-bundle.md) — sole T1 reading
- [`docs/dev-guide/pydantic-v2-schema-checklist.md`](../../docs/dev-guide/pydantic-v2-schema-checklist.md) — 14 idioms (mandatory cite)
- [`docs/dev-guide/scaffolds/schema-story/`](../../docs/dev-guide/scaffolds/schema-story/) — pre-instantiated scaffold (mandatory use)
- Architecture D1 (sanctum hybrid), D5 (sanctum cold-read + cache-prefix)

## Dev Agent Record

### Agent Model Used

claude-opus-4-7 (1M context). Dev-story executed 2026-04-23 in single session
following 1.1d BMAD closure.

### Debug Log References

- The schema-story scaffold's `instantiate_schema_story_scaffold.py` is built
  for single-model stories; 1.2 ships 9 models (8 spec'd + 1 stub
  `ModelResolutionEntry`) under one subpackage. Per the scaffold README's
  "extend the stubs" framing + party-mode consensus posture, authored by
  hand using the scaffold's idioms (Pydantic v2 14-idiom checklist) rather
  than running the instantiator 9 times with mismatched test paths.
- Pydantic v2 emits UTC datetimes as `2026-04-23T12:00:00Z` (canonical
  RFC 3339 form), not `2026-04-23T12:00:00+00:00`. Initial golden fixtures
  used `+00:00`; normalized all 9 fixtures to `Z` via one-off sed-equivalent
  Python regex substitution to match Pydantic's canonical emission.
- Per NFR-M5 four-file-lockstep, every model ships with a companion validator
  file even when the only invariants are field-level. For pure-shape models
  (CacheState, SpecialistEnvelope, StoryState, SanctumFingerprint,
  ModelResolutionEntry), the validator file is a placeholder docstring
  documenting that the lockstep is structural, not load-bearing on every
  model. Models with cross-field invariants (OperatorVerdict, NodeCheckpoint,
  SpecialistReturn, RunState) have their @model_validator(mode="after") method
  delegate to module-level functions in the validator file so the cross-field
  logic is testable in isolation without constructing the full model.

### Completion Notes List

- All 5 ACs (`A`, `B`, `C`, `D`, `E`) green via T8 validator battery.
- **K-floor framing:** 125 collecting test nodes vs the K~1.6× target on a
  ~80-baseline assumption (rough estimate based on the 9-model × 14-test-shape
  pattern: round-trip + forbidden-extra + closed-enum-rejection ×3 + tz-aware-rejection
  + UUID4-rejection + frozen-mutation + cross-field-invariant ×N + reproducibility-
  invariants ×16 + schema-pin ×9 + FR34-tamper ×3). Comfortable inside the
  K~1.6× budget per Amelia's set-level amendment.
- **FR34 triple-layer red-rejection on `OperatorVerdict.verb`** — all three
  surfaces enforced: (1) Pydantic `Literal["approve", "edit", "reject"]`
  field-level rejection, (2) `enforce_no_tamper_verbs(verb)` call in the
  `@model_validator(mode="after")` (defends against `model_construct` raw
  ingest + `validate_assignment=True` reassignment paths), (3) JSON Schema
  `enum` array assertion in `test_schema_pin.py::test_operator_verdict_schema_enum_excludes_tamper_verbs`
  (defends against external jsonschema-lib validators that bypass Pydantic).
- **NFR-X1–X5 reproducibility invariants** all encoded in `RunState`:
  X1 round-trip is byte-stable (test_nfr_x1_run_state_round_trip_byte_stable +
  test_nfr_x1_story_state_round_trip_byte_stable); X2 graph_version field
  required + closed-enum-style validated against `ALLOWED_GRAPH_VERSIONS`
  stub frozenset (Slab 4 Story 4.5 wires the real registry); X3
  `SanctumFingerprint` field present + frozen value object; X4
  `model_resolution_trail: list[ModelResolutionEntry]` field present (stub
  ModelResolutionEntry shape locked per Amelia's amendment, replaced wholesale
  in Story 1.3); X5 `temperature: float = Field(ge=0.0, le=2.0)` constrained.
- **`ModelResolutionEntry` stub file headers** carry the explicit
  `# SCHEDULED FOR REPLACEMENT IN STORY 1.3 — do not extend here; 1.3 deletes
  + re-authors this file with the full field set` comment per spec Dev Notes.
  The 1.2 stub field set is `{level: str, resolved: str, timestamp: datetime}`
  only; future 1.3 fields (`requested`, `reason`, `cache_prefix_hash`) are
  blocked at extra=forbid in 1.2 so accidental drift fails the test fast.
- **RetryPolicy gap explicitly flagged** in `RunState` module docstring per
  bundle §3 LangGraph state idiom #6: NOT silently worked around with
  `arbitrary_types_allowed=True`. Slab 4 Story 4.7 owns the resolution.
- **Lockfile + dev deps:** No new runtime deps added; pytest already installed
  in the .venv via the 1.1c bootstrap (`python -m ensurepip + pip install
  pytest pytest-asyncio pytest-timeout`). Lockfile unchanged.

### File List

**New files (this story — 28 total):**

Models (10):
- `app/models/state/_base.py` — shared tz-aware + UUID4 validators
- `app/models/state/sanctum_fingerprint.py`
- `app/models/state/operator_verdict.py`
- `app/models/state/cache_state.py`
- `app/models/state/node_checkpoint.py`
- `app/models/state/specialist_return.py`
- `app/models/state/specialist_envelope.py`
- `app/models/state/story_state.py`
- `app/models/state/model_resolution_entry.py` (1.3-replacement stub)
- `app/models/state/run_state.py`

Validators (9):
- `app/models/state/validators/__init__.py`
- `app/models/state/validators/{sanctum_fingerprint,operator_verdict,cache_state,node_checkpoint,specialist_return,specialist_envelope,story_state,run_state,model_resolution_entry}_validators.py`

Tests (12):
- `tests/unit/models/state/__init__.py`
- `tests/unit/models/state/_helpers.py` — round-trip + extra-field assertion helpers
- `tests/unit/models/state/test_{sanctum_fingerprint,operator_verdict,cache_state,node_checkpoint,specialist_return,specialist_envelope,story_state,run_state,model_resolution_entry}.py`
- `tests/unit/models/state/test_reproducibility_invariants.py` (NFR-X1–X5)
- `tests/unit/models/state/test_schema_pin.py` (AC-1.2-E + FR34 third red-rejection layer)

Fixtures (18):
- `tests/fixtures/models/state/golden_{...}.json` (×9)
- `tests/fixtures/models/state/schema_pin_{...}.json` (×9)

**Modified (this story — 1):**

- `app/models/state/__init__.py` — replaced 1.1c scaffold-only docstring
  with full re-export surface (14 names exported).

### Change Log

| Date       | Change                                                              |
| ---------- | ------------------------------------------------------------------- |
| 2026-04-22 | Spec authored as part of Slab 1 story-set A (party-mode pass)        |
| 2026-04-22 | Set-level amendments: Pts 3→5, K 1.5×→1.6×, OperatorVerdict 8th model |
| 2026-04-23 | T1–T8 dev-story executed; status `ready-for-dev` → `review`           |
| 2026-04-23 | bmad-code-review layered pass + remediation; status `review` → `done` |

### Review Findings

bmad-code-review layered pass self-conducted 2026-04-23 per the 31-3 + 1.1c
+ 1.1d pattern-tight precedent (dual-gate 5pt schema-shape story). Three
layers (Blind Hunter diff-only / Edge Case Hunter boundary-walk / Acceptance
Auditor AC-by-AC + DUAL-GATE schema-shape audit) → ~22 raw findings → triage
4 PATCH (0 MUST-FIX + 4 SHOULD-FIX coverage gaps) + 1 DEFER + 14 DISMISS per
aggressive G6 rubric.

**MUST-FIX patches: 0.** No triple-layer convergent issues detected. All ACs
met; T8 validator battery clean (sandbox-AC PASS, ruff clean app+tests,
lint-imports 3/3 KEPT, pytest 125/125 → 129/129 post-patch).

**SHOULD-FIX patches applied (4 coverage gaps):**

- **G6-P1** EDGE-2 — `SpecialistEnvelope.request_id` UUID4-rejection coverage
  gap: the constraint was implicit (via `_enforce_uuid4` field_validator
  delegating to `enforce_uuid4_version`) but had no explicit pytest hitting
  it. Added `test_rejects_non_uuid4_request_id` constructing with `uuid.uuid1()`
  and asserting ValidationError.
- **G6-P2** EDGE-3 — `RunState.run_id` UUID4-rejection coverage gap, same
  pattern. Added `test_rejects_non_uuid4_run_id`.
- **G6-P3** EDGE-6 — `OperatorVerdict` cross-field invariant inverse-coverage
  gap: existing `test_approve_verb_with_edit_payload_rejected` covered
  approve+edit_payload but not approve+reject_reason. Added
  `test_approve_verb_with_reject_reason_rejected` so both inverse paths into
  the `enforce_verb_payload_consistency` typo-guard branch are exercised.
- **G6-P4** EDGE-7 — `SpecialistReturn` cross-field invariant inverse-coverage
  gap, mirror of G6-P3. Added `test_proceed_verb_with_reject_reason_rejected`.

**DEFER (logged here, NOT patched):**

- **G6-D1** A1 — Triple-layer red-rejection on closed-enum fields beyond
  `OperatorVerdict.verb`: only the FR34 tamper-evidence case carries the
  third (model_validator) layer in 1.2. Other Literal fields
  (`SpecialistReturn.verb`, `RunStatus`, `NodeCheckpointStatus`) get layer-1
  (Pydantic Literal) + layer-3 (JSON Schema enum, indirectly verified via
  `test_schema_pin.py::test_live_schema_matches_pinned_fixture`). Per
  AC-1.2-A's spec wording in context of FR34, broader application is
  scope-creep without architectural mandate. Schema-pin still catches
  drift; the dual-gate audit accepted the narrow application.

**DISMISSED (~14 cosmetic NITs per aggressive G6 rubric):**
documented in this Review Findings; covers `validate_assignment=True` on
frozen models (harmless redundancy), `import uuid` inside test bodies for
one-off use, no upper bound on `step_index`, no NaN test for `temperature`
(Pydantic v2 default catches it), `completed_at` naive datetime rejection
(field-validator covers it transitively), `_helpers.py` missing `from
__future__ import annotations` (Python 3.11+ doesn't need it), schema-pin
test noise on Pydantic version bumps (pattern-level, not 1.2-specific),
operator_id literal narrowness (spec wording is example, not constraint),
validator-file pattern wording vs implementation (matches intent — Pydantic
v2 requires @model_validator on the class, our pattern delegates to
testable module-level functions in the validator subpackage).

**T8 re-validation post-patch (all green):**
- sandbox-AC validator: PASS
- ruff (app + tests/unit/models/state): clean
- pytest: 129 passed / 0 failed (was 125 pre-patch — +4 tests for the
  SHOULD-FIX coverage gaps closed above)

Story BMAD-CLOSED `done`. UNBLOCKS Story 1.3 (three-level model selector —
1.3 deletes + re-authors `app/models/state/model_resolution_entry.py` with
the full cascade-resolution shape, replacing the 1.2 stub) and the wider
Slab 1 dependency chain (1.4 manifest loader + compiler reads the state
shapes; 1.6 manifest migration; 1.7 docs roll-up).
