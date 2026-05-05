# Migration Story 7c.7: §04.5 G1.5 Run-Budget Estimator HIL Surface (FR-7c-11)

**Status:** ready-for-dev *(spec authored 2026-05-05 lookahead_tier=1 author-ahead-aggressive; predecessors 7c.5.G1 + 7c.3b CLOSED. Wave-3 entry under V7 v1.1 elevated_cap=N+3.)*
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

- [ ] **T1 — Readiness checks** (mirror 7c.6 T1; predecessor reads + parity_contract decorator + ADR 0002 §2 G1.5-under-G1)
- [ ] **T2 — §section package + OperatorVerdict model**
  - [ ] T2.1 `app/gates/section_04_5/__init__.py` + `poll_surface.py`
  - [ ] T2.2 `app/models/operator_verdict_section_04_5.py`
- [ ] **T3 — JSON schema regen** via Path.write_text canonical command:
  ```bash
  .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_04_5 import Section04_5OperatorVerdict; import json; Path('app/models/operator_verdict_section_04_5.v1.schema.json').write_text(json.dumps(Section04_5OperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
  ```
- [ ] **T4 — Shape-pin + DSL-registration + 3-transport-parity tests**
- [ ] **T5 — C6 import-linter modules list append** (coordinate-or-sequence with concurrent stories per PARALLEL-DISPATCH GUARDRAIL #3)
- [ ] **T6 — Verification battery (R2)** — focused + §02A non-regression + smoke + R2 broad + class-conformance + lint-imports + sandbox-AC + ruff
- [ ] **T10 — Codex self-review dropbox** at `_codex-handoff/7c-7.ready-for-review.md`

---

## Required Readings (T1)

(Same as 7c.6 + 7c.6 spec/prompt as canonical Wave-3 reference once landed.)

## Sandbox-AC validator status

PASS (zero forbidden CLIs in dev-agent AC blocks).

## Dispatch state

DISPATCH-READY post-V7-v1.1-codification. Parallel-dispatchable with 7c.6 + 7c.8 per C6 path-disjointness + V7 v1.1 elevated_cap=3.
