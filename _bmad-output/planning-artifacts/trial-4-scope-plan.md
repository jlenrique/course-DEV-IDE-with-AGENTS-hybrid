# Trial-4 scope plan — feature-rich full-walk trial

**Ratified:** 2026-06-18, bmad-party-mode trial-scoping round (Winston/Amelia/Murat/John, unanimous, no impasse).
**Supersedes:** the `roadmap-consensus-2026-06-12` "Trial A = FROZEN-engine baseline, then WAVE-1, then Trial B" sequencing. Operator directive ("the next run should fully exercise available functionality while bringing online a number of features already requested") merges the frozen-A baseline and the WAVE-1 feature trial into ONE feature-rich trial.

## Decision: one feature-rich full-walk trial
- The frozen-A baseline is RETIRED as a separate trial. Rationale (Murat, releasing his prior advocacy): the pre-WAVE-0-fix clean-engine window already closed when the storyboard-correctness fix (`cabbf2c`) merged; a fresh frozen pass would cost a full run cycle for an artifact whose only job is a "before" snapshot.
- **Baseline mitigation (Murat):** pin a **golden-run replay fixture** from the best prior certified run (receipts + pause-topology + envelope outputs frozen on disk) as the regression baseline. ~80% of frozen-A's isolation value at ~5% of the cost. (Action item; not blocking arc-1.)

## Coverage floor — what earns the word "full" (Murat)
Full spine, every gate traversed, no folded-≠-exercised cheating:
G0 directive (real composition, not pre-baked) → G1 corpus/clustering → G2B + G2C storyboards → G3 (first full-run proof of the WAVE-0 storyboard-correctness fix) → G4 voice → G5 audio/handoff.
**Minimum genuine HIL:** ≥1 real variant-pick pause (G2B) + ≥1 real voice-pick pause (G4A), each taking a human pick and threading it downstream (receipt proves the pick).

## Feature backlog — dependency-ordered (hard chain: Arc1 → Arc2; Arc3 parallel)

### Arc 1 — gate-engine backbone (the one real engine cut; full spec→party→implement→review)
**1a. pause-topology contract pin** (root — defines WHERE pauses are contractually legal in the walk). Land FIRST; it is the contract the fold fix must conform to (Winston: fixing fold without the pin re-derives topology inside the engine — the churn the freeze guarded against).
**1b. fold-semantics gate-engine fix** — make a `fold_with` gate able to pause AFTER its parent content node runs (today it pauses BEFORE → the voice/variant HIL is "HIL-in-name-only," choosing blind). The ONLY engine-cutting item; highest structural risk. Conforms to 1a.
*Pins gating arc-1 (Murat):* pause-topology pin self-validates; fold-semantics needs a golden-replay test proving every gate's fold/pause decision matches the contract table in both folded and unfolded states.
*Batch 1a+1b into one arc (Winston/Amelia — same gate-engine surface; pin-then-fix avoids a second pass).*

### Arc 2 — selection wakes (additive; STRICTLY after Arc 1; batch the two)
**2a. G2B variant-pick wake** (operator picks storyboard A/B).
**2b. G4A voice-pick wake** (operator picks voice; closes `voice-selection-hil-fold-defect`).
Parallel siblings once fold lands (Winston). Batch as one "selection wakes" spec — identical wake plumbing (pause point → operator prompt → resume with selection threaded; receipt proves it). *MUST NOT ship before Arc 1* (HIL-in-name-only trap — Amelia: "filing them as quick-devs would be malpractice").
*Pins (Murat):* each gate genuinely pauses, receives a pick, resumes with the pick threaded downstream; receipt shows the pick.

### Arc 3 — measured-durations (parallel quick-dev; independent surface)
mp3 probe post-TTS → real measured durations → re-arm G5 WPM check (closes `enrique-measured-durations`). No gate-engine contact; runs parallel to Arc 1/2. Snapshot test that measured durations populate + are sane vs estimates.

## Deferred (NOT in trial-4)
- **Witness→strict envelope-validator flip** — stays WITNESS for trial-4 (its gate "this trial's S5 anomalies.jsonl reviewed clean" is definitionally unsatisfiable before the trial that introduces the new behavior — Murat). Dev-time strict DRY-RUN early to surface producer gaps against static substrate (Winston/Amelia), but the runtime flip gates the trial AFTER trial-4 (review trial-4 anomalies clean → flip for trial-5).
- **Motion (kira)** — HARD OUT (unanimous). Unproven/input-starved (cycle-5/6 four-layer-silence investigation); requires a net-new manifest motion-plan producer + un-defaulting kira + un-folding G2F + compositor `[]` rejection = a dp-v2 motion data-plane arc, not a trial feature. Would confound trial-4 attribution. Reactivation trigger: dp-v2 motion data-plane substrate lands.

## Non-negotiable (Winston): if schedule pressure forces a cut, cut from the FRONT (drop measured-durations / defer the strict dry-run) — NEVER ship Arc 2 ahead of Arc 1. "A trial with two real pauses beats a trial with prettier slides where the pauses are lying."

## Execution status
- [ ] Arc 1 — pause-topology pin + fold-semantics (spec → party → implement → review → push)
- [ ] Arc 2 — G2B + G4A selection wakes (gated by Arc 1)
- [ ] Arc 3 — measured-durations (parallel)
- [ ] Golden-run replay baseline pinned (Murat)
- [ ] Trial-4 run (after Arc 1+2 land; Arc 3 if ready)
