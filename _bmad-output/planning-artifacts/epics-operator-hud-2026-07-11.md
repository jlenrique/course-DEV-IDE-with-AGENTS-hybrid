---
stepsCompleted: [1, 2, 3]
inputDocuments:
  - _bmad-output/planning-artifacts/briefs/brief-operator-hud-revival-2026-07-11/brief.md
  - _bmad-output/planning-artifacts/briefs/brief-operator-hud-revival-2026-07-11/addendum.md
  - _bmad-output/planning-artifacts/ux-designs/ux-operator-hud-2026-07-11/DESIGN.md
  - _bmad-output/planning-artifacts/ux-designs/ux-operator-hud-2026-07-11/EXPERIENCE.md
  - _bmad-output/planning-artifacts/architecture/architecture-operator-hud-2026-07-11/ARCHITECTURE-SPINE.md
  - _bmad-output/planning-artifacts/hud-revival-party-assessment-and-plan-2026-07-11.md
status: party-greenlit-with-amendments
greenlight: _bmad-output/planning-artifacts/epic-35-party-greenlight-2026-07-11.md
created: 2026-07-11
---

# Operator HUD v1 — Epic Breakdown (Epic 35)

## Overview

Complete epic and story breakdown for the Operator HUD flight deck, decomposing the operator-amended brief, the approved UX spine pair, and the finalized architecture spine (19 ADs) into implementable stories. One epic per party plan §5.4; stories cut along the adversary-review unit boundaries the spine governs. Requirements source is the brief (PRD replaced by scoped brief — party amendment 2026-07-11). Session target: smallest story chain reaching a live E2E witness run (3 slides, 1 motion video, 1 workbook) with the HUD performing to spec.

## Requirements Inventory

### Functional Requirements

- FR1: Pre-flight (phase 01) renders as a checklist, items appearing individually as the runtime tests them; SPOC spawn is gated on all-green by the runtime, not the HUD.
- FR2: Heartbeats (phase 02) render per dependency with real-call latency and quota/credit reading tagged `direct|proxy|unknown`; `unknown` never renders green; `missed` is distinct from `fail`.
- FR3: Two-stage you-are-here map — stage-1 intake/planning steps, then the ratified workflow's `hud_tracked` nodes; stage 2 is a dim placeholder until ratification; walk index from the runtime, never counted HUD-side.
- FR4: Gate briefings — gate ID/focus/operator prompt, drafted proposal + confidence, artifacts-under-judgment inline (G2B variant thumbnails, G4A voice rows), and the exact copy-paste verdict command with digest pre-filled.
- FR5: Error briefing — `paused_error_tag`, error message verbatim, node + walk index, re-entry point, recover command block.
- FR6: Batch briefing — `waiting_batch_id`, time parked, `trial resume-batch` command block; violet calm treatment.
- FR7: Specialist chips (monogram + status ring + glyph) expanding to briefings: current activity, node, model, last artifact, cost attribution.
- FR8: Read-only state-trace well — append-only feed of state transitions, gate open/close, specialist dispatch/return, artifact writes.
- FR9: Health strip — token burn, cost vs budget, per-platform credit/quota tiles, each with mandatory staleness stamp; threshold-crossed treatment.
- FR10: Modality chips — BATCH, DETECTIVE, styleguide slug — always rendered, activation as the signal, provenance on expand.
- FR11: Notifications — five v1 event classes per `hud-config.yaml` opt-in (paused_at_gate, paused_at_error, batch_pause_resumed, health_threshold, run_stalled); channels on-HUD visual + optional sound + phone push (Pushover primary / ntfy fallback via Apprise); email/webhook OUT.
- FR12: Run-stalled watchdog fires when nominally `in-flight` and `progress_seq` frozen past budget, including a producer-dead reading; survives runtime-session death.
- FR13: Self-updating page — ETag-gated poll every 2–5s, in-place section DOM updates preserving disclosure/scroll/selection; no manual refresh.
- FR14: All seven envelope statuses render distinctly (registered, in-flight, paused-at-gate, paused-at-error, waiting_for_provider_batch, completed, failed), status strings verbatim.
- FR15: Every pause class renders a next action verbatim from the projection (runtime-composed via CLI-co-located builder); the HUD never composes commands.
- FR16: `completed` renders a deliverables summary (deck, audio, workbook, Descript-ready bundle paths + final cost).
- FR17: Run identity guard — HUD binds one trial_id; mismatch/ambiguity renders REFUSE-TO-RENDER; healthz identity-checked (trial_id + launch nonce).
- FR18: Unrecognized statuses/schema versions render literally as UNRECOGNIZED (idle slate, raw value quoted), never coerced.

### NonFunctional Requirements

- NFR1: Read-only, zero-button — GET-only server; no verdict affordances anywhere; interactivity = disclosure + selection + links + scroll only.
- NFR2: Zero-lie — projection is sole input; every value carries its age; dead feeds veil STALE; run.json is truth with reconcile-on-entry (AD-17).
- NFR3: Glanceable — run state, blocking condition, next action legible within 5 seconds, above the fold at 1440×900.
- NFR4: Staleness budgets — run state 5s, health tiles 60s (operator-approved defaults).
- NFR5: No-mocks heartbeats — real live calls, never mocked/simulated/cached; cheap paid pings acceptable.
- NFR6: Performance — no 525KB run.json parse in the HUD path; LangSmith out of the data path; projection ≤128KB target / 256KB tripwire; emission is serialize+write only.
- NFR7: Governance — pipeline-lockstep regime on all trigger paths; Tier-2 manifest bump party-gated before dev; regime doc read at T1.
- NFR8: Evidence — L1 contract/enum tests, L2 golden fixtures per pause class + adversary fixtures, L3 first-run-stands live witness per pause class, L4 keep-it-open usage witness; per-story DoD names its witness set.
- NFR9: Accessibility floor — color+shape+symbol never color alone; aria-live announcements; reduced-motion respected; text zoom 125% keeps the 5-second band above the fold.
- NFR10: Windows-first local — single operator, localhost only, `.venv/Scripts/python.exe`; os.replace bounded-retry discipline; tests touching network/db marked serial/live.

### Additional Requirements (Architecture)

- AR1: All 19 ADs of ARCHITECTURE-SPINE.md bind; stories cite the ADs they implement.
- AR2: Contract package (`app/models/runtime/operator_surface.py`) ships strict model + lenient reader + `derive_event_transitions` + `HudConfig`; dual pins committed (AD-4).
- AR3: `OperatorSurfaceAssembler` sole writer; emission cadence transition/section/tick; `_persist_envelope` integration both walks; ~3501 bypass routed (AD-2/15).
- AR4: Pinned start sequence: mint → run dir → registered projection → HUD server → pre-flight → SPOC (AD-7).
- AR5: Notifier own process, own state dir, restart semantics, Apprise env-only creds (AD-9).
- AR6: Legacy retirement — coordination.db reader + mtime fallback deleted; run_hud.py deprecation stub; Dev-Cycle/M5 panels retired; import-linter contracts added (AD-8/12, paradigm arrows).
- AR7: Envelope status-model files join `block_mode_trigger_paths` (reverse tripwire) in the same Tier-2 bump (AD-5/14).

### UX Design Requirements

- UX-DR1: DESIGN.md tokens implemented verbatim (18 colors, 6 type roles, radii, spacing, 15 component groups); dark cockpit only.
- UX-DR2: Annunciator strip severity ordering (error/failed > gate > batch > health > stale > nominal), one condition at a time, aria-live, one-time 300ms luminance step, no blinking.
- UX-DR3: Urgency auto-expand contract carried verbatim (is_current OR conditions OR blockers → expanded, wins over remembered collapse).
- UX-DR4: All State Patterns rows (7 statuses + panel-level: no-active-run, binding, unrecognized, identity-uncertain, tile-stale, feed-lost, config-unreadable) implemented per EXPERIENCE.md.
- UX-DR5: Voice-and-tone table binds microcopy (cockpit terse, verbatim statuses, ages always shown).
- UX-DR6: Key-screen mocks are composition reference; spines win on conflict.

### FR Coverage Map

| Requirement | Story |
|---|---|
| FR1, FR2 | 35.3 (produce), 35.5 (render) |
| FR3, FR7, FR8, FR9, FR10, FR13, FR14, FR16, FR18, UX-DR1–6 | 35.5 |
| FR4, FR5, FR6, FR15 | 35.2 (producer), 35.5 (render) |
| FR11, FR12 | 35.6 |
| FR17 | 35.3, 35.4, 35.5 |
| NFR1–NFR6, NFR9, NFR10 | 35.1–35.6 (per-story ACs) |
| NFR7, AR7 | 35.0 |
| NFR8 | every story DoD + 35.7 |
| AR1–AR5 | 35.1, 35.2, 35.3, 35.4 |
| AR6 | 35.8 |

## Epic List

- Epic 35: Operator HUD v1 — Flight Deck (single epic; 9 stories 35.0–35.8)

## Epic 35: Operator HUD v1 — Flight Deck

The read-only dark-cockpit instrument panel for Marcus-SPOC production runs, built on the runtime-owned operator-surface projection, reaching a live E2E witness run with the party finding the HUD performed to spec.

**Story order (party-amended, greenlight record #4):** 35.0 → 35.1 → 35.2 → 35.3 (STRICTLY after 35.2 — same runner region) → 35.5 → 35.8 (STRICTLY after 35.5 — run_hud.py collision) → 35.7. Parallel lanes: 35.4 ∥ 35.3 (server.py owned by 35.4 only); 35.6 ∥ 35.5 (disjoint trees). Any two agents touching the runner or the manifest serialize by rule. DoD-over-clock: witness sets non-compressible; at the wall, stop at the last DoD-complete story.

### Story 35.0: Tier-2 manifest-lockstep bump + 4-failure test disposition (pre-dev gate)

As the operator, I want the lockstep manifest extended to the new HUD surface and the 4 known ambient test failures dispositioned, so that all Epic-35 dev is regime-governed from the first line and no pre-existing red is mistaken for new breakage.

**Acceptance Criteria:**

**Given** party-mode consensus ratifying the Tier-2 change (AD-14)
**When** `state/config/pipeline-manifest.yaml` is bumped adding to `block_mode_trigger_paths`: `app/models/runtime/operator_surface.py`, `app/models/schemas/operator-surface.v1.schema.json`, `app/marcus/orchestrator/operator_surface_assembler.py`, `app/hud/**`, `app/notify/**`, `tests/unit/models/test_operator_surface_shape_pin.py`, `tests/contracts/test_operator_surface_parity.py`, `tests/hud/**`, `tests/notify/**`, `app/models/runtime/production_trial_envelope.py` (AD-5 reverse tripwire), and `app/marcus/orchestrator/production_runner.py` (explicit party INCLUDE — hosts the AD-2 emit seam); the version field(s) that bump (pack_version v4.2→v4.3 and/or schema_version) follow regime mechanics with the lockstep checker as arbiter, choice documented in evidence
**Then** `check_pipeline_manifest_lockstep.py` exits 0 (trigger paths registered ahead of file creation are inert — AD-14)
**And** the 4 failing pins in tests/test_run_hud.py + tests/test_progress_map.py are dispositioned: 2 stale pins fixed or marked for retirement in 35.8; 2 environment-pollution failures documented as retired-by-35.8 (injection-seam obsolete under AD-8); a green or explained baseline is recorded in the story evidence.

### Story 35.1: Operator-surface contract package

As the runtime, I want a versioned projection contract with dual pins, so that producer and consumers can never silently drift.

**Acceptance Criteria:**

**Given** the spine's AD-1/4/5/16/18/19
**When** `app/models/runtime/operator_surface.py` lands with `OperatorSurfaceProjection` v1 (strict), `read_operator_surface_lenient()`, `derive_event_transitions()`, `HudConfig` + loader + defaults, and `app/models/schemas/operator-surface.v1.schema.json`
**Then** the byte-pin test and the producer↔consumer parity test both pass (AD-4a/4b patterns)
**And** L1 enum set-equality against `ProductionTrialStatus` passes (all seven statuses)
**And** the lenient reader renders typed `Unrecognized` on a future-fields fixture and an unknown-status fixture without raising
**And** `derive_event_transitions` passes golden transition fixtures for all five event classes including resume-that-repauses and recover-reenter edges
**And** the projection model enforces ring-buffer caps (trace 200, health history 50/tile) with the 256KB tripwire test.

### Story 35.2: Assembler + runner emission (both walks)

As the runtime, I want every state change projected exactly once through one assembler, so that the HUD's single input is complete, fresh, and reconciled.

**Acceptance Criteria:**

**Given** AD-2/15/17 and the two-walk gotcha
**When** `OperatorSurfaceAssembler` lands and `_persist_envelope` calls `assembler.emit(envelope)`, the ~3501 bypass is routed through `_persist_envelope`, section APIs cover steps/preflight/health/trace, and the freshness tick runs while in-flight
**Then** golden-fixture tests show a projection written at every status transition in BOTH walks (start + continue entry points, all pause classes, terminals)
**And** `seq` bumps on every write while `progress_seq` bumps only on progress events (L1)
**And** every runner entry point re-emits from the current envelope first (skew fixture renders run.json truth after touch — AD-17)
**And** atomic write with bounded retry passes the replace-under-open-reader test on Windows; exhaustion logs and skips without raising into the walk
**And** next-action command strings come from the CLI-co-located builder and round-trip through the actual CLI parser for every pause class (AD-3)
**And** ANY exception inside `assembler.emit()` is caught, logged, and never propagates into either walk (fault-injection test — greenlight amendment 8); `run.json` write semantics are unchanged in passing
**And** the replace-under-open-reader requirement is the party-downgraded deterministic smoke (one held reader + bounded-retry + fault-injected exhaustion branch); the concurrency hammer goes to deferred-inventory.

### Story 35.3: Start-path integration — pinned sequence + HUD server lifecycle + pre-flight/heartbeats

As the operator, I want the runtime start path to mint the projection, launch the HUD server, and run real pre-flight/heartbeats before SPOC spawns, so that pre-flight is authoritative and the HUD is alive from the first moment.

**Acceptance Criteria:**

**Given** AD-7/8/11
**When** the start sequence lands (mint trial_id → run dir → registered projection → launch HUD server child → pre-flight phase 01 → heartbeats phase 02 → SPOC spawn gated on all-green)
**Then** `/healthz` returns `{trial_id, launch_nonce, mode}` and the pre-flight item passes only on match; child bind failure = pre-flight FAIL (wrong-server-on-port fixture)
**And** phase-01 items derive from the ready_for_trial check set in-runtime; phase-02 heartbeats are REAL live calls with latency + quota/credit + confidence written into the projection as each completes (no mocks — NFR5); v1 live heartbeat set = OpenAI + Gamma + LangSmith-env-presence (party trim, greenlight amendment 10 — remaining platforms accrete under the AD-13 falter-surface regression rule)
**And** the story spec reconciles the pinned AD-7 sequence with the real start topology (trial.py::start_trial + run_production_trial) including pre-envelope exits `cancelled-at-g0`/`saved-only`: those exits leave the projection at `registered` with a terminal trace event (greenlight amendment 12)
**And** a failed item blocks SPOC spawn and persists in the projection
**And** live witness (L3): one real start-path run recording pre-flight → all-green → spawn, banked as evidence.

### Story 35.4: GET-only HUD server + projection reader

As the operator, I want a localhost read-only server with ETag polling, so that the page self-updates within the staleness budget without any mutation surface.

**Acceptance Criteria:**

**Given** AD-6/8
**When** `app/hud/server.py` (GET `/`, `/projection`, `/healthz` only) and `app/hud/data.py` (`read_operator_surface_lenient(run_dir)` — explicit path, no discovery) land
**Then** a route-inventory test proves no non-GET route exists
**And** `/projection` returns ETag `<schema_version>:<seq>`, serves read-then-respond byte snapshots, and returns 304 on If-None-Match match (route-implemented)
**And** identity mismatch between bound trial_id and projection renders the REFUSE-TO-RENDER payload
**And** the server reads only the projection + static assets (import-linter: no orchestrator, no hud_data_sources, no strict-model parse).

### Story 35.5: Flight-deck view — render retarget to the projection

As the operator, I want the full dark-cockpit page rendered from the projection per the UX spines, so that every run state is glanceable and honest.

**Acceptance Criteria:**

**Given** the UX spine pair (operator-approved) and AD-12
**When** the render shell is retargeted into `app/hud/render/` fed only by projection data
**Then** L2 golden fixtures render all seven statuses distinctly with verbatim strings, all five zones, annunciator severity ordering, two-stage map with urgency auto-expand, gate/error/batch briefings with inline artifacts + command blocks, specialist chips, health strip with staleness stamps + confidence tags, modality chips, and state-trace well; v1 panel-state golden set = no-active-run, unrecognized, refuse-to-render, stale-veil (party trim, greenlight amendment 10 — binding/feed-lost/config-unreadable fixtures are a named fast-follow); the narrowed-component-selection golden fixture is owned here (amendment 11)
**And** the poll loop applies in-place zone-scoped DOM replacement preserving disclosure/scroll/selection (no location.reload; zone innerHTML replacement satisfies AD-12 for v1 — no granular diffing); preservation is tested as a render unit with the live check riding the 35.7 witness checklist (amendment 10)
**And** DESIGN.md tokens verbatim; color+shape+symbol on every status; reduced-motion honored
**And** a legacy-shaped run dir renders UNRECOGNIZED (L2)
**And** kept render pins re-pointed at projection-fed fixtures; Dev-Cycle/M5 panels absent.

### Story 35.6: Notifier service + stall watchdog + phone push

As the operator, I want per-event-class notifications including phone push and a stall watchdog that survives session death, so that AFK never means flying blind.

**Acceptance Criteria:**

**Given** AD-9/10/18/19
**When** `app/notify/service.py` lands as its own process (launched by the start path, not fate-shared), consuming the projection + `HudConfig`, pushing via Apprise (Pushover primary, ntfy fallback, env creds)
**Then** golden transition fixtures fire exactly the five event classes via the contract's `derive_event_transitions` (no local derivation)
**And** the watchdog fires `run_stalled` on frozen `progress_seq` past budget while in-flight, including the producer-dead reading; `waiting_for_provider_batch` exempt
**And** restart-mid-pause fixture: active-unacknowledged `paused_*` fires once, `batch_pause_resumed` on observed transition only (own state dir)
**And** live witness (L3): one real phone push delivered via accountless ntfy (party trim — Pushover becomes a config-swap once the operator provisions a token; story close never fate-shares with operator account setup), banked as provider delivery evidence
**And** notifier failure never propagates (fault-injection test).

### Story 35.7: E2E witness run + party performance review

As the operator, I want a live small production run (3 slides, 1 motion video, 1 workbook) flown with the HUD open end-to-end, so that the party can judge the HUD performed to spec on a real flight.

**Acceptance Criteria:**

**Given** stories 35.0–35.6 done (35.8 may trail if files don't overlap)
**When** a live Marcus-SPOC production trial runs as a SMALL run — `component_selection` deck+motion+workbook all true, slide count minimized via corpus/LO curation at the planning gates, emergent count accepted and recorded (party reword, greenlight amendment 3 — no 3-slide directive knob exists) — HUD server up from pre-flight, all gates decided via the conversational surface using HUD-rendered command blocks
**Then** the run reaches `completed` with deliverables (deck export, motion clip, workbook.md/.docx)
**And** the HUD's projection trail demonstrates: pre-flight rendered as tested; every pause class hit in-run renders distinctly with a working copy-paste next action; staleness stamps honest; zero-lie held (no contradiction vs run.json); notifications fired per config
**And** the abort/continuity criterion holds (amendment 9): a HUD/projection defect mid-run is a logged finding while the paid run continues on the SPOC surface; abort only if emission corrupts run.json or blocks a walk; first-run-stands
**And** fully-spawned party mode (core four + contrarians Splinter/Level) reviews the evidence against Murat's 10-item checklist (greenlight amendment 14) using the scoped-verdict schema (amendment 2): classes witnessed live vs covered-by-golden vs live-witness debt, per-class; PASS language = "HUD performed to spec on the witnessed surface"; brief SC5 stays open as the L4 standing witness
**And** L3 witnesses from the run are promoted into the L2 golden set.

### Story 35.8: Legacy retirement + import fences

As the codebase, I want the April HUD's data path retired and the layer arrows enforced, so that the wrong-run fallback is dead code-level, not just policy.

**Acceptance Criteria:**

**Given** AD-8/12 and the paradigm enforcement note
**When** the coordination.db reader, `_find_latest_bundle`, and bundle-gate yaml pipeline are deleted from the HUD path; `run_hud.py` becomes a deprecation stub pointing at `trial hud`; `tests/test_run_hud.py` retires with it; import-linter contracts land (app.hud/app.notify ↛ orchestrator; anything ↛ hud_data_sources; consumers ↛ strict parse)
**Then** `lint-imports` passes with the new contracts
**And** the manifest trigger rows for the stubbed files are updated in the same change (Tier-1 within the 35.0 party-ratified trigger-path envelope — see greenlight post-gate addendum)
**And** full test suite green (minus quarantined/live) with the 35.0 disposition honored.
