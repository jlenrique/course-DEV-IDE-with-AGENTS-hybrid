# Migration Story 7c.10: §07B G2M Per-Slide A/B Variant HIL Surface (FR-7c-14)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=1; predecessors 7c.5.G2C CLOSED at `0ec80df` + 7c.3b CLOSED at `f8fc1a8`. Pre-authored as part of G2C-aliased Wave-3 fanout. AMELIA-P3 stagger AUTO-SATISFIED under single-Codex.)*
**Sprint key:** `migration-7c-10-section-07b-g2m-per-slide-variant`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 2; **K-target:** 1.3×; **Estimated LOC:** ~400; **Gate-mode:** single-gate; **R-tier:** R2; **T11-tier:** lite; **Lookahead-tier:** 1.
**Cross-agent review:** false
**files_touched:** 7 new + 1 modified (C6 import-linter contract modules list append)

---

## Story

As the dev-agent,
I want the §07B G2M per-slide A/B variant HIL surface authored as a NEW §section package mirroring the §02A canonical poll-surface pattern,
So that operators can pick A or B variant per slide via mandatory CLI transport (HTTP + MCP-stdio optional per FR-7c-14) emitting `Section07BOperatorVerdict` with verb ∈ {`select`, `edit`, `reject`}, with three-transport schema-stability via FR-7c-49 shape-pin discipline.

---

## Predecessor / Dependency Context

- **7c.5.G2C** (CLOSED `0ec80df`): G2C family DecisionCard contract; G2M aliases to G2C per ADR 0002 §2 (parent family `G2C`; consumer surface "Per-slide A/B variant surface, section 07B"). 7c.10 declares `alias_of="G2C"`.
- **7c.3b** (CLOSED `f8fc1a8`): §02A G0 poll-surface canonical HIL pattern.
- **G2CCard** (closed at 7c.5.G2C `0ec80df`): consumed by §07B G2M poll-surface.
- **Wave-3 sibling pattern** (7c.6/7c.7/7c.8 trio + 7c.13/7c.14 next-batch): canonical references. **7c.14 is closest match** — same select/edit/reject verb-pattern + 3-way verb-payload `model_validator(mode="after")`.
- **G2C-aliased fanout siblings** (7c.9/7c.11/7c.12): concurrent dispatch under single-Codex (AMELIA-P3 auto-satisfied). 4-way C6 modules-list coordinate-or-sequence.
- **C6 import-linter contract** at `pyproject.toml::tool.importlinter`: post-Wave-3-next-batch state has 6 entries. **THIS STORY APPENDS `app.gates.section_07b` to C6's modules list.**

---

## Acceptance Criteria

### AC-7c.10-A — §section package + parity_contract registration (FR-7c-14 + FR-7c-20)

**Given** §02A canonical poll-surface pattern at `app/gates/section_02a/poll_surface.py`
**When** the dev-agent authors `app/gates/section_07b/poll_surface.py`
**Then** the module:
1. Declares `SURFACE_ID = SECTION_07B_SURFACE_ID`.
2. Registers via `@parity_contract(surface_id="section_07b_g2m_per_slide_variant", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"], alias_of="G2C")`.
3. Implements `display_per_slide_variant(g2c_card_or_path: G2CCard | Path) -> dict[str, Any]` (renders A/B variant candidates from G2CCard's per-slide-variant payload).
4. Implements `submit_verdict(slide_id: str, verdict_payload: dict, transport: TransportName) -> Section07BOperatorVerdict`.
5. Re-emits `canonical_model_bytes` + `compute_model_digest` helpers locally per Wave-3 precedent.

### AC-7c.10-B — OperatorVerdict variant + JSON schema regen (FR-7c-49)

**When** the dev-agent authors `app/models/operator_verdict_section_07b.py` + regenerates `app/models/operator_verdict_section_07b.v1.schema.json`:
1. `Section07BOperatorVerdict` Pydantic-v2 model: `surface_id: Literal["section_07b_g2m_per_slide_variant"]` + `verb: Section07BVerdictVerb` (closed `Literal["select", "edit", "reject"]`) + `slide_id: str` (strip-then-non-empty) + standard envelope fields per §02A precedent.
2. `PerSlideVariantPayload` (mandatory iff verb=select; carries `selected_variant: Literal["A", "B"]` + optional `rationale: str | None`).
3. `PerSlideVariantEditPayload` (mandatory iff verb=edit; mirror `DirectiveEditPayload`).
4. JSON schema regenerated via Path.write_text(... encoding="utf-8") per A18. LF-only; NO BOM.

### AC-7c.10-C — Three-transport schema-stability shape-pin (FR-7c-49)

**Then** `tests/schemas/operator_verdict/test_section_07b_shape.py` asserts `Section07BOperatorVerdict` schema hash STABLE across CLI / HTTP / MCP-stdio transports per FR-7c-49 harness.

### AC-7c.10-D — DSL-registration audit + 3-transport-parity test

**Then**:
1. `tests/gates/section_07b/test_g2m_poll_surface_dsl_registration.py` — asserts `parity_contract` registered with correct surface_id + transports + `alias_of="G2C"`. Reload-isolated.
2. `tests/gates/section_07b/test_g2m_poll_surface_three_transport_parity.py` — round-trips a sample G2M variant verdict via CLI + HTTP + MCP-stdio.

### AC-7c.10-E — C6 import-linter modules list append (binding=hard)

**When** the dev-agent updates `pyproject.toml`:
**Then** `app.gates.section_07b` appended to C6 contract `modules` list. Lint-imports re-runs PASS with 12 KEPT. **PARALLEL-DISPATCH GUARDRAIL #3 (binding):** 4-way coordinate-or-sequence with 7c.9/7c.11/7c.12.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks** (mirror 7c.9 T1.1-T1.5)
- [ ] **T2 — Author §section package + OperatorVerdict model**
  - [ ] T2.1 `app/gates/section_07b/__init__.py`
  - [ ] T2.2 `app/gates/section_07b/poll_surface.py` per AC-A
  - [ ] T2.3 `app/models/operator_verdict_section_07b.py` per AC-B
- [ ] **T3 — Generate JSON schema (AC-B)**
  - [ ] T3.1 Generate `app/models/operator_verdict_section_07b.v1.schema.json` via:
    ```bash
    .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_07b import Section07BOperatorVerdict; import json; Path('app/models/operator_verdict_section_07b.v1.schema.json').write_text(json.dumps(Section07BOperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
    ```
- [ ] **T4 — Author shape-pin + 3-transport-parity test + DSL-registration audit (AC-C + AC-D)**
- [ ] **T5 — C6 import-linter modules list append (AC-E)**
- [ ] **T6 — Verification battery (R-tier R2)** (mirror 7c.9 T6.1-T6.9 with §07B substitutions)
- [ ] **T10 — Codex self-review dropbox** at `_codex-handoff/7c-10.ready-for-review.md`

---

## Required Readings (T1)

Same as 7c.9 with §07b/G2M/A/B substitutions. **Closest sibling: 7c.14** (same verb-pattern select/edit/reject + 3-way verb-payload consistency).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS (expected; validator must run pre-dispatch).

---

## Dispatch state

**DISPATCH-READY** post-Wave-3-next-batch close. Per V7 v2 Murat triple-condition (qualifies on all three), 4-story parallel dispatch with 7c.9/7c.11/7c.12 is in-policy under elevated_cap=N+3. AMELIA-P3 stagger auto-satisfied under single-Codex.

---

## Dev Agent Record

(populated by Codex at T1-T10)

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for next-batch G2C-aliased fanout dispatch.
