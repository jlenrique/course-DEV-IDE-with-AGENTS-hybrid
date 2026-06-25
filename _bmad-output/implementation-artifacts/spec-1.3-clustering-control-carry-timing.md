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

## Party-mode GREEN-LIGHT (2026-06-24) — 4/4 GREEN, no impasse
John / Winston / Murat / Mary all GREEN on the carry-first reframe. Binding amendments folded:
- **A1 (John):** build **1.3-carry as its own NEW CYCLE**; 1.3-control + 1.3-timing → deferred-inventory with reactivation triggers (NOT bundled).
- **A2 (Murat):** witness must assert **all four cluster fields (`cluster_id`/`cluster_role`/`cluster_position`/`narrative_arc`) non-degenerate on the head AND the interstitial**, AND singletons carry the **declared degenerate/None sentinel** (not silently absent) — full-field + negative case, traced to the Pass-1 emission. ("≥1 head + ≥1 interstitial" was too weak — a partial drop passes vacuously.)
- **A3 (Winston):** fix at the **single discovered drop point in the Pass-2 → storyboard-export projection** (likely Gary's slide-row build dropping fields on segment expansion) — widen the projection to copy the four labels through, **NOT** re-derive clusters at export. The trace-task MUST produce the exact file/line **+ a block-mode-trigger check BEFORE any edit**.
- **A4 (Mary):** 1.3-control is the **fallback if organic chunk/keep-dense proves unstable across the next 2–3 trials** — file it with that trigger; "low priority" must not become "dropped."

**Status: 1.3-carry ready-for-dev (own NEW CYCLE). 1.3-control + 1.3-timing → deferred-inventory.**

## Trace-task result (2026-06-24, pre-edit per Winston A3)
The drop is **two points**, both confirmed on the real `c2c6dcbf` checkpoint (block-mode check: `storyboard_publisher.py` + `narration_join.py` are NOT in `block_mode_trigger_paths` — safe):
1. **`cluster_id`/`cluster_role`/`cluster_position`** ARE present on the Pass-2 `segment_manifest_deltas` (e.g. `c-u01`/`head`/`establish`), but `join_narration_segments` (the party-governed neck) builds an output row that **omits them**. → Fix in the EXPORT projection `app/marcus/orchestrator/storyboard_publisher.py::_write_segment_manifest_for_b`: after the join, re-attach the three fields from the matching delta (by segment `id`). **Do NOT widen `narration_join` (governed).**
2. **`narrative_arc`** is non-null on the **Pass-1 plan_units** (`output.lesson_plan.plan_units[*].narrative_arc`, keyed by `cluster_id`) but **absent from the Pass-2 deltas**. → In the caller `publish_storyboard_for_gate` (storyboard-B branch, which has `production_envelope`), build a `cluster_id → narrative_arc` map from the irene_pass1 plan_units and pass it into `_write_segment_manifest_for_b`; set each segment's `narrative_arc` from the map by `cluster_id`. **Deterministic lookup, not re-derive.**
Singletons: degenerate cluster (cluster_id=`c-<unit>`, role=head, position=establish, narrative_arc may be its own) — carry the declared values, never silently absent (Murat A2).
