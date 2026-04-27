# Run HUD Guide

Generate a snapshot:

```bash
.venv/Scripts/python.exe -m scripts.utilities.run_hud --open
```

Run live regeneration while a trial is active:

```bash
.venv/Scripts/python.exe -m scripts.utilities.run_hud --watch 30 --open
```

Watch mode rewrites `reports/run-hud.html` every interval. The browser reload timer then shows fresh data because the file on disk changes.

## Panels

- **System Health:** preflight result plus source-health checks from sprint-status and handoff files.
- **Production Run:** legacy pipeline position and gate results from bundle sidecars.
- **Dev Cycle:** sprint progress from `_bmad-output/implementation-artifacts/sprint-status.yaml`.
- **Active Trial:** latest or selected migrated-runtime trial, per-agent cost, trace link, and drift alerts.
- **Cost Engineering:** cascade preview, pricing preview, last-five-trial median cost, and `MARCUS_TRIAL_BUDGET_USD` soft cap.
- **M5 Conditional Window:** remaining window posture and open-condition statuses while the window is relevant.
- **Ad-hoc Mode:** quick command reference plus LangSmith ad-hoc trace availability.

Use `--trial-id <id>` to pin the active-trial panel. Use `--no-adhoc-panel` if you do not want the HUD to query the ad-hoc LangSmith project.

At a 30 second watch interval, the expected overhead is negligible: filesystem reads, local cost-report parsing, optional Postgres/checkpointer reads as that substrate becomes available, and a cheap LangSmith project query.
