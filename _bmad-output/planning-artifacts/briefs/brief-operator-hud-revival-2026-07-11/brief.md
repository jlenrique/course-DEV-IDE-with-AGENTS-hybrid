---
title: Operator HUD — Flight Deck for Marcus-SPOC Production Runs
status: draft
created: 2026-07-11
updated: 2026-07-11
---

# Operator HUD — Flight Deck for Marcus-SPOC Production Runs

## Vision

A **read-only flight deck on the operator's second monitor**, alive from the moment a runtime instance starts to the moment the run lands. It renders pre-flight, then tracks the live run moment-by-moment so the HIL's (human-in-the-loop's) decisions are always informed — *"I am actively piloting this jet, mid-flight."* The conversational Marcus-SPOC surface remains the only place decisions are made; the HUD is the instrument panel beside it.

The April 2026 HUD failed for four named reasons: **incomplete, unreliable, not self-updating, hard to read at a glance**. This product is those four failures inverted — and that inversion is the acceptance bar.

## User & moment

One solo operator/HIL, second monitor dedicated to the HUD, running hours-long production trials that pause at gates (DecisionCard verdicts), on errors, and for provider batches. Primary moment: **live piloting** — glancing mid-conversation to confirm state, health, and where the run is. Single active run only; no fleet views, no history browsing.

## The run lifecycle the HUD renders

1. **Pre-flight (Phase 01)** — runtime instance starts; HUD is already up showing "pre-flight in progress" on the you-are-here map. Checklist items render individually as the runtime tests them: hardware/software environment, default settings, databases, LiteLLM, **the HUD's own server**, and every essential readiness measure.
2. **Heartbeats (Phase 02)** — live connectivity tests of every API/LLM/platform dependency, rendered per dependency. Heartbeats are real calls (see Principle 5).

   **PRE-FLIGHT CONTRACT (load-bearing definition):** if pre-flight and heartbeats clear and the runtime then falters on missing or bad connectivity, pre-flight failed its job — coverage is defined as *anything whose absence would make the runtime falter* (the "falter-surface").
3. **Spawn & conversation** — on all-green, Marcus-SPOC spawns; the HUD flips to run tracking.
4. **The walk** — a **two-stage you-are-here map**: the intake/planning steps first; after lesson-plan and workflow ratification, the ratified workflow's own steps. Dark-cockpit posture: nominal is quiet and dim; the active step and any anomaly are the bright things. A persistent **annunciator strip** carries the single current blocking condition (gate awaiting verdict = master caution).
5. **Drill-down everywhere** — each gate expands to a **briefing** (the decision, its data, its DecisionCard); each specialist agent and specialty service is an **icon that expands to a briefing** of its current state; a debugger-like, read-only **state-trace window** shows app-state changes and Marcus↔agent traffic.
6. **Standing instruments** — a **health strip** (token burn, platform credit/subscription status for OpenAI, Gamma, and the other platforms in the run's dependency set, with per-tile "last updated Xs ago" staleness stamps) and **prominent modality indicators**: batch mode, detective mode, selected styleguide.

## Product principles (binding)

1. **Read-only, zero-button.** No verdict affordances, ever; next actions render as copy-paste commands (decision-card digest pre-filled). `[ASSUMPTION: v1 keeps even the pre-flight trigger out of the HUD — the runtime start path executes pre-flight and gates SPOC spawn on it; the HUD only visualizes. Recommended because it keeps read-only pure and pre-flight authoritative whether or not the HUD is open.]`
2. **Zero-lie rule.** The HUD never contradicts the envelope (the run's persisted state carrier); unrecognized states render as "unrecognized," never as garbage or stale truth. Every tile admits its age; a dead feed flips to an explicit STALE state.
3. **Self-updating.** Live, moment-by-moment, no manual refresh — served locally from the runtime session. Local server approved; its readiness is itself a pre-flight item.
4. **Glanceable by design.** Dark-cockpit hierarchy: at-a-glance status + health by default, maximum insight one drill-down away.
5. **No-mocks heartbeats.** Heartbeats and pre-flight checks are real live calls — never mocked, simulated, or cached; cheap paid pings are acceptable.
6. **Configurable notifications.** Per-event-class opt-in/out via a HUD config YAML. Starting set: batch-pause resumed, paused-at-gate, paused-at-error, health-threshold crossed. `[ASSUMPTION: v1 channels are on-HUD visual + optional sound; phone/email parked for v2.]`

## Scope

**IN (v1):** pre-flight + heartbeat visualization; two-stage progress map with drill-down; gate briefings; specialist/service icons with briefings; read-only state-trace window; health strip (token use, platform credits where fetchable — mechanisms in addendum §C); modality indicators; YAML-configured notifications; locally served page.

**OUT (v1):** any interactive affordance beyond copy-paste text; fleet/multi-run views; historical run browsing; phone/email/webhook notifications; full trace-waterfall re-implementation (link out to LangSmith for that depth); eval/drift panels; Dev-Cycle/sprint panels and the M5 relic panel (dev dashboards live elsewhere).

## Success criteria

1. **Complete** — every envelope status and pause class renders distinctly (`paused-at-gate` / `paused-at-error` / `waiting_for_provider_batch` / `in-flight` / `completed` / `failed` — the envelope's canonical status strings); every gate and specialist in the ratified workflow has a briefing; pre-flight covers the full falter-surface (contract above).
2. **Reliable** — zero-lie holds across one full live run; legacy/unknown artifacts render as unrecognized; the HUD never displays the wrong run.
3. **Self-updating** — state changes appear without operator action within the staleness budget shown on the tile.
4. **Glanceable** — run state, blocking condition, and next action legible within five seconds of a glance, never below the fold.
5. **The keep-it-open witness** — the operator keeps the HUD open across the next real production trials *by choice*, and completes a full trial using only HUD + conversational SPOC, never spelunking run-dir files to learn state.

## Constraints & governance

`run_hud.py`, `progress_map.py`, and their tests are pipeline-lockstep `block_mode_trigger_paths` — all dev on them is manifest-regime governed (regime doc at T1; Tier-2 manifest changes party-gated). Architecture phase must deliver the runtime-owned, versioned **operator-surface projection contract** (written by both runner walks; dual shape-pins) so the HUD can never silently drift from the envelope again. Existing assets: the April HUD's data/render layers are cleanly separable with ~98 passing pins — reuse is a tiering decision for the architecture phase, not a constraint here.

## Open questions (for UX + architecture phases)

- Transport detail: SSE vs. short-poll from the local server; the runtime↔HUD process lifecycle (who starts/stops the server). `[ASSUMPTION: poll-first, SSE only if the projection cadence demands it.]`
- Health thresholds and their notification defaults (delegated to team; operator reviews at UX gate).
- Iconography and briefing content per specialist/service (UX phase, designed against real run-dir fixtures).
- Pre-flight item inventory derivation — from `ready_for_trial` scripts + the falter-surface contract (architecture phase).
