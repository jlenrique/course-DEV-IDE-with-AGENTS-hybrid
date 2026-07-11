# Reconcile — Brief + Addendum vs ARCHITECTURE-SPINE.md

Input: `_bmad-output/planning-artifacts/briefs/brief-operator-hud-revival-2026-07-11/brief.md` + `addendum.md`
Spine: `_bmad-output/planning-artifacts/architecture/architecture-operator-hud-2026-07-11/ARCHITECTURE-SPINE.md`
Reviewer pass: 2026-07-11 (input-reconciliation).

## Binding principles 1–6

| # | Principle | Verdict | Where / what's missing |
|---|---|---|---|
| 1 | Read-only, zero-button; copy-paste commands digest-pre-filled; runtime executes pre-flight and gates SPOC spawn | **LANDED** | AD-6 (GET-only, mutation route = defect), AD-3 (projection carries exact next-action command; HUD never composes), AD-11 (runtime-executed pre-flight gates spawn). Digest lands via AD-3's incorporation of EXPERIENCE §Projection Demands ("full card incl. … digest"). |
| 2 | Zero-lie: never contradicts envelope; unrecognized renders as unrecognized; every tile admits age; dead feed → explicit STALE | **LANDED** | AD-4 (UNRECOGNIZED on unknown schema_version), AD-5 (verbatim status vocabulary), Conventions (per-section `as_of`, mtime-gated reads). STALE rendering itself is UX-owned; data support present. |
| 3 | Self-updating, served locally from the runtime session; server readiness is a pre-flight item | **LANDED** | AD-6 (ETag 2–5s poll), AD-7 (`/healthz` 200 as pre-flight checklist item, session-owned lifecycle). |
| 4 | Glanceable dark-cockpit hierarchy | **CORRECTLY-DEFERRED** | UX-owned (EXPERIENCE/DESIGN); spine ties render zones to DESIGN tokens in the Capability Map and preserves the render shell (AD-12). |
| 5 | No-mocks heartbeats — real live calls, never mocked/simulated/cached | **LANDED** | AD-11 ("real calls, never mocked/cached" — "simulated" not restated but semantically covered). |
| 6 | Configurable notifications incl. phone in v1; per-event-class opt-in via YAML; channels on-HUD + sound + push; email/webhook OUT of v1 | **PARTIAL** | Five event classes, channels, YAML config, Apprise/Pushover/ntfy all land (AD-9, AD-10, Conventions, Structural Seed). **Missing: the email/webhook v1 exclusion is not restated as a guard.** This matters more than it looks: the chosen mechanism (Apprise) makes adding email/webhook a one-line config URL — nothing in the spine forbids the channel set silently widening. One sentence in AD-9 ("channels are exactly these three; adding a channel class is a scope change") would close it. |

## Scope IN (v1)

| Item | Verdict | Notes |
|---|---|---|
| Pre-flight + heartbeat visualization | LANDED | AD-11, Capability Map "Pre-flight + heartbeat board". |
| Two-stage progress map with drill-down | LANDED | Capability Map (stage-1 manifest + ratified `hud_tracked`, walk index), AD-1/AD-3. |
| Gate briefings | LANDED | Via AD-3's incorporation of §Projection Demands (decision card, artifacts under judgment ride as paths/URLs in projection). |
| Specialist/service icons with briefings | **PARTIAL** | Specialist *agents* land via §Projection Demands "specialist roster activity". The brief's lifecycle §5 says "each specialist agent **and specialty service** is an icon that expands to a briefing" — non-agent specialty *services* (e.g., LiteLLM, Gamma-as-service state beyond a health tile) have no named projection slot in the spine or in §Projection Demands. If service briefings are intended, the projection needs a slot; if they collapsed into health tiles, say so. |
| Read-only state-trace window | LANDED | §Projection Demands (append-only events) via AD-3; Capability Map row 1. |
| Health strip (token use, credits where fetchable) | LANDED | Capability Map "Cost/credits with confidence tags", AD-11. See addendum §C below for the mechanics gap. |
| Modality indicators | LANDED | Via AD-3 (§Projection Demands modality readings + provenance). |
| YAML notifications + phone push + stall watchdog | LANDED | AD-9, AD-10. |
| Locally served page | LANDED | AD-6, AD-7. |

## Scope OUT (v1)

All OUT items are either structurally excluded or named: interactivity (AD-6), fleet/history (Deferred, v2), trace-waterfall (AD-3 — LangSmith link rides in projection), Dev-Cycle/M5 (AD-12 retired with pins). Eval/drift panels: absent by construction, acceptable. Email/webhook: see Principle 6 PARTIAL.

## Success criteria 1–5

| # | Criterion | Verdict | Notes |
|---|---|---|---|
| 1 | Complete — every status/pause class distinct; every gate/specialist has a briefing; **pre-flight covers the full falter-surface** | **PARTIAL** | Statuses: AD-5 (all seven, resolving the brief's six against the envelope's seven — good). Briefings: via AD-3. **Missing: the falter-surface contract** — the brief's load-bearing definition ("coverage = anything whose absence would make the runtime falter") is nowhere encoded as a rule, coverage test, or derivation procedure. AD-11 says *how* pre-flight executes and reports, not *what the item inventory is* or how completeness is judged. See Open Questions below — this was explicitly assigned to the architecture phase. |
| 2 | Reliable — zero-lie across a live run; unknowns unrecognized; never the wrong run | LANDED | AD-3, AD-4, AD-8, AD-13 L2/L3. |
| 3 | Self-updating within the staleness budget shown on the tile | LANDED | AD-6; budgets in `hud-config.yaml` (Structural Seed, Deferred). |
| 4 | Glanceable — five-second rule | CORRECTLY-DEFERRED | Layout law lives in EXPERIENCE/DESIGN. |
| 5 | **Keep-it-open witness** — operator completes a full trial on HUD + SPOC only, by choice | **PARTIAL** | The spine's evidence ladder (AD-13) tops out at L3 per-pause-class component witnesses. The arc-level acceptance — the brief's ultimate success bar and the party plan's usage-witness disposition of Level's challenge — is not named anywhere (no "L4"/arc witness, no mention in AD-13 or Deferred). Epics can carry it, but the spine is where the evidence ladder was defined; one line naming the terminal witness would keep it from evaporating between phases. |

## Constraints & governance §

| Item | Verdict | Notes |
|---|---|---|
| Lockstep `block_mode_trigger_paths` governance | LANDED | AD-14 (incl. Tier-2 party-gated pre-dev story). |
| Runtime-owned versioned projection, both walks, dual shape-pins | LANDED | AD-1, AD-2, AD-4. |
| Reuse as a tiering decision | LANDED | AD-12 (retarget data layer, keep render shell, ~98 pins). |

## Open questions §

| Question | Verdict | Notes |
|---|---|---|
| Transport (poll-first, SSE only if justified); runtime↔HUD lifecycle | LANDED | AD-6, AD-7, Deferred (SSE condition preserved). |
| Phone-push mechanism selection | LANDED | AD-9 (Apprise; Pushover primary, ntfy fallback, web-verified). |
| Health thresholds + notification defaults (team; operator reviews at UX gate) | CORRECTLY-DEFERRED | [ASSUMPTION]-tagged defaults in `hud-config.yaml` (Deferred §). |
| Iconography + briefing content per specialist | CORRECTLY-DEFERRED | UX phase (DESIGN [ASSUMPTION] monograms). |
| **Pre-flight item inventory derivation — from `ready_for_trial` scripts + the falter-surface contract (architecture phase)** | **DROPPED** | The brief hands this question *to the architecture phase by name*, and no AD answers it. AD-11 fixes ownership (runtime executes, projection reports) but never says where the checklist comes from, that it derives from `ready_for_trial`, or how falter-surface coverage is asserted. This is the single clearest dropped input across the brief. |

## Addendum

| Item | Verdict | Notes |
|---|---|---|
| §A interview record | LANDED | Fully reflected through the brief's principles (checked above); pre-flight-contract verbatim principle shares the SC1/open-question gap. |
| §B comparables digest | CORRECTLY-DEFERRED | UX consumed it (EXPERIENCE §Inspiration); no architecture residue expected. |
| §C fetchability table | **PARTIAL** | Confidence taxonomy (`direct|proxy|unknown`, never-false-green) lands in AD-11; per-platform mechanics correctly deferred to story level (Deferred §). Two quiet facts didn't carry: (a) **OpenAI usage/costs require a separate Admin API key, not the inference key** — a credential/config architecture fact (the spine's env-only credential convention covers push creds only; nothing anticipates a second OpenAI key class); (b) **Gamma authoritative `remaining` piggybacks generation polls** — i.e., mid-run health readings come from the runtime's *own production calls*, not heartbeats; the Capability Map sources health from "cost-report + heartbeat readings" only, which has no slot for piggybacked in-run readings. |
| §E config sketch | LANDED | Structural Seed `hud-config.yaml` ("notification matrix + budgets + hud.port"); naming Conventions match (snake_case event classes, `hud.`/`notify.` keys). |
| §F phone push promoted to v1 | LANDED | AD-9. |
| §F run-stalled watchdog | LANDED | AD-10 (600s default = EXPERIENCE's 10-min [ASSUMPTION]; consistent). |
| §F quota sufficiency joined the falter-surface | **PARTIAL** | Never-false-green + proxy confidence land (AD-11). The "joined the falter-surface" half inherits the missing falter-surface contract (SC1/open-question DROPPED item): nothing asserts quota checks are *part of the coverage definition*. |
| §F dev-run notifier reuse hint | LANDED | AD-9 (producer-agnostic shared service, outside `app/gates/**`) + Deferred "Dev-side stall producer". |

## Tally

LANDED 21 · PARTIAL 5 (Principle 6 channel guard; specialist/service briefings; SC1 falter-surface; SC5 keep-it-open witness; §C fetchability facts + §F quota-sufficiency [counted once with SC1]) · DROPPED 1 (pre-flight inventory derivation) · CORRECTLY-DEFERRED 5.
