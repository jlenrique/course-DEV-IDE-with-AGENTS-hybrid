# Migration Story 7c.17b: 2 Marcus-Bound Writers + Envelope Aggregation — Theme-Resolution + Outbound-Envelope + pre-dispatch-package-gary.md (Divergent-Sanctum Partition; FR-7c-24 + FR-7c-25 + FR-7c-54)

**Status:** ready-for-dev *(spec authored 2026-05-06 lookahead_tier=1; predecessor 7c.0b CLOSED — sanctum-alignment DSL primitive at `app.parity.contracts._sanctum` shipped + queryable; the 5 writer_ids enumerated in 7c.0b AC-B are canonical for THIS story's 2 writers + 7c.17a's 3 writers. Marcus sanctum BMB-aligned at `_bmad/memory/bmad-agent-marcus/`. AMELIA-P2 sandbox-AC PASS expected pre-dispatch.)*
**Sprint key:** `migration-7c-17b-marcus-writers-theme-resolution-outbound-envelope`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 2
**K-target:** 1.3×
**Estimated LOC:** ~700 (theme_resolution writer ~120 + outbound_envelope writer ~150 + envelope schema regen ~50 + theme-resolution schema regen ~30 + pre-dispatch-package-gary.md aggregator ~120 + 4 tests ~70 each + sanctum-registry test)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** lite (per governance JSON entry `7c-17b`; AC count ≤5 + Marcus orchestrator-namespace sibling files + new schemas under sanctum-pinned `_bmad/memory/bmad-agent-marcus/schemas/` + envelope aggregation is YAML-emit + markdown-aggregator + no parity-DSL contract evolution + no governance/pipeline-manifest touch + single-gate)
**Lookahead-tier:** 1
**files_touched:** 11 new + 0 modified (assuming `app/marcus/orchestrator/writers/__init__.py` already created by 7c.17a OR by this story if dispatched first)

---

## Story

As Marcus,
I want to emit `gary-theme-resolution.json` + `gary-outbound-envelope.yaml` per plan unit, and aggregate ALL FIVE per-plan-unit packages (slide-content + fidelity-slides + diagram-cards from 7c.17a + theme-resolution + outbound-envelope from this story) into a single `pre-dispatch-package-gary.md` bundle for Gary dispatch, with each writer module declaring its sanctum-alignment row via the FR-7c-54 DSL primitive,
So that Gary receives the experience-profile + creative-directive theme inputs in resolved form + a single envelope handoff replaces the 5-file scattered shape, and the markdown aggregate gives the operator a single readable bundle for pre-dispatch review.

This story implements the **divergent-sanctum partition** half of the Wave-4 Marcus-writer split per **Winston W5 architectural partition principle**: 2 writers + envelope aggregation operating at the *theme-resolution + outbound-envelope* layer (rather than the per-slide-payload layer of 7c.17a). The complement is 7c.17a (slide-content + fidelity-slides + diagram-cards; shared-sanctum partition). Future maintenance of the 5 writers inherits this partition logic; cross-story refactors will respect it.

---

## Predecessor / Dependency Context

- **7c.0b** (CLOSED 2026-05-04): sanctum-alignment DSL primitive at `app.parity.contracts._sanctum` (FR-7c-54) shipped + queryable via `iter_sanctum_alignments()` + manifest emission via `emit_sanctum_alignment_manifest()`. The 5 writer_ids are canonical (`gary-slide-content`, `gary-fidelity-slides`, `gary-diagram-cards`, `gary-theme-resolution`, `gary-outbound-envelope`).
- **7c.17a** (parallel-dispatch SIBLING): authors `app/marcus/orchestrator/writers/__init__.py` + `slide_content.py` + `fidelity_slides.py` + `diagram_cards.py` + 3 schemas under `_bmad/memory/bmad-agent-marcus/schemas/` + sanctum-alignment registrations for the first 3 writer_ids. THIS STORY appends `theme_resolution.py` + `outbound_envelope.py` to the writers/ namespace + `gary-theme-resolution.schema.json` + `pre-dispatch-package.schema.json` (envelope schema) under the same schemas/ dir + sanctum-alignment registrations for the remaining 2 writer_ids. **Path-disjoint at module level**; shared parent directories (`writers/` + `schemas/`) require first-mover-creates coordination per parallel-dispatch guardrails.
- **20c-7..20c-15** (Wave 2B; experience-profile + creative-directive substrate): the source of `experience_profile` + `creative_directive` inputs that `theme_resolution` resolves into Gary's payload shape. THIS STORY's writer emits the RESOLVED PAYLOAD; the wiring "who calls theme_resolution with what experience-profile" is OUT OF SCOPE here.
- **Marcus sanctum** at `_bmad/memory/bmad-agent-marcus/`: BMB-pattern aligned (6 canonical files). The new `schemas/` subdirectory is shared with 7c.17a (5 distinct schema filenames; first-mover creates the directory).
- **Marcus M1-M4 import-linter contracts** (`pyproject.toml::tool.importlinter`): the writers/ namespace under `app.marcus.orchestrator.writers/` falls under existing M1-M4 contract scope. M3 (specialists may not import writers) + M4 (dispatch stays dependency-light) hold by construction. **No pyproject.toml edit required.**
- **7c.13/7c.14 next-batch + Wave-3 trio + G2C-aliased fanout**: read-only sibling references for Pydantic-v2 + LF-only schema regen pattern.
- **FR-7c-25 envelope schema location pin**: `_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json`. Fields: `{writer_id, target_section, payload_ref, dispatched_at, operator_id}`. THIS STORY lands the schema + the YAML emitter writer.

---

## Acceptance Criteria

### AC-7c.17b-A — theme-resolution writer (FR-7c-24 + FR-7c-54)

**Given** the experience-profile + creative-directive theme inputs (FR-7c-24) + the new `app/marcus/orchestrator/writers/` namespace + the FR-7c-54 sanctum-alignment DSL
**When** the dev-agent authors `app/marcus/orchestrator/writers/theme_resolution.py`
**Then** the theme-resolution module:
1. Declares Pydantic-v2 model `GaryThemeResolution` with `model_config = ConfigDict(extra="forbid", validate_assignment=True)` capturing the resolved theme payload: `plan_unit_id: str` (`min_length=1` + strip-then-non-empty), `target_section: str` (`min_length=1`), `experience_profile_id: str` (`min_length=1`), `creative_directive_id: str | None` (optional; null permitted to keep this story decoupled from CD-output integration), `resolved_theme: ResolvedTheme`, `schema_version: int = 1` (per FR-7c-51).
2. Declares `ResolvedTheme` sub-model: `theme_name: str` (`min_length=1`), `palette: ThemePaletteHint` (closed `Literal["light", "dark", "high-contrast", "brand-default"]` — minimum set; widening requires party-mode consensus), `template_intent: str | None` (Gary template hint; non-blocking).
3. Implements `emit_gary_theme_resolution(payload: GaryThemeResolution, output_path: Path) -> Path` — writes JSON via `output_path.write_text(json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True), encoding="utf-8")` per A18 (LF-only, NO BOM). Returns `output_path`.
4. At module import time, calls `declare_sanctum_alignment(writer_id="gary-theme-resolution", sanctum_path="_bmad/memory/bmad-agent-marcus/")` per FR-7c-54.

### AC-7c.17b-B — outbound-envelope writer + envelope schema (FR-7c-25 + FR-7c-54)

**Given** the FR-7c-25 envelope schema location pin (`_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json`) + envelope field set `{writer_id, target_section, payload_ref, dispatched_at, operator_id}`
**When** the dev-agent authors `app/marcus/orchestrator/writers/outbound_envelope.py`
**Then** the outbound-envelope module:
1. Declares Pydantic-v2 model `GaryOutboundEnvelope` (envelope shape) with `model_config = ConfigDict(extra="forbid", validate_assignment=True)`:
   - `plan_unit_id: str` (`min_length=1` + strip-then-non-empty)
   - `target_section: str` (`min_length=1`)
   - `entries: list[OutboundEnvelopeEntry]` (`min_length=1`; one entry per per-plan-unit writer output — typically 5 for the 7c.17a + 7c.17b complete set, but constraint is non-empty list; partial bundles permitted for partial dispatches)
   - `dispatched_at: datetime` (timezone-aware UTC per Pydantic-v2 schema-checklist)
   - `operator_id: str` (`min_length=1`; provenance per NFR-7c-S5)
   - `schema_version: int = 1`
2. Declares `OutboundEnvelopeEntry` sub-model:
   - `writer_id: str` (`min_length=1`; one of the 5 canonical Marcus-bound writer_ids — closed-enum check via `Literal[...]` typed alias `OutboundEnvelopeWriterId = Literal["gary-slide-content", "gary-fidelity-slides", "gary-diagram-cards", "gary-theme-resolution", "gary-outbound-envelope"]`)
   - `target_section: str` (`min_length=1`)
   - `payload_ref: str` (`min_length=1`; relative path or URI to the per-writer output JSON)
   - `dispatched_at: datetime`
   - `operator_id: str` (`min_length=1`)
3. Implements `emit_gary_outbound_envelope(payload: GaryOutboundEnvelope, output_path: Path) -> Path` — writes YAML via PyYAML with `sort_keys=True` + `default_flow_style=False` + `allow_unicode=True`, deterministic byte output, LF-only, NO BOM:
   ```python
   import yaml
   output_path.write_text(
       yaml.safe_dump(payload.model_dump(mode="json"), sort_keys=True, default_flow_style=False, allow_unicode=True),
       encoding="utf-8",
   )
   ```
   (PyYAML is already a project dependency per existing `state/config/*.yaml` consumption.)
4. At module import time, calls `declare_sanctum_alignment(writer_id="gary-outbound-envelope", sanctum_path="_bmad/memory/bmad-agent-marcus/")` per FR-7c-54.
5. Exposes a `pre_dispatch_package_gary_md(envelope: GaryOutboundEnvelope, payload_loaders: ...) -> str` markdown-aggregator function returning the rendered `pre-dispatch-package-gary.md` body (operator-readable bundle; aggregates per-entry headings + payload digests; deterministic ordering by `writer_id`).

### AC-7c.17b-C — JSON + YAML schema regen for theme-resolution + envelope (FR-7c-51 schema_version discipline)

**When** the dev-agent regenerates the schema files under `_bmad/memory/bmad-agent-marcus/schemas/`:
**Then** the following land:
- `_bmad/memory/bmad-agent-marcus/schemas/gary-theme-resolution.schema.json`
- `_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json` (envelope schema; FR-7c-25 location pin)

Each generated via the canonical Path.write_text command (per A18) — NOT PowerShell `>` redirection:
```bash
.venv/Scripts/python.exe -c "from pathlib import Path; from app.marcus.orchestrator.writers.theme_resolution import GaryThemeResolution; import json; Path('_bmad/memory/bmad-agent-marcus/schemas/gary-theme-resolution.schema.json').write_text(json.dumps(GaryThemeResolution.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"

.venv/Scripts/python.exe -c "from pathlib import Path; from app.marcus.orchestrator.writers.outbound_envelope import GaryOutboundEnvelope; import json; Path('_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json').write_text(json.dumps(GaryOutboundEnvelope.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
```
LF-only; NO BOM; deterministic byte output across Codex re-invocations.

### AC-7c.17b-D — Shape-pin tests + envelope-aggregation test + sanctum-registry test under `tests/marcus/orchestrator/writers/`

**Then** the dev-agent authors:
1. `tests/marcus/orchestrator/writers/test_theme_resolution.py` — covers (a) valid payload round-trip via `model_validate` + `emit_gary_theme_resolution` writes LF-only JSON byte-equivalent to schema; (b) closed-enum red-rejection on `ThemePaletteHint`; (c) strip-then-non-empty red-rejection on `plan_unit_id`; (d) `creative_directive_id` null-permitted path; (e) JSON schema hash STABLE pin.
2. `tests/marcus/orchestrator/writers/test_outbound_envelope.py` — covers (a) valid envelope round-trip via `model_validate` + `emit_gary_outbound_envelope` writes deterministic YAML; (b) closed-enum red-rejection on `OutboundEnvelopeWriterId` (asserts non-canonical writer_id like `"random-writer"` raises ValidationError); (c) strip-then-non-empty red-rejection on `operator_id`; (d) `entries` non-empty list red-rejection; (e) JSON schema hash STABLE pin; (f) `pre_dispatch_package_gary_md` aggregator returns deterministic markdown ordered by `writer_id`.
3. `tests/marcus/orchestrator/writers/test_sanctum_alignments_complement.py` — imports the 2 NEW writer modules from this story (triggering module-import-time `declare_sanctum_alignment` calls) + asserts `iter_sanctum_alignments()` registry contains the 2 NEW writer_ids `gary-theme-resolution` + `gary-outbound-envelope` with `sanctum_path="_bmad/memory/bmad-agent-marcus/"` and `alignment_kind="bmb-pattern"`. Uses `_clear_sanctum_alignments_for_tests` fixture per Slab-7b precedent for hermetic test runs.

   **Cross-story note:** the 7c.17a story authors `tests/marcus/orchestrator/writers/test_sanctum_alignments.py` covering the FIRST 3 writers; this story authors a separate file (`test_sanctum_alignments_complement.py`) covering the LAST 2 writers, to keep the two stories' test files path-disjoint. A future "all-5-together" sanctum-registry assertion can be a follow-on (or inline in 7c.21 closeout audit per FR-7c-50 audit-chain integrity).

### AC-7c.17b-E — Sanctum-alignment manifest emission smoke (FR-7c-54 + 7c.0b AC-F)

**Given** the FR-7c-54 sanctum-alignment manifest emission utility (`emit_sanctum_alignment_manifest(manifest_path)`) shipped by 7c.0b
**When** the test suite imports all 5 writer modules (3 from 7c.17a + 2 from this story) inside a hermetic test
**Then** `emit_sanctum_alignment_manifest(tmp_path / "manifest.json")` writes a 5-entry JSON manifest with deterministic ordering, schema_version=1, and all 5 writer_ids present. (Test goes under `tests/marcus/orchestrator/writers/test_sanctum_alignments_complement.py` — covers the manifest-emission path the AUDIT-AC layer at 7c.20a/c will consume.)

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.0b done; `app.parity.contracts._sanctum` importable + DSL surface stable.
  - [ ] T1.2 Confirm 7c.17a state: if CLOSED, `app/marcus/orchestrator/writers/__init__.py` + `_bmad/memory/bmad-agent-marcus/schemas/` directory + 3 sibling writer modules already on disk (this story extends). If parallel-dispatching, first-mover-creates rule applies (this story creates `__init__.py` if 7c.17a hasn't yet; no real content; subsequent rebases conflict-trivially).
  - [ ] T1.3 Read `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` §AC-7c.0b-B (sanctum-alignment DSL primitive) + §AC-7c.0b-F (manifest-emission integration).
  - [ ] T1.4 Read `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` (sibling story's writer modules + schema regen pattern + sanctum-registry test pattern).
  - [ ] T1.5 Read `tests/parity/test_sanctum_alignment_dsl.py` for DSL clear-fixture + manifest-emission round-trip pattern.
  - [ ] T1.6 Read existing project YAML emit usage to confirm PyYAML import idiom (e.g., `state/config/*.yaml` loaders + dumpers; ensure `yaml.safe_dump` with deterministic kwargs).
  - [ ] T1.7 Read `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (Pydantic-v2 + LF-only schema regen + shape-pin discipline).
  - [ ] T1.8 Confirm Marcus sanctum BMB-aligned (6 canonical files); no SKILL.md frontmatter touch required.
  - [ ] T1.9 Refresh broad-regression baseline + record class-conformance baseline.

- [ ] **T2 — Author theme_resolution writer (AC-A)**
  - [ ] T2.1 Author `app/marcus/orchestrator/writers/theme_resolution.py` per AC-A: `GaryThemeResolution` + `ResolvedTheme` + `ThemePaletteHint` Literal + `emit_gary_theme_resolution` + module-import-time `declare_sanctum_alignment(writer_id="gary-theme-resolution", ...)`.

- [ ] **T3 — Author outbound_envelope writer + markdown aggregator (AC-B)**
  - [ ] T3.1 Author `app/marcus/orchestrator/writers/outbound_envelope.py` per AC-B: `GaryOutboundEnvelope` + `OutboundEnvelopeEntry` + `OutboundEnvelopeWriterId` Literal + `emit_gary_outbound_envelope` (YAML emitter via PyYAML deterministic dump) + `pre_dispatch_package_gary_md` markdown aggregator + module-import-time `declare_sanctum_alignment(writer_id="gary-outbound-envelope", ...)`.

- [ ] **T4 — Generate 2 schemas under Marcus sanctum (AC-C)**
  - [ ] T4.1 Verify `_bmad/memory/bmad-agent-marcus/schemas/` directory exists (created by 7c.17a OR by this story if 7c.17a hasn't dispatched).
  - [ ] T4.2 Generate 2 schemas via canonical Path.write_text command pattern (per A18). LF-only; NO BOM.

- [ ] **T5 — Author shape-pin tests + sanctum-registry-complement test + manifest-emission smoke (AC-D + AC-E)**
  - [ ] T5.1 Author `tests/marcus/orchestrator/writers/test_theme_resolution.py`.
  - [ ] T5.2 Author `tests/marcus/orchestrator/writers/test_outbound_envelope.py` (covers YAML emit + closed-enum writer_id + envelope round-trip + markdown-aggregator deterministic ordering).
  - [ ] T5.3 Author `tests/marcus/orchestrator/writers/test_sanctum_alignments_complement.py` with `_clear_sanctum_alignments_for_tests` autouse fixture; covers (a) registry contains 2 NEW writer_ids after import; (b) `emit_sanctum_alignment_manifest` 5-entry round-trip when ALL 5 writer modules imported.

- [ ] **T6 — Verification battery (R-tier R2; T11-tier lite)**
  - [ ] T6.1 Focused: `.venv/Scripts/python.exe -m pytest tests/marcus/orchestrator/writers/ -p no:randomly -q --tb=short` PASS (covers BOTH 7c.17a tests + 7c.17b tests if 7c.17a closed; otherwise 7c.17b tests in isolation).
  - [ ] T6.2 DSL non-regression: `.venv/Scripts/python.exe -m pytest tests/parity/test_sanctum_alignment_dsl.py -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [ ] T6.3 §02A non-regression: `.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [ ] T6.4 Wave-3 closed §section non-regression sweep: `.venv/Scripts/python.exe -m pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_05_5/ tests/gates/section_07b/ tests/gates/section_07d/ tests/gates/section_07f/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [ ] T6.5 Marcus orchestrator non-regression: `.venv/Scripts/python.exe -m pytest tests/marcus/ -p no:randomly -q --tb=short` PASS UNCHANGED for the pre-existing test surface.
  - [ ] T6.6 Smoke: nodeid baseline UNCHANGED.
  - [ ] T6.7 R2 broad: failure count ≤ T1 baseline (delta ≤ 0); per-failure git-log-attribution required for any failures present.
  - [ ] T6.8 Class-conformance: T1-baseline UNCHANGED (no parity_contract decorators added — these are Marcus writers, not HIL surfaces; no shape-pin file under `tests/parity/`).
  - [ ] T6.9 Lint-imports: 12 KEPT / 0 broken UNCHANGED (no pyproject.toml edits).
  - [ ] T6.10 Sandbox-AC: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-17b-marcus-writers-theme-resolution-outbound-envelope.md` PASS.
  - [ ] T6.11 Ruff: clean on `app/marcus/orchestrator/writers/theme_resolution.py` + `outbound_envelope.py` + new test files.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-17b.ready-for-review.md` with: 11-file lockstep verification + 2 sanctum-alignment registrations evidence (writer_id + sanctum_path + alignment_kind triplet × 2) + envelope schema landed at the FR-7c-25 location pin (`_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json`) + per-writer schema-hash literal pinned in shape-pin tests + Marcus M1-M4 non-regression confirmation + DSL non-regression confirmation + class-conformance UNCHANGED + broad-regression delta with per-failure attribution + (if concurrent dispatch) `app/marcus/orchestrator/writers/__init__.py` + `_bmad/memory/bmad-agent-marcus/schemas/` directory-creation coordination evidence with 7c.17a + 5-entry manifest emission smoke evidence.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` (FR-7c-54 sanctum-alignment DSL primitive contract + manifest-emission utility).
3. `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` (sibling story; writer module + schema regen + sanctum-registry test pattern).
4. `app/parity/contracts/_sanctum.py` + `app/parity/contracts/__init__.py` (DSL implementation + public surface; READ-ONLY).
5. `tests/parity/test_sanctum_alignment_dsl.py` (DSL clear-fixture + manifest round-trip pattern).
6. `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (Wave-3 sibling: Pydantic-v2 + LF-only schema regen + shape-pin discipline).
7. `app/models/operator_verdict_section_08b.py` (Pydantic-v2 ConfigDict + closed-enum Literal + strip-then-non-empty pattern reference).
8. `app/marcus/orchestrator/specialist_summary_writer.py` + `app/marcus/orchestrator/__init__.py` (Marcus orchestrator namespace + import-style sibling reference).
9. `_bmad/memory/bmad-agent-marcus/INDEX.md` (Marcus sanctum BMB confirmation; READ-ONLY).
10. `pyproject.toml::tool.importlinter::contracts` (M1-M4 contract scope confirmation; no edit required).
11. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening — canonical Path.write_text command).
12. `docs/dev-guide/pydantic-v2-schema-checklist.md` (14 schema idioms — apply per-writer model).
13. Memory entry `project_slab_7b_skill_md_sanctum_alignment.md` (sanctum-alignment row pattern).
14. Existing PyYAML usage examples (e.g., `state/config/*.yaml` loaders) for deterministic `yaml.safe_dump` idiom.
15. Governance JSON `7c-17b` entry: gate_mode=single-gate, K=1.3×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-0b"].
16. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.17b` (epic-level scope authority; FR-7c-25 envelope schema location pin).

---

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. Schema-regen commands invoke `.venv/Scripts/python.exe` only (allowed per CLAUDE.md operator preference + memory `feedback_venv_python_allowed`). PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-READY** post-AMELIA-P2 PASS. **Parallel-dispatch viable with 7c.17a** under shared-file coordination guardrails (mirror image of 7c.17a's dispatch state):

- **`app/marcus/orchestrator/writers/__init__.py`**: shared namespace marker. First-mover creates as empty package; subsequent rebases (no real content; conflict-trivial).
- **`_bmad/memory/bmad-agent-marcus/schemas/` directory**: shared parent dir; 5 distinct schema filenames across 7c.17a (3) + 7c.17b (2). First-mover creates the directory.
- **No C6 import-linter contract touch** (writers live under `app.marcus.orchestrator.writers`, not `app.gates.**`). No pyproject.toml coordinate-or-sequence required.
- **DSL registry collisions**: 5 distinct `writer_id` values — no collision.

If sequential dispatch is preferred (operator-decision), dispatch 7c.17a first (creates `writers/` namespace + `schemas/` directory + 3 writer modules + 3 schemas + 4 tests); 7c.17b extends with 2 writer modules + 2 schemas + 3 tests. Sequential is lower-coordination but slower.

**After 7c.17b closes:** 7c.15 (DISPATCH-BLOCKED on this story per epic spec; spec already pre-authored at lookahead_tier=2) becomes dispatchable.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

(populated by Codex at T1-T6)

### Completion Notes List

(populated by Codex at T10)

### File List

(populated by Codex at T10)

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for Wave-4 entry parallel-dispatch.
