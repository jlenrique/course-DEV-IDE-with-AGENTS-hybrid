# Codex dev-story prompt — Story 7c.17a (3 Marcus-Bound Writers: Slide-Content + Fidelity-Slides + Diagram-Cards; shared-sanctum partition; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-17a.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 4 — slot 1 (Wave-4 entry; first-of-pair with 7c.17b).
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-READY** post-AMELIA-P2 PASS.

**Parallel-dispatch context:** This story is intended for concurrent dispatch with **7c.17b** (path-disjoint at module level: 7c.17a authors `slide_content.py` + `fidelity_slides.py` + `diagram_cards.py`; 7c.17b authors `theme_resolution.py` + `outbound_envelope.py`). Shared parent directories (`app/marcus/orchestrator/writers/` + `_bmad/memory/bmad-agent-marcus/schemas/`) require first-mover-creates-then-others-rebase coordination — see PARALLEL-DISPATCH GUARDRAILS below. Per Slab 7b precedent, Marcus-writer-style stories used parallel-dispatch successfully.

**NOTE:** 7c.15 remains DISPATCH-BLOCKED on 7c.17b close. After 7c.17a + 7c.17b close, 7c.15 becomes dispatchable.

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

You may launch your own subagents to execute T2/T3/T4 in parallel within this story (path-disjoint at the file level: 3 writer modules + 3 schemas + 5 test files = ~12 new files, all in this story's scope). Shared-file edits MUST be serialized:

- **`app/marcus/orchestrator/writers/__init__.py`** — IF dispatching concurrently with 7c.17b, write ONCE as empty package marker; subsequent worker rebases (no real content; conflict-trivial).
- **`_bmad/memory/bmad-agent-marcus/schemas/`** directory — first-mover creates parent dir; 5 distinct schema filenames across the two stories (no per-file collision).
- **`app/parity/contracts/_sanctum.py`** — DO NOT modify (7c.0b deliverable; consumed via public DSL surface only).
- **`tests/parity/test_sanctum_alignment_dsl.py`** — DO NOT modify (7c.0b deliverable; reference-only).
- **`_bmad/memory/bmad-agent-marcus/`** sanctum 6 BMB files — DO NOT touch (Marcus sanctum BMB-aligned; only NEW `schemas/` subdir is in scope).
- **Closed Wave-3 §section packages** (`app/gates/section_*/`) — DO NOT touch (read-only sibling references).

Recommended sub-agent split:
- 1 subagent: AC-A slide_content writer + JSON schema regen
- 1 subagent: AC-B fidelity_slides writer + JSON schema regen
- 1 subagent: AC-C diagram_cards writer + JSON schema regen
- Main thread: writers/__init__.py + tests/marcus/orchestrator/writers/__init__.py + AC-E shape-pin tests + sanctum-registry test + T7 verification battery + T10 dropbox

---

```
Run bmad-dev-story on Story 7c.17a (Slab 7c Wave 4 slot 1; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` §AC-7c.0b-B (sanctum-alignment DSL primitive contract).
3. **`app/parity/contracts/_sanctum.py`** (DSL implementation; READ-ONLY).
4. **`app/parity/contracts/__init__.py`** (public DSL surface — what to import).
5. **`tests/parity/test_sanctum_alignment_dsl.py`** (canonical DSL usage + `_clear_sanctum_alignments_for_tests` fixture pattern).
6. `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (Wave-3 sibling reference; lite-tier follower; Pydantic-v2 + LF-only schema regen pattern).
7. **`app/models/operator_verdict_section_08b.py`** (Pydantic-v2 ConfigDict + closed-enum Literal + strip-then-non-empty pattern reference).
8. **`app/marcus/orchestrator/specialist_summary_writer.py`** + `app/marcus/orchestrator/__init__.py` (sibling namespace + import-style reference).
9. `_bmad/memory/bmad-agent-marcus/INDEX.md` (Marcus sanctum BMB confirmation; READ-ONLY).
10. `pyproject.toml::tool.importlinter::contracts` (M1-M4 contract scope confirmation; NO EDIT REQUIRED — writers/ namespace inherits M1-M4 by construction).
11. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening; canonical Path.write_text command in this prompt).
12. `docs/dev-guide/pydantic-v2-schema-checklist.md` (14 schema idioms; apply to all 3 writer models).
13. Memory entry `project_slab_7b_skill_md_sanctum_alignment.md` (sanctum-alignment row pattern).
14. Governance JSON `7c-17a` entry: gate_mode=single-gate, K=1.3×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-0b"].
15. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.17a` (epic-level scope authority).

## T1 hard checkpoints

- 7c.0b done (sanctum-alignment DSL primitive shipped + queryable via `iter_sanctum_alignments()`).
- `from app.parity.contracts import declare_sanctum_alignment, iter_sanctum_alignments, SanctumAlignmentDeclaration` importable.
- `from app.parity.contracts._sanctum import _clear_sanctum_alignments_for_tests` importable for test hygiene.
- Marcus sanctum BMB-aligned: 6 canonical files at `_bmad/memory/bmad-agent-marcus/` (INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES). Confirm; do NOT modify.
- `app/marcus/orchestrator/writers/` does NOT exist yet (this story creates it). `_bmad/memory/bmad-agent-marcus/schemas/` does NOT exist yet (this story creates it).
- Class-conformance baseline: record observed (~19 + Wave-3 trio's added shape-pins post-2026-05-06; recompute at T1). NEW directory `tests/marcus/orchestrator/writers/` does NOT add parity contract files (these are NOT HIL surfaces; no parity_contract decorator).
- Broad-regression baseline: re-run.

## Files in scope

**New (12 files):**
- `app/marcus/orchestrator/writers/__init__.py` (empty namespace; package marker only)
- `app/marcus/orchestrator/writers/slide_content.py` (~120 LOC; `GarySlideContent` + `SlideContentEntry` + `SlideContentKind` Literal + `emit_gary_slide_content` + module-import-time `declare_sanctum_alignment(writer_id="gary-slide-content", sanctum_path="_bmad/memory/bmad-agent-marcus/")`)
- `app/marcus/orchestrator/writers/fidelity_slides.py` (~120 LOC; `GaryFidelitySlides` + `VeraFidelityCriterion` + `FidelitySeverity` Literal + `emit_gary_fidelity_slides` + sanctum declaration for `gary-fidelity-slides`)
- `app/marcus/orchestrator/writers/diagram_cards.py` (~120 LOC; `GaryDiagramCards` + `DiagramCard` + `DiagramVisualKind` Literal + `emit_gary_diagram_cards` + sanctum declaration for `gary-diagram-cards`)
- `_bmad/memory/bmad-agent-marcus/schemas/gary-slide-content.schema.json` (regen via Path.write_text per A18)
- `_bmad/memory/bmad-agent-marcus/schemas/gary-fidelity-slides.schema.json` (regen via Path.write_text per A18)
- `_bmad/memory/bmad-agent-marcus/schemas/gary-diagram-cards.schema.json` (regen via Path.write_text per A18)
- `tests/marcus/orchestrator/writers/__init__.py` (empty namespace)
- `tests/marcus/orchestrator/writers/test_slide_content.py` (~70 LOC; round-trip + closed-enum red-reject + strip-then-non-empty red-reject + schema-hash STABLE pin)
- `tests/marcus/orchestrator/writers/test_fidelity_slides.py` (~70 LOC; same shape; covers severity closed-enum + `vera_source_ref` null-permitted)
- `tests/marcus/orchestrator/writers/test_diagram_cards.py` (~70 LOC; same shape; covers `DiagramVisualKind` closed-enum)
- `tests/marcus/orchestrator/writers/test_sanctum_alignments.py` (~50 LOC; imports the 3 writer modules + asserts `iter_sanctum_alignments()` registry contains the 3 writer_ids with `sanctum_path="_bmad/memory/bmad-agent-marcus/"` and `alignment_kind="bmb-pattern"`; uses autouse `_clear_sanctum_alignments_for_tests` fixture per `tests/parity/test_sanctum_alignment_dsl.py` precedent)

**Modified (0 files):**
- (No existing-file edits required. Writers/ namespace + schemas/ subdir + tests/ subdir are all greenfield.)

**Do NOT modify:**
- `app/parity/contracts/` (7c.0b deliverable; READ-ONLY DSL surface — import only)
- `tests/parity/test_sanctum_alignment_dsl.py` (7c.0b reference; READ-ONLY)
- `_bmad/memory/bmad-agent-marcus/` 6 canonical BMB files (INDEX/PERSONA/CREED/BOND/MEMORY/CAPABILITIES — Marcus sanctum is already BMB-aligned)
- `pyproject.toml` (NO import-linter edit — writers/ inherits M1-M4 by construction; do NOT add new contracts)
- `app/marcus/orchestrator/` existing modules (specialist_summary_writer, supervisor, routing, write_api, directive_composer, pre_gate_marcus, per_slide_subgraph, html_review_pack, conversation_persistence, dispatch_adapter, gate_runner, production_runner) — READ-ONLY sibling references
- Wave-3 closed §section packages (`app/gates/section_*/`) — read-only sibling references
- Skill files (`skills/bmad-agent-marcus/SKILL.md`) — Marcus is already BMB-aligned per Slab-7b precedent; sanctum-alignment for these writers is operationalized via the Python DSL call at module import (not via SKILL.md doc-section editing)

## Critical implementation notes

- **Pydantic-v2 ConfigDict discipline (per `docs/dev-guide/pydantic-v2-schema-checklist.md`):** all 3 models declare `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. Closed-enum Literal types on every enumerated field. `strip-then-non-empty` validators on all string fields per Wave-3 G2A canonical (mirror `app/models/operator_verdict_section_08b.py`).
- **`schema_version: int = 1`** on every model per FR-7c-51 schema_version discipline. Bump-on-change test discipline applies (test asserts schema hash stable; `schema_version` increments when schema hash changes).
- **Sanctum-alignment declaration at module import time:**
  ```python
  from app.parity.contracts import declare_sanctum_alignment
  
  declare_sanctum_alignment(
      writer_id="gary-slide-content",
      sanctum_path="_bmad/memory/bmad-agent-marcus/",
  )
  ```
  Place this near the top of each writer module (after imports, before model definitions). Default `alignment_kind="bmb-pattern"` since Marcus sanctum is BMB-aligned.
- **Idempotent module-import safety:** `declare_sanctum_alignment` raises `DuplicateSanctumAlignmentError` if the same `writer_id` is registered twice. In production runtime this is fine (modules import once per session). In tests, use the autouse `_clear_sanctum_alignments_for_tests` fixture from `tests/parity/test_sanctum_alignment_dsl.py` precedent to keep registry hermetic.
- **JSON schema regen via Path.write_text (per A18):** NO PowerShell `>` redirection. LF-only; verify NO BOM. Canonical command:
  ```bash
  .venv/Scripts/python.exe -c "from pathlib import Path; from app.marcus.orchestrator.writers.slide_content import GarySlideContent; import json; Path('_bmad/memory/bmad-agent-marcus/schemas/gary-slide-content.schema.json').write_text(json.dumps(GarySlideContent.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
  ```
  Repeat for fidelity_slides + diagram_cards.
- **Schema-hash STABLE pin in shape-pin tests:** capture the schema hash at first generation; assert against frozen literal. If schema content drifts intentionally, bump `schema_version` and update the frozen literal. This is the FR-7c-51 schema_version discipline applied to writer schemas.
- **Sanctum-registry test hermeticity:** the test file uses `_clear_sanctum_alignments_for_tests` autouse fixture (mirror `tests/parity/test_sanctum_alignment_dsl.py:19-22`). After fixture clears registry, explicitly import the 3 writer modules INSIDE the test to trigger their module-import-time `declare_sanctum_alignment` calls; then assert `list(iter_sanctum_alignments())` contains exactly the 3 expected declarations with correct `writer_id` + `sanctum_path` + `alignment_kind`.
- **No parity_contract decorator on writers** — these are Marcus writers, NOT HIL surfaces. The parity_contract DSL is for surfaces under `app/gates/**` only. Class-conformance count is UNCHANGED; broad-regression class-conformance assertion stays at the T1 baseline.
- **No pyproject.toml edit** — writers/ namespace inherits M1-M4 by construction. M3 (specialists may not import writers) + M4 (dispatch stays dependency-light) hold by default since no specialist or dispatch module imports the new writers/ subdirectory.
- **K-target 1.3× ≈ 540 LOC ceiling.** Estimate ~500-600 LOC actual.
- **T11 lite tier:** AC count = 5 + Marcus-orchestrator-namespace sibling files + new schemas under sanctum-pinned dir + no parity-DSL contract evolution + no governance/pipeline-manifest touch + single-gate.

## PARALLEL-DISPATCH GUARDRAILS (binding even under solo dispatch — same six rules from V6+V7)

1. **AMEND-7d-i AST-scan compliance.** N/A for Marcus-writer stories (no shape-pin in `tests/parity/test_decision_card_*` scope). Sanctum-registry test does NOT import LOCKSTEP_CHECK.
2. **Pattern-replication discipline.** Read `app/models/operator_verdict_section_08b.py` for Pydantic-v2 ConfigDict + closed-enum + strip-then-non-empty pattern. Read `app/marcus/orchestrator/specialist_summary_writer.py` for Marcus orchestrator namespace style. Read `tests/parity/test_sanctum_alignment_dsl.py` for sanctum-DSL fixture pattern. Mirror exactly except for writer-specific surface_id + payload shape.
3. **Shared-file integration ordering.** `app/marcus/orchestrator/writers/__init__.py` + `_bmad/memory/bmad-agent-marcus/schemas/` parent dir — coordinate-or-sequence with concurrent 7c.17b. First-mover creates; subsequent rebases.
4. **Pattern-parity ratchet.** strip-then-non-empty validators on all string fields (mirror G2A canonical). `Field(...)` with description on every field. Closed-enum Literal types. `model_config = ConfigDict(extra="forbid", validate_assignment=True)` everywhere. `schema_version: int = 1`.
5. **Class-conformance arithmetic.** UNCHANGED (no parity_contract decorators added; no `tests/parity/` shape-pins added). Document at T10 as "class-conformance UNCHANGED — Marcus writers are not HIL surfaces; FR-7c-54 sanctum-registry test does not register a parity_contract surface."
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0; per-failure git-log-attribution required for any failures present.

## Verification battery (T7)

```bash
.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/writers/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/parity/test_sanctum_alignment_dsl.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_05_5/ tests/gates/section_07b/ tests/gates/section_07d/ tests/gates/section_07f/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/marcus/ -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md
.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/writers/ tests/marcus/orchestrator/writers/
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-17a.ready-for-review.md`. Include: 12-file lockstep verification + 3 sanctum-alignment registrations evidence (writer_id + sanctum_path="_bmad/memory/bmad-agent-marcus/" + alignment_kind="bmb-pattern" triplet × 3) + per-writer schema-hash literal pinned in shape-pin tests + Marcus M1-M4 non-regression confirmation + DSL non-regression confirmation + class-conformance UNCHANGED + broad-regression delta with per-failure attribution + (if concurrent dispatch) coordination evidence with 7c.17b on `app/marcus/orchestrator/writers/__init__.py` + `_bmad/memory/bmad-agent-marcus/schemas/` directory creation.

T11: Claude lite tier (~10-15 min: spec-checklist + diff-skim + status flip; lite-batchable per AMEND-V3 if path-disjoint with sibling 7c.17b review).

## Boundary

HALT on: 7c.0b not done; sanctum-alignment DSL surface not importable from `app.parity.contracts`; `_clear_sanctum_alignments_for_tests` not importable from `app.parity.contracts._sanctum`; class-conformance count != T1-baseline (Marcus writers should NOT add parity contracts; if count changes, audit for unintended parity_contract decorator); broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; coordination conflict on shared `__init__.py` or `schemas/` parent dir with concurrent 7c.17b worker (coordinate-or-sequence; do NOT silently overwrite).

DO NOT touch: 7c.0b DSL implementation (`app/parity/contracts/_sanctum.py`); test_sanctum_alignment_dsl.py; Marcus sanctum 6 BMB files; pyproject.toml; existing Marcus orchestrator modules; closed Wave-3 §section packages; Marcus SKILL.md.

DO NOT introduce: new third-party deps; defensive enum widening on `SlideContentKind` / `FidelitySeverity` / `DiagramVisualKind`; non-deterministic test fixtures; integration logic between Vera output and fidelity_slides writer (out of scope — payload SHAPE only); SKILL.md doc-section additions (sanctum-alignment is operationalized via Python DSL only per FR-7c-54 contract).
```

---

## Operator dispatch checklist

1. ☐ 7c.0b done.
2. ☐ Sanctum-alignment DSL importable from `app.parity.contracts` (`declare_sanctum_alignment`, `iter_sanctum_alignments`, `SanctumAlignmentDeclaration`).
3. ☐ Marcus sanctum BMB-aligned (6 canonical files at `_bmad/memory/bmad-agent-marcus/`).
4. ☐ AMELIA-P2 freshness check.
5. ☐ Sandbox-AC validator PASS.
6. ☐ Sprint-status: ready-for-dev.
7. ☐ If parallel-dispatching with 7c.17b: confirm Codex understands `app/marcus/orchestrator/writers/__init__.py` + `_bmad/memory/bmad-agent-marcus/schemas/` first-mover-creates rule.
8. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.17b lands concurrently, spawn both in parallel + close-batch commit when both PASS.
