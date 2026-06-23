# Next-Trial Readiness Checklist + Verdict (2026-06-23, `/goal` v9)

**Corpus:** `course-content/courses/tejal-apc-c1-m1-p2-trends` (frozen). **Branch:** `fidelity-perception-arc-2026-06-19`.

## Readiness matrix

| Axis | State | Evidence |
|---|---|---|
| **Tool/connectivity** | ✅ READY | Pre-flight 9 ready / 0 failed — Gamma/Canvas/Notion/ElevenLabs/Qualtrics/Wondercraft/Kling/Descript/Box all live |
| **Pipeline completes G0→done** | ✅ READY | Smoke `386912d6` completed (0 hard-blocks, 0 degraded), real Storyboard A+B published |
| **Perception (reading-path)** | ✅ READY | LLM-first (gpt-5.5 authoritative tuple); image_role ~0.79–0.86, macro 0.857; safe-degrade; T11 closed `e8e8c4e`. ⚠️ honest: numbers are on the CONSUMED-14 (resubstitution; a fresh naive holdout is the true generalization gate — Mary) |
| **Narration voice** | ✅ READY | Content-first voice principle + softened spatial cadence tokens committed (`5147e0f`, `148fea9`); operator validated Storyboard-B alignment as "SO GOOD" |
| **Reading-path no longer hard-blocks** | ✅ READY | Irene conformance → advisory (warnings observable, never halts a run) |
| **Variant distinctness** | 🟡 QUEUED (preferred, NOT blocking) | Variant arc party-green-lit (3/3) + Codex-prompt-ready (`codex-dev-prompt-variant-arc.md`); NOT built (Codex-gated). **John Q4: single-variant is an acceptable trial-1 fallback** |
| **Voice/WPM (non-default voice)** | 🟡 known item | `beta-voice-select-wpm-qa-interaction` open; clean path uses default voice |
| **Motion (f)** | 🟡 review-only | Motion data-plane structurally unproven; narrated-deck deliverable is the trial scope |

## Verdict
**READY for a next trial run on the voice/perception axis, with single-variant as the trial-1 fallback.** The capabilities the goal set out to restore/improve (LLM-first perception, content-first narration, fail-safe reading-path) are DONE, committed, and validated end-to-end by `386912d6`. The variant arc is a green-lit, Codex-ready ENHANCEMENT — preferred but not a blocker (per party).

## The operator fork (STOP-and-ASK — goal stop condition)
Two honest paths to the next trial:
- **(A) Proceed to trial-1 NOW** with single-variant (variant arc queued for trial-2). Fastest; exercises all the new voice/perception work live.
- **(B) Build the variant arc first** — dispatch Codex on `codex-dev-prompt-variant-arc.md` → Claude T11 → then trial with genuine 2-up distinctness.

## Fresh smoke (v9) — COMPLETED end-to-end
**Trial `242b859f-024f-4458-be8d-a94a8c69c45e`: status=`completed`, 0 errors, 0 hard-blocks**, driven G0→done via automated approve-verdict gate-resume. Exercised LIVE: LLM-first reading-path perception, the NEW content-first narration voice (cadence cleanup, committed after `386912d6`), real ElevenLabs audio on all 6 segments, fresh Storyboard A+B. Evidence: `smoke-v9-result.json`. Fresh Storyboard B: `…/storyboards/242b859f-…-b/index.html`.

## Trial-readiness party-mode green-light (2026-06-23)
- **John (PM): GREEN-WITH-CONDITIONS.** C1 mandatory consumed-14 provenance label on every number; C2 fresh naive holdout = named POST-trial gate; C3 narrated-deck scope fence (motion review-only, WPM open); C4 single-variant declared as trial-1 fallback not target; C5 trial purpose stated as "verification, NOT accuracy certification." Risk consciously accepted: primary-key ~0.68 in-sample is soft, bounded by safe-degrade.
- **Murat (QA): GREEN-WITH-CONDITIONS.** This is a VERIFICATION run (operability), NOT a benchmark; completion ≠ correctness; **no "X% accurate" claim may be derived from the consumed-14** (forbidden in any output/handoff); every number subject+substrate-tagged with the n=14 ±7% noise floor stated inline; generalization = UNMEASURED until the holdout rescan; single-roll provenance recorded. No dissent.
- **Mary (evidence-integrity): GREEN-WITH-CONDITIONS.** Dissent **SATISFIED for the trial-1 verification scope** (resubstitution is the *correct* instrument for "does it hold where we looked") and **STANDS as the tripwire for any generalization/scale claim** until the fresh naive holdout clears. H1–H4 governance record: H1 provenance (14 = consumed reserve); H2 measurement-class (resubstitution/in-sample upper bound); H3 admissible-claim (end-to-end fidelity verification ONLY); H4 inherited-green (the caveat is STICKY — any downstream artifact citing a consumed-14 number inherits H1–H3; a number can't be laundered clean by copying into a cleaner summary).

## ✅ VERDICT — UNANIMOUS 3/3 GREEN-WITH-CONDITIONS (no impasse) → terminal state (a) reached
**The next trial run (TRIAL-1, single-variant, narrated-deck) is READY.** Binding conditions (all three voices converge):
1. **Verification run, NOT a benchmark** — purpose stated at launch: end-to-end substrate verification of LLM-first reading-path + content-first voice + live audio; NOT a perception-accuracy / generalization certification.
2. **Resubstitution stamp on EVERY reading-path number** (consumed-14, n=14 ±7% roll-noise, in-sample upper-bound) — sticky/inherited; **no "X% accurate" claim off the consumed-14**, ever.
3. **Single-variant = accepted trial-1 fallback** (variant arc party-green-lit + Codex-ready, unbuilt) — declared, not silent.
4. **Fresh naive holdout = BINDING post-trial gate** before any generalization / ready-at-scale claim (`reading-path-fresh-naive-holdout-pre-trial`; instrument `reading_path_holdout_rescan.py` staged). This is what flips Mary's dissent from open→satisfied-for-scope.
5. **Scope fence: narrated-deck only** — motion review-only; non-default-voice WPM open; both recorded as known-open.

## Honest caveats carried into the trial (not hidden)
- Reading-path accuracy is measured on the CONSUMED-14 dev set (~image_role 0.82 / primary-key ~0.68, n=14 ±1-slide roll-noise) — a **fresh naive holdout** is required before any *generalization* claim (`reading-path-fresh-naive-holdout-pre-trial`; Mary's standing dissent).
- A fresh full smoke would additionally validate the *new* content-first voice (the cadence cleanup landed AFTER `386912d6`) and produce a fresh Storyboard B for operator review — recommended as part of trial-1 or a quick pre-trial confirmation.
- Non-default voice WPM + motion synthesis remain known queued items.
