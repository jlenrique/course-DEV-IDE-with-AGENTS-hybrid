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

## Honest caveats carried into the trial (not hidden)
- Reading-path accuracy is measured on the CONSUMED-14 dev set (~image_role 0.82 / primary-key ~0.68, n=14 ±1-slide roll-noise) — a **fresh naive holdout** is required before any *generalization* claim (`reading-path-fresh-naive-holdout-pre-trial`; Mary's standing dissent).
- A fresh full smoke would additionally validate the *new* content-first voice (the cadence cleanup landed AFTER `386912d6`) and produce a fresh Storyboard B for operator review — recommended as part of trial-1 or a quick pre-trial confirmation.
- Non-default voice WPM + motion synthesis remain known queued items.
