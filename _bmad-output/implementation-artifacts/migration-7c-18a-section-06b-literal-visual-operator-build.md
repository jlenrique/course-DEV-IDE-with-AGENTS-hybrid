# Migration Story 7c.18a: §06B Literal-Visual Operator Build HIL Surface (FR-7c-26)

**Status:** review *(Codex implementation complete 2026-05-06; ready for T11 lite review.)*
**Sprint key:** `migration-7c-18a-section-06b-literal-visual-operator-build`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 1
**K-target:** 1.3×
**Estimated LOC:** ~400 (poll-surface module ~120 + Section06BOperatorVerdict model ~60 + LiteralVisualBuildPayload model ~40 + JSON schema ~50 + shape-pin ~80 + 3-transport-parity test ~70 + DSL-registration test ~30)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** lite (per governance JSON entry `7c-18a`; AC count ≤5 + sibling-files only + new §section package + new OperatorVerdict variant + 3-transport schema-stability via FR-7c-49 harness + Codex T10 self-review clean + single-gate)
**Lookahead-tier:** 1
**files_touched:** 7 new + 1 modified (C6 import-linter contract modules list append for `app.gates.section_06b`)

---

## Story

As the operator,
I want to build literal-visual operator content at the §06B surface, emitting per-slide visual specifications consumed downstream by §07 Gary dispatch,
So that diagram-bearing slides have explicit operator-authored visual specifications (not auto-generated guesses), submitted via mandatory CLI transport with HTTP + MCP-stdio optional per FR-7c-26 — emitting `Section06BOperatorVerdict` with verb ∈ {`submit`, `edit`, `discard`}, with three-transport schema-stability via FR-7c-49 shape-pin discipline.

This is an **operator-build HIL surface** — the operator authors content (not just renders a verdict on an upstream Card). The surface mirrors the §02A canonical poll-surface shape (closed at 7c.3b) with build-flavored verbs (`submit / edit / discard` mirroring 7c.14's `select / edit / reject` pattern: action-flavored verb + revision verb + abandon verb).

---

## Predecessor / Dependency Context

- **7c.17a** (Wave 4; close-pending; predecessor for Wave-5 entry): authors `app/marcus/orchestrator/writers/diagram_cards.py` + `GaryDiagramCards` + `DiagramCard` Pydantic-v2 model + JSON schema. **§06B's operator-authored output downstream-feeds Gary dispatch via the `gary-diagram-cards.json` payload shape**. Codex T1 may consume `DiagramCard`'s field set (slide_index + visual_kind + specification + caption) as the per-slide visual specification shape inside `LiteralVisualBuildPayload`, OR define a parallel shape; the choice is a T1-T9 decision documented in the dispatch-state context (sibling-pattern duplication is precedent under C6 isolation rules).
- **7c.17b** (Wave 4; close-pending; predecessor for Wave-5 entry): authors `app/marcus/orchestrator/writers/outbound_envelope.py` + envelope schema. §06B's output is one of the per-plan-unit packages aggregated into the `pre-dispatch-package-gary.md` bundle.
- **7c.3b** (CLOSED `f8fc1a8`): §02A G0 poll-surface canonical HIL pattern. Authoritative reference at `app/gates/section_02a/poll_surface.py`.
- **7c.14** (CLOSED 2026-05-06): §11 G4A voice-selection HIL surface — closest sibling for **action-flavored verb-set pattern** (`select / edit / reject` + 3-way verb-payload `model_validator(mode="after")`). §06B mirrors this shape with `submit / edit / discard`.
- **Wave-3 trio + next-batch + G2C-aliased fanout (CLOSED 2026-05-05/06):** canonical references for §section package + parity_contract + OperatorVerdict + 3-transport-parity discipline.
- **C6 import-linter contract** at `pyproject.toml::tool.importlinter` (per 7c.4b D5 P-1 patch): `independence` type with modules list. **THIS STORY APPENDS `app.gates.section_06b` to C6's modules list.**
- **No alias_of parent family**: §06B is a NEW surface family (NOT aliased to G1/G2/G3/G4/G5/G6 per ADR 0002). The parity_contract decorator omits the `alias_of` kwarg (or passes `alias_of=None`); the surface stands alone as its own family.

---

## Acceptance Criteria

### AC-7c.18a-A — §section package + parity_contract registration (FR-7c-26)

**Given** §02A canonical poll-surface pattern at `app/gates/section_02a/poll_surface.py` + Wave-3 sibling §section packages
**When** the dev-agent authors `app/gates/section_06b/poll_surface.py`
**Then** the module:
1. Declares `SURFACE_ID = SECTION_06B_SURFACE_ID` (constant from new `app/models/operator_verdict_section_06b.py`).
2. Registers via `@parity_contract(surface_id="section_06b_literal_visual_build", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"])` per FR-7c-26 transport defaults (CLI mandatory; HTTP + MCP-stdio optional per FR-7c-32 default — § 06B is not externally enumerated as multi-transport-mandatory). **No `alias_of` kwarg** — §06B is a new family.
3. Implements `display_literal_visual_targets(upstream_or_path: Path | dict[str, Any]) -> dict[str, Any]` (poll function; renders the per-slide flagged-for-literal-visual targets that the operator must build for; T1-T9 decision: consume from upstream Vera fidelity flagging or from plan-unit metadata).
4. Implements `submit_verdict(plan_unit_id: str, verdict_payload: dict, transport: TransportName) -> Section06BOperatorVerdict` (submit function; emits OperatorVerdict).
5. Re-emits `canonical_model_bytes` + `compute_model_digest` helpers locally to satisfy C6 cross-§section independence (per Wave-3-trio + next-batch + G2C-fanout precedent).

### AC-7c.18a-B — OperatorVerdict variant + JSON schema regen (FR-7c-49)

**When** the dev-agent authors `app/models/operator_verdict_section_06b.py` + regenerates `app/models/operator_verdict_section_06b.v1.schema.json`:
1. `Section06BOperatorVerdict` Pydantic-v2 model: `surface_id: Literal["section_06b_literal_visual_build"]` + `verb: Section06BBuildVerb` (closed `Literal["submit", "edit", "discard"]`) + `plan_unit_id: str` (`min_length=1` + strip-then-non-empty validator per Wave-3 G2A canonical) + standard envelope fields per §02A precedent (run_id UUID4 + operator_id pattern + submitted_at tz-aware + decision_card_digest sha256 + 3-way verb-payload consistency `model_validator(mode="after")` mirroring 7c.14 pattern).
2. `LiteralVisualBuildPayload` (mandatory iff verb=submit; carries `target_section: str` + `slide_specifications: list[SlideVisualSpecification]` with `min_length=1`). `SlideVisualSpecification` sub-model: `slide_index: int` (`ge=1`), `visual_kind: VisualSpecKind` (closed `Literal[...]` mirroring 7c.17a's `DiagramVisualKind` minimum set: `{"flowchart", "sequence", "comparison", "literal-visual"}` — Codex T1-T9 confirms exact alignment with 7c.17a or documents partial divergence with rationale), `specification: str` (`min_length=1` — operator-authored per-slide visual spec), `caption: str | None`.
3. `LiteralVisualEditPayload` (mandatory iff verb=edit; mirrors `DirectiveEditPayload` shape; carries field-level edits to a previously-submitted spec).
4. JSON schema regenerated via Path.write_text(... encoding="utf-8") canonical command (anti-pattern A18). LF-only; NO BOM.
5. `decision_card_digest: str (sha256-hex pattern)` — for build surfaces, this is the digest of the build_payload itself (operator-submitted content) OR the digest of an upstream artifact (e.g., upstream Vera fidelity-flagged slide list). T1-T9 decision documented in Completion Notes.

### AC-7c.18a-C — Three-transport schema-stability shape-pin (FR-7c-49)

**Then** `tests/schemas/operator_verdict/test_section_06b_shape.py` asserts `Section06BOperatorVerdict` schema hash STABLE across CLI / HTTP / MCP-stdio transports per FR-7c-49 harness pattern. Use `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section06BOperatorVerdict, surface_id="section_06b_literal_visual_build", transports=["cli", "http", "mcp-stdio"])` from `tests/schemas/operator_verdict/_harness.py` (7c.4b D3 deliverable; canonical helper).

### AC-7c.18a-D — DSL-registration audit + 3-transport-parity test

**Then**:
1. `tests/gates/section_06b/test_literal_visual_build_dsl_registration.py` — asserts `parity_contract` registered with correct surface_id + transports + `alias_of` absent (or None). **Reload-isolated** to avoid shared-registry ordering flake under xdist (per 7c.6 Codex precedent).
2. `tests/gates/section_06b/test_literal_visual_build_three_transport_parity.py` — round-trips a sample §06B verdict via CLI + HTTP + MCP-stdio simulated transports; asserts payload digest equals across all three (per Wave-3 trio precedent).

### AC-7c.18a-E — C6 import-linter modules list append (binding=hard per 7c.4b D5)

**When** the dev-agent updates `pyproject.toml`:
**Then** `app.gates.section_06b` appended to C6 contract `modules` list (current state post-Wave-3 + Wave-3 next-batch + G2C-aliased fanout: `[app.gates.section_02a, app.gates.section_04a, app.gates.section_04_5, app.gates.section_04_55, app.gates.section_05_5, app.gates.section_07b, app.gates.section_07d, app.gates.section_07f, app.gates.section_08b, app.gates.section_11]`; will become `[..., app.gates.section_06b]` post-this-story). Lint-imports re-runs PASS with 12 KEPT (UNCHANGED count; C6 just gets a wider module list). **PARALLEL-DISPATCH GUARDRAIL #3 (binding):** if 7c.18b dispatches concurrently, two-way coordinate-or-sequence — main thread (or whichever worker integrates first) writes the union of both new §section entries; subsequent worker rebases before commit.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks**
  - [x] T1.1 Confirm 7c.17a + 7c.17b done in sprint-status (HARD predecessor block; Wave-5 entry depends on Wave-4 close).
  - [x] T1.2 Read `app/gates/section_02a/poll_surface.py` + `app/models/operator_verdict_section_02a.py` + Wave-3 trio + next-batch sibling references.
  - [x] T1.3 Read `app/models/operator_verdict_section_11.py` (7c.14 — closest sibling for 3-way verb-payload `model_validator` + action-flavored verb-set pattern).
  - [x] T1.4 Read `app/marcus/orchestrator/writers/diagram_cards.py` + `app/marcus/orchestrator/writers/fidelity_slides.py` (7c.17a deliverables; reference for `DiagramCard` payload shape + Vera fidelity-flagged slide list — decide alignment vs duplication for `SlideVisualSpecification`).
  - [x] T1.5 Read `app/parity/contracts/_decorator.py` + `_declaration.py` for parity_contract API + verify it accepts surface registration without `alias_of` (or with explicit `alias_of=None`).
  - [x] T1.6 Read ADR 0002 to confirm §06B is NOT in the family-aliases catalog (no parent family).
  - [x] T1.7 Refresh broad-regression baseline + record class-conformance baseline.

- [x] **T2 — Author §section package + OperatorVerdict model**
  - [x] T2.1 Author `app/gates/section_06b/__init__.py` (empty namespace).
  - [x] T2.2 Author `app/gates/section_06b/poll_surface.py` per AC-A.
  - [x] T2.3 Author `app/models/operator_verdict_section_06b.py` per AC-B with `Section06BOperatorVerdict` + `LiteralVisualBuildPayload` + `SlideVisualSpecification` + `LiteralVisualEditPayload` + `Section06BBuildVerb` + `VisualSpecKind` + `SECTION_06B_SURFACE_ID`.

- [x] **T3 — Generate JSON schema (AC-B)**
  - [x] T3.1 Generate `app/models/operator_verdict_section_06b.v1.schema.json` via:
    ```bash
    .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_06b import Section06BOperatorVerdict; import json; Path('app/models/operator_verdict_section_06b.v1.schema.json').write_text(json.dumps(Section06BOperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
    ```
    (Path.write_text per A18; NO PowerShell `>` redirection.)

- [x] **T4 — Author shape-pin + 3-transport-parity test + DSL-registration audit (AC-C + AC-D)**
  - [x] T4.1 Author `tests/schemas/operator_verdict/test_section_06b_shape.py` using FR-7c-49 harness.
  - [x] T4.2 Author `tests/gates/section_06b/__init__.py` + `_helpers.py`.
  - [x] T4.3 Author `tests/gates/section_06b/test_literal_visual_build_dsl_registration.py` (reload-isolated).
  - [x] T4.4 Author `tests/gates/section_06b/test_literal_visual_build_three_transport_parity.py`.

- [x] **T5 — C6 import-linter modules list append (AC-E)**
  - [x] T5.1 Update `pyproject.toml::tool.importlinter::contracts::C6::modules` to append `app.gates.section_06b`. **PARALLEL-DISPATCH GUARDRAIL #3:** if running concurrently with 7c.18b, write the union of both new §section entries.

- [x] **T6 — Verification battery (R-tier R2)**
  - [x] T6.1 Focused: `pytest tests/gates/section_06b/ tests/schemas/operator_verdict/test_section_06b_shape.py -p no:randomly -q --tb=short` PASS.
  - [x] T6.2 §02A non-regression: `pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [x] T6.3 Wave-3 + Wave-3-next-batch + G2C-fanout non-regression sweep: `pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ tests/gates/section_05_5/ tests/gates/section_07b/ tests/gates/section_07d/ tests/gates/section_07f/ tests/gates/section_08b/ tests/gates/section_11/ -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [x] T6.4 Wave-4 Marcus-writer non-regression: `pytest tests/marcus/orchestrator/writers/ -p no:randomly -q --tb=short` PASS UNCHANGED (7c.17a + 7c.17b deliverables).
  - [x] T6.5 Smoke: nodeid baseline UNCHANGED.
  - [x] T6.6 R2 broad: failure count ≤ T1 baseline (45 failed vs inherited 47-failure Wave-5 pre-fix run; structural new-target failures resolved).
  - [x] T6.7 Class-conformance: PASS at 19 parity contract files; shape-pin files live under `tests/schemas/operator_verdict/`.
  - [x] T6.8 Lint-imports: 12 KEPT / 0 broken (UNCHANGED count; C6 modules list grew).
  - [x] T6.9 Sandbox-AC: PASS.
  - [x] T6.10 Ruff: clean.

- [x] **T10 — Codex self-review dropbox**
  - [x] T10.1 Drop `_codex-handoff/7c-18a.ready-for-review.md`.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor).
3. `_bmad-output/implementation-artifacts/migration-7c-14-section-11-g4a-voice-selection.md` (closest sibling for action-flavored verb-set + 3-way verb-payload `model_validator`).
4. `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` (Wave-4 sibling; predecessor; `DiagramCard` shape reference).
5. `app/gates/section_02a/poll_surface.py` (canonical pattern reference).
6. `app/gates/section_11/poll_surface.py` (action-flavored sibling pattern).
7. `app/models/operator_verdict_section_02a.py` + `app/models/operator_verdict_section_11.py` (canonical + action-verb sibling references).
8. `app/marcus/orchestrator/writers/diagram_cards.py` (7c.17a deliverable; `DiagramCard` shape).
9. `app/marcus/orchestrator/writers/fidelity_slides.py` (7c.17a deliverable; Vera fidelity-flagged slide list shape — relevant for upstream payload determination at T1).
10. `tests/schemas/operator_verdict/_harness.py` (FR-7c-49 harness; READ-ONLY).
11. `tests/schemas/operator_verdict/test_section_02a_shape.py` + Wave-3 + next-batch shape-pins (canonical references).
12. `tests/gates/section_02a/*.py` + Wave-3 + next-batch DSL-registration + 3-transport-parity tests.
13. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract decorator + alias_of optional kwarg semantics).
14. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (confirm §06B is NOT in family-aliases catalog; this surface stands alone).
15. `pyproject.toml::tool.importlinter` (C6 contract; modules list).
16. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
17. Governance JSON `7c-18a` entry: gate_mode=single-gate, K=1.3×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-17a", "7c-17b"].
18. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.18a` (epic-level scope authority).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-DEFERRED** until 7c.17a + 7c.17b close (Wave 4 close-batch). Per governance JSON entry, this story has `prerequisite_stories=["7c-17a", "7c-17b"]` (binding=hard).

**Lookahead-tier=1 rationale:** spec is pre-authored to capture Wave-5 entry intent + readiness checks + AC structure so the operator can dispatch immediately when Wave-4 close lands. Without pre-author, Wave-5 entry would be gated on this session's Claude availability.

**Parallel-dispatch viable with 7c.18b** (path-disjoint at module level: 7c.18a authors `section_06b`; 7c.18b authors `section_07c`). Shared `pyproject.toml` C6 modules list edit requires coordinate-or-sequence per PARALLEL-DISPATCH GUARDRAIL #3.

**V7 v2 Murat triple-condition fit:** C6-touching ✓ + lookahead_tier=1 ✓ + t11_tier=lite ✓ — qualifies for parallel-dispatch under elevated_cap=N+3.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

- 2026-05-06: Focused Wave-5 new tests: 35 passed.
- 2026-05-06: Structural C6 allowlist regression fixed; structural target-list tests: 10 passed.
- 2026-05-06: Broad regression: 45 failed, 4412 passed, 27 skipped, 2 xfailed. Remaining failures are inherited baseline classes; prior new structural failures are resolved.
- 2026-05-06: Ruff clean; lint-imports 12 kept / 0 broken; class-conformance PASS at 19; sandbox-AC PASS.

### Completion Notes List

- Implemented §06B as a standalone no-alias HIL surface with mandatory CLI and optional HTTP/MCP-stdio transports.
- Added `Section06BOperatorVerdict` with submit/edit/discard three-way payload consistency, UUID4/tz-aware/sha256 validators, and LF/no-BOM JSON schema.
- `display_literal_visual_targets` accepts either a dict or JSON path and uses a local `SlideVisualSpecification` shape aligned to 7c.17a diagram-card intent without importing sibling gate packages.
- Build-surface `decision_card_digest` is treated as the digest of the operator-submitted build payload or upstream target package supplied to the verdict envelope.

### File List

- `app/gates/section_06b/__init__.py`
- `app/gates/section_06b/poll_surface.py`
- `app/models/operator_verdict_section_06b.py`
- `app/models/operator_verdict_section_06b.v1.schema.json`
- `tests/gates/section_06b/__init__.py`
- `tests/gates/section_06b/_helpers.py`
- `tests/gates/section_06b/test_literal_visual_build_dsl_registration.py`
- `tests/gates/section_06b/test_literal_visual_build_three_transport_parity.py`
- `tests/schemas/operator_verdict/test_section_06b_shape.py`
- `pyproject.toml`
- `tests/structural/test_import_linter_c4_target_list_populated.py`
- `tests/structural/test_import_linter_c6_target_list_populated.py`
- `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py`

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for Wave-5 entry post-Wave-4 close.
- 2026-05-06: Codex implemented §06B literal-visual build surface, tests, schema, C6 registration, structural allowlist update, and ready-for-review handoff.
