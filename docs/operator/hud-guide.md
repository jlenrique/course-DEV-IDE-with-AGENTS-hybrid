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

## Per-step summaries

Each Production Run step includes an expandable summary. The summary is derived from existing bundle artifacts, keyed by the manifest step ID and label. It shows the locked artifact source, captured fields when the source has structured metadata, and the artifact freshness timestamp. If the HUD cannot find a known artifact for a step, it says `no locked artifact yet`.

The current step and any step with warnings or blockers auto-expand. Saved collapse state is ignored for current, warning, and blocker steps so urgent states are visible after every refresh. You can manually collapse an urgent step after seeing it, but the next render opens it again while the status remains urgent. Other steps preserve expand/collapse state through browser refresh via `sessionStorage`; the state key is based on each stable step summary ID. Clearing browser session storage resets all non-urgent expansion state to defaults.

`--watch` remains pull-based: the CLI rewrites `reports/run-hud.html` on the requested interval, and the browser reloads the rewritten file. There is no push event bus.

Use `--trial-id <id>` to pin the active-trial panel. Use `--no-adhoc-panel` if you do not want the HUD to query the ad-hoc LangSmith project.

At a 30 second watch interval, the expected overhead is negligible: filesystem reads, local cost-report parsing, optional Postgres/checkpointer reads as that substrate becomes available, and a cheap LangSmith project query.
