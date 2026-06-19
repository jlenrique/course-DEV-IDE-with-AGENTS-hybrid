# BETA Phase 1 — Closure Ratification & Forward-Path Authority (2026-06-19)

**Status:** RATIFIED. Operator (Juan) is the ratifying authority; ratified 2026-06-19 following a fully-spawned 5-agent party-mode round (Winston/architect, John/PM, Murat/test-architect, Mary/analyst, Amelia/dev). This is the **durable home for the ratified forward path** referenced by `docs/STATE-OF-THE-APP.md` §9 and `next-session-start-here.md`.

**Governance basis:** CLAUDE.md sprint-governance §2 (party-mode green-light), §4 (consensus), and the party-mode roster requirement (fully spawned, not impersonated). Panel verdict: **unanimous (5/5)** on Items 1 & 2; Item-3 P1-timing fork resolved by operator ("Ratify as recommended").

---

## 1. What is CLOSED

**BETA Phase 1 = engine-reliability + voice-binding. CLOSED by ratification.**

Evidence on disk (frozen corpus `tejal-apc-c1-m1-p2-trends`):
- **Engine error-free ×2** — runs `b7919f65` + `bb76170c` (`beta-error-free-twice-milestone-2026-06-19.md`), zero Class-A, Class-B within the §2 flake budget (auto-retry absorbed Irene slide-join variance).
- **Marcus-SPOC error-free ×2** — runs `e2291039` + `74f72a4c` (`marcus-spoc-ag-demonstration-2026-06-19.md`), a–g narrated per gate.
- **Voice-binding proven live** — run `710684c0` (operator `select` → synthesis emits the picked voice).
- **S0 foundation** — crash-taxonomy (`5c9cbea`), ingestion-report (`6497514`), card candidates (`a0d85a8`), `select` verb (`c1fc663`), voice re-route (`3b5eec0`), ratchet (`b87bc2d`), auto-retry keystone (`e9d20be`), SPOC (`9ec7a40`).

This is a **true and valuable claim about engine reliability on a reduced (approve-path) trial.** It is closed because the work shipped, was validated, and no forward decision executes against it.

## 2. What Phase 1 did NOT cover (binding carve-out)

Phase 1's "done" **explicitly excludes** the following §8 capabilities. This enumeration is the artifact that prevents "error-free ×2" from ever again being misread as "BETA §8-met":

- **(e) variant generation** — Gary N-dispatch / per-slide variant pick: **not started** (`trial-4-binding-variant-voice-picker`).
- **(d) research review** — Tracy on the trial path: **production-path orphaned** (`beta-d-research-review-trial-path-attach`).
- **(f) motion-plan review** — see §4 (carved out in writing here).
- **(g) reading-path + perception fidelity** — **REGRESSED, disaster-level** (see §3). Below even the BETA suggest-level.
- **(a)/(b)/(c) sources / ingestion / lesson-plan** — **PARTIAL** (thin conversational surface; S0.2 ingestion has a residual summary-timing bug).
- **Voice-binding-to-completion on a non-default voice** — gated on the WPM policy (§5; `beta-voice-select-wpm-qa-interaction`).

## 3. The known defect carried forward (named, dated coverage-debt)

**`fidelity-metric-blind-to-perception-regression`** (filed 2026-06-19; repaired-forward in P2 below).

Pass-2 narration grounds on the slide **brief**, not the rendered PNG → it narrated a "$5.2T line + bars" chart never rendered (slide shows $4.5T stat callouts + a photo). The perception layer + reading-path (Z/F/triptych scan-order) machinery were severed at the 2026-04-24 upstream cut. **The G5 quality gate is anti-correlated** (Murat): it checks script/audio mechanics, not narration↔rendered-slide fidelity, so a green "error-free" signal rises *with* the volume of confident-wrong output. Top-of-register risk. Repaired forward as P2; the detector (P2-1) converts this defect into a permanent regression guardrail.

## 4. Motion (f) carve-out — RATIFIED IN WRITING

Per BETA spec §4.6 (Winston A2 / Murat G-Q4): **(f) motion-plan review is carved out of the BETA error-free claim.** No honest motion-plan producer exists; G2F stays unwoken (no theater gate). Motion *synthesis* remains out of scope (`beta-motion-synthesis-data-plane`). This closes the prior "CARVED (not ratified)" governance hole.

## 5. WPM-policy ruling (unblocks P1)

The G5 WPM floor (130) is **not voice-agnostic in effect** — Sarah's natural 128 WPM trips it (same disease as §3, smaller dose: a gate asserting the wrong invariant). RULING (Murat, operator-ratified):
- **Target:** an evidence-backed, genuinely **voice-agnostic** intelligibility floor (the floor exists to catch *runaway-fast* TTS, not natural cadence — the real floor is likely well below 128).
- **Interim (if empirical work deferred):** lower the universal floor to the documented slowest natural voice rate minus margin, with a code comment citing why. **Not** a per-voice table (N gates drift), **not** blanket operator-override.
- **Operator override:** retained only as **logged break-glass**, never the default path.

This makes P1 a clean `bmad-quick-dev` one-shot (~1 file + 1 shape-pin test).

## 6. Governance decision — Option B (no retroactive Epic 35)

**Unanimous 5/5.** The June BETA program ran Claude-direct quick-dev + trials (sanctioned by CLAUDE.md Cleanup-arc execution mode). It is **NOT** back-filled into `sprint-status.yaml` as a retroactive Epic 35 — all five voices judged that fiction that corrupts the audit ledger and taxes the sanctioned velocity mode. Instead:
- This document is the written closure.
- `deferred-inventory.md` remains the **single source of truth** for gaps; `sprint-status.yaml` carries a reconciliation banner pointing here + to STATE-OF-THE-APP.
- The charter's stale T5a/S0.4 "pending" lines are superseded by the charter's reconciliation banner.
- **"error-free" is rebranded** everywhere going forward to **"error-free (mechanics only — fidelity unverified)"** until the P2 detector lands (John, binding).
- **DoD gate (Mary, binding):** every forward story strikes/updates its deferred-inventory entry + harvests cross-trial-learnings — promoted from consultation to a **gating checkbox**.

## 7. Ratified forward path (authority for the next arc)

| # | Work | Workflow | Gate-mode | Sequence |
|---|---|---|---|---|
| **P3** | This closure ratification + reconciliation pass | written ratification (this doc) | n/a | ✅ **done** (this artifact) |
| **P1** | voice↔WPM → voice-agnostic floor per §5 ruling | `bmad-quick-dev` | single | **parallel** with P2-1 (orthogonal surface) |
| **P2** | perception + reading-path + fidelity detector | `bmad-create-prd` → `bmad-create-epics-and-stories` → `bmad-create-story` | — | after PRD |
| ↳ **P2-1** | **Fidelity detector — RED first** vs the $5.2T fixture; **Class-A / no-retry**; two-sided (catches bad, passes good) | create-story | **dual** | detector first; own story (do NOT fold) |
| ↳ **P2-2** | PNG-grounded `PerceptionArtifact` (schema-shape; scaffold; four-file lockstep; Pydantic-v2 14-idiom) | create-story | **dual** | turns detector partly green |
| ↳ **P2-3** | Pass-2 consumes perceived visuals — the regression fix (`app/specialists/irene/graph.py` `_assemble_pass_2_prompt`/`_slide_roster`; `pass_2_template.py`) | create-story | **dual** | turns detector fully green (regression-green) |
| ↳ **P2-4** | Reading-path (Z/F/triptych) native rewrite (do NOT re-absorb upstream) | create-story | single | last / parallel |

**Implementation correction (Amelia, binding):** P2 does **not** create a second perception authority. The PNG-grounded perception becomes the authority for *narration fidelity*; Vera's brief-derived perception drops to *secondary context*. Pass-2 grounds on the PNG-grounded artifact.

**Detector-first is non-negotiable (Winston + Murat, went to the mat):** P2-1 lands RED against the existing $5.2T trial as committed evidence the detector can catch the failure *before* the repair turns it green — preventing the vacuous-pass / "test tuned to the buggy output" trap. Any pipeline-manifest/pack touch in P2 → **pipeline-lockstep regime + party-mode green-light before dev.**

## 8. Panel attribution

Fully-spawned party-mode (real subagents), 2026-06-19:
- 🏗️ **Winston** — severed-control-loop framing; P2 = PRD-chain; detector separable + first.
- 📋 **John** — "error-free" is a liability phrase → rebrand mechanics-only; Option B decisive.
- 🧪 **Murat** — metric is *anti-correlated* not blind; detector RED-first, Class-A no-retry, two-sided, dual-gate; WPM voice-agnostic floor.
- 📊 **Mary** — construct-invalidity holds; Option B stops drift cheaper; promote inventory/cross-trial to a DoD gate.
- 💻 **Amelia** — one-perception-authority correction; 4-story red-green breakdown; P1 = policy-ruling-then-quick-dev.

Operator resolved the P1-timing fork: **P1 runs in parallel with the detector** (with §5 ruling making it a clean one-shot).
