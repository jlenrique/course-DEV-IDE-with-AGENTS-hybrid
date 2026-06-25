# Spec — Story 1.3 (reframed): clustering control + cluster-label carry + transition timing

**Status:** ready-for-dev (pending operator confirm on the reframe)
**Class:** S (substrate) · **Authority:** `forward-development-sequence-2026-06-24.md` §Phase-1 1d; live evidence from trial `c2c6dcbf` (terminal-(b) clustered A/B run).

## Why reframe

The original 1.3 ("three small adds: chunk directive, keep-dense marker, transition timing") was scoped when clustering was dormant. The live run changed the picture — **the LLM chunked dense slides AND kept synthesis slides dense organically**, with no explicit markers, and delivered cleanly to Descript. So the three adds are no longer "make clustering work." Re-graded against the live manifest:

| Original add | Live evidence | New status |
|---|---|---|
| (a) per-slide chunk directive | LLM chunked 3 dense slides unaided | **Control guardrail** (force/suppress per slide). Low priority — cheap insurance vs n=1 variance. |
| (b) keep-dense marker | LLM kept 3 gestalt slides as singletons unaided | **Control guardrail** (pin a slide dense). Low priority — same. |
| (c) inter-sub-slide transition timing | manifest has only `timing_role`; no `cluster_gap`/`transition_buffer`/`onset_delay`/`dwell` | **Polish** — absent, but Underlord timed slides from audio duration, so non-blocking. |
| **NEW — cluster-label carry** | delivered manifest carries `bridge_type` but NOT `cluster_id`/`cluster_role`/`cluster_position`/`narrative_arc` | **Raise priority** — without cluster labels in the delivered artifact you cannot *verify* cluster structure in what shipped. |

## Proposed scope (three sub-stories, re-prioritized)

### 1.3-carry (DO FIRST — most valuable)
Carry the cluster LABELS into the final segment manifest. Today count + narration propagate (6→13 segments) but `cluster_id`/`cluster_role`/`cluster_position`/`narrative_arc` drop somewhere between Pass-1 plan_units (which carry them, per Story 1.1) and the exported `segment-manifest-storyboard-*.yaml`. 
- **AC:** the delivered segment manifest's segments carry `cluster_id`/`cluster_role`/`cluster_position`/`narrative_arc` for clustered slides (degenerate/None for singletons), traceable to the Pass-1 emission.
- **Verify:** re-export a clustered run; assert ≥1 head + ≥1 interstitial carry the labels (witness, not unit suite).
- **Trace task:** find the drop point (Gary slide-row build → Pass-2 → storyboard export); the schema already supports the fields (survival probe proved it).

### 1.3-control (LOW priority — cheap guardrail)
- Per-slide **chunk directive** via `special_treatment_directives` (`force_chunk` / `suppress_chunk` / `interstitial_count`).
- **keep-dense pin** so a named gestalt slide can never be chunked (consumed in Pass-1's cluster-decision; never a chunk candidate — amendment #5 carried).
- **AC:** a directive on a slide deterministically overrides the LLM's organic decision; pinned slide stays singleton across N runs.

### 1.3-timing (DEFER — polish)
- Emit `cluster_gap` / `transition_buffer` (within-cluster pacing) on the segment manifest.
- **Non-blocking:** audio-duration timing covers delivery today; revisit when within-cluster pacing control is wanted.

## Governance / fences
Additive. Don't regress the organic chunk/keep-dense behavior. No G5/reading-path/figure-gate touch. `narration_join` untouched. NEW CYCLE per substrate story; the carry fix likely touches the Pass-2 → storyboard-export path (verify no block-mode trigger).

## Open question for operator
Confirm the reframe (carry-first, control-low, timing-deferred) vs. the original equal-weight three-add framing. Default if no objection: build **1.3-carry** first as its own NEW CYCLE; file 1.3-control + 1.3-timing to deferred-inventory.
