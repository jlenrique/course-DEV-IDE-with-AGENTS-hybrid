# Codex dev-story prompt — Story 7c.7 (§04.5 G1.5 Run-Budget Estimator HIL Surface; single-gate; lite T11)

**Cycle:** Claude spec → Codex T1-T10 → drops `_codex-handoff/7c-7.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 3 — slot 2.
**Pre-authored:** 2026-05-05.
**Dispatch state:** **DISPATCH-READY post-V7-v1.1.**

**Parallel-dispatch context:** intended for concurrent dispatch with 7c.6 + 7c.8 per V7 v1.1 elevated_cap=N+3.

---

```
Run bmad-dev-story on Story 7c.7 (Slab 7c Wave 3 slot 2; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-7-section-04-5-g1-5-estimator.md`.

## Required reading (in order)

1. Story spec.
2. **`_bmad-output/implementation-artifacts/migration-7c-6-section-04a-g1a-per-plan-unit-ratification.md`** AND **its Codex prompt** (canonical Wave-3 sibling; pattern reference).
3. `app/gates/section_02a/poll_surface.py` + `app/models/operator_verdict_section_02a.py` + `tests/schemas/operator_verdict/test_section_02a_shape.py` + `tests/gates/section_02a/*.py` (canonical pattern).
4. `tests/schemas/operator_verdict/_harness.py` (7c.4b D3; FR-7c-49 harness; READ-ONLY).
5. `app/models/decision_cards/g1.py` (POST-7c.5.G1-migration).
6. `app/parity/contracts/_decorator.py` + `_declaration.py` (parity_contract + alias_of).
7. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (G1.5 covered by G1 family per §2 / §4).
8. `pyproject.toml::tool.importlinter::contracts::C6` (modules list).
9. `docs/dev-guide/specialist-anti-patterns.md::A18`.
10. Governance JSON `7c-7` + `wave_3_lookahead_policy::current_cap=3` (V7 v1.1).

## T1 hard checkpoints

- 7c.5.G1 + 7c.3b done.
- alias_of forward syntax in parity_contract.
- G1Card importable + inherits DecisionCardBase.
- Class-conformance baseline: record observed.
- Broad-regression baseline: re-run.

## Files in scope

**New (7 files):**
- `app/gates/section_04_5/__init__.py` (empty namespace)
- `app/gates/section_04_5/poll_surface.py` (~120 LOC; mirror §02A)
- `app/models/operator_verdict_section_04_5.py` (~50 LOC; Section04_5OperatorVerdict + EstimatorEditPayload + Section04_5VerdictVerb + SECTION_04_5_SURFACE_ID)
- `app/models/operator_verdict_section_04_5.v1.schema.json` (regen via Path.write_text per A18)
- `tests/schemas/operator_verdict/test_section_04_5_shape.py`
- `tests/gates/section_04_5/__init__.py` + `_helpers.py` + `test_g1_5_estimator_dsl_registration.py` + `test_g1_5_estimator_three_transport_parity.py`

**Modified (1 file):** `pyproject.toml` C6 modules append `app.gates.section_04_5`. **Coordinate-or-sequence with 7c.6 + 7c.8 if concurrent.**

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_04_5_g1_5_estimator", mandatory_transports=["cli", "http"], optional_transports=["mcp-stdio"], alias_of="G1")`. Per FR-7c-11: CLI + HTTP mandatory; MCP-stdio optional.
- **Closed verb Literal:** `Section04_5VerdictVerb = Literal["acknowledged", "edit", "reject"]` per FR-7c-11 cost-impact-acknowledged framing.
- **JSON schema regen:** Path.write_text per A18:
  ```bash
  .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_04_5 import Section04_5OperatorVerdict; import json; Path('app/models/operator_verdict_section_04_5.v1.schema.json').write_text(json.dumps(Section04_5OperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
  ```
- **Shape-pin via FR-7c-49 harness:** `transports=["cli", "http", "mcp-stdio"]` (schema-stability across all three even though MCP-stdio is optional).
- **K-target 1.3× ≈ 520 LOC ceiling.**
- **T11 lite tier:** mirror 7c.6 eligibility checks.

## PARALLEL-DISPATCH GUARDRAILS (binding; same six rules)

(Identical to 7c.6 prompt; #3 specifically applies to pyproject.toml C6 modules list under concurrent dispatch with 7c.6+7c.8.)

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_04_5/ tests/schemas/operator_verdict/test_section_04_5_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-7-section-04-5-g1-5-estimator.md
.venv/Scripts/python.exe -m ruff check app/gates/section_04_5/ app/models/operator_verdict_section_04_5.py tests/gates/section_04_5/ tests/schemas/operator_verdict/test_section_04_5_shape.py
```

## T10 + T11

T10: dropbox at `_codex-handoff/7c-7.ready-for-review.md`. Same content as 7c.6 T10 with §04.5-specific evidence.

T11: Claude lite (~10-15 min). Lite-batchable with 7c.6+7c.8 reviews if path-disjoint.

## Boundary

(Identical to 7c.6 except §04.5-specific paths.)
```

---

## Operator dispatch checklist

(Same as 7c.6 with §04.5 adaptations.)

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent. Concurrent with 7c.6 + 7c.8 if all three land same window.
