# State of the App — Canonical Status Synthesis

**Date:** 2026-06-19
**Status:** Canonical orientation doc. Single source of truth for "where the development plan actually stands."
**Provenance:** Synthesizes two independent assessments produced 2026-06-19 — (1) the live session assessment (triangulating `SESSION-HANDOFF.md`, `next-session-start-here.md`, `bmm-workflow-status.yaml`, `deferred-inventory.md`, the BETA spec/charter, and on-disk run evidence), and (2) an independent external analysis triangulating the same artifacts. Where the two diverged, the divergences were adjudicated against on-disk evidence (git history, `slab-7c-retrospective.md`, run directories); both factual conflicts resolved in favor of the external analysis (see §10). This doc exists so the plan does not have to be re-derived every session.

> **Maintenance:** refresh at (a) each arc/epic close that materially changes validated scope, (b) any trial postmortem that moves a §4 scorecard row, (c) any governance ratification that changes how BETA or the forward arcs are tracked. Keep the §4 scorecard and §5 tracker-reality table honest — they are the load-bearing anti-drift surfaces.

---

## 1. The three-layer "done" — why status feels disorienting

The single biggest source of confusion is that **three different things each have their own "done," and they are routinely conflated.** Read every status claim through this lens:

| Layer | What "done" means here | Honest status |
|---|---|---|
| **A. Migration substrate** (Slabs 1–7c) | BMAD stories closed in `sprint-status.yaml` | **Largely shipped & BMAD-closed.** `migration-master-status: shipped`. Slabs 1–6 done; 7a 8/8, 7b done, 7c 36/36 (closed 2026-05-07). |
| **B. Production trial engine** (G0→completion) | The runtime actually produces a narrated-deck lesson end-to-end on a real corpus | **Validated.** Trial-4 PASS; engine error-free ×2 + Marcus-SPOC error-free ×2 on disk (2026-06-19). |
| **C. BETA spec as written** (`beta-spec-2026-06-19.md §8`) | The full conversational product: a+b+c+e through Marcus-SPOC with binding picks, d+f present/carved, §5 quality infra green, error-free twice | **NOT met.** Partially demonstrated under narrow interpretations (see §4). |
| **D. Product quality** (narration fidelity) | The narration describes what is actually on the slide, in scan order | **🔴 Regressed — disaster-level.** Pass-2 grounds on the slide *brief*, not the rendered slide. |

**The trap:** Layer A's "shipped" and Layer B's "validated" are real and earned. They do **not** imply Layer C ("BETA met") or Layer D ("quality good"). The recent BETA work is best described as **reliable pipeline mechanics with a thin Marcus wrapper**, on a path that does not yet exercise the full spec and actively masks a Layer-D regression.

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

**One-line reality:** *The platform reliably produces a narrated slide deck (text + visuals + audio + published storyboard) from a corpus, with operator review gates and recoverable errors, driven by a conversational Marcus.*

---

## 3. 🔴 THE CRIPPLING — fidelity regression + a metric that cannot see it (Layer D)

This is what makes BETA feel "crippled," and it is **more dangerous than a flaky pipeline:**

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
| **(g) reading-path** (§6) | Suggest-level only for BETA | **Regressed** (see §3) | — | **FAIL** — perception + reading-path lost, below even suggest-level |

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
- **BETA carry-forward:** `beta-voice-select-wpm-qa-interaction`; `trial-4-binding-variant-voice-picker`; `beta-d-research-review-trial-path-attach`; `beta-motion-synthesis-data-plane`; `beta-generality-across-corpora`; `beta-marcus-namespace-collision-rename`; the merged perception+reading-path arc.
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

1. **Voice↔WPM quick win** (`beta-voice-select-wpm-qa-interaction`) — smallest honest unblock to take capability-(e) to completion on a non-default voice. Party QA-semantics decision (re-target / operator-overridable / widen tolerance), then a non-default-voice run completes error-free.
2. **Perception + reading-path REPAIR + ENHANCE** (the disaster arc) — restore perception grounding (vision pass over rendered PNGs → `PerceptionArtifact` → Pass-2 narrates from perceived visuals); restore reading-path classification (`reading_path` field + conformance check); **and ship a fail-loud fidelity detector** (§3) as a co-equal deliverable. Likely a `bmad-create-prd`/architecture-scale arc; schema-shape discipline; any manifest/pack touch → pipeline-lockstep regime.
3. **Governance / spec ratification** — ratify in writing what "BETA" means (engine-reliability Phase 1 vs full §8), and file the BETA remainder as real epics/stories so charter, handoff, and sprint-status stop drifting (§5).

---

## 9. Governance decision — RESOLVED (Option B, party-ratified 2026-06-19)

**Question:** how should the June BETA program be formally represented in BMAD?

**RESOLVED: Option B**, unanimous 5/5 in a fully-spawned party-mode round, operator-ratified. Ratify **"BETA Phase 1 = engine-reliability + voice-binding"** closed *in writing*; file only forward stories; **no retroactive Epic 35** (all five voices judged it audit-ledger fiction). `deferred-inventory.md` remains the single source of truth for gaps. Durable artifact: [`_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md`](../_bmad-output/planning-artifacts/beta-phase-1-closure-ratification-2026-06-19.md) — which is also the **authority for the ratified forward path** (P3→P1→P2 structure in §8 above). Binding riders: "error-free" rebranded **"error-free (mechanics only — fidelity unverified)"** until the P2 detector lands; deferred-inventory + cross-trial-learnings updates promoted from consultation to a **DoD gate** on every forward story.

---

## 10. Adjudication record — where the two analyses diverged

Both factual conflicts resolved against on-disk evidence, **in favor of the external analysis**:

1. **Slab 7c completion.** Session assessment cited "72% (26/36)"; external cited "done." Evidence: `slab-7c-retrospective.md` = **36/36 DONE, closed 2026-05-07**; `sprint-status.yaml:1620` = `done`. The 72% was a stale 2026-05-06 mid-marathon figure. **External correct.**
2. **sprint-status staleness.** External said "last meaningfully updated 2026-05-07"; actual last touch was **2026-05-22** (Epic-34 tombstone). Minor date error, but the substantive claim — that the tracker predates and omits all June BETA work — is **verified correct** (grep → 0 BETA entries).

**The external analysis's sharpest, correct contribution** (which the session assessment underweighted): *the success metric is blind to the fidelity regression — "error-free" masks confident-wrong output* (§3). This doc adopts that framing as load-bearing.
