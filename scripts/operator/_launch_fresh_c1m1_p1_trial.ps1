$ErrorActionPreference = "Stop"
Set-Location "C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid"
& ".\.venv\Scripts\Activate.ps1"
$env:MARCUS_G0_DISPATCH_LIVE = "1"
$env:MARCUS_RESEARCH_DETECTIVE_LIVE = "1"
$env:MARCUS_TRIAL_BUDGET_USD = "10"
Write-Host ""
Write-Host "=== Marcus-SPOC fresh production trial ===" -ForegroundColor Cyan
Write-Host "corpus:  course-content/courses/tejal-apc-c1m1-p1-call"
Write-Host "plan:    runs/6408280c-8b1e-4dcb-bdcb-55d873d76c05/ratified-collateral-intent.yaml"
Write-Host "preset:  production | encounter: recorded | vision: batch | HUD: on"
Write-Host "flags:   G0_DISPATCH_LIVE=1 | RESEARCH_DETECTIVE_LIVE=1 | BUDGET=$10"
Write-Host "HUD:     http://localhost:8791"
Write-Host ""
& .\.venv\Scripts\python.exe -m app.marcus.cli trial start `
  --preset production `
  --input "course-content/courses/tejal-apc-c1m1-p1-call" `
  --course-source-root "course-content/courses/tejal-apc-c1m1-p1-call" `
  --encounter-mode recorded `
  --lesson-plan-collateral-intent "runs/6408280c-8b1e-4dcb-bdcb-55d873d76c05/ratified-collateral-intent.yaml" `
  --llm-execution-mode batch `
  --hud on `
  --operator-id Juanl
