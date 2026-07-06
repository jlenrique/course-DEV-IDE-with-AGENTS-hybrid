# Canonical Production Conversation arc — GREEN-LIGHT party record (2026-07-06)

**Verdict: 6/6 GO-WITH-AMENDMENTS (unanimous; no impasse — Quinn/John escalation chain not invoked).**
**Branch:** `dev/workbook-2026-07-06` · **Session:** 16 (Class S) · **Facilitator:** Claude (Marcus-activated), fully-spawned party per `bmad-party-mode` (6 independent subagents).
**Seats:** Winston (architecture) · John (PM, decision owner) · Murat (test architect) · Amelia (dev feasibility) · Dan (Creative Director, adjunct) · Marcus (operator-experience, independent adjunct spawn).

---

## 1. The arc (as ratified)

**Theme:** every ceremony that is built, live-proven-once, and dormant-by-default becomes a **standing property of a normal Marcus-SPOC production run**. The arc closes the Horizon-2/BETA-§8 remainder and workbook gaps #1/#2/#4. Operator directive (2026-07-06, binding): the styleguide pick and the G0 enrichment loop "should be canonical — performed on every run with HIL input"; CD issue addressed; Tracy working.

### Story spine (ratified sequence)

| # | Story | Content | Size |
|---|-------|---------|------|
| S0 | Arc charter + contracts | This record + the **styleguide-binding→CD one-page contract** (W2) + **T6b/c/d equivalence mapping** (J3) + per-leg default-flip owners (J-own) + leg-3 **Tier-1-vs-Tier-2 ruling** (W3) + `-n 0` rerun of the workbook xdist-suspect test (M-pre) | S |
| S1 = 1a | CD activation contract | NEW `app/specialists/cd/_act.py` + **ResolvedCreativeDirective** envelope artifact-write + explicit **skip-record** semantics; dispatch still routes around; RED-first against the contract | M/L |
| S2 = 2w | Picker canonical (wiring) | `run_picker_preflight` wired into `start_trial_cli` **before run-dir creation**; pick persisted into the bundle; resume/recover NEVER re-prompt; WARN-seed preserved; kickoff-meeting Beat-1 narration + inline-list publish-flake degrade | S |
| S3 = 1b | CD activation (live) | Dispatch un-routed; 4.75 executes in BOTH walks (two receipts); CD consumes a real picked styleguide; protected-invariant checks (source-wins-loudly) | S/M |
| S4 = 2f | FAIL-LOUD flip | Styleguide-less WARN-seed → hard failure at trial-start, pre-spend (gated on S3 = cd-envelope-authoring landed) | S |
| S5 = 3 | G0 enrichment canonical | **Pre-gate:** blast-radius grep of first-pause-G1 suites (N≤5 single story, else split 3a migration / 3b flip) + pre-G1 resume-walk audit. Then `MARCUS_G0_ENRICHMENT_ACTIVE` default-ON (kill-switch retained); G0E/G0R standing gates; Beats 2–3 narration; fast-path machinery (fingerprint-gated G0E reuse; conservative G0R); `MARCUS_G0_DISPATCH_LIVE` = live in production, deterministic in default test path (`--run-live` arming) | M/L |
| S6 = 4 | Tracy/research canonical | `MARCUS_RESEARCH_DISPATCH_LIVE` default-ON **narrow scope: Scite-canonical; Consensus explicitly deferred with a skip-witness**; resume idempotency (no double-dispatch); degrade-when-creds-absent = recorded envelope outcome + intake-time narration; cited `research_entries` → workbook DOI section via the envelope (contract already AC-D-pinned) | S |
| S7 = 5 | Workbook generalization | **Construction story, not a flip** (W4): retire `_CH2_KC`/`_CH3_KC`/`_FURTHER_READING`; derive from (1) enrichment cards → (2) lesson plan → (3) resolved citations; degrade-with-provenance per missing segment; FAIL-LOUD on zero-enrichment; tejal golden-parity; **in-graph 07W live proof** (side-door driver dead as evidence) | M |
| S8 = 6 | Composed live proof | Operator-named **next unproduced lesson** through the full SPOC conversation; evidence pack per M4; **run 2 with a different choice-path** (J-d4); arc done-signal | M wall-clock |

Dependency spine: S0 → S1 → S2 → S3 → S4 → {S5, S6} → S7 → S8. (S5/S6 parallelizable in principle; single-dev-lane runs them sequentially, order by readiness.)

### Arc DONE-SIGNAL (John, ratified verbatim authority for §5 stop-conditions)

1. All canonical defaults are **committed config on the branch** — a cold run by someone with no memory of this arc gets the full conversation.
2. One non-tejal corpus through the full SPOC conversation, every gate performed (CD, picker, G0E/G0R, research), **nothing-bypassed** proven by evidence (see M4), zero side-door invocations.
3. All three pillars produced; workbook DOI section carries real resolvable citations tracing to same-run live TexasRows.
4. **Second run** with the operator taking a different choice-path at ≥1 gate. A run requiring a mid-run code fix does not count as the clean run.
5. Party concurrence + (if armed) shadow-monitor concurrence.

---

## 2. Amendment ledger (all binding unless marked)

**John (PM rulings):**
- J1: Leg 4 stays in-arc, narrow scope (dispatch-ON + envelope threading; research *quality* OUT).
- J2: Learner-ready prose/revoicing explicitly OUT → deferred-inventory with direction-may-flip caveat.
- J3: **Batch-LLM GO fires at arc close ONLY IF the charter maps T6b/c/d onto specific legs in writing** (S0 deliverable). Conservative default: no unaudited equivalence.
- J4: Every canonical HIL gate ships a one-keystroke accept-recommended path (canonical must be cheap to comply with).
- J5: No cost governor; visible per-run cost line suffices (operator ruling: cost not a constraint).
- J6: Tracking = party-records + SESSION-HANDOFF convention continues; charter states done-signal verbatim; deferred-inventory mandatory for fenced-out items; one STATE-OF-THE-APP §11 refresh at arc close.
- J-own: Named owner for each leg's default-flip in this charter — **each story's close includes its own default-flip** (owner: the story itself; "leg 6 will catch it" is the parking pattern).

**Winston (architecture):**
- W1: Sequence as ratified above (resolved via Amelia's splits).
- W2: **Contract-first one-pager** for the styleguide-binding→CD-consumption seam BEFORE S1/S2 open (what the picker commits, where it lands, what CD reads at 4.75).
- W3: S5 includes the **pre-G1 resume-walk audit** (does resume/recover handle a pause EARLIER than G1?) + a pre-dev **Tier-1-vs-Tier-2 lockstep ruling** on the default flip (nodes already compiled; expect Tier-1, but rule before dev opens — `workflow_runner.py` is a block-mode trigger path regardless).
- W4: S7 rescoped as a construction story with in-graph live proof.
- W5: CD contract = **explicit-skip-record / presence-not-absence** semantics; downstream keys off presence; finding neither artifact nor skip-record = loud failure (route-around structurally impossible).
- W6: Named regression checks for the two protected invariants (VO↔on-screen; source-detail→Gamma) ride S1, S2, S8.
- W-risk: S2's pick must persist where the continuation walk reads it; resume must provably never re-prompt nor fall back to WARN-seed. Budget a bitrot audit on `run_picker_preflight` (zero callers today).
- W-deg (party call, Winston proposing, unopposed): research outage = **degrade-with-recorded-empty** (provenance-carrying), never silent, never halt-the-lesson.

**Murat (test architecture — per-leg witnesses binding):**
- M1: S5's integration-suite migration is a **prerequisite gate before the flip opens**, with a **test-disposition ledger** (test → disposition → replacement witness) in completion notes. Refuse "both worlds green" coverage vanity: unset-env variant becomes canonical; flag-ON becomes escape-hatch coverage or is deleted.
- M2: Leg 4 scope honesty — Scite-canonical in writing; Consensus `pytest.skip` witness naming the deferred-inventory entry.
- M3: Leg 1 witness doubled: **runner-emitted receipts in BOTH walks** (execution evidence with output digest or enumerated skip reason; graph-presence assertions refused).
- M4: S8 evidence pack: (i) **runner-stamped env attestation** at trial start; (ii) per-node receipts for every canonical node; (iii) gate transcript showing operator verdicts (none scripted/auto-defaulted); (iv) workbook citations **traceable to same-run TexasRows**; (v) explicit side-door-absence assertion. Recover-resume acceptable (product behavior; exercises both walks); **content assertions first-run-stands** (no retry-to-green on output quality).
- M-wit per leg: S2 = observed HALT at the production call site on absent/invalid seed (resumable paused state, not a WARN string); S5 = default-ENV integration walk with assert-unset preamble pausing at G0E/G0R; separate default-witness for `MARCUS_G0_DISPATCH_LIVE` (deterministic path with a receipt saying so); S6 = ≥1 real cited TexasRow with resolvable DOI inside a production walk (content-inspected, not row-counted); S7 = RED on a non-tejal chapter structure BEFORE the fix + tejal byte-parity after.
- M-pre: One `-n 0` rerun of `test_ac12_dp6_fresh_required_blocks_reuse_stamp` before S7 opens; xdist rule: any new parallel-run red gets one `-n 0` confirmation before triage.

**Amelia (dev feasibility):**
- A1: Leg 1 split 1a/1b as ratified (contract authoring is greenfield — no `_act.py` exists; envelope-write shape is being AUTHORED, get it right or re-cut two legs).
- A2: S5 T1 task #1 = the first-pause-G1 grep with exact suite list+count BEFORE ACs freeze; check for a shared fixture/helper to migrate once instead of N suites.
- A3: S2 ships WARN-preserving; FAIL-LOUD is S4, never bundled.
- A4: **Default-flip, retain flag as kill-switch** + one OFF-path smoke test; retirement filed in deferred-inventory (trigger: leg-6 green) as trailing S-story.
- A5: S7 derivation order: enrichment cards → lesson plan → resolved citations; degrade-with-provenance (recorded omission per missing segment; visible workbook note OK; invented content never); zero-enrichment = FAIL-LOUD at `_act` entry. RED-first quartet: tejal golden-parity / synthetic 1-segment corpus / missing-card omission / zero-enrichment raise.
- A-flag (honesty): dispatch-table path for 1b and the leg-3 suite count are stated expectations, not verified reads — both are T1 verification tasks.

**Dan (Creative Director):**
- D1: **ResolvedCreativeDirective** contract: (i) bound styleguide resolution — CD binds pick→per-variant gamma_settings, full field-set snapshot with guide id+version+timestamp; Studio companion selected by production_mode tag, studio branch rejects Classic-only keys; (ii) CD owns **experience-profile** resolution (explicit, never silently inferred; underdetermined = named fallback on the record); (iii) **layering manifest** — base = styleguide, overlay = source-derived, overlay wins, written per field-family so Gary composes mechanically.
- D2: **CD is the single resolution point** — no other node reads `gamma-style-guides.yaml` at runtime (explicit AC).
- D3: **Source wins LOUDLY** — content overrides silent by design (the invariant); *structural* collisions (e.g., source demands Studio treatment under a Classic pick) surfaced as a named conflict in the artifact, resolved for source, discrepancy on the record.
- D4: Fatigue mitigation = **last-used-per-corpus pre-selection with visible provenance**, one-keystroke confirm; NO bypass flag, NO auto-accept-on-timeout. Pick telemetry from artifact provenance = roster-health signal (90% single-guide concentration → CD-substrate session, not ceremony weakening).
- D5: Dan's S8 sign-off bars: (i) picked guide's **fingerprint on the wire** (actual Gamma request body); (ii) source detail intact on the SAME wire, source value present where both addressed a field (one briefed slide rendered live); (iii) fail-loud proven by a deliberate no-pick failure pre-spend; (iv) envelope chain digest-auditable end-to-end, resolution surviving resume/recover intact; (v) skip honesty.
- D6: CD's 4.75 contract survives ≥1 solo live exercise BEFORE S8 is scheduled. Advisory boundary intact: CD authors, validator backstops, Marcus transports, runner enforces — canonicalization must not make CD a run-state mutator.
- D-skip: legitimate skips ONLY: (i) resume/recover with a valid artifact already in the envelope (idempotent re-entry, no re-resolution mid-run); (ii) run types with no visual deliverable. "No pick" is NEVER a skip path post-S4.

**Marcus (operator experience):**
- X1: **One kickoff meeting, three beats** (look → material → contract) with an up-front framing line naming all three and the known end; never a surprise gate N+1. G0E and G0R stay SEPARATE beats (inventory correctness vs pedagogical contract — collapsing means ratifying LOs from an unconfirmed manifest; on the record).
- X2: **Ceremony canonical; deliberation not** (ratified interpretation of the operator's "canonical on every run"): the gate fires every run, state displayed, operator holds the pen — provenance-visible reuse with one-key "reuse / redo fresh" IS the gate firing. Fast-paths: pick = course-scoped reuse; G0E = corpus-fingerprint-gated (any file change → fresh, with a DIFF shown, not the full manifest); G0R = conservative (fingerprint AND directive/intent unchanged; any LO edit or waiver → always fresh); G2B+ = never (they judge fresh artifacts); research = cache reuse when LOs unchanged, provenance line in workbook footer.
- X3: **CD invisible** — no fourth visible ceremony; operator sees CD's OUTPUT (a resolved-directive line inside an existing pause, or a surfaced conflict). Named dissent if violated.
- X4: **Failure narrations are in-scope AC**, not follow-ons: picker publish flake → retrigger / inline-text pick (registry is SSOT, page is convenience) / provenance-reuse, operator's numbered choice; G0R inadequacy → stop-and-talk naming WHICH objective and WHY, options = park-objective (rec) / add-material (+access coaching) / explicit logged waiver; research creds absent → detected AT INTAKE, headed-relogin offer, degrade = visible "research enrichment skipped — credentials unavailable" marker (wired-but-token-gated honesty pattern, extended not reinvented).
- X5: Proof corpus = **the operator's next unproduced lesson** (adjacent to the concierge Part-1 module) — mints a real asset, exercises warm-callback against a real predecessor; a fully-outside corpus may run as a SECOND cheaper generalization probe. Defaults: prior pick per course else standard-A; A/B on a corpus's first run, single on re-runs.

---

## 3. Corpus criteria for S8 (converged; operator names the lesson at S8-open)

Structurally non-tejal on the axes S7 generalized (chapter count/section shape) · literature-rich (DOI-indexed domain — empty TexasRows must be an honest red) · mixed source types (PDF + docx/deck + image folder + ideally one URL-directive) · one genuine adequacy wrinkle (a THIN objective G0R can catch) · material the operator knows cold · **fresh to the pipeline** (never side-doored; no cached prefixes — NB likely disqualifies Part-3, which fed Leg-C floor probes) · standard `course-content/courses/<lesson_slug>/` layout · **zero corpus-specific diffs** (corpus name in run-dir, nowhere in `git diff`).

## 4. Roadmap bindings

- This arc = the Horizon-2/BETA-§8 closing move; **Batch-LLM epic GO at arc close is conditional on the S0 T6b/c/d equivalence mapping** (J3).
- STATE-OF-THE-APP §11 refresh at arc close (currently one refresh behind).
- Flag-retirement follow-ons + prose-uplift arc filed in deferred-inventory at S0.
- Codex shadow-monitor NOT armed at green-light time (newest ledger = 2026-06-30/2026-07-03); operator arms if desired before dev opens.

## 5. Governance

Full BMAD spine per story: spec → validator (where applicable) → fresh general-purpose dev agent RED-first → 3-lane `bmad-code-review` → live proof → party/dual-gate close per story risk. Single Claude dev lane + Codex shadow-monitor (ledger-only). SPOC-is-the-goal guardrail affirmed by every seat. Protected invariants (VO↔on-screen; source-detail→Gamma conveyance) carry named checks on S1/S2/S8.

---

## 6. S0 ADDENDUM — charter deliverables executed (2026-07-06, same session)

**(a) M-pre discharged — xdist suspect is NOT real.** `tests/marcus/lesson_plan/test_workbook_producer.py::test_ac12_dp6_fresh_required_blocks_reuse_stamp` PASSED in 1.72s at `-n 0`. The session-15 failure is confirmed an xdist concurrency artifact; workbook residual gap #6 CLOSED. Standing xdist rule (one `-n 0` confirmation before triaging any new parallel red) carries for the arc.

**(b) W2 contract authored.** [`styleguide-binding-cd-contract-2026-07-06.md`](styleguide-binding-cd-contract-2026-07-06.md) — picker commits a *reference* (name+version) into the directive pre-run-dir; CD is the single resolution point writing one `ResolvedCreativeDirective` (or explicit skip-record) into the envelope; Gary composes from the envelope, never the SSOT yaml; source wins loudly via the layering manifest. S1 and S2 implement against that page.

**(c) J3 T6b/c/d equivalence mapping (governs the Batch-LLM GO at arc close):**
- **T6d** (Tracy on the trial path + review-only ack) → **COVERED by S6**, exceeded on substance: the braid-S3 runner hook already attaches Tracy at 04.55; S6 makes live dispatch canonical and threads *cited* entries to the workbook. S6 carries one added AC: the SPOC narrates the dispatched/cited research result post-04.55 (review-only, non-blocking — T6d's ack surface).
- **T6b** (readable Marcus-facing ingestion report at G1) → **SPIRIT COVERED by S5's Beat-2** (the G0E typed source manifest is a richer intake-side report than T6b asked for); the G1 summary's S0.2 timing defect is NOT fixed by this arc → filed as `g1-ingestion-report-timing-residual` in deferred-inventory.
- **T6c** (content-free lesson-plan-review pause AFTER Irene Pass-1) → **PARTIAL**: G0R ratifies the LO contract BEFORE Pass-1; post-Pass-1 plan-unit review remains folded (G1A/04A, fold_with G2C). Precedented cheap wake exists (07B-gate/11-gate membership pattern; manifest edit → lockstep regime applies). **Decision at S5 spec-time: in-arc rider vs deferral** (`t6c-post-pass1-plan-review-wake` filed). Per J3's conservative ruling, the arc-close Batch-LLM GO evaluation treats T6c per that outcome — a deferral means the GO carries T6c as a named open item for the party to weigh, not an automatic block on an otherwise-clean close.

**(d) W3 Tier ruling (pre-dev, as demanded):** the G0 default flip lives in `app/marcus/orchestrator/g0_enrichment_wiring.py` (+ possibly `production_runner.py`) — **neither is a `block_mode_trigger_paths` member**, no `pipeline-manifest.yaml` edit is needed (nodes + edges already compiled), no pack prose changes. **Ruling: Tier-1; lockstep regime not triggered by the flip itself.** EXCEPTION: if S5 absorbs the T6c G1A wake, THAT piece edits the manifest (`fold_with` clear) → regime doc read at T1 + the woken-via-membership precedent applies (topology refinement within v4.2; pack stays v4.2; party consent already in this record's context but re-confirmed at S5 spec).

**(e) Deferred-inventory filings landed** (§Named-But-Not-Filed → "Canonical Production Conversation arc — fenced-out items"): prose-uplift arc (J2), two flag retirements (A4, trigger S8-green), Consensus enablement (M2), the T6b timing residual, and the conditional T6c wake.

**S0 status: COMPLETE.** S1 (CD activation contract) and S2 (picker wiring) are unblocked; S1 spec authoring is the next action.
