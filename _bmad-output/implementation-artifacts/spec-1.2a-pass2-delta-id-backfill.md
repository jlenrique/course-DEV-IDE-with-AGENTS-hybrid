# Spec — Story 1.2a: Pass-2 delta-id backfill for clustered decks

**Status:** ready-for-dev
**Class:** S (substrate) · single-gate · r_tier R2 · t11_tier standard
**Parent:** Story 1.2 downstream re-verification surfaced this on the FIRST live clustered run (trial `52890be7`).
**Authority:** `forward-development-sequence-2026-06-24.md` §Phase-1 1c ("RE-VERIFY downstream … re-scope if it needs repair"); live diagnosis below.

## Live diagnosis (trial 52890be7, 2026-06-24)

The first live clustered production run drove G1→G2B→G2C→G3→G4→G4A and **published a 13-slide clustered Storyboard-B**, but **error-paused at the enrique/ElevenLabs audio leg (node 12)** with `elevenlabs.join.dropped-segments` — all 13 segments dropped, pre-spend guard correctly refused.

Root cause (isolated from the checkpoint run_state):
- Pass-2 emitted **parallel arrays of equal length (13 each)**: `narration_script` with well-formed ids `seg-01…seg-13`, and `segment_manifest_deltas` with **all `id` == None**.
- The party-governed shared join `app/specialists/narration_join.py::join_narration_segments` matches narration↔delta **by `id`**. Id-less deltas → `segment_id == ""` → no narration text joins → enrique's `dropped` set = all 13 → `elevenlabs.join.dropped-segments`.
- The simpler 6-flat-slide mirror runs (`7d530d0a`/`6cb8eafd`) did NOT trigger this: the Pass-2 LLM included delta ids on the smaller output. The **clustered 13-sub-slide deck's larger/more-complex Pass-2 output** is where the LLM dropped the delta `id` field — an LLM-variance failure exacerbated by cluster expansion.

This is NOT clustering-specific in principle (any deck where the LLM omits delta ids would break), but clustering is what surfaced it.

## Fix (contained; party-governed join policy UNTOUCHED)

Add a deterministic **id-backfill normalization at the Pass-2 output boundary** (in `app/specialists/irene/graph.py`, immediately after `_parse_pass_2_response`, BEFORE the `_assert_*` checks and before the join is ever consumed by publisher/enrique/G5):

- New pure function `backfill_delta_ids(parsed: dict) -> dict` (no I/O, no raise):
  - Let `narr = parsed["narration_script"]`, `deltas = parsed["segment_manifest_deltas"]` (both lists).
  - For each delta lacking a non-empty `id`/`segment_id`: **only when `len(deltas) == len(narr)`**, assign the delta's `id` from `narr[index].id` (positional alignment of the parallel arrays). If lengths differ, leave untouched (the existing asserts/guards still fire — do NOT fabricate a mis-pairing).
  - Pure (copy, no mutation of input), idempotent.
- Call it in the Pass-2 act path right after parse.

**Why at the Pass-2 boundary, not in `narration_join.py`:** the join module is the single party-governed home of the join POLICY (2026-06-12 Winston Q1 consensus, import-identity-pinned across publisher/enrique/G5). Backfilling missing ids is a DATA-completeness fix at the source, not a policy change — keeps all three consumers consistent automatically and avoids reopening the join-policy contract. Mirrors the Story 1.1 `normalize_clusters` backstop pattern.

## Acceptance criteria (RED-first)
- **AC-1:** `backfill_delta_ids` — deltas with all-None ids + `len(deltas)==len(narration)` get ids from narration by index (seg-01…seg-N); existing non-empty delta ids are preserved unchanged.
- **AC-2:** length-mismatch (deltas≠narration) → deltas left untouched (no fabricated pairing).
- **AC-3:** pure (no input mutation) + idempotent.
- **AC-4:** end-to-end — a parsed Pass-2 output with id-less deltas, after backfill, joins via `join_narration_segments` with ZERO dropped segments (reuse the trial-`52890be7` shape: 13 narration ids + 13 id-less deltas with perception_source set).
- **AC-5 (non-regression):** the existing 6-flat-slide path (deltas already have ids) is byte-unchanged; `narration_join.py` UNTOUCHED; G5 figure detector UNTOUCHED; irene graph + enrique + quinn_r suites stay green.
- **AC-6 (live recover):** `trial recover` on the paused trial `52890be7` from node 12 re-runs enrique with the fix → audio leg proceeds (no `elevenlabs.join.dropped-segments`). [operator-gated live leg / Claude may run it]

## Fences
Additive only. `narration_join.py` (party-governed) UNTOUCHED. G5 quinn_r figure detector UNTOUCHED. No block-mode/manifest/pack path. No `--no-verify`, no force-push.

## T11 outcome (2026-06-24)
Green-light: Winston + Murat GREEN-WITH-AMENDMENTS (no impasse) — amendments folded (all-None-only backfill; length-mismatch leaves guard to fire; positional-invariant pinned; real-shape AC-4; phantom still caught). Implemented RED-first (Claude-direct, proportional to a ~15-line pure backstop). T11 adversarial Edge-Case review: **SOLID — no BLOCKER/MAJOR**; pre-spend guard NOT weakened, `narration_join.py` + G5 UNTOUCHED. Two MINOR residuals: (1) all-falsy-vs-all-None gate → **FIXED** (gate now keys on `id is not None`, +2 tests); (2) **DEFERRED** `pass2-delta-backfill-duplicate-narration-id` — if Pass-2 ever emits duplicate narration ids, backfill makes them join (vs drop) and the id-keyed join could cross text; pre-existing join-domain risk, not introduced here; party-governed `narration_join` territory. Battery: 11 backfill tests + 178 irene/enrique/quinn_r (1 ambient xfail) + ruff + lint-imports 15/0.

## Verify-cheaply note
The fix lives in Pass-2 OUTPUT handling, which the checkpointed run_state already holds (id-less deltas). `trial recover` from the error-paused node 12 re-runs only the audio leg against the fixed join input — no Gamma re-render, no Pass-2 re-run. Fast, real-artifact verification.
