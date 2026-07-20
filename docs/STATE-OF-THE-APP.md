# State of the App — Canonical Status Synthesis

**Date:** 2026-06-19 · **Last updated:** 2026-07-20 (**Project Quality Scorecard arc COMPLETE + LIVE-WIRED + MERGED TO MASTER `656e6241`** — 8-dimension scorecard (Q1–Q3) + Epic Q4 live-wiring into the SPOC runtime (operator-surface quality tile, run-end `quality-final-report.md`, HUD flight-deck render); live-equality witnesses ride the R2 trial. Prior reconcile 2026-07-17: Epics 41/42/43 CLOSED, master `12775df6`, KG `bfefcc1b`.)
**Status:** Canonical orientation doc. Single source of truth for "where the development plan actually stands."

> **2026-07-20 CURRENT SNAPSHOT — YOU ARE HERE NOW.** Branch `dev/quality-scorecard-epic-2026-07-19` (HEAD `9cbf2512`), **merged `--no-ff` to `master` `656e6241`** (pushed). The **Project Quality Scorecard** is now BUILT end-to-end and LIVE-WIRED into the Marcus-SPOC runtime, and the whole arc is on master:
> - **8-dimension scorecard (Epics Q1+Q2+Q3) COMPLETE** — DID 65/B-, cost 62/B-, coverage 58/C, fidelity 58/C, capability 50/C, tracker-coherence 38/D, lane-discipline 75/B, calibration 25/D (report-only). 8 pairwise-disjoint leak namespaces, `ranked_project_leaks=13`, coverage clean; every honesty pin proven RED-under-seeded-edit. Equal-weight scoring; band+ranked-leaks+trend reporting (no false-precise /100). Lives at `app/quality/` (GL-3 clean leaf) + `docs/quality/project-quality-scorecard.md`.
> - **Epic Q4 — Live-Wiring COMPLETE** — 6/6 party-greenlit-before-dev (Tier-2 block-mode substrate, QLW-1..16). The scorecard renders into the runtime on THREE operator-facing surfaces: a compact `quality` tile on `operator-surface.json` (Q4.1, additive `operator-surface.v1`, no schema/pack bump), a per-run standalone `state/config/runs/<trial_id>/quality-final-report.md` (Q4.2, atomic write, terminal-only), and the HUD flight-deck render incl. the `client.py` POLL_JS mirror (Q4.3). The operator now sees the honest Band + ranked leaks + trend + scorecard staleness at the accept/reject/edit decision moment. Reads the COMMITTED scorecard doc, never live signals (determinism-as-honesty); zero-lie fail-soft on every surface.
> - **Honestly deferred (operator-gated):** the LIVE equality witnesses (report/tile == independently-computed env truth) ride the **R2 operator-steered live trial** — the BUILD is offline-proven, no surface claims live-proven. The **fresh-naive-holdout measurement** (`reading-path-fresh-naive-holdout-pre-trial` = DID Leak-4) remains owed; recording it flips CAL1 weak→strong.
> - **Retention note:** SOTA §11 you-are-here reconciliation + the roll-down of the SUPERSEDED 2026-07-10 snapshot below to `STATE-OF-THE-APP.history.md` are a small follow-up for the next Class-S session (banner freshness prioritized this pass).
>
> **2026-07-17 PRIOR SNAPSHOT.** Branch `trial/c1m1-p1-2026-07-17` (cut off consolidated `master` `12775df6`). The product is the **Marcus-SPOC local runtime orchestrator**: a host-machine runtime that drives an actual app instance; **not** an externally hosted app and not a proofing/concierge vehicle. Since the 2026-07-10 snapshot below, three waves landed and master consolidated:
> - **Presentation-Support Workbook (Epics 36–40) ✅ live gate PASSED (2026-07-15)** — first complete runner-verified MD+DOCX workbook (trial `a940c5eb`); Epic 38 CLOSED; LO-overlay bridge fixed. Consolidated to master.
> - **Resume-Walk Dispatch Integrity (Epic 41) ✅ CLOSED** — the `bc747b51` frozen-run fix: root cause was **budget starvation** (`max_specialist_calls=1`), not keyless resume. Throttle removed; `MARCUS_TRIAL_BUDGET_USD` is now an **enforced stop**; silent specialist skip **fails loud in both walks**; resume/recover runs a live-env preflight.
> - **Operator-Surface Next-Pass (Epic 42) ✅ CLOSED** — the flight-deck HUD **survives pause** + launches windowless (`localhost:8791`); a **public read-only overlay** over ngrok (`deplete-courier-blurt.ngrok-free.dev`, allowlist-scrubbed); the **G_SETTINGS pre-walk settings gate ("G0S", default-ON)** with a 16-toggle readout.
> - **HIL Surface Tabular Coverage (Epic 43) ✅ CLOSED** — the trigger was a live trial whose FIRST gate dumped **raw YAML**; now **all 14 operator-reviewed gate surfaces render bespoke tables** via a content-type renderer registry, pinned by a RED-first coverage ratchet (allowlist EMPTY) + a SPOC↔projector anti-drift parity guard.
> - **Master consolidated `12775df6`** (workbook wave merged `--no-ff`); fresh `trial/c1m1-p1-2026-07-17` cut for the R2 run. KG regenerated at `bfefcc1b` (2699 nodes / 5164 edges / 7 layers). ONBOARDING/guides refreshed 2026-07-17.
> - **Live frontier (operator next):** the **R2 operator-steered live trial** on corpus `tejal-apc-c1m1-p1-call` — witnesses the tabular G0 directive + every gate table, the G0S default-ON pause, the windowless + public HUD, and a budget-braked, now-completable run. bc747b51 is honestly recoverable (or a fresh trial). The 2026-07-10 snapshot below is SUPERSEDED.
>
> **(SUPERSEDED 2026-07-10 SNAPSHOT, retained for provenance.)** Branch `dev/agentic-research-foundations-2026-07-10`. The current product is still the **Marcus-SPOC local runtime orchestrator**: a host-machine runtime that drives an actual app instance; it is **not** an externally hosted runtime app and not a proofing/concierge vehicle. The latest closed work and live frontier are:
> - **S7 Phase-2 A-D / S8 / Six Mine-Now / Batch LLM v1:** remain CLOSED (do not reopen). Binding letters unchanged.
> - **Agentic Research Foundations (R0–R7) PROMOTED/CLOSED** on this branch — posture-aware detective (opt-in `MARCUS_RESEARCH_DETECTIVE_LIVE`, default **OFF**); Scite+Consensus triangulation; credibility labels; Jefferson seam (live fenced); Irene intake; R7 hard pause before Pass-2. Close: `agentic-research-foundations-promote-2026-07-10.md`.
> - **Workbook research products (W0–W4) CLOSED** — shared research packet → encyclopedia **Research Glossary** + **Research Trends/hot-topics** in workbook MD/DOCX. Close: `workbook-research-products-close-2026-07-10.md`. Live W4: `evidence/workbook-w4-20260711T021418Z/`.
> - **TRAIL trio CLOSED under fences** — OpenAlex adapter (metadata+OA links; LIVE `openalex-live-20260711T024437Z`); glossary capability-note polish (not human SME-reviewed); semantic WARN-only tripwire substrate (full claim↔source audit still TRAIL). Close: `trail-trio-close-2026-07-10.md`.
> - **Live frontier (operator-chosen next):** **Workbook artifact customization** (interactive design session). Residuals parked: full semantic audit calibration, ERIC/LoC, detective default-ON policy, Tejal motion/node-15/Desmond brief, Batch A1-EXT. Do **not** burn novel HAI/PHS ingest unless explicitly pulled.
> - **Required monitors/gates.** BMAD workflow remains preferred for multi-story work; party mode is required for green-light/close consensus. Live local runtime testing is indispensable as components are authored or edited. **Styleguide governance:** never ad-hoc-edit a completed/approved registry guide — add a named variant.
>
> **Short-term roadmap (next 1-2 sessions; refreshed 2026-07-15 EVE — post-roadmap-conversation).** ✅ Epic 38 CLOSED (retro done; 38.2 re-homed to the 39-wave; MERGE ratified for overlay exercises; Paid-Run Economy Protocol bound — `wave-3940-kickoff-party-record-2026-07-15.md`). (1) Master consolidation → (2) answer-leak strip → (3) 37-2b story dispatch under the protocol (probes → batched governed runs A/B → off-frozen-lesson finale). Superseded text: (1) **CLOSE EPIC 38**: land the Pass-1 head-self-parent normalization (in flight), run ONE clean governed live verification (workbook LO section must render real statements — the LO-overlay bridge fix `9d4f0593` is already in), then party green-light + `bmad-code-review` close Stories 38.1 + 38.3a, then the REQUIRED epic-38 retrospective. (2) **Post-close roadmap conversation** (operator + party): disposition of 38.2 Ask-B, Epics 39/40 sequencing, master consolidation timing, and the cross-SME Phase-2 question. Residuals parked: full-deck motion, node-15 handoff contribution, Desmond brief-on-disk, classic-condense HELR; Batch A1-EXT (TRAIL); full semantic claim audit; `langsmith-start-receipt-offline-stamp`.
>
> **Longer roadmap to project completion.** Major lanes: (1) real source ingestion/enrichment for HAI video/slides and PHS Confluence/Canvas; (2) source-purpose-aware lesson planning with operator-owned LO ratification and explicit workflow selection; (3) collateral projector families beyond workbook while preserving the input-side/output-side boundary; (4) course/SME registry completion for styleguide, voice, attribution, and approval routing; (5) full local Marcus-SPOC production proof on real course content; (6) trust-complete hardening still open from prior arcs, including narration fidelity flag activation, reading-path fresh-naive holdout, bundle-carrier robustness, recover/error-pause hardening, and source/research quality debts; (7) Batch A1-EXT all-node tiering only if/when a second LLM node is proven batch-eligible.
>
> **Deferred work picture.** The standing backlog remains substantial and intentional: Epics 15-18 (learning/compound intelligence, bounded autonomy, research/reference services, additional asset families), greenfield specialists as needed, named active-arc follow-ons in `deferred-inventory.md` (including parked HELR `irene-pass2-figure-contradiction-classic-condense` with 2026-07-10 speakable down-payment), Batch A1-EXT TRAIL, full semantic claim↔source audit (WARN tripwire only landed), ERIC/LoC adapters, Gamma/styleguide carried work from the older branch context, course-source operator holds, S7/S8 prose/quality follow-ons, and governance hygiene (knowledge graph / onboarding refresh, stale tracker reconciliation, and untracked evidence cleanup). Treat `deferred-inventory.md` as the detailed ledger; this section is the current product-path synthesis.
>
> **Story/epic progression through completion.** Closed foundation: migration Slabs 1-7c, BETA Phase 1, P2 fidelity/perception, variant/voice, clustering, braid/workbook/research/SPOC, P5 downstream consumption, directed/enhanced VO, Concierge Production Substrate, Canonical Production Conversation S0-S6, S7 workbook generalization, S7 Phase-2 A-D, **S8 FULLY COMPLETE**, post-S8 Irene-literal→Gary-preserve, **Batch LLM Execution Mode v1 CLOSED**, **Agentic Research Foundations PROMOTED**, **Workbook research products CLOSED**, **TRAIL trio (OpenAlex + glossary polish + semantic WARN tripwire) CLOSED under fences**. Active: workbook customization. Completion horizon: Epics 15-18 plus selected greenfield specialists convert the proven local runtime into a multi-course, multi-asset, learning/intelligence platform.

> **🧭 FRAMING PRINCIPLE — the goal is the PRODUCT, not the proofing vehicle (operator-stated 2026-06-30; load-bearing).** Two distinct "Marcus" entities must never be conflated when reading "where we are":
> - **Marcus-SPOC** = the **runtime orchestrator** — the operator-facing conversational surface that drives an actual *instance of the APP and its production runtime*. **This is the only product goal.** The codebase exists to make the SPOC-orchestrated runtime correct and trustworthy.
> - **BMAD-persona Marcus** (the planning/dev/exploratory persona, the one with the sanctum) running **"concierge"-style exploratory / trial / proofing runs** is a different thing entirely. Those runs happen **off the books** — they are a **means of discovery, not an end.** They exercise the pipeline and can surface real production-codebase defects worth fixing on their own merits.
> - **We do NOT design or shape the production codebase to make those off-the-books concierge/proofing runs work.** When a proofing run finds something, we fix it because it's a genuine production-codebase problem **for the product's (the SPOC runtime's) sake** — never to "make the concierge run pass." Every fix earns its place by improving the real product. Read every "concierge … arc" below through this lens: it names a **body of production-codebase hardening that proofing runs helped surface and prioritize**, *not* a design target of its own.


> History archived to [`STATE-OF-THE-APP.history.md`](STATE-OF-THE-APP.history.md) — superseded status banners + §11.1/§11.5 you-are-here snapshots (2026-07-01 and earlier). Retention: current + 1 prior stays here (the FRAMING PRINCIPLE guardrail banner, referenced by session-START §0, stays permanently).

---

## 1. The three-layer "done" — why status feels disorienting

The single biggest source of confusion is that **three different things each have their own "done," and they are routinely conflated.** Read every status claim through this lens:

| Layer | What "done" means here | Honest status |
|---|---|---|
| **A. Migration substrate** (Slabs 1–7c) | BMAD stories closed in `sprint-status.yaml` | **Largely shipped & BMAD-closed.** `migration-master-status: shipped`. Slabs 1–6 done; 7a 8/8, 7b done, 7c 36/36 (closed 2026-05-07). |
| **B. Production trial engine** (G0→completion) | The runtime actually produces a narrated-deck lesson end-to-end on a real corpus | **Validated.** Trial-4 PASS; engine error-free ×2 + Marcus-SPOC error-free ×2 on disk (2026-06-19). |
| **C. BETA spec as written** (`beta-spec-2026-06-19.md §8`) | The full conversational product: a+b+c+e through Marcus-SPOC with binding picks, d+f present/carved, §5 quality infra green, error-free twice | **NOT met.** Partially demonstrated under narrow interpretations (see §4). |
| **D. Product quality** (narration fidelity) | The narration describes what is actually on the slide, in scan order | **🟢 Grounding leg FIXED (2026-06-21); reading-path being productized (P2-4c, 2026-06-23).** Pass-2 grounds on the perceived rendered slide (`PerceptionArtifact`), fail-loud-G5-guarded (P2-1/2/3 + AC-6 live strike). Reading-path: catalog **v1.1** (compositional tuple) ratified; classifier built (**P2-4c S1+S2+S3 DONE**). ⚠️ The **0.93** held-out number is the **catalog-approach (Claude-labeled) vs gold — NOT the built classifier**, which is UNMEASURED (a live dry-run scored 0.071 on stale perceptions). **P2-4b = real calibration** (re-perceive → recalibrate → measure), not a rubber-stamp. *(Was: "🔴 Regressed — disaster-level.")* |

**The trap:** Layer A's "shipped" and Layer B's "validated" are real and earned. They do **not** imply Layer C ("BETA met"). **Layer D's grounding regression is now closed** (2026-06-21) — narration is perception-grounded and detector-guarded; the residual Layer-D gap is reading-path *scan-order calibration* (P2-4b, operator-gated), not the confident-wrong hallucination the BETA path used to mask.

---

## 2. ✅ VALIDATED — what is demonstrated to work (Layer B)

Exercised against the live frozen corpus (`tejal-apc-c1-m1-p2-trends`), with real APIs and real spend:

- **Full G0→completion pipeline.** Ingest corpus → compose directive → draft storyboards → render **Gamma slides** → generate **ElevenLabs narration** → QA → assemble **compositor bundle + Descript hand-off** → **publish storyboards to GitHub Pages.** First complete run 2026-06-12 (cycle 5); zero-fix fresh certification 2026-06-12 (cycle 6); Trial-4 (`d7ad4dac`) G0→completion, $0.24.
- **HIL gate machinery.** Multi-gate pause/resume (G1→G2C first live-crossed in Trial-3); woken G2B (variant) + G4A (voice) review gates; durable checkpoints; cross-process verdict replay.
- **Error-pause taxonomy (WAVE-0).** Live-path crashes convert to *recoverable error-pauses* instead of killing trials — the operator's "unimpeachable error-flagging platform first" priority, largely delivered.
- **Auto-retry on known LLM-variance** — absorbs Irene slide-join variance in-dispatch (the "error-free" keystone).
- **Picker binding (`select` verb)** — operator voice pick re-routes to synthesis, proven live (run `710684c0`, Sarah at synthesis).
- **Marcus conversational SPOC** — narrates capabilities **a–g** per gate, drove a full run to error-free completion **twice** (`e2291039` + `74f72a4c`).
- **§02A→wrangler schema coherence** (Epic 34, 7/7) — producer/consumer vocabulary fork closed; integration ratchet installed.
- **Perception-grounded narration fidelity** (P2 arc, 2026-06-21) — Pass-2 narrates from the perceived rendered slide (`PerceptionArtifact`), not the brief; a fail-loud G5 fidelity detector fails Class-A on unsupported visual claims. **Live-verified:** the AC-6 strike ran live Pass-2 over the frozen corpus → committed detector GREEN 8/8 + held-out (independently re-judged). Reading-path scan-order *machinery* shipped (P2-4a); scan-order *calibration accuracy* is P2-4b (operator-gated).

**One-line reality:** *The platform reliably produces a narrated slide deck (text + visuals + audio + published storyboard) from a corpus, with operator review gates and recoverable errors, driven by a conversational Marcus.*

---

## 3. ✅ RESOLVED (2026-06-21) — was: THE CRIPPLING — fidelity regression + a metric that cannot see it (Layer D)

> **✅ RESOLVED via the P2 arc (2026-06-21).** All three failure modes below are closed: **(1)** perception grounding restored — Pass-2 grounds on the perceived rendered slide via the rich `PerceptionArtifact` (P2-2 vision node + P2-3 grounding fix), demoting the brief to subordinate context; the $4.5T/$5.2T drift no longer reproduces (AC-6 live strike: detector GREEN 8/8 + held-out). **(2)** reading-path grammar — the severed scan-order machinery (closed `reading_path` enum + classifier + verify-node + emission lint + parity) was natively rebuilt in **P2-4a**; the repertoire-growth + real-slide calibration leg is **P2-4b (operator-gated)**. **(3)** the blind metric — a **fail-loud G5-class fidelity detector (P2-1)** now fails Class-A when narration references a visual the perception layer does not see, so "error-free" can no longer rise with hallucination volume. The deferred entry `fidelity-metric-blind-to-perception-regression` is **STRUCK**. The historical description below is retained for provenance.

This **was** what made BETA feel "crippled," and it **was more dangerous than a flaky pipeline:**

1. **Perception grounding lost.** Pass-2 narration grounds on the slide **brief**, not the rendered PNG. Confirmed evidence: slide-01 narrates a "$5.2 trillion line + paired bars" dual-axis chart that was **never rendered** (the slide shows $4.5T / 74% / 3x stat callouts + a building photo), with a wrong figure ($5.2T vs $4.5T). Root cause: the perception layer was dropped at the 2026-04-24 upstream severance.
2. **Reading-path grammar lost.** The scan-order classification machinery (Z/F/center-out/triptych enum + `reading_path` schema field + emission lint + heuristic classifier) was a 5-part lockstep upstream; at severance **only the worked-examples doc was absorbed**. The narration no longer keys to a slide's scan pattern. Standing operator complaint: "narration doesn't follow the natural scan of the slide."
3. **🎯 The success metric is BLIND to it.** G5 checks script/audio **mechanics** (WPM floor, coverage), not "does the narration describe what is actually on the slide." Therefore a run can complete **"error-free" while producing pedagogically wrong narration** — and every clean run *increases the volume of confident, authoritative-sounding hallucination*. This is worse than a visibly flaky run.

**Implication for the repair:** restoring perception + reading-path is necessary but **not sufficient**. The arc MUST also ship a **fail-loud fidelity detector** (a G5-class check that fails Class-A when narration references a visual the perception layer does not see), or the repair can silently re-regress and "error-free" remains untrustworthy.

This is a regression against **Epic 2A fidelity intent** ("perception confirmed, not blind; provenance traceable") and the product's core value proposition.

---

## 4. BETA spec §8 scorecard — capability by capability

Scored against `beta-spec-2026-06-19.md` §1–§3 + §8. **Literal engine criterion (§2 mechanics) and spec-spirit (§8 full path) are scored separately on purpose.**

| Cap (spec ref) | Spec intent | Built? | Validated in a trial? | Verdict |
|---|---|---|---|---|
| **SPOC** (§4.7) | Conversational Marcus; operator never touches raw CLI | Partial — `marcus_spoc.py` narrates a–g + submits verdicts | Yes ×2, but **approve-path / scripted decisions** | **PARTIAL** — no free-form NL; subprocess-over-seam, not SKILL.md persona in IDE chat |
| **(a) sources** (§4.1) | Confirm per-source treatment in dialogue | Partial — reads `directive.yaml`, prints roles | Surfaced in SPOC transcript | **PARTIAL** — in-conversation re-treat not deeply exercised |
| **(b) ingestion** (§4.2) | Readable report; close T4-F1 | Partial — S0.2 wired manifest; **timing bug remains** | G1 no longer false-rejects | **PARTIAL** — summary can still show "Emitted artifacts: none" mid-node |
| **(c) lesson plan** (§4.3) | Dedicated plan-review pause | Thin — reads `irene-pass1.md` if present | Mentioned in SPOC | **PARTIAL** — no real G1.x review/edit loop |
| **(d) research** (§4.5) | Tracy on trial path; operator ack (non-blocking) | **No** on production path | SPOC reports "none dispatched" | **FAIL/CARVED → SPECCED (braid S3)** — Epic-28 Tracy module + Irene→Tracy→Texas bridge built but production-path orphaned; braid **S3 (thin research wiring)** specs the runner wire-through → cited workbook entries (DP2, ratification 2026-06-24). One Tracy (research-intent) + Texas (dispatch); the "typography" registry line was stale (Story 0, fixed) |
| **(e) variants** (§4.4) | N-dispatch, per-slide bind | **Yes (A/B)** — per-variant Gamma settings + genuine per-slide selection | **Yes ×2 (2026-06-24)** — `7d530d0a` + mirror `6cb8eafd`, real Playwright chooser clicks, error-free to Descript | **PASS (A/B per-slide)** — arbitrary-N + variant-B figure-grounding are filed follow-ons; *(was FAIL — single-dispatch)* |
| **(e) voice** (§4.4) | Voice candidates → bind | **Yes** (mechanics) | Voice select→synthesis **proven** (`710684c0`) | **PASS (mechanics)** — but exercised *separately*, not inside the twice-gate runs |
| **(e) clustering/pace** (§4.4) | Read-only surface | Read-only present | Shown in SPOC | **PASS (read-only)** |
| **(f) motion** (§4.6) | Honest motion-plan artifact OR written carve-out | Carved **in practice** | SPOC narrates "no motion clips" | **CARVED (implicit)** — no producer; carve-out **not party-ratified in writing** |
| **(g) reading-path** (§6) | Suggest-level only for BETA | **Restored + SHIPPED LLM-first** — gpt-5.5 authoritative tuple producer; geometry → telemetry; Irene conformance advisory | Grounding: AC-6 strike GREEN 8/8 + held-out. Reading-path: pipeline completes G0→done with operator-validated narration↔layout; numbers on **consumed-14** (resubstitution) | **PASS (grounding + LLM-first reading-path SHIPPED)** — exceeds the BETA suggest-level bar. **Residual:** generalization unproven off the consumed-14 → **fresh naive holdout** is the binding post-trial gate. *(Was: BUILT-BUT-UNCALIBRATED; the P2-4c-classifier framing is superseded.)* |

### §2 "error-free twice" — literal vs spirit

- **Literal engine criterion: MET.** Two consecutive error-free runs on the frozen corpus, no substrate change between, zero Class-A, Class-B within budget (auto-retry absorbed Irene variance). Evidence: `beta-error-free-twice-milestone-2026-06-19.md`; runs `b7919f65` + `bb76170c` verified `completed`.
- **§8 spirit: NOT MET.** §8 requires Marcus-SPOC conversation exercising **a+b+c+e with binding picks**, d+f present-or-carved, **and §5 quality infra green.** Actual: a–g narrated in template form (not richly exercised); **(e) voice binding proven *separately*, not inside the qualifying runs** (both used approve-path + default voice); (e) variants absent; (d) not wired; (f) carved implicitly; §5 partial (crash-guard + retry yes; full per-gate live-dispatch harness incomplete).

**Net:** the reliability gate passed on a **reduced path** while the product-value gates failed. "Core gate MET" (per the session handoff) is true only for Layer-B engine reliability — not for Layer-C BETA-to-spec.

---

## 5. The two epic universes & tracker reality

Two parallel planning stacks coexist — the other big source of disorientation.

| Track | Artifact | Scope | State |
|---|---|---|---|
| **Legacy APP plan** | `epics.md` | 22 epics / 97 stories | Epics 1–14 + SB **done** (MVP gate passed); 15–18 **backlog**; clusters 19–24/20c partial |
| **LangChain/LangGraph migration** | `epics-langchain-langgraph-migration.md` + Slabs 7a/7b/7c | 9 epics / 56 stories / 184 pts | **shipped**; Slabs 1–6 done; 7a/7b done; 7c 36/36 done |

### Tracker drift — three sources disagree (governance finding)

`sprint-status.yaml` was last meaningfully updated **2026-05-22** (an Epic-34 tombstone). It contains **zero** BETA / Trial-5 / S0.x / error-free entries (verified: grep `beta|trial-5|S0|error-free` → 0 hits). The June BETA program ran **Claude-direct quick-dev + trials**, not `bmad-create-story` → `bmad-dev-story` → sprint flip. Consequence — three sources now disagree:

- **Charter** (`beta-trial-sequence-charter`): mid-session notes still say T5a / S0.4 *pending* (stale — code landed after).
- **Handoff** (`SESSION-HANDOFF.md`): says BETA core gate *MET*.
- **Sprint-status**: says *nothing happened* in June.

`deferred-inventory.md` is the **only live, current map** of gaps. Harmonizing these is the explicit purpose of the harmonization arc that follows this doc.

---

## 6. ⏸️ DEFERRED — filed, near-term reactivatable (`deferred-inventory.md`)

- 🟠 **`v5-manifest-coherence-reconciliation`** — *binding "pre-next-trial," not someday.* Production-canonical v5 pack has no manifest-coherence guard; highest-probability bite before the next content trial.
- **Trial-3 findings still open:** `#7` pause-write atomicity; `#8` `max_specialist_calls` segment-cap semantics.
- **Slab 6.1 substrate enhancements:** multi-pass envelope path X/Y; compiled-edge traversal (needed before non-linear manifests); trial-envelope lifecycle invariants; real LangSmith trace binding.
- **Trial-4 follow-ons:** `live-trial-replay-baseline`; `g4b-input-package-hil-wake`; `generalized-membership-wake-toggle`.
- **BETA carry-forward:** ~~`beta-voice-select-wpm-qa-interaction`~~ → **RESOLVED 2026-06-19 (P1)** (voice-agnostic WPM intelligibility band; `spec-p1-voice-agnostic-wpm-floor.md`); `trial-4-binding-variant-voice-picker`; `beta-d-research-review-trial-path-attach`; `beta-motion-synthesis-data-plane`; `beta-generality-across-corpora`; `beta-marcus-namespace-collision-rename`; ~~the merged perception+reading-path arc~~ → **DONE 2026-06-21** (P2-1/2/3/4a closed + regression struck; only `p2-4b-reading-path-repertoire-and-conformance-corpus` remains, operator-gated).
- **Housekeeping:** Slab 7b/7c review NITs (digest-helper extraction, scanner staleness, sidecar cleanups); repo-wide ruff debt.

**Counts:** ~30–31 backlog-epic stories (Epics 15/16/17/18 + greenfield specialists) + 4 deferred-stories-in-active-epics + a long named-follow-on tail.

---

## 7. 🔭 ASPIRATIONAL — epics on the shelf (specced, not built)

- **Epic 15 — Learning & Compound Intelligence** (7 stories): turn tracked runs into organizational intelligence. Gated on "first tracked trial completed" — **that gate is now arguably met**, making this the most reactivation-ready aspirational epic.
- **Epic 16 — Bounded Autonomy Expansion** (5): Marcus autonomous routing on routine decisions. Depends on Epic 15 evidence.
- **Epic 17 — Research & Reference Services** (5): related-resources, citation injection, hypothesis-research mode (Tracy's full scope; BETA (d) is a thin slice).
- **Epic 18 — Additional Asset Families** (7): cases, quizzes, discussions, handouts, **podcasts**, diagrams. 18-7 framework gates the rest; podcasts/infographics ship as *new pack families*.
- **Lesson Planner MVP** (Epics 28–32): substantial schema substrate landed (31-1/31-2/31-3 — registries, log, producer ABC); **not wired into the production trial path.** Epic 28 (Tracy) module-complete but **production-path orphaned**.
- **Motion** (Epic 14 + kira): structurally present, never proven — converges with BETA T8.
- **Greenfield specialists** (Mike, Eli, Mira, Sally, Kim): empty sidecars; generate on-demand via the validated `bmad-create-specialist`.

---

## 8. Forward priorities (factored into the post-harmonization arc)

1. ~~**Voice↔WPM quick win**~~ — **✅ DONE (P1, 2026-06-19).** Resolved via `spec-p1-voice-agnostic-wpm-floor.md`: G5's WPM check became a voice-agnostic intelligibility band (Murat §5 ruling), so a non-default voice (Sarah's 128 WPM) no longer trips the floor; break-glass `wpm_breach_override` retained. Party green-light + T11 3-lane PASS. Capability-(e) voice-binding now completes error-free on non-default voices.
2. **Perception + reading-path REPAIR + ENHANCE** (the disaster arc) — **✅ grounding DONE (2026-06-21); reading-path ENHANCE actively building (2026-06-23).** Perception grounding restored + detector-guarded (P2-1/2/3 + AC-6 strike); P2-4a machinery shipped. The ENHANCE leg then went deeper than "calibrate the 7-enum": operator training tuned the catalog to a **compositional tuple** (v1.1, party+operator-ratified D1–D3), the **P2-4b methodology flipped** (Claude-labels → operator-confirm/deny; held-out **A6 0.93 PASS**), and a classifier refactor **P2-4c** is building it via NEW CYCLE Codex (**S1+S2 DONE**, S3 in flight). **Remaining:** P2-4c S3 (gpt-5.5 escalation) → T11; then **P2-4b finalize** = `run_live()` the built classifier vs the confirmed gold (pre-staged + self-tested). Follow-ons on the register: `reading-path-icon-set-cue`, `callout-intent-speech-act-axis-harvest`, κ-harness-NOT-WIRED.
3. **Governance / spec ratification** — ratify in writing what "BETA" means (engine-reliability Phase 1 vs full §8), and file the BETA remainder as real epics/stories so charter, handoff, and sprint-status stop drifting (§5).

---

## 9. Governance decision — RESOLVED (Option B, party-ratified 2026-06-19)

**Question:** how should the June BETA program be formally represented in BMAD?

**RESOLVED: Option B**, unanimous 5/5 in a fully-spawned party-mode round, operator-ratified. Ratify **"BETA Phase 1 = engine-reliability + voice-binding"** closed *in writing*; file only forward stories; **no retroactive Epic 35** (all five voices judged it audit-ledger fiction). `deferred-inventory.md` remains the single source of truth for gaps. Durable artifact: [`_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md`](../_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md) — which is also the **authority for the ratified forward path** (P3→P1→P2 structure in §8 above). Binding riders: "error-free" was rebranded **"error-free (mechanics only — fidelity unverified)"** until the P2 detector lands — **that condition is now MET (2026-06-21):** the P2-1 fail-loud fidelity detector shipped and the P2-3 grounding fix passed its AC-6 live regression-green strike, so fidelity is now *verified* (perception-grounded + detector-guarded), not merely mechanics. (The reading-path scan-order *accuracy* sub-claim still awaits P2-4b's operator corpus.) Deferred-inventory + cross-trial-learnings updates remain promoted from consultation to a **DoD gate** on every forward story.

---

## 10. Adjudication record — where the two analyses diverged

Both factual conflicts resolved against on-disk evidence, **in favor of the external analysis**:

1. **Slab 7c completion.** Session assessment cited "72% (26/36)"; external cited "done." Evidence: `slab-7c-retrospective.md` = **36/36 DONE, closed 2026-05-07**; `sprint-status.yaml:1620` = `done`. The 72% was a stale 2026-05-06 mid-marathon figure. **External correct.**
2. **sprint-status staleness.** External said "last meaningfully updated 2026-05-07"; actual last touch was **2026-05-22** (Epic-34 tombstone). Minor date error, but the substantive claim — that the tracker predates and omits all June BETA work — is **verified correct** (grep → 0 BETA entries).

**The external analysis's sharpest, correct contribution** (which the session assessment underweighted): *the success metric is blind to the fidelity regression — "error-free" masks confident-wrong output* (§3). This doc adopts that framing as load-bearing.

---

## 11. Project Pathway — Current Progression & Completion Horizons

> **PERMANENT, LOAD-BEARING SURFACE — keep updated.** This is the "where on the completion pathway are we" map. Refresh **§11.1 You-are-here** + the **§11.2 pathway tree** status glyphs at **every story/arc close**, and the **§11.5 progress table** at every arc close. Same anti-drift discipline as §4 (scorecard) and §5 (tracker reality). Status glyphs: ✅ done · 🔄 in flight · ⏸ operator/external-gated · ◐ partial · ❌ not started.
>
> **Execution model (NEW CYCLE):** substrate-impacting forward stories run **Codex T1–T10 (dev) → Claude T11 (`bmad-code-review` + party-mode close + commit + `done`-flip)**; party-mode green-light precedes dev on Tier-3 stories. Claude T11 may land small, party-ratified local hardenings but does not author the dev story. (Cleanup arcs run Claude-direct per CLAUDE.md.)

**Last pathway update:** 2026-07-17 (Epics 41/42/43 CLOSED — resume-walk dispatch integrity + operator-surface next-pass + HIL-surface tabular coverage; master consolidated `12775df6`; KG/ONBOARDING/guides refreshed; live frontier = the R2 operator-steered live trial).

### 11.1 You are here

**(2026-07-17 — CURRENT / YOU ARE HERE NOW) The GOAL is the Marcus-SPOC local runtime product.** Since the workbook live gate passed (2026-07-15), the operator ran a live Marcus-SPOC trial and it surfaced two classes of production defect that three epics then closed — all consolidated to `master` (`12775df6`) and now on `trial/c1m1-p1-2026-07-17`:

- **Resume-Walk Dispatch Integrity (Epic 41) ✅ CLOSED.** The `bc747b51` "frozen composed run" was diagnosed as **budget starvation** (`max_specialist_calls=1`), three nodes upstream of the loud symptom — not keyless resume. Fix: throttle **removed** (`d8fb959b`); `MARCUS_TRIAL_BUDGET_USD` is an **enforced stop** (`cf7df4fd`); silent specialist skip **fails loud in both walks** (`81fdc495`); resume/recover runs a live-env preflight (`3919c7fb`). The old workbook-seam "budget-guard deferred" debt is resolved.
- **Operator-Surface Next-Pass (Epic 42) ✅ CLOSED.** Local flight-deck HUD **survives pause** + windowless `CREATE_NO_WINDOW` (`localhost:8791`); a separate **public read-only overlay** (`app/hud/public.py`) over ngrok reserved domain (`deplete-courier-blurt.ngrok-free.dev`, positive-allowlist scrub — never secrets/card internals/export paths); 16-toggle settings readout + the **G_SETTINGS pre-walk gate ("G0S", default-ON wake-sentinel)** for confirm-or-change before the walk.
- **HIL Surface Tabular Coverage (Epic 43) ✅ CLOSED.** The trigger: a live trial's FIRST gate (G0 directive) dumped **raw YAML**; a sweep found 13 more gates emitting identity-only tables + dense JSON. Now **14 operator-reviewed content types → 14 bespoke tabular renderers** via a content-type renderer registry (`hil_tabular_projector.py`), the `GATE_TO_CONTENT_TYPE` bridge, a **RED-first coverage ratchet** (`GATE_CONTENT_TYPES` + shrink-only allowlist, now **EMPTY**), and a **SPOC↔projector anti-drift parity guard**. The durable fix is the ratchet, not the renderers — a prose AC had let the 42-1 projector false-close on 1-of-15 surfaces.

**Live frontier (operator next): the R2 operator-steered live trial** on corpus `tejal-apc-c1m1-p1-call` — witnesses the tabular G0 directive table, a purpose-built table at every gate pause, the G0S default-ON settings pause, the windowless localhost HUD + the public ngrok HUD, and a **budget-braked, now-completable** run. Runbook: `docs/admin-guide.md` §"Trial Integrity & Operator Surface" + `docs/operator/trial-run-runbook.md`.

**Standing state:** KG regenerated at `bfefcc1b` (2699 nodes / 5164 edges / 7 layers; 2026-07-17); ONBOARDING + user/dev/admin/specialist guides aligned same day; master consolidated `12775df6`; six immutable negative first-run-stands witnesses preserved. Three production observations filed (fix-on-own-merits only, SPOC-goal guardrail): `section-11-display-voice-candidates-model-binding-mismatch` (MED), `spoc-g0e-flagged-axis-diverges-from-projector-ungrounded` (LOW), G1A/G1.5/G4B/G5 not in the woken `ProductionGateId` set (renderers future-proof).

> **(SUPERSEDED you-are-here — 2026-07-15, retained for provenance)** **The GOAL is the Marcus-SPOC local runtime product. The fourth product deliverable — the presentation-support learner WORKBOOK (Epics 36-40 redesign) — ran END-TO-END for the first time on 2026-07-15: governed trial `a940c5eb` reached `status: completed` / `success: true` and emitted a runner-verified MD+DOCX workbook. Claim discipline (closure-party F1 correction): these runs used the FROZEN lesson itself — corpus `tejal-apc-c1-m1-p2-trends` (Tejal Part 2 "Trends/Case for Change") — so the witnessed claim is "the redesigned workbook pipeline live-proven end-to-end on the frozen lesson." Off-frozen-lesson generalization of the REDESIGNED producer (e.g. `tejal-c1m1-p3-opportunity`) and cross-SME generalization are both OPEN claims (the S7-era off-lesson proof covered the pre-redesign producer). Epic 38 is in CLOSURE; the post-close roadmap conversation is queued.**

Between 2026-07-10 and 07-15 (all on top of the S7/S8/plan-ratify baseline below):

- **Batch LLM Execution Mode v1 ✅ CLOSED** (opt-in vision batch transport; default realtime; workbook not batch-eligible).
- **Agentic Research Foundations R0–R7 ✅ PROMOTED** (posture-aware retrieval, evidence-hierarchy credibility, anti-fabrication intake, R7 detective hard-pause; `MARCUS_RESEARCH_DETECTIVE_LIVE` default OFF).
- **Workbook Research Products W0–W4 + TRAIL trio ✅ CLOSED** (research glossary + trends with empty-honesty; OpenAlex adapter; WARN-only semantic tripwire).
- **Operator HUD Epic 35 ✅ DONE + OPERATOR-USABLE** (all 10 stories; unanimous party re-verdict "performed to spec"; runtime-owned GET-only HUD server + ntfy notifier; legacy `run_hud.py` retired).
- **Presentation-Support Workbook redesign (Epics 36–40; planned end-to-end 2026-07-12):** Epic 36 ✅ done (prework producer, 4 stories); Epic 37 ◐ (37.1/2a/3/4 done; 37.2b/5/6 backlog); **Epic 38 🔄 CLOSING** (38.0 + 38.3b done; **38.1 + 38.3a live-gate PASSED** — first complete workbook); Epics 39/40 ❌ backlog.

**Epic-38 close DoD (the trigger for the post-close roadmap conversation):**

1. ✅ LO-overlay bridge fix (`9d4f0593`) — authority-map join replaces the fragile marker bridge; deterministic green (87 tests incl. run-verified 6/6 replay probe); party 4/4 + Blind/Edge review.
2. 🔄 Pass-1 head-self-parent normalization (spec `spec-38-3a-pass1-head-self-parent-normalize.md`, party 4/4, dev in flight) — trial `5ee9ac39` froze as negative witness #6 when the live model emitted self-referential `parent_slide_id` on head units.
3. ⏸ ONE clean governed live verification run (`MARCUS_G0_DISPATCH_LIVE=1`, fresh id, first-run-stands): workbook completes AND its Learning Objectives section renders real statements — 0 placeholders, no loss callout.
4. ⏸ Party green-light + `bmad-code-review` close of Stories 38.1 + 38.3a (sprint-status flips to done).
5. ⏸ Epic-38 retrospective — **REQUIRED** (governance/substrate change: graph topology + lockstep surface) — includes the deferred-inventory consultation per CLAUDE.md.
6. Open question FOR the conversation (not a gate unless ratified): 38.2 Ask-B hot-topics disposition (close-with-epic vs defer), Epics 39/40 sequencing, master-consolidation timing, cross-SME Phase-2 entry.

**Standing state:** KG + ONBOARDING regenerated at `b24b2aed` (2026-07-15); user/dev/admin/operator guides aligned same day; master consolidation owed at arc close; five negative first-run-stands witnesses + `5ee9ac39` preserved immutable.

### 11.2 The ratified pathway (sequence)

Authority: `beta-phase-1-closure-ratification-2026-06-19.md` (forward path) + `epics-perception-reading-path-fidelity.md` (P2) + the BETA charter.

```text
[PAST — CLOSED]
  Migration Slabs 1–7c ............................ ✅ shipped
  BETA Phase 1 (engine reliability + voice bind) .. ✅ ratified closed (Option B)
  P3 (closure + tracker reconciliation) ........... ✅ done
  P1 (voice-agnostic WPM floor) ................... ✅ resolved (spec-p1-…; deferred-inventory struck)

[P2 — Perception + reading-path fidelity arc]
  P2-1 Fidelity detector (RED-first) .............. ✅ done
  P2-2 Vision node + PerceptionArtifact ........... ✅ done  (⚠ shipped FIXTURE-backed — corrected by vision-perceiver-real; see note ▼)
  P2-3 Pass-2 consumes perceived visuals .......... ✅ done  (+ AC-6 live regression-green strike FIRED → regression STRUCK)
  P2-4a Reading-path native machinery (7-enum) .... ✅ done  (Codex → Claude T11 → 5/5 CLOSE, 38f2ba8)
  vision-perceiver-real (live gpt-5.5 enabler) .... ✅ done  (perception NOW genuinely live)
  ── reading-path CATALOG arc (2026-06-22) ──
  Catalog v1 (flat-7-enum → compositional tuple) .. ✅ done  (operator round-1 training 26/54 → party 6/6 GREEN-W-AMEND)
  Held-out confirm/deny round (methodology FLIP) .. ✅ done  (Claude-labeled → operator-confirmed; A6 top-1 13/14 = 0.93 PASS)
  Catalog v1.1 (D1–D3: multi_column N≥2 / callout_intent / permutability) ✅ done  (party 6/6 + operator-ratified)
  ── P2-4c reading-path tuple-classifier refactor (2026-06-23) ──
  P2-4c S1 geometry + additive tuple schema ....... ✅ done  (Codex → T11 HAND BACK → remediation → re-T11 → 5/5 CLOSE)
  P2-4c S2 per-element image-role tiers ........... ✅ done  (Codex → T11 HAND BACK → remediation → re-T11 → 5/5 CLOSE)
  P2-4c S3 gpt-5.5 escalation tuple-delta ......... ✅ done  (5/5 CLOSE-WITH-RIDERS; built classifier SUPERSEDED by the LLM-first ship ▼)
  ── reading-path SHIP PIVOT (2026-06-23) ──
  Reading-path → LLM-FIRST (gpt-5.5 authoritative) . ✅ SHIPPED  (T11 e8e8c4e; geometry→telemetry; Irene conformance advisory; pipeline completes 386912d6; operator-validated)
  Content-first narration voice (not spatial geo) .. ✅ done  (5147e0f + 148fea9)
  P2-4b honest-accuracy / fresh-naive-holdout ...... ⏸ consumed-14 numbers only (resubstitution); FRESH NAIVE HOLDOUT = binding POST-trial generalization gate (Mary's dissent)
  P2 epic retrospective + close ................... ❌ after the SPOC build / before scale-up

[NEXT-TRIAL READINESS — CLOSED (2026-06-23)]
  Fresh full smoke G0→completed (242b859f) ........ ✅ 0 errors; LLM-first perception + content-first voice + live audio + fresh Storyboard A+B
  Trial-readiness party green-light (3/3) ......... ✅ John/Murat/Mary, binding conditions (verification-not-benchmark; resubstitution stamp; fresh-holdout post-trial; narrated-deck fence)

[VARIANT / VOICE CAPABILITY — BUILT + LIVE-PROVEN PER-SLIDE (2026-06-23/24)]
  Variant arc (per-variant Gamma settings) ........ ✅ T11 done (45b7724) — CD-directive→runner→Gary→G2B
  Variant-selection downstream-consumption fix .... ✅ done — was set@G2B, read nowhere; deck-doubling roster fixed
  Genuine PER-SLIDE A/B selection (Playwright HIL) . ✅ GOAL SATISFIED — 2 live mirror runs (7d530d0a + 6cb8eafd) error-free to Descript; real gh-pages chooser clicks
  Competent-presenter narration voice ............. ✅ done — audience-addressed, argument-driven, grounded in slide stats
  (e) voice candidate→bind ........................ ✅ mechanics proven (710684c0) + voice-agnostic WPM floor (P1)

[CLUSTERING ARC — CLOSED at terminal-(b) (2026-06-24)]
  Story 1.1 Pass-1 cluster emission re-wire ....... ✅ done  (T11; party-CLOSE 3/3)
  Story 1.2a downstream delta-id repair ........... ✅ done  (verified live end-to-end)
  Story 1.4 clustering × per-sub-slide A/B ........ ✅ done  (proven live, trial c2c6dcbf)
  Story 1.3-carry cluster labels into manifest .... ✅ done
  Descript narrated VIDEO produced + PUBLISHED .... ✅ share.descript.com/view/TePGsXmfdQc
  Desmond publish-to-Descript skill ............... ✅ shipped + witnessed + registered
  Fidelity QA/QC (L1 text_mode=preserve + L2 audit)  ✅ done  (L2 warn-only; semantic leg deferred)
  Stories 1.3 polish (chunk-directive/keep-dense/timing) ◐ parked; fold into a later trial

[THE BRAID — RATIFIED NEXT FRONTIER (green-light 6/6, 2026-06-24 PM-2); client-value-first]
  Story 0 Tracy registry hygiene .................. ✅ done  (Claude-direct; stale "typography" line corrected)
  Story 0b DP6 slide_production_paths operand ..... ✅ done  (14553d9; reuse-gate operand + predicate)
  ── Slice 1 (CLIENT VALUE — the workbook) ── ALL DONE 2026-06-25 (NEW CYCLE: dev → 3-lane T11 → party CLOSE)
  S1 Lesson-plan collateral+research spec (Irene Pass-1) ✅ done  (71c2626; 159 tests; observable-degrade + byte-stability fixes)
  S2 Workbook producer (Markdown→DOCX) ............ ✅ done  (2cac27b; 135 tests; T11 HAND-BACK → fixed 3 believed-green seams)
  S3 Thin research wiring (Irene→Tracy→Texas via runner) ✅ done  (96f2f24; 28 tests; T11 HAND-BACK → wired 2 integration orphans)
  ── Slice 2 (HONEST INTERLOCUTOR — Marcus) ──
  S4 Marcus capability-overlay (GENERATED + CI-parity) ✅ done  (cce6df1; 21 tests; T11 HAND-BACK → wired local staleness guard)
  Live small-scale validation (frozen tejal) ...... ✅ Leg A workbook PROVEN-LIVE (real .docx + real word/media figure) · Leg C overlay --check exit 0 · Leg B research live-leg CLOSED (scite OAuth automated → live Texas dispatch → 3 real cited TexasRows)
  S5 REAL conversational Marcus SPOC (LLM REPL) .... ✅ done  (e20aadc, 2026-06-25) — LLM stop-and-chat; deterministic guard (hallucinating model drives engine ZERO times); HIL-proven live across 6 gates + honesty. BRAID ARC COMPLETE.

[P5 DOWNSTREAM-CONSUMPTION ARC — COMPLETE (2026-06-26/27); the enrichment loop CLOSED]
  P1 LLM component-extraction (live gpt-5) ........ ✅ done  (bc405e0; 26 components, 0 fabrication)
  P2 Texas pass-0 citation-resolution + universal-md ✅ done  (8abc533; live scite, all paths)
  P3 Irene pass-1 pedagogy-annotation overlay ..... ✅ done  (cdc138d; additive on G0EnrichmentResult; live)
  P5-S1 workbook CONSUMES the enriched corpus ..... ✅ done  (f07e89c; byte-verified — learner deliverable shaped by 2 enrichment passes)

[DIRECTED SYNTHESIZED-VOICE ARC — COMPLETE (2026-06-28); 9 steps + UDAC + ElevenLabs sweep signed off]
  Per-segment voice_direction contract → emission .. ✅ done  (CD/Irene emit; Storyboard-B displays pre-spend)
  Enrique directed ElevenLabs + acoustic verify ... ✅ done  (5-tier precedence; deterministic MUR-4 judge)
  Terminal live Descript enriched bundle .......... ✅ done  (2d1ced94; CF-A E2E both walks + UDAC Run-Asset-Index)
  07D.5 deterministic motion-plan producer ........ ✅ done  (d96ff3c; adapter over Epic-14 engine + kling library)

[ENHANCED-VO ARC — DONE clip-level (2026-06-29)]
  enhanced-vo-1 slide_key role→slide identity join . ✅ done  (d4455e4f; replaces fail-open ordinal match)
  enhanced-vo-2 v3 TAG-ONLY provider-text compiler . ✅ done  (077d68e2; byte-exact strip_tags firewall; 4 sha256 channels)
  Operator blind A/B = B but SUBTLE (intonation>pace) ✅ finding recorded — v3 tag channel = real-but-subtle control surface
  Descript full-mix cross-confirm ................. ⏸ filed (clip-level A/B only; publish FAILED — follow-on)
  Master consolidated (96309e10) ................. ✅ done

[CONCIERGE PRODUCTION SUBSTRATE ARC — CURRENT (opened 2026-06-29); true-production deck+motion+workbook+Descript via 4 legs]
  Leg-1a REAL Irene rhetorical_role emission ...... ✅ done  (af301d4c; de-inerts the shipped v3 [slow] voice channel; live ElevenLabs gate PASS)
  Coverage-assurance interlock (Leg-1) ............ ✅ DUAL-GATE CLOSED path A (2026-06-30, 53eb4a85) — fidelity firewall: fail-loud before audio spend on any uncovered source-note point
       ├ BLOCK arm proven LIVE ($0 ElevenLabs halt of a real run) ✅
       ├ COVERED arm proven OFFLINE (both-arms figure-token fixture) ✅
       ├ option C real-run covered green attempted LIVE ×2 → NOT-CONVERGED (infra flakes before G3) → fallback A
       └ HONEST: numeral/figure-token facet ONLY; production narration NOT proven figure-faithful → Leg-4
  Leg-1b warm_callback authoring + Vera-R7 teeth ... ✅ done  (097f7423, party 5/5) — block-by-omission teeth; live real-gpt-5 ALL_PASS ×2; flag-OFF; + 16:9 down-payment (27309271, live 2400×1350) + Descript publication-receipt (3dd908f4, live)
  Leg-2 motion bundle composition (B2/B3 live) .... ✅ done  (4e3b77a5) — per-run kira motion isolation; LIVE 2 real Kling renders + two-run coexistence; party 5/5→4/4
  Leg-3 callback + intelligent clustering ONLINE .. ✅ done VERIFY-ONLY (7f8db3c9) — confirm-spike: substrate ALREADY CORRECT → ZERO production code; 07G per-sub-slide invariant live-proven; callback-on-cluster filed OPEN
  Leg-4 asset/fidelity ledgers .................... ✅ done DONE-SIGNAL (9866b42f + a7091081) — UDAC broken-asset HALT live-proven ($0 before the paid Gamma call, digest-based, 6/6 Murat bars) + narration⊆source conflict-gate (flag default-OFF, teeth-witnessed on real gpt-5.5)
  FINAL party CONCURRENCE (arc done-signal) ....... ✅ 6/6 (3c88d90c, 2026-07-01) — HONEST: trust-GATED not trust-COMPLETE; fidelity flag-ON precision + positive-carry + UDAC universality + carrier validator filed OPEN
  Concierge Part-1 narrated lesson → Descript (PARALLEL) ✅ PUBLISHED 2026-06-30 (web.descript.com/d4c69938-…; every gate honored, zero code edits)
  Master consolidated + branches pruned ........... ✅ 5b4be86d (2026-07-01)

[GAMMA STYLEGUIDE LIBRARY ARC — CURRENT (opened 2026-07-01; branch dev/gamma-styleguide-library-2026-07-01); CD-owned creative-control substrate; Phase-1 machinery Legs A–E → Phase-2 roster growth ~8]
  Leg-A library spine ............................. ✅ done  (bd0003d3) — CD-owned SSOT yaml + hermetic validator write-gate + Gary styleguide base-layer seam (source WINS — protected invariant) + unconditional 16:9 override REMOVED + 3 seeds; AC#5 live Classic-vs-Studio differential
  RIPE styleguide-retire-default-variant-pair ..... ✅ done  (7b42dede) — single binding paid-dispatches EXACTLY ONE deck; AC#8 live (1 real generate_deck, negative-twin zero fixture-B)
  gamma-instructions-channel-cleanup .............. ✅ done  (bb33852d) — operator principle: additionalInstructions never merely echoes nor contradicts a structured param; AC#8 live wire capture
  Leg-B1 documented dependency rules .............. ✅ done  (d7ec3207) — warnings channel + Rule 2 (ERROR) + Rule 3 (WARN); guardrail shrank the claim (dedups/drops honest)
  Leg-B2 learned-store scaffold ................... ✅ done  (2391974e) — hermetic declarative interpreter + append-only observations ledger + identity-manifest pin (id-set+predicate-hash, NO count); EMPTY manifest by design; promotion machinery deferred to post-Leg-E
  Leg-C min_cluster_floor scripted class .......... 🔄 IN FLIGHT (c933404d) — offline build + 3-lane review + P1–P8 remediation DONE; ▶ NEXT = the LIVE Part-3 baseline = the D1 GO/NO-GO (real Pass-1 output contract) → live proof AC#9–13 → dual-gate CLOSE (Murat + Irene; 07G non-waivable)
  Leg-D HTML style-picker at CD-entry ............. ❌ queued (last_used write-back, thumbnails, A/B two-select, provenance round-trip)
  Leg-E live-doc audit (Texas gamma_docs provider)  ❌ queued (3 terminal states; provenance triple; first REAL learned-store observations → promotion-path reactivates)
  Phase-2 interactive roster growth to ~8 ......... ❌ after Legs A–E (Storyboard-B-terminating; with-Marcus)
  Batch LLM Execution Mode epic ................... ⏸ SPECced + DEFERRED to the arc-close juncture (OpenAI-only; Tranche A registry+harness → Tranche B async batch; operator holds the GO)

[LESSON-PLANNING → WORKBOOK PRODUCT LINE — 2026-07-08 → CURRENT]
  S7 Phase-2 A-D course-source substrate .......... ✅ done (2026-07-08)
  S8 selection-edge bridge (Quinn R6 fenced) ...... ✅ FULLY COMPLETE — do not reopen
  Marcus plan-ratify Claims A/B (live bespoke) .... ✅ done (2026-07-09)
  Phase-2 Six Mine-Now + integrated E2E ........... ✅ done (2026-07-10; party 4/4)
  Mine-next Track A + trust Waves 1-2 + Tejal P4 fullwalk ✅ done (2026-07-10; PASS-WITH-FENCES)
  Batch LLM Execution Mode v1 ..................... ✅ CLOSED (opt-in vision batch; default realtime)
  Agentic Research Foundations R0–R7 .............. ✅ PROMOTED (detective default-OFF; flag-OFF bit-identical)
  Workbook Research Products W0–W4 + TRAIL trio ... ✅ CLOSED (glossary/trends, empty-honesty; OpenAlex; WARN tripwire)
  Operator HUD Epic 35 (10 stories) ............... ✅ DONE + operator-usable (unanimous re-verdict; runtime HUD server; run_hud.py retired)
  ── Presentation-Support Workbook (Epics 36–40; planned end-to-end 2026-07-12) ──
  Epic 36 prework producer (36.1–36.4) ............ ✅ done (2026-07-13; live ba470ff2 machine-primary PASS)
  Epic 37 review + deep-dive (37.1/2a/3/4) ........ ✅ done · 37.2b / 37.5 / 37.6 ❌ backlog
  Epic 38 research asks + 07W terminal band ....... ✅ CLOSED (2026-07-15; retrospective done)
       ├ 38.0 two-packet intake + 38.3b band orchestrator ✅ done
       ├ 38.1 + 38.3a LIVE GATE PASSED ............ ✅ trial a940c5eb (2026-07-15) — FIRST COMPLETE runner-verified workbook (5-run scout→batch→run arc; verdict honesty)
       ├ LO-overlay bridge fix .................... ✅ 9d4f0593 — authority-map join, party 4/4 + T4 review, 87 tests
       └ Pass-1 head-self-parent normalization .... ✅ done (witness 5ee9ac39 was frozen #6; clean verification + closures landed)
  ── Epics-39/40 wave (branch dev/workbook-wave-3940-2026-07-15; consolidated to master) ──
  Answer-leak strip + 37-2b + 39-1 + 39-1b ........ ✅ landed under the Paid-Run Economy Protocol
  Master consolidation (wave → master `12775df6`) . ✅ DONE (--no-ff; merged branch pruned; fresh trial branch cut)
  Epic 39 trends render (39.2) · Epic 40 cover (40.1) ❌ backlog (queued behind the R2 trial)
  ── bc747b51 live-trial fallout → Epics 41/42/43 (2026-07-17; all CLOSED; consolidated `12775df6`) ──
  Epic 41 Resume-Walk Dispatch Integrity .......... ✅ CLOSED — the bc747b51 fix (budget starvation, not keyless resume)
       ├ 41-1 resume/recover live-env preflight ... ✅ 3919c7fb
       ├ 41-2 fail-loud on silent specialist skip (both walks, RED-first) ✅ 81fdc495
       ├ 41-3 REMOVE max_specialist_calls throttle  ✅ d8fb959b — the actual root-cause fix
       └ 41-4 MARCUS_TRIAL_BUDGET_USD enforced-stop  ✅ cf7df4fd — a brake, not a gauge
  Epic 42 Operator-Surface Next-Pass (party 5/5) .. ✅ CLOSED
       ├ 42-1 tabular HIL + neutral verb .......... ✅ 8a9f7095 (seed of Epic 43)
       ├ 42-2 HUD survives pause + CREATE_NO_WINDOW  ✅ 72a15de5
       ├ 42-3 16-toggle settings readout .......... ✅ 482cf78a
       ├ 42-4 public read-only HUD non-leak overlay  ✅ f8dd93d2
       ├ 42-5/6 G0S pre-walk settings gate + default-ON ✅ 8d485ace + 39f006ac
       └ 42-8 ngrok reserved-domain public HUD .... ✅ 4ca3d19b (live-proven; deplete-courier-blurt.ngrok-free.dev)
  Epic 43 HIL Surface Tabular Coverage (5/5) ...... ✅ CLOSED — 14 reviewed surfaces → 14 tabular renderers
       ├ 43-2 renderer registry + generic fallback + paused-gate wiring ✅ the systemic fix
       ├ 43-10 RED-first coverage ratchet (allowlist drained 15→0) ✅
       ├ 43-1/3/4/5/6/7/8 per-gate bespoke renderers ✅ (G0 directive, variant/mode, voice, plan-unit/estimator, targets, motion, package/handoff)
       ├ 43-9 honest de-scope (research_packet + workbook not reviewed surfaces → allowlist EMPTY) ✅
       └ 43-11 SPOC↔projector anti-drift parity guard ✅
  GCM account-picker neutralize fix ............... ✅ b9b5029f (gh-pages publish no longer seeds x-access-token identity)
  KG + ONBOARDING + guides refreshed (bfefcc1b) ... ✅ 2026-07-17
  ▶ R2 operator-steered live trial ................ ⏸ NEXT (operator at the wheel; corpus tejal-apc-c1m1-p1-call)

[BETA Phase 2 / charter remainder]
  pass2-grounding-to-chosen-variant-figures ....... ⏸ filed caveat — blocks B-heavy NON-demo trials; party decision pending (3 fixes, none a gate-relaxation)
  T6 Review lanes (ingestion / lesson-plan / Tracy)  ❌ not started
  T8 Motion plan (honest producer OR ratified carve) ❌ carved in practice, not ratified in writing
  S0.4 Full per-gate live-dispatch harness ........ ◐ auto-retry only
  Full BETA §8 dress rehearsal (a+b+c+e binding) .. ◐ per-slide variant + presenter voice now LIVE; full conversational a+b+c path pending the real SPOC

[ASPIRATIONAL / SHELF]
  Epic 15 Learning & Compound Intelligence ........ ❌ gate ("first tracked trial") now arguably met → most reactivation-ready
  Epics 16–18 (autonomy / research / asset families) ❌ shelf
  Lesson Planner MVP (28–32) wired to trial path .. ◐ schema substrate landed; production-path orphaned
  Cross-corpus generality · motion synthesis · greenfield specialists … ❌ long tail
```

> **Correction (2026-06-21) — legible, not silent.** The P2-2 line previously read as "real PerceptionArtifact." That described a **fixture-backed contract** (Pydantic models + a pinned `VISION_PROVIDER_ENDPOINT` that was never configured, default model `vision-fixture-v1`, a single hand-authored slide-01 golden), **not** a live perceiver — no model was wired to perceive an arbitrary PNG. As of the **`vision-perceiver-real`** enabler CLOSE (2026-06-21; party 5/5 green-light → 3-layer `bmad-code-review` → 4/4 CLOSE), perception is **genuinely live**: `app/specialists/vision/provider.py` makes a real `gpt-5.5` multimodal call; live AC-8 perceived all 6 frozen-corpus PNGs HIGH/perceived. Root cause logged as the **"believed-green tracker"** drift class (a green suite standing in for live capability / current config — the OpenAI catalog-snapshot test was also found already-RED for `gpt-5.4`); see deferred-inventory `believed-green-tracker-audit` + anti-pattern G1. This enabler PRECEDES the P2-4b labeling kit, which now consumes genuine perception.

### 11.3 Position-in-sequence

| Milestone | Status | Notes |
|---|---|---|
| P2-4a reading-path machinery (7-enum) | ✅ `38f2ba8` | 3-layer review + party 5/5 CLOSE |
| Catalog v1 (compositional tuple) | ✅ `54afb27` | operator round-1 training 26/54 → party 6/6 GREEN-W-AMEND |
| Held-out confirm/deny round (A6 PASS) | ✅ `e647e93` | methodology flip; primary-key top-1 13/14 = 0.93; catalog → v1.1 (D1–D3) |
| P2-4c S1 (geometry + tuple schema) | ✅ `2f6f123` | Codex → T11 hand-back → remediation → re-T11 → 5/5 CLOSE |
| P2-4c S2 (image-role tiers) | ✅ `d4f2b2c` | Codex → T11 hand-back → remediation → re-T11 → 5/5 CLOSE |
| P2-4c S3 (gpt-5.5 escalation) | ✅ 5/5 CLOSE-WITH-RIDERS | built classifier SUPERSEDED by the LLM-first ship ▼ |
| **Reading-path → LLM-FIRST ship** | ✅ `e8e8c4e` | gpt-5.5 authoritative; geometry→telemetry; conformance advisory; pipeline completes (`386912d6`); operator-validated. Numbers on consumed-14 (resubstitution) |
| Next-trial readiness gate | ✅ party 3/3 (`242b859f` smoke) | verification-not-benchmark; resubstitution stamp; fresh-naive-holdout = post-trial gate |
| Variant arc + per-slide A/B (presenter voice) | ✅ GOAL SATISFIED 2026-06-24 | 2 live mirror runs error-free to Descript; real Playwright chooser clicks; HEAD `b19aa37` |
| Full-repo harmonization | ✅ green-core 2026-06-24 | lockstep PASS + walks READY + lint 15/0; 17 ambient stale-pins tracked |
| Clustering arc → terminal-(b) + Descript video published | ✅ 2026-06-24 | 1.1/1.2a/1.4/1.3-carry T11-closed; `c2c6dcbf`; Desmond publish skill + fidelity L1/L2 |
| **Braid green-light (workbook+research+interlocutor)** | ✅ 6/6 2026-06-24 PM-2 | ratification doc; Story 0 done; S1–S4 specs → dev; client-value-first |
| Braid Slice 1 (workbook companion) | ✅ done 2026-06-25 | S1 (71c2626) → S2 producer MD→DOCX (2cac27b) → S3 research wire (96f2f24); workbook PROVEN-LIVE |
| Braid Slice 2 / REAL conversational Marcus SPOC (S5) | ✅ done `e20aadc` 2026-06-25 | LLM stop-and-chat REPL on a GENERATED capability-self-model; deterministic guard; HIL-proven 6 gates. BRAID COMPLETE |
| Research live-leg (scite/Consensus) | ✅ CLOSED 2026-06-25 | scite OAuth automated (headed Playwright) → live Texas dispatch → 3 real cited TexasRows |
| P5 downstream-consumption arc (loop CLOSED) | ✅ done 2026-06-27 | P1+P2+P3 live-signed-off; workbook CONSUMES enriched corpus (f07e89c, byte-verified) |
| Directed synthesized-voice arc (9 steps + UDAC) | ✅ done `2d1ced94` 2026-06-28 | voice_direction contract → directed ElevenLabs → acoustic verify → live Descript; 07D.5 motion producer |
| Enhanced-VO arc (v3 tag compiler + slide_key join) | ✅ done clip-level 2026-06-29 | `d4455e4f`+`077d68e2`; A/B = B subtle; master consolidated `96309e10`. Descript full-mix cross-confirm filed |
| Concierge Leg-1a (real rhetorical_role emission) | ✅ done `af301d4c` 2026-06-30 | de-inerts the v3 voice channel; live ElevenLabs gate PASS |
| **Concierge coverage-assurance interlock (Leg-1)** | ✅ DUAL-GATE CLOSED path A `53eb4a85` 2026-06-30 | fidelity firewall; BLOCK arm LIVE ($0), COVERED arm OFFLINE; numeral-facet ONLY; narration-fidelity → Leg-4 |
| Concierge Leg-1b (warm_callback + Vera-R7 teeth) | ✅ done `097f7423` 2026-06-30 | party 5/5; live real-gpt-5 ALL_PASS ×2; + 16:9 (`27309271`) + Descript receipt (`3dd908f4`) down-payments |
| Concierge Legs 2/3/4 + final concurrence | ✅ **ARC COMPLETE** 2026-07-01 | Leg-2 `4e3b77a5` (live Kling ×2) · Leg-3 `7f8db3c9` (verify-only, ZERO code) · Leg-4 `9866b42f`+`a7091081` (UDAC halt live $0 + fidelity gate flag-OFF) · concurrence 6/6 `3c88d90c`. Trust-GATED not trust-COMPLETE |
| Master consolidated (post-arc) | ✅ `5b4be86d` 2026-07-01 | merged concierge + P5 branches pruned; next arcs branch fresh from master |
| Gamma Styleguide Leg-A (library spine) | ✅ done `bd0003d3` 2026-07-01 | CD-owned SSOT + hermetic validator + Gary base-layer seam + 16:9 override removed; AC#5 live differential |
| Gamma RIPE retire-default-variant-pair | ✅ done `7b42dede` 2026-07-01 | single binding → exactly one paid deck; AC#8 live + negative twin |
| Gamma instructions-channel cleanup | ✅ done `bb33852d` 2026-07-01 | non-echo/non-contradiction channel contract; AC#8 live wire capture |
| Gamma Leg-B (B1 rules + B2 learned-store scaffold) | ✅ done `d7ec3207` + `2391974e` 2026-07-01 | dual-gate ×2; empty-manifest-by-design; anti-vacuous pin |
| ▶ Gamma Leg-C (min_cluster_floor scripted class) | 🔄 **IN FLIGHT** `c933404d` | offline+review+remediation done; **NEXT = live Part-3 baseline (D1 GO/NO-GO)** → AC#9–13 → dual-gate CLOSE |
| Gamma Legs D/E + Phase-2 roster growth | ❌ queued | picker → live-doc audit (first learned-store observations) → interactive roster ~8 |
| Batch LLM Execution Mode epic | ⏸ deferred to arc-close juncture | SPECced (`epic-batch-llm-execution-mode-spec-2026-07-01.md`); OpenAI-only; operator holds GO |
| P2 epic close | ❌ before scale-up | fresh-naive-holdout still owed for generalization |
| BETA Phase 2 (T6 / T8 / full §8) | ◐ variant+voice+SPOC live; full §8 dress rehearsal open | concierge substrate hardened ✅; after the Gamma creative-control arc |
| S7 Phase-2 A-D + S8 (Quinn R6) + plan-ratify A/B | ✅ 2026-07-08/09 | course-source substrate; selection bridge FULLY COMPLETE (do not reopen); live bespoke Irene Pass-1 |
| Batch v1 · Research R0–R7 · Workbook W0–W4 · TRAIL | ✅ all CLOSED/PROMOTED 2026-07-10 | opt-in vision batch; governed research (detective default-OFF); glossary/trends empty-honesty |
| Operator HUD Epic 35 (10 stories) | ✅ DONE 2026-07-11/12 | unanimous party re-verdict; HUD authorized for real operator use; legacy run_hud retired |
| Workbook redesign planned end-to-end | ✅ 2026-07-12 (Class P) | `epics-presentation-support-workbook-2026-07-12.md`; DAG build order ratified |
| Epic 36 + Epic 37 (37.1/2a/3/4) | ✅ 2026-07-13 | prework producer live PASS (ba470ff2); review/deep-dive/check/reflection projections |
| **Epics 36-40 WORKBOOK LIVE GATE** | ✅ **PASSED 2026-07-15** (trial `a940c5eb`) | **first complete runner-verified workbook** (MD+DOCX); 5-run scout→batch→run arc; verdict honesty; witnesses immutable |
| LO-overlay bridge fix | ✅ `9d4f0593` 2026-07-15 | authority-map join (structural precedence over markers); party 4/4 + Blind/Edge T4; 87 tests incl. 6/6 replay probe |
| Pass-1 head-self-parent normalization + Epic 38 close | ✅ done 2026-07-15 | witness `5ee9ac39` was frozen #6; clean verification + 38.1/38.3a closures + REQUIRED retrospective landed |
| Master consolidation (workbook wave → master) | ✅ `12775df6` 2026-07-17 | `--no-ff`; merged branch pruned; fresh `trial/c1m1-p1-2026-07-17` cut |
| **Epic 41 Resume-Walk Dispatch Integrity** | ✅ CLOSED 2026-07-17 | the `bc747b51` fix: budget starvation (`max_specialist_calls=1`) not keyless resume — throttle removed (`d8fb959b`), budget enforced-stop (`cf7df4fd`), fail-loud silent-skip both walks (`81fdc495`), resume/recover preflight (`3919c7fb`) |
| **Epic 42 Operator-Surface Next-Pass** | ✅ CLOSED 2026-07-17 (party 5/5) | HUD survives-pause + windowless; public ngrok read-only overlay (allowlist-scrubbed); G_SETTINGS pre-walk gate ("G0S") default-ON + 16-toggle readout |
| **Epic 43 HIL Surface Tabular Coverage** | ✅ CLOSED 2026-07-17 (5/5) | 14 reviewed gate surfaces → 14 bespoke tabular renderers; RED-first coverage ratchet (allowlist EMPTY); SPOC↔projector anti-drift parity guard; requirement `hil-operator-surfaces-must-be-tabular` COMPLETED |
| GCM account-picker neutralize + KG/ONBOARDING/guides | ✅ 2026-07-17 | `b9b5029f` publish-identity fix; KG regen `bfefcc1b` (2699/5164/7 layers); guides refreshed |
| ▶ R2 operator-steered live trial | ⏸ NEXT | operator at the wheel; corpus `tejal-apc-c1m1-p1-call`; witnesses tabular G0 + every gate table + G0S pause + windowless/public HUD + budget-braked completable run |
| Epics 37-residual (37.2b/5/6) · 38.2 · 39 · 40 | ❌ backlog | queued behind the R2 trial; cross-SME Phase-2 still open |

**You are here (2026-07-17) →** the **goal is the Marcus-SPOC product**; its four deliverables — narrated-deck, cited workbook-companion sections, honest conversational Marcus, and the full presentation-support learner **WORKBOOK** — have all run end-to-end live, the workbook first on 2026-07-15 (trial `a940c5eb`). Since then the operator ran a live SPOC trial that surfaced two production-defect classes, and **three epics closed them**: **Epic 41** hardened the trial engine (the `bc747b51` frozen run was budget starvation, now fixed — throttle removed, budget an enforced stop, fail-loud on silent skip in both walks); **Epic 42** hardened the operator surfaces (HUD survives-pause + windowless + a public read-only ngrok overlay; a G0S pre-walk settings gate, default-ON); **Epic 43** made every one of the 14 operator-reviewed gate surfaces render a bespoke **table** instead of the raw JSON the first trial dumped, pinned by a coverage ratchet (allowlist EMPTY) + a SPOC↔projector parity guard. **Master is consolidated at `12775df6`**; the KG/ONBOARDING/guides are refreshed at `bfefcc1b`. The active frontier is the **R2 operator-steered live trial** on `tejal-apc-c1m1-p1-call` — the first run to witness the full tabular gate surfaces, the default-ON settings pause, the windowless + public HUD, and a budget-braked, now-completable run. Standing debts unchanged: reading-path fresh naive holdout; narration-fidelity flag default-OFF; trust-GATED-not-trust-COMPLETE residuals; Gamma Leg-C/D/E + Phase-2 roster parked.


### 11.4 Completion horizons

**Horizon 1 — Product trust restored (P2 / fidelity).** Narration grounds on the *rendered* slide (P2-3 ✅); a fail-loud detector catches hallucinations (P2-1/2/3 ✅); reading-path is **LLM-first and SHIPPED** (gpt-5.5 authoritative, conformance advisory; ✅ 2026-06-23). **Largely MET:** "error-free" now means mechanics **and** fidelity, and reading order is perception-driven on the live pipeline. **Residual:** reading-path accuracy stands on the **consumed-14** (resubstitution) — a **fresh naive holdout** is the binding generalization gate before any scale-up claim; the variant-B figures-as-prose grounding caveat (`pass2-grounding-to-chosen-variant-figures`) is open for B-heavy non-demo trials.

**Horizon 2 — BETA spec as written (`beta-spec §8`).** **Now largely live:** genuine per-slide variant picks + presenter voice demonstrated error-free twice to Descript; voice candidate→bind proven; the **real conversational Marcus SPOC shipped** (S5 `e20aadc`, 2026-06-25 — LLM stop-and-chat REPL, HIL-proven across 6 gates); the runtime beneath it is fail-loud hardened (concierge substrate arc COMPLETE 2026-07-01) and gaining a CD-owned creative-control surface (the Gamma Styleguide Library, in flight). **Open:** Tracy on the trial path (T6d); dedicated lesson-plan / ingestion review surfaces (T6b/c); motion carve-out ratified in writing or an honest producer (T8); a full §8 dress rehearsal exercising the **conversational a+b+c path** (variant/voice picks already covered). **Exit:** the conversational Marcus product on the frozen corpus, error-free twice **to spec**.

**Horizon 3 — Full APP vision (epics on the shelf).** Learning/intelligence (Epic 15), bounded autonomy (16), full research (17), new asset families (18); Lesson Planner MVP integrated into production trials; cross-corpus generality, motion synthesis, greenfield specialists. **Exit:** a multi-corpus, multi-use-case platform — months beyond the current arc.

### 11.5 Honest progress estimate

| Universe | Approx. complete | Basis |
|---|---|---|
| LangGraph migration substrate | **~95%+** | shipped; Slabs 1–7c closed |
| BETA Phase 1 (engine reliability + voice bind) | **100%** | ratified closed (Option B) |
| P2 fidelity / perception arc | **~92%** | grounding 100% (P2-1/2/3 + strike); reading-path **LLM-first SHIPPED** (gpt-5.5 authoritative; pipeline completes). Residual: accuracy on consumed-14 only — **fresh naive holdout** owed for generalization; variant-B figures-as-prose caveat open |
| Next-trial readiness | **100% (single-variant)** | party-certified 3/3 + fresh smoke `242b859f` completed; binding conditions recorded |
| Variant / per-slide A/B + presenter voice | **100% (demonstrated)** | 2 live mirror runs error-free to Descript via real Playwright chooser clicks; arbitrary-N + B-grounding are filed follow-ons |
| Clustering / VO follow-along arc | **100% (terminal-(b))** | clustered + per-sub-slide A/B run to Descript (`c2c6dcbf`); 1.1/1.2a/1.4/1.3-carry T11-closed; video PUBLISHED; 1.3 polish parked |
| Braid (workbook + research + interlocutor) | **100% (COMPLETE 2026-06-25)** | S1/S2/S3/S4 + S5 conversational SPOC (`e20aadc`) + Story 0/0b all closed through full gate; workbook PROVEN-LIVE; research live-leg CLOSED (scite OAuth → 3 cited TexasRows); SPOC HIL-proven 6 gates |
| P5 downstream-consumption arc (enrichment loop) | **100% (CLOSED 2026-06-27)** | P1 extraction + P2 citation-resolution + P3 pedagogy-annotation live-signed-off; workbook CONSUMES enriched corpus (f07e89c, byte-verified) |
| Directed synthesized-voice arc | **100% (2026-06-28)** | per-segment voice_direction → directed ElevenLabs → acoustic verify → live Descript; UDAC Run-Asset-Index; ElevenLabs param sweep; 07D.5 motion producer |
| Enhanced-VO arc (v3 directed voice) | **100% clip-level (2026-06-29)** | v3 tag-only compiler (byte-exact firewall) + slide_key join; A/B = B subtle (intonation>pace). Descript full-mix cross-confirm = filed follow-on |
| Concierge Production Substrate arc (4 legs) | **100% (COMPLETE 2026-07-01)** | all legs party-CLOSED + live-proven (Leg-2 Kling ×2 · Leg-3 verify-only ZERO code · Leg-4 UDAC halt $0 + fidelity gate flag-OFF); final concurrence 6/6; HONEST: trust-GATED not trust-COMPLETE (flag-ON precision, positive-carry, UDAC universality, carrier validator filed OPEN); master consolidated `5b4be86d` |
| Gamma Styleguide Library arc (Phase-1 machinery) | **~60% (Legs A+B + 2 stories done; Leg-C at its live gate)** | Leg-A spine + RIPE variant-pair + instructions-cleanup + Leg-B1/B2 all closed + live-proven; Leg-C offline done, live Part-3 baseline (D1 GO/NO-GO) next; Legs D/E queued; Phase-2 roster growth after machinery |
| S7 Phase-2 A-D course-source substrate | **100% (CLOSED 2026-07-08)** | Story A registry/manifests + broad-root guard; Story B syllabus proposals; Story C canonical asset/gap records; Story D lesson-planning input bundle + `ComponentSelection` boundary; shadow monitor concurred after backfill |
| S8 first selection-edge runtime slice | **100% for first slice (CLOSED `282ea82f`)** | Ratified local lesson-plan collateral intent -> bundle catalog -> `ComponentSelection` -> local production runner path; 25 focused tests passed + local CLI witnesses |
| S8 full bridge/prose arc | **CLOSED on claim envelope (not E2E COMPLETE)** | Selection + planning-input + prose + Part-4 corpus + AFK HIL composed-start (G0→G1) proven; terminal walk blocked at known Gamma single-slide `brief-unmatched`; see `s8-close-letter-claim-envelope-2026-07-08.md` |
| Batch v1 + Research R0–R7 + Workbook W0–W4 + TRAIL | **100% (CLOSED/PROMOTED 2026-07-10)** | opt-in vision batch (hermetic done-bar); governed research w/ credibility tiers + R7 gate (default-OFF); glossary/trends empty-honesty; OpenAlex live-proven |
| Operator HUD (Epic 35) | **100% (2026-07-12)** | 10/10 stories; live E2E + fix arc; unanimous party re-verdict; authorized for real operator use. Non-blocking debt: batch pause-class witness, browser witness, L2-golden snapshot |
| Presentation-Support Workbook (Epics 36–40) | **~80%** | Epic 36 ✅; Epic 37 4/7 ✅; **Epic 38 ✅ CLOSED** (first complete workbook `a940c5eb`; LO-bridge fixed; retrospective done; master consolidated); Epics 39 (trends render) / 40 (cover) backlog; verdict-honest runner; 6 immutable negative witnesses |
| Resume-Walk Dispatch Integrity (Epic 41) | **100% (CLOSED 2026-07-17)** | the `bc747b51` fix: budget starvation not keyless resume — `max_specialist_calls` throttle removed (`d8fb959b`); `MARCUS_TRIAL_BUDGET_USD` enforced-stop (`cf7df4fd`); fail-loud silent-skip both walks (`81fdc495`); resume/recover live-env preflight (`3919c7fb`) |
| Operator-Surface Next-Pass (Epic 42) | **100% (CLOSED 2026-07-17, party 5/5)** | HUD survives-pause + windowless (`localhost:8791`); public read-only ngrok overlay (allowlist-scrubbed, `deplete-courier-blurt.ngrok-free.dev`); G_SETTINGS pre-walk gate ("G0S") default-ON + 16-toggle readout; R2 live leg owed |
| HIL Surface Tabular Coverage (Epic 43) | **100% (CLOSED 2026-07-17, 5/5)** | 14 operator-reviewed gate surfaces → 14 bespoke tabular renderers; RED-first coverage ratchet (allowlist drained 15→0=EMPTY); SPOC↔projector anti-drift parity guard; requirement `hil-operator-surfaces-must-be-tabular` COMPLETED |
| BETA Phase 2 / full §8 spec | **~60–70%** | variant+voice picks + the real conversational SPOC LIVE; the concierge substrate hardening DONE; open: motion (T8), Tracy trial-path review surfaces (T6), full §8 dress rehearsal |
| Full APP (Epics 15–18 + LP integration) | **~15–20%** | substrate exists; not yet wired to the operator product |

**Bottom line (2026-07-01):** the three product pillars — the **narrated-deck**, the **cited WORKBOOK companion**, and the **honest conversational Marcus SPOC** — are all **end-to-end live and individually proven**, and the runtime beneath them is now **fail-loud-before-spend hardened**: the **Concierge Production Substrate arc is COMPLETE** (coverage interlock live at $0, warm_callback teeth, per-run motion isolation with real Kling renders, clustering verified-already-correct with zero code, UDAC broken-asset halt live at $0, Descript publication receipt — final party concurrence 6/6), with honest residuals filed (**trust-GATED, not trust-COMPLETE**: the narration-fidelity flag stays default-OFF pending precision+activation; positive-carry, UDAC universality, and the bundle-carrier extraordinary-robustness arc remain OPEN). **Master is consolidated at `5b4be86d`.** The live frontier is the **Gamma Styleguide Library arc** — making the hardened runtime **creatively governable** through a CD-owned library of named styleguides that is the **sole determinant of Gamma output** (baked-in overrides removed; the source-detail→Gamma conveyance protected, source WINS). Phase-1 machinery is ~60% done: Leg-A (library spine + hermetic write-gate + live Classic-vs-Studio differential), the RIPE single-variant fix, the instructions-channel contract (never echo, never contradict), and Leg-B dependency enforcement (documented rules + an honest empty-by-design learned-store scaffold) are all closed and live-proven; **Leg-C (the `scripted` imperative channel) sits at its decisive gate — the live Part-3 baseline that adjudicates D1** (does real Irene Pass-1 output expose the sub-structure + role tags the offline honoring assumes, or does the pre-authorized output-contract extension fire?). Then Leg-D (style picker), Leg-E (live-doc audit, first real learned-store observations), and Phase-2 interactive roster growth. Waiting at the arc-close juncture: the **Batch LLM Execution Mode** epic (OpenAI-only; transport-equivalent). Standing debts unchanged: reading-path fresh naive holdout; full §8 dress rehearsal. (The full-spine discipline keeps earning its keep — this arc alone, the 3-lane review caught a tautological offline contract and converted it into a decisive live gate rather than a false green.)
**Bottom line (2026-07-15):** the product's four deliverables — narrated-deck, cited workbook-companion sections, conversational Marcus, and the **full presentation-support learner WORKBOOK** — have all now run end-to-end live; the workbook's first complete run (`a940c5eb`) landed 2026-07-15 with an honest runner verdict, and its last shippability defect (the placeholder Learning Objectives section) is fixed at `9d4f0593`. **Epic 38 is in closure**: one deterministic fix in flight (Pass-1 head-self-parent live-variance normalization; witness `5ee9ac39` frozen), then one clean governed verification run, story closures for 38.1 + 38.3a, and the REQUIRED retrospective. The **post-close roadmap conversation** then decides: 38.2 Ask-B disposition, Epics 39 (glossary/trends render) / 40 (cover) sequencing, **master consolidation** (owed; branch `codex/workbook-enhanced-epics-36-40`), and **cross-SME Phase-2** entry (the witnessed claim is frozen-lesson end-to-end (corpus `tejal-apc-c1-m1-p2-trends`, Tejal Part 2); the redesigned producer's off-lesson run (`tejal-c1m1-p3-opportunity`) and cross-SME are both open). The operator cockpit (Epic-35 HUD) and the governed research runtime (R0–R7) are standing capabilities beneath all of it. Standing debts unchanged: reading-path fresh naive holdout; narration-fidelity flag default-OFF; trust-GATED residuals; Gamma Phase-2 roster + Batch A1-EXT parked.
**Bottom line (2026-07-17):** the workbook wave consolidated to `master` (`12775df6`), and then the first live Marcus-SPOC trial off that base did its real job as a discovery vehicle — it surfaced two production-defect classes that **three epics closed in one wave**: **Epic 41** hardened the trial engine (the `bc747b51` "frozen run" was budget starvation, `max_specialist_calls=1` — throttle removed, `MARCUS_TRIAL_BUDGET_USD` now an enforced stop, silent specialist skip fails loud in both walks, resume/recover runs a live-env preflight); **Epic 42** hardened the operator surfaces (the flight-deck HUD survives pause + launches windowless, a public read-only ngrok overlay watches a run from any device with a positive-allowlist scrub, and a G0S pre-walk settings gate default-ON confirms run settings up front); **Epic 43** made **every one of the 14 operator-reviewed gate surfaces render a bespoke table** instead of the raw YAML/JSON the first trial dumped — the durable fix being the RED-first coverage ratchet (allowlist drained to EMPTY) plus a SPOC↔projector anti-drift parity guard, not the renderers themselves. Master is consolidated; the KG/ONBOARDING/guides are refreshed at `bfefcc1b`. The single owed item is the **R2 operator-steered live trial** on `tejal-apc-c1m1-p1-call` — the confirmation run that witnesses the full tabular gate surfaces, the default-ON settings pause, the windowless + public HUD, and a budget-braked, now-completable trial. Standing debts unchanged: reading-path fresh naive holdout; narration-fidelity flag default-OFF; trust-GATED residuals; Gamma Phase-2 roster + Batch A1-EXT parked; cross-SME Phase-2 still open.

## Current Reconciliation Note - 2026-07-09

S7 Phase-2 A-D and **S8 are FULLY COMPLETE** (Quinn R6; do not reopen). Post-S8 Irene-literal→Gary-preserve is **MET** (`235f2b82…`). Pass-2 figure/numeral under classic-condense is **parked HELR**. Live frontier on `dev/lesson-planning-2026-07-09` is **bigger gains**: Phase-2 spine `lesson-plan-directs-production-collateral-to-selection-edge` (primary candidate), and/or real HAI/PHS ingestion, LO ratification, course/SME routing — not numeral polish. Product guardrail unchanged: Marcus-SPOC local runtime orchestration, not proofing/concierge convenience. HAI 510 and PHS 620 remain honest fixtures until authorized ingestion.

---
