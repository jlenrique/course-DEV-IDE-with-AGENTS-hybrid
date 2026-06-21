# State of the App — Canonical Status Synthesis

**Date:** 2026-06-19 · **Last updated:** 2026-06-21 (P2 fidelity arc — grounding regression CLOSED)
**Status:** Canonical orientation doc. Single source of truth for "where the development plan actually stands."

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
| **D. Product quality** (narration fidelity) | The narration describes what is actually on the slide, in scan order | **🟢 Grounding leg FIXED (2026-06-21); reading-path calibration pending.** Pass-2 now grounds on the perceived rendered slide (`PerceptionArtifact`), guarded by a fail-loud G5 detector (P2-1/2/3 + AC-6 live strike). Reading-path **machinery** restored (P2-4a); reading-path **calibration accuracy on real slides** (P2-4b) is operator-gated. *(Was: "🔴 Regressed — disaster-level; Pass-2 grounds on the slide brief.")* |

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
| **(g) reading-path** (§6) | Suggest-level only for BETA | **Restored (machinery)** — perception grounding + `reading_path` classifier + fail-loud verify-node (P2-1/2/3/4a) | Grounding: AC-6 live strike GREEN 8/8 + held-out (2026-06-21). Reading-path accuracy: pending P2-4b corpus | **PASS (grounding) / PARTIAL (reading-path)** — perception + scan-order machinery shipped; real-slide scan-order *calibration* is P2-4b (operator-gated). *(Was: FAIL — perception + reading-path lost.)* |

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
2. **Perception + reading-path REPAIR + ENHANCE** (the disaster arc) — **✅ DONE (2026-06-21), except the operator-gated calibration leg.** Shipped as the PRD-gated P2 arc: perception grounding restored (vision pass → `PerceptionArtifact` → Pass-2 narrates from perceived visuals; P2-2/P2-3), reading-path classification + fail-loud conformance restored (`reading_path` field + classifier + verify-node; P2-4a), and the **fail-loud fidelity detector shipped first as committed RED evidence** (P2-1). AC-6 live regression-green strike FIRED. **Remaining:** **P2-4b** (reading-path repertoire growth + held-out ≥80% real-slide conformance corpus) — operator-gated on a scan-order exemplar harvest.
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

**Last pathway update:** 2026-06-21 (P2-4a closed).

### 11.1 You are here

**P2 fidelity arc — machinery COMPLETE; only the operator-gated calibration leg (P2-4b) remains.** P2-1/2/3/4a are closed and the disaster-level grounding regression is **struck** (AC-6 live strike fired). The live frontier is **P2-4b**, blocked on an operator scan-order exemplar harvest. After P2 closes, the ratified path turns to the **BETA Phase-2 charter remainder** (T5b–T8), then the **aspirational epics**. Latest close: **P2-4a `done` at `38f2ba8`** (Codex T1–T10 → Claude T11 → party-mode 5/5).

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
  P2-2 Vision node + PerceptionArtifact ........... ✅ done
  P2-3 Pass-2 consumes perceived visuals .......... ✅ done  (+ AC-6 live regression-green strike FIRED → regression STRUCK)
  P2-4a Reading-path native machinery ............. ✅ done  (Codex T1–T10 → Claude T11 → 5/5 CLOSE, 38f2ba8)
  P2-4b Repertoire growth + ≥80% real-slide corpus  ⏸ operator-gated (scan-order harvest) — LAST P2 item
  P2 epic retrospective + close ................... ❌ after P2-4b (machinery-only partial close possible sooner)

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

### 11.3 Position-in-sequence

| Milestone | Status | Notes |
|---|---|---|
| P2-3 close + grounding strike | ✅ `485662e` | AC-6 live strike GREEN 8/8 + held-out |
| P2-4 party green-light + spec | ✅ `da9e186` | 5/5 PARTIAL-SPEC-NOW (machinery vs calibration split) |
| P2-4a dev (T1–T10) | ✅ Codex | handoff `_codex-handoff/p2-4a-…ready-for-review.md` |
| P2-4a T11 review + close | ✅ `38f2ba8` | 3-layer review + party 5/5 CLOSE + 2 ratified hardenings |
| **P2-4b operator harvest + story** | ⏸ **blocked on operator** | ≥8–10 labeled real slides + ≥1 known-wrong-default |
| P2 epic close | ❌ after P2-4b | machinery-only partial close optional |
| BETA Phase 2 (T5b–T8) | ❌ not started | after P2 |

**You are here →** one operator input (the scan-order harvest) from unblocking the **final P2 story**; the machinery half of the top-priority fidelity arc is closed.

### 11.4 Completion horizons

**Horizon 1 — Product trust restored (P2 complete).** Narration grounds on the *rendered* slide (P2-3 ✅); a fail-loud detector catches hallucinations (P2-1/2/3 ✅); scan-order machinery live (P2-4a ✅); real-slide scan-order calibration (P2-4b ⏸). **Exit:** "error-free" means mechanics **and** fidelity — and reading order is verified on real slides. *(Grounding+detector exit already met 2026-06-21; reading-path-calibration exit pending P2-4b.)*

**Horizon 2 — BETA spec as written (`beta-spec §8`).** Variant picker mechanics (T5b); Tracy on the trial path (T6d); dedicated lesson-plan / ingestion review surfaces (T6b/c); Marcus SPOC beyond scripted approve-path (T7); motion carve-out ratified or an honest producer (T8); two qualifying runs exercising **binding voice + variant picks** (not approve-path only). **Exit:** the conversational Marcus product on the frozen corpus, error-free twice **to spec**.

**Horizon 3 — Full APP vision (epics on the shelf).** Learning/intelligence (Epic 15), bounded autonomy (16), full research (17), new asset families (18); Lesson Planner MVP integrated into production trials; cross-corpus generality, motion synthesis, greenfield specialists. **Exit:** a multi-corpus, multi-use-case platform — months beyond the current arc.

### 11.5 Honest progress estimate

| Universe | Approx. complete | Basis |
|---|---|---|
| LangGraph migration substrate | **~95%+** | shipped; Slabs 1–7c closed |
| BETA Phase 1 (engine reliability + voice bind) | **100%** | ratified closed (Option B) |
| P2 fidelity / perception arc | **~95%** | P2-1/2/3/4a closed + strike fired; only operator-gated P2-4b remains |
| BETA Phase 2 / full §8 spec | **~25–35%** | voice mechanics + thin SPOC; variants/research/motion/full-path open |
| Full APP (Epics 15–18 + LP integration) | **~15–20%** | substrate exists; not wired to the operator product |

**Bottom line:** the project is **one review-and-close cycle past** the machinery of its top-priority fidelity arc — P2-1/2/3/4a done, the disaster regression struck. Total completion still needs **P2-4b (operator evidence)**, then the **BETA charter remainder (T5b–T8)**, then the **aspirational epics** — a long tail after P2 closes.
