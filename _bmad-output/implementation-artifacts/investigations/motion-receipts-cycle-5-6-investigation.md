# Investigation: Motion receipts absent from certified production runs (cycles 5-6)

## Hand-off Brief

1. **What happened.** The motion leg (node 07E, kira) executed in BOTH certified runs but received zero motion-plan inputs (`input keys: cache_prefix` — the ungrounded-prompt starvation signature) and `_load_motion_plan`'s empty-default branch (`app/specialists/kira/_act.py:77`) converted that starvation into an empty slide list, so the Kling loop iterated zero times and returned `motion_receipts: []` with trail tag `kling.dispatch.ok` and `provenance: real` — Confirmed at every link.
2. **Where the case stands.** Concluded, High confidence. Root cause is a two-layer defect: (i) **no producer** — nothing in the pipeline manifest produces a motion plan or projects one into 07E (its sole dependency `upstream_output: quinn_r` delivers a QA verdict, not a plan); (ii) **silent default** — kira treats absent inputs as a mode switch instead of a contract violation, the exact S0-doctrine violation class ("absence of inputs is a contract violation, never a mode switch"). The folded G2F gate (07F, `fold_with: G3`, groundless-allowlisted) and the compositor's pinned tolerance of `motion_receipts: []` make the vacuous result invisible end-to-end.
3. **What's needed next.** No fix in WAVE 0 (engine FROZEN; Trial A is narrated-deck-shaped and needs no motion). Fix is a **motion data-plane arc** (dp-v2-class, own party round) after Trial A — see Recommended Next Steps.

## Case Info

| Field            | Value |
| ---------------- | ----- |
| Ticket           | WAVE-0 roadmap item `roadmap-consensus-2026-06-12` ("motion diagnosis") |
| Date opened      | 2026-06-12 |
| Status           | Concluded |
| System           | trial/4-2026-06-12 @ 6b4c9c4; certified substrate 8b306b1 (cycle-6) |
| Evidence sources | Run dirs `state/config/runs/{036e7ff8…,f8da20ae…}/` (run.json envelope, specialist-summaries, trace-fixture.json), `state/config/pipeline-manifest.yaml`, `app/specialists/kira/_act.py`, PIN-G1 allowlist |

## Problem Statement

Party round 2026-06-12 listed "motion-receipts diagnosis" in Wave 0 and gated "visual-scan VO" on "motion proven" — implying motion is not proven despite two certified runs claiming 20/20 `provenance: real`. Neither certified run dir contains any motion artifact. Why?

## Evidence Inventory

| Source | Status | Notes |
| ------ | ------ | ----- |
| Cycle-6 run dir | Available | Full: run.json (162KB envelope), 22 specialist summaries, trace fixture, decision cards |
| Cycle-5 run dir | Available | kira summary verified identical |
| Pipeline manifest | Available | Motion nodes 07E/07F at `state/config/pipeline-manifest.yaml:479-507` |
| Kira source | Available | `app/specialists/kira/_act.py` |
| Kling provider logs | Missing | Irrelevant — Confirmed the provider was never called (zero loop iterations, cost_usd 0.0) |

## Timeline of Events

| Time | Event | Source | Confidence |
| ---- | ----- | ------ | ---------- |
| 2026-06-12 08:00:27Z | Cycle-5 kira 07E: `input keys: cache_prefix`, emitted `none`, `kling.dispatch.ok` | `state/config/runs/036e7ff8…/specialist-summaries/kira-20260612T080027737378Z.md` | Confirmed |
| 2026-06-12 09:18:32Z | Cycle-6 kira 07E: identical signature | `state/config/runs/f8da20ae…/specialist-summaries/kira-20260612T091832826383Z.md` | Confirmed |
| 2026-06-12 09:18:32Z | 07E contribution: `motion_receipts: []`, `motion_asset_paths: []`, `bundle_path: runs\kira-motion` (dir never created), `cost_usd: 0.0`, `provenance: real` | cycle-6 `run.json` envelope, node 07E | Confirmed |
| 2026-06-12 09:22:43Z | Compositor (node 14) consumed `motion_receipts: []` without complaint | manifest projection `state/config/pipeline-manifest.yaml:718-720`; pinned tolerance `tests/specialists/test_audio_segment_grounding.py::test_compositor_derives_audio_from_invocation` | Confirmed |

## Confirmed Findings

### Finding 1: Node 07E executed in both certified runs
**Evidence:** kira dispatch marker in cycle-6 `trace-fixture.json` (25/10 deterministic-marker tokens, `gpt-5-nano`); 07E contribution present in both envelopes.
**Detail:** Motion was not skipped, folded away, or unreachable — the node ran and contributed.

### Finding 2: 07E was input-starved
**Evidence:** Both kira summaries: `Received — input keys: cache_prefix`. Manifest `state/config/pipeline-manifest.yaml:484-485`: 07E's only delivery is `dependencies: {upstream_output: quinn_r}` — quinn_r's pre-composition QA verdict (07B), which carries no motion plan. No `dependency_projections` exist for 07E; no manifest node produces `motion_plan`, `motion_plan_path`, or kling prompts.
**Detail:** Same starvation fingerprint dp-v1.1 convicted at node 08 (the sepsis confabulation) — but where Irene confabulated, kira silently no-opped.

### Finding 3: The silent mechanism is `_load_motion_plan`'s empty default
**Evidence:** `app/specialists/kira/_act.py:69-77` — no `motion_plan` key, no `motion_plan_path`, falls to `return {"slides": payload.get("slides") or []}`; `_slides_from_plan` accepts `[]`; the per-slide loop (`:167`) iterates zero times; return at `:235-240` is `motion_receipts: []` and `act()` stamps `kling.dispatch.ok` (`:268`).
**Detail:** Zero Kling calls, zero files written (motion_dir mkdir is inside the loop), zero cost — and a "successful" contribution. The S0 sweep killed the *fixture-MP4 fallback* in this file (comment `:198-202`) but left the *empty-plan* silent branch alive.

### Finding 4: Three independent guards each had a blind spot here
**Evidence:** (i) G2F Motion Gate (07F) is `fold_with: G3` (`pipeline-manifest.yaml:501`) — folded gates never pause (same class as the filed voice-HIL fold defect); (ii) 07F is on the PIN-G1 `GROUNDLESS_ALLOWLIST` (`tests/contracts/test_manifest_grounding_contract.py:48`) — the motion gate body audits nothing; (iii) the compositor tolerates `motion_receipts: []` by pinned test.
**Detail:** The vacuous motion leg is invisible to the gate that owns it, the grounding audit, and the consumer.

### Finding 5: `provenance: real` includes the vacuous motion contribution
**Evidence:** 07E contribution `provenance: "real"` in both envelopes.
**Detail:** "Real" means no-fixture-used, which is technically true (nothing was used at all). The 20/20 provenance:real certification claim is accurate for what it measures but does not assert per-node *productivity* — 07E (and gate-body 07F) contributed nothing.

## Deduced Conclusions

### Deduction 1: Certification claims stand for the narrated-deck deliverable; the motion leg is uncertified
**Based on:** Findings 1-5.
**Reasoning:** Cycles 5-6 produced narrated decks (slides + 6 narration segments + assembly bundle); no claimed deliverable depended on motion. But any future run wanting motion would get the same silent no-op today.
**Conclusion:** The party's "visual-scan VO after motion proven" gating is correct — motion is structurally unproven; the motion data plane was never built (dp-v1.1/v1.2 grounded nodes 08/12/13/14 but never 07E).

## Hypothesized Paths

### Hypothesis A: Motion nodes folded/skipped by workflow-template selection
**Status:** Refuted. **Resolution:** 07E executed in both runs (Finding 1).

### Hypothesis B: Kira dispatched but produced empty receipts silently
**Status:** Confirmed (mechanism in Finding 3 — empty-plan default branch, not the fixture gate; the fixture fallback was already dead per S0).

### Hypothesis C: Motion leg structurally unreachable (fold semantics)
**Status:** Refuted for the node / Confirmed for the gate. **Resolution:** 07E runs; the G2F *gate* can never pause (fold_with: G3) and its body is groundless — the oversight surface, not the execution path, is what's unreachable.

### Hypothesis D: Receipts written to wrong/legacy path
**Status:** Refuted. **Resolution:** `runs/kira-motion` does not exist; zero iterations means zero writes anywhere; the contribution merely *names* the legacy default path it would have used (`bundle_path` field) — which is the enrique `DEFAULT_BUNDLE_PATH` sibling, still live in kira.

## Missing Evidence

| Gap | Impact | How to Obtain |
| --- | ------ | ------------- |
| None for the diagnosis | — | Root cause Confirmed end-to-end from disk evidence + source |

## Source Code Trace

| Element | Detail |
| ------- | ------ |
| Error origin | `app/specialists/kira/_act.py:77` (`_load_motion_plan` empty default) → `:167` zero-iteration loop → `:268` `kling.dispatch.ok` |
| Trigger | Node 07E dispatch with no motion-plan keys in the projected payload |
| Condition | No manifest producer/projection for a motion plan + silent empty default + folded groundless gate + tolerant consumer |
| Related files | `state/config/pipeline-manifest.yaml:479-507,718-720`; `app/specialists/kira/kling_dispatch.py` (rostered fixture seam, NOT implicated); `tests/contracts/test_manifest_grounding_contract.py:48` (07F allowlist row) |

## Conclusion

**Confidence: High** (Confirmed root cause; deterministic — reproduces on every run of the current manifest).

The motion leg is a **structurally complete but data-starved limb**: the node runs, the specialist code is capable, but no pipeline producer feeds it, the specialist silently accepts starvation, the gate that should catch the gap is folded + groundless, and the consumer tolerates the empty result. Four-layer silence, end to end. This is the silent-gap family generalized to a whole subgraph — the same doctrine violation the phantom-delta fix just closed at row level.

## Recommended Next Steps

### Fix direction (NOT WAVE 0 — engine frozen; Trial A needs no motion)
A **motion data-plane arc** (dp-v2-class; party design round required), in dependency order:
1. **Producer**: a motion-plan source (CD creative directive and/or Irene briefs → per-slide kling prompts) + `dependency_projections` into 07E (precedent: dp-v1.1 node-08 grounding).
2. **Starvation raise**: `_load_motion_plan` refuses empty (kira's phantom-delta sibling) — REQUIRES kira taxonomy re-base first (`KiraActError` is a bare RuntimeError on the EXCLUSIONS list; a raise today would crash, not error-pause).
3. **Gate**: G2F unfold/grounding rides the Wave-1 fold-semantics fix (same engine surface as voice-HIL).
4. **Hygiene riders at next kira touch**: retire `DEFAULT_BUNDLE_PATH = runs/kira-motion` (enrique-pattern); compositor empty-receipts tolerance becomes workflow-conditional (motion-enabled runs must refuse `[]`).

### Diagnostic
None needed — but Trial A's transcript should record 07E's `motion_receipts: []` as EXPECTED for the narrated-deck workflow, so the baseline doesn't mis-read it as regression.

## Reproduction Plan

Deterministic: any `trial start --preset production` on the current manifest produces a 07E contribution with `motion_receipts: []` and trail `kling.dispatch.ok`. Isolated proof: `generate_motion_from_plan({})` returns `{"motion_receipts": [], ...}` with zero client calls.

## Side Findings

- The kira-summary phrase "input keys: cache_prefix" is a reusable starvation detector — a grep across `specialist-summaries/` finds every starved node in any run (worth folding into PIN-G1 or the trial postmortem checklist).
- `taxonomy re-base` priority confirmed for kira: any future fail-loud motion behavior is blocked on her bare error class.
- Gary's fabricated two-key roster (`app/specialists/gary/_act.py:95`) remains the sibling empty-input pattern in the slides leg (already filed at deferred-work 2026-06-12).
