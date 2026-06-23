# State of the App — Canonical Status Synthesis

**Date:** 2026-06-19 · **Last updated:** 2026-06-23 (reading-path tuple arc — catalog v1.1 ratified; P2-4c S1+S2 DONE; S3 in flight)
**Status:** Canonical orientation doc. Single source of truth for "where the development plan actually stands."

> **⚡ 2026-06-23 UPDATE — the reading-path leg advanced from "operator-gated" to an active, mostly-built sub-arc (P2-4c).** Three things changed the picture since 2026-06-21: **(1) the reading-path PATTERN CATALOG was tuned + ratified.** Operator slide-perception training (26/54 slides) → `reading-path-patterns-catalog.md` **v1** (a **compositional tuple** `{macro_layout × image_role(1–4) × text_substructure × narration_cadence}` replacing the flat 7-enum) → `bmad-party-mode` 6/6 → **v1.1** after a held-out confirm/deny round (decisions D1–D3). **(2) the P2-4b methodology FLIPPED** (operator-authorized): instead of operator-labels-then-score, **Claude labeled the 14 held-out slides via catalog v1, the operator confirmed/denied** — result **0.93 primary-key agreement**. ⚠️ **PROVENANCE (S3-T11 correction 2026-06-23):** that 0.93 measures the **catalog-approach (Claude-in-loop labels) vs gold** — it is **NOT the built deterministic classifier's accuracy.** A live dry-run of the *built* P2-4c classifier vs the same gold scored **primary-key 0.071 on STALE perceptions** (captured pre-S2-role_tier → geometry backfill only) — an un-fair number pending fresh re-perception. **The built classifier's honest accuracy is UNMEASURED.** P2-4b is therefore **real calibration work** (re-perceive under role_tier → recalibrate → measure), **not "one command."** The held-out reserve is now CONSUMED. **(3) the catalog drove a classifier refactor, P2-4c** (additive tuple schema + hybrid-(c) classifier), built via NEW CYCLE Codex: **S1 DONE + S2 DONE** (each: Codex T1–T10 → Claude T11 HAND BACK → remediation → re-T11 → party 5/5 CLOSE — the T11 gate caught real over-claim / vacuous-gate / index-misalignment defects the green battery hid, twice); **S3 (gpt-5.5 escalation) is in flight**; **P2-4b finalize is fully pre-staged + self-tested** (`reading_path_p2_4b_run.run_live()` scores the built classifier vs the confirmed gold). Anti-patterns **H1** (green-test-certifies-a-bug) + **H2** (agreement-harness PASSes on empty/excluded scored set) harvested; a believed-green audit found the liveness stratum CLEAN (one filed config-red: `model-id-denylist-vs-allowlist-contradiction`). §11 below is refreshed; the 2026-06-21 banner's "P2-4b operator-gated on a harvest" framing is **SUPERSEDED** by the flip.

> **⚡ 2026-06-21 UPDATE — the Layer-D "crippling" fidelity regression (§3) is CLOSED.** The P2 perception/reading-path arc landed: **P2-1** fail-loud fidelity detector (done) → **P2-2** PNG-grounded `PerceptionArtifact` (closed) → **P2-3** Pass-2 grounds on perceived visuals, the regression fix (closed) **+ its AC-6 live regression-green strike FIRED** (live Pass-2 over the frozen corpus → committed detector GREEN 8/8 + held-out, independently re-judged) → **P2-4a** reading-path native machinery (classifier + fail-loud verify-node + cadence, closed). The deferred entry `fidelity-metric-blind-to-perception-regression` is **STRUCK**. The reading-path **calibration** leg (**P2-4b** — repertoire growth + the held-out ≥80% real-slide conformance corpus) remains **operator-gated** on a scan-order exemplar harvest. Sections §3 / §4-row-(g) / §8-#2 / §9 below are annotated inline; the strikethrough/❌ framing in those sections is **historical** (pre-2026-06-21).
**Provenance:** Synthesizes two independent assessments produced 2026-06-19 — (1) the live session assessment (triangulating `SESSION-HANDOFF.md`, `next-session-start-here.md`, `bmm-workflow-status.yaml`, `deferred-inventory.md`, the BETA spec/charter, and on-disk run evidence), and (2) an independent external analysis triangulating the same artifacts. Where the two diverged, the divergences were adjudicated against on-disk evidence (git history, `slab-7c-retrospective.md`, run directories); both factual conflicts resolved in favor of the external analysis (see §10). This doc exists so the plan does not have to be re-derived every session.

> **Maintenance:** refresh at (a) each arc/epic close that materially changes validated scope, (b) any trial postmortem that moves a §4 scorecard row, (c) any governance ratification that changes how BETA or the forward arcs are tracked, (d) **every story/arc close — update §11 (Project Pathway): the §11.1 "You are here", the §11.2 pathway-tree glyphs, and (at arc close) the §11.5 progress table.** Keep the §4 scorecard, §5 tracker-reality table, and §11 pathway honest — they are the load-bearing anti-drift surfaces.

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
| **(d) research** (§4.5) | Tracy on trial path; operator ack (non-blocking) | **No** on production path | SPOC reports "none dispatched" | **FAIL/CARVED** — Epic-28 module exists but **production-path orphaned** |
| **(e) variants** (§4.4) | N-dispatch, per-slide bind | **No** — still single-dispatch | — | **FAIL** — T5b not started; distinctness deferred by design |
| **(e) voice** (§4.4) | Voice candidates → bind | **Yes** (mechanics) | Voice select→synthesis **proven** (`710684c0`) | **PASS (mechanics)** — but exercised *separately*, not inside the twice-gate runs |
| **(e) clustering/pace** (§4.4) | Read-only surface | Read-only present | Shown in SPOC | **PASS (read-only)** |
| **(f) motion** (§4.6) | Honest motion-plan artifact OR written carve-out | Carved **in practice** | SPOC narrates "no motion clips" | **CARVED (implicit)** — no producer; carve-out **not party-ratified in writing** |
| **(g) reading-path** (§6) | Suggest-level only for BETA | **Restored + rebuilt** — P2-4a machinery → catalog **v1.1** tuple + P2-4c hybrid classifier (S1+S2+S3 DONE) | Grounding: AC-6 strike GREEN 8/8 + held-out. Reading-path: catalog-approach 0.93 (Claude-labeled) ≠ built-classifier (UNMEASURED; 0.071 on stale perceptions); escalation live-proven but over-fires (93%) | **PASS (grounding) / BUILT-BUT-UNCALIBRATED (reading-path)** — full tuple classifier shipped + escalation live-proven; **honest accuracy + escalation calibration is P2-4b** (re-perceive → recalibrate → measure), not yet earned. *(Was: PARTIAL — calibration operator-gated.)* |

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

**Last pathway update:** 2026-06-23 (P2-4c S1+S2+S3 all DONE; P2-4b reframed as the real calibration gate after the S3-T11 live dry-run found 0.93=catalog-approach ≠ built-classifier).

### 11.1 You are here

**P2 fidelity arc — grounding closed; reading-path tuple classifier fully BUILT (P2-4c S1+S2+S3 all DONE) but NOT yet calibrated/validated.** The disaster-level grounding regression is **struck** (P2-1/2/3 + AC-6). The reading-path leg deepened past P2-4a: operator training tuned the catalog to a **compositional tuple** (`reading-path-patterns-catalog.md` **v1.1**, party 6/6 + operator-ratified D1–D3); a **held-out confirm/deny round** scored **0.93** — ⚠️ **that 0.93 is the catalog-approach (Claude-in-loop labels) vs gold, NOT the built classifier.** The catalog was then built into the classifier as **P2-4c** (additive tuple schema + hybrid-(c)): **S1 (geometry+schema), S2 (image-role tiers), and S3 (gpt-5.5 escalation) are ALL CLOSED** (each: Codex NEW CYCLE → Claude T11 → party 5/5 CLOSE; S1 & S2 each took one hand-back; S3 closed-with-riders). **The live frontier is now P2-4b — the REAL calibration + honest-accuracy gate, NOT a rubber-stamp.** An S3-T11 live dry-run of the *built* classifier vs gold scored **0.071 primary-key on STALE perceptions** (captured pre-S2-role_tier; geometry backfill only) and the escalation predicate **over-fired at 93%** (vs the 20% ceiling). So P2-4b owns a 4-leg job: **re-perceive the held-out under S2's role_tier prompt → recalibrate the escalation predicate → re-measure honest built-classifier accuracy → (contingent) improve macro/image_role**. After P2-4b: P2 epic close → **BETA Phase-2 remainder** (T5b–T8) → **aspirational epics**.

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
  P2-4c S3 gpt-5.5 escalation tuple-delta ......... ✅ done  (5/5 CLOSE-WITH-RIDERS; live-proven 0-degraded but UNCALIBRATED — 93% escalation, threshold PERMISSIVE)
  P2-4b finalize — REAL calibration + honest accuracy ⏸ NOT one-command. 4 legs: re-perceive under S2 role_tier → recalibrate predicate → measure built-classifier accuracy → contingent macro/image_role improve. (0.93 = catalog-approach NOT built-classifier; built scored 0.071 on stale perceptions)
  P2 epic retrospective + close ................... ❌ after P2-4b

[AFTER P2 — BETA Phase 2 / charter remainder]
  T5b Variant N-dispatch + per-slide bind ......... ❌ not started
  T6 Review lanes (ingestion / lesson-plan / Tracy)  ❌ not started
  T7 Marcus SPOC deepen (beyond scripted approve) .. ◐ thin MVP exists; not full spec
  T8 Motion plan (honest producer OR ratified carve) ❌ carved in practice, not ratified in writing
  S0.4 Full per-gate live-dispatch harness ........ ◐ auto-retry only
  Full BETA §8 dress rehearsal (a+b+c+e binding) .. ❌ not met (two qualifying runs used approve-path + default voice)

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
| P2-4c S3 (gpt-5.5 escalation) | ✅ 5/5 CLOSE-WITH-RIDERS | live-proven (0 degraded) but UNCALIBRATED — 93% escalation; threshold PERMISSIVE |
| **P2-4b — REAL calibration + honest accuracy** | ⏸ **the live frontier** | 4 legs: re-perceive (role_tier) → recalibrate predicate → measure built-classifier accuracy → contingent improve. NOT one-command. |
| P2 epic close | ❌ after P2-4b | |
| BETA Phase 2 (T5b–T8) | ❌ not started | after P2 |

**You are here →** the reading-path tuple classifier is **fully BUILT** (P2-4c S1+S2+S3 done + reviewed) but **NOT yet calibrated/validated**. The S3-T11 live dry-run revealed the 0.93 was the **catalog-approach (Claude labels)**, not the built classifier (0.071 on stale perceptions; 93% escalation). The next milestone, **P2-4b, is genuine calibration work** (re-perceive → recalibrate → measure), not a rubber-stamp.

### 11.4 Completion horizons

**Horizon 1 — Product trust restored (P2 complete).** Narration grounds on the *rendered* slide (P2-3 ✅); a fail-loud detector catches hallucinations (P2-1/2/3 ✅); the compositional-tuple classifier is BUILT (P2-4c S1+S2+S3 ✅) but **not yet calibrated** — the built-classifier accuracy is UNMEASURED (0.93 was the catalog-approach; built scored 0.071 on stale perceptions; escalation over-fires 93%). **Exit:** "error-free" means mechanics **and** fidelity — and reading order is classifier-verified on real slides at a *measured, honest* accuracy. *(Grounding+detector exit met 2026-06-21; reading-path exit needs **P2-4b real calibration**: re-perceive → recalibrate → measure.)*

**Horizon 2 — BETA spec as written (`beta-spec §8`).** Variant picker mechanics (T5b); Tracy on the trial path (T6d); dedicated lesson-plan / ingestion review surfaces (T6b/c); Marcus SPOC beyond scripted approve-path (T7); motion carve-out ratified or an honest producer (T8); two qualifying runs exercising **binding voice + variant picks** (not approve-path only). **Exit:** the conversational Marcus product on the frozen corpus, error-free twice **to spec**.

**Horizon 3 — Full APP vision (epics on the shelf).** Learning/intelligence (Epic 15), bounded autonomy (16), full research (17), new asset families (18); Lesson Planner MVP integrated into production trials; cross-corpus generality, motion synthesis, greenfield specialists. **Exit:** a multi-corpus, multi-use-case platform — months beyond the current arc.

### 11.5 Honest progress estimate

| Universe | Approx. complete | Basis |
|---|---|---|
| LangGraph migration substrate | **~95%+** | shipped; Slabs 1–7c closed |
| BETA Phase 1 (engine reliability + voice bind) | **100%** | ratified closed (Option B) |
| P2 fidelity / perception arc | **~85%** | grounding 100% (P2-1/2/3 + strike); reading-path classifier fully BUILT (catalog v1.1 + P2-4c S1/S2/S3 done) but **calibration/validation NOT done** — built-classifier accuracy unmeasured (0.93 was catalog-approach; 0.071 on stale); P2-4b is a real 4-leg calibration milestone, not a rubber-stamp |
| BETA Phase 2 / full §8 spec | **~25–35%** | voice mechanics + thin SPOC; variants/research/motion/full-path open |
| Full APP (Epics 15–18 + LP integration) | **~15–20%** | substrate exists; not wired to the operator product |

**Bottom line:** the reading-path tuple classifier is **fully BUILT** (P2-4c S1+S2+S3 closed) but **not yet calibrated or honestly validated** — the S3-T11 live dry-run revealed the 0.93 was the catalog-approach (Claude labels), while the *built* classifier scored 0.071 on stale perceptions and escalation over-fires at 93%. So the next milestone, **P2-4b, is real calibration work** (re-perceive under role_tier → recalibrate the predicate → measure honest built-classifier accuracy → contingently improve), NOT a one-command rubber-stamp. After P2-4b: P2 close → **BETA charter remainder (T5b–T8)** → **aspirational epics**. (The NEW CYCLE T11 gate has earned its keep: across S1/S2/S3 it caught over-claim, vacuous-gate, index-misalignment, AND — via the S3 live smoke — a believed-green metric-attribution error that the green battery + a synthetic harness self-test both hid.)
