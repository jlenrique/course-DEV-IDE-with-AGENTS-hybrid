$ErrorActionPreference = "Stop"

Write-Host "== Story 7a.8 focused slice =="
.venv/Scripts/python.exe -m pytest `
  tests/parity/test_operator_control_parity.py `
  tests/parity/test_operator_control_parity_row_count.py `
  tests/parity/test_composition_spec_invariants.py `
  tests/parity/test_nfr_cg_block_aggregated.py `
  tests/integration/marcus/test_calibration_tripwire.py `
  tests/integration/marcus/test_engagement_decay_report.py `
  tests/integration/marcus/test_marcus_duality_boundary.py `
  -q --tb=short

Write-Host "== Wider regression slice =="
.venv/Scripts/python.exe -m pytest `
  tests/unit/manifest `
  tests/integration/marcus `
  tests/composition `
  tests/parity `
  tests/structural `
  tests/unit/marcus `
  tests/specialists/texas `
  tests/specialists/_scaffold `
  tests/cli `
  tests/unit/models `
  -q --tb=line

Write-Host "== Substrate gates =="
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py `
  _bmad-output/implementation-artifacts/migration-7a-8-integration-parity-test-suite-slab-7a-closeout.md

Write-Host "== Code quality =="
.venv/Scripts/python.exe -m ruff check `
  app/marcus/orchestrator/gate_runner.py `
  app/marcus/orchestrator/dispatch_adapter.py `
  app/marcus/orchestrator/production_runner.py `
  tests/parity `
  tests/integration/marcus/test_calibration_tripwire.py `
  tests/integration/marcus/test_engagement_decay_report.py `
  tests/integration/marcus/test_marcus_duality_boundary.py
.venv/Scripts/lint-imports.exe

Write-Host "== Composition smokes =="
.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-1-directive-composer-composition-smoke.py
.venv/Scripts/python.exe _bmad-output/implementation-artifacts/migration-7-7-a2-shims-composition-smoke.py

Write-Host "== Operator-only trial-2 ceremony reminder =="
Write-Host "Run trial-2 or trial-2 dry-run with --allow-offline-cost-report, then paste stdout and run_summary.yaml paths into Completion Notes."
