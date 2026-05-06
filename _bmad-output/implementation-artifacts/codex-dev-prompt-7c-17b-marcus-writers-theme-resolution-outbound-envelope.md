# Codex dev-story prompt — Story 7c.17b (2 Marcus-Bound Writers + Envelope Aggregation: Theme-Resolution + Outbound-Envelope; divergent-sanctum partition; single-gate; lite T11)

**Cycle:** Claude spec (lookahead_tier=1) → Codex T1-T10 → drops `_codex-handoff/7c-17b.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 4 — slot 2 (Wave-4 entry; second-of-pair with 7c.17a; closes Wave 4).
**Pre-authored:** 2026-05-06.
**Dispatch state:** **DISPATCH-READY** post-AMELIA-P2 PASS.

**Parallel-dispatch context:** This story is intended for concurrent dispatch with **7c.17a** (path-disjoint at module level: 7c.17a authors slide_content + fidelity_slides + diagram_cards; 7c.17b authors theme_resolution + outbound_envelope). Shared parent directories (`app/marcus/orchestrator/writers/` + `_bmad/memory/bmad-agent-marcus/schemas/`) require first-mover-creates-then-others-rebase coordination — see PARALLEL-DISPATCH GUARDRAILS below.

**NOTE:** 7c.15 unblocks ON THIS STORY's close (per 7c.15 spec dispatch_state: "DISPATCH-BLOCKED on 7c.17b"; §15 Marcus bundle writer at FR-7c-29 consumes this story's outbound-envelope.yaml aggregation).

---

## CODEX-SIDE PARALLEL-WORKER GUIDANCE

You may launch your own subagents to execute T2/T3 in parallel within this story (path-disjoint at the file level: 2 writer modules + 2 schemas + 3 test files = ~11 new files). Shared-file edits MUST be serialized:

- **`app/marcus/orchestrator/writers/__init__.py`** — IF dispatching concurrently with 7c.17a, write ONCE as empty package marker; subsequent worker rebases (no real content; conflict-trivial). If 7c.17a already CLOSED, the file already exists; do NOT modify it.
- **`_bmad/memory/bmad-agent-marcus/schemas/`** directory — first-mover creates parent dir; 5 distinct schema filenames across the two stories.
- **`app/parity/contracts/_sanctum.py`** — DO NOT modify (7c.0b deliverable; consumed via public DSL surface only).
- **`tests/parity/test_sanctum_alignment_dsl.py`** — DO NOT modify (7c.0b deliverable; reference-only).
- **`_bmad/memory/bmad-agent-marcus/`** sanctum 6 BMB files — DO NOT touch.
- **7c.17a writer modules** (slide_content.py + fidelity_slides.py + diagram_cards.py) — DO NOT touch (sibling story deliverables; READ-ONLY references).
- **7c.17a tests** (test_slide_content.py + test_fidelity_slides.py + test_diagram_cards.py + test_sanctum_alignments.py) — DO NOT touch.

Recommended sub-agent split:
- 1 subagent: AC-A theme_resolution writer + JSON schema regen
- 1 subagent: AC-B outbound_envelope writer + envelope schema regen + markdown aggregator
- Main thread: AC-D shape-pin tests + sanctum-registry-complement test + AC-E manifest-emission smoke + T6 verification battery + T10 dropbox

---

```
Run bmad-dev-story on Story 7c.17b (Slab 7c Wave 4 slot 2; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-17b-marcus-writers-theme-resolution-outbound-envelope.md`.

## Required reading (in order)

1. Story spec (5 ACs A-E; T1-T10 task structure).
2. `_bmad-output/implementation-artifacts/migration-7c-0b-scaffold-foundation.md` §AC-7c.0b-B + §AC-7c.0b-F (sanctum-alignment DSL primitive + manifest-emission utility).
3. `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` (sibling story; writer module + schema regen + sanctum-registry test pattern).
4. **`app/parity/contracts/_sanctum.py`** (DSL implementation; READ-ONLY).
5. **`app/parity/contracts/__init__.py`** (public DSL surface — what to import).
6. **`tests/parity/test_sanctum_alignment_dsl.py`** (canonical DSL usage + `_clear_sanctum_alignments_for_tests` fixture pattern + manifest round-trip example).
7. `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (Wave-3 sibling reference; lite-tier follower; Pydantic-v2 + LF-only schema regen pattern).
8. **`app/models/operator_verdict_section_08b.py`** (Pydantic-v2 ConfigDict + closed-enum Literal + strip-then-non-empty pattern reference).
9. **`app/marcus/orchestrator/specialist_summary_writer.py`** + `app/marcus/orchestrator/__init__.py` (sibling namespace + import-style reference).
10. `_bmad/memory/bmad-agent-marcus/INDEX.md` (Marcus sanctum BMB confirmation; READ-ONLY).
11. `pyproject.toml::tool.importlinter::contracts` (M1-M4 contract scope confirmation; NO EDIT REQUIRED).
12. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening; canonical Path.write_text command).
13. `docs/dev-guide/pydantic-v2-schema-checklist.md` (14 schema idioms; apply to both writer models).
14. Existing PyYAML usage examples (e.g., `state/config/*.yaml` loaders) for deterministic `yaml.safe_dump` idiom.
15. Memory entry `project_slab_7b_skill_md_sanctum_alignment.md` (sanctum-alignment row pattern).
16. Governance JSON `7c-17b` entry: gate_mode=single-gate, K=1.3×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-0b"].
17. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.17b` (epic-level scope authority; FR-7c-25 envelope schema location pin: `_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json`).

## T1 hard checkpoints

- 7c.0b done (sanctum-alignment DSL primitive shipped + queryable + manifest-emission utility shipped).
- `from app.parity.contracts import declare_sanctum_alignment, iter_sanctum_alignments, emit_sanctum_alignment_manifest` importable.
- `from app.parity.contracts._sanctum import _clear_sanctum_alignments_for_tests` importable for test hygiene.
- Marcus sanctum BMB-aligned: 6 canonical files at `_bmad/memory/bmad-agent-marcus/`. Confirm; do NOT modify.
- `_bmad/memory/bmad-agent-marcus/schemas/` may or may not exist depending on 7c.17a state — first-mover creates.
- `app/marcus/orchestrator/writers/__init__.py` may or may not exist — first-mover creates as empty package marker.
- 7c.17a state: if CLOSED, sibling writer modules + tests already on disk (READ-ONLY references). If parallel-dispatching, do not import from sibling modules at module-import time (per AC-D test-file separation rule).
- PyYAML available as a project dep (verify via `python -c "import yaml; print(yaml.__version__)"`).
- Class-conformance baseline: record observed (UNCHANGED expected — Marcus writers are NOT HIL surfaces; no parity_contract decorators).
- Broad-regression baseline: re-run.

## Files in scope

**New (11 files; assumes `app/marcus/orchestrator/writers/__init__.py` already exists post-7c.17a — if 7c.17a not yet closed, this story creates it as empty package marker):**
- `app/marcus/orchestrator/writers/theme_resolution.py` (~120 LOC; `GaryThemeResolution` + `ResolvedTheme` + `ThemePaletteHint` Literal + `emit_gary_theme_resolution` + module-import-time `declare_sanctum_alignment(writer_id="gary-theme-resolution", sanctum_path="_bmad/memory/bmad-agent-marcus/")`)
- `app/marcus/orchestrator/writers/outbound_envelope.py` (~150 LOC; `GaryOutboundEnvelope` + `OutboundEnvelopeEntry` + `OutboundEnvelopeWriterId` Literal + `emit_gary_outbound_envelope` (YAML emitter via PyYAML deterministic dump) + `pre_dispatch_package_gary_md` markdown aggregator + sanctum declaration for `gary-outbound-envelope`)
- `_bmad/memory/bmad-agent-marcus/schemas/gary-theme-resolution.schema.json` (regen via Path.write_text per A18)
- `_bmad/memory/bmad-agent-marcus/schemas/pre-dispatch-package.schema.json` (envelope schema; FR-7c-25 location pin; regen via Path.write_text per A18)
- `tests/marcus/orchestrator/writers/test_theme_resolution.py` (~70 LOC; round-trip + closed-enum red-reject + strip-then-non-empty red-reject + null-permitted creative_directive_id + schema-hash STABLE pin)
- `tests/marcus/orchestrator/writers/test_outbound_envelope.py` (~90 LOC; envelope round-trip + YAML emit determinism + closed-enum writer_id red-reject + envelope entries non-empty red-reject + markdown-aggregator deterministic ordering + schema-hash STABLE pin)
- `tests/marcus/orchestrator/writers/test_sanctum_alignments_complement.py` (~70 LOC; clears registry; imports the 2 NEW writer modules; asserts iter_sanctum_alignments contains the 2 NEW writer_ids; THEN imports all 5 writer modules + asserts emit_sanctum_alignment_manifest 5-entry round-trip)

**Conditionally new (1 file; create only if 7c.17a hasn't yet):**
- `app/marcus/orchestrator/writers/__init__.py` (empty namespace; first-mover creates)
- `tests/marcus/orchestrator/writers/__init__.py` (empty namespace; first-mover creates)

**Modified (0 files):**
- (No existing-file edits required.)

**Do NOT modify:**
- `app/parity/contracts/` (7c.0b deliverable; READ-ONLY DSL surface — import only)
- `tests/parity/test_sanctum_alignment_dsl.py` (7c.0b reference; READ-ONLY)
- `_bmad/memory/bmad-agent-marcus/` 6 canonical BMB files
- `pyproject.toml` (NO import-linter edit — writers/ inherits M1-M4 by construction)
- `app/marcus/orchestrator/` existing modules (READ-ONLY sibling references)
- 7c.17a writer modules (slide_content.py + fidelity_slides.py + diagram_cards.py) — READ-ONLY sibling deliverables
- 7c.17a tests (test_slide_content.py + test_fidelity_slides.py + test_diagram_cards.py + test_sanctum_alignments.py) — READ-ONLY
- Closed Wave-3 §section packages — read-only sibling references
- Marcus SKILL.md — Marcus is already BMB-aligned; sanctum-alignment is operationalized via Python DSL only

## Critical implementation notes

- **Pydantic-v2 ConfigDict discipline:** both models declare `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. Closed-enum Literal types on every enumerated field. `strip-then-non-empty` validators on all string fields per Wave-3 G2A canonical.
- **`schema_version: int = 1`** on both models per FR-7c-51.
- **YAML emitter determinism:**
  ```python
  import yaml
  output_path.write_text(
      yaml.safe_dump(
          payload.model_dump(mode="json"),
          sort_keys=True,
          default_flow_style=False,
          allow_unicode=True,
      ),
      encoding="utf-8",
  )
  ```
  YAML emit must be byte-deterministic across Codex re-invocations. Test asserts deterministic byte output.
- **`OutboundEnvelopeWriterId` closed-enum:** `Literal["gary-slide-content", "gary-fidelity-slides", "gary-diagram-cards", "gary-theme-resolution", "gary-outbound-envelope"]` — these are THE 5 canonical Marcus-bound writer_ids enumerated in 7c.0b AC-B examples. Widening the enum requires party-mode consensus.
- **Sanctum-alignment declaration at module import time:**
  ```python
  from app.parity.contracts import declare_sanctum_alignment
  
  declare_sanctum_alignment(
      writer_id="gary-theme-resolution",
      sanctum_path="_bmad/memory/bmad-agent-marcus/",
  )
  ```
  Place near the top of each writer module (after imports, before model definitions). Default `alignment_kind="bmb-pattern"`.
- **Sanctum-registry-complement test hermeticity:** the test file uses `_clear_sanctum_alignments_for_tests` autouse fixture (mirror `tests/parity/test_sanctum_alignment_dsl.py:19-22`). After fixture clears registry, EXPLICITLY import the 2 NEW writer modules INSIDE the test function (not at file top) to trigger their module-import-time `declare_sanctum_alignment` calls. For the manifest-emission smoke test (AC-E), import all 5 writer modules to populate the registry, then call `emit_sanctum_alignment_manifest(tmp_path / "manifest.json")` and assert 5 entries with deterministic ordering.
- **JSON schema regen via Path.write_text (per A18):** NO PowerShell `>` redirection. LF-only; verify NO BOM. Two schema files: `gary-theme-resolution.schema.json` + `pre-dispatch-package.schema.json` (envelope; FR-7c-25 location pin).
- **Markdown aggregator (`pre_dispatch_package_gary_md`):** deterministic ordering by `writer_id`. Per-entry markdown heading + `payload_ref` link + dispatched_at timestamp + operator_id provenance line. Operator-readable bundle. Test asserts deterministic markdown byte output across re-invocations with the same envelope input.
- **No parity_contract decorator on writers** — these are Marcus writers, NOT HIL surfaces.
- **No pyproject.toml edit** — writers/ namespace inherits M1-M4 by construction.
- **K-target 1.3× ≈ 540 LOC ceiling.** Estimate ~600-700 LOC actual (envelope + markdown aggregator are slightly heavier than per-payload writers; still in band).
- **T11 lite tier:** AC count = 5 + sibling files + sanctum-pinned schema location + no contract evolution + no governance touch + single-gate.

## PARALLEL-DISPATCH GUARDRAILS (binding even under solo dispatch — same six rules from V6+V7)

1. **AMEND-7d-i AST-scan compliance.** N/A for Marcus-writer stories.
2. **Pattern-replication discipline.** Mirror 7c.17a's writer module shape (Pydantic-v2 + ConfigDict + closed-enum + sanctum declaration at module import) + Wave-3 sibling Pydantic-v2 + LF-only schema regen pattern + `tests/parity/test_sanctum_alignment_dsl.py` for clear-fixture + manifest round-trip.
3. **Shared-file integration ordering.** `app/marcus/orchestrator/writers/__init__.py` + `_bmad/memory/bmad-agent-marcus/schemas/` parent dir + `tests/marcus/orchestrator/writers/__init__.py` — coordinate-or-sequence with concurrent 7c.17a worker. First-mover creates; subsequent rebases.
4. **Pattern-parity ratchet.** strip-then-non-empty on all string fields. `Field(...)` with description on every field. Closed-enum Literal types. `model_config = ConfigDict(extra="forbid", validate_assignment=True)`. `schema_version: int = 1`. Timezone-aware datetime for `dispatched_at`.
5. **Class-conformance arithmetic.** UNCHANGED (no parity_contract decorators added).
6. **Broad-regression baseline shift with per-failure attribution.** Record T1 baseline; T9 delta ≤ 0.

## Verification battery (T6)

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
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-17b-marcus-writers-theme-resolution-outbound-envelope.md
.venv/Scripts/python.exe -m ruff check app/marcus/orchestrator/writers/theme_resolution.py app/marcus/orchestrator/writers/outbound_envelope.py tests/marcus/orchestrator/writers/test_theme_resolution.py tests/marcus/orchestrator/writers/test_outbound_envelope.py tests/marcus/orchestrator/writers/test_sanctum_alignments_complement.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-17b.ready-for-review.md`. Include: 11-file lockstep verification + 2 sanctum-alignment registrations evidence (writer_id + sanctum_path="_bmad/memory/bmad-agent-marcus/" + alignment_kind="bmb-pattern" triplet × 2) + envelope schema landed at FR-7c-25 location pin + per-writer schema-hash literals + Marcus M1-M4 non-regression + DSL non-regression + class-conformance UNCHANGED + broad-regression delta with per-failure attribution + (if concurrent dispatch) coordination evidence with 7c.17a + 5-entry manifest emission smoke evidence.

T11: Claude lite tier (~10-15 min: spec-checklist + diff-skim + status flip; lite-batchable per AMEND-V3 if path-disjoint with sibling 7c.17a review).

## Boundary

HALT on: 7c.0b not done; sanctum-alignment DSL surface or `emit_sanctum_alignment_manifest` not importable; class-conformance count != T1-baseline; broad-regression failure count > T1 baseline AND any new failure not git-log-verified-inherited; coordination conflict on shared `__init__.py` or `schemas/` parent dir with concurrent 7c.17a worker (coordinate-or-sequence; do NOT silently overwrite); YAML emit non-deterministic (test fails) — root-cause; do not paper over with kwargs jiggling.

DO NOT touch: 7c.0b DSL implementation; test_sanctum_alignment_dsl.py; Marcus sanctum 6 BMB files; pyproject.toml; existing Marcus orchestrator modules; 7c.17a writer modules + tests; closed Wave-3 §section packages; Marcus SKILL.md.

DO NOT introduce: new third-party deps (PyYAML already a project dep — do not add new YAML libraries); defensive enum widening on `OutboundEnvelopeWriterId` / `ThemePaletteHint`; non-deterministic test fixtures; integration logic between CD output and theme_resolution writer (out of scope — payload SHAPE only); SKILL.md doc-section additions; cross-test imports between this story's tests and 7c.17a's tests (each story owns its sanctum-registry test file separately per AC-D rule — keeps stories independently reviewable).
```

---

## Operator dispatch checklist

1. ☐ 7c.0b done.
2. ☐ Sanctum-alignment DSL importable from `app.parity.contracts` (`declare_sanctum_alignment`, `iter_sanctum_alignments`, `emit_sanctum_alignment_manifest`, `SanctumAlignmentDeclaration`).
3. ☐ Marcus sanctum BMB-aligned (6 canonical files at `_bmad/memory/bmad-agent-marcus/`).
4. ☐ AMELIA-P2 freshness check.
5. ☐ Sandbox-AC validator PASS.
6. ☐ Sprint-status: ready-for-dev.
7. ☐ If parallel-dispatching with 7c.17a: confirm Codex understands `app/marcus/orchestrator/writers/__init__.py` + `_bmad/memory/bmad-agent-marcus/schemas/` first-mover-creates rule.
8. ☐ Dispatch.

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent (~10-15 min). If 7c.17a lands concurrently, spawn both in parallel + close-batch commit when both PASS.

**Wave-4 close consequence:** Once 7c.17b CLOSED, **7c.15 (DISPATCH-BLOCKED) becomes dispatchable** — its §15 Marcus bundle writer (FR-7c-29) consumes this story's `gary-outbound-envelope.yaml` aggregation.
