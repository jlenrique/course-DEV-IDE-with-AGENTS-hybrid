# Migration Story 7c.12: §07F G2F Motion Gate HIL Surface (FR-7c-16)

**Status:** done *(Codex T1-T10 complete 2026-05-06 + Claude T11 lite PASS-zero-patches at `7c-12-code-review-2026-05-06.md`; focused 13 passed, 4-story focused 52 passed, §02A non-regression 15 passed, sibling HIL regression 43 passed, smoke 181 passed/18 skipped, lint-imports 12 KEPT (C6 6→10 entries), sandbox-AC PASS, ruff clean; broad regression 4352 passed/43 failed UNCHANGED. Verb-pattern verified: approve/edit/reject + 2-way `model_validator(mode="after")` mirrors §02A canonical + 7c.13 sibling. Transport-set IDENTICAL to 7c.13: CLI+HTTP-mandatory + MCP-stdio-optional. **Wave-3 G2C-aliased fanout COMPLETE.**)*
**Sprint key:** `migration-7c-12-section-07f-g2f-motion-gate`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 2; **K-target:** 1.3×; **Estimated LOC:** ~400; **Gate-mode:** single-gate; **R-tier:** R2; **T11-tier:** lite; **Lookahead-tier:** 1.
**Cross-agent review:** false
**files_touched:** 7 new + 1 modified (C6 import-linter contract modules list append)

---

## Story

As the dev-agent,
I want the §07F G2F motion gate HIL surface authored as a NEW §section package mirroring the §02A canonical poll-surface pattern,
So that operators can approve/edit/reject motion-clip output via mandatory CLI + HTTP transports (MCP-stdio optional per FR-7c-16) emitting `Section07FOperatorVerdict` with verb ∈ {`approve`, `edit`, `reject`}, with three-transport schema-stability via FR-7c-49 shape-pin discipline.

---

## Predecessor / Dependency Context

- **7c.5.G2C** (CLOSED `0ec80df`): G2C family DecisionCard contract; G2F aliases to G2C per ADR 0002 §2 (parent family `G2C`; consumer surface "Motion-clip approval surface, section 07F"). 7c.12 declares `alias_of="G2C"`.
- **7c.3b** (CLOSED `f8fc1a8`): §02A G0 poll-surface canonical HIL pattern.
- **G2CCard** (closed at 7c.5.G2C `0ec80df`): consumed by §07F G2F poll-surface (motion-clip output payload).
- **Wave-3 sibling pattern** (7c.6/7c.7/7c.8 trio + 7c.13/7c.14 next-batch): canonical references. **7c.13 is closest match** — same CLI+HTTP-mandatory transport-set + approve/edit/reject verb-pattern (review framing).
- **G2C-aliased fanout siblings** (7c.9/7c.10/7c.11): concurrent dispatch under single-Codex. 4-way C6 modules-list coordinate-or-sequence.
- **C6 import-linter contract** at `pyproject.toml::tool.importlinter`: post-Wave-3-next-batch state has 6 entries. **THIS STORY APPENDS `app.gates.section_07f` to C6's modules list.**

---

## Acceptance Criteria

### AC-7c.12-A — §section package + parity_contract registration (FR-7c-16 + FR-7c-20)

**Given** §02A canonical poll-surface pattern at `app/gates/section_02a/poll_surface.py`
**When** the dev-agent authors `app/gates/section_07f/poll_surface.py`
**Then** the module:
1. Declares `SURFACE_ID = SECTION_07F_SURFACE_ID`.
2. Registers via `@parity_contract(surface_id="section_07f_g2f_motion_gate", mandatory_transports=["cli", "http"], optional_transports=["mcp-stdio"], alias_of="G2C")`.
3. Implements `display_motion_clip(g2c_card_or_path: G2CCard | Path) -> dict[str, Any]` (renders motion-clip output for review).
4. Implements `submit_verdict(motion_clip_id: str, verdict_payload: dict, transport: TransportName) -> Section07FOperatorVerdict`.
5. Re-emits `canonical_model_bytes` + `compute_model_digest` helpers locally per Wave-3 precedent.

### AC-7c.12-B — OperatorVerdict variant + JSON schema regen (FR-7c-49)

**When** the dev-agent authors `app/models/operator_verdict_section_07f.py` + regenerates `app/models/operator_verdict_section_07f.v1.schema.json`:
1. `Section07FOperatorVerdict` Pydantic-v2 model: `surface_id: Literal["section_07f_g2f_motion_gate"]` + `verb: Section07FVerdictVerb` (closed `Literal["approve", "edit", "reject"]`) + `motion_clip_id: str` (strip-then-non-empty) + standard envelope fields per §02A precedent.
2. `MotionClipEditPayload` (mandatory iff verb=edit; mirror `DirectiveEditPayload`).
3. JSON schema regenerated via Path.write_text(... encoding="utf-8") per A18. LF-only; NO BOM.

### AC-7c.12-C — Three-transport schema-stability shape-pin (FR-7c-49)

**Then** `tests/schemas/operator_verdict/test_section_07f_shape.py` asserts `Section07FOperatorVerdict` schema hash STABLE across CLI / HTTP / MCP-stdio transports per FR-7c-49 harness.

### AC-7c.12-D — DSL-registration audit + 3-transport-parity test

**Then**:
1. `tests/gates/section_07f/test_g2f_poll_surface_dsl_registration.py` — asserts `parity_contract` registered with correct surface_id + transports + `alias_of="G2C"`. Reload-isolated.
2. `tests/gates/section_07f/test_g2f_poll_surface_three_transport_parity.py` — round-trips a sample G2F motion-clip approval verdict via CLI + HTTP + MCP-stdio.

### AC-7c.12-E — C6 import-linter modules list append (binding=hard)

**When** the dev-agent updates `pyproject.toml`:
**Then** `app.gates.section_07f` appended to C6 contract `modules` list. Lint-imports re-runs PASS with 12 KEPT. **PARALLEL-DISPATCH GUARDRAIL #3 (binding):** 4-way coordinate-or-sequence with 7c.9/7c.10/7c.11.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks** (mirror 7c.9 T1.1-T1.5)
- [x] **T2 — Author §section package + OperatorVerdict model**
  - [x] T2.1 `app/gates/section_07f/__init__.py`
  - [x] T2.2 `app/gates/section_07f/poll_surface.py` per AC-A
  - [x] T2.3 `app/models/operator_verdict_section_07f.py` per AC-B
- [x] **T3 — Generate JSON schema (AC-B)**
  - [x] T3.1 Generate `app/models/operator_verdict_section_07f.v1.schema.json` via:
    ```bash
    .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_07f import Section07FOperatorVerdict; import json; Path('app/models/operator_verdict_section_07f.v1.schema.json').write_text(json.dumps(Section07FOperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
    ```
- [x] **T4 — Author shape-pin + 3-transport-parity test + DSL-registration audit (AC-C + AC-D)**
- [x] **T5 — C6 import-linter modules list append (AC-E)**
- [x] **T6 — Verification battery (R-tier R2)**
- [x] **T10 — Codex self-review dropbox** at `_codex-handoff/7c-12.ready-for-review.md`

---

## Required Readings (T1)

Same as 7c.9 with §07f/G2F substitutions. **Closest sibling: 7c.13** (same CLI+HTTP-mandatory + approve/edit/reject verb-pattern).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS (expected; validator must run pre-dispatch).

---

## Dispatch state

**DISPATCH-READY** post-Wave-3-next-batch close. Per V7 v2 Murat triple-condition (qualifies on all three), 4-story parallel dispatch with 7c.9/7c.10/7c.11 is in-policy under elevated_cap=N+3. AMELIA-P3 stagger auto-satisfied under single-Codex.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

- T1: Confirmed 7c.5.G2C, 7c.3b, Wave-3 trio, and 7c.13/7c.14 closed context; class-conformance baseline observed at 19.
- T2-T5: Worker authored `section_07f` package, verdict model, LF-only schema, shape-pin, DSL audit, and 3-transport parity tests. Main thread applied the 4-way C6 union append.
- T6: Focused §07F suite `13 passed`; integrated 4-story focused suite `52 passed`; §02A non-regression `15 passed`; sibling HIL regression `43 passed`; smoke `181 passed, 18 skipped`; lint-imports `12 kept, 0 broken`; sandbox-AC PASS; ruff clean.
- T6 broad: `4352 passed, 43 failed, 27 skipped, 2 xfailed`; inherited failure count unchanged. `test_resume_api_authority` remains inherited and now lists new verdict-model paths in the already-failing direct-constructor scanner.

### Completion Notes List

- Implemented Section 07F G2F motion-clip approval HIL surface with `alias_of="G2C"` and CLI+HTTP mandatory / MCP-stdio optional transport declaration.
- Added `Section07FOperatorVerdict`, `MotionClipEditPayload`, LF-only JSON schema, FR-7c-49 shape-pin, reload-isolated DSL audit, and 3-transport parity tests.
- Coordinated shared C6 import-linter edit as a 4-way union append with 7c.9/7c.10/7c.11.

### File List

- `app/gates/section_07f/__init__.py`
- `app/gates/section_07f/poll_surface.py`
- `app/models/operator_verdict_section_07f.py`
- `app/models/operator_verdict_section_07f.v1.schema.json`
- `tests/gates/section_07f/__init__.py`
- `tests/gates/section_07f/_helpers.py`
- `tests/gates/section_07f/test_g2f_poll_surface_dsl_registration.py`
- `tests/gates/section_07f/test_g2f_poll_surface_three_transport_parity.py`
- `tests/schemas/operator_verdict/test_section_07f_shape.py`
- `_bmad-output/implementation-artifacts/migration-7c-12-section-07f-g2f-motion-gate.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_codex-handoff/7c-12.ready-for-review.md`
- `pyproject.toml`

### Change Log

- 2026-05-06: Codex implemented 7c.12 through T10 and moved story to review.
- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for next-batch G2C-aliased fanout dispatch.
