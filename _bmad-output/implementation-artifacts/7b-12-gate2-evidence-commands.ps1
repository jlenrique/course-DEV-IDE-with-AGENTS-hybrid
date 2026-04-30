$ErrorActionPreference = "Stop"

# Slab 7b 7b.12 Integration — DUAL-GATE Gate-2 operator-witnessed evidence ceremony.
# Run this script at next-session-start; paste verbatim stdout into the
# "Completion Notes" section of `migration-7b-12-integration-parity-suite-closeout.md`.
#
# Per 7b.12 spec AC-N: operator runs full focused + wider regression battery
# + sandbox-AC + lockstep + ruff + lint-imports + Composition Smoke + 5-API smoke
# + trial-2 cost-projection. Gate-2 PASS requires all 14 evidence blocks PASS.

Write-Host "== 7b.12 focused parity slice =="
.venv/Scripts/python.exe -m pytest `
  tests/parity/test_skill_md_sanctum_alignment.py `
  tests/parity/test_eleven_specialists_addressable.py `
  tests/parity/test_mapping_checklist_status.py `
  tests/parity/test_nfr_cg_slab7b_block_aggregated.py `
  tests/parity/test_rate_limit_budgets_declared.py `
  tests/parity/test_pipeline_determinism_harness.py `
  -q --tb=short

Write-Host "== All 11 per-specialist activation contracts =="
.venv/Scripts/python.exe -m pytest tests/parity/test_*_activation_contract.py -q --tb=short

Write-Host "== Wider regression slice (deterministic order; -p no:randomly) =="
.venv/Scripts/python.exe -m pytest `
  tests/unit/manifest `
  tests/integration/marcus `
  tests/composition `
  tests/parity `
  tests/structural `
  tests/unit/marcus `
  tests/specialists `
  tests/cli `
  tests/unit/models `
  -p no:randomly `
  --ignore=tests/integration/marcus/test_directive_confirm_or_edit_prompt.py `
  -q --tb=line

Write-Host "== Substrate gates =="
.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py

Write-Host "== Sandbox-AC validator on all 12 Slab 7b stories =="
$slab7bStories = @(
  "_bmad-output/implementation-artifacts/migration-7b-1-texas-hardening.md",
  "_bmad-output/implementation-artifacts/migration-7b-2-quinn-r-hardening.md",
  "_bmad-output/implementation-artifacts/migration-7b-3-vera-hardening.md",
  "_bmad-output/implementation-artifacts/migration-7b-4-irene-pass1-refresh.md",
  "_bmad-output/implementation-artifacts/migration-7b-5-tracy-port-shape-sidecar.md",
  "_bmad-output/implementation-artifacts/migration-7b-6-gary-port-shape.md",
  "_bmad-output/implementation-artifacts/migration-7b-7-kira-port-shape.md",
  "_bmad-output/implementation-artifacts/migration-7b-8-enrique-port-shape.md",
  "_bmad-output/implementation-artifacts/migration-7b-9-wanda-port-shape-onto-scaffold.md",
  "_bmad-output/implementation-artifacts/migration-7b-10-dan-greenfield.md",
  "_bmad-output/implementation-artifacts/migration-7b-11-compositor-greenfield.md",
  "_bmad-output/implementation-artifacts/migration-7b-12-integration-parity-suite-closeout.md"
)
.venv/Scripts/python.exe scripts/utilities/validate_migration_story_sandbox_acs.py @slab7bStories

Write-Host "== Class-conformance validator (6 classes; 11 contracts) =="
.venv/Scripts/python.exe scripts/utilities/validate_parity_test_class_conformance.py tests/parity/

Write-Host "== Live-API detector (NFR-CG13 strict) =="
.venv/Scripts/python.exe scripts/utilities/detect_live_api_in_tests.py

Write-Host "== Code quality (story-scoped) =="
.venv/Scripts/python.exe -m ruff check `
  tests/parity/test_eleven_specialists_addressable.py `
  tests/parity/test_mapping_checklist_status.py `
  tests/parity/test_nfr_cg_slab7b_block_aggregated.py `
  tests/parity/test_rate_limit_budgets_declared.py `
  app/specialists/compositor `
  app/specialists/dan

Write-Host "== Import-linter contracts =="
.venv/Scripts/lint-imports.exe

Write-Host ""
Write-Host "============================================================"
Write-Host "== OPERATOR-GATED CEREMONY (separate live-credential blocks) =="
Write-Host "============================================================"
Write-Host ""
Write-Host "AC-7b.12-G operator-gated cache-hit-rate harness aggregation:"
Write-Host "  .venv/Scripts/python.exe scripts/utilities/run_cache_hit_harness.py --all-specialists --median-from-index 2 --threshold 0.85 > _bmad-output/implementation-artifacts/7b-12-cache-hit-harness-evidence.txt"
Write-Host "  .venv/Scripts/python.exe scripts/utilities/run_pipeline_determinism_harness.py --threshold 0.99 > _bmad-output/implementation-artifacts/7b-12-pipeline-determinism-harness-evidence.txt"
Write-Host ""
Write-Host "AC-7b.12-H trial-2 cost-projection (Round-(a) John A1 / SR-T6):"
Write-Host "  .venv/Scripts/python.exe scripts/utilities/project_trial_2_cost.py --evidence-path _bmad-output/implementation-artifacts/7b-12-trial-2-cost-projection.json"
Write-Host ""
Write-Host "AC-7b.12-I 5-API live-binding smoke (cost ceiling \$6.00 / 5 APIs x 3 canaries x \$0.40):"
Write-Host "  .venv/Scripts/python.exe scripts/utilities/run_5_api_smoke.py --apis gamma,kling,elevenlabs,wondercraft,dan-llm-only --max-canaries-per-api 3 --max-cost-per-canary 0.40 --evidence-path _bmad-output/implementation-artifacts/7b-12-5-api-smoke-evidence.json"
Write-Host ""
Write-Host "AC-7b.12-O MVP Exit Gate verification (G2 + 9-of-11):"
Write-Host "  Operator runs trial-2 (or trial-2 dry-run); verifies G2 reached cleanly with"
Write-Host "  real content from >=9 of 11 specialists (>=3 per class); SG-1+SG-2+SG-3 green."
Write-Host "  Evidence: _artifacts/trial-2/g2_exit_evidence.yaml"
Write-Host ""
Write-Host "AC-7b.12-P Slab Close Gate verification (G3 + 11 cascade-reading):"
Write-Host "  Operator runs trial-2 to G3; verifies cascade-reading of 11 specialists"
Write-Host "  (Wanda + Tracy contribute via Pass-2 cascade audit logs)."
Write-Host "  Evidence: _artifacts/trial-2/g3_close_evidence.yaml"
Write-Host ""
Write-Host "Gate-2 PASS = all 14 evidence blocks above PASS + 5-API smoke total spend <= \$6.00 +"
Write-Host "trial-2 cost-projection <= BS-3 ceiling. Operator pastes verbatim stdout/JSON into"
Write-Host "Completion Notes; Slab 7b retrospective opens at T15."
