# GitHub GCM “Select an account” popup (jlenrique vs x-access-token)

## Recurring cause (this repo)

Not a mysterious Windows glitch. A **second GitHub identity** keeps getting written into Windows Credential Manager:

| Target | User |
|---|---|
| `git:https://github.com` | `jlenrique` (your real account) |
| `git:https://x-access-token@github.com` | `x-access-token` (PAT-as-username) |

Git Credential Manager’s multi-account UI then forces **Select an account** on every HTTPS `git fetch` / `push` / `pull` — including mid-agent commits. That stalls long-running BMAD/dev loops.

### How the rogue identity was re-seeded

Production **gh-pages publish** (styleguide picker / chooser transport in `app/marcus/orchestrator/gh_pages_publish.py`) clones and pushes with:

```text
https://x-access-token:{PAT}@github.com/...
```

While the default `credential.helper=manager` was active, a successful publish **stored** that URL’s username (`x-access-token`) in WinCred. The next operator-facing git op then saw two accounts.

Secondary contributors (same pattern elsewhere): any tool that uses `https://x-access-token:…@github.com` *without* disabling the credential helper (agents, one-off scripts, `GH_TOKEN` URL injection).

## Durable fixes (landed 2026-07-17)

1. **Stop the seed** — `gh_pages_publish._git` now runs with `-c credential.helper=` + `GCM_INTERACTIVE=Never` so the PAT stays in the ephemeral URL and is **not** written to GCM.
2. **Neutralize script** — `scripts/operator/neutralize_github_gcm_account_picker.ps1`
   - Deletes rogue `x-access-token` WinCred entries
   - Pins `credential.https://github.com.username=jlenrique`
   - Optionally rewrites `origin` to `https://jlenrique@github.com/...`
3. **Trial harness** — `scripts/setup/ready_for_trial.ps1` runs neutralize as a `[pre]` step.

## Operator commands

```powershell
# One-shot clean + pin + fix origin
.\scripts\operator\neutralize_github_gcm_account_picker.ps1 -FixOrigin

# Status only (exit 2 if rogue present)
.\scripts\operator\neutralize_github_gcm_account_picker.ps1 -CheckOnly

# Background watch during a long agent session (Ctrl+C to stop)
.\scripts\operator\neutralize_github_gcm_account_picker.ps1 -Watch -IntervalSeconds 60
```

If the popup appears mid-run: choose **`jlenrique`**, then re-run the neutralize script (or let `-Watch` catch it). Prefer **not** choosing `x-access-token`.

## Do not

- Embed `https://x-access-token:…@github.com` in `origin` / `upstream` remotes.
- Leave `GH_TOKEN` / `GITHUB_TOKEN` in the parent shell that agents inherit for ordinary pushes — use `gh auth` / GCM as `jlenrique` instead.
