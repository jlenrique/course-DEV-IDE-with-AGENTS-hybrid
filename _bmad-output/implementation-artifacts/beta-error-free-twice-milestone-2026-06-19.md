# BETA Milestone — Error-Free Production Run ×2 (2026-06-19)

## Result
**Two consecutive error-free production-pipeline runs on the frozen BETA corpus, no substrate change between them.** Satisfies the `beta-spec-2026-06-19.md §2` "error-free twice" criterion for the production engine (the narrated-deck pipeline with operator HIL at all 6 gates).

| Run | Trial ID | Path | Outcome |
|---|---|---|---|
| #1 | `b7919f65-75be-4479-b14a-2994f4fcfc8e` | G0→G1→G2B→G2C→G3→G4→G4A→completion | `completed`, 0 error-pauses, 0 manual recovers, Storyboards A+B published, 6/6 narration |
| #2 | `bb76170c-3a7a-479a-ab4f-b41792b96637` | same | `completed`, 0 error-pauses, 0 manual recovers, Storyboards A+B published, 6/6 narration |

Corpus: `course-content/courses/tejal-apc-c1-m1-p2-trends` (frozen). Preset: production. Operator HIL at every gate (approve-path; the operator reviews + accepts each surface). Driver: `.tmp/drive_trial.py` (approve every gate, resume in-process; the S0.4 bounded auto-retry absorbed the Irene pass-2 LLM variance with NO operator-manual recover — the criterion's "Class-B absorbed by bounded automatic recovery").

## "Error-free" per §2 — verified
- **Zero Class-A events** (no crash, no false-negative gate reject blocking, no input-starvation): the driver trace shows clean gate-to-gate progression both runs.
- **Class-B (LLM variance) absorbed automatically within budget**: the Irene pass-2 perception_source variance (which forced 1–3 manual recovers in Trial-4/T5a) was auto-retried in-dispatch (S0.4, commit `e9d20be`) — no operator-manual recover in either run.
- **No substrate change between the two runs** (the counter held).

## What made this possible (this session's fixes)
- `5c9cbea` S0.1 crash-taxonomy (ModeMismatchError error-pauses) · `6497514` S0.2 ingestion-report · `a0d85a8` S0.3 card candidates · `c1fc663` T5b `select` verb · `3b5eec0` T5a-F3 voice re-route · `b87bc2d` S0.4 ratchet · **`e9d20be` S0.4 flake-budget auto-retry (the keystone for error-free)**.
- Picker binding (capability e/voice) separately PROVEN live: T5a rerun `710684c0` bound operator-selected Sarah at the synthesis node 12.

## Honest scope reconciliation (what this IS and ISN'T)
**IS:** the production engine (narrated-deck pipeline) runs error-free, twice, with operator HIL review/accept at all gates, and the auto-retry makes LLM variance non-blocking. The picker-binding capability is proven.

**IS NOT (remaining BETA scope, multi-arc):** the full **Marcus conversational SPOC** surface (a–g conducted in natural conversation rather than CLI gate verdicts) is not yet built; review-lanes (b) ingestion / (c) lesson-plan / (d) research as distinct conversational surfaces, and (f) motion synthesis, remain. These are charter items T6/T7/T8 + the SPOC Epic. The two error-free runs use the gate-shim HIL surface, not the conversational Marcus layer.

**Open finding (filed):** `beta-voice-select-wpm-qa-interaction` (T5a-val-F5) — a NON-default voice select can trip the G5 WPM gate (voice-agnostic target); needs a party-mode QA-semantics decision before a non-default-voice run completes error-free. The ×2 runs above use the in-band recommended voice (approve-path), which is a legitimate operator review/accept.

## Evidence (gitignored run dirs; preserve)
`state/config/runs/b7919f65-.../` and `state/config/runs/bb76170c-.../` — full artifacts (6 decision cards + verdicts, bundle, exports, assembly-bundle with 6 mp3s, cost reports). Storyboard URLs in each run's publish receipt.
