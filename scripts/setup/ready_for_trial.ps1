# ready_for_trial.ps1 - pre-flight one-command harness for first real trial readiness.
#
# Usage:
#   pwsh scripts/setup/ready_for_trial.ps1
#
# Exit 0 only when every required check passes. Prints a per-step summary and a
# final READY FOR TRIAL / BLOCKED banner.

[CmdletBinding()]
param()

$ErrorActionPreference = "Continue"
$PSNativeCommandUseErrorActionPreference = $false
$repoRoot = Resolve-Path "$PSScriptRoot\..\.."
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$ruff = Join-Path $repoRoot ".venv\Scripts\ruff.exe"
$lintImports = Join-Path $repoRoot ".venv\Scripts\lint-imports.exe"

$results = [System.Collections.Generic.List[object]]::new()

function Invoke-Step {
    param(
        [int]$Number,
        [string]$Name,
        [scriptblock]$Action
    )

    Write-Host ""
    Write-Host "[$Number/9] $Name..." -ForegroundColor Yellow

    $previousPreference = $ErrorActionPreference
    $ErrorActionPreference = "Stop"
    $global:LASTEXITCODE = 0
    try {
        $output = & $Action 2>&1
        $exitCode = $LASTEXITCODE
        if ($null -eq $exitCode) {
            $exitCode = 0
        }
    } catch {
        $output = @($_.Exception.Message)
        $exitCode = 1
    } finally {
        $ErrorActionPreference = $previousPreference
    }

    if ($output) {
        $output | ForEach-Object { Write-Host "  $_" }
    }

    $results.Add(
        [pscustomobject]@{
            Number = $Number
            Name = $Name
            ExitCode = $exitCode
        }
    ) | Out-Null

    if ($exitCode -eq 0) {
        Write-Host "  PASS" -ForegroundColor Green
    } else {
        Write-Host "  FAIL (exit $exitCode)" -ForegroundColor Red
    }
}

Push-Location $repoRoot
try {
    # Non-blocking hygiene: delete any GCM "x-access-token" identity that would
    # stall later git push/pull with the Select-an-account popup. Source of the
    # reseed was gh-pages publish (now also fixed in gh_pages_publish._git).
    Write-Host ""
    Write-Host "[pre] neutralize GitHub GCM account-picker (x-access-token)..." -ForegroundColor Yellow
    $neutralize = Join-Path $repoRoot "scripts\operator\neutralize_github_gcm_account_picker.ps1"
    # Prefer pwsh when present; fall back to Windows PowerShell 5.1.
    $shell = if (Get-Command pwsh -ErrorAction SilentlyContinue) { "pwsh" } else { "powershell" }
    & $shell -NoProfile -File $neutralize -FixOrigin
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  WARN: neutralize exited $LASTEXITCODE (continuing; fix before long agent git runs)" -ForegroundColor Yellow
    } else {
        Write-Host "  PASS" -ForegroundColor Green
    }

    Invoke-Step 1 "trial_run_preflight.py" {
        & $python "scripts\utilities\trial_run_preflight.py"
    }
    Invoke-Step 2 "migration_health_dashboard.py" {
        & $python "scripts\utilities\migration_health_dashboard.py"
    }
    Invoke-Step 3 "m5_pre_vote_audit.py" {
        & $python "scripts\utilities\m5_pre_vote_audit.py"
    }
    Invoke-Step 4 "app.runtime.cascade_config validate" {
        & $python -m app.runtime.cascade_config validate
    }
    Invoke-Step 5 "pytest remediation model-id guards" {
        & $python -m pytest `
            "tests\test_no_fictitious_model_ids.py" `
            "tests\integration\runtime\test_cascade_ids_in_openai_published_catalog.py" `
            "tests\integration\runtime\test_cascade_config_loading.py" `
            -q --tb=short
    }
    Invoke-Step 6 "required key presence (OPENAI_API_KEY, LANGSMITH_API_KEY)" {
        & $python -c "from scripts.utilities.env_loader import load_env; load_env(); import os; missing=[name for name in ('OPENAI_API_KEY','LANGSMITH_API_KEY') if not os.environ.get(name)]; assert not missing, f'Missing required keys: {missing}'; print('PASS: required keys present')"
    }
    Invoke-Step 7 "ruff check runtime/replay/runtime-model test surfaces" {
        & $ruff check `
            "app/runtime" `
            "app/replay" `
            "app/models/runtime" `
            "tests/unit/runtime" `
            "tests/integration/runtime" `
            "tests/integration/replay" `
            "tests/migration" `
            "tests/trial_replay" `
            "tests/test_no_fictitious_model_ids.py"
    }
    Invoke-Step 8 "lint-imports" {
        & $lintImports --config "pyproject.toml"
    }
    Invoke-Step 9 "pytest tests/migration -q --tb=short" {
        & $python -m pytest "tests/migration" -q --tb=short
    }
} finally {
    Pop-Location
}

$failed = $results | Where-Object { $_.ExitCode -ne 0 }

Write-Host ""
Write-Host "=== ready_for_trial summary ===" -ForegroundColor Cyan
foreach ($result in $results) {
    $status = if ($result.ExitCode -eq 0) { "PASS" } else { "FAIL" }
    Write-Host ("[{0}/9] {1}: {2}" -f $result.Number, $result.Name, $status)
}

Write-Host ""
if ($failed.Count -eq 0) {
    Write-Host "YOU ARE READY FOR TRIAL" -ForegroundColor Green
    exit 0
}

$firstFailed = $failed | Select-Object -First 1
Write-Host ("BLOCKED - see step {0} ({1}) above." -f $firstFailed.Number, $firstFailed.Name) -ForegroundColor Red
exit 1
