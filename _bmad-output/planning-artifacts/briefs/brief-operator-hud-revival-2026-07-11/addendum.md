# Addendum — Operator HUD Brief (depth for PRD/UX/Architecture consumers)

## A. Interview record (2026-07-11, binding-gate satisfaction)

Operator answers that pinned the brief (fresh requirements superseding the party plan's §3 where they diverge):

- Second monitor, dedicated display space; definitely read-only; **real-time moment-by-moment cockpit** is the product ("actively piloting this jet, mid-flight") — the party's returning-to-paused-run job is demoted to a supporting moment.
- Pre-flight as first-class HUD phase (checklist rendered as tested), **Phase-02 heartbeats** for all APIs/LLMs; on success Marcus-SPOC spawns.
- Two-stage progress map (pre-ratification steps → ratified workflow steps) with drill-down; gate briefings; specialist/service icons with briefings; debugger-like state window; health measures (token use, subscriptions/credits: Gamma, OpenAI, etc.); modality switches prominent (batch, detective, styleguide). UX detail + health-measure definitions delegated to team.
- Gap-round answers: pre-flight ownership = team recommendation adopted (runtime executes, HUD visualizes; zero-button v1); notifications yes, **per-event opt-in via HUD config YAML**; heartbeats = cheap live tests fine, **never mocked/simulated/cached**; keep-it-open bar = ALL of complete/reliable/self-updating/glanceable (named failure modes of the April HUD); local server approved, its readiness itself a pre-flight item, plus the **pre-flight contract** (verbatim principle): *"If preflight/heartbeats clear, and the runtime falters due to missing or bad connectivity etc., the preflight failed its job."*

## B. Comparables research digest (2026-07-11)

- **LangGraph Studio / LangSmith**: graph-as-map with click-through node state snapshots; Trace Mode embeds live traces; drill-down model run → node → LLM call → token/latency. Custom dashboards use top-row metric cards with thresholds. (Fleet-scale 2026 features not relevant to a solo HUD.)
- **Converged agent-ops idioms** (Langfuse, AgentOps, Weave, Braintrust): waterfall/timeline with nested spans as universal drill-down; per-trace token+cost rolled to session totals; green/amber/red at span level with error badges bubbling up.
- **Mission-control patterns to steal**: GitHub Actions/Buildkite vertical step list with per-step state icon + running duration timer + streaming log for the active step; **aviation dark-cockpit** (nominal = dim, anomalies bright); persistent **annunciator strip** for the single blocking condition; NASA Open MCT status hierarchy (summary row → tiles → drill).
- **Pre-flight/heartbeat precedents**: status-page gradations (operational/degraded/down per dependency); staleness as first-class ("last updated Xs ago", missed-heartbeat is its own alarm distinct from failing); color+shape+symbol, never color alone.
- **Avoid**: trace-waterfall re-implementation (link to LangSmith), eval/drift panels, fleet views, manual status entry, color-only encoding, unbounded auto-refresh without a stale indicator.

## C. Health-strip fetchability (verified 2026-07)

| Signal | Verdict | Mechanism |
|---|---|---|
| OpenAI usage/costs | FETCHABLE | `GET /v1/organization/usage/*` + `GET /v1/organization/costs` (daily buckets) — requires a separate **Admin API key**, not the inference key |
| OpenAI live rate/quota gauge | FREE | `x-ratelimit-remaining-{tokens,requests}` / `x-ratelimit-reset-*` headers on calls already being made |
| OpenAI prepaid credit balance | NOT fetchable | no official endpoint (legacy `credit_grants` deprecated) — derive from Costs API or manual entry |
| Gamma credits | PARTIAL | `credits: {deducted, remaining}` returned on `GET /v1.0/generations/{id}` — authoritative `remaining` piggybacks every generation poll; between polls show last-seen + staleness stamp |

## D. Prior-asset inventory (for the architecture tier decision)

- `scripts/utilities/run_hud.py` (1,466 lines): `collect_hud_data()` returns a plain dict; ten `_render_*` functions; CSS/JS string constants — layers cleanly separable. ~98 passing pins across `tests/test_run_hud.py` + `tests/test_progress_map.py`; 4 failures (2 stale pins, 2 environment-pollution — no `runs_root` injection seam). Known traps: 525KB `run.json` fully parsed for two fields (mtime-gate it); `_query_active_run_id` silent wrong-run fallback; live LangSmith call inside data collection; stale watch-mode docstring.
- `hud_per_step_summary.py` urgency auto-expand contract is good — carry it forward.
- Governance: `run_hud.py`, `progress_map.py`, `tests/test_run_hud.py`, `tests/test_progress_map.py` in `block_mode_trigger_paths` (pipeline-manifest:63-67).
- Party plan (7-voice, 2026-07-11): `_bmad-output/planning-artifacts/hud-revival-party-assessment-and-plan-2026-07-11.md` — adopted workflow chain, L1/L2/L3 evidence strategy, projection-contract direction.

## E. Notification config sketch (starting point for architecture)

```yaml
# hud-config.yaml (illustrative)
notifications:
  batch_pause_resumed: { enabled: true,  sound: true }
  paused_at_gate:      { enabled: true,  sound: true }
  paused_at_error:     { enabled: true,  sound: true }
  health_threshold:    { enabled: false, sound: false }
staleness_budget_seconds: 5
```

## F. Review amendments (2026-07-11) + adjacent need

- Phone push promoted to v1; new **run-stalled watchdog** event class (no progress within budget while nominally in-flight). Quota/credit sufficiency joined the falter-surface (proxies allowed, honest confidence display, never false green).
- **Adjacent need (not HUD v1 scope, design hint for architecture):** the operator wants stall notifications for **dev runs** too (long dev-auto/test sessions while AFK). Design the notifier as a small shared service the HUD consumes, so a dev-side producer can reuse it later without touching the HUD.
