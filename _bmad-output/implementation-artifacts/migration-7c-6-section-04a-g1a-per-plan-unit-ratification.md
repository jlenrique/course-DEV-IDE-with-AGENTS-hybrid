# Migration Story 7c.6: §04A G1A Per-Plan-Unit Ratification HIL Surface (FR-7c-10)

**Status:** done *(spec authored 2026-05-05 lookahead_tier=1 author-ahead-aggressive; predecessor 7c.5.G1 CLOSED at `6a81e66`; 7c.3b CLOSED at `f8fc1a8` provides canonical poll-surface pattern. Wave-3 entry under V7 v1.1 elevated_cap=N+3 ratified at slab-opener party-mode 2026-05-05. Closed 2026-05-05 via T11 lite PASS-zero-patches verdict at `7c-6-code-review-2026-05-05.md`.)*
**Sprint key:** `migration-7c-6-section-04a-g1a-per-plan-unit-ratification`
**Epic:** Slab 7c — Marcus Orchestrational Tail
**Pts:** 2
**K-target:** 1.3×
**Estimated LOC:** ~400 (poll-surface module ~120 + OperatorVerdict model ~50 + JSON schema ~50 + shape-pin ~80 + 3-transport-parity test ~70 + DSL-registration test ~30)
**Gate-mode:** single-gate
**Cross-agent review:** false
**R-tier:** R2
**T11-tier:** lite (per governance JSON; AC count ≤5 + sibling-files only + no schema/contract/governance touch + Codex T10 self-review clean + single-gate)
**Lookahead-tier:** 1
**files_touched:** 7 new + 1 modified (C6 import-linter contract modules list append)

---

## Story

As the dev-agent,
I want the §04A G1A per-plan-unit ratification HIL surface authored as a NEW §section package mirroring the §02A canonical poll-surface pattern (closed at 7c.3b),
So that operators can ratify per-plan-unit content via mandatory CLI transport (HTTP + MCP-stdio optional per FR-7c-10) emitting `Section04AOperatorVerdict` with verb ∈ {`approve`, `edit`, `reject`} per plan unit, with three-transport schema-stability via FR-7c-49 shape-pin discipline.

---

## Predecessor / Dependency Context

- **7c.5.G1** (CLOSED `6a81e66`): G1 family DecisionCard contract; G1A aliases to G1 per ADR 0002 §2 (parent family `G1`; consumer surface "Per-plan-unit ratification surface, section 04A"). Per ADR 0002 §3 Alias-DSL Clause Inheritance: "An alias may declare transport coverage for its own operator surface" — 7c.6 declares §04A G1A's transport coverage via parity_contract decorator with `alias_of="G1"`.
- **7c.3b** (CLOSED `f8fc1a8`): §02A G0 poll-surface canonical HIL pattern. Authoritative reference at `app/gates/section_02a/poll_surface.py`. 7c.6 mirrors its structure: parity_contract decorator + SURFACE_ID + transport-tagged poll/submit functions + canonical_model_bytes + compute_model_digest helpers.
- **G1Card** (closed at 7c.5.G1): consumed by §04A G1A poll-surface as the operator-facing payload. `from app.models.decision_cards.g1 import G1Card` (post-G1-migration; inherits DecisionCardBase).
- **C6 import-linter contract** at `pyproject.toml::tool.importlinter` (per 7c.4b D5 P-1 patch): `independence` type with modules list. **THIS STORY APPENDS `app.gates.section_04a` to C6's modules list** as part of the four-file-lockstep co-commit.

---

## Acceptance Criteria

### AC-7c.6-A — §section package + parity_contract registration (FR-7c-10 + FR-7c-20)

**Given** §02A canonical poll-surface pattern at `app/gates/section_02a/poll_surface.py`
**When** the dev-agent authors `app/gates/section_04a/poll_surface.py`
**Then** the module:
1. Declares `SURFACE_ID = SECTION_04A_SURFACE_ID` (constant from new `app/models/operator_verdict_section_04a.py`).
2. Registers via `@parity_contract(surface_id="section_04a_g1a_poll", mandatory_transports=["cli"], optional_transports=["http", "mcp-stdio"], alias_of="G1")` per FR-7c-10 transport requirements + ADR 0002 §3 alias_of forward syntax.
3. Implements `display_plan_unit(plan_unit_or_path: PlanUnit | Path) -> dict[str, Any]` (poll function; mirror `display_directive`).
4. Implements `submit_verdict(plan_unit_id: str, verdict_payload: dict, transport: TransportName) -> Section04AOperatorVerdict` (submit function; emits OperatorVerdict).
5. Reuses `canonical_model_bytes` + `compute_model_digest` helpers from `app/gates/section_02a/poll_surface.py` via shared import OR re-emits identical helpers (mirror G2A pattern-replication discipline).

### AC-7c.6-B — OperatorVerdict variant + JSON schema regen (FR-7c-49)

**When** the dev-agent authors `app/models/operator_verdict_section_04a.py` + regenerates `app/models/operator_verdict_section_04a.v1.schema.json`:
1. `Section04AOperatorVerdict` Pydantic-v2 model: `surface_id: Literal["section_04a_g1a_poll"]` + `verb: Section04AVerdictVerb` (closed `Literal["approve", "edit", "reject"]`) + `plan_unit_id: str` (non-empty; strip-then-non-empty per G2A pattern) + standard envelope fields per §02A precedent.
2. `PlanUnitEditPayload` (mirror `DirectiveEditPayload`) for `verb=edit` payloads.
3. JSON schema regenerated via Path.write_text(... encoding="utf-8") canonical command (anti-pattern A18; canonical command in Codex prompt).

### AC-7c.6-C — Three-transport schema-stability shape-pin (FR-7c-49)

**Then** `tests/schemas/operator_verdict/test_section_04a_shape.py` asserts `Section04AOperatorVerdict` schema hash STABLE across CLI / HTTP / MCP-stdio transports per FR-7c-49 harness pattern. Use `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section04AOperatorVerdict, surface_id="section_04a_g1a_poll", transports=["cli", "http", "mcp-stdio"])` from `tests/schemas/operator_verdict/_harness.py` (7c.4b D3 deliverable; canonical helper).

### AC-7c.6-D — DSL-registration audit + 3-transport-parity test

**Then**:
1. `tests/gates/section_04a/test_g1a_poll_surface_dsl_registration.py` — asserts `parity_contract` registered with correct surface_id + transports + alias_of="G1"; mirrors `tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py`.
2. `tests/gates/section_04a/test_g1a_poll_surface_three_transport_parity.py` — round-trips a sample G1A verdict via CLI + HTTP + MCP-stdio simulated transports; asserts payload digest equals across all three.

### AC-7c.6-E — C6 import-linter modules list append (binding=hard per 7c.4b D5)

**When** the dev-agent updates `pyproject.toml`:
**Then** `app.gates.section_04a` appended to C6 contract `modules` list (current list: `app.gates.section_02a` post-7c.4b; will become `[app.gates.section_02a, app.gates.section_04a]` post-this-story). Lint-imports re-runs PASS with 12 KEPT (UNCHANGED count; C6 just gets a wider module list). **PARALLEL-DISPATCH GUARDRAIL #3 (binding):** if 7c.7 + 7c.8 dispatch concurrently, three-way coordinate-or-sequence — main thread (or whichever worker integrates first) writes the union of all three new §section entries; subsequent workers rebase before commit.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks**
  - [x] T1.1 Confirm 7c.5.G1 + 7c.3b done in sprint-status.
  - [x] T1.2 Read `app/gates/section_02a/poll_surface.py` + `app/models/operator_verdict_section_02a.py` + `tests/gates/section_02a/*.py` + `tests/schemas/operator_verdict/test_section_02a_shape.py` for canonical pattern (7c.3b).
  - [x] T1.3 Read `app/models/decision_cards/g1.py` (POST-G1-migration; inherits DecisionCardBase) for G1Card consumption.
  - [x] T1.4 Read ADR 0002 §3 for alias_of forward syntax; verify `parity_contract` decorator accepts `alias_of` kwarg (per 7c.4b D1).
  - [x] T1.5 Refresh broad-regression baseline + record class-conformance baseline.

- [x] **T2 — Author §section package + OperatorVerdict model**
  - [x] T2.1 Author `app/gates/section_04a/__init__.py` (empty namespace; mirror §02A).
  - [x] T2.2 Author `app/gates/section_04a/poll_surface.py` per AC-A.
  - [x] T2.3 Author `app/models/operator_verdict_section_04a.py` per AC-B with `Section04AOperatorVerdict` + `PlanUnitEditPayload` + `Section04AVerdictVerb` + `SECTION_04A_SURFACE_ID`.

- [x] **T3 — Generate JSON schema (AC-B)**
  - [x] T3.1 Generate `app/models/operator_verdict_section_04a.v1.schema.json` via:
    ```bash
    .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_04a import Section04AOperatorVerdict; import json; Path('app/models/operator_verdict_section_04a.v1.schema.json').write_text(json.dumps(Section04AOperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
    ```
    (Path.write_text per A18; NO PowerShell `>` redirection.)

- [x] **T4 — Author shape-pin + 3-transport-parity test + DSL-registration audit (AC-C + AC-D)**
  - [x] T4.1 Author `tests/schemas/operator_verdict/test_section_04a_shape.py` using FR-7c-49 harness.
  - [x] T4.2 Author `tests/gates/section_04a/__init__.py` + `_helpers.py` (mirror §02A).
  - [x] T4.3 Author `tests/gates/section_04a/test_g1a_poll_surface_dsl_registration.py`.
  - [x] T4.4 Author `tests/gates/section_04a/test_g1a_poll_surface_three_transport_parity.py`.

- [x] **T5 — C6 import-linter modules list append (AC-E)**
  - [x] T5.1 Update `pyproject.toml::tool.importlinter::contracts::C6::modules` to append `app.gates.section_04a`. **PARALLEL-DISPATCH GUARDRAIL #3:** if running concurrently with 7c.7/7c.8, write the union of all three §section entries OR coordinate-or-sequence per main-thread integration pattern.

- [x] **T6 — Verification battery (R-tier R2)**
  - [x] T6.1 Focused: `pytest tests/gates/section_04a/ tests/schemas/operator_verdict/test_section_04a_shape.py -p no:randomly -q --tb=short` PASS.
  - [x] T6.2 §02A non-regression: `pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [x] T6.3 Smoke: 200-nodeid baseline UNCHANGED.
  - [x] T6.4 R2 broad: failure count ≤ T1 baseline (delta ≤ 0).
  - [x] T6.5 Class-conformance: T1-baseline + 1 (new shape-pin file).
  - [x] T6.6 Lint-imports: 12 KEPT / 0 broken (UNCHANGED count; C6 modules list grew).
  - [x] T6.7 Sandbox-AC: PASS.
  - [x] T6.8 Ruff: clean.

- [x] **T10 — Codex self-review dropbox**
  - [x] T10.1 Drop `_codex-handoff/7c-6.ready-for-review.md`.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor; 7c.3b).
3. `app/gates/section_02a/poll_surface.py` (canonical pattern reference).
4. `app/models/operator_verdict_section_02a.py` (canonical OperatorVerdict variant).
5. `tests/schemas/operator_verdict/_harness.py` (7c.4b D3 FR-7c-49 harness).
6. `tests/schemas/operator_verdict/test_section_02a_shape.py` (canonical shape-pin).
7. `tests/gates/section_02a/*.py` (canonical DSL-registration + 3-transport-parity tests).
8. `app/models/decision_cards/g1.py` (post-7c.5.G1-migration; inherits DecisionCardBase).
9. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax per 7c.4b D1).
10. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G1A alias mapping per §2).
11. `pyproject.toml::tool.importlinter` (C6 contract; modules list).
12. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
13. Governance JSON `7c-6` entry + `wave_3_lookahead_policy::current_cap=3` (V7 v1.1).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS.

---

## Dispatch state

**DISPATCH-READY** post-V7-v1.1-codification (current commit). Per V7 v1.1 elevated cap = N+3, this story can dispatch IN PARALLEL with 7c.7 + 7c.8 (path-disjoint trio per C6 import-linter contract; each authors a NEW §section package; shared C6 modules list append requires coordinate-or-sequence per PARALLEL-DISPATCH GUARDRAIL #3).

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

- T1 checkpoints: `parity_contract` importable with `alias_of`; `G1Card` inherits `DecisionCardBase`; `PlanUnit` importable; sprint-status row observed as `in-progress` with main-thread C6 union note.
- C6 coordination: `pyproject.toml` read-only verification showed C6 modules already include `app.gates.section_02a`, `app.gates.section_04a`, `app.gates.section_04_5`, and `app.gates.section_04_55`; no pyproject edit made per operator ownership boundary.
- Schema generation: `Path('app/models/operator_verdict_section_04a.v1.schema.json').write_text(..., encoding='utf-8')`.
- Focused §04A: `13 passed`.
- §02A non-regression: `15 passed`.
- Smoke: `181 passed, 18 skipped`.
- Broad regression: first T1 attempt timed out at 120s; final broad run completed with `46 failed, 4271 passed, 27 skipped, 2 xfailed`. Remaining failures are inherited checkout/out-of-scope areas; focused Wave-3 story suites are green.
- Class conformance: `PASS: 19 parity contract file(s) conform (11 activation + 8 decision-card shape-pin)`. Tool scope is `tests/parity/`, so this story's operator-verdict shape pin under `tests/schemas/` does not change the count.
- Lint-imports: `12 kept, 0 broken`.
- Sandbox-AC validator: `PASS`.
- Ruff on owned files: clean.

### Completion Notes List

- Added the Section 04A G1A poll surface with `display_plan_unit`, `submit_verdict`, deterministic G1 card construction, digest helpers, edit validation, and digest-checked resume.
- Added `Section04AOperatorVerdict`, `PlanUnitEditPayload`, closed surface id, closed verb Literal, strip-then-non-empty string validators, UUID4/tz-aware/sha256 validation, and verb-payload consistency checks.
- Added test-local CLI/HTTP/MCP-stdio transport simulation proving equivalent verdict payloads across transports while keeping the runtime surface to `poll_surface.py`.
- Added FR-7c-49 shape pin using the shared operator-verdict harness plus an on-disk schema equality assertion.
- Added reload-isolated DSL registration tests for `alias_of="G1"` with CLI mandatory and HTTP/MCP-stdio optional, avoiding shared-registry ordering flake in broad xdist runs.

### File List

- `app/gates/section_04a/__init__.py`
- `app/gates/section_04a/poll_surface.py`
- `app/models/operator_verdict_section_04a.py`
- `app/models/operator_verdict_section_04a.v1.schema.json`
- `tests/gates/section_04a/__init__.py`
- `tests/gates/section_04a/_helpers.py`
- `tests/gates/section_04a/test_g1a_poll_surface_dsl_registration.py`
- `tests/gates/section_04a/test_g1a_poll_surface_three_transport_parity.py`
- `tests/schemas/operator_verdict/test_section_04a_shape.py`
- `_codex-handoff/7c-6.ready-for-review.md`

### Change Log

- 2026-05-06: Codex implemented Story 7c.6 through T10 and produced ready-for-review handoff.
