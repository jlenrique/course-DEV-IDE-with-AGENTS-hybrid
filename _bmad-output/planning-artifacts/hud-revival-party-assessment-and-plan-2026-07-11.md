# Operator HUD Revival — Party Assessment & Adopted Plan (2026-07-11)

**Gate:** planning green-light (operator-directed pivot from workbook customization to the HUD)
**Party:** full-spawn subagent mode, tailored roster — core four (Winston / John / Amelia / Murat) + Sally (UX, task-critical add-on) + **anti-consensus club contrarians Splinter (consensus challenger) + Level (claim checker)** per explicit operator mandate for contrarian inputs (v6.10 machinery).
**Votes:** 5× GO-WITH-AMENDMENTS (Winston, John, Amelia, Murat, Sally) + 2 contrarian briefs that materially changed the plan (see §4).
**Stop contract honored:** workflow adopted + assessment + plan only — no implementation opened.

---

## 1. Due-diligence assessment (verified, with party corrections)

- The HUD (`scripts/utilities/run_hud.py`, 1,466 lines + `hud_data_sources.py` + `hud_per_step_summary.py` + `progress_map.py`) was **closed 2026-04-28** (Slab 6.5) as a static-HTML generator with a pull-based watch loop. It has been **dark for ~2.5 months** while the runtime moved: it reads a dead surface (`source-bundles/gates/gate-*.yaml` — **zero such files on disk**; newest bundle 2026-04-21) and is blind to the current `state/config/runs/<uuid>/` reality (`decision-card-G*.json`, `run_summary.yaml`, `error-pause.json`, `resume-command.json`).
- **Sharper mechanism than briefed (Level):** `hud_data_sources.py:102-115` takes status from `trial-start.json` FIRST, `run.json` only as fallback — so a completed run displays "registered-offline". The envelope's pause vocabulary (`paused-at-gate` / `paused-at-error` / `waiting_for_provider_batch`, `production_trial_envelope.py`) appears nowhere in the HUD (zero grep hits).
- **CLAIM CORRECTED — "17 ambient test failures" is stale/mis-scoped.** Actual (run live at this gate, twice): **4 failed / 98 passed** across `tests/test_run_hud.py` + `tests/test_progress_map.py` — 1-2 stale pins (renamed `_scan_bundle_artifacts` seam; `WAVE_LABELS` missing 6 live epic IDs) + 2 environment-pollution failures (the "empty run" hermetic test renders the operator's real latest run because `collect_hud_data` has no `runs_root` injection seam). The STATE-OF-THE-APP:56 "17" was a 2026-06-24 whole-layer count; treat it as superseded.
- **CLAIM CORRECTED — the code is not a liability-shaped blob (Amelia, from reading it):** `collect_hud_data()` returns a plain dict; rendering is ten `_render_*` functions; the data layer is cleanly separable. Minimal retarget ≈ 1–2 days; served/live variant +2–3 days; ground-up rebuild would torch ~98 passing pins for aesthetics.
- **CLAIM CHALLENGED — "essential" is asserted, not evidenced (Level):** real usage logged 2026-04-19 ("HUD launched — 33 steps confirmed") and mid-trial operator feedback existed; but `reports/run-hud.html` was last written 2026-04-28 and **~269 run dirs have been created since May 1 with zero HUD regenerations**. The concierge/braid/enhanced-VO/batch arcs all ran HIL through the conversational SPOC surface with the HUD dark. Disposition in §3.
- No push bus exists anywhere (confirmed); `narrate_gate` in `marcus_spoc.py` already handles gate decisions conversationally (confirmed); `run_hud.py`/`progress_map.py`/their tests are `block_mode_trigger_paths` (pipeline-manifest:63-67) — all HUD work is **pipeline-lockstep-regime governed** (dev reads the regime doc at T1; manifest edits are Tier-2 party-gated).
- Traps on record (Amelia): `run.json` is ~525KB and gets fully parsed for two fields (mtime-gate it); `_query_active_run_id` silently falls back on coordination.db drift (can show the WRONG RUN with no indication); `read_adhoc_summary` makes a live LangSmith network call inside data collection (render-blocker if ever served); stale docstring claims watch mode is dormant while a live loop exists.

## 2. State-of-the-app context

Marcus-SPOC runtime is the product (binding guardrail). Recent closes: S7 Phase-2/S8/Six-Mine/Batch-v1, Agentic Research Foundations R0–R7, Workbook Research Products W0–W4, TRAIL trio, BMAD harness v6.10.0 (witnessed 5/5). Live frontier before this pivot: workbook artifact customization + fenced residuals + HAI/PHS ingestion. Runs pause at gates (DecisionCards over cli/http/mcp), on errors, and for provider batches — hours-long runs the operator leaves and returns to. The deferred-work queue holds 9 evidenced items (phantom-framing trio strongest).

## 3. Product definition (the party's synthesis — binding for the brief)

**The HUD is the ambient, read-only, glanceable companion to the conversational SPOC surface — never a second decision surface.** Marcus-SPOC (`narrate_gate` + gate CLI) remains the only actor. The HUD's #1 job (John's JTBD ranking): *"why is my run stopped and what exactly do I do next"* — rendered as state / why / what-I'm-judging / **next-action as a copy-paste command with the decision-card digest baked in** (kills the runbook's documented `digest_mismatch` surprise). Jobs #2-#4: healthy-vs-wedged (with **staleness honesty** — "snapshot as of HH:MM:SS" + time-since-pause as a first-class element), produced-so-far glance, cost-vs-soft-cap one-liner. Explicitly OUT of the HIL surface: Dev Cycle tab, M5 relic panel, historical run browsing, cost engineering, any interactive verdict affordance, any push transport in v1.

**Disposition of Level's "essential" challenge:** the operator has explicitly directed this arc, which settles *whether*; Level's evidence reshapes *what* — the brief MUST carry a usage-witness success criterion (John's: "operator completes a full trial using only HUD + verdict CLI, never opening run-dir files by hand; v1 pays for itself in the very next production trial or we cut deeper") plus the **zero-lie rule** (the HUD never contradicts the envelope; unrecognized states render as unrecognized, never as garbage or stale truth).

## 4. Collisions and how they resolved

| Collision | Resolution |
|---|---|
| **Rebuild thin viewer (Splinter) vs retarget (Amelia, from code)** | **Retarget the data layer, keep the render shell** — Amelia's evidence (separable layers, ~98 green pins, 1–2 day tier-a) beats sunk-cost framing. But Splinter's deep point survives via Winston: **the contract is the product** — the data layer becomes a thin consumer of a runtime-owned projection, which is 80% of Splinter's "honest thin view over the envelope". |
| **Full PRD (Winston/Sally) vs lean spec (John/Amelia/Splinter)** | **PRD dropped to a scoped product brief** (majority + proportionality); **UX keeps a full two-spine phase** (Sally's argument stands: this is the surface where a human makes money-spending judgments on hours-long runs — the failure mode is wrong verdicts, not ugliness); **architecture phase is non-negotiable** (all seven agree it's where the load-bearing decisions live). |
| **HUD vs SPOC-as-surface (Splinter's split-brain attack)** | Absorbed as the §3 read-only confession. Any future actionable affordance requires a fresh party gate. |
| **"Essential" premise (Level)** | Operator direction settles the *whether*; usage-witness criterion + next-trial payoff test make the *worth it* falsifiable. |

## 5. ADOPTED WORKFLOW (per bmad-help catalog + party amendments)

1. **`bmad-product-brief`** (lean, scoped) — pins the §3 product definition, JTBD ranking, IN/OUT list, zero-lie rule, usage-witness success criteria. *(replaces full `bmad-prd` — party amendment)*
2. **`bmad-ux`** (v6.8 two-spine: DESIGN.md + EXPERIENCE.md) — moment-based IA (returning / watching / deciding / closing — NOT a panel inventory), designed against **real run-dir fixtures** (run `22b27500…` carries all three pause flavors; no invented mocks). EXPERIENCE.md non-negotiables per Sally §3: answer-first 5-second rule, every-pause-renders-a-next-action, artifacts-under-judgment inline, urgency auto-expand kept, staleness honesty, Dev-Cycle/M5 ruled out.
3. **`bmad-architecture`** (required) — MUST decide: (a) **runtime-owned operator-surface projection contract** — one versioned status document written by the production runner (BOTH walks — standing two-walk gotcha), shared Pydantic model + dual JSON-Schema shape-pins so producer changes fail producer tests; (b) served-vs-static (v1 default: static + mtime/etag-gated 2–5s poll; SSE only as Tier-1 follow-on IF the gate-verdict flow independently justifies a served operator API); (c) retire-path for legacy bundle-gate/coordination.db readers + the silent wrong-run fallback; (d) perf/traps budget (525KB run.json mtime-gating, LangSmith call out of the data path).
4. **`bmad-create-epics-and-stories`** — one epic, few stories; **named stories** (not incidental cleanup): 4-failure test disposition (pre-story gate), manifest-lockstep update, injection-seam fix, M5 panel retirement.
5. **`bmad-check-implementation-readiness`** → **`bmad-sprint-planning`** → gated dev: **formal `bmad-dev-story`** for anything touching the lockstep trigger-path trio; **`bmad-dev-auto` residual class** for the mechanical items (stale pins, panel retirement, seam fix).

**Evidence strategy (Murat, adopted as story ACs):** L1 enum contract test (set-equality against the envelope status vocabulary — plus the reverse tripwire: envelope status-model files added to `block_mode_trigger_paths`); L2 golden run-dir fixtures per pause class + one legacy-shaped dir rendering "unrecognized"; L3 one first-run-stands live witness per pause class as it lands, promoted into the L2 golden set (rewind-recover golden-bundle pattern). DoD per story names its witness set. Risk matrix headline: R1 wrong-but-plausible state during a live paused run (High/High) — mitigated by L1+L2+zero-lie rule.

## 6. Party-machinery note (standing `bmad-party-machinery-check` item)

First real party gate on production work under v6.10: **the machinery behaved — and earned its cost.** Seven independent subagent spawns; every voice ran its own verification; **two briefing claims were refuted by voices running actual code** (the "17 failures" count; the monolith framing), and the **anti-consensus seats materially changed the outcome** (PRD→brief; read-only scope confession; usage-witness criterion) rather than decorating it. Dissent was recorded, not dissolved. Persistent party memory appended at close.

## 7. Next session opens with

`bmad-product-brief` (fresh context window per bmad-help convention), input = §3 of this artifact. Branch: cut `dev/hud-revival-2026-07-11` from master after merging the outstanding residuals branch.
