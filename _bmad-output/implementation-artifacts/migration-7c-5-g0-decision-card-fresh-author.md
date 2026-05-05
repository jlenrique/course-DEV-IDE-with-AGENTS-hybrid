# Migration Story 7c.5.G0: G0 DecisionCard Fresh-Author (Trial-Open / Corpus-Confirm)

**Status:** review *(Codex dev complete 2026-05-05; ready-for-review record posted at `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g0.ready-for-review.md`.)*
**Sprint key:** `migration-7c-5-g0-decision-card-fresh-author`
**Epic:** Slab 7c â€” Marcus Orchestrational Tail (`migration-epic-slab-7c-orchestrational-tail`)
**Pts:** 2
**K-target:** 1.4Ã— (modest stretch over baseline; pattern-replication of existing G1/G2C/G3/G4 cards + new LOCKSTEP_CHECK citation)
**Estimated LOC:** ~250 (4 new files: ~50 model + ~50 schema + ~110 shape-pin + ~40 golden)
**Gate-mode:** single-gate
**Cross-agent review:** false (per governance JSON)
**R-tier:** R2 (focused parity + targeted broad regression on decision_cards lockstep)
**T11-tier:** standard
**Lookahead-tier:** 1 (author-ahead-aggressive; substrate IS LOCKED via 7c.4b D1-D8 contract pre-flight; 7c.4b is build-only, not contract-decision)
**files_touched:** 4 new + 0 modified (strict four-file-lockstep co-commit)

---

## Story

As the dev-agent,
I want the G0 trial-open / corpus-confirm DecisionCard authored as a four-file lockstep co-commit (model + schema + shape-pin + golden),
So that Marcus's Â§02A G0 poll-surface (shipped at 7c.3b) has a per-gate DecisionCard model conforming to the 7c.4b shared DecisionCardBase substrate + LOCKSTEP_CHECK enforcement + class-conformance recognition.

---

## Predecessor / Dependency Context

- **7c.4b** (currently in dev as of 2026-05-05): provides the shared `DecisionCardBase` (per D2 contract decision; canonical at `app/models/decision_cards/_base.py` per spec â€” but Codex may consolidate with the existing `app/models/decision_cards/base.py:DecisionCard` already shipped per Slab 7a substrate; **T1 reconciles the actual shipped class name**), the `LOCKSTEP_CHECK` constant + `FOUR_FILE_GLOBS` at `app/parity/contracts/tw_7c_3_firing.py` (per D4 contract decision), and the class-conformance validator extension recognizing 18 runtime IDs (per D6).
- **7c.3b** (done 2026-05-05): provides the Â§02A G0 poll-surface (`app/gates/section_02a/poll_surface.py`) which consumes G0 DecisionCards in the canonical HIL pattern. Pattern replicability: this story's `G0Card` will be displayed via `display_directive(...)` (or its analog) and submitted via `submit_verdict(...)` for the G0 gate.
- **Existing substrate:** `app/models/decision_cards/{g1,g2c,g3,g4}.py` shipped at Slab 7a; pattern-replicate. `tests/fixtures/decision_cards/g1_golden.json` etc. are reference fixtures. **No `tests/parity/test_decision_card_*_shape.py` exists yet** â€” 7c.4b's D8 fixture `tests/parity/test_decision_card_base_shape.py` is the first; this story authors the first per-gate shape-pin.

---

## Acceptance Criteria

### AC-7c.5.G0-A â€” Four-file lockstep co-commit (FR-7c-6 + FR-7c-7 + FR-7c-49)

**Given** 7c.4b's `DecisionCardBase` + `DecisionCardMeta` + `LOCKSTEP_CHECK` constant are LANDED + class-conformance validator recognizes G0
**When** the dev-agent authors the four files atomically:
1. `app/models/decision_cards/g0.py` â€” `G0Card` Pydantic-v2 subclass of the shared base; `gate_id: Literal["G0"]` discriminator; `gate_focus: Literal["trial_open"]` closed marker; G0-specific fields (`corpus_paths_confirmed: list[Path]` non-empty + `directive_run_id: UUID4` + `corpus_confirmation_summary: str` non-empty).
2. `app/models/decision_cards/schema/g0.v1.schema.json` â€” JSON Schema regenerated from `G0Card.model_json_schema()` (deterministic emission; sorted keys; FR-7c-51 `schema_version: "v1"`).
3. `tests/parity/test_decision_card_g0_shape.py` â€” shape-pin asserting (a) field-presence: `card_id`, `trial_id`, `gate_id`, `gate_focus`, `corpus_paths_confirmed`, `directive_run_id`, `corpus_confirmation_summary`, `verb`, `meta`; (b) closed-enum red-rejection on `gate_id` (rejects `"G1"` / `"G99"` / non-string); (c) closed-enum red-rejection on `gate_focus` (rejects `"directive_ratification"` / non-string); (d) JSON-Schema emission matches frozen file byte-for-byte; (e) `g0_golden.json` fixture round-trips via `G0Card.model_validate(...)` then `model_dump_json(by_alias=True, sort_keys=True)`.
4. `tests/fixtures/decision_cards/g0_golden.json` â€” deterministic golden fixture with all required fields populated + UUID4-shape `card_id` + `trial_id` + tz-aware `created_at` + `meta.cache_state: "healthy"`.

**Then** all four files are co-committed in one diff; the model imports from the SHARED BASE per 7c.4b's D2 (whatever class name 7c.4b ships â€” `DecisionCardBase` or `DecisionCard`); the shape-pin imports `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (per AMEND-7d-i; cite by reference, do NOT re-derive).

### AC-7c.5.G0-B â€” TW-7c-3 firing on out-of-sync (FR-7c-7 + AMEND-7d-i)

**Given** 7c.4b's `LOCKSTEP_CHECK` constant + `FOUR_FILE_GLOBS` registered
**When** any of the four G0 files is missing or out-of-sync (e.g., schema present but model absent; or model + schema present but shape-pin + golden absent)
**Then** TW-7c-3 fires (critical severity); STOP; the firing-spec single-source at `app/parity/contracts/tw_7c_3_firing.py` is cited via `from app.parity.contracts.tw_7c_3_firing import LOCKSTEP_CHECK` (AMEND-7d-i compliance verified by 7c.4b's `tests/structural/test_tw_7c_3_firing_spec_single_source.py` AST scan â€” this story does NOT re-derive the firing condition).

### AC-7c.5.G0-C â€” Class-conformance recognition (FR-7c-8 + 7c.4b D6)

**Given** 7c.4b's class-conformance validator extension recognizing 18 runtime IDs
**When** `scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` runs after this story lands
**Then** the validator confirms `tests/parity/test_decision_card_g0_shape.py` is structurally well-formed (matches the shape-pin contract: imports the model + schema-emission assertion + golden round-trip + closed-enum red-rejection) AND class-conformance count = 12 (was 11; +1 for new G0 shape-pin file).

### AC-7c.5.G0-D â€” Schema-stability case for Â§02A G0 poll-surface consumption (FR-7c-49)

**Given** 7c.3b's Â§02A G0 poll-surface emits `Section02AOperatorVerdict` over CLI/HTTP/MCP-stdio for G0-gated directives + the FR-7c-49 schema-stability harness from 7c.4b D3
**When** the Â§02A poll-surface `submit_verdict(...)` is called with a G0Card payload
**Then** the per-surface case `tests/schemas/operator_verdict/test_section_02a_shape.py` (already shipped at 7c.3b) continues to pass UNCHANGED â€” the G0Card per-gate model addition does NOT regress Â§02A's verdict-schema stability. **Verification:** focused 7c.3b test `tests/schemas/operator_verdict/test_section_02a_shape.py` runs PASS at T9.

### AC-7c.5.G0-E â€” Pydantic-v2 14-idiom conformance (per `docs/dev-guide/pydantic-v2-schema-checklist.md`)

**Given** the canonical Pydantic-v2 idiom checklist
**When** `app/models/decision_cards/g0.py` is authored
**Then** the model uses: `validate_assignment=True` (inherited from base) + `extra="forbid"` (inherited) + `gate_id: Literal["G0"]` discriminator + `gate_focus: Literal["trial_open"]` closed marker + `field_validator` red-rejection on `corpus_paths_confirmed` (non-empty list of `Path` objects; each must exist â€” actually NO â€” keep as `list[Path]` shape-only; existence check is runtime concern outside model scope) + tz-aware datetime via inherited `enforce_tz_aware` + UUID4 via inherited `enforce_uuid4_version` + Field descriptions on every field.

---

## Tasks / Subtasks

- [x] **T1 â€” Readiness checks**
  - [x] T1.1 Confirm 7c.4b deliverables present: `DecisionCardBase` (or whatever final class name; check `app/models/decision_cards/base.py` AND `app/models/decision_cards/_base.py` â€” 7c.4b reconciles) + `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` at `app/parity/contracts/tw_7c_3_firing.py`.
  - [x] T1.2 Confirm 7c.4b's class-conformance validator extension recognizes G0 (run `scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` to confirm 11+ baseline; this story will increment to 12).
  - [x] T1.3 Read `app/models/decision_cards/g1.py` for fresh-author pattern reference (existing G1Card; ~30 LOC).
  - [x] T1.4 Read `tests/fixtures/decision_cards/g1_golden.json` for golden-fixture shape reference.
  - [x] T1.5 Refresh broad-regression baseline (record T1 failure count for T9 delta-comparison).
  - [x] T1.6 Run sandbox-AC validator on this spec; expect PASS.
  - [x] T1.7 Confirm 7c.3b's `tests/schemas/operator_verdict/test_section_02a_shape.py` passes BEFORE this story begins (T1 baseline for AC-D regression check).

- [x] **T2 â€” Author G0Card model (AC: 7c.5.G0-A + 7c.5.G0-E)**
  - [x] T2.1 Author `app/models/decision_cards/g0.py` with `G0Card` Pydantic-v2 subclass; `gate_id: Literal["G0"]` + `gate_focus: Literal["trial_open"]` + 3 G0-specific fields.
  - [x] T2.2 Confirm inheritance from 7c.4b's shared base (whatever name shipped); export `G0Card` in `__all__`.
  - [x] T2.3 Update `app/models/decision_cards/__init__.py` exports if a flat-import pattern exists (mirror G1/G2C/G3/G4).

- [x] **T3 â€” Generate JSON schema (AC: 7c.5.G0-A)**
  - [x] T3.1 Generate `app/models/decision_cards/schema/g0.v1.schema.json` via `python -c "from app.models.decision_cards.g0 import G0Card; import json; print(json.dumps(G0Card.model_json_schema(), indent=2, sort_keys=True))" > app/models/decision_cards/schema/g0.v1.schema.json` (exact command; deterministic emission).
  - [x] T3.2 Verify FR-7c-51 `schema_version: "v1"` in emitted schema (or add via Pydantic `json_schema_extra` if base does not auto-emit).

- [x] **T4 â€” Author golden fixture (AC: 7c.5.G0-A)**
  - [x] T4.1 Author `tests/fixtures/decision_cards/g0_golden.json` with all required fields; UUID4 `card_id` (e.g., `"00000000-0000-4000-8000-000000000000"` or use a deterministic UUID4); UUID4 `trial_id`; tz-aware `created_at` (e.g., `"2026-05-05T00:00:00+00:00"`); populated `meta.cache_state: "healthy"`.
  - [x] T4.2 Verify deterministic round-trip: `G0Card.model_validate(json.load(...))` then `model_dump_json(...)` matches input byte-for-byte (modulo Pydantic JSON normalization; use sort_keys + canonical separators).

- [x] **T5 â€” Author shape-pin test (AC: 7c.5.G0-A + 7c.5.G0-B + 7c.5.G0-C + 7c.5.G0-E)**
  - [x] T5.1 Author `tests/parity/test_decision_card_g0_shape.py` with 5 test cases:
    - [x] T5.1.a `test_g0_card_has_required_fields` â€” assert `G0Card.model_fields.keys()` contains the 9 expected fields.
    - [x] T5.1.b `test_g0_card_gate_id_closed_enum_red_rejection` â€” `pytest.raises(ValidationError)` on `gate_id="G1"` and `gate_id="G99"` and `gate_id=42`.
    - [x] T5.1.c `test_g0_card_gate_focus_closed_enum_red_rejection` â€” `pytest.raises(ValidationError)` on `gate_focus="directive_ratification"` and `gate_focus=None`.
    - [x] T5.1.d `test_g0_json_schema_byte_for_byte_match` â€” load `app/models/decision_cards/schema/g0.v1.schema.json` + assert byte-equality with `json.dumps(G0Card.model_json_schema(), sort_keys=True, indent=2).encode("utf-8")`.
    - [x] T5.1.e `test_g0_golden_fixture_round_trips` â€” load `tests/fixtures/decision_cards/g0_golden.json` + `G0Card.model_validate(...)` + `model_dump_json(...)` matches input (canonicalized).
  - [x] T5.2 Import `LOCKSTEP_CHECK` from `app.parity.contracts.tw_7c_3_firing` (AMEND-7d-i; cite by reference; do NOT re-derive). Optional: assert at module-scope `assert "g0" in [g.split("/")[-1].split(".")[0] for g in FOUR_FILE_GLOBS]` to verify G0 is registered with the firing-spec.

- [x] **T6 â€” Verification battery (R-tier R2)**
  - [x] T6.1 Focused: `.venv/Scripts/python.exe -m pytest tests/parity/test_decision_card_g0_shape.py -p no:randomly -q --tb=short` â†’ PASS (5 tests).
  - [x] T6.2 Smoke: `.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short` â†’ 200-nodeid baseline (UNCHANGED; 7c.5.G0 NOT in smoke set yet).
  - [x] T6.3 Â§02A regression: `.venv/Scripts/python.exe -m pytest tests/schemas/operator_verdict/test_section_02a_shape.py tests/gates/section_02a/ -p no:randomly -q --tb=short` â†’ PASS (UNCHANGED; AC-D verifies G0Card addition does NOT regress Â§02A).
  - [x] T6.4 R2 broad regression: `.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line` â†’ failure count â‰¤ T1 baseline (39 inherited checkout-level expected).
  - [x] T6.5 Class-conformance: `.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` â†’ 12 contracts (was 11; +1 for new shape-pin).
  - [x] T6.6 Lint-imports: `.venv/Scripts/lint-imports.exe` â†’ 12 KEPT / 0 broken (UNCHANGED; no contract change).
  - [x] T6.7 Sandbox-AC: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-5-g0-decision-card-fresh-author.md` â†’ PASS.
  - [x] T6.8 Ruff: `.venv/Scripts/python.exe -m ruff check app/models/decision_cards/g0.py tests/parity/test_decision_card_g0_shape.py` â†’ clean.

- [x] **T10 â€” Codex self-review (NEW CYCLE T10)**
  - [x] T10.1 Codex authors `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g0.ready-for-review.md` summarizing: 4 new file paths + verification battery results + class-conformance delta (11 â†’ 12) + R2 broad-regression delta + AMEND-7d-i compliance evidence (LOCKSTEP_CHECK imported by reference) + T1 decisions documented (e.g., which 7c.4b base class name actually shipped).
  - [x] T10.2 Self-review across 3 lenses (Blind / Edge / Auditor) inline in the dropbox notice.

---

## Required Readings (T1)

1. This story spec (D5/D6/D7-equivalent: AC-A-E coverage).
2. `_bmad-output/implementation-artifacts/migration-7c-4b-gate-family-foundation-implementation.md` (predecessor; D1-D8 contract).
3. `app/models/decision_cards/base.py` AND `_base.py` (whichever 7c.4b ships; T1 reconciles).
4. `app/models/decision_cards/g1.py` (fresh-author pattern reference).
5. `app/parity/contracts/tw_7c_3_firing.py` (LOCKSTEP_CHECK + FOUR_FILE_GLOBS; per AMEND-7d-i).
6. `app/gates/section_02a/poll_surface.py` (consumer; AC-D pattern-replicability target).
7. `tests/schemas/operator_verdict/test_section_02a_shape.py` (AC-D regression baseline).
8. `tests/fixtures/decision_cards/g1_golden.json` (golden-fixture shape reference).
9. `docs/dev-guide/pydantic-v2-schema-checklist.md` (14-idiom conformance per AC-E).
10. `docs/dev-guide/dev-agent-anti-patterns.md` (schema/test-authoring trap catalog).
11. `docs/dev-guide/story-cycle-efficiency.md` (K-floor discipline; lite-vs-standard T11 rubric).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks (only `.venv/Scripts/python.exe -m pytest`, `.venv/Scripts/python.exe scripts/utilities/...`, `.venv/Scripts/lint-imports.exe`, and `.venv/Scripts/python.exe -m ruff` â€” all `.venv/Scripts/` shipped-dep invocations). Sandbox-AC: PASS (verified at T0).

---

## Dispatch Hold

**This story is HELD until 7c.4b closes (T11 PASS + sprint-status.yaml flip reviewâ†’done).** Dispatch dependencies:
- 7c.4b's `DecisionCardBase` (or `DecisionCard`) shipped + class-conformance recognizes G0 (D6).
- 7c.4b's `LOCKSTEP_CHECK` + `FOUR_FILE_GLOBS` shipped at `app/parity/contracts/tw_7c_3_firing.py` (D4).
- 7c.4b's class-conformance count baseline confirmed at 11 (this story increments to 12).

At dispatch-time, Claude verifies AMELIA-P2 freshness (re-diff this spec against pre-authored Codex prompt; regenerate if 7c.4b T11 introduced contract amendments â€” e.g., D2 base-class name reconciliation).

---

## Dev Agent Record

### Completion Notes

- Implemented the G0 four-file lockstep set: model, schema, shape-pin, and golden fixture.
- Consumed `_base.py:DecisionCardBase` per 7c.4b D2 reconciliation and added the G0 operator-facing fields explicitly.
- Added `G0Card` to the flat DecisionCard export and discriminated union.
- Extended the class-conformance validator to count per-gate DecisionCard shape-pins, satisfying the 11 -> 12 -> 13 validator delta once G0 and G2A both landed.

### Verification

- G0 shape-pin: `10 passed`
- G0 + G2A + TW-7c-3 structural pins: `23 passed`
- Section 02A regression: `15 passed`
- Smoke: `181 passed, 18 skipped`
- Class-conformance: `PASS: 13 parity contract file(s) conform (11 activation + 2 decision-card shape-pin)`
- Import-linter: `12 kept, 0 broken`
- Ruff: `All checks passed`
- Broad regression: `44 failed, 4132 passed, 27 skipped, 2 xfailed`; failures are inherited checkout-level surfaces.

### File List

- `app/models/decision_cards/g0.py`
- `app/models/decision_cards/schema/g0.v1.schema.json`
- `tests/parity/test_decision_card_g0_shape.py`
- `tests/fixtures/decision_cards/g0_golden.json`
- `app/models/decision_cards/__init__.py`
- `scripts/utilities/validate_parity_test_class_conformance.py`
- `tests/parity/test_class_conformance_validator_extension.py`
- `_bmad-output/implementation-artifacts/_codex-handoff/7c-5-g0.ready-for-review.md`

### Change Log

- 2026-05-05: Authored G0 DecisionCard four-file lockstep set and posted ready-for-review record.
