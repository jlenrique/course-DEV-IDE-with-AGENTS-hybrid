# Migration Story 7c.7: §04.5 G1.5 Run-Budget Estimator HIL Surface (FR-7c-11)

**Status:** done *(spec authored 2026-05-05 lookahead_tier=1 author-ahead-aggressive; predecessors 7c.5.G1 + 7c.3b CLOSED. Wave-3 entry under V7 v1.1 elevated_cap=N+3. Closed 2026-05-05 via T11 lite PASS-zero-patches verdict at `7c-7-code-review-2026-05-05.md`. Cross-Wave SHOULD-FIX-DEFERRED: digest-helper extraction filed in deferred-inventory.)*
**Sprint key:** `migration-7c-7-section-04-5-g1-5-estimator`
**Pts:** 2; **K-target:** 1.3×; **Estimated LOC:** ~400; **Gate-mode:** single-gate; **R-tier:** R2; **T11-tier:** lite; **Lookahead-tier:** 1.

**files_touched:** 7 new + 1 modified (C6 import-linter modules list append).

---

## Story

As the dev-agent,
I want the §04.5 G1.5 run-budget estimator HIL surface authored as a NEW §section package mirroring the §02A canonical poll-surface pattern,
So that operators can review and lock the run-budget estimator via mandatory CLI + HTTP transports (MCP-stdio optional per FR-7c-11) emitting `Section04_5OperatorVerdict` with cost-impact-acknowledged verb, with three-transport schema-stability via FR-7c-49 shape-pin discipline.

---

## Predecessor / Dependency Context

- **7c.5.G1** + **7c.3b** CLOSED. G1.5 aliases to G1 per ADR 0002 §2 / §4 ("`G1.5` is covered by the `G1` family contract"). 7c.7 declares §04.5 G1.5's transport coverage via parity_contract decorator with `alias_of="G1"`.
- **§02A canonical poll-surface pattern:** `app/gates/section_02a/poll_surface.py`. Pattern-replicate with `mandatory_transports=["cli", "http"]` (FR-7c-11) instead of all-three.

---

## Acceptance Criteria

### AC-7c.7-A — §section package + parity_contract registration (FR-7c-11)

`app/gates/section_04_5/poll_surface.py` with `@parity_contract(surface_id="section_04_5_g1_5_estimator", mandatory_transports=["cli", "http"], optional_transports=["mcp-stdio"], alias_of="G1")`. Implements `display_estimator(estimator_or_path) → dict` + `submit_verdict(estimator_id, verdict_payload, transport) → Section04_5OperatorVerdict`. Reuse `canonical_model_bytes` + `compute_model_digest` helpers per §02A canonical.

### AC-7c.7-B — OperatorVerdict variant + JSON schema regen (FR-7c-49)

`app/models/operator_verdict_section_04_5.py` with `Section04_5OperatorVerdict` (`surface_id: Literal["section_04_5_g1_5_estimator"]` + `verb: Section04_5VerdictVerb` (closed `Literal["acknowledged", "edit", "reject"]` per cost-impact-acknowledged framing) + `estimator_id: str` strip-then-non-empty + standard envelope fields). `EstimatorEditPayload` for `verb=edit`. JSON schema regenerated via Path.write_text canonical command per A18.

### AC-7c.7-C — Three-transport schema-stability shape-pin (FR-7c-49)

`tests/schemas/operator_verdict/test_section_04_5_shape.py` using FR-7c-49 harness with `transports=["cli", "http", "mcp-stdio"]` (schema-stability checked across all three even though only CLI+HTTP are mandatory; MCP-stdio is optional but its schema must remain stable if the surface adds it later).

### AC-7c.7-D — DSL-registration audit + 3-transport-parity test

`tests/gates/section_04_5/test_g1_5_estimator_dsl_registration.py` + `tests/gates/section_04_5/test_g1_5_estimator_three_transport_parity.py` mirror §02A.

### AC-7c.7-E — C6 import-linter modules list append (binding=hard)

`pyproject.toml::tool.importlinter::contracts::C6::modules` appends `app.gates.section_04_5`. **PARALLEL-DISPATCH GUARDRAIL #3:** coordinate-or-sequence with 7c.6 + 7c.8 if concurrent dispatch.

---

## Tasks / Subtasks (compact; mirror 7c.6 structure)

- [x] **T1 — Readiness checks** (mirror 7c.6 T1; predecessor reads + parity_contract decorator + ADR 0002 §2 G1.5-under-G1)
- [x] **T2 — §section package + OperatorVerdict model**
  - [x] T2.1 `app/gates/section_04_5/__init__.py` + `poll_surface.py`
  - [x] T2.2 `app/models/operator_verdict_section_04_5.py`
- [x] **T3 — JSON schema regen** via Path.write_text canonical command:
  ```bash
  .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_04_5 import Section04_5OperatorVerdict; import json; Path('app/models/operator_verdict_section_04_5.v1.schema.json').write_text(json.dumps(Section04_5OperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
  ```
- [x] **T4 — Shape-pin + DSL-registration + 3-transport-parity tests**
- [x] **T5 — C6 import-linter modules list append** (coordinate-or-sequence with concurrent stories per PARALLEL-DISPATCH GUARDRAIL #3)
- [x] **T6 — Verification battery (R2)** — focused + §02A non-regression + smoke + R2 broad + class-conformance + lint-imports + sandbox-AC + ruff
- [x] **T10 — Codex self-review dropbox** at `_codex-handoff/7c-7.ready-for-review.md`

---

## Required Readings (T1)

(Same as 7c.6 + 7c.6 spec/prompt as canonical Wave-3 reference once landed.)

## Sandbox-AC validator status

PASS (zero forbidden CLIs in dev-agent AC blocks).

## Dispatch state

DISPATCH-READY post-V7-v1.1-codification. Parallel-dispatchable with 7c.6 + 7c.8 per C6 path-disjointness + V7 v1.1 elevated_cap=3.

---

## Dev Agent Record

### Debug Log

- T1 read story prompt/spec, 7c.6 prompt/spec, Section 02A canonical poll-surface/model/tests, FR-7c-49 harness, G1Card, parity_contract alias support, ADR 0002, A18, governance JSON, and C6 state.
- T1 baseline: `validate_parity_test_class_conformance.py tests/parity/` PASS with 19 parity contract files. Initial smoke attempt was red due concurrent `section_04_55` tests importing not-yet-present modules; later smoke passed after concurrent 7c.8 files landed.
- C6 coordination: `pyproject.toml` already contained the coordinated union including `app.gates.section_04_5`; this story did not edit `pyproject.toml`.
- Import-linter caught an initial cross-surface import from Section 04.5 to Section 02A helpers. Fixed by re-emitting identical `canonical_model_bytes` and `compute_model_digest` helpers locally, preserving C6 independence.

### Completion Notes

- Implemented Section 04.5 G1.5 estimator surface with `alias_of="G1"`, mandatory CLI+HTTP transports, optional MCP-stdio, display/submit/resume helpers, UTF-8 JSON/YAML estimator loading, and transport-neutral digest helpers.
- Added `Section04_5OperatorVerdict`, closed `Section04_5VerdictVerb = Literal["acknowledged", "edit", "reject"]`, `EstimatorEditPayload`, strip-then-non-empty estimator/operator identifiers, standard envelope fields, and verb/payload consistency validation.
- Regenerated `app/models/operator_verdict_section_04_5.v1.schema.json` using the required `Path.write_text(..., encoding='utf-8')` command.
- Added Section 04.5 focused shape-pin, DSL-registration, YAML load, tamper-digest, estimator-id mismatch, and three-transport parity coverage.

### Verification Evidence

- PASS: `.venv/Scripts/python.exe -m pytest tests/gates/section_04_5/ tests/schemas/operator_verdict/test_section_04_5_shape.py -p no:randomly -q --tb=short` -> 13 passed.
- PASS: `.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short` -> 15 passed.
- PASS: `.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short` -> 181 passed, 18 skipped.
- PASS: `.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/` -> 19 parity contract files conform.
- PASS: `.venv/Scripts/lint-imports.exe` -> 12 kept, 0 broken.
- PASS: `.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-7-section-04-5-g1-5-estimator.md` -> no sandbox-AC violations.
- PASS: `.venv/Scripts/python.exe -m ruff check app/gates/section_04_5/ app/models/operator_verdict_section_04_5.py tests/gates/section_04_5/ tests/schemas/operator_verdict/test_section_04_5_shape.py` -> all checks passed.
- BROAD BASELINE NOTE: `.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line` remains red with 46 failed, 4271 passed, 27 skipped, 2 xfailed. Failures are inherited checkout/out-of-scope and environment-sensitive issues; focused 7c.7, Section 02A non-regression, smoke, import-linter, sandbox, class-conformance, and Ruff are green.

### File List

- `app/gates/section_04_5/__init__.py`
- `app/gates/section_04_5/poll_surface.py`
- `app/models/operator_verdict_section_04_5.py`
- `app/models/operator_verdict_section_04_5.v1.schema.json`
- `tests/gates/section_04_5/__init__.py`
- `tests/gates/section_04_5/_helpers.py`
- `tests/gates/section_04_5/test_g1_5_estimator_dsl_registration.py`
- `tests/gates/section_04_5/test_g1_5_estimator_three_transport_parity.py`
- `tests/schemas/operator_verdict/test_section_04_5_shape.py`
- `_bmad-output/implementation-artifacts/migration-7c-7-section-04-5-g1-5-estimator.md`
- `_codex-handoff/7c-7.ready-for-review.md`

### Change Log

- 2026-05-06: Implemented Story 7c.7 Section 04.5 G1.5 run-budget estimator HIL surface and review handoff.
