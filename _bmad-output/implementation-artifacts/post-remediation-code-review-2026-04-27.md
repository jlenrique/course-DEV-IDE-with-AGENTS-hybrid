# Post-Remediation Code Review — 2026-04-27

## Scope

Review mode: `full` bmad-code-review over post-remediation working tree.

Diff base: `24c4899 feat(5a.5): close M5 as conditional ship`.

Spec inputs:

- Codex dispatch: post-remediation batch B3/B5/B7/B-extra/B-cr.
- `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- `_bmad-output/upstream-state.md`.
- `_bmad-output/implementation-artifacts/m5-decision.md`.
- `docs/dev-guide/specialist-anti-patterns.md` anti-pattern A15.

Review layers:

- Blind Hunter.
- Edge Case Hunter.
- Acceptance Auditor.

## Verification

- `pytest tests/test_no_fictitious_model_ids.py tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py tests/integration/runtime/test_cascade_config_loading.py tests/test_live_smoke_snapshot_allowlist.py tests/integration/marcus/test_trial_cli.py tests/integration/runtime/test_measure_trial_cost.py tests/integration/runtime/test_record_trial_cost_report.py tests/unit/runtime/test_trial_economics_report_strict.py tests/unit/models/test_model_selection_policy.py tests/unit/models/test_pipeline_registry.py tests/unit/models/test_selector.py -q --tb=short --timeout=30`: PASS, 57 passed.
- `pytest tests/live/ -q -m live --tb=short --timeout=20` with placeholder env values: PASS, 13 skipped.
- `pytest tests/live/ -q --tb=short --timeout=20`: all 13 live tests deselected by default; pytest exits 5 because no non-live tests remain in that slice.
- `ruff check` on touched trial/live/model/economics surfaces: PASS.
- `lint-imports --config pyproject.toml`: PASS, 9 kept, 0 broken.
- `pytest tests/migration -q --tb=short --timeout=30`: PASS, 85 passed.
- `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/setup/ready_for_trial.ps1`: PASS, `YOU ARE READY FOR TRIAL`.
- `bash scripts/setup/ready_for_trial.sh`: NOT RUN; `bash` is not installed on this Windows host.

## Triage

### Patch

| Finding | Disposition |
| --- | --- |
| OpenAI live cascade smoke used `max_tokens`, which GPT-5 rejects. | Patched to `max_completion_tokens`; live smoke now skips cleanly when no real key is present. |
| Trial CLI could previously create a zero-cost offline report while looking like production evidence. | Patched so LangSmith env is required before default execution; offline mode is explicit via `--allow-offline-cost-report` and marks `production_clone_launch_evidence=false`. |
| Trial CLI accepted `--operator-id` but the M3 harness hard-coded operator identity in applied verdicts. | Patched `run_local_m3_trial` to propagate `operator_id` to verdict/apply phases; tests cover propagation. |
| Trial runbook used incorrect override commands. | Patched to `python -m app.marcus.cli gate override-submit` and `override-apply`. |
| Trial runbook Step 0 allowed raw preflight to bypass the ready harness. | Patched Step 0 to use `scripts/setup/ready_for_trial.ps1` / `.sh` as the primary readiness gate. |
| `sprint-status.yaml` still described the carry-forward condition as dispatch-registry unresolved. | Patched to name Plausible-Token live verification as condition #4 and dispatch-registry as resolved. |
| PowerShell ready harness could falsely pass if a command was not found. | Patched `Invoke-Step` to stop on PowerShell errors and force nonzero failures. |
| OpenAI pricing/registry metadata was stale after the substrate correction. | Patched `runtime/config/openai_pricing.yaml`, `app/models/registry.yaml`, and affected golden tests/fixtures to April 2026 official prices: `gpt-5`, `gpt-5-mini`, and `gpt-5-nano`. |
| Active development-guide surfaces still named deprecated fictitious GPT-5 variants as examples. | Patched `docs/dev-guide/specialist-migration-template.md` and `docs/dev-guide/langgraph-migration-guide.md`; historical A10/A15 anti-pattern examples remain intact as defect evidence. |
| Generated `tests/live/__pycache__` was present in the working tree. | Removed. |

### Dismiss

| Finding | Rationale |
| --- | --- |
| Ready-for-trial harness should execute the live OpenAI cascade smoke before declaring ready. | Dismissed for this batch. The dispatch explicitly separates readiness from operator-presence live verification; live OpenAI smoke remains post-batch operator work to close M5 condition #4. The harness now runs the structural lint guard, catalog-membership test, and cascade loading test before declaring readiness. |

### Decision Needed

| Finding | Why It Needs Operator Decision |
| --- | --- |
| B-extra production-clone trial launcher is implemented as a CLI registration shim around the deterministic local M3 harness, not a verified live production graph invocation. | The code no longer fabricates production evidence: default execution requires LangSmith env, explicit offline mode is labeled `registered-offline`, and generated run config records `production_clone_launch_evidence=false`. However, the current available seam is still `marcus/orchestrator/m3_trial.py`, not a proven live OpenAI production orchestration path. Operator decision is required: accept this as a registration shim and keep condition #3 open for the real operator-window trial, or authorize locating/implementing the real production graph entry point before this batch is declared closed. |

## Acceptance Auditor Result

A15 is closed for production-code model IDs at the static/code level: the lint guard passes, cascade IDs are catalog-allowlisted, and the cascade loader validates against the corrected OpenAI catalog snapshot. Live verification is still pending by design under M5 condition #4.

B3, B5, and B7 meet their dispatch acceptance gates. B-extra is partially remediated but remains `decision_needed` because the launcher does not yet prove production-clone equivalence.
