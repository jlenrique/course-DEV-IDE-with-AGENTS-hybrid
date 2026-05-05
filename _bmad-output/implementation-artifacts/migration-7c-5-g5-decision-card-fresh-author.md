# Migration Story 7c.5.G5: G5 DecisionCard Fresh-Author (Final Operator Handoff)

**Status:** ready-for-dev *(spec authored 2026-05-05 lookahead_tier=1; predecessor 7c.4b CLOSED at `8b12970`; sibling fresh-authors 7c.5.G0 + 7c.5.G2A landed at `review` 2026-05-05 — T1-T10 complete; T11 pending. **HELD-RELEASED:** sibling pattern artifacts NOW ON DISK at `app/models/decision_cards/g0.py` + `tests/parity/test_decision_card_g0_shape.py` + `tests/fixtures/decision_cards/g0_golden.json` (G2A counterparts also on disk). Per operator-override pattern, Codex MAY dispatch pre-T11-close.)*
**Sprint key:** `migration-7c-5-g5-decision-card-fresh-author`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 1
**K-target:** 1.2× (pattern-replication of G0/G2A; identical four-file structure; no new contract decisions)
**Estimated LOC:** ~250 (4 new files: ~70 model + ~50 schema + ~110 shape-pin + ~40 golden)
**Gate-mode:** single-gate
**Cross-agent review:** false (per governance JSON)
**R-tier:** R2
**T11-tier:** standard
**Lookahead-tier:** 1 (author-ahead-aggressive; substrate FULLY LOCKED — `DecisionCardBase` shipped at `app/models/decision_cards/_base.py` + `LOCKSTEP_CHECK` at `app/parity/contracts/tw_7c_3_firing.py`)
**files_touched:** 4 new + ≤1 modified (`__init__.py` flat-export if pattern matches G0/G2A)

---

## Story

As the dev-agent,
I want the G5 final-operator-handoff DecisionCard authored as a four-file lockstep co-commit (model + schema + shape-pin + golden),
So that downstream Wave-3 story 7c.15 (§11B G4B input-package + §15 G5 final operator handoff bundle emission, per AMEND-4 fold) has a per-gate DecisionCard model conforming to the 7c.4b shared `DecisionCardBase` + LOCKSTEP_CHECK enforcement + class-conformance recognition.

---

## Predecessor / Dependency Context

- **7c.4b** (CLOSED 2026-05-05 at `8b12970`; T11 cross-agent MANDATORY PASS-with-P-1-patch): provides shared `DecisionCardBase` + `DecisionCardMeta` + `CacheState` StrEnum + `CacheStateLiteral` at `app/models/decision_cards/_base.py`; `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` at `app/parity/contracts/tw_7c_3_firing.py`; class-conformance validator extension recognizing 18 runtime IDs (D6); C6 import-linter contract on independence type per P-1 patch.
- **7c.5.G0 + 7c.5.G2A** (sibling fresh-authors; in flight on Codex 2026-05-05): provide concrete fresh-author pattern reference. `app/models/decision_cards/g0.py` (Codex's G0 implementation) is the canonical pattern template — mirrors `DecisionCardBase` inheritance + `gate_id` / `gate_focus` Literals + `card_id`/`trial_id`/`created_at`/`verb` standard fields + `field_validator` chain + `field_serializer` for Path lists.
- **Existing legacy substrate:** `app/models/decision_cards/{g1,g2c,g3,g4}.py` (Slab 7a; inherit from legacy `DecisionCard` at `base.py`). 2-class regime is intentional and documented; G5 is fresh-author and consumes ONLY the new `DecisionCardBase` (NOT legacy `DecisionCard`).
- **Consumer:** Wave-3 story `7c.15` (§11B G4B input-package + §15 G5 final operator handoff + FR-7c-29 Marcus-side §15 bundle emission). 7c.15 references G5Card via the consumer-side poll-surface that emits `assembly bundle + DESCRIPT-ASSEMBLY-GUIDE.md regen + Trial-3 transcript anchor + slab-close evidence pointer`. **7c.15 is NOT yet filed** (waits on G4 + G5 + 7c.3b + 7c.17b prereqs); G5Card's payload is designed to encode the four artifacts 7c.15 will emit.

---

## Acceptance Criteria

### AC-7c.5.G5-A — Four-file lockstep co-commit (FR-7c-6 + FR-7c-7 + FR-7c-49)

**Given** 7c.4b's `DecisionCardBase` + `DecisionCardMeta` + `LOCKSTEP_CHECK` are LANDED + class-conformance validator recognizes G5
**When** the dev-agent authors the four files atomically:
1. `app/models/decision_cards/g5.py` — `G5Card` Pydantic-v2 subclass of `DecisionCardBase`; `gate_id: Literal["G5"]` discriminator; `gate_focus: Literal["final_operator_handoff"]` closed marker; G5-specific fields:
   - `bundle_run_id: UUID` (UUID4-validated; identifies the trial run that produced the handoff bundle)
   - `handoff_artifact_paths: list[Path]` (non-empty; pattern-replicate G0's `corpus_paths_confirmed` validator + serializer; lists assembly bundle + DESCRIPT-ASSEMBLY-GUIDE + transcript anchor + slab-close evidence pointer paths)
   - `handoff_summary: str` (non-empty; operator-facing summary)
2. `app/models/decision_cards/schema/g5.v1.schema.json` — JSON Schema regenerated from `G5Card.model_json_schema()` (deterministic emission; `sort_keys=True`; FR-7c-51 `schema_version: "v1"`).
3. `tests/parity/test_decision_card_g5_shape.py` — shape-pin asserting (a) field-presence: `decision_card_digest`, `meta`, `schema_version`, `card_id`, `trial_id`, `gate_id`, `gate_focus`, `created_at`, `bundle_run_id`, `handoff_artifact_paths`, `handoff_summary`, `verb` (12 fields); (b) closed-enum red-rejection on `gate_id` (rejects `"G0"` / `"G99"` / non-string); (c) closed-enum red-rejection on `gate_focus` (rejects `"slab_close_ceremony"` / non-string); (d) JSON-Schema emission matches frozen file byte-for-byte; (e) `g5_golden.json` round-trips via `G5Card.model_validate(...)` + `model_dump_json(by_alias=True)`; (f) non-empty `handoff_artifact_paths` validation (raises `ValidationError` on empty list); (g) non-empty `handoff_summary` validation (raises on `""`); (h) frozen mutation rejection (model_config inherits `frozen=True` from base).
4. `tests/fixtures/decision_cards/g5_golden.json` — deterministic golden fixture with all required fields populated + UUID4-shape `card_id` / `trial_id` / `bundle_run_id` + tz-aware `created_at` (e.g., `"2026-05-05T00:00:00+00:00"`) + `meta.cache_state: "healthy"` + `meta.affected_nodes: []` + `meta.override_trail: []` + ≥1 path in `handoff_artifact_paths` + non-empty `handoff_summary` + `verb: "approve"` + valid sha256 hex `decision_card_digest`.

**Then** all four files are co-committed in one diff; the model imports from the SHARED BASE `app.models.decision_cards._base.DecisionCardBase`; the shape-pin imports `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (per AMEND-7d-i; cite by reference; do NOT re-derive).

### AC-7c.5.G5-B — TW-7c-3 firing on out-of-sync (FR-7c-7 + AMEND-7d-i)

**Given** 7c.4b's `LOCKSTEP_CHECK` constant + `FOUR_FILE_GLOBS` registered
**When** any of the four G5 files is missing or out-of-sync (e.g., schema present but model absent; or model + schema present but shape-pin + golden absent)
**Then** TW-7c-3 fires (critical severity); STOP; the firing-spec single-source at `app/parity/contracts/tw_7c_3_firing.py` is cited via `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i compliance verified by 7c.4b's `tests/structural/test_tw_7c_3_firing_spec_single_source.py` AST scan — this story does NOT re-derive the firing condition).

### AC-7c.5.G5-C — Class-conformance recognition (FR-7c-8 + 7c.4b D6)

**Given** 7c.4b's class-conformance validator extension recognizing 18 runtime IDs
**When** `scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` runs after this story lands
**Then** the validator confirms `tests/parity/test_decision_card_g5_shape.py` is structurally well-formed AND class-conformance count = T1-baseline + 1.

**T1 records the actual class-conformance baseline at story-open** (depends on whether 7c.5.G0 / 7c.5.G2A have landed first):
- If neither G0 nor G2A landed: baseline = 11; this story increments to 12.
- If G0 landed but G2A not: baseline = 12; this story increments to 13.
- If G2A landed but G0 not: baseline = 12; this story increments to 13.
- If both landed: baseline = 13; this story increments to 14.

### AC-7c.5.G5-D — Cross-gate non-regression on existing per-gate cards

**Given** legacy G1/G2C/G3/G4 cards (Slab 7a substrate; inherit from legacy `DecisionCard`) + sibling G0Card / G2ACard (if landed; inherit from `DecisionCardBase`)
**When** this story lands
**Then** existing tests against G1Card / G2CCard / G3Card / G4Card / G0Card / G2ACard construction continue to pass UNCHANGED (no model-side regression; G5Card addition is purely additive). **Verification:** `pytest tests/parity/ tests/parametrized_harness/ -p no:randomly -q` PASS at T9 with all per-gate shape-pins green.

### AC-7c.5.G5-E — Pydantic-v2 14-idiom conformance (per `docs/dev-guide/pydantic-v2-schema-checklist.md`)

**Given** the canonical Pydantic-v2 idiom checklist
**When** `app/models/decision_cards/g5.py` is authored
**Then** the model uses: inherited `validate_assignment=True` + inherited `extra="forbid"` + inherited `frozen=True` + `gate_id: Literal["G5"]` discriminator + `gate_focus: Literal["final_operator_handoff"]` closed marker + `field_validator` chain (UUID4 enforcement on `card_id` / `trial_id` / `bundle_run_id`; tz-aware enforcement on `created_at`; non-empty enforcement on `handoff_artifact_paths` + `handoff_summary`) + `field_serializer` for `handoff_artifact_paths` (Path → posix string list, mirror G0's pattern) + Field descriptions on every field + `schema_version: Literal["v1"]` field.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.4b done (sprint-status.yaml `migration-7c-4b-gate-family-foundation-implementation: done`); `DecisionCardBase` + `DecisionCardMeta` importable from `app.models.decision_cards._base`; `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` importable from `app.parity.contracts.tw_7c_3_firing`.
  - [ ] T1.2 Record class-conformance baseline at story-open: run `.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/`. Document the baseline count (11 if neither sibling landed; 12 if one; 13 if both). This story increments by exactly +1.
  - [ ] T1.3 Read `app/models/decision_cards/g0.py` (Codex's shipped G0Card) as the canonical fresh-author pattern reference. Mirror its inheritance + Literal discriminators + field_validator chain + field_serializer for Path lists.
  - [ ] T1.4 Read `tests/fixtures/decision_cards/g0_golden.json` (sibling fresh-author golden fixture; once G0 lands).
  - [ ] T1.5 Read `tests/parity/test_decision_card_g0_shape.py` (sibling fresh-author shape-pin; once G0 lands) for closed-enum red-rejection + JSON-Schema byte-match + golden round-trip patterns.
  - [ ] T1.6 Refresh broad-regression baseline (T1 failure count for T9 delta-comparison; expect 39-41 inherited checkout-level).
  - [ ] T1.7 Run sandbox-AC validator on this spec; expect PASS.

- [ ] **T2 — Author G5Card model (AC: 7c.5.G5-A + 7c.5.G5-E)**
  - [ ] T2.1 Author `app/models/decision_cards/g5.py` mirroring G0's structure: import `DecisionCardBase` from `_base.py`; import `enforce_tz_aware` + `enforce_uuid4_version` from `app.models.state._base`; declare `DecisionCardVerb` Literal; declare `G5Card(DecisionCardBase)` with all fields per AC-A.
  - [ ] T2.2 Field validators: `_enforce_uuid4` for `card_id` / `trial_id` / `bundle_run_id`; `_enforce_tz` for `created_at`; `_require_handoff_artifact_paths` (non-empty); `_require_handoff_summary` (non-empty).
  - [ ] T2.3 Field serializer: `_serialize_handoff_artifact_paths` (Path → posix string list, mirror G0's `_serialize_corpus_paths`).
  - [ ] T2.4 Export `G5Card` in `__all__`.
  - [ ] T2.5 Update `app/models/decision_cards/__init__.py` exports if a flat-import pattern exists (mirror G0's pattern; check whether G0 added an entry).

- [ ] **T3 — Generate JSON schema (AC: 7c.5.G5-A)**
  - [ ] T3.1 Generate `app/models/decision_cards/schema/g5.v1.schema.json` via `.venv/Scripts/python.exe -c "from app.models.decision_cards.g5 import G5Card; import json; print(json.dumps(G5Card.model_json_schema(), indent=2, sort_keys=True))" > app/models/decision_cards/schema/g5.v1.schema.json` (exact command; deterministic emission).
  - [ ] T3.2 Verify FR-7c-51 `schema_version: "v1"` field present in emitted schema (Pydantic emits this automatically from the `Literal["v1"]` field declaration).
  - [ ] T3.3 Pattern-match G0's emitted schema for structural parity (same top-level keys; same property ordering under sort_keys).

- [ ] **T4 — Author golden fixture (AC: 7c.5.G5-A)**
  - [ ] T4.1 Author `tests/fixtures/decision_cards/g5_golden.json` with deterministic stable values:
    - `decision_card_digest`: 64-char lowercase hex (e.g., `"a"*64` for fixture determinism)
    - `meta.cache_state: "healthy"` + `meta.affected_nodes: []` + `meta.override_trail: []`
    - `schema_version: "v1"`
    - `card_id`: stable UUID4 (e.g., `"00000000-0000-4000-8000-000000000005"`)
    - `trial_id`: stable UUID4
    - `bundle_run_id`: stable UUID4
    - `gate_id: "G5"` + `gate_focus: "final_operator_handoff"`
    - `created_at: "2026-05-05T00:00:00+00:00"` (tz-aware ISO 8601)
    - `handoff_artifact_paths`: list with ≥1 deterministic path (e.g., `["course-content/courses/example-trial/assembly-bundle/"]`)
    - `handoff_summary`: non-empty string (e.g., `"Trial assembly bundle handed off to operator for Descript composition."`)
    - `verb: "approve"`
  - [ ] T4.2 Verify deterministic round-trip: `G5Card.model_validate(json.load(...))` then `model_dump_json(by_alias=True, sort_keys=True)` is stable byte-for-byte across N=2 invocations (no nondeterminism).

- [ ] **T5 — Author shape-pin test (AC: 7c.5.G5-A + 7c.5.G5-B + 7c.5.G5-C + 7c.5.G5-E)**
  - [ ] T5.1 Author `tests/parity/test_decision_card_g5_shape.py` mirroring G0's shape-pin structure with 8 test cases per AC-A items (a)-(h):
    - [ ] T5.1.a `test_g5_card_has_required_fields` — `G5Card.model_fields.keys()` contains the 12 expected fields.
    - [ ] T5.1.b `test_g5_card_gate_id_closed_enum_red_rejection` — `pytest.raises(ValidationError)` on `gate_id="G0"`, `gate_id="G99"`, `gate_id=42`.
    - [ ] T5.1.c `test_g5_card_gate_focus_closed_enum_red_rejection` — `pytest.raises(ValidationError)` on `gate_focus="slab_close_ceremony"`, `gate_focus="trial_open"`, `gate_focus=None`.
    - [ ] T5.1.d `test_g5_json_schema_byte_for_byte_match` — load `app/models/decision_cards/schema/g5.v1.schema.json` + assert byte-equality with deterministic regeneration.
    - [ ] T5.1.e `test_g5_golden_fixture_round_trips` — load `tests/fixtures/decision_cards/g5_golden.json` + `G5Card.model_validate(...)` + `model_dump_json(by_alias=True)` matches input (canonicalized).
    - [ ] T5.1.f `test_g5_card_rejects_empty_handoff_artifact_paths` — `pytest.raises(ValidationError)` on `handoff_artifact_paths=[]`.
    - [ ] T5.1.g `test_g5_card_rejects_empty_handoff_summary` — `pytest.raises(ValidationError)` on `handoff_summary=""`.
    - [ ] T5.1.h `test_g5_card_frozen_mutation_rejection` — `pytest.raises(ValidationError)` on `card.gate_id = "G6"` (inherited `frozen=True`).
  - [ ] T5.2 Import `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` at module level (AMEND-7d-i; cite by reference; do NOT re-derive). Optional: assert at module-scope `assert "g5" in [g.split("/")[-1].split(".")[0] for g in FOUR_FILE_GLOBS]` to verify G5 is registered.
  - [ ] T5.3 Optional: add `test_g5_lockstep_all_four_files_present` invoking `LOCKSTEP_CHECK("G5", repo_root=...)` and asserting `result.all_four_present is True` (sanity check that the four-file co-commit is observable to the firing-spec).

- [ ] **T6 — Verification battery (R-tier R2)**
  - [ ] T6.1 Focused: `.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g5_shape.py -p no:randomly -q --tb=short` → PASS (8 tests).
  - [ ] T6.2 Cross-gate non-regression (AC-D): `.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ -p no:randomly -q --tb=short` → PASS UNCHANGED (existing G0 / G2A / per-gate construction tests preserved).
  - [ ] T6.3 Smoke: `.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short` → 200-nodeid baseline UNCHANGED (G5 NOT in smoke set).
  - [ ] T6.4 R2 broad regression: `.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line` → failure count ≤ T1 baseline (39-41 inherited checkout-level expected).
  - [ ] T6.5 Class-conformance: `.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` → T1-baseline + 1.
  - [ ] T6.6 Lint-imports: `.venv/Scripts/lint-imports.exe` → 12 KEPT / 0 broken UNCHANGED (no contract change; G5 lives under `app.models.decision_cards` which is import-linter scoped via existing C contracts).
  - [ ] T6.7 Sandbox-AC: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g5-decision-card-fresh-author.md` → PASS.
  - [ ] T6.8 Ruff: `.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g5.py tests/parity/test_decision_card_g5_shape.py` → clean.

- [ ] **T10 — Codex self-review (NEW CYCLE T10)**
  - [ ] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g5.ready-for-review.md` summarizing: 4 new file paths + verification battery results + class-conformance delta (T1-baseline → +1) + R2 broad-regression delta + AMEND-7d-i compliance evidence (LOCKSTEP_CHECK imported by reference; show import line) + AC-D cross-gate non-regression confirmation.
  - [ ] T10.2 Self-review across 3 lenses (Blind / Edge / Auditor) inline in the dropbox notice.

---

## Required Readings (T1)

1. This story spec (D5/D6/D7-equivalent: AC-A-E coverage).
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8 contract).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-05.md` (T11 verdict; documents the 2-class regime + P-1 patch + canonical class names shipped).
4. `app/models/decision_cards/_base.py` (canonical `DecisionCardBase` + `DecisionCardMeta` + `CacheState`).
5. `app/models/decision_cards/g0.py` (sibling fresh-author pattern; canonical reference once landed).
6. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK + FOUR_FILE_GLOBS; per AMEND-7d-i).
7. `tests/parity/test_decision_card_g0_shape.py` (sibling fresh-author shape-pin; pattern reference once landed).
8. `tests/fixtures/decision_cards/g0_golden.json` (golden-fixture shape reference once landed).
9. `tests/parity/test_decision_card_base_shape.py` (7c.4b D8 base-class shape-pin; structural pattern).
10. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G5 = final operator handoff gate; family-contract authoring target).
11. `docs/dev-guide/pydantic-v2-schema-checklist.md` (14-idiom conformance per AC-E).
12. `docs/dev-guide/dev-agent-anti-patterns.md` (schema/test-authoring trap catalog).
13. `docs/dev-guide/story-cycle-efficiency.md` (K-floor discipline; lite-vs-standard T11 rubric).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks (only `.venv/Scripts/python.exe -m pytest`, `.venv/Scripts/python.exe scripts/utilities/...`, `.venv/Scripts/lint-imports.exe`, `.venv/Scripts/python.exe -m ruff`, and `.venv/Scripts/python.exe -c "..."` — all `.venv/Scripts/` shipped-dep invocations). Sandbox-AC: PASS (verified at T0).

---

## Dispatch Status

**HELD-RELEASED 2026-05-05** — sibling fresh-author pattern artifacts now on disk:
- `app/models/decision_cards/g0.py` + `g2a.py`
- `app/models/decision_cards/schema/g0.v1.schema.json` + `g2a.v1.schema.json`
- `tests/parity/test_decision_card_g0_shape.py` + `test_decision_card_g2a_shape.py`
- `tests/fixtures/decision_cards/g0_golden.json` + `g2a_golden.json`

G0/G2A sprint-status = `review` (T1-T10 complete; T11 pending; not yet `done`-flipped). Per the documented operator-override pattern (next-session-start-here.md "Operator override pattern observed"), Codex MAY consume on-disk pattern artifacts pre-T11-close to keep Codex queue moving while Claude catches up T11 + commits in batches.

T1 hard-checkpoint relaxation: instead of requiring G0/G2A `done` in sprint-status, T1 verifies the four sibling artifact files exist on disk. AMELIA-P2 freshness check still applies — if any T11 patch lands on G0/G2A before this story dispatches, re-read this spec against post-T11 g0.py / g2a.py for pattern divergence.
