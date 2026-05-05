# Codex dev-story prompt — Story 7c.8 (§04.55 G1.5 Run-Constants Lock HIL Surface; single-gate; lite T11)

**Cycle:** Claude spec → Codex T1-T10 → drops `_codex-handoff/7c-8.ready-for-review.md` → Claude T11 lite → commit + flip done.
**Wave:** 3 — slot 3.
**Pre-authored:** 2026-05-05.
**Dispatch state:** **DISPATCH-READY post-V7-v1.1.**

**Parallel-dispatch context:** concurrent dispatch with 7c.6 + 7c.7 per V7 v1.1 elevated_cap=N+3.

---

```
Run bmad-dev-story on Story 7c.8 (Slab 7c Wave 3 slot 3; single-gate; lite T11).

Spec: `_bmad-output/implementation-artifacts/migration-7c-8-section-04-55-run-constants-lock.md`.

## Required reading (in order)

1. Story spec.
2. **`_bmad-output/implementation-artifacts/migration-7c-6-section-04a-g1a-per-plan-unit-ratification.md`** AND **its Codex prompt** (canonical Wave-3 sibling).
3. **`_bmad-output/implementation-artifacts/migration-7c-7-section-04-5-g1-5-estimator.md`** AND its prompt (sibling at G1.5 alias; same alias label).
4. `app/gates/section_02a/poll_surface.py` + `app/models/operator_verdict_section_02a.py` + `tests/schemas/operator_verdict/test_section_02a_shape.py` + `tests/gates/section_02a/*.py`.
5. `tests/schemas/operator_verdict/_harness.py` (7c.4b D3; READ-ONLY).
6. `app/models/decision_cards/g1.py`.
7. `app/parity/contracts/_decorator.py` + `_declaration.py`.
8. `docs/dev-guide/adr/0002-slab-7c-gate-taxonomy.md` (§04.55 surface uses G1.5 covered by G1).
9. `pyproject.toml::tool.importlinter::contracts::C6`.
10. `docs/dev-guide/specialist-anti-patterns.md::A18`.
11. Governance JSON `7c-8` + V7 v1.1.

## T1 hard checkpoints

- 7c.5.G1 + 7c.3b done.
- alias_of forward syntax in parity_contract.
- G1Card importable + inherits DecisionCardBase.
- Class-conformance + broad-regression baselines recorded.

## Files in scope

**New (7 files):**
- `app/gates/section_04_55/__init__.py`
- `app/gates/section_04_55/poll_surface.py`
- `app/models/operator_verdict_section_04_55.py`
- `app/models/operator_verdict_section_04_55.v1.schema.json` (regen via Path.write_text per A18)
- `tests/schemas/operator_verdict/test_section_04_55_shape.py`
- `tests/gates/section_04_55/__init__.py` + `_helpers.py` + `test_g1_5_run_constants_dsl_registration.py` + `test_g1_5_run_constants_two_transport_parity.py`

**Modified (1 file):** `pyproject.toml` C6 append `app.gates.section_04_55`. **Coordinate-or-sequence with 7c.6 + 7c.7.**

## Critical implementation notes

- **parity_contract registration:** `@parity_contract(surface_id="section_04_55_g1_5_run_constants", mandatory_transports=["cli", "http"], optional_transports=[], alias_of="G1")`. Per FR-7c-12: CLI + HTTP mandatory only; no MCP-stdio.
- **Closed verb Literal:** `Section04_55VerdictVerb = Literal["lock", "edit", "reject"]` per FR-7c-12 run-constants-lock framing.
- **JSON schema regen:** Path.write_text per A18:
  ```bash
  .venv/Scripts/python.exe -c "from pathlib import Path; from app.models.operator_verdict_section_04_55 import Section04_55OperatorVerdict; import json; Path('app/models/operator_verdict_section_04_55.v1.schema.json').write_text(json.dumps(Section04_55OperatorVerdict.model_json_schema(), indent=2, sort_keys=True), encoding='utf-8')"
  ```
- **Shape-pin via FR-7c-49 harness:** `transports=["cli", "http", "mcp-stdio"]` (schema-stability across all three even though FR-7c-12 only mandates CLI+HTTP).
- **2-transport parity test:** since MCP-stdio is not declared optional in FR-7c-12 (unlike 7c.7), the per-surface parity test asserts CLI + HTTP only (named `test_g1_5_run_constants_two_transport_parity.py`; mirror §02A's three-transport version with one transport stripped).
- **K-target 1.3× ≈ 520 LOC ceiling.**

## PARALLEL-DISPATCH GUARDRAILS (binding; same six rules)

(Identical to 7c.6 prompt.)

## Verification battery (T9)

```bash
.venv/Scripts/python.exe -m pytest tests/gates/section_04_55/ tests/schemas/operator_verdict/test_section_04_55_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest tests/gates/section_02a/ tests/schemas/operator_verdict/test_section_02a_shape.py -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest --smoke -p no:randomly -q --tb=short
.venv/Scripts/python.exe -m pytest -p no:randomly -q --tb=line
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/
.venv/Scripts/lint-imports.exe
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-7c-8-section-04-55-run-constants-lock.md
.venv/Scripts/python.exe -m ruff check app/gates/section_04_55/ app/models/operator_verdict_section_04_55.py tests/gates/section_04_55/ tests/schemas/operator_verdict/test_section_04_55_shape.py
```

## T10 + T11

T10: `_codex-handoff/7c-8.ready-for-review.md`. Same content shape as 7c.6/7c.7.

T11: Claude lite (~10-15 min). Lite-batchable.

## Boundary

(Identical to 7c.6 / 7c.7 except §04.55-specific paths.)
```

---

## Operator dispatch checklist

(Same as 7c.6 + 7c.7 with §04.55 adaptations.)

## Post-Codex-T10 dropbox-watch

Spawn 1 T11 lite review subagent. Concurrent with 7c.6 + 7c.7.
