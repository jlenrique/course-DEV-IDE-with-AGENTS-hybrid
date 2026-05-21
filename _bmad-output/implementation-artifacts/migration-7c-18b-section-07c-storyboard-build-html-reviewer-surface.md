# Migration Story 7c.18b: §07C Storyboard Build + HTML Reviewer Surface (FR-7c-27)

**Status:** review *(Codex implementation complete 2026-05-06; ready for T11 lite review.)*
**Sprint key:** `migration-7c-18b-section-07c-storyboard-build-html-reviewer-surface`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 2
**K-target:** 1.3×
**Estimated LOC:** ~450 (poll-surface module ~120 + Section07COperatorVerdict model ~70 + StoryboardBuildPayload model ~50 + HTML reviewer artifact emitter ~60 + JSON schema ~50 + shape-pin ~80 + 3-transport-parity test ~70 + DSL-registration test ~30)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** lite (per governance JSON entry `7c-18b`; AC count ≤5 + sibling-files only + new §section package + new OperatorVerdict variant + HTML emitter is standalone helper + 3-transport schema-stability via FR-7c-49 harness + Codex T10 self-review clean + single-gate)
**Lookahead-tier:** 1
**files_touched:** 7 new + 1 modified (C6 import-linter contract modules list append for `app.gates.section_07c`)

---

## Story

As the operator,
I want to build a storyboard with HTML reviewer surface at §07C, with reviewer artifact rendered for §08B Storyboard B + live-URL HIL consumption,
So that storyboard review has a structured HTML surface (not a flat text dump), submitted via mandatory CLI transport with HTTP + MCP-stdio optional per FR-7c-27 — emitting `Section07COperatorVerdict` with verb ∈ {`submit`, `edit`, `discard`}, with three-transport schema-stability via FR-7c-49 shape-pin discipline.

This is an **operator-build HIL surface** (mirrors 7c.18a §06B's pattern: `submit / edit / discard` build-flavored verbs). The output artifact is an HTML file consumable by **§08B Storyboard B + live-URL HIL** (closed at 7c.13). §07C is the *upstream producer* of the HTML reviewer artifact that §08B *renders for review*.

---

## Predecessor / Dependency Context

- **7c.17a** (Wave 4; close-pending; predecessor for Wave-5 entry): authors `app/marcus/orchestrator/writers/slide_content.py` + `GarySlideContent` Pydantic-v2 model. **§07C's storyboard build consumes Gary's slide outputs upstream**; the storyboard renders per-slide content into a structured HTML reviewer artifact.
- **7c.17b** (Wave 4; close-pending; predecessor for Wave-5 entry): authors `app/marcus/orchestrator/writers/outbound_envelope.py` + envelope schema. §07C's output is one of the per-plan-unit artifacts that may be referenced from the `pre-dispatch-package-gary.md` aggregation.
- **7c.13** (CLOSED 2026-05-06): §08B G3B Storyboard B + live-URL HIL surface. **§08B is the DOWNSTREAM CONSUMER of §07C's HTML reviewer artifact**. The artifact emission shape declared by THIS STORY must be consumable by the §08B poll-surface (which displays the storyboard for operator approval).
- **7c.3b** (CLOSED `f8fc1a8`): §02A G0 poll-surface canonical HIL pattern.
- **7c.14** (CLOSED 2026-05-06): action-flavored verb-set sibling pattern (`select / edit / reject` + 3-way verb-payload `model_validator(mode="after")`) — §07C mirrors with `submit / edit / discard`.
- **7c.18a** (parallel-dispatch SIBLING; same pre-author batch): §06B literal-visual operator build. SAME operator-build pattern; SAME verb set; SAME parity_contract registration shape (no `alias_of`; new family). Verb-payload + schema-pin patterns are byte-equivalent except for surface-specific payload shape.
- **Wave-3 trio + next-batch + G2C-aliased fanout + 7c.13 next-batch (CLOSED 2026-05-05/06):** canonical references for §section package + parity_contract + OperatorVerdict + 3-transport-parity discipline.
- **C6 import-linter contract**: THIS STORY APPENDS `app.gates.section_07c` to C6's modules list (sibling-pair with 7c.18a's `app.gates.section_06b` append; coordinate-or-sequence under parallel dispatch).
- **No alias_of parent family**: §07C is a NEW surface family (NOT aliased to G1/G2/G3/G4/G5/G6). The parity_contract decorator omits `alias_of` (or passes `alias_of=None`).

---

## Acceptance Criteria

### AC-7c.18b-A — §section package + parity_contract registration (FR-7c-27)

**Given** §02A canonical poll-surface pattern + Wave-3 + next-batch sibling §section packages + 7c.18a sibling pre-author
**When** the dev-agent authors `app/gates/section_07c/poll_surface.py`
**Then** the module:
1. Declares `SURFACE_ID = SECTION_07C_SURFACE_ID` (constant from new `app/models/operator_verdict_section_07c.py`).
2. Registers via `@parity_contract(surface_id="section_07c_storyboard_build", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"])` per FR-7c-27 transport defaults. **No `alias_of` kwarg** — §07C is a new family.
3. Implements `display_storyboard_targets(upstream_or_path: Path | dict[str, Any]) -> dict[str, Any]` (poll function; renders the per-plan-unit storyboard targets that the operator must build for; T1-T9 decision: consume from upstream `gary-slide-content.json` (7c.17a deliverable) for slide-content sources + plan-unit metadata).
4. Implements `submit_verdict(plan_unit_id: str, verdict_payload: dict, transport: TransportName) -> Section07COperatorVerdict` (submit function; emits OperatorVerdict).
5. Re-emits `canonical_model_bytes` + `compute_model_digest` helpers locally to satisfy C6 cross-§section independence (per Wave-3-trio + next-batch + G2C-fanout precedent).

### AC-7c.18b-B — OperatorVerdict variant + JSON schema regen (FR-7c-49)

**When** the dev-agent authors `app/models/operator_verdict_section_07c.py` + regenerates `app/models/operator_verdict_section_07c.v1.schema.json`:
1. `Section07COperatorVerdict` Pydantic-v2 model: `surface_id: Literal["section_07c_storyboard_build"]` + `verb: Section07CBuildVerb` (closed `Literal["submit", "edit", "discard"]`) + `plan_unit_id: str` (`min_length=1` + strip-then-non-empty validator per Wave-3 G2A canonical) + standard envelope fields per §02A precedent (run_id UUID4 + operator_id pattern + submitted_at tz-aware + decision_card_digest sha256 + 3-way verb-payload consistency `model_validator(mode="after")` mirroring 7c.14 / 7c.18a).
2. `StoryboardBuildPayload` (mandatory iff verb=submit; carries `target_section: str` + `storyboard_html_path: str` (relative path to the emitted HTML reviewer artifact; min_length=1 + strip-then-non-empty + `.html` suffix validator) + `slide_count: int` (`ge=1`) + `storyboard_html_digest: str` (sha256-hex of the emitted HTML file content; tamper-evidence per NFR-7c-S1)).
3. `StoryboardEditPayload` (mandatory iff verb=edit; mirror `DirectiveEditPayload` shape; carries field-level edits to a previously-submitted storyboard).
4. JSON schema regenerated via Path.write_text(... encoding="utf-8") canonical command (anti-pattern A18). LF-only; NO BOM.

### AC-7c.18b-C — HTML reviewer artifact emitter helper

**Given** the operator-submitted `StoryboardBuildPayload`
**When** the §07C surface processes verb=submit
**Then** an HTML reviewer artifact is emitted to `storyboard_html_path` via a deterministic emitter helper (`emit_storyboard_html(payload: StoryboardBuildPayload, output_path: Path, slide_content: list[...]) -> Path`):
1. The emitter writes a minimal structured HTML document (UTF-8; LF-only line endings; NO BOM) suitable for §08B Storyboard B + live-URL HIL consumption — minimum: `<!doctype html>` + `<title>Storyboard — {plan_unit_id} / {target_section}</title>` + per-slide section blocks rendering slide_index + title + body + (optional) caption.
2. The emitter is byte-deterministic across re-invocations with identical input (test asserts via sha256 hash pin on the emitted bytes).
3. The emitter is colocated with the surface (`app/gates/section_07c/storyboard_html_emitter.py` or inlined in `poll_surface.py`; T1-T9 decision based on size).
4. The emitter does NOT depend on any external HTML-templating library beyond Python stdlib (no Jinja / no MarkupSafe addition; use string-template + html.escape per Python stdlib).

### AC-7c.18b-D — Three-transport schema-stability shape-pin (FR-7c-49)

**Then** `tests/schemas/operator_verdict/test_section_07c_shape.py` asserts `Section07COperatorVerdict` schema hash STABLE across CLI / HTTP / MCP-stdio transports per FR-7c-49 harness pattern. Use `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section07COperatorVerdict, surface_id="section_07c_storyboard_build", transports=["cli", "http", "mcp-stdio"])` from `tests/schemas/operator_verdict/_harness.py`.

### AC-7c.18b-E — DSL-registration audit + 3-transport-parity test + HTML emitter determinism test + C6 import-linter modules list append

**Then**:
1. `tests/gates/section_07c/test_storyboard_build_dsl_registration.py` — asserts `parity_contract` registered with correct surface_id + transports + `alias_of` absent (or None). **Reload-isolated** per 7c.6 Codex precedent.
2. `tests/gates/section_07c/test_storyboard_build_three_transport_parity.py` — round-trips a sample §07C verdict via CLI + HTTP + MCP-stdio simulated transports; asserts payload digest equals across all three.
3. `tests/gates/section_07c/test_storyboard_html_emitter_determinism.py` — invokes the HTML emitter twice with identical input; asserts emitted bytes are sha256-identical (byte-determinism); asserts UTF-8 + LF-only + NO BOM.

**When** the dev-agent updates `pyproject.toml`:
**Then** `app.gates.section_07c` appended to C6 contract `modules` list (post-7c.18a state will include both `section_06b` and `section_07c` if both close). Lint-imports re-runs PASS with 12 KEPT (UNCHANGED count). **PARALLEL-DISPATCH GUARDRAIL #3 (binding):** if 7c.18a dispatches concurrently, two-way coordinate-or-sequence — main thread (or whichever worker integrates first) writes the union of both new §section entries.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks**
  - [x] T1.1 Confirm 7c.17a + 7c.17b done in sprint-status (HARD predecessor block).
  - [x] T1.2 Read 7c.18a sibling spec + Codex prompt (same pre-author batch; pattern parity for §06B/§07C operator-build pair).
  - [x] T1.3 Read `app/gates/section_02a/poll_surface.py` + Wave-3 sibling references.
  - [x] T1.4 Read `app/models/operator_verdict_section_11.py` (action-verb sibling for 3-way verb-payload `model_validator`).
  - [x] T1.5 Read `app/marcus/orchestrator/writers/slide_content.py` + `GarySlideContent` shape (7c.17a; upstream slide-content source for `display_storyboard_targets`).
  - [x] T1.6 Read `app/gates/section_08b/poll_surface.py` (7c.13 deliverable; §08B is the downstream consumer of §07C's HTML artifact — confirm artifact contract assumptions).
  - [x] T1.7 Read `app/parity/contracts/_decorator.py` for parity_contract API + `alias_of` optional kwarg semantics.
  - [x] T1.8 Read ADR 0002 to confirm §07C is NOT in family-aliases catalog.
  - [x] T1.9 Refresh broad-regression baseline + record class-conformance baseline.

- [x] **T2 — Author §section package + OperatorVerdict model**
  - [x] T2.1 Author `app/gates/section_07c/__init__.py` (empty namespace).
  - [x] T2.2 Author `app/gates/section_07c/poll_surface.py` per AC-A.
  - [x] T2.3 Author `app/models/operator_verdict_section_07c.py` per AC-B with `Section07COperatorVerdict` + `StoryboardBuildPayload` + `StoryboardEditPayload` + `Section07CBuildVerb` + `SECTION_07C_SURFACE_ID`.

- [x] **T3 — Author HTML reviewer artifact emitter (AC-C)**
  - [x] T3.1 Implement `emit_storyboard_html` deterministic emitter (Python stdlib only; UTF-8; LF-only; NO BOM; sha256-stable bytes).
  - [x] T3.2 Colocate with surface (`app/gates/section_07c/storyboard_html_emitter.py` OR inlined in `poll_surface.py`; T1-T9 decision).

- [x] **T4 — Generate JSON schema (AC-B)**
  - [x] T4.1 Generate `app/models/operator_verdict_section_07c.v1.schema.json` via:
    ```bash
    .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_07c import Section07COperatorVerdict; import json; Path('app/models/operator_verdict_section_07c.v1.schema.json').write_text(json.dumps(Section07COperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
    ```
    (Path.write_text per A18; NO PowerShell `>` redirection.)

- [x] **T5 — Author shape-pin + 3-transport-parity test + DSL-registration audit + HTML emitter determinism test (AC-D + AC-E)**
  - [x] T5.1 Author `tests/schemas/operator_verdict/test_section_07c_shape.py` using FR-7c-49 harness.
  - [x] T5.2 Author `tests/gates/section_07c/__init__.py` + `_helpers.py`.
  - [x] T5.3 Author `tests/gates/section_07c/test_storyboard_build_dsl_registration.py` (reload-isolated).
  - [x] T5.4 Author `tests/gates/section_07c/test_storyboard_build_three_transport_parity.py`.
  - [x] T5.5 Author `tests/gates/section_07c/test_storyboard_html_emitter_determinism.py`.

- [x] **T6 — C6 import-linter modules list append (AC-E)**
  - [x] T6.1 Update `pyproject.toml::tool.importlinter::contracts::C6::modules` to append `app.gates.section_07c`. **PARALLEL-DISPATCH GUARDRAIL #3:** if running concurrently with 7c.18a, write the union of both new §section entries.

- [x] **T7 — Verification battery (R-tier R2)**
  - [x] T7.1 Focused: `pytest tests/gates/section_07c/ tests/schemas/operator_verdict/test_section_07c_shape.py -p no:randomly -q --tb=short` PASS.
  - [x] T7.2 §02A non-regression: PASS UNCHANGED.
  - [x] T7.3 Wave-3 + Wave-3-next-batch + G2C-fanout non-regression sweep: PASS UNCHANGED.
  - [x] T7.4 Wave-4 Marcus-writer non-regression: `pytest tests/marcus/orchestrator/writers/ -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [x] T7.5 §08B non-regression: `pytest tests/gates/section_08b/ -p no:randomly -q --tb=short` PASS UNCHANGED (§08B consumes §07C output downstream — non-regression confirms no contract break).
  - [x] T7.6 Smoke: nodeid baseline UNCHANGED.
  - [x] T7.7 R2 broad: failure count ≤ T1 baseline (45 failed vs inherited 47-failure Wave-5 pre-fix run; structural new-target failures resolved).
  - [x] T7.8 Class-conformance: PASS at 19 parity contract files; shape-pin files live under `tests/schemas/operator_verdict/`.
  - [x] T7.9 Lint-imports: 12 KEPT / 0 broken UNCHANGED.
  - [x] T7.10 Sandbox-AC: PASS.
  - [x] T7.11 Ruff: clean.

- [x] **T10 — Codex self-review dropbox**
  - [x] T10.1 Drop `_codex-handoff/7c-18b.ready-for-review.md`.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-18a-section-06b-literal-visual-operator-build.md` (sibling spec; same operator-build verb-set pattern; same pre-author batch).
3. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor).
4. `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (DOWNSTREAM consumer of §07C's HTML artifact — §08B reads what §07C emits).
5. `_bmad-output/implementation-artifacts/migration-7c-14-section-11-g4a-voice-selection.md` (action-flavored verb-set + 3-way verb-payload `model_validator`).
6. `_bmad-output/implementation-artifacts/migration-7c-17a-marcus-writers-slide-content-fidelity-slides-diagram-cards.md` (Wave-4 predecessor; `GarySlideContent` shape — upstream slide-content source).
7. `app/gates/section_02a/poll_surface.py` + `app/gates/section_11/poll_surface.py` + `app/gates/section_08b/poll_surface.py` (canonical + action-verb + downstream-consumer pattern references).
8. `app/models/operator_verdict_section_02a.py` + `app/models/operator_verdict_section_11.py` (canonical + action-verb references).
9. `app/marcus/orchestrator/writers/slide_content.py` (7c.17a; `GarySlideContent` shape).
10. `tests/schemas/operator_verdict/_harness.py` (FR-7c-49 harness; READ-ONLY).
11. `tests/schemas/operator_verdict/test_section_02a_shape.py` + Wave-3 + next-batch shape-pins.
12. `tests/gates/section_02a/*.py` + Wave-3 + next-batch DSL-registration + 3-transport-parity tests.
13. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract API + `alias_of` optional).
14. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (confirm §07C is NOT in family-aliases catalog).
15. `pyproject.toml::tool.importlinter` (C6 contract).
16. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
17. Governance JSON `7c-18b` entry: gate_mode=single-gate, K=1.3×, t11_tier=lite, lookahead_tier=1, prerequisite_stories=["7c-17a", "7c-17b"].
18. `_bmad-output/planning-artifacts/epics-slab-7c-orchestrational-tail.md §Story 7c.18b` (epic-level scope authority).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS expected at AMELIA-P2.

---

## Dispatch state

**DISPATCH-DEFERRED** until 7c.17a + 7c.17b close. Per governance JSON entry, this story has `prerequisite_stories=["7c-17a", "7c-17b"]` (binding=hard).

**Lookahead-tier=1 rationale:** spec is pre-authored to capture Wave-5 entry intent so the operator can dispatch immediately when Wave-4 close lands.

**Parallel-dispatch viable with 7c.18a** (path-disjoint at module level: 7c.18a authors `section_06b`; 7c.18b authors `section_07c`). Shared `pyproject.toml` C6 modules list edit requires coordinate-or-sequence per PARALLEL-DISPATCH GUARDRAIL #3.

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

- Implemented §07C as a standalone no-alias HIL surface with mandatory CLI and optional HTTP/MCP-stdio transports.
- Added `Section07COperatorVerdict` with submit/edit/discard three-way payload consistency, `.html` path validation, sha256 HTML digest validation, and LF/no-BOM JSON schema.
- `display_storyboard_targets` accepts either a dict or JSON path; the upstream payload is the Gary slide-content package shape from 7c.17a plus plan-unit metadata.
- Colocated the deterministic HTML emitter in `app/gates/section_07c/storyboard_html_emitter.py`; it uses only stdlib `html.escape`, writes UTF-8 LF bytes, and is sha256-stable across identical invocations.

### File List

- `app/gates/section_07c/__init__.py`
- `app/gates/section_07c/poll_surface.py`
- `app/gates/section_07c/storyboard_html_emitter.py`
- `app/models/operator_verdict_section_07c.py`
- `app/models/operator_verdict_section_07c.v1.schema.json`
- `tests/gates/section_07c/__init__.py`
- `tests/gates/section_07c/_helpers.py`
- `tests/gates/section_07c/test_storyboard_build_dsl_registration.py`
- `tests/gates/section_07c/test_storyboard_build_three_transport_parity.py`
- `tests/gates/section_07c/test_storyboard_html_emitter_determinism.py`
- `tests/schemas/operator_verdict/test_section_07c_shape.py`
- `pyproject.toml`
- `tests/structural/test_import_linter_c4_target_list_populated.py`
- `tests/structural/test_import_linter_c6_target_list_populated.py`
- `tests/structural/test_import_linter_contracts_c4_c5_c6_present.py`

### Change Log

- 2026-05-06: Spec pre-authored by Claude (lookahead_tier=1) for Wave-5 entry post-Wave-4 close.
- 2026-05-06: Codex implemented §07C storyboard build surface, deterministic HTML reviewer emitter, tests, schema, C6 registration, structural allowlist update, and ready-for-review handoff.
