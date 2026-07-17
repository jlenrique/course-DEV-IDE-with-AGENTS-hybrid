# Operator HUD Guide (Epic 35 runtime HUD)

> **Rewritten 2026-07-15.** The legacy static-HTML HUD (`scripts/utilities/run_hud.py --open/--watch`) was **retired at Epic 35 story 35.8** — that module is now a deprecation stub exposing only the `PIPELINE_STEPS` lockstep projection. The operator HUD is now a **runtime-owned, GET-only localhost server** over a per-run projection file. Epic 35 closed 2026-07-12 with a unanimous party re-verdict: the HUD is **authorized for real operator use**.

## How it launches

The HUD launches **automatically with a trial**: `python -m app.marcus.cli trial start ...` starts the HUD server and the notifier as start-path children (`--hud on` is the default; pass `--hud off` to run without them — runtime pre-flight and heartbeats run regardless).

Open it in a browser at:

```
http://localhost:8791
```

- Port: `HUD_PORT` env var (default `8791`). Mode: `HUD_MODE` (default `session`).
- The server is **GET-only** and localhost-bound — it can display state but can never mutate a run.

## What it shows

The HUD renders the run's **operator-surface projection** — `state/config/runs/<trial_id>/operator-surface.json` — written by a single writer (`app/marcus/orchestrator/operator_surface_assembler.py`) every time the runtime persists the envelope. Contract: `operator-surface.v1` (`app/models/runtime/operator_surface.py`; parity contract-pinned in `tests/contracts/`).

Surfaces include: run/status header, the pending **gate card** (with a paste-ready `trial resume` inline-verdict command — all 8 gate classes witnessed paste-driven on the live E2E), specialist roster, event trace, cost/economics, and ambient instrument sections.

**No wrong-run fallback exists.** The April failure mode (HUD silently rendering the newest bundle from a different run) was deleted with the legacy reader chain, not bypassed — the HUD reads only the projection of the run that launched it.

## Notifications

- Config: `state/config/hud-config.yaml` — per-event-class matrix (`paused_at_gate`, error classes, …) with `enabled` / `sound` / `push` toggles. Unknown keys are rejected; an unreadable file falls back to defaults and the HUD says so ("config unreadable — defaults active").
- On-HUD toast + sound are the HUD page's channel; phone push goes through the `app/notify/` ntfy notifier (+ watchdog).
- **Push credentials are never in the YAML** — they live in the `HUD_PUSH_URLS` env var only.

## Acting on a gate

The HUD is read-only; verdicts go through the CLI. Copy the paste command from the gate card — it is a `python -m app.marcus.cli trial resume --trial-id <id> ...` inline-verdict invocation — run it in a shell, and watch the HUD update as the walk resumes.

## Known non-blocking debt (Epic 35 close record)

Batch pause-class rendering un-witnessed live; browser DOM/notification witness; L2-golden gate-snapshot. Workbook runs are typically driven by the governed live-test runner with HUD OFF (runner-enforced) — see `docs/admin-guide.md` §Workbook Live Authoring.

## Public read-only overlay (any browser / phone, stable URL)

The localhost HUD above is the **authority**. Story 42-4 adds an **optional** outbound overlay so you can watch a run from any browser or phone at one stable URL. It is a **separate** GET-only app (`app/hud/public.py`) serving a positive-allowlist projection of the same run — status/gate/progress/roster/settings/trace only. It **never** exposes the launch nonce, resume/paste commands, decision-card evidence, error/source text, credentials, or export paths, and it can never serve a write route (belt-and-suspenders beyond the tunnel's identity ACL). Localhost stays authority; if no tunnel is configured, the overlay is simply absent and the run is unaffected.

Access is **identity-aware and never anonymous**: Cloudflare Access (account login + MFA, or an emailed single-use PIN allowlisted to you) on a named Cloudflare Tunnel (preferred), or Tailscale Serve on your tailnet (fallback). Full setup recipe + validation checklist: `docs/admin-guide.md` §Public Read-Only HUD Overlay.

## Pointers

- Dev-side substrate map: `docs/dev-guide.md` §Current Status (Epic 35 bullet).
- Close record: `docs/project-context.md` §2026-07-11 addendum; stories under `_bmad-output/implementation-artifacts/`.
