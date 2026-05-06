# Migration Story 7c.15: §11B G4B Input-Package + §15 G5 Final Operator Handoff (FR-7c-19 + FR-7c-29 AMEND-4 Fold)

**Status:** in-progress *(Codex T1 started 2026-05-06; 7c.17b predecessor is now done.)*
**Sprint key:** `migration-7c-15-section-11b-g4b-section-15-g5-final-operator-handoff`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 3 (heavier than other Wave-3 stories — dual-FR + dual surface + Marcus writer)
**K-target:** 1.6×
**Estimated LOC:** ~700 (2× poll-surface modules ~240 + 2× OperatorVerdict models ~100 + 2× JSON schemas ~100 + 2× shape-pins ~160 + 2× 3-transport-parity tests ~140 + 2× DSL-registration tests ~60 + Marcus writer ~150 + Marcus writer tests ~100)
**Gate-mode:** single-gate (per John PM Round-2: dual-FR co-dependent — JTBD round-trip; do NOT split)
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** standard (per governance JSON; AC count >5 + Marcus writer module touch + dual surface)
**Lookahead-tier:** 2
**files_touched:** 14 new + 1 modified (C6 import-linter contract modules list append for 2 new §sections)

---

## Story

As the dev-agent,
I want both the §11B G4B input-package preview HIL surface AND the §15 G5 final operator handoff HIL surface authored as NEW §section packages, alongside the Marcus-side §15 bundle emission writer (FR-7c-29 — assembly bundle + DESCRIPT-ASSEMBLY-GUIDE.md regen + Trial-3 transcript anchor + slab-close evidence pointer),
So that operators can review the input-package preview at §11B (mandatory CLI + HTTP) AND complete the final operator handoff at §15 (mandatory CLI + HTTP + MCP-stdio per FR-7c-19), with Marcus emitting the consolidated slab-close bundle keyed to the §15 G5 OperatorVerdict acceptance.

This story implements **AMEND-4 fold** per John PM Round-2: FR-7c-19 (operator-side §11B + §15) and FR-7c-29 (Marcus-side §15 bundle emission) are JTBD round-trip co-dependent — the operator's §15 G5 acceptance triggers Marcus's bundle emission; splitting them would require a synthetic intermediate state with no real consumer.

---

## Predecessor / Dependency Context

- **7c.5.G4** (CLOSED `0ec80df`): G4 family DecisionCard contract; G4B aliases to G4 per ADR 0002 §2.
- **7c.5.G5** (CLOSED `f059e84`): G5 family DecisionCard contract; §15 G5 surface consumes G5Card (post-G5-fresh-author).
- **7c.3b** (CLOSED `f8fc1a8`): §02A G0 poll-surface canonical HIL pattern.
- **7c.17b** (BACKLOG; Wave 4): authors `gary-outbound-envelope.yaml` aggregation. **THIS STORY'S MARCUS WRITER CONSUMES 7c.17b'S OUTPUT** for the §15 bundle emission. **HARD DISPATCH-BLOCKER: 7c.15 cannot dispatch until 7c.17b closes.**
- **G4Card** (closed at 7c.5.G4 `0ec80df`): consumed by §11B G4B poll-surface as the input-package preview payload.
- **G5Card** (closed at 7c.5.G5 `f059e84`): consumed by §15 G5 poll-surface as the final-handoff payload.
- **Wave-3 trio sibling pattern** (7c.6/7c.7/7c.8) + **Wave-3 next-batch** (7c.13/7c.14): canonical references for §section poll-surface + OperatorVerdict + 3-transport-parity discipline.
- **C6 import-linter contract**: this story APPENDS BOTH `app.gates.section_11b` AND `app.gates.section_15` to C6's modules list (two-entry append).

---

## Acceptance Criteria

### AC-7c.15-A — §11B G4B input-package poll-surface (FR-7c-19 §11B)

**Given** §02A canonical poll-surface pattern + Wave-3 sibling §section precedents
**When** the dev-agent authors `app/gates/section_11b/poll_surface.py`
**Then** the module:
1. Declares `SURFACE_ID = SECTION_11B_SURFACE_ID`.
2. Registers via `@parity_contract(surface_id="section_11b_g4b_input_package", mandatory_transports=["cli", "http"], optional_transports=["mcp-stdio"], alias_of="G4")` per FR-7c-19 §11B.
3. Implements `display_input_package(g4_card_or_path: G4Card | Path) -> dict[str, Any]`.
4. Implements `submit_verdict(input_package_id: str, verdict_payload: dict, transport: TransportName) -> Section11BOperatorVerdict`.
5. Re-emits `canonical_model_bytes` + `compute_model_digest` helpers locally.

### AC-7c.15-B — §15 G5 final-operator-handoff poll-surface (FR-7c-19 §15)

**When** the dev-agent authors `app/gates/section_15/poll_surface.py`
**Then** the module:
1. Declares `SURFACE_ID = SECTION_15_SURFACE_ID`.
2. Registers via `@parity_contract(surface_id="section_15_g5_final_handoff", mandatory_transports=["cli", "http", "mcp-stdio"], optional_transports=[], alias_of="G5")` per FR-7c-19 §15 (3-mandatory; no optional).
3. Implements `display_final_handoff(g5_card_or_path: G5Card | Path) -> dict[str, Any]`.
4. Implements `submit_verdict(handoff_id: str, verdict_payload: dict, transport: TransportName) -> Section15OperatorVerdict`.
5. Re-emits digest helpers locally.

### AC-7c.15-C — Section11BOperatorVerdict + Section15OperatorVerdict + JSON schemas (FR-7c-49)

**When** the dev-agent authors `app/models/operator_verdict_section_11b.py` + `app/models/operator_verdict_section_15.py` + regenerates both `.v1.schema.json` files:
1. `Section11BOperatorVerdict`: surface_id Literal["section_11b_g4b_input_package"] + verb `Literal["approve", "edit", "reject"]` + input_package_id strip-then-non-empty + standard envelope fields + InputPackageEditPayload.
2. `Section15OperatorVerdict`: surface_id Literal["section_15_g5_final_handoff"] + verb `Literal["complete", "edit", "reject"]` (per FR-7c-19 "Operator completes final operator handoff" — completion-action verb) + handoff_id strip-then-non-empty + standard envelope fields + HandoffEditPayload.
3. Both JSON schemas regenerated via Path.write_text(... encoding="utf-8") per A18. LF-only; NO BOM.

### AC-7c.15-D — Three-transport schema-stability shape-pins (FR-7c-49 ×2)

**Then**:
1. `tests/schemas/operator_verdict/test_section_11b_shape.py` asserts `Section11BOperatorVerdict` schema hash STABLE across CLI / HTTP / MCP-stdio.
2. `tests/schemas/operator_verdict/test_section_15_shape.py` asserts `Section15OperatorVerdict` schema hash STABLE across CLI / HTTP / MCP-stdio.
Both via `assert_operator_verdict_schema_stable_across_transports(...)` from `tests/schemas/operator_verdict/_harness.py`.

### AC-7c.15-E — DSL-registration audits + 3-transport-parity tests (×2 surfaces)

**Then**:
1. `tests/gates/section_11b/test_g4b_poll_surface_dsl_registration.py` (alias_of="G4"; CLI+HTTP mandatory) + `test_g4b_poll_surface_three_transport_parity.py`. Reload-isolated.
2. `tests/gates/section_15/test_g5_poll_surface_dsl_registration.py` (alias_of="G5"; CLI+HTTP+MCP-stdio mandatory; `optional_transports=[]`) + `test_g5_poll_surface_three_transport_parity.py`. Reload-isolated.

### AC-7c.15-F — Marcus §15 bundle emission writer (FR-7c-29)

**Given** 7c.17b's outbound-envelope.yaml aggregation (DISPATCH-BLOCKER if absent)
**When** the dev-agent authors `app/marcus/orchestrator/writers/section_15_bundle.py`
**Then** the writer:
1. Defines a Pydantic-v2 model `Section15Bundle` with `validate_assignment=True` capturing: assembly_bundle_path (Path; non-empty), descript_assembly_guide_md_digest (sha256), trial_3_transcript_anchor (sha256 hash-anchor), slab_close_evidence_path (Path).
2. Implements `emit_section_15_bundle(g5_verdict: Section15OperatorVerdict, outbound_envelope: ...) -> Section15Bundle` — triggered ON §15 G5 verb=complete acceptance.
3. Regenerates DESCRIPT-ASSEMBLY-GUIDE.md from final state (consumes 7c.17b's outbound-envelope.yaml + each per-plan-unit pre-dispatch package + slab-close ceremony state).
4. Computes Trial-3 transcript anchor (sha256 of the live-trial transcript file).
5. Writes slab-close evidence pointer to consolidated path.
6. Sanctum-alignment per FR-7c-54: writer module declares its sanctum-alignment row in the Marcus activation block per Slab 7b precedent (memory entry `project_slab_7b_skill_md_sanctum_alignment.md`) OR documents an explicit Cora-sidecar-style exception.

### AC-7c.15-G — C6 import-linter modules list append (×2 entries)

**When** the dev-agent updates `pyproject.toml`:
**Then** BOTH `app.gates.section_11b` AND `app.gates.section_15` appended to C6 contract `modules` list. Lint-imports re-runs PASS with 12 KEPT (UNCHANGED count). **Note:** `app.marcus.orchestrator.writers.section_15_bundle` lives under `app.marcus` not `app.gates`, so it is NOT a C6 entry — it is governed by Marcus contracts M1-M4 instead.

---

## Tasks / Subtasks

- [ ] **T1 — Readiness checks**
  - [ ] T1.1 Confirm 7c.5.G4 + 7c.5.G5 + 7c.3b done. **CONFIRM 7c.17b done (HARD BLOCKER).**
  - [ ] T1.2 Read §02A canonical pattern + Wave-3 trio sibling pattern (7c.6/7c.7/7c.8) + 7c.13/7c.14 specs (next-batch sibling pattern; closer transport-set match for §11B).
  - [ ] T1.3 Read `app/models/decision_cards/g4.py` + `app/models/decision_cards/g5.py` for G4Card + G5Card consumption.
  - [ ] T1.4 Read 7c.17b deliverable: `gary-outbound-envelope.yaml` schema + writer module (`app/marcus/orchestrator/writers/outbound_envelope.py` per Wave-4 7c.17b spec).
  - [ ] T1.5 Read existing Marcus writer modules under `app/marcus/orchestrator/writers/` for sanctum-alignment pattern (per Slab 7b precedent).
  - [ ] T1.6 Read ADR 0002 §3 for alias_of forward syntax (G4 + G5 alias-clause inheritance for §11B + §15 surfaces).
  - [ ] T1.7 Refresh broad-regression baseline + record class-conformance baseline.

- [ ] **T2 — Author §11B G4B §section package + OperatorVerdict model + JSON schema**
  - [ ] T2.1 `app/gates/section_11b/{__init__,poll_surface}.py`.
  - [ ] T2.2 `app/models/operator_verdict_section_11b.py` + regen `.v1.schema.json`.

- [ ] **T3 — Author §15 G5 §section package + OperatorVerdict model + JSON schema**
  - [ ] T3.1 `app/gates/section_15/{__init__,poll_surface}.py`.
  - [ ] T3.2 `app/models/operator_verdict_section_15.py` + regen `.v1.schema.json`.

- [ ] **T4 — Author Marcus §15 bundle emission writer (FR-7c-29)**
  - [ ] T4.1 `app/marcus/orchestrator/writers/section_15_bundle.py` with `Section15Bundle` Pydantic-v2 model + `emit_section_15_bundle` function.
  - [ ] T4.2 Sanctum-alignment row added to Marcus activation block (per Slab 7b precedent) OR Cora-sidecar exception documented.
  - [ ] T4.3 DESCRIPT-ASSEMBLY-GUIDE.md regeneration logic (consume 7c.17b outbound-envelope.yaml + per-plan-unit packages).
  - [ ] T4.4 Trial-3 transcript anchor computation (sha256).
  - [ ] T4.5 Slab-close evidence pointer wiring.

- [ ] **T5 — Author shape-pins + 3-transport-parity tests + DSL-registration audits (×2 surfaces)**
  - [ ] T5.1 `tests/schemas/operator_verdict/test_section_11b_shape.py`.
  - [ ] T5.2 `tests/schemas/operator_verdict/test_section_15_shape.py`.
  - [ ] T5.3 `tests/gates/section_11b/{__init__,_helpers,test_g4b_poll_surface_dsl_registration,test_g4b_poll_surface_three_transport_parity}.py`.
  - [ ] T5.4 `tests/gates/section_15/{__init__,_helpers,test_g5_poll_surface_dsl_registration,test_g5_poll_surface_three_transport_parity}.py`.

- [ ] **T6 — Author Marcus writer tests**
  - [ ] T6.1 `tests/marcus/orchestrator/writers/test_section_15_bundle.py` — covers `Section15Bundle` shape, `emit_section_15_bundle` behavior, DESCRIPT-ASSEMBLY-GUIDE.md regen determinism, Trial-3 anchor sha256, sanctum-alignment row presence.

- [ ] **T7 — C6 import-linter modules list append (AC-G)**
  - [ ] T7.1 Update `pyproject.toml::tool.importlinter::contracts::C6::modules` to append BOTH `app.gates.section_11b` AND `app.gates.section_15`.

- [ ] **T8 — Verification battery (R-tier R2; standard-tier T11)**
  - [ ] T8.1 Focused: pytest `tests/gates/section_11b/` + `tests/gates/section_15/` + both shape-pins.
  - [ ] T8.2 Focused: pytest Marcus writer tests.
  - [ ] T8.3 §02A non-regression PASS.
  - [ ] T8.4 Wave-3 trio non-regression PASS.
  - [ ] T8.5 Marcus contracts M1-M4 non-regression PASS.
  - [ ] T8.6 Smoke baseline UNCHANGED.
  - [ ] T8.7 R2 broad: failure count ≤ T1 baseline (delta ≤ 0); per-failure git-log-attribution.
  - [ ] T8.8 Class-conformance: T1-baseline + 2 (TWO new shape-pin files).
  - [ ] T8.9 Lint-imports: 12 KEPT / 0 broken.
  - [ ] T8.10 Sandbox-AC: PASS.
  - [ ] T8.11 Ruff: clean.

- [ ] **T10 — Codex self-review dropbox**
  - [ ] T10.1 Drop `_codex-handoff/7c-15.ready-for-review.md`. Standard-tier T11 means dropbox includes deeper coverage: Marcus-writer-test attribution + sanctum-alignment evidence + cross-surface coordination evidence + dual-FR fold rationale verification.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor).
3. `_bmad-output/implementation-artifacts/migration-7c-6-section-04a-g1a-per-plan-unit-ratification.md` + `migration-7c-13-section-08b-g3b-storyboard-b-live-url.md` (sibling references; §11B closest match for transport-set CLI+HTTP).
4. `_bmad-output/implementation-artifacts/migration-7c-17b-...md` (predecessor; outbound-envelope writer reference for §15 bundle consumption).
5. `app/gates/section_02a/poll_surface.py` + Wave-3 trio §section packages (canonical + sibling pattern).
6. `app/models/operator_verdict_section_02a.py` + Wave-3 trio OperatorVerdict variants.
7. `app/models/decision_cards/g4.py` + `app/models/decision_cards/g5.py` (G4Card + G5Card consumption).
8. `app/marcus/orchestrator/writers/` (existing Marcus writers for sanctum-alignment pattern).
9. `app/marcus/orchestrator/writers/outbound_envelope.py` (7c.17b deliverable; consumed by §15 bundle writer).
10. `tests/schemas/operator_verdict/_harness.py` (FR-7c-49 harness; READ-ONLY).
11. `tests/schemas/operator_verdict/test_section_02a_shape.py` + Wave-3 trio shape-pins.
12. `tests/gates/section_02a/*.py` + Wave-3 trio test patterns.
13. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax).
14. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G4B + G5 alias mappings per §2; G5 is a net-new family — NOT an alias).
15. `pyproject.toml::tool.importlinter` (C6 contract).
16. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
17. Memory entry `project_slab_7b_skill_md_sanctum_alignment.md` (sanctum-alignment row pattern for Marcus writer).
18. Governance JSON `7c-15` entry + `wave_3_lookahead_policy::current_cap=3` (V7 v1.1; V7 v2 auto-fired).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS (expected; validator must run pre-dispatch).

---

## Dispatch state

**DISPATCH-BLOCKED on 7c.17b** (Wave 4 backlog). 7c.15's Marcus §15 bundle writer (FR-7c-29) consumes 7c.17b's `gary-outbound-envelope.yaml` aggregation; without 7c.17b's outbound-envelope writer landed, the §15 bundle writer cannot reference its input contract.

**Unblock path:** operator advances to Wave 4 (open 7c.17a + 7c.17b stories), closes 7c.17b, then 7c.15 dispatches.

**Alternative scope-narrowing path (NOT recommended):** split 7c.15 into 7c.15a (HIL surfaces only — §11B + §15) and 7c.15b (Marcus §15 bundle writer; depends on 7c.17b). This was REJECTED at PRD round per John PM Round-2 ("dual-FR co-dependent — JTBD round-trip; do NOT split"). If split is reconsidered, requires party-mode re-ratification.

**Lookahead-tier=2 rationale:** spec is pre-authored to capture scope intent + readiness checks + AC structure; dispatch deferred until 7c.17b lands. Pre-authoring at lookahead=2 ensures 7c.15's planning doesn't get lost in Wave-4 churn.

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

(populated by Codex at T1-T9)

### Completion Notes List

(populated by Codex at T10)

### File List

(populated by Codex at T10)

### Change Log

- 2026-05-05: Spec pre-authored by Claude (lookahead_tier=2) for post-7c.17b dispatch.
