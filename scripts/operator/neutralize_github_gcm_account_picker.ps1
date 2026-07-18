<#
.SYNOPSIS
  Neutralize the recurring GitHub "Select an account" (jlenrique vs x-access-token) GCM popup.

.DESCRIPTION
  Recurring cause (this repo):
    Production gh-pages publish (styleguide picker / chooser) historically cloned/pushed
    with https://x-access-token:{PAT}@github.com/... WHILE the default Git Credential
    Manager helper was active. GCM then STORED a Windows credential:
      Target: git:https://x-access-token@github.com
      User:   x-access-token
    That second identity makes GCM prompt on every later HTTPS git op.

  This script:
    1) Deletes any Windows Credential Manager entries for x-access-token@github.com
       (and the empty gh:github.com: ghost entry).
    2) Pins credential.https://github.com.username = jlenrique (global).
    3) Optionally rewrites origin to https://jlenrique@github.com/... (account-in-URL).
    4) Verifies `git credential fill` returns username=jlenrique (non-interactive).

  Pair with the code fix in app/marcus/orchestrator/gh_pages_publish.py::_git
  (credential.helper disabled for publish subprocesses) so the seed stops regenerating.

.PARAMETER CheckOnly
  Report status; do not delete credentials or rewrite config/remotes.

.PARAMETER FixOrigin
  Rewrite this repo's origin URL to include jlenrique@ (recommended once).

.PARAMETER Watch
  Loop: neutralize whenever an x-access-token credential reappears (Ctrl+C to stop).

.PARAMETER IntervalSeconds
  Poll interval for -Watch (default 30).

.EXAMPLE
  .\scripts\operator\neutralize_github_gcm_account_picker.ps1 -FixOrigin
  .\scripts\operator\neutralize_github_gcm_account_picker.ps1 -Watch -IntervalSeconds 60
#>
[CmdletBinding()]
param(
    [switch]$CheckOnly,
    [switch]$FixOrigin,
    [switch]$Watch,
    [int]$IntervalSeconds = 30,
    [string]$GitHubUser = "jlenrique",
    [string]$RepoRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
}

$RogueTargets = @(
    "LegacyGeneric:target=git:https://x-access-token@github.com",
    "LegacyGeneric:target=gh:github.com:"
)

function Get-GitHubCredentialLines {
    cmdkey /list 2>&1 | Out-String
}

function Test-RogueXAccessTokenPresent {
    $list = Get-GitHubCredentialLines
    return ($list -match "x-access-token@github\.com") -or ($list -match "User:\s*x-access-token")
}

function Remove-RogueCredentials {
    $deleted = 0
    foreach ($t in $RogueTargets) {
        $out = cmdkey /delete:$t 2>&1 | Out-String
        if ($out -match "deleted successfully") {
            Write-Host "Deleted credential: $t" -ForegroundColor Yellow
            $deleted++
        }
    }
    # Catch any other git:/gh: targets that literally embed x-access-token
    $list = Get-GitHubCredentialLines
    foreach ($line in ($list -split "`n")) {
        if ($line -match 'Target:\s*(.+\bx-access-token\b.+)$') {
            $target = $Matches[1].Trim()
            $out = cmdkey /delete:$target 2>&1 | Out-String
            if ($out -match "deleted successfully") {
                Write-Host "Deleted credential: $target" -ForegroundColor Yellow
                $deleted++
            }
        }
    }
    return $deleted
}

function Set-PinnedGitHubUsername {
    git config --global "credential.https://github.com.username" $GitHubUser | Out-Null
    $got = git config --global --get "credential.https://github.com.username"
    if ($got -ne $GitHubUser) {
        throw "Failed to pin credential.https://github.com.username (got '$got')"
    }
    Write-Host "Pinned credential.https://github.com.username=$GitHubUser" -ForegroundColor Green
}

function Set-OriginAccountInUrl {
    Push-Location $RepoRoot
    try {
        $cur = git remote get-url origin 2>$null
        if (-not $cur) { return }
        if ($cur -match '^https://github\.com/') {
            $next = $cur -replace '^https://github\.com/', "https://${GitHubUser}@github.com/"
            git remote set-url origin $next
            Write-Host "origin -> $next" -ForegroundColor Green
        }
        elseif ($cur -match "^https://x-access-token@github\.com/") {
            $next = $cur -replace '^https://x-access-token@github\.com/', "https://${GitHubUser}@github.com/"
            git remote set-url origin $next
            Write-Host "origin (was x-access-token) -> $next" -ForegroundColor Green
        }
        else {
            Write-Host "origin left unchanged: $cur" -ForegroundColor DarkGray
        }
    }
    finally {
        Pop-Location
    }
}

function Test-CredentialFillUsername {
    $prev = $env:GCM_INTERACTIVE
    $env:GCM_INTERACTIVE = "never"
    try {
        $input = "protocol=https`nhost=github.com`n`n"
        $fill = $input | & git credential fill 2>&1 | Out-String
        if ($fill -match "(?m)^username=(.+)$") {
            $u = $Matches[1].Trim()
            if ($u -eq $GitHubUser) {
                Write-Host "credential fill username=$u (OK)" -ForegroundColor Green
                return $true
            }
            Write-Host "credential fill username=$u (EXPECTED $GitHubUser)" -ForegroundColor Red
            return $false
        }
        Write-Host "credential fill did not return username (may need interactive login once)" -ForegroundColor Yellow
        return $false
    }
    finally {
        if ($null -eq $prev) { Remove-Item Env:GCM_INTERACTIVE -ErrorAction SilentlyContinue }
        else { $env:GCM_INTERACTIVE = $prev }
    }
}

function Invoke-NeutralizeOnce {
    Write-Host "=== GitHub GCM account-picker neutralize ===" -ForegroundColor Cyan
    Write-Host "RepoRoot: $RepoRoot"
    $rogue = Test-RogueXAccessTokenPresent
    Write-Host ("Rogue x-access-token credential present: {0}" -f $rogue)

    if ($CheckOnly) {
        $pin = git config --global --get "credential.https://github.com.username" 2>$null
        Write-Host "Pinned username: $pin"
        Push-Location $RepoRoot
        try { Write-Host "origin: $(git remote get-url origin 2>$null)" } finally { Pop-Location }
        if ($rogue) { exit 2 } else { exit 0 }
    }

    if ($rogue) {
        $n = Remove-RogueCredentials
        Write-Host "Deleted $n rogue credential entry(ies)."
    }
    else {
        Write-Host "No rogue x-access-token credential found." -ForegroundColor DarkGray
    }

    Set-PinnedGitHubUsername
    if ($FixOrigin) { Set-OriginAccountInUrl }

    $ok = Test-CredentialFillUsername
    if (-not $ok) {
        Write-Host "Hint: run 'gh auth login' once as $GitHubUser, then re-run this script." -ForegroundColor Yellow
    }

    if (Test-RogueXAccessTokenPresent) {
        Write-Host "FAIL: rogue credential still present after neutralize." -ForegroundColor Red
        exit 2
    }
    Write-Host "Neutralize complete." -ForegroundColor Green
}

if ($Watch) {
    Write-Host "Watching for x-access-token GCM reseeds every ${IntervalSeconds}s (Ctrl+C to stop)..." -ForegroundColor Cyan
    while ($true) {
        if (Test-RogueXAccessTokenPresent) {
            Write-Host "$(Get-Date -Format o) ROGUE DETECTED - neutralizing" -ForegroundColor Yellow
            & $PSCommandPath -FixOrigin:$FixOrigin -GitHubUser $GitHubUser -RepoRoot $RepoRoot
        }
        Start-Sleep -Seconds $IntervalSeconds
    }
}
else {
    Invoke-NeutralizeOnce
}
