# 7b.6 Codex Self-Review - Gary Port-Shape

Date: 2026-04-29
Story: `migration-7b-6-gary-port-shape`
Status: ready for Claude bmad-code-review

## Scope Check

- Implemented Gary Class-C API-bound act body in `app/specialists/gary/_act.py`.
- Preserved `app/specialists/gary/gamma_dispatch.py` as legacy helper and retained old graph monkeypatch compatibility.
- Created canonical six-file Gary BMB sanctum at `_bmad/memory/bmad-agent-gary/`.
- Created missing canonical persona skill at `skills/bmad-agent-gary/SKILL.md`; `skills/bmad-agent-gamma/` was not modified.
- Extended parity validator with additive Class-C assertions; Class-A, Class-B, and Class-C+ conformance still pass.
- Added credential rotation register and Gary rate-limit budget.
- Added Composition Spec Section 10 decision-log row for Class-C six-file BMB pattern.

## Guardrails

- AC-B body ceiling: `act()` body is 37 LOC, below the 150 LOC ceiling.
- NFR-CG13: `detect_live_api_in_tests.py` passes; Gary tests use fake clients and fixture cassettes only.
- Substrate-as-floor: `git diff -- app/marcus/orchestrator/dispatch_adapter.py` is empty.
- No edits to `skills/bmad-agent-gamma/` or `skills/gamma-api-mastery/`.

## Verification

- Focused Gary battery: `64 passed`.
- `validate_parity_test_class_conformance.py tests/parity/`: PASS, 6 activation contracts.
- `check_pipeline_manifest_lockstep.py`: PASS.
- `validate_migration_story_sandbox_acs.py migration-7b-6...`: PASS.
- Story-scoped `ruff check`: PASS.
- `lint-imports.exe`: 9/9 contracts kept.
- Broad regression: `1284 passed, 21 skipped, 1 deselected, 2 failed`.

## Residuals

- Broad regression residual 1: `tests/specialists/wanda/test_wanda_sanctum_populated.py::test_sanctum_digest_nonempty_post_population` remains the known Wanda sanctum drift noted in the 7b.5 baseline.
- Broad regression residual 2: `tests/specialists/desmond/test_desmond_act_node_authoring.py::test_desmond_act_live_llm_smoke` failed on live LLM output missing the mandatory Automation Advisory section. This is outside Gary scope and not caused by the Gary changes.
- Operator-gated live Gamma canary was not run in this dev-agent session; AC-6-B remains T13/operator-gated.
