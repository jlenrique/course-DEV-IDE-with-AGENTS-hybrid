# Migration Story 7c.17a: 3 Marcus-Bound Writers — Slide-Content + Fidelity-Slides + Diagram-Cards (Shared-Sanctum Partition; FR-7c-21 + FR-7c-22 + FR-7c-23 + FR-7c-54)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=1; predecessor 7c.0b CLOSED — sanctum-alignment DSL primitive at `app.parity.contracts._sanctum` shipped + queryable; the 5 writer_ids enumerated in 7c.0b AC-B are canonical for THIS story's 3 writers + 7c.17b's 2 writers. Marcus sanctum BMB-aligned at `_bmad/memory/bmad-agent-marcus/`. AMELIA-P2 sandbox-AC PASS expected pre-dispatch.)*
**Sprint key:** `migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 2
**K-target:** 1.3×
**Estimated LOC:** ~600 (3 writer modules ~120 each = 360 + 3 schema regen ~30 each = 90 + writers/__init__.py ~10 + 4 tests ~70 each = 280; minus shared-helper consolidation)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** lite (per governance JSON entry `7c-17a`; AC count ≤5 + Marcus orchestrator-namespace sibling files + new schemas under sanctum-pinned `_bmad/memory/bmad-agent-marcus/schemas/` + no parity-DSL contract evolution + no governance/pipeline-manifest touch + single-gate)
**Lookahead-tier:** 1
**files_touched:** 12 new + 0 modified

---

## Story

As Marcus,
I want to emit `gary-slide-content.json` + `gary-fidelity-slides.json` + `gary-diagram-cards.json` per plan unit prior to Gary dispatch, with each writer module declaring its sanctum-alignment row via the FR-7c-54 DSL primitive,
So that Gary receives the text+payload-shape pre-dispatch package with Vera-fidelity-criteria-prepopulated payload + literal-visual diagram requirements, with operational sanctum-alignment evidence preserved across activations.

This story implements the **shared-sanctum partition** half of the Wave-4 Marcus-writer split per **Winston W5 architectural partition principle**: 3 writers sharing a *transport boundary* (text + payload-shape pre-dispatch with Vera-fidelity criteria as the unifying contract). NOT a process partition. The complement is 7c.17b (theme-resolution + outbound-envelope; divergent-sanctum partition + envelope aggregation). Future maintenance of the 5 writers inherits this partition logic; cross-story refactors will respect it.

---

## Predecessor / Dependency Context

- **7c.0b** (CLOSED 2026-05-04): sanctum-alignment DSL primitive at `app.parity.contracts._sanctum` (FR-7c-54) shipped + queryable via `iter_sanctum_alignments()` + manifest emission via `emit_sanctum_alignment_manifest()`. The 5 writer_ids listed in 7c.0b AC-B examples (`gary-slide-content`, `gary-fidelity-slides`, `gary-diagram-cards`, `gary-theme-resolution`, `gary-outbound-envelope`) are the canonical identifiers for this story's 3 writers + 7c.17b's 2 writers.
- **7b.6** (CLOSED `1f81965` 2026-04-30): Gary Class-C body activation — sibling specialist who consumes this story's output downstream. Gary's sanctum at `_bmad/memory/bmad-agent-gary/` is BMB-pattern aligned. **NOT modified by this story** (read-only sibling reference).
- **7b.3** (CLOSED `1f81965` 2026-04-30): Vera Class-A hardening — Vera's fidelity-verdict producer. THIS STORY's `gary-fidelity-slides` writer carries Vera's pre-resolved fidelity criteria in its emitted payload (FR-7c-22). The wiring "who reads Vera's verdict and feeds it into the writer call" is OUT OF SCOPE here — this story emits the payload SHAPE; integration is a downstream concern.
- **Marcus sanctum** at `_bmad/memory/bmad-agent-marcus/`: BMB-pattern aligned (6 canonical files: INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES). The new `schemas/` subdirectory is created by THIS STORY (greenfield).
- **Marcus M1-M4 import-linter contracts** (`pyproject.toml::tool.importlinter`): the writers/ namespace under `app.marcus.orchestrator.writers/` falls under the existing M1-M4 contract scope and inherits M3 (specialists may not import them) + M4 (dispatch stays dependency-light) BY CONSTRUCTION. **No pyproject.toml edit required.**
- **7c.13/7c.14 next-batch + 7c.6/7c.7/7c.8 trio + 7c.9/7c.10/7c.11/7c.12 fanout** (CLOSED 2026-05-06): canonical references for Pydantic-v2 model + LF-only schema regen pattern via `Path.write_text(... encoding="utf-8")` (anti-pattern A18) and shape-pin discipline. **Read-only sibling references.**

---

## Acceptance Criteria

### AC-7c.17a-A — `app/marcus/orchestrator/writers/` namespace + slide-content writer (FR-7c-21 + FR-7c-54)

**Given** the new `app/marcus/orchestrator/writers/` namespace + the FR-7c-54 sanctum-alignment DSL at `app.parity.contracts`
**When** the dev-agent authors `app/marcus/orchestrator/writers/__init__.py` (empty namespace) + `app/marcus/orchestrator/writers/slide_content.py`
**Then** the slide-content module:
1. Declares Pydantic-v2 model `GarySlideContent` with `model_config = ConfigDict(extra="forbid", validate_assignment=True)` capturing the per-plan-unit slide content payload: `plan_unit_id: str` (`min_length=1` + strip-then-non-empty validator per Wave-3 G2A canonical), `target_section: str` (`min_length=1`), `slides: list[SlideContentEntry]` (`min_length=1`), `schema_version: int = 1` (per FR-7c-51 schema_version discipline).
2. Declares `SlideContentEntry` sub-model: `slide_index: int` (`ge=1`), `title: str` (`min_length=1`), `body: str` (`min_length=1`), `content_kind: SlideContentKind` (closed `Literal[...]` — minimum set: `{"narrative", "exposition", "summary"}`; widening requires party-mode consensus).
3. Implements `emit_gary_slide_content(payload: GarySlideContent, output_path: Path) -> Path` — writes JSON via `output_path.write_text(json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8")` per A18 (LF-only, NO BOM). Returns `output_path`.
4. At module import time, calls `declare_sanctum_alignment(writer_id="gary-slide-content", sanctum_path="_bmad/memory/bmad-agent-marcus/")` per FR-7c-54 (alignment_kind defaults to `"bmb-pattern"` since Marcus sanctum is BMB-aligned).

### AC-7c.17a-B — fidelity-slides writer (FR-7c-22 + FR-7c-54)

**When** the dev-agent authors `app/marcus/orchestrator/writers/fidelity_slides.py`
**Then** the module:
1. Declares Pydantic-v2 model `GaryFidelitySlides` (same `ConfigDict(extra="forbid", validate_assignment=True)` discipline) capturing the Vera-fidelity-criteria-prepopulated payload: `plan_unit_id: str` (strip-then-non-empty), `target_section: str`, `vera_criteria: list[VeraFidelityCriterion]` (`min_length=1`), `schema_version: int = 1`.
2. Declares `VeraFidelityCriterion` sub-model: `criterion_id: str` (`min_length=1`), `severity: FidelitySeverity` (closed `Literal["MUST", "SHOULD", "MAY"]` per Vera contract), `description: str` (`min_length=1`), `vera_source_ref: str | None` (provenance pointer for cross-reference to §06 Vera contract — non-blocking pointer; null permitted to keep this story decoupled from Vera-output integration).
3. Implements `emit_gary_fidelity_slides(payload: GaryFidelitySlides, output_path: Path) -> Path` per the same Path.write_text + A18 discipline.
4. At module import time, calls `declare_sanctum_alignment(writer_id="gary-fidelity-slides", sanctum_path="_bmad/memory/bmad-agent-marcus/")`.

### AC-7c.17a-C — diagram-cards writer (FR-7c-23 + FR-7c-54)

**When** the dev-agent authors `app/marcus/orchestrator/writers/diagram_cards.py`
**Then** the module:
1. Declares Pydantic-v2 model `GaryDiagramCards` capturing the literal-visual diagram requirements payload: `plan_unit_id: str`, `target_section: str`, `cards: list[DiagramCard]` (`min_length=1`), `schema_version: int = 1`.
2. Declares `DiagramCard` sub-model: `slide_index: int` (`ge=1`), `visual_kind: DiagramVisualKind` (closed `Literal[...]` — minimum set: `{"flowchart", "sequence", "comparison", "literal-visual"}`), `specification: str` (`min_length=1` — operator-authored per-slide visual specification), `caption: str | None` (optional rendering caption).
3. Implements `emit_gary_diagram_cards(payload: GaryDiagramCards, output_path: Path) -> Path` per A18 discipline.
4. At module import time, calls `declare_sanctum_alignment(writer_id="gary-diagram-cards", sanctum_path="_bmad/memory/bmad-agent-marcus/")`.

### AC-7c.17a-D — JSON schema regen for 3 writers under Marcus sanctum (FR-7c-51 schema_version discipline)

**When** the dev-agent regenerates 3 JSON schemas under `_bmad/memory/bmad-agent-marcus/schemas/`:
**Then** each schema lands at:
- `_bmad/memory/bmad-agent-marcus/schemas/gary-slide-content.schema.json`
- `_bmad/memory/bmad-agent-marcus/schemas/gary-fidelity-slides.schema.json`
- `_bmad/memory/bmad-agent-marcus/schemas/gary-diagram-cards.schema.json`

Each generated via the canonical Path.write_text command (per A18) — NOT PowerShell `>` redirection:
```bash
.venv/Scripts/python.exe -c "from pathlib import Path; from app.marcus.orchestrator.writers.slide_content import GarySlideContent; import json; Path('_bmad/memory/bmad-agent-marcus/schemas/gary-slide-content.schema.json').write_text(json.dumps(GarySlideContent.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
```
LF-only; NO BOM; deterministic byte output across Codex re-invocations.

### AC-7c.17a-E — Shape-pin tests + sanctum-registry test under `tests/marcus/orchestrator/writers/`

**Then** the dev-agent authors:
1. `tests/marcus/orchestrator/writers/__init__.py` (empty namespace).
2. `tests/marcus/orchestrator/writers/test_slide_content.py` — covers (a) valid payload round-trip via `model_validate` + `emit_gary_slide_content` writes LF-only JSON byte-equivalent to schema; (b) closed-enum red-rejection on `SlideContentKind`; (c) strip-then-non-empty red-rejection on `plan_unit_id`; (d) JSON schema hash STABLE pin (`hashlib.sha256(json.dumps(GarySlideContent.model_json_schema(), sort_keys=True).encode()).hexdigest()` matches a frozen literal asserted in the test).
3. `tests/marcus/orchestrator/writers/test_fidelity_slides.py` — same shape; covers `VeraFidelityCriterion` closed-enum severity + `vera_source_ref` null-permitted path.
4. `tests/marcus/orchestrator/writers/test_diagram_cards.py` — same shape; covers `DiagramVisualKind` closed-enum.
5. `tests/marcus/orchestrator/writers/test_sanctum_alignments.py` — imports the 3 writer modules (triggering module-import-time `declare_sanctum_alignment` calls) + asserts `iter_sanctum_alignments()` registry contains the 3 writer_ids `gary-slide-content`, `gary-fidelity-slides`, `gary-diagram-cards` with `sanctum_path="_bmad/memory/bmad-agent-marcus/"` and `alignment_kind="bmb-pattern"`. Uses the `_clear_sanctum_alignments_for_tests` fixture pattern from `tests/parity/test_sanctum_alignment_dsl.py` to keep registry hermetic across test runs (per Slab-7b precedent for shared-registry hygiene).

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.0b done in sprint-status; `app.parity.contracts._sanctum` importable + DSL surface stable (`declare_sanctum_alignment`, `iter_sanctum_alignments`, `SanctumAlignmentDeclaration`, `_clear_sanctum_alignments_for_tests`).
  - [ ] T1.2 Read `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` §AC-7c.0b-B for sanctum-alignment DSL contract.
  - [ ] T1.3 Read `tests/parity/test_sanctum_alignment_dsl.py` for canonical DSL usage + clear-fixture pattern.
  - [ ] T1.4 Read `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (Wave-3 next-batch sibling reference for Pydantic-v2 + LF-only schema regen + shape-pin discipline).
  - [ ] T1.5 Read existing Marcus orchestrator modules for namespace + import-style sibling reference: `app/marcus/orchestrator/specialist_summary_writer.py` + `app/marcus/orchestrator/__init__.py`.
  - [ ] T1.6 Confirm Marcus sanctum BMB-aligned (6 canonical files at `_bmad/memory/bmad-agent-marcus/`); no SKILL.md frontmatter touch required.
  - [ ] T1.7 Refresh broad-regression baseline + record class-conformance baseline.

- [ ] **T2 — Author writers/ namespace + slide_content writer (AC-A)**
  - [ ] T2.1 Author `app/marcus/orchestrator/writers/__init__.py` (empty namespace; package-marker only — do NOT re-export writer functions to keep import surface lazy).
  - [ ] T2.2 Author `app/marcus/orchestrator/writers/slide_content.py` per AC-A: `GarySlideContent` + `SlideContentEntry` + `SlideContentKind` + `emit_gary_slide_content` + module-import-time `declare_sanctum_alignment`.

- [ ] **T3 — Author fidelity_slides writer (AC-B)**
  - [ ] T3.1 Author `app/marcus/orchestrator/writers/fidelity_slides.py` per AC-B.

- [ ] **T4 — Author diagram_cards writer (AC-C)**
  - [ ] T4.1 Author `app/marcus/orchestrator/writers/diagram_cards.py` per AC-C.

- [ ] **T5 — Generate 3 JSON schemas under Marcus sanctum (AC-D)**
  - [ ] T5.1 Create `_bmad/memory/bmad-agent-marcus/schemas/` directory.
  - [ ] T5.2 Generate 3 schemas via the canonical Path.write_text command pattern (per A18). LF-only; NO BOM. **PARALLEL-DISPATCH NOTE:** if 7c.17b dispatches concurrently, the `_bmad/memory/bmad-agent-marcus/schemas/` directory creation is path-disjoint per file (5 distinct schema filenames), but the directory itself is shared — first-mover creates; subsequent rebases.

- [ ] **T6 — Author shape-pin tests + sanctum-registry test (AC-E)**
  - [ ] T6.1 Author `tests/marcus/orchestrator/writers/__init__.py`.
  - [ ] T6.2 Author per-writer shape-pin tests (`test_slide_content.py`, `test_fidelity_slides.py`, `test_diagram_cards.py`).
  - [ ] T6.3 Author `tests/marcus/orchestrator/writers/test_sanctum_alignments.py` with `_clear_sanctum_alignments_for_tests` autouse fixture per `tests/parity/test_sanctum_alignment_dsl.py` precedent.

- [ ] **T7 — Verification battery (R-tier R2; T11-tier lite)**
  - [ ] T7.1 Focused: `.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/writers/ -p no:randomly -q --tb=short` PASS.
  - [ ] T7.2 DSL non-regression: `.venv/Scripts/python.exe -m pytest tests/parity/test_sanctum_alignment_dsl.py -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [ ] T7.3 §02A non-regression: `.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [ ] T7.4 Wave-3 closed §section non-regression sweep: `.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_05_5/ tests/gates/section_07b/ tests/gates/section_07d/ tests/gates/section_07f/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [ ] T7.5 Marcus orchestrator non-regression: `.venv/Scripts/python.exe -m pytest tests/marcus/ -p no:randomly -q --tb=short` PASS UNCHANGED for the pre-existing test surface (delta = +1 new directory `tests/marcus/orchestrator/writers/`).
  - [ ] T7.6 Smoke: nodeid baseline UNCHANGED.
  - [ ] T7.7 R2 broad: `.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line`. Failure count ≤ T1 baseline (delta ≤ 0); per-failure git-log-attribution required for any failures present.
  - [ ] T7.8 Class-conformance: T1-baseline UNCHANGED (no parity_contract decorators added — these are Marcus writers, not HIL surfaces; no shape-pin file under `tests/parity/`).
  - [ ] T7.9 Lint-imports: 12 KEPT / 0 broken UNCHANGED (no pyproject.toml edits).
  - [ ] T7.10 Sandbox-AC: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` PASS.
  - [ ] T7.11 Ruff: clean on `app/marcus/orchestrator/writers/` + `tests/marcus/orchestrator/writers/`.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-17a.ready-for-review.md` with: 12-file lockstep verification + 3 sanctum-alignment registrations evidence (writer_id + sanctum_path + alignment_kind triplet) + per-writer schema hash + Marcus M1-M4 non-regression confirmation + DSL non-regression confirmation + class-conformance UNCHANGED + broad-regression delta with per-failure attribution + (if concurrent dispatch) `_bmad/memory/bmad-agent-marcus/schemas/` directory-creation coordination evidence with 7c.17b.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` (FR-7c-54 sanctum-alignment DSL primitive contract).
3. `app/parity/contracts/_sanctum.py` (DSL implementation reference).
4. `app/parity/contracts/__init__.py` (public DSL surface — what to import).
5. `tests/parity/test_sanctum_alignment_dsl.py` (canonical DSL usage + `_clear_sanctum_alignments_for_tests` fixture pattern).
6. `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (Wave-3 sibling: Pydantic-v2 + LF-only schema regen + shape-pin discipline).
7. `app/models/operator_verdict_section_08b.py` (Pydantic-v2 ConfigDict pattern + closed-enum Literal + strip-then-non-empty validator reference).
8. `app/marcus/orchestrator/specialist_summary_writer.py` + `app/marcus/orchestrator/__init__.py` (Marcus orchestrator namespace + import-style sibling reference).
9. `_bmad/memory/bmad-agent-marcus/INDEX.md` (Marcus sanctum BMB confirmation; READ-ONLY).
10. `pyproject.toml::tool.importlinter::contracts` (M1-M4 contract scope confirmation; no edit required).
11. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening — canonical Path.write_text command).
12. `docs/dev-guide/pydantic-v2-schema-checklist.md` (14 schema idioms — apply per-writer model).
13. Memory entry `project_slab_7b_skill_md_sanctum_alignment.md` (sanctum-alignment row pattern).
14. Governance JSON `7c-17a` entry: gate_mode=single-gate, K=1.3×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-0b"].
15. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.17a` (epic-level scope authority).

---

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. Schema-regen commands invoke `.venv/Scripts/python.exe` only (allowed per CLAUDE.md operator preference + memory `feedback_venv_python_allowed`). PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-READY** post-AMELIA-P2 PASS. **Parallel-dispatch viable with 7c.17b** under shared-file coordination guardrails:

- **`app/marcus/orchestrator/writers/__init__.py`**: shared namespace marker. First-mover creates as empty package; subsequent rebases (no real content; conflict-trivial).
- **`_bmad/memory/bmad-agent-marcus/schemas/` directory**: shared parent dir; 5 distinct schema filenames across 7c.17a (3) + 7c.17b (2). First-mover creates the directory.
- **No C6 import-linter contract touch** (writers live under `app.marcus.orchestrator.writers`, not `app.gates.**`). No pyproject.toml coordinate-or-sequence required.
- **DSL registry collisions**: 5 distinct `writer_id` values (`gary-slide-content`, `gary-fidelity-slides`, `gary-diagram-cards`, `gary-theme-resolution`, `gary-outbound-envelope`) — no collision.

If sequential dispatch is preferred, dispatch 7c.17a first (creates `writers/` namespace + `_bmad/memory/bmad-agent-marcus/schemas/` directory); 7c.17b extends.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

(populated by Codex at T1-T7)

### Completion Notes List

(populated by Codex at T10)

### File List

(populated by Codex at T10)

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for Wave-4 entry parallel-dispatch.
