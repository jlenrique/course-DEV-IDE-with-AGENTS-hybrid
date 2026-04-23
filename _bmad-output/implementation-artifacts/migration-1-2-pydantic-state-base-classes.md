# Migration Story 1.2: Pydantic State Base Classes + Shape-Pin Tests

**Status:** ready-for-dev
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

_(placeholder for dev agent + reviewer fill-in)_
