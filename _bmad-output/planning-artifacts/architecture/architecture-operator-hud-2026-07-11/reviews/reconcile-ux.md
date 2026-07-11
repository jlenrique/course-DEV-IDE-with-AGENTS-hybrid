# Reconcile — UX spines (EXPERIENCE.md + DESIGN.md) vs ARCHITECTURE-SPINE.md

Input: `_bmad-output/planning-artifacts/ux-designs/ux-operator-hud-2026-07-11/EXPERIENCE.md` + `DESIGN.md`
Spine: `_bmad-output/planning-artifacts/architecture/architecture-operator-hud-2026-07-11/ARCHITECTURE-SPINE.md`
Reviewer pass: 2026-07-11 (input-reconciliation).

Note on method: AD-3 incorporates EXPERIENCE §Projection Demands wholesale ("the projection carries everything EXPERIENCE.md §Projection Demands lists"). That blanket reference is a legitimate landing mechanism, so demands are marked LANDED when producible under it — except where the demand has structural consequences the blanket cannot absorb (growth, who-writes-it, lifecycle). Those are called out.

## §Projection Demands (every bullet must be producible under the ADs)

| Demand | Verdict | Notes |
|---|---|---|
| Envelope status (seven) + pause metadata + timestamps per reading | LANDED | AD-5 explicit; Conventions per-section `as_of`. |
| Run identity (trial_id, lesson/corpus, preset, operator_id); refuse on mismatch | LANDED | AD-8 (trial_id binding + REFUSE-TO-RENDER); remaining identity fields via AD-3 blanket. |
| Pre-flight/heartbeat items: state, output, latency, quota + confidence | LANDED | AD-11 explicit, field-for-field. |
| Two-stage step list (manifest steps; ratified `hud_tracked` nodes) w/ status, conditions, blockers, locked-artifact summary, walk index | LANDED | Capability Map row explicit; AD-1/AD-3. |
| Active decision card (full, incl. pick context + digest) + exact next-action command per pause class | LANDED | AD-3 explicit on the command string; card via blanket. |
| Specialist roster activity (per-agent node, status, model, last artifact, cost attribution) | LANDED | Via AD-3 blanket. (Brief-side note: non-agent "specialty services" have no slot — see reconcile-brief.md.) |
| Health readings **including per-reading history for this run** (feeds tile drill-down) | **PARTIAL** | Readings + confidence land (AD-11, Capability Map). The **history-this-run** clause did not: no AD names it, and the Deferred bullet "Projection v2 fields (fleet/**history**…)" is dangerously readable as deferring it — but tile drill-down history is a *v1* EXPERIENCE requirement (Health tile: "expands to … history-this-run"). Worse, it has structural consequences the spine never faces: history + append-only state-trace events inside **one JSON document rewritten wholesale at every `_persist_envelope`** grows without bound over an hours-long run — the same failure family as the 525KB `run.json` trap the spine itself cites in AD-3. No size budget, ring-buffer/trim rule, or sidecar decision exists. |
| Modality readings (llm_execution_mode, detective disposition, styleguide) **+ provenance** | LANDED | Via AD-3 blanket; producer sources them (EXPERIENCE says the projection sources from run.json/sidecar/directive.yaml — consistent with AD-3 keeping consumers off those files). |
| State-trace events (append-only) | LANDED (with the growth caveat above) | Capability Map row 1; AD-3 blanket. |
| **Notification config echo** + watchdog progress heartbeat | **Config echo: DROPPED · heartbeat: LANDED** | Watchdog heartbeat = AD-10 (`seq`, `last_transition_at`). The **config echo** has no path: AD-9 has the *notifier* reading `hud-config.yaml`, but nothing has the *producer* reading it and echoing it into the projection — which the HUD needs for the header notifications chip and the "config unreadable — defaults active" state (EXPERIENCE §State Patterns). Under AD-3 the HUD may read only the projection, so it cannot read `hud-config.yaml` itself; as specified, the chip is unrenderable. Needs either a producer-side echo or an explicit exemption. |

## §Zero-Lie & Staleness Contract

| Rule | Verdict | Notes |
|---|---|---|
| 1. No inference, no fallback resolution, no command composition | LANDED | AD-3, AD-8. |
| 2. Every value timestamped; per-feed staleness budgets (5s state / 60s health [ASSUMPTION]) | LANDED | Conventions `as_of`; budgets live in `hud-config.yaml` (Structural Seed, Deferred [ASSUMPTION] tagging). |
| 3. Unknown ≠ bad ≠ stale — three distinct renderings | LANDED | Data-layer half in AD-4 (UNRECOGNIZED) + staleness support; renderings themselves UX-owned. |
| 4. Quota green only with `direct`/`proxy`; `unknown` never green | LANDED | AD-11, verbatim. |
| 5. **Missed-heartbeat is its own alarm, distinct from a failing heartbeat** | **DROPPED** | Nowhere in the spine. The projection/consumer contract never distinguishes "reading failed" from "reading absent/not reported" — the schema would need an explicit absent-vs-failed encoding (or a per-item expected-cadence field) for the consumer to render this third state. This rule also originated in the brief addendum §B precedents, so it has dropped twice. |

## §Notifications (matrix + [ASSUMPTION] defaults)

| Item | Verdict | Notes |
|---|---|---|
| Five event classes, exact snake_case names | LANDED | AD-9 matches EXPERIENCE names one-for-one; Conventions pin snake_case-per-EXPERIENCE. |
| Per-class channel defaults [ASSUMPTION — operator reviews at UX gate] | CORRECTLY-DEFERRED | Deferred § tags defaults [ASSUMPTION] in `hud-config.yaml`. |
| `run_stalled` budget 10 min [ASSUMPTION] | LANDED | AD-10 default 600s — consistent. |
| Derivation from projection *transitions* (e.g., `batch_pause_resumed` = batch→in-flight edge) | LANDED | AD-9 "derives … from projection transitions"; AD-10 seq gives edge detection. |
| Toast mirrors annunciator, persists until condition clears; sound optional | CORRECTLY-DEFERRED | View behavior; on-HUD channel correctly rendered "from projection state, not from the notifier" (AD-9). |
| Push tells the operator to come look, never carries verdict affordances | LANDED | Implied by AD-9 signature (`title, message, priority`) + AD-6 no-mutation; producible. |

## §State Patterns & lifecycle (architecture-relevant rows)

| Item | Verdict | Notes |
|---|---|---|
| REFUSE-TO-RENDER on identity mismatch/ambiguity | LANDED | AD-8 cites the UX state by name. |
| UNRECOGNIZED status/artifact | LANDED | AD-4, AD-5, AD-13 L2 legacy-dir fixture. |
| BINDING — awaiting first snapshot | LANDED (producible) | Server up before first `_persist_envelope` write; view renders no-data state. |
| **NO ACTIVE RUN — HUD already open before a trial starts, then binds (Flow 1 step 1, §State Patterns)** | **PARTIAL** | AD-7 launches the server *as a child of the runtime session*, bound to one `trial_id` **at launch**. Under that lifecycle the "HUD already open, NO ACTIVE RUN, then binds to the new trial" moment is unreachable — the server doesn't exist until the run's session does, and is never unbound. Either the idle state collapses to the brief post-launch/pre-registration window (then EXPERIENCE Flow 1 should be amended), or a longer-lived HUD page is intended (then AD-7 needs a rebinding story). The spine and the UX spine currently disagree and neither flags it. |
| Feed lost (poll failing) → veil + escalation | LANDED (producible) | Client knows its own last successful poll; producible under AD-6. |
| Notification config unreadable → chip warning | DROPPED (same root as config-echo above) | Unrenderable without the projection echo. |

## DESIGN.md (architecture-relevant)

| Item | Verdict | Notes |
|---|---|---|
| **No-blink rule + poll re-render: disclosure state persists across self-refresh; auto-scroll only while at bottom; everything selectable (command block = the designed selection target); motion limited to freshness sweep + one-time 300ms luminance step** | **DROPPED** | The spine's render model is `render_html(data)` full-page HTML out (AD-12) re-rendered on every ETag 200 (AD-6). A naive full-DOM replacement every 2–5s snapshot **destroys open `<details>` disclosure, mid-copy text selection, and scroll position, and reads as blinking** — violating four EXPERIENCE/DESIGN behavioral rules at once. No AD or Convention addresses the DOM-update strategy (morphdom-style patch, per-zone replacement, or state save/restore across renders). This is the largest UX→architecture gap: it sits exactly at the seam the spine owns (polling render), and it will otherwise be discovered mid-dev. |
| Single dark mode, hand-rolled HTML/CSS continuous with April render shell, no UI system | LANDED | AD-12; Capability Map cites DESIGN tokens. |
| Color+shape+symbol never color alone; contrast floors; nominal-dim exemption | CORRECTLY-DEFERRED | Pure visual identity; no architecture residue. |
| Freshness meter (client-side age readout with sweep) | LANDED (producible) | Client-local clock vs snapshot `as_of`; no server support needed. |
| Tabular-nums, tokens, shapes vocabulary | CORRECTLY-DEFERRED | UX-owned. |
| Reduced-motion suppression | CORRECTLY-DEFERRED | CSS-level; note it interacts with the DOM-update gap above (instant render must still not blink). |

## Tally

LANDED 18 · PARTIAL 2 (health history-this-run + projection growth; NO-ACTIVE-RUN lifecycle contradiction) · DROPPED 3 (notification-config echo [+ its config-unreadable state]; missed-heartbeat-as-own-alarm; DOM-update/no-blink strategy for polling render) · CORRECTLY-DEFERRED 5.
