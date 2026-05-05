# Migration Story 7c.8: §04.55 G1.5 Run-Constants Lock HIL Surface (FR-7c-12)

**Status:** ready-for-dev *(spec authored 2026-05-05 lookahead_tier=1 author-ahead-aggressive; predecessors 7c.5.G1 + 7c.3b CLOSED. Wave-3 entry under V7 v1.1 elevated_cap=N+3.)*
**Sprint key:** `migration-7c-8-section-04-55-run-constants-lock`
**Pts:** 2; **K-target:** 1.3×; **Estimated LOC:** ~400; **Gate-mode:** single-gate; **R-tier:** R2; **T11-tier:** lite; **Lookahead-tier:** 1.

**files_touched:** 7 new + 1 modified (C6 import-linter modules list append).

---

## Story

As the dev-agent,
I want the §04.55 G1.5 run-constants lock HIL surface authored as a NEW §section package mirroring the §02A canonical poll-surface pattern,
So that operators can lock run-constants via mandatory CLI + HTTP transports (per FR-7c-12; no MCP-stdio optional declared) emitting `Section04_55OperatorVerdict` with run-constants-lock verb, with three-transport schema-stability via FR-7c-49 shape-pin discipline.

---

## Predecessor / Dependency Context

- **7c.5.G1** + **7c.3b** CLOSED. Per ADR 0002 §2 / §4: §04.55 surface uses G1.5 (covered by G1 family contract). 7c.8 declares §04.55 G1.5's transport coverage via parity_contract with `alias_of="G1"`.
- **Sibling 7c.7 (§04.5 G1.5 estimator)** also aliases to G1.5; both surfaces operate on different runtime artifacts (estimator vs run-constants) but share G1 family contract via the `G1.5` alias label.

---

## Acceptance Criteria

### AC-7c.8-A — §section package + parity_contract registration (FR-7c-12)

`app/gates/section_04_55/poll_surface.py` with `@parity_contract(surface_id="section_04_55_g1_5_run_constants", mandatory_transports=["cli", "http"], optional_transports=[], alias_of="G1")`. Implements `display_run_constants(constants_or_path) → dict` + `submit_verdict(constants_id, verdict_payload, transport) → Section04_55OperatorVerdict`. Reuse `canonical_model_bytes` + `compute_model_digest` helpers per §02A canonical.

### AC-7c.8-B — OperatorVerdict variant + JSON schema regen (FR-7c-49)

`app/models/operator_verdict_section_04_55.py` with `Section04_55OperatorVerdict` (`surface_id: Literal["section_04_55_g1_5_run_constants"]` + `verb: Section04_55VerdictVerb` (closed `Literal["lock", "edit", "reject"]` per run-constants-lock framing) + `run_constants_id: str` strip-then-non-empty + standard envelope fields). `RunConstantsEditPayload` for `verb=edit`. JSON schema regenerated via Path.write_text canonical command per A18.

### AC-7c.8-C — Three-transport schema-stability shape-pin (FR-7c-49)

`tests/schemas/operator_verdict/test_section_04_55_shape.py` using FR-7c-49 harness with `transports=["cli", "http", "mcp-stdio"]` (schema-stability checked across all three even though FR-7c-12 only mandates CLI+HTTP).

### AC-7c.8-D — DSL-registration audit + transport-parity test

`tests/gates/section_04_55/test_g1_5_run_constants_dsl_registration.py` + `tests/gates/section_04_55/test_g1_5_run_constants_two_transport_parity.py` (CLI+HTTP since FR-7c-12 declares no MCP-stdio).

### AC-7c.8-E — C6 import-linter modules list append (binding=hard)

`pyproject.toml::tool.importlinter::contracts::C6::modules` appends `app.gates.section_04_55`. PARALLEL-DISPATCH GUARDRAIL #3: coordinate-or-sequence with 7c.6 + 7c.7 if concurrent dispatch.

---

## Tasks / Subtasks (compact; mirror 7c.6 structure)

- [ ] **T1 — Readiness checks** (mirror 7c.6 T1)
- [ ] **T2 — §section package + OperatorVerdict model**
- [ ] **T3 — JSON schema regen** via Path.write_text canonical command:
  ```bash
  .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_04_55 import Section04_55OperatorVerdict; import json; Path('app/models/operator_verdict_section_04_55.v1.schema.json').write_text(json.dumps(Section04_55OperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
  ```
- [ ] **T4 — Shape-pin + DSL-registration + 2-transport-parity tests**
- [ ] **T5 — C6 import-linter modules list append**
- [ ] **T6 — Verification battery (R2)**
- [ ] **T10 — Codex self-review dropbox** at `_codex-handoff/7c-8.ready-for-review.md`

---

## Required Readings (T1)

(Same as 7c.6 + 7c.7.)

## Sandbox-AC validator status

PASS.

## Dispatch state

DISPATCH-READY post-V7-v1.1-codification. Parallel-dispatchable with 7c.6 + 7c.7.
