# Migration Story 7c.5.G6: G6 DecisionCard Fresh-Author (Slab-Close Ceremony)

**Status:** ready-for-dev *(spec authored 2026-05-05 lookahead_tier=1; predecessor 7c.4b CLOSED at `8b12970`; sibling fresh-authors 7c.5.G0 + 7c.5.G2A landed at `review` 2026-05-05 — T1-T10 complete; T11 pending. **HELD-RELEASED:** sibling pattern artifacts NOW ON DISK. Per operator-override pattern, Codex MAY dispatch pre-T11-close.)*
**Sprint key:** `migration-7c-5-g6-decision-card-fresh-author`
**Epic:** Slab 7c — Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 1
**K-target:** 1.2× (pattern-replication of G0/G2A; identical four-file structure; no new contract decisions)
**Estimated LOC:** ~260 (4 new files: ~75 model + ~50 schema + ~115 shape-pin + ~40 golden)
**Gate-mode:** single-gate
**Cross-agent review:** false (per governance JSON)
**R-tier:** R2
**T11-tier:** standard
**Lookahead-tier:** 1 (author-ahead-aggressive; substrate FULLY LOCKED — `DecisionCardBase` shipped at `app/models/decision_cards/_base.py` + `LOCKSTEP_CHECK` at `app/parity/contracts/tw_7c_3_firing.py`)
**files_touched:** 4 new + ≤1 modified (`__init__.py` flat-export if pattern matches G0/G2A)

---

## Story

As the dev-agent,
I want the G6 slab-close-ceremony DecisionCard authored as a four-file lockstep co-commit (model + schema + shape-pin + golden),
So that downstream story 7c.21 (Slab 7c retrospective close + cross-agent MANDATORY review per AMEND-7d-iii STOP-on-TW-7c-6-fire branch) has a per-gate DecisionCard model conforming to the 7c.4b shared `DecisionCardBase` + LOCKSTEP_CHECK enforcement + class-conformance recognition.

---

## Predecessor / Dependency Context

- **7c.4b** (CLOSED 2026-05-05 at `8b12970`; T11 cross-agent MANDATORY PASS-with-P-1-patch): provides shared `DecisionCardBase` + `DecisionCardMeta` + `CacheState` + `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` + class-conformance validator extension recognizing 18 runtime IDs (D6) + C6 import-linter contract on independence type.
- **7c.5.G0 + 7c.5.G2A** (sibling fresh-authors; in flight on Codex 2026-05-05): provide concrete fresh-author pattern reference. `app/models/decision_cards/g0.py` is the canonical pattern template.
- **Existing legacy substrate:** `app/models/decision_cards/{g1,g2c,g3,g4}.py` (Slab 7a; inherit from legacy `DecisionCard` at `base.py`). 2-class regime is intentional and documented; G6 is fresh-author and consumes ONLY the new `DecisionCardBase` (NOT legacy `DecisionCard`).
- **Consumer:** Wave-6 story `7c.21` (Slab 7c retrospective close + slab-close ceremony evidence; cross-agent MANDATORY review per AMEND-7d-iii). 7c.21 references G6Card via the slab-close ceremony emission. **7c.21 is NOT yet filed** (waits on full Wave-2/3/4/5 closure); G6Card's payload is designed to encode the four artifacts 7c.21 will emit (retrospective doc + slab-close evidence pointer + final summary + closure run reference).
- **ADR 0002 §1 note:** "G2A and G6 are family-contract authoring targets. They are not part of the FR-7c-6 18-ID Trial-3 runtime list unless a later manifest story explicitly promotes them into runtime dispatch." G6 is therefore a family-contract-only landing in this story; runtime dispatch promotion is out-of-scope (deferred to a future post-Slab-7c manifest story if/when needed).

---

## Acceptance Criteria

### AC-7c.5.G6-A — Four-file lockstep co-commit (FR-7c-6 + FR-7c-7 + FR-7c-49)

**Given** 7c.4b's `DecisionCardBase` + `DecisionCardMeta` + `LOCKSTEP_CHECK` are LANDED + class-conformance validator recognizes G6
**When** the dev-agent authors the four files atomically:
1. `app/models/decision_cards/g6.py` — `G6Card` Pydantic-v2 subclass of `DecisionCardBase`; `gate_id: Literal["G6"]` discriminator; `gate_focus: Literal["slab_close_ceremony"]` closed marker; G6-specific fields:
   - `slab_id: str` (non-empty; shape-validated to `^[0-9]+[a-z]?$` for slab-id form like "7c", "7", "5a", "12b"; pattern enforced via field_validator)
   - `closing_run_id: UUID` (UUID4-validated; identifies the final trial run referenced by closure)
   - `retrospective_path: Path` (canonical retrospective doc path; non-empty)
   - `closing_artifact_paths: list[Path]` (non-empty; pattern-replicate G0's `corpus_paths_confirmed` validator + serializer; lists retrospective + slab-close evidence pointer + final summary doc paths)
   - `slab_close_summary: str` (non-empty; operator-facing summary of slab closure)
2. `app/models/decision_cards/schema/g6.v1.schema.json` — JSON Schema regenerated from `G6Card.model_json_schema()` (deterministic emission; `sort_keys=True`; FR-7c-51 `schema_version: "v1"`).
3. `tests/parity/test_decision_card_g6_shape.py` — shape-pin asserting (a) field-presence: `decision_card_digest`, `meta`, `schema_version`, `card_id`, `trial_id`, `gate_id`, `gate_focus`, `created_at`, `slab_id`, `closing_run_id`, `retrospective_path`, `closing_artifact_paths`, `slab_close_summary`, `verb` (14 fields); (b) closed-enum red-rejection on `gate_id` (rejects `"G5"` / `"G99"` / non-string); (c) closed-enum red-rejection on `gate_focus` (rejects `"final_operator_handoff"` / non-string); (d) JSON-Schema emission matches frozen file byte-for-byte; (e) `g6_golden.json` round-trips via `G6Card.model_validate(...)` + `model_dump_json(by_alias=True)`; (f) non-empty `closing_artifact_paths` validation (raises `ValidationError` on empty list); (g) non-empty `slab_close_summary` validation (raises on `""`); (h) `slab_id` pattern validation (rejects `""`, `"slab-7c"`, `"7C"`, `"7-c"`; accepts `"7c"`, `"7"`, `"12b"`); (i) frozen mutation rejection.
4. `tests/fixtures/decision_cards/g6_golden.json` — deterministic golden fixture with all required fields populated + UUID4-shape `card_id` / `trial_id` / `closing_run_id` + tz-aware `created_at` + `meta.cache_state: "healthy"` + `slab_id: "7c"` + ≥1 path in `closing_artifact_paths` + non-empty `retrospective_path` + non-empty `slab_close_summary` + `verb: "approve"` + valid sha256 hex `decision_card_digest`.

**Then** all four files are co-committed in one diff; the model imports from the SHARED BASE `app.models.decision_cards._base.DecisionCardBase`; the shape-pin imports `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (per AMEND-7d-i; cite by reference; do NOT re-derive).

### AC-7c.5.G6-B — TW-7c-3 firing on out-of-sync (FR-7c-7 + AMEND-7d-i)

Identical to 7c.5.G0-B / 7c.5.G5-B template: any of the four G6 files missing or out-of-sync fires TW-7c-3 critical; LOCKSTEP_CHECK cited by reference; no re-derivation.

### AC-7c.5.G6-C — Class-conformance recognition (FR-7c-8 + 7c.4b D6)

**Given** 7c.4b's class-conformance validator extension recognizing 18 runtime IDs
**When** `scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` runs after this story lands
**Then** the validator confirms `tests/parity/test_decision_card_g6_shape.py` is structurally well-formed AND class-conformance count = T1-baseline + 1.

**T1 records the actual class-conformance baseline at story-open** (depends on which siblings have landed: 11 if none; 12 if one; 13 if two; 14 if three of G0/G2A/G5).

### AC-7c.5.G6-D — Cross-gate non-regression on existing per-gate cards

**Given** legacy G1/G2C/G3/G4 cards (Slab 7a substrate) + sibling G0Card / G2ACard / G5Card (if landed)
**When** this story lands
**Then** existing tests against G1Card / G2CCard / G3Card / G4Card / G0Card / G2ACard / G5Card construction continue to pass UNCHANGED (no model-side regression; G6Card addition is purely additive). **Verification:** `pytest tests/parity/ tests/parametrized_harness/ -p no:randomly -q` PASS at T9 with all per-gate shape-pins green.

### AC-7c.5.G6-E — Pydantic-v2 14-idiom conformance (per `docs/dev-guide/pydantic-v2-schema-checklist.md`)

**Given** the canonical Pydantic-v2 idiom checklist
**When** `app/models/decision_cards/g6.py` is authored
**Then** the model uses: inherited `validate_assignment=True` + inherited `extra="forbid"` + inherited `frozen=True` + `gate_id: Literal["G6"]` discriminator + `gate_focus: Literal["slab_close_ceremony"]` closed marker + `field_validator` chain (UUID4 enforcement on `card_id` / `trial_id` / `closing_run_id`; tz-aware enforcement on `created_at`; non-empty enforcement on `closing_artifact_paths` + `slab_close_summary`; pattern enforcement on `slab_id`) + `field_serializer` for `closing_artifact_paths` and `retrospective_path` (Path → posix string, mirror G0's pattern) + Field descriptions on every field + `schema_version: Literal["v1"]` field.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.4b done (sprint-status.yaml `migration-7c-4b-gate-family-foundation-implementation: done`); `DecisionCardBase` + `DecisionCardMeta` importable from `app.models.decision_cards._base`; `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` importable from `app.parity.contracts.tw_7c_3_firing`.
  - [ ] T1.2 Record class-conformance baseline at story-open: run `.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/`. Document the baseline count. This story increments by exactly +1.
  - [ ] T1.3 Read `app/models/decision_cards/g0.py` (Codex's shipped G0Card) as the canonical fresh-author pattern reference.
  - [ ] T1.4 Read `tests/fixtures/decision_cards/g0_golden.json` (sibling fresh-author golden fixture; once G0 lands).
  - [ ] T1.5 Read `tests/parity/test_decision_card_g0_shape.py` (sibling fresh-author shape-pin; once G0 lands) for closed-enum red-rejection + JSON-Schema byte-match + golden round-trip patterns.
  - [ ] T1.6 Refresh broad-regression baseline (T1 failure count for T9 delta-comparison; expect 39-41 inherited checkout-level).
  - [ ] T1.7 Run sandbox-AC validator on this spec; expect PASS.

- [ ] **T2 — Author G6Card model (AC: 7c.5.G6-A + 7c.5.G6-E)**
  - [ ] T2.1 Author `app/models/decision_cards/g6.py` mirroring G0's structure: import `DecisionCardBase` from `_base.py`; import `enforce_tz_aware` + `enforce_uuid4_version` from `app.models.state._base`; declare `DecisionCardVerb` Literal; declare `G6Card(DecisionCardBase)` with all fields per AC-A.
  - [ ] T2.2 Field validators: `_enforce_uuid4` for `card_id` / `trial_id` / `closing_run_id`; `_enforce_tz` for `created_at`; `_require_closing_artifact_paths` (non-empty); `_require_slab_close_summary` (non-empty); `_validate_slab_id_pattern` (regex `^[0-9]+[a-z]?$`; raises on empty / mismatched form).
  - [ ] T2.3 Field serializers: `_serialize_closing_artifact_paths` (Path → posix string list, mirror G0's `_serialize_corpus_paths`); `_serialize_retrospective_path` (Path → posix string, single-value variant).
  - [ ] T2.4 Export `G6Card` in `__all__`.
  - [ ] T2.5 Update `app/models/decision_cards/__init__.py` exports if a flat-import pattern exists (mirror G0).

- [ ] **T3 — Generate JSON schema (AC: 7c.5.G6-A)**
  - [ ] T3.1 Generate `app/models/decision_cards/schema/g6.v1.schema.json` via `.venv/Scripts/python.exe -c "from app.models.decision_cards.g6 import G6Card; import json; print(json.dumps(G6Card.model_json_schema(), indent=2, sort_keys=True))" > app/models/decision_cards/schema/g6.v1.schema.json` (exact command; deterministic emission).
  - [ ] T3.2 Verify FR-7c-51 `schema_version: "v1"` field present in emitted schema.
  - [ ] T3.3 Pattern-match G0's emitted schema for structural parity.

- [ ] **T4 — Author golden fixture (AC: 7c.5.G6-A)**
  - [ ] T4.1 Author `tests/fixtures/decision_cards/g6_golden.json` with deterministic stable values:
    - `decision_card_digest`: 64-char lowercase hex (e.g., `"a"*64`)
    - `meta.cache_state: "healthy"` + `meta.affected_nodes: []` + `meta.override_trail: []`
    - `schema_version: "v1"`
    - `card_id`: stable UUID4 (e.g., `"00000000-0000-4000-8000-000000000006"`)
    - `trial_id`: stable UUID4
    - `closing_run_id`: stable UUID4
    - `gate_id: "G6"` + `gate_focus: "slab_close_ceremony"`
    - `created_at: "2026-05-05T00:00:00+00:00"` (tz-aware ISO 8601)
    - `slab_id: "7c"`
    - `retrospective_path`: deterministic path (e.g., `"_bmad-output/planning-artifacts/slab-7c-retrospective.md"`)
    - `closing_artifact_paths`: list with ≥1 deterministic path (e.g., `["_bmad-output/planning-artifacts/slab-7c-retrospective.md", "_bmad-output/planning-artifacts/slab-7c-close-evidence-pointer.md"]`)
    - `slab_close_summary`: non-empty string (e.g., `"Slab 7c orchestrational tail closed; 36 stories complete; tripwire ledger green."`)
    - `verb: "approve"`
  - [ ] T4.2 Verify deterministic round-trip.

- [ ] **T5 — Author shape-pin test (AC: 7c.5.G6-A + 7c.5.G6-B + 7c.5.G6-C + 7c.5.G6-E)**
  - [ ] T5.1 Author `tests/parity/test_decision_card_g6_shape.py` mirroring G0's shape-pin structure with 9 test cases per AC-A items (a)-(i):
    - [ ] T5.1.a `test_g6_card_has_required_fields` — `G6Card.model_fields.keys()` contains the 14 expected fields.
    - [ ] T5.1.b `test_g6_card_gate_id_closed_enum_red_rejection` — `pytest.raises(ValidationError)` on `gate_id="G5"`, `gate_id="G99"`, `gate_id=42`.
    - [ ] T5.1.c `test_g6_card_gate_focus_closed_enum_red_rejection` — `pytest.raises(ValidationError)` on `gate_focus="final_operator_handoff"`, `gate_focus="trial_open"`, `gate_focus=None`.
    - [ ] T5.1.d `test_g6_json_schema_byte_for_byte_match` — load schema file + assert byte-equality with deterministic regeneration.
    - [ ] T5.1.e `test_g6_golden_fixture_round_trips` — load golden + `G6Card.model_validate(...)` + `model_dump_json(by_alias=True)` matches input.
    - [ ] T5.1.f `test_g6_card_rejects_empty_closing_artifact_paths` — `pytest.raises(ValidationError)` on `closing_artifact_paths=[]`.
    - [ ] T5.1.g `test_g6_card_rejects_empty_slab_close_summary` — `pytest.raises(ValidationError)` on `slab_close_summary=""`.
    - [ ] T5.1.h `test_g6_card_validates_slab_id_pattern` — parametrize: accept `["7", "7c", "12", "12b", "5a"]`; reject `["", "slab-7c", "7C", "7-c", "7cd", "7ab"]`.
    - [ ] T5.1.i `test_g6_card_frozen_mutation_rejection` — `pytest.raises(ValidationError)` on `card.gate_id = "G5"`.
  - [ ] T5.2 Import `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` at module level (AMEND-7d-i; cite by reference).
  - [ ] T5.3 Optional: add `test_g6_lockstep_all_four_files_present` invoking `LOCKSTEP_CHECK("G6", repo_root=...)` and asserting `result.all_four_present is True`.

- [ ] **T6 — Verification battery (R-tier R2)**
  - [ ] T6.1 Focused: `.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g6_shape.py -p no:randomly -q --tb=short` → PASS (9 tests).
  - [ ] T6.2 Cross-gate non-regression (AC-D): `.venv/Scripts/python.exe -m pytest tests/parity/ tests/parametrized_harness/ -p no:randomly -q --tb=short` → PASS UNCHANGED.
  - [ ] T6.3 Smoke: `.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short` → 200-nodeid baseline UNCHANGED.
  - [ ] T6.4 R2 broad regression: `.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line` → failure count ≤ T1 baseline.
  - [ ] T6.5 Class-conformance: `.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` → T1-baseline + 1.
  - [ ] T6.6 Lint-imports: `.venv/Scripts/lint-imports.exe` → 12 KEPT / 0 broken UNCHANGED.
  - [ ] T6.7 Sandbox-AC: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g6-decision-card-fresh-author.md` → PASS.
  - [ ] T6.8 Ruff: `.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g6.py tests/parity/test_decision_card_g6_shape.py` → clean.

- [ ] **T10 — Codex self-review (NEW CYCLE T10)**
  - [ ] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g6.ready-for-review.md` summarizing: 4 new file paths + verification battery results + class-conformance delta + R2 broad-regression delta + AMEND-7d-i compliance evidence + AC-D cross-gate non-regression confirmation + 2-class regime confirmation (G6Card inherits `DecisionCardBase`).
  - [ ] T10.2 Self-review across 3 lenses (Blind / Edge / Auditor) inline in the dropbox notice.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8).
3. `_bmad-output/implementation-artifacts/7c-4b-code-review-2026-05-05.md` (T11 verdict; 2-class regime documented).
4. `app/models/decision_cards/_base.py` (canonical `DecisionCardBase`).
5. `app/models/decision_cards/g0.py` (sibling fresh-author canonical pattern).
6. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK; AMEND-7d-i).
7. `tests/parity/test_decision_card_g0_shape.py` (sibling shape-pin pattern reference once landed).
8. `tests/fixtures/decision_cards/g0_golden.json` (golden-fixture reference once landed).
9. `tests/parity/test_decision_card_base_shape.py` (7c.4b D8 base-class shape-pin).
10. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G6 = slab-close ceremony gate; family-contract authoring target; NOT in 18-ID PRODUCTION_GATE_IDS list).
11. `docs/dev-guide/pydantic-v2-schema-checklist.md`.
12. `docs/dev-guide/dev-agent-anti-patterns.md`.
13. `docs/dev-guide/story-cycle-efficiency.md`.

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks (only `.venv/Scripts/` invocations of pytest/ruff/python utilities). Sandbox-AC: PASS (verified at T0).

---

## Dispatch Status

**HELD-RELEASED 2026-05-05** — sibling fresh-author pattern artifacts now on disk (g0.py + g2a.py + schemas + shape-pins + goldens). G0/G2A sprint-status = `review` (T11 pending). Per operator-override pattern, Codex MAY dispatch pre-T11-close. T1 verifies the four sibling artifact files exist on disk rather than requiring `done` in sprint-status. AMELIA-P2 freshness check still applies — re-read g0.py / g2a.py if any post-T11 patch lands first.
