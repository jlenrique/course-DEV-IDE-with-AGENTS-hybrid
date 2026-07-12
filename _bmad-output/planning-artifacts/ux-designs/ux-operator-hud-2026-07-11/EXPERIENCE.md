---
name: Operator HUD — Flight Deck
status: final
created: 2026-07-11
updated: 2026-07-11
sources:
  - _bmad-output/planning-artifacts/briefs/brief-operator-hud-revival-2026-07-11/brief.md
  - _bmad-output/planning-artifacts/briefs/brief-operator-hud-revival-2026-07-11/addendum.md
  - _bmad-output/planning-artifacts/hud-revival-party-assessment-and-plan-2026-07-11.md
---

# Operator HUD — Experience Spine

> Paired with `DESIGN.md` (visual identity — token references `{…}` resolve there). Designed against the real run-dir fixtures of trial `22b27500-6e67-4dd7-8308-fd89defe3d99` (`state/config/runs/…`), which carries all three pause flavors. Spines win on conflict with any mock.

## Foundation

Single always-on browser page on a dedicated second monitor, locally served from the runtime session, self-updating (poll-first; transport detail is architecture's). One solo operator (the HIL), one active run, hours-long. **Read-only, zero-button**: the conversational Marcus-SPOC surface is the only place decisions happen; the HUD is the instrument panel beside it. No UI system — hand-rolled HTML/CSS continuous with the April HUD's render shell; `DESIGN.md` is the visual identity reference.

The page binds to one `trial_id` for its lifetime and displays that binding in the identity header. It renders what the runtime's operator-surface projection says — never what it infers. If the projection doesn't say it, the HUD doesn't show it.

## Information Architecture

One surface — the flight deck — organized as five fixed zones, top to bottom. "Navigation" is drill-down disclosure inside zones, never page changes.

| Zone | Position | Job | Drill-down |
|---|---|---|---|
| Annunciator strip | Full-width top | The single current blocking condition (or quiet "in flight") | none — it *is* the summary |
| Identity header | Below annunciator | Which run, which lesson, preset, envelope status badge, modality chips (BATCH / DETECTIVE / styleguide), notifications chip, elapsed, freshness meter | none |
| Health strip | One row of tiles | Token burn, run cost vs budget, platform credit/quota per dependency (OpenAI, Gamma, ElevenLabs, Kling, Descript, LangSmith, LiteLLM), each with staleness stamp | tile expands to source-of-reading + confidence + history-this-run |
| Main deck — you-are-here map (left) + context panel (right) | Two columns | Left: two-stage step map. Right: whatever the moment demands — pre-flight board, current-step briefing, gate/error/batch briefing | every map node expands; every specialist chip expands to its briefing |
| State-trace well | Full-width bottom, collapsed | Debugger-like read-only feed of app-state changes and Marcus↔specialist traffic | expand; newest at bottom |

The five-second rule is a layout law: run state (badge), blocking condition (annunciator), and next action (command block in the context panel) all sit above the fold at 1440×900 — the full five-second band is defined in `DESIGN.md.Layout & Spacing` (annunciator, header, health strip, active map node, next-action block).

→ Composition reference: `mockups/flight-deck-in-flight.html` — nominal glance; `mockups/flight-deck-paused-at-gate.html` — G4A master caution + command block; `mockups/flight-deck-preflight.html` — phase 01/02 board + STALE veil exemplar. Spine wins on conflict.

## The Two-Stage You-Are-Here Map

The map renders the run's own shape, not a hardcoded step list.

- **Stage 1 — Intake & planning** (pre-ratification): the eight manifest steps from `directive-composer` through `g0-ratify-gate` (gates G0E, G0R). Rendered first, as its own titled group ("PLANNING").
- **Stage 2 — Ratified workflow**: after lesson-plan + workflow ratification, the ratified workflow's `hud_tracked` nodes (01 … 15 plus terminal leaves like 07W), with their gate codes. Until ratification, stage 2 renders as a single dim placeholder row ("workflow pends ratification — N steps will appear here"); after ratification it expands to the real node list. The map never invents steps that aren't ratified yet.

Node row anatomy: status marker (shape+symbol per `DESIGN.md`), node ID (`{typography.mono}`), label, gate badge when the node is a gate, duration-so-far on the active node. **Urgency auto-expand contract (carried forward verbatim from `hud_per_step_summary.py`): a step's detail block renders expanded when `is_current OR conditions present OR blockers present`; auto-expanded state wins over any remembered collapsed state.** Expanded detail shows the step's locked-artifact summary fields (or "no locked artifact yet"), conditions, blockers, and a `pack_version_mismatch` flag when present.

Progress numerals ("Step 33 / 47") use the node-walk index the runtime reports — the HUD never counts steps itself.

## Voice and Tone

Cockpit terse. Every sentence is a reading, not a narration. Envelope status strings render **verbatim** (`paused-at-gate`, `waiting_for_provider_batch`) — the vocabulary the runtime, runbook, and CLI share is the vocabulary the HUD speaks.

| Do | Don't |
|---|---|
| "PAUSED AT GATE G4A — voice selection awaits your verdict" | "Almost there! Marcus needs your input 🎉" |
| "STALE · last good 14:32:07 (94s ago)" | "Data may be out of date" |
| "quota reading: proxy (derived from rate-limit headers)" | A green checkmark over a guess |
| "UNRECOGNIZED STATUS 'archived' — envelope vocabulary v1 does not know this value" | Coercing an unknown status to the nearest known one |
| "batch parked at provider · poll `trial resume-batch` when notified" | "Error: waiting" (a healthy wait is not an error) |
| Numbers with units and ages: "$0.44 · no cap · 12s ago" | Bare numbers |

## Component Patterns

Behavioral. Visual specs live in `DESIGN.md.Components`.

| Component | Use | Behavioral rules |
|---|---|---|
| Annunciator strip | Top of page, always | Shows exactly one condition — the highest-severity current blocker: paused-at-error/failed > paused-at-gate > waiting_for_provider_batch > health threshold crossed > stale feed > nominal. Changes announce via `aria-live="polite"` and a one-time 300ms luminance step (no blinking). Nominal text: "IN FLIGHT — {node_id} · {node label}". |
| Status badge | Identity header | Envelope status verbatim, uppercase, with paired symbol. Never truncated, never paraphrased. |
| Modality chip | Identity header | BATCH, DETECTIVE, and styleguide slug — all read from the projection, which sources them from `run.json` `llm_execution_mode`, the detective disposition sidecar, and `directive.yaml` `gamma_settings[].styleguide` respectively (the HUD never reads run artifacts directly — zero-lie rule 1). All three always render; activation is the signal (filled vs hollow dot). Chip expands to the provenance of the reading. |
| Health tile | Health strip | Label, value, sub-line, mandatory staleness stamp. Credit/quota tiles carry a confidence tag: `direct` (fetched balance, e.g. Gamma `credits.remaining`), `proxy` (derived — OpenAI rate-limit headers, Costs API spend), `unknown` (renders idle slate, never green). Threshold crossed → amber ring + ⚠ and (if enabled) fires the `health_threshold` notification. Feed dead past its staleness budget → stale veil. |
| Pre-flight check row | Context panel, phases 01–02 | One row per readiness item, each rendering as the runtime tests it (○ → ◐ → ✓/✕). A failed row auto-expands with the failure output and stays failed — pre-flight rows never reset silently. |
| Heartbeat row | Pre-flight phase 02 | Dependency name, real-call latency, quota/credit reading with confidence tag. A heartbeat that cannot verify sufficiency shows `proxy`/`unknown` — the row can pass connectivity yet flag sufficiency separately. |
| Map node | You-are-here map | See §Two-Stage Map. Click/tap anywhere on the row toggles its detail disclosure. Gate nodes show their gate badge permanently — the operator learns where pauses live before reaching them. |
| Current-step briefing | Context panel when `in-flight` (walking) | Reuses the briefing-card anatomy with the active-cyan left border. Contents: node ID + label, duration-so-far, locked-artifact summary fields (or "no locked artifact yet"), conditions and blockers when present. Auto-expanded per the urgency contract. |
| Gate briefing card | Context panel when `paused-at-gate` | Contents in fixed order: (1) gate ID + `gate_focus` + `operator_prompt`; (2) the decision data — drafted proposal with confidence + rationale; (3) **artifacts under judgment inline**: G2B variant thumbnails (PNG per variant with `display_title`), G4A voice rows (name, characteristics, sample link), evidence excerpts with file paths; (4) the command block. Renders within one screen-height where possible; artifacts beyond the first three collapse behind disclosure. |
| Error briefing card | Context panel when `paused-at-error` | `paused_error_tag`, the `error-pause.json` `message` verbatim, `node_id` + walk index, re-entry point (`reenter_at_node`), then the command block (recover command). Red left border. |
| Batch briefing card | Context panel when `waiting_for_provider_batch` | `waiting_batch_id`, time parked, expected mechanics ("LiteLLM provider batch; resume polls the batch"), command block (`trial resume-batch …`). Violet left border — calm, not alarming. |
| Deliverables summary | Context panel when `completed` | Reuses the briefing-card anatomy with a dim-green left border. Contents: one row per export produced (deck export, audio manifest, workbook.md/.docx, Descript-ready bundle) as path/link, then the final cost line from the cost report. |
| Failure briefing | Context panel when `failed` | Reuses the error briefing card (red left border). Contents: last gate crossed, failure message verbatim, LangSmith trace link, and the recovery command if the projection supplies one — else "no automated recovery — see SPOC" plainly. |
| Specialist chip | Under the map, one chip per roster member active in this run | Chip = monogram + status ring + corner glyph (▶ active now, ✓ done, ⚠ degraded/retrying, ⏸ awaiting operator, ○ not yet reached). Expands to a briefing: current/last activity, node it serves, model in use (from cost report per-agent breakdown), last artifact produced (path), tokens/cost attributed. |
| Command block | Inside any briefing with a next action | Renders the **exact command string the runtime projection supplies** — the HUD never composes or edits commands (zero-lie applies to actions too). Fully selectable text; one command per block; the decision-card digest is already in it. |
| State-trace well | Bottom | Append-only mono feed: state transitions, gate opens/closes, specialist dispatch/return, artifact writes. Newest last; auto-scroll only while already at bottom. Empty: "no events yet" in dim ink. Read-only; no filtering UI in v1 beyond the disclosure itself. |
| Notification toast | Overlay, top-right | On-HUD visual channel for enabled event classes; persists until the condition clears (it mirrors the annunciator, never replaces it). Optional sound per config. |

## State Patterns

The envelope's canonical seven statuses, each distinct at a glance (success criterion 1); `in-flight` appears twice because its pre-flight and walking phases render differently. The brief's criterion enumerates six; the envelope model (`production_trial_envelope.py`) defines seven — `registered` is included here under the brief's own "every envelope status" clause.

| Envelope status | Annunciator | Context panel | Next action shown |
|---|---|---|---|
| `registered` | idle slate — "REGISTERED — awaiting pre-flight" | pre-flight board, all rows pending | none yet |
| `in-flight` (pre-flight running) | quiet — "PRE-FLIGHT IN PROGRESS" | pre-flight board rendering checks as tested, then heartbeats | none — watch |
| `in-flight` (walking) | quiet — "IN FLIGHT — {node}" | current-step briefing (auto-expanded per urgency contract) | none — watch |
| `paused-at-gate` | **amber master caution** — "PAUSED AT GATE {gate_id}" + time-since-pause | gate briefing card | `gate decide …` command block |
| `paused-at-error` | **red** — "PAUSED AT ERROR — {paused_error_tag}" + time-since-pause | error briefing card | recover command block |
| `waiting_for_provider_batch` | **violet** — "PARKED — PROVIDER BATCH {waiting_batch_id}" + time parked | batch briefing card | `trial resume-batch …` command block |
| `completed` | dim green — "LANDED — completed {completed_at}" | deliverables summary: exports produced (deck, audio, workbook, Descript-ready bundle) with paths; final cost line | none — links to deliverables |
| `failed` | **red, steady** — "FAILED — {reason tag}" | failure briefing: last gate crossed, error message, LangSmith trace link | whatever recovery command the projection supplies, else "no automated recovery — see SPOC" |

Panel-level states, independent of envelope status:

| State | Treatment |
|---|---|
| No active run | Whole deck idle slate: "NO ACTIVE RUN — HUD bound to none. Start a trial to begin pre-flight." No stale data from previous runs is shown, ever. |
| Binding — awaiting first snapshot | HUD has bound to a trial but no projection snapshot has arrived yet: idle slate "BINDING — {trial_id} · awaiting first snapshot". No data rendered until the first snapshot lands. |
| Unrecognized status / artifact | Renders literally as UNRECOGNIZED in idle slate with the raw value quoted and the schema version that failed to match. Never coerced, never hidden (zero-lie). |
| Run identity uncertain | If active-run resolution is ambiguous or the bound `trial_id` mismatches what the projection reports, the deck veils entirely: "RUN IDENTITY UNCERTAIN — refusing to render." The April HUD's silent wrong-run fallback is explicitly dead. |
| Tile stale (feed older than its staleness budget) | Stale veil per `DESIGN.md`: dashed amber border, content dimmed, "STALE · last good {t}" stamp. Value remains legible — old truth labeled old, never erased into a spinner. |
| Feed lost (poll failing) | Annunciator escalates: "HUD FEED LOST — {t}s since last snapshot"; every tile veils. The page keeps rendering the last snapshot under veils. |
| Notification config unreadable | Notifications chip in header shows ⚠ "config unreadable — defaults active"; HUD keeps flying. |

## Zero-Lie & Staleness Contract

Behavioral restatement of the brief's binding principle, as testable rules:

1. Every zone renders from the runtime-owned projection; the HUD performs no inference, no fallback resolution, and composes no command strings.
2. Every displayed value carries a timestamp; every tile displays age; each feed has a staleness budget (default **5s** for run state, 60s for health tiles [ASSUMPTION — thresholds delegated to team, operator reviews at UX gate]); exceeding it flips the stale veil.
3. Unknown ≠ bad ≠ stale — three distinct renderings (idle slate UNRECOGNIZED / red error / amber veil).
4. A quota/credit reading may claim green only with `direct` or `proxy` confidence attached; `unknown` never renders green.
5. Missed-heartbeat is its own alarm, distinct from a failing heartbeat.

## Notifications

Per-event-class opt-in via `hud-config.yaml`. Channels: on-HUD toast + optional sound + phone push (mechanism selected in architecture). Email/webhook OUT of v1.

| Event class | Fires when | Default [ASSUMPTION — operator reviews at UX gate] | Copy pattern |
|---|---|---|---|
| `paused_at_gate` | envelope → `paused-at-gate` | on · sound · push | "Gate {gate_id} awaits your verdict — {lesson} · parked {t}" |
| `paused_at_error` | envelope → `paused-at-error` | on · sound · push | "Run paused at error {tag} — recoverable, see HUD" |
| `batch_pause_resumed` | provider batch completes and run resumes | on · sound · no push | "Batch landed — run resumed at {node}" |
| `health_threshold` | any health tile crosses its configured threshold | on-HUD only | "{tile}: {value} crossed {threshold}" |
| `run_stalled` | watchdog: no projection progress within budget while nominally `in-flight` (default budget 10 min [ASSUMPTION]) | on · sound · push | "Run quiet {t} at {node} — nominally in flight; worth a look" |

The stall watchdog is the "AFK thinking everything is purring" guard. Notifications never carry verdict affordances — the phone push tells the operator to come look, nothing more. (Architecture note per brief addendum §F: notifier is a small shared service the HUD consumes, reusable by a future dev-side producer.)

## Interaction Primitives

The entire interactivity budget, exhaustively:

- **Disclosure** — click/tap toggles detail on map nodes, tiles, chips, briefing artifact lists, the state-trace well. Disclosure state persists across self-refresh; the urgency auto-expand contract overrides remembered collapse.
- **Text selection** — everything is selectable; command blocks are the designed selection target.
- **Links out** — LangSmith trace, artifact file paths, deliverable exports, sample-audio URLs. Links open outside the HUD; the HUD itself never navigates.
- **Scroll** — page and well scrolling only.

**Banned:** buttons, forms, inputs, toggles, verdict affordances of any kind, drag, keyboard shortcuts that mutate anything, browser-refresh dependence (the page self-updates), modal dialogs.

## Accessibility Floor

Behavioral. Visual contrast floors and the deliberate nominal-dim exemption live in `DESIGN.md.Colors`.

- Color never carries meaning alone — every status pairs shape + symbol (binding from brief; also the color-blind floor).
- Annunciator changes announce via `aria-live="polite"`; pause-class changes via `aria-live="assertive"`. All zones are landmarks; disclosure elements are native `<details>` — keyboard-operable for free, logical tab order top-to-bottom.
- Reduced-motion: freshness sweep and luminance step suppressed; state changes render instantly.
- Text zoom to 125% must keep the five-second band (annunciator/header/health/active node/command block) above the fold at 1440×900.
- Sound is always optional and per-event (config), never the sole channel for anything.

## Inspiration & Anti-patterns

Digest of the brief's comparables research (addendum §B), as adopted or rejected:

- **Lifted — aviation dark cockpit + annunciator**: nominal dim, anomaly bright, one master-caution surface. The organizing metaphor.
- **Lifted — GitHub Actions/Buildkite step list**: vertical step map with per-step state icon and running duration; streaming detail for the active step.
- **Lifted — NASA Open MCT hierarchy**: summary row → tiles → drill-down; no information requires more than one drill.
- **Lifted — status-page gradations**: per-dependency operational/degraded/down with staleness as first-class; missed-heartbeat as its own alarm.
- **Lifted — LangGraph Studio**: graph-as-map with click-through node state. But link out for trace depth.
- **Rejected — trace-waterfall re-implementation**: LangSmith already does it; the HUD links to the trace and stops.
- **Rejected — eval/drift panels, fleet views, historical browsing, Dev-Cycle/M5 panels**: ruled out by brief scope; the April HUD's Dev Cycle tab and M5 relic panel do not return.
- **Rejected — manual status entry and unbounded auto-refresh without stale indication**: both named April failure modes.

## Key Flows

Protagonist: **Juan**, the solo operator/HIL, HUD on the right-hand monitor, Marcus-SPOC conversation on the left.

### Flow 1 — Pre-flight to spawn (Juan, 9:10am, starting a production trial)

1. Juan starts a runtime instance from the SPOC surface. The HUD (already open, "NO ACTIVE RUN") binds to the new trial and the annunciator reads "PRE-FLIGHT IN PROGRESS".
2. The context panel renders the checklist row by row as the runtime tests: environment, settings, databases, LiteLLM, the HUD's own server — each ○ → ◐ → ✓ in real time.
3. Phase 02 heartbeats follow: one row per dependency — OpenAI, Gamma, ElevenLabs, Kling, Descript, LangSmith — each a real call with latency and a quota/credit reading tagged `direct` or `proxy`.
4. The Gamma row shows `credits: 412 remaining · direct · 2s ago`. The OpenAI row shows `quota: proxy (rate-limit headers) · ok`.
5. **Climax:** the last row turns green, the annunciator flips to "IN FLIGHT — 01 · Activation + Preflight", stage 1 of the map lights its first node cyan, and Marcus-SPOC greets Juan on the left monitor. The jet is off the ground and every instrument agreed before it moved.

Failure: the LiteLLM row fails → row auto-expands with the failure output, annunciator goes red "PRE-FLIGHT FAILED — litellm", SPOC does not spawn (runtime gates it, not the HUD), and the panel holds the failure until a new pre-flight begins.

### Flow 2 — The five-second glance (Juan, mid-conversation, an hour in)

1. Juan is deep in a SPOC exchange about lesson framing; he flicks his eyes right.
2. Annunciator: quiet "IN FLIGHT — 07 · Gary Dispatch + Export". Header: cost "$0.31 · no cap · 8s ago". Gary's chip shows ▶; map shows Step 21/47 with duration ticking.
3. **Climax:** within five seconds he's back in the conversation, confident nothing needs him. The glance cost nothing because nominal is dim — there was nothing bright to investigate.

Failure: any tile past its staleness budget shows the amber veil instead — Juan knows the *feed* is the problem, not the run, and the annunciator says which.

### Flow 3 — Gate verdict (Juan, 11:40am, G4A voice selection)

1. A sound fires (per config) and his phone buzzes; the annunciator has gone amber: "PAUSED AT GATE G4A — voice selection awaits your verdict · parked 0:12".
2. The map shows node 11-gate glowing amber; the context panel is the gate briefing: `gate_focus: voice_selection`, the operator prompt, and the voice options inline — names, characteristics, sample links.
3. Juan clicks two samples, decides, and reads the drafted proposal line ("proposal: approve · confidence 0.72").
4. The command block shows the exact verdict command, digest pre-filled: `gate decide --trial-id 22b27500… --gate-id G4A --verb approve --card-id … --decision-card-digest … --operator-id juanl`.
5. **Climax:** he selects the block, pastes it into the SPOC surface, and watches the annunciator fall quiet again — "IN FLIGHT — 12 · ElevenLabs Audio Generation". He never touched the HUD to act; the panel and the stick stayed different instruments.

Failure: he edits the verb before pasting and the digest no longer matches → the runtime rejects it on the SPOC side; the HUD still shows the same valid command block (its truth never depended on what he typed).

### Flow 4 — Error pause while AFK (Juan, lunch, node 08)

1. At node 08 Irene hits a narration-figure contradiction; the envelope flips `paused-at-error`. Juan's phone: "Run paused at error irene.figure-contradiction — recoverable, see HUD."
2. Back at the desk: annunciator red, "PAUSED AT ERROR — irene.figure-contradiction · parked 9:41". Error briefing shows the `error-pause.json` message verbatim ("slide-05 narration figures not present in perceived authority: ['percent:10','percent:90']"), node 08 · walk index 33, re-entry point `reenter_at_node: 08`.
3. He expands Irene's specialist chip — her briefing shows the Pass-2 dispatch that raised the contradiction and the last artifact she wrote — then glances at the state-trace well, where the dispatch/return sequence confirms nothing else moved after the pause.
4. The command block carries the recover command the projection supplied.
5. **Climax:** Juan reads the message, pastes the recover command into SPOC, and the map re-lights at node 08 — no run-dir spelunking, no guessing which artifact to open. The error told him exactly what the runtime knew, when it knew it.

Failure: the error is one the projection marks non-recoverable → the briefing says so plainly and points to the SPOC conversation and the LangSmith trace instead of offering a command.

### Flow 5 — Overnight batch park (Juan, 11pm → 7am, batch mode run)

1. The run enters `waiting_for_provider_batch`. Annunciator goes violet — "PARKED — PROVIDER BATCH batch_abc123 · parked 0:03". The BATCH modality chip has been filled since launch, so nothing about this is a surprise.
2. Juan reads the batch briefing (batch ID, resume mechanics, `trial resume-batch` command block) and goes to bed — violet means nobody owes anybody a verdict.
3. At 6:52am the batch lands and the run resumes; his phone (batch_pause_resumed, if enabled) and the HUD both say "Batch landed — run resumed at 07G".
4. **Climax:** morning glance: annunciator quiet, map advanced four nodes overnight, cost tile up by the batch's amount with a fresh stamp. The run flew unattended and the panel can prove it.

Failure: the batch stalls past the watchdog budget → `run_stalled` fires ("Run quiet 6h at 07G — nominally in flight; worth a look"); the annunciator escalates to amber with the stall reading. Violet never silently becomes forever.

### Flow 6 — Landing (Juan, end of trial)

1. Node 15 completes; envelope → `completed`. Annunciator: dim green "LANDED — completed 14:02:11".
2. Context panel becomes the deliverables summary: deck export, audio manifest, workbook.md/.docx, Descript-ready bundle — each a path/link — and the final cost line from the cost report.
3. **Climax:** Juan completes the trial having used only HUD + SPOC — the keep-it-open witness (success criterion 5) is the run itself.

Failure: the run ends `failed` instead — annunciator steady red "FAILED — {reason tag}", the failure briefing shows last gate crossed, the message verbatim, and the LangSmith trace link; if the projection supplies no recovery command the briefing says "no automated recovery — see SPOC" and stops. A failed landing still tells the whole truth from the panel.

## Projection Demands (handoff to architecture)

What each zone requires the runtime-owned operator-surface projection to carry — the UX-side half of the contract; architecture owns its schema, versioning, and dual-walk write points:

- envelope status (canonical seven) + pause metadata (`paused_gate`, `paused_error_tag`, `waiting_batch_id`) + timestamps for every reading
- run identity (trial_id, lesson/corpus, preset, operator_id) — HUD refuses to render on mismatch
- pre-flight/heartbeat item list with per-item state, output, latency, quota reading + confidence tag
- two-stage step list (stage-1 manifest steps; stage-2 ratified `hud_tracked` nodes) with per-step status, conditions, blockers, locked-artifact summary, walk index
- active decision card (full card incl. pick context and digest) and the **exact next-action command string** per pause class
- specialist roster activity (per-agent current node, status, model, last artifact, cost attribution)
- health readings (token burn, cost vs budget_status, per-platform credit/quota + confidence, LangSmith trace URL) including per-reading history for this run (feeds the health-tile drill-down)
- modality readings (llm_execution_mode, detective disposition, styleguide + provenance)
- state-trace events (append-only)
- notification config echo + watchdog progress heartbeat
