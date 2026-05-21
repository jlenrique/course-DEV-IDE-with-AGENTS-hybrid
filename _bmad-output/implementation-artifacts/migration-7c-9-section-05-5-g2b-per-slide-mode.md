# Migration Story 7c.9: §05.5 G2B Per-Slide Presentation Mode HIL Surface (FR-7c-13)

**Status:** done *(Codex T1-T10 complete 2026-05-06 + Claude T11 lite PASS-zero-patches at `7c-9-code-review-2026-05-06.md`; focused 13 passed, 4-story focused 52 passed, §02A non-regression 15 passed, sibling HIL regression 43 passed, smoke 181 passed/18 skipped, lint-imports 12 KEPT (C6 6→10 entries via 4-way coordinate-or-sequence), sandbox-AC PASS, ruff clean; broad regression 4352 passed/43 failed UNCHANGED from inherited baseline. Verb-pattern verified: select/edit/reject + closed selected_mode enum + 3-way `model_validator(mode="after")`.)*
**Sprint key:** `migration-7c-9-section-05-5-g2b-per-slide-mode`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 2
**K-target:** 1.3×
**Estimated LOC:** ~400 (poll-surface module ~120 + OperatorVerdict model ~50 + JSON schema ~50 + shape-pin ~80 + 3-transport-parity test ~70 + DSL-registration test ~30)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** lite
**Lookahead-tier:** 1
**files_touched:** 7 new + 1 modified (C6 import-linter contract modules list append)

---

## Story

As the dev-agent,
I want the §05.5 G2B per-slide presentation mode HIL surface authored as a NEW §section package mirroring the §02A canonical poll-surface pattern (closed at 7c.3b),
So that operators can select per-slide presentation mode (narrated-deck vs motion-enabled-narrated-lesson) via mandatory CLI transport (HTTP + MCP-stdio optional per FR-7c-13) emitting `Section05_5OperatorVerdict` with verb ∈ {`select`, `edit`, `reject`}, with three-transport schema-stability via FR-7c-49 shape-pin discipline.

---

## Predecessor / Dependency Context

- **7c.5.G2C** (CLOSED `0ec80df`): G2C family DecisionCard contract; G2B aliases to G2C per ADR 0002 §2 (parent family `G2C`; consumer surface "Per-slide presentation mode surface, section 05.5"). Per ADR 0002 §3 Alias-DSL Clause Inheritance: 7c.9 declares §05.5 G2B's transport coverage via parity_contract decorator with `alias_of="G2C"`.
- **7c.3b** (CLOSED `f8fc1a8`): §02A G0 poll-surface canonical HIL pattern.
- **G2CCard** (closed at 7c.5.G2C `0ec80df`): consumed by §05.5 G2B poll-surface as the operator-facing payload. `from app.models.decision_cards.g2c import G2CCard` (post-G2C-migration; inherits DecisionCardBase).
- **Wave-3 sibling pattern** (7c.6/7c.7/7c.8 trio + 7c.13/7c.14 next-batch): canonical references for §section poll-surface + OperatorVerdict + 3-transport-parity discipline. 7c.6 (mandatory CLI only) is closest sibling for transport-set.
- **G2C-aliased fanout siblings** (7c.10/7c.11/7c.12): concurrent dispatch under single-Codex (AMELIA-P3 auto-satisfied). All four append to C6 modules list — **4-way coordinate-or-sequence on pyproject.toml**.
- **C6 import-linter contract** at `pyproject.toml::tool.importlinter`: post-Wave-3-next-batch state has 6 entries `[section_02a, section_04a, section_04_5, section_04_55, section_08b, section_11]`. **THIS STORY APPENDS `app.gates.section_05_5` to C6's modules list.**

---

## Acceptance Criteria

### AC-7c.9-A — §section package + parity_contract registration (FR-7c-13 + FR-7c-20)

**Given** §02A canonical poll-surface pattern at `app/gates/section_02a/poll_surface.py`
**When** the dev-agent authors `app/gates/section_05_5/poll_surface.py`
**Then** the module:
1. Declares `SURFACE_ID = SECTION_05_5_SURFACE_ID` (constant from new `app/models/operator_verdict_section_05_5.py`).
2. Registers via `@parity_contract(surface_id="section_05_5_g2b_per_slide_mode", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"], alias_of="G2C")` per FR-7c-13 transport requirements + ADR 0002 §3 alias_of forward syntax.
3. Implements `display_per_slide_mode(g2c_card_or_path: G2CCard | Path) -> dict[str, Any]` (poll function; renders per-slide mode candidates from G2CCard's per-slide-mode payload).
4. Implements `submit_verdict(slide_id: str, verdict_payload: dict, transport: TransportName) -> Section05_5OperatorVerdict` (submit function; emits OperatorVerdict).
5. Re-emits `canonical_model_bytes` + `compute_model_digest` helpers locally to satisfy C6 cross-§section independence (per Wave-3 trio + next-batch precedent).

### AC-7c.9-B — OperatorVerdict variant + JSON schema regen (FR-7c-49)

**When** the dev-agent authors `app/models/operator_verdict_section_05_5.py` + regenerates `app/models/operator_verdict_section_05_5.v1.schema.json`:
1. `Section05_5OperatorVerdict` Pydantic-v2 model: `surface_id: Literal["section_05_5_g2b_per_slide_mode"]` + `verb: Section05_5VerdictVerb` (closed `Literal["select", "edit", "reject"]`) + `slide_id: str` (non-empty; strip-then-non-empty per G2A pattern) + standard envelope fields per §02A precedent (run_id UUID4 + operator_id pattern + submitted_at tz-aware + decision_card_digest sha256 + verb-payload consistency `model_validator(mode="after")`).
2. `PerSlideModePayload` (mandatory iff verb=select; carries `selected_mode: Literal["narrated-deck", "motion-enabled-narrated-lesson"]` + optional `rationale: str | None`).
3. `PerSlideModeEditPayload` (mandatory iff verb=edit; mirror `DirectiveEditPayload` shape).
4. JSON schema regenerated via Path.write_text(... encoding="utf-8") canonical command (anti-pattern A18). LF-only; NO BOM.

### AC-7c.9-C — Three-transport schema-stability shape-pin (FR-7c-49)

**Then** `tests/schemas/operator_verdict/test_section_05_5_shape.py` asserts `Section05_5OperatorVerdict` schema hash STABLE across CLI / HTTP / MCP-stdio transports per FR-7c-49 harness pattern. Use `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section05_5OperatorVerdict, surface_id="section_05_5_g2b_per_slide_mode", transports=["cli", "http", "mcp-stdio"])` from `tests/schemas/operator_verdict/_harness.py`.

### AC-7c.9-D — DSL-registration audit + 3-transport-parity test

**Then**:
1. `tests/gates/section_05_5/test_g2b_poll_surface_dsl_registration.py` — asserts `parity_contract` registered with correct surface_id + transports + `alias_of="G2C"`. **Reload-isolated** to avoid shared-registry ordering flake under xdist (per Wave-3 precedent).
2. `tests/gates/section_05_5/test_g2b_poll_surface_three_transport_parity.py` — round-trips a sample G2B per-slide-mode verdict via CLI + HTTP + MCP-stdio simulated transports; asserts payload digest equals across all three.

### AC-7c.9-E — C6 import-linter modules list append (binding=hard per 7c.4b D5)

**When** the dev-agent updates `pyproject.toml`:
**Then** `app.gates.section_05_5` appended to C6 contract `modules` list. Lint-imports re-runs PASS with 12 KEPT (UNCHANGED count). **PARALLEL-DISPATCH GUARDRAIL #3 (binding):** if 7c.10/7c.11/7c.12 dispatch concurrently, **4-way coordinate-or-sequence** — main thread (or whichever worker integrates first) writes the union of all four new §section entries (`section_05_5 + section_07b + section_07d + section_07f`); subsequent workers rebase before commit.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks**
  - [x] T1.1 Confirm 7c.5.G2C + 7c.3b done in sprint-status; confirm Wave-3 trio + 7c.13/7c.14 closed (reference patterns).
  - [x] T1.2 Read §02A canonical pattern + Wave-3 trio + 7c.13/7c.14 sibling pattern for re-emit-helpers C6-isolation.
  - [x] T1.3 Read `app/models/decision_cards/g2c.py` (POST-G2C-migration; inherits DecisionCardBase) for G2CCard consumption.
  - [x] T1.4 Read ADR 0002 §3 for alias_of forward syntax.
  - [x] T1.5 Refresh broad-regression baseline + record class-conformance baseline.

- [x] **T2 — Author §section package + OperatorVerdict model**
  - [x] T2.1 Author `app/gates/section_05_5/__init__.py` (empty namespace).
  - [x] T2.2 Author `app/gates/section_05_5/poll_surface.py` per AC-A.
  - [x] T2.3 Author `app/models/operator_verdict_section_05_5.py` per AC-B with `Section05_5OperatorVerdict` + `PerSlideModePayload` + `PerSlideModeEditPayload` + `Section05_5VerdictVerb` + `SECTION_05_5_SURFACE_ID`.

- [x] **T3 — Generate JSON schema (AC-B)**
  - [x] T3.1 Generate `app/models/operator_verdict_section_05_5.v1.schema.json` via:
    ```bash
    .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_05_5 import Section05_5OperatorVerdict; import json; Path('app/models/operator_verdict_section_05_5.v1.schema.json').write_text(json.dumps(Section05_5OperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
    ```
    (Path.write_text per A18; NO PowerShell `>` redirection.)

- [x] **T4 — Author shape-pin + 3-transport-parity test + DSL-registration audit (AC-C + AC-D)**
  - [x] T4.1 Author `tests/schemas/operator_verdict/test_section_05_5_shape.py`.
  - [x] T4.2 Author `tests/gates/section_05_5/__init__.py` + `_helpers.py`.
  - [x] T4.3 Author `tests/gates/section_05_5/test_g2b_poll_surface_dsl_registration.py` (reload-isolated).
  - [x] T4.4 Author `tests/gates/section_05_5/test_g2b_poll_surface_three_transport_parity.py`.

- [x] **T5 — C6 import-linter modules list append (AC-E)**
  - [x] T5.1 Update `pyproject.toml::tool.importlinter::contracts::C6::modules` to append `app.gates.section_05_5`. **PARALLEL-DISPATCH GUARDRAIL #3:** 4-way coordinate-or-sequence with concurrent 7c.10/7c.11/7c.12.

- [x] **T6 — Verification battery (R-tier R2)**
  - [x] T6.1 Focused: `pytest tests/gates/section_05_5/ tests/schemas/operator_verdict/test_section_05_5_shape.py -p no:randomly -q --tb=short` PASS.
  - [x] T6.2 §02A non-regression PASS UNCHANGED.
  - [x] T6.3 Wave-3 trio + 7c.13/7c.14 non-regression PASS UNCHANGED.
  - [x] T6.4 Smoke baseline UNCHANGED.
  - [x] T6.5 R2 broad: failure count ≤ T1 baseline (delta ≤ 0); per-failure git-log-attribution.
  - [x] T6.6 Class-conformance: T1-baseline + 1 (new shape-pin file).
  - [x] T6.7 Lint-imports: 12 KEPT / 0 broken.
  - [x] T6.8 Sandbox-AC: PASS.
  - [x] T6.9 Ruff: clean.

- [x] **T10 — Codex self-review dropbox**
  - [x] T10.1 Drop `_codex-handoff/7c-9.ready-for-review.md`.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor).
3. `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` + `migration-7c-14-section-11-g4a-voice-selection.md` (closest sibling references — most recently closed Wave-3-follower pattern).
4. `app/gates/section_02a/poll_surface.py` (canonical pattern reference).
5. `app/gates/section_04a/poll_surface.py` + `section_08b/poll_surface.py` (Wave-3 sibling re-emit patterns; CLI-mandatory match for 7c.9).
6. `app/models/operator_verdict_section_02a.py` + `operator_verdict_section_04a.py` (canonical + sibling OperatorVerdict variants).
7. `tests/schemas/operator_verdict/_harness.py` (FR-7c-49 harness; READ-ONLY).
8. `tests/schemas/operator_verdict/test_section_02a_shape.py` + Wave-3 sibling shape-pins.
9. `tests/gates/section_02a/*.py` + Wave-3 sibling DSL-registration + 3-transport-parity tests.
10. `app/models/decision_cards/g2c.py` (POST-7c.5.G2C-migration; inherits DecisionCardBase per 0ec80df; G2CCard consumed by §05.5 surface).
11. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax per 7c.4b D1).
12. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G2B alias mapping per §2).
13. `pyproject.toml::tool.importlinter` (C6 contract; current 6-entry state).
14. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
15. Governance JSON `7c-9` entry + `wave_3_lookahead_policy::current_cap=3` (V7 v2 promoted post-Wave-3-trio close).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS (expected; validator must run pre-dispatch).

---

## Dispatch state

**DISPATCH-READY** post-Wave-3-next-batch close. Per V7 v2 Murat triple-condition (C6 ∧ lookahead_tier=1 ∧ t11_tier=lite — qualifies on all three), 4-story parallel dispatch with 7c.10/7c.11/7c.12 is in-policy under elevated_cap=N+3. AMELIA-P3 stagger auto-satisfied under single-Codex.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

- T1: Confirmed 7c.5.G2C, 7c.3b, Wave-3 trio, and 7c.13/7c.14 closed context; class-conformance baseline observed at 19.
- T2-T5: Worker authored `section_05_5` package, verdict model, LF-only schema, shape-pin, DSL audit, and 3-transport parity tests. Main thread applied the 4-way C6 union append.
- T6: Focused §05.5 suite `13 passed`; integrated 4-story focused suite `52 passed`; §02A non-regression `15 passed`; sibling HIL regression `43 passed`; smoke `181 passed, 18 skipped`; lint-imports `12 kept, 0 broken`; sandbox-AC PASS; ruff clean.
- T6 broad: `4352 passed, 43 failed, 27 skipped, 2 xfailed`; inherited failure count unchanged. `test_resume_api_authority` remains inherited and now lists new verdict-model paths in the already-failing direct-constructor scanner.

### Completion Notes List

- Implemented Section 05.5 G2B per-slide presentation-mode HIL surface with `alias_of="G2C"` and CLI mandatory / HTTP+MCP-stdio optional transport declaration.
- Added `Section05_5OperatorVerdict`, `PerSlideModePayload`, `PerSlideModeEditPayload`, LF-only JSON schema, FR-7c-49 shape-pin, reload-isolated DSL audit, and 3-transport parity tests.
- Coordinated shared C6 import-linter edit as a 4-way union append with 7c.10/7c.11/7c.12.

### File List

- `app/gates/section_05_5/__init__.py`
- `app/gates/section_05_5/poll_surface.py`
- `app/models/operator_verdict_section_05_5.py`
- `app/models/operator_verdict_section_05_5.v1.schema.json`
- `tests/gates/section_05_5/__init__.py`
- `tests/gates/section_05_5/_helpers.py`
- `tests/gates/section_05_5/test_g2b_poll_surface_dsl_registration.py`
- `tests/gates/section_05_5/test_g2b_poll_surface_three_transport_parity.py`
- `tests/schemas/operator_verdict/test_section_05_5_shape.py`
- `_bmad-output/implementation-artifacts/migration-7c-9-section-05-5-g2b-per-slide-mode.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_codex-handoff/7c-9.ready-for-review.md`
- `pyproject.toml`

### Change Log

- 2026-05-06: Codex implemented 7c.9 through T10 and moved story to review.
- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for next-batch G2C-aliased fanout dispatch.
