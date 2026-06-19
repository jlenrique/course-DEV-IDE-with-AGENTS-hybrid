# T5a Trial — Voice-Picker Binding Validation (Run Log)

**Trial ID:** `630e4225-1555-4075-8345-0f2930fa7d3b`
**Purpose (charter T5a):** validate the BETA `select` voice-picker binding END-TO-END on the live path — operator `select`s a NON-default voice at G4A → assert the post-G4A narration synthesis emits THAT voice (the one part S0.3+T5b unit tests can't prove: operator→Enrique→synthesis wiring).
**Corpus:** `course-content/courses/tejal-apc-c1-m1-p2-trends` (frozen BETA corpus). **Preset:** production. **Operator:** operator_juan.
**Substrate under test:** S0.1 crash-taxonomy + S0.2 ingestion-report + S0.3 card candidates + T5b `select` verb + S0.4 ratchet (commits 5c9cbea..b87bc2d).
**Error-free criterion (BETA §2):** zero Class-A (substrate) events; Class-B (API variance) within flake budget (≤1 auto-retry/node, ≤3/run); operator-manual recover = the EXPECTED HIL action here (not a failure — this is a HIL trial).

## Hypotheses being tested
1. The S0.x fixes reduce the Trial-4 cascade (G1 no longer false-rejects; no 07B crash).
2. A `select` verdict at G4A with a non-default `selected_voice_id` binds, and the synthesis emits that voice.

## Gate ledger
### G0 — directive: auto-confirmed (Claude-as-operator)
### G1 — APPROVED (decision softened reject→revise vs Trial-4)
- card_id `a6134eb8…` digest `d505a194…`. Drafted decision **`revise`** (Trial-4 was `reject`/halt-for-repair) — S0.2 partial effect: signals now include `local_bundle_reference_only`. Bundle real (6 artifacts on disk). Approved (content present).
- **🟡 FINDING T5a-F1 (S0.2 timing bug):** Texas summary STILL "Emitted artifacts: none". Root cause: the summary is emitted MID-NODE (before the runner appends the texas contribution to `production_envelope`), so `_artifacts_from_contribution` finds no contribution at emit time. S0.2 fix targets the right function but runs at the wrong time. Proper fix: read the bundle `manifest.json` at gate-build time, OR emit the summary AFTER the contribution lands, OR have the pre-gate slot_values read the manifest directly. NOT a blocker (G1 approvable; decision already softened). Follow-up after T5a.

### G2B — APPROVED (S0.3 LIVE-VALIDATED ✅)
- card_id `ec0154c8…` digest `d7f6a353…`. **`variant_candidates: ['A']` POPULATED** + `pick_context` carries the `variant-options` structured entry. S0.3 candidate-population confirmed on the live path. Single-dispatch → 1 variant → approve (meaningful select is the 3-voice G4A pick). **NO CRASH, NO FIX NEEDED G1→G2B** — the Trial-4 cascade (Gamma brief-unmatched + 07B ModeMismatch) is GONE (prior-session fixes + S0.1 held).
### G2B — variant (will `select` to exercise the variant path, or approve)
### G2C — APPROVED (ready, no blockers; Storyboard A published). card_id `a9c1a1c6…`.

### ⛔→↻ irene pass-2 `slide-join-failed` (node 08) — RECOVER #1
- **🟠 FINDING T5a-F2 (PROMOTE from watch):** `irene.pass2.slide-join-failed` recurred — **2-for-2 first-roll across Trial-4 (T4-F5) + T5a.** No longer "watch-only variance"; it's a reliable first-roll miss. For BETA "error-free twice" this MUST be absorbed by the S0.4 flake-budget auto-retry (≤1/node) OR hardened in the pass-2 prompt/schema. Promote → active follow-on `beta-irene-pass2-perception-source-autoretry-or-harden`.
- **Action:** `trial recover` (re-roll node 08); Trial-4 cleared on one re-roll.
### G3 — motion approve
### G4 — fidelity approve
### G3 — motion approve (focus motion_clip_approval). card_id `585131b5…`.
### G4 — fidelity approve. card_id `574ecb57…`.

### 🎯 G4A — voice `select` (THE T5a VALIDATION)
- **S0.3/T4-F6 LIVE-VALIDATED:** `voice_candidates: [Roger CwhRBWX…, Sarah EXAVITQu…, Laura FGY2WhT…]` POPULATED on the card (Trial-4 had `[]`). card_id `28c08cfa…` digest `08c71d69…`.
- **Submitting the first-ever live `select` verdict:** choose NON-default **Sarah (EXAVITQu4vr4xnSDxMaL)** (default/recommended = Roger). `verb=select`, `edit_payload={selected_voice_id: EXAVITQu4vr4xnSDxMaL}`.
- **Validation target:** after completion, the synthesized narration / voice_selection must use Sarah, NOT Roger.
### 🏁 T5a COMPLETE — status `completed`; 6 segments synthesized; BUT voice did NOT bind
- **Run quality:** G0→completion CLEAN — only 1 irene re-roll (T5a-F2), ZERO crashes, ZERO substrate fixes mid-run. The Trial-4 cascade (Gamma brief-unmatched, 07B ModeMismatch) is GONE. S0.1/S0.2(partial)/S0.3 all validated live. Cost ~$1.08 narration + upstream.
- **🔴 FINDING T5a-F3 (THE re-route gap — precisely located):** the `select` MERGE WORKED (Sarah `EXAVITQu…` is in checkpoint/cache_prefix/run.json/resume-command) but the synthesis used **Roger (default)**, operator_id `operator-defaulted-recommended`, on nodes 11/11B/12. Root cause: the select-merge lands in `run_state.cache_state.cache_prefix`, but the **per-node post-G4A enrique dispatch does NOT source voice_selection from it** — node 12's `dependency_projections` are only narration_script/segment_manifest_deltas, and `build_voice_selection_contract` (enrique `_act.py:162-186`) re-defaults to `preview.recommended_voice_id` because the operator selection never reaches its `payload`. The merge is ORPHANED. Exactly the "merge necessary but not sufficient" gap Murat predicted at T5b.
- **Fix locus (next iteration — "repair" then "rerun"):** thread the operator-selected voice from `run_state.cache_state.cache_prefix.voice_selection.selected_voice_id` into the post-G4A elevenlabs dispatch payload — either (a) a `runner_supplied_payload` elevenlabs branch in `_dispatch_specialist_at_node`/`_runner_payload_for_specialist` carrying the selected voice, or (b) enrique reads the operator selection from a durable per-trial location the dispatch preserves. Then RE-RUN T5a to re-validate live (synthesis emits Sarah). Filed `beta-t5a-voice-select-consumption-not-wired`.
- **What T5a PROVED (high value):** the picker DATA path is complete end-to-end (candidates surfaced live, select verb accepted, merge correct, run completes); the only remaining gap is the synthesis CONSUMPTION of the merged selection — now precisely located by the live trial (the exact thing unit tests couldn't catch).

## Findings (live)
_log as observed_
