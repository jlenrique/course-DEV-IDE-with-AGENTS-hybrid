# Migration Story 7c.12: §07F G2F Motion Gate HIL Surface (FR-7c-16)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=1; predecessors 7c.5.G2C CLOSED at `0ec80df` + 7c.3b CLOSED at `f8fc1a8`. Pre-authored as part of G2C-aliased Wave-3 fanout. AMELIA-P3 stagger AUTO-SATISFIED under single-Codex.)*
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

- [ ] **T1 — Readiness checks** (mirror 7c.9 T1.1-T1.5)
- [ ] **T2 — Author §section package + OperatorVerdict model**
  - [ ] T2.1 `app/gates/section_07f/__init__.py`
  - [ ] T2.2 `app/gates/section_07f/poll_surface.py` per AC-A
  - [ ] T2.3 `app/models/operator_verdict_section_07f.py` per AC-B
- [ ] **T3 — Generate JSON schema (AC-B)**
  - [ ] T3.1 Generate `app/models/operator_verdict_section_07f.v1.schema.json` via:
    ```bash
    .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_07f import Section07FOperatorVerdict; import json; Path('app/models/operator_verdict_section_07f.v1.schema.json').write_text(json.dumps(Section07FOperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
    ```
- [ ] **T4 — Author shape-pin + 3-transport-parity test + DSL-registration audit (AC-C + AC-D)**
- [ ] **T5 — C6 import-linter modules list append (AC-E)**
- [ ] **T6 — Verification battery (R-tier R2)**
- [ ] **T10 — Codex self-review dropbox** at `_codex-handoff/7c-12.ready-for-review.md`

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

(populated by Codex at T1-T10)

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for next-batch G2C-aliased fanout dispatch.
