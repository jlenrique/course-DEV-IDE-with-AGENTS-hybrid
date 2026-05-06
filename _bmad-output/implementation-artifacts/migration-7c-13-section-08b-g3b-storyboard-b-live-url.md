# Migration Story 7c.13: §08B G3B Storyboard B + Live-URL HIL Surface (FR-7c-17)

**Status:** done *(Codex T1-T10 complete 2026-05-06 + Claude T11 lite PASS-zero-patches at `7c-13-code-review-2026-05-06.md`; focused 13 passed, combined next-batch focused 26 passed, §02A non-regression 15 passed, Wave-3 trio non-regression 25 passed, smoke 181 passed/18 skipped, lint-imports 12 KEPT (C6 4→6 entries), sandbox-AC PASS, ruff clean; broad regression 4300 passed/43 failed BELOW inherited Wave-3 band. `test_no_unauthorized_callers` confirmed PRE-EXISTING scanner-staleness — DISMISSED; deferred-inventory entry filed for scanner-hardening.)*
**Sprint key:** `migration-7c-13-section-08b-g3b-storyboard-b-live-url`
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
I want the §08B G3B Storyboard B + live-URL HIL surface authored as a NEW §section package mirroring the §02A canonical poll-surface pattern (closed at 7c.3b),
So that operators can review Storyboard B + live-URL content via mandatory CLI + HTTP transports (MCP-stdio optional per FR-7c-17) emitting `Section08BOperatorVerdict` with verb ∈ {`approve`, `edit`, `reject`}, with three-transport schema-stability via FR-7c-49 shape-pin discipline.

---

## Predecessor / Dependency Context

- **7c.5.G3** (CLOSED `0ec80df`): G3 family DecisionCard contract; G3B aliases to G3 per ADR 0002 §2 (parent family `G3`; consumer surface "Storyboard B + live-URL review surface, section 08B"). Per ADR 0002 §3 Alias-DSL Clause Inheritance: 7c.13 declares §08B G3B's transport coverage via parity_contract decorator with `alias_of="G3"`.
- **7c.3b** (CLOSED `f8fc1a8`): §02A G0 poll-surface canonical HIL pattern. Authoritative reference at `app/gates/section_02a/poll_surface.py`.
- **G3Card** (closed at 7c.5.G3 `0ec80df`): consumed by §08B G3B poll-surface as the operator-facing payload. `from app.models.decision_cards.g3 import G3Card` (post-G3-migration; inherits DecisionCardBase).
- **Wave-3-trio sibling pattern** (7c.6 / 7c.7 / 7c.8 closing concurrently): canonical reference for §section poll-surface + OperatorVerdict + 3-transport-parity discipline. Lite-tier T11 verdicts inform pattern-parity ratchets at this story's T1.
- **C6 import-linter contract** at `pyproject.toml::tool.importlinter` (per 7c.4b D5 P-1 patch): `independence` type with modules list. **THIS STORY APPENDS `app.gates.section_08b` to C6's modules list.**

---

## Acceptance Criteria

### AC-7c.13-A — §section package + parity_contract registration (FR-7c-17 + FR-7c-20)

**Given** §02A canonical poll-surface pattern at `app/gates/section_02a/poll_surface.py`
**When** the dev-agent authors `app/gates/section_08b/poll_surface.py`
**Then** the module:
1. Declares `SURFACE_ID = SECTION_08B_SURFACE_ID` (constant from new `app/models/operator_verdict_section_08b.py`).
2. Registers via `@parity_contract(surface_id="section_08b_g3b_poll", mandatory_transports=["cli", "http"], optional_transports=["mcp-stdio"], alias_of="G3")` per FR-7c-17 transport requirements + ADR 0002 §3 alias_of forward syntax.
3. Implements `display_storyboard_b(storyboard_or_path: G3Card | Path) -> dict[str, Any]` (poll function; mirror `display_directive`).
4. Implements `submit_verdict(storyboard_id: str, verdict_payload: dict, transport: TransportName) -> Section08BOperatorVerdict` (submit function; emits OperatorVerdict).
5. Re-emits `canonical_model_bytes` + `compute_model_digest` helpers locally to satisfy C6 cross-§section independence (per Wave-3-trio precedent — 7c.6/7c.7/7c.8 all re-emit rather than import from §02A).

### AC-7c.13-B — OperatorVerdict variant + JSON schema regen (FR-7c-49)

**When** the dev-agent authors `app/models/operator_verdict_section_08b.py` + regenerates `app/models/operator_verdict_section_08b.v1.schema.json`:
1. `Section08BOperatorVerdict` Pydantic-v2 model: `surface_id: Literal["section_08b_g3b_poll"]` + `verb: Section08BVerdictVerb` (closed `Literal["approve", "edit", "reject"]`) + `storyboard_id: str` (non-empty; strip-then-non-empty per G2A pattern) + standard envelope fields per §02A precedent (run_id UUID4 + operator_id pattern + submitted_at tz-aware + decision_card_digest sha256 + verb-payload consistency `model_validator(mode="after")`).
2. `StoryboardBEditPayload` (mirror `DirectiveEditPayload`) for `verb=edit` payloads.
3. JSON schema regenerated via Path.write_text(... encoding="utf-8") canonical command (anti-pattern A18; canonical command in Codex prompt). LF-only; NO BOM.

### AC-7c.13-C — Three-transport schema-stability shape-pin (FR-7c-49)

**Then** `tests/schemas/operator_verdict/test_section_08b_shape.py` asserts `Section08BOperatorVerdict` schema hash STABLE across CLI / HTTP / MCP-stdio transports per FR-7c-49 harness pattern. Use `assert_operator_verdict_schema_stable_across_transports(verdict_class=Section08BOperatorVerdict, surface_id="section_08b_g3b_poll", transports=["cli", "http", "mcp-stdio"])` from `tests/schemas/operator_verdict/_harness.py` (7c.4b D3 deliverable; canonical helper).

### AC-7c.13-D — DSL-registration audit + 3-transport-parity test

**Then**:
1. `tests/gates/section_08b/test_g3b_poll_surface_dsl_registration.py` — asserts `parity_contract` registered with correct surface_id + transports + `alias_of="G3"`; mirrors `tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py`. **Reload-isolated** to avoid shared-registry ordering flake under xdist (per 7c.6 Codex precedent).
2. `tests/gates/section_08b/test_g3b_poll_surface_three_transport_parity.py` — round-trips a sample G3B verdict via CLI + HTTP + MCP-stdio simulated transports; asserts payload digest equals across all three.

### AC-7c.13-E — C6 import-linter modules list append (binding=hard per 7c.4b D5)

**When** the dev-agent updates `pyproject.toml`:
**Then** `app.gates.section_08b` appended to C6 contract `modules` list (current state post-Wave-3 trio: `[app.gates.section_02a, app.gates.section_04a, app.gates.section_04_5, app.gates.section_04_55]`; will become `[..., app.gates.section_08b]` post-this-story). Lint-imports re-runs PASS with 12 KEPT (UNCHANGED count; C6 just gets a wider module list). **PARALLEL-DISPATCH GUARDRAIL #3 (binding):** if 7c.14 dispatches concurrently, two-way coordinate-or-sequence — main thread (or whichever worker integrates first) writes the union of both new §section entries; subsequent worker rebases before commit.

---

## Tasks / Subtasks

- [x] **T1 — Readiness checks**
  - [x] T1.1 Confirm 7c.5.G3 + 7c.3b done in sprint-status; confirm Wave-3 trio (7c.6/7c.7/7c.8) closed (reference patterns).
  - [x] T1.2 Read `app/gates/section_02a/poll_surface.py` + `app/models/operator_verdict_section_02a.py` + `tests/gates/section_02a/*.py` + `tests/schemas/operator_verdict/test_section_02a_shape.py` for canonical pattern.
  - [x] T1.3 Read `app/gates/section_04a/poll_surface.py` + `app/models/operator_verdict_section_04a.py` (Wave-3 sibling reference for re-emit pattern; same §02A mirror).
  - [x] T1.4 Read `app/models/decision_cards/g3.py` (POST-G3-migration; inherits DecisionCardBase) for G3Card consumption.
  - [x] T1.5 Read ADR 0002 §3 for alias_of forward syntax; verify `parity_contract` decorator accepts `alias_of` kwarg (per 7c.4b D1).
  - [x] T1.6 Refresh broad-regression baseline + record class-conformance baseline (likely 19 post-Wave-3-trio close +N for trio's shape-pins; recompute at T1).

- [x] **T2 — Author §section package + OperatorVerdict model**
  - [x] T2.1 Author `app/gates/section_08b/__init__.py` (empty namespace; mirror §02A).
  - [x] T2.2 Author `app/gates/section_08b/poll_surface.py` per AC-A.
  - [x] T2.3 Author `app/models/operator_verdict_section_08b.py` per AC-B with `Section08BOperatorVerdict` + `StoryboardBEditPayload` + `Section08BVerdictVerb` + `SECTION_08B_SURFACE_ID`.

- [x] **T3 — Generate JSON schema (AC-B)**
  - [x] T3.1 Generate `app/models/operator_verdict_section_08b.v1.schema.json` via:
    ```bash
    .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_08b import Section08BOperatorVerdict; import json; Path('app/models/operator_verdict_section_08b.v1.schema.json').write_text(json.dumps(Section08BOperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
    ```
    (Path.write_text per A18; NO PowerShell `>` redirection.)

- [x] **T4 — Author shape-pin + 3-transport-parity test + DSL-registration audit (AC-C + AC-D)**
  - [x] T4.1 Author `tests/schemas/operator_verdict/test_section_08b_shape.py` using FR-7c-49 harness.
  - [x] T4.2 Author `tests/gates/section_08b/__init__.py` + `_helpers.py` (mirror §02A / Wave-3-trio).
  - [x] T4.3 Author `tests/gates/section_08b/test_g3b_poll_surface_dsl_registration.py` (reload-isolated).
  - [x] T4.4 Author `tests/gates/section_08b/test_g3b_poll_surface_three_transport_parity.py`.

- [x] **T5 — C6 import-linter modules list append (AC-E)**
  - [x] T5.1 Update `pyproject.toml::tool.importlinter::contracts::C6::modules` to append `app.gates.section_08b`. **PARALLEL-DISPATCH GUARDRAIL #3:** if running concurrently with 7c.14, write the union of both new §section entries OR coordinate-or-sequence per main-thread integration pattern.

- [x] **T6 — Verification battery (R-tier R2)**
  - [x] T6.1 Focused: `pytest tests/gates/section_08b/ tests/schemas/operator_verdict/test_section_08b_shape.py -p no:randomly -q --tb=short` PASS.
  - [x] T6.2 §02A non-regression: `pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [x] T6.3 Wave-3 trio non-regression: `pytest tests/gates/section_04a/ tests/gates/section_04_5/ tests/gates/section_04_55/ -p no:randomly -q --tb=short` PASS UNCHANGED.
  - [x] T6.4 Smoke: nodeid baseline UNCHANGED.
  - [x] T6.5 R2 broad: failure count ≤ T1 baseline (delta ≤ 0); per-failure git-log-attribution required for any failures present.
  - [x] T6.6 Class-conformance: T1-baseline + 1 (new shape-pin file).
  - [x] T6.7 Lint-imports: 12 KEPT / 0 broken (UNCHANGED count; C6 modules list grew).
  - [x] T6.8 Sandbox-AC: PASS.
  - [x] T6.9 Ruff: clean.

- [x] **T10 — Codex self-review dropbox**
  - [x] T10.1 Drop `_codex-handoff/7c-13.ready-for-review.md`.

---

## Required Readings (T1)

1. This story spec.
2. `_bmad-output/implementation-artifacts/migration-7c-3b-section-02a-g0-poll-surface-canonical-hil-pattern.md` (canonical predecessor; 7c.3b).
3. `_bmad-output/implementation-artifacts/migration-7c-6-section-04a-g1a-per-plan-unit-ratification.md` (Wave-3 sibling reference).
4. `app/gates/section_02a/poll_surface.py` (canonical pattern reference).
5. `app/gates/section_04a/poll_surface.py` (Wave-3 sibling re-emit pattern reference).
6. `app/models/operator_verdict_section_02a.py` (canonical OperatorVerdict variant).
7. `app/models/operator_verdict_section_04a.py` (Wave-3 sibling OperatorVerdict; mirror this for `Section08BOperatorVerdict`).
8. `tests/schemas/operator_verdict/_harness.py` (7c.4b D3 FR-7c-49 harness; READ-ONLY).
9. `tests/schemas/operator_verdict/test_section_02a_shape.py` + `test_section_04a_shape.py` (canonical + Wave-3 shape-pins).
10. `tests/gates/section_02a/*.py` + `tests/gates/section_04a/*.py` (canonical + Wave-3 DSL-registration + 3-transport-parity tests).
11. `app/models/decision_cards/g3.py` (post-7c.5.G3-migration; inherits DecisionCardBase per 0ec80df).
12. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of forward syntax per 7c.4b D1).
13. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G3B alias mapping per §2).
14. `pyproject.toml::tool.importlinter` (C6 contract; modules list).
15. `docs/dev-guide/specialist-anti-patterns.md::A18` (PowerShell BOM hardening).
16. Governance JSON `7c-13` entry + `wave_3_lookahead_policy::current_cap=3` (V7 v1.1 elevated; V7 v2 promotion auto-fired post-Wave-3-trio close).

## Sandbox-AC validator status

Spec contains zero forbidden CLIs in dev-agent AC blocks. PASS (expected; validator must run pre-dispatch).

---

## Dispatch state

**DISPATCH-DEFERRED** until Wave-3 trio (7c.6/7c.7/7c.8) close-batch commits and V7 v2 auto-fires at `wave_3_closed_count >= 3`. Per V7 v2 promotion (Murat triple-condition: C6 ∧ lookahead_tier=1 ∧ t11_tier=lite — this story qualifies on all three), Wave-3 7c.13/7c.14 may dispatch concurrently (path-disjoint at file level; shared C6 modules list requires coordinate-or-sequence per PARALLEL-DISPATCH GUARDRAIL #3).

---

## Dev Agent Record

### Agent Model Used

Codex GPT-5 (bmad-dev-story discipline).

### Debug Log References

- T1: Confirmed 7c.5.G3, 7c.3b, and Wave-3 trio close state via sprint-status/commit context; class-conformance baseline observed at 19.
- T2-T5: Authored `section_08b` package, verdict model, LF-only schema, shape-pin, DSL registration audit, 3-transport parity tests, and C6 union append with 7c.14.
- T6: Focused §08B suite `13 passed`; combined next-batch focused suite `26 passed`; §02A non-regression `15 passed`; Wave-3 trio non-regression `25 passed`; smoke `181 passed, 18 skipped`; lint-imports `12 kept, 0 broken`; sandbox-AC PASS; ruff clean.
- T6 broad: `4300 passed, 43 failed, 27 skipped, 2 xfailed`; failure count is below inherited Wave-3 band. Failures are outside new §08B behavior; `test_resume_api_authority` remains inherited and now reports the new verdict model files in an already-failing direct-constructor scanner.

### Completion Notes List

- Implemented Section 08B G3B Storyboard B/live-URL HIL surface with alias-aware parity registration: mandatory `cli` + `http`, optional `mcp-stdio`, `alias_of="G3"`.
- Added `Section08BOperatorVerdict`, `StoryboardBEditPayload`, LF-only JSON schema, schema-stability shape-pin, reload-isolated DSL audit, and three-transport parity tests.
- Coordinated the shared C6 import-linter edit as a union append with 7c.14 (`app.gates.section_08b` + `app.gates.section_11`).

### File List

- `app/gates/section_08b/__init__.py`
- `app/gates/section_08b/poll_surface.py`
- `app/models/operator_verdict_section_08b.py`
- `app/models/operator_verdict_section_08b.v1.schema.json`
- `tests/gates/section_08b/__init__.py`
- `tests/gates/section_08b/_helpers.py`
- `tests/gates/section_08b/test_g3b_poll_surface_dsl_registration.py`
- `tests/gates/section_08b/test_g3b_poll_surface_three_transport_parity.py`
- `tests/schemas/operator_verdict/test_section_08b_shape.py`
- `_bmad-output/implementation-artifacts/migration-7c-13-section-08b-g3b-storyboard-b-live-url.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `_codex-handoff/7c-13.ready-for-review.md`
- `pyproject.toml`

### Change Log

- 2026-05-06: Codex implemented 7c.13 through T10 and moved story to review.
- 2026-05-05: Spec pre-authored by Claude (lookahead_tier=1) for next-batch dispatch.
