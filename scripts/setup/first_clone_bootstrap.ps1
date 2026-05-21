# first_clone_bootstrap.ps1 — one-command setup for fresh clone (Windows / PowerShell)
#
# Usage:
#   pwsh scripts/setup/first_clone_bootstrap.ps1
#   pwsh scripts/setup/first_clone_bootstrap.ps1 -SkipPostgres
#
# What it does:
#   1. Verify Python 3.11+ + git on PATH
#   2. Create .venv if absent
#   3. Install deps via pip (preferred for Windows; uv works too if installed)
#   4. Stub .env from .env.example if .env absent
#   5. Install pre-commit hooks (recommended)
#   6. Optional: Postgres reachability ping (skip with -SkipPostgres)
#   7. Run trial_run_preflight.py for sanity verdict
#
# Per CLAUDE.md operator preference: invoke .venv/Scripts/ binaries freely (no per-command prompts).

[CmdletBinding()]
param(
    [switch]$SkipPostgres,
    [switch]$SkipPreCommit
)

$ErrorActionPreference = "Stop"
$repoRoot = Resolve-Path "$PSScriptRoot\..\.."

Write-Host "=== first_clone_bootstrap (Windows) ===" -ForegroundColor Cyan
Write-Host "Repo: $repoRoot"
Write-Host ""

# --- Step 1: Python + git check ---
Write-Host "[1/7] Verifying Python 3.11+ + git on PATH..." -ForegroundColor Yellow
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "  FAIL: python not on PATH. Install Python 3.11+ from python.org." -ForegroundColor Red
    exit 2
}
$pyver = & python --version 2>&1
Write-Host "  Python: $pyver"
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "  WARN: git not on PATH (commits/pushes will fail)" -ForegroundColor Yellow
} else {
    Write-Host "  Git: $((& git --version).Trim())"
}

# --- Step 2: venv ---
Write-Host ""
Write-Host "[2/7] Creating .venv if absent..." -ForegroundColor Yellow
if (Test-Path "$repoRoot\.venv\Scripts\python.exe") {
    Write-Host "  PASS: .venv exists"
} else {
    Write-Host "  Creating .venv..."
    Push-Location $repoRoot
    & python -m venv .venv
    Pop-Location
    Write-Host "  PASS: .venv created"
}

# --- Step 3: Install deps ---
Write-Host ""
Write-Host "[3/7] Installing dependencies via pip..." -ForegroundColor Yellow
Push-Location $repoRoot
& .\.venv\Scripts\python.exe -m pip install --upgrade pip 2>&1 | Out-Null
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]" 2>&1 | Tee-Object -Variable pipOut | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "  FAIL: pip install failed" -ForegroundColor Red
    Write-Host $pipOut
    Pop-Location
    exit 2
}
Write-Host "  PASS: deps installed (editable + dev extras)"
Pop-Location

# --- Step 4: .env stub ---
Write-Host ""
Write-Host "[4/7] Stubbing .env from .env.example if absent..." -ForegroundColor Yellow
if (Test-Path "$repoRoot\.env") {
    Write-Host "  PASS: .env exists"
} elseif (Test-Path "$repoRoot\.env.example") {
    Copy-Item "$repoRoot\.env.example" "$repoRoot\.env"
    Write-Host "  PASS: .env stubbed from .env.example"
    Write-Host "  ACTION REQUIRED: edit .env and replace <placeholder> values with real credentials" -ForegroundColor Cyan
} else {
    Write-Host "  WARN: no .env.example found; create .env manually" -ForegroundColor Yellow
}

# --- Step 5: Pre-commit hooks ---
if ($SkipPreCommit) {
    Write-Host ""
    Write-Host "[5/7] Skipping pre-commit install (per -SkipPreCommit)" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "[5/7] Installing pre-commit hooks..." -ForegroundColor Yellow
    Push-Location $repoRoot
    & .\.venv\Scripts\pre-commit.exe install 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  PASS: pre-commit hooks installed"
    } else {
        Write-Host "  WARN: pre-commit install failed (you can run manually later)" -ForegroundColor Yellow
    }
    Pop-Location
}

# --- Step 6: Postgres ping ---
if ($SkipPostgres) {
    Write-Host ""
    Write-Host "[6/7] Skipping Postgres check (per -SkipPostgres)" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "[6/7] Pinging Postgres (non-fatal; trial-run can use in-memory checkpointer)..." -ForegroundColor Yellow
    Push-Location $repoRoot
    $pgOut = & .\.venv\Scripts\python.exe -c @"
import os, sys
db = os.environ.get('DATABASE_URL')
if not db:
    print('SKIP: DATABASE_URL not set in environment'); sys.exit(0)
try:
    import psycopg
    psycopg.connect(db, connect_timeout=5).close()
    print('PASS: Postgres reachable')
except Exception as e:
    print(f'WARN: Postgres ping failed: {e}'); sys.exit(0)
"@ 2>&1
    Write-Host "  $pgOut"
    Pop-Location
}

# --- Step 7: Preflight ---
Write-Host ""
Write-Host "[7/7] Running trial_run_preflight.py..." -ForegroundColor Yellow
Push-Location $repoRoot
& .\.venv\Scripts\python.exe scripts\utilities\trial_run_preflight.py
$preflightExit = $LASTEXITCODE
Pop-Location

Write-Host ""
Write-Host "=== Bootstrap complete ===" -ForegroundColor Cyan
if ($preflightExit -eq 0) {
    Write-Host "Verdict: GREEN — ready for trial-run (warnings may apply; review preflight output above)" -ForegroundColor Green
} elseif ($preflightExit -eq 1) {
    Write-Host "Verdict: YELLOW — non-required failures detected; review preflight output above" -ForegroundColor Yellow
} else {
    Write-Host "Verdict: RED — blocking failures; resolve before trial-run (see preflight output above)" -ForegroundColor Red
}
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit .env to replace <placeholder> values with real credentials"
Write-Host "  2. Read docs/operator/trial-run-runbook.md for first-trial workflow"
Write-Host "  3. Read README.md for project orientation + status"
Write-Host ""
exit $preflightExit
