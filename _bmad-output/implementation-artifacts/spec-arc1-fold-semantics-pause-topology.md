---
title: 'Arc 1 — pause-topology contract pin + fold-semantics gate-engine fix (wake folded HIL gates to pause AFTER their content)'
type: 'feature'
created: '2026-06-18'
status: 'D2-RESOLVED-via-tiebreaker — split into Arc-1a (manifest topology, Tier-2 pack bump, party-ratification pending) + Arc-1b (membership wake)'
baseline_commit: '7156678'
checkpoint_1: 'IN PROGRESS — party green-light reached consensus on D1/D3/D4 + all amendments, but D2 (un-fold-on-wake vs deferred-pause) is at IMPASSE (3 un-fold: Winston/Amelia/John; 1 deferred: Murat, who requested escalation). Party-mode impasse-resolution chain invoked: Dr. Quinn synthesis round. See Spec Change Log.'
context:
  - '{project-root}/_bmad-output/planning-artifacts/trial-4-scope-plan.md'
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md (voice-selection-hil-fold-defect)'
  - '{project-root}/app/manifest/compiler.py'
  - '{project-root}/app/manifest/schema.py'
  - '{project-root}/state/config/pipeline-manifest.yaml'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem (mechanical root cause, traced this session):** Folded HIL gates are structurally unable to pause. `app/manifest/compiler.py::production_gate_ids` (L99-104) returns pause-handler gate codes ONLY for nodes where `fold_with is None and fold_target is None`. A node carrying `fold_with` (e.g. node 11/11B = G4A/G4B voice-pick `fold_with: G4`; the G2B variant-pick fold) is therefore EXCLUDED from `production_gate_ids` → `_active_node_handler` (compiler L202) gives it a specialist/orchestration handler, never a `_production_gate_node` pause handler. So the folded gate NEVER pauses. The only pause is at the surfaced target gate (G4), which sits at a topological point BEFORE the folded gate's content node runs (G4 fires before node-11 renders voice options). Net: the operator cannot pick a voice/variant because at the only pause point the artifact to choose among does not yet exist — "HIL-in-name-only" (`voice-selection-hil-fold-defect`).

**Why it matters now:** This is the trial-4 keystone. The ratified trial-4 plan requires ≥1 genuine variant-pick pause (G2B) + ≥1 genuine voice-pick pause (G4A). Neither is possible until a folded gate can pause AFTER its content node. Arc 2 (the wakes) is strictly gated on this.

**Approach (two coupled pieces, pin-before-fix per Winston):**
1. **Pause-topology contract pin (1a, lands FIRST):** a test/contract artifact that pins, per gate code, WHERE in the compiled walk a pause is contractually legal — specifically that a folded HIL gate's pause point is AFTER its content node, not at the surfaced parent's pre-content position. The fix (1b) must conform to this pin; without it the fix re-derives topology implicitly inside the engine (the churn the freeze guarded against).
2. **Fold-semantics gate-engine fix (1b):** make a folded gate able to present an OPT-IN pause AFTER its content node runs. **Folded auto-resolve stays the DEFAULT** (roadmap: "folded mode stays default; pause opt-in") — a folded gate without an active opt-in behaves exactly as today (no pause, auto-resolve to the recommended pick). When the gate is "woken" (opt-in), the compiled graph routes a pause handler to fire after the content node, with the rendered options available to the DecisionCard.

This is a **gate-engine-cutting** change (the one real engine cut in trial-4). Zero behavior change on the default (folded, not-woken) path — that is the regression guarantee; only the woken path is new.

## OPEN DESIGN DECISIONS — route to party-mode (do NOT pre-decide)

1. **Wake mechanism.** How does an operator opt a folded gate into pausing? Options: (a) per-run CLI flag listing gate codes to wake (`--wake-gates G2B,G4A`); (b) a manifest/preset opt-in; (c) an operator directive field. Author lean: (a) per-run flag — explicit, per-trial, no manifest mutation, no engine default change.
2. **Pause-point placement.** Does the woken folded gate (i) become a real surfaced pause node positioned AFTER its content node (un-fold-on-wake), or (ii) stay folded but the engine defers its pause to fire post-content within the merged gate? Author lean: (i) — simpler, and the pause-topology pin can assert the post-content position directly. Winston/Amelia to rule on compiler complexity.
3. **DecisionCard + resume threading.** The woken pause must surface the rendered options (the A/B storyboard variants; the voice previews) on the DecisionCard, and the resume must thread the operator's pick downstream (variant → which storyboard pack continues; voice → enrique TTS). Confirm the existing `resume_api` + verdict-section envelopes cover variant/voice picks, or what must be added.
4. **Default-path invariance proof.** What is the exact pin proving the folded-not-woken path is byte-identical to today (the regression guarantee)?

## Boundaries & Constraints
**Always:** folded auto-resolve stays the default; the woken path is purely additive. Pin precedes fix (1a before 1b). Conform to the pause-topology contract. Preserve the recoverable error-pause family. Golden-replay test of every gate's fold/pause decision in both states (Murat MUST-FIX before trial).
**Ask First (party):** the 4 design decisions. Any change to the surfaced-gate set or the manifest fold declarations. Any resume_api / verdict-envelope schema change.
**Never:** no change to the default folded behavior; no second control plane; do not wake gates by default; do not let a woken gate pause at the pre-content position (the very bug).

## Code Map (investigation findings)
- `app/manifest/compiler.py:99-104` — `production_gate_ids`: EXCLUDES `fold_with`/`fold_target` nodes → folded gates get no pause handler. **Primary fix surface.**
- `app/manifest/compiler.py:167-203` — `_production_gate_node` + `_active_node_handler` (gate-vs-specialist handler selection by `production_gate_ids` membership).
- `app/manifest/schema.py:136-201` — `fold_with`/`fold_target` NodeSpec fields + mutual-exclusion validator (fold is modeled; runtime/compile consumption is the gap).
- `app/marcus/orchestrator/production_runner.py` — gate-node branch (`node_kind == "gate"` → `_pause_at_gate`); NOTE: zero `fold` references — runtime pauses purely on `production_gate_ids` membership + `pause_at_gates`/`active_gate_ids`. The wake must flow into which nodes get gate handlers / are active.
- `state/config/pipeline-manifest.yaml` — node 11/11B (G4A/G4B `fold_with: G4`), the G2B variant fold, G0 `fold_with: G1`.
- `app/gates/resume_api.py` — DecisionCard register/digest/resume (decision 3).
- existing fold tests: `tests/unit/manifest/test_node_spec_fold_fields.py`, `test_manifest_fold_with_declarations.py`, `test_gate_topology_cli.py`, `test_gate_fold_manifest_emit.py` (fold is modeled + emit-tested; the pause-topology runtime contract is the new pin).

## Tasks & Acceptance (provisional — finalize after party resolves the 4 decisions)
- [ ] **1a pause-topology contract pin** — per-gate-code legal pause position; asserts a woken folded gate pauses AFTER its content node; folded-not-woken asserts no pause. (lands first)
- [ ] **1b fold-semantics fix** — wake mechanism (decision 1) routes a pause handler post-content for woken folded gates (decision 2); default path untouched.
- [ ] DecisionCard surfaces rendered options + resume threads the pick (decision 3).
- [ ] Golden-replay pin: every gate's fold/pause decision matches the contract table in BOTH folded-default and woken states (Murat).
- [ ] Default-path byte-identical pin (decision 4).
- [ ] Governance: pipeline-manifest-regime check (compiler is a block_mode_trigger_path — read `docs/dev-guide/pipeline-manifest-regime.md` at T1; likely Tier-2 pack/topology consideration → party consensus already in progress via this spec); lockstep + lint-imports + ruff.

**Acceptance Criteria (provisional):**
- Given a folded gate NOT woken, the compiled graph + walk are byte-identical to today (auto-resolve, no pause).
- Given a folded gate WOKEN, the walk pauses AFTER its content node with the rendered options on the DecisionCard; resume threads the pick downstream.
- The pause-topology pin fails if a woken gate's pause lands at the pre-content position (the bug).
- Full battery green (manifest unit + marcus integration + lockstep + lint-imports + ruff), no new failures vs the ambient roster.

## Spec Change Log
**2026-06-18 — party green-light + D2 impasse + Quinn synthesis REFUTED by verification → John PM tiebreaker.**
- Consensus on D1 (CLI `--wake-gates` as a COMPILER input, not runtime — Winston firewall), D3 (scope-moved to Arc 2: Arc 1 round-trips an opaque token on a sentinel gate; real pick-threading + envelope spike = Arc 2), D4 (compile-time golden on `production_gate_ids(woken=∅)` == today + Winston membership lint + provenance stamp + config-plane/no-pack-bump).
- **D2 IMPASSE:** 3 (Winston/Amelia/John) = un-fold-on-wake; 1 (Murat) = deferred-pause (drift-proof one-edge delta); Murat requested escalation.
- **Dr. Quinn synthesis ("membership-only wake": add gate_code to `production_gate_ids`, activate the gate's intrinsic post-content scaffold gate_decision) — predicted 4-of-4 CONTINGENT on a code fact.**
- **VERIFICATION REFUTES the synthesis (orchestrator, code-read):** the folded HIL gate-codes are CO-LOCATED on content-producing specialist nodes (node-11/11B `elevenlabs` carry G4A/G4B; node-07B `quinn-r` carries G2B); `compiler._production_gate_node` is a content-free no-op that SUPPRESSES the specialist (runtime pauses, never dispatches). So membership-only wake → content-free PRE-content pause = the original bug. No separate post-content gate node exists for these codes; the gate IS the content node. Surfaced gates today (G1/G2C/G3/G4) are content-free pause nodes positioned AFTER prior content-producing nodes.
- **Implication:** a post-content voice/variant pause requires EITHER (i) manifest topology split (a separate folded post-content gate node after the content specialist — likely pack-plane) — possibly enabling Quinn's membership-only wake afterward (candidate "synthesis-2"); OR (ii) runtime honoring a post-content pause for the co-located node (Winston-blocked as second control plane). Neither is "free"; Murat's drift concern about (i) stands.
- **CHAIN STEP 2 — John (PM) tiebreaker, FINAL + BINDING (2026-06-18):** path **(i) manifest topology split → membership-only wake**; (ii) deferred-pause REJECTED (Winston firewall upheld). Arc 1 splits: **Arc 1a** — restructure each co-located voice/variant gate into [content specialist, gate_code REMOVED] → [separate content-free gate node carrying the gate_code, FOLDED/no-op by default]; **Tier-2 pack-version bump**, party-ratified BEFORE dev; folded behavior byte-identical to today. **Arc 1b** — wake = membership inclusion of the separate gate node's gate_code (Quinn's wake, now valid). **1a ships + folded-verified BEFORE 1b.** Murat pin = 3 lockstep-wired invariants: (1) gate_code only on content-free nodes immediately preceded by their content specialist (no gate_code on content-producing nodes); (2) folded-equivalence no-op (byte-identical folded trace); (3) single-control-plane (only `production_gate_ids` membership converts folded→pause; no runtime pause-branch — Winston firewall as a test). **Arc-1 ship def revised:** 1a merged+pack-ratified+folded-equivalent run, AND 1b merged + woken run renders content THEN pauses post-content for G4A/G4B + G2B. Next: party-mode RATIFY the Tier-2 pack bump (not relitigate i/ii) → author Arc-1a spec → NEW-CYCLE Codex hand-off.

## Verification
- `.\.venv\Scripts\python.exe -m pytest tests/unit/manifest/ tests/integration/marcus/ -q`
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py`
- `.\.venv\Scripts\lint-imports.exe` · `.\.venv\Scripts\ruff.exe check <touched>`
