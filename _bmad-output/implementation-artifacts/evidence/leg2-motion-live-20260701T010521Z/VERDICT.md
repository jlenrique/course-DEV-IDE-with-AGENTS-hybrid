# Leg-2 Motion-Isolation LIVE REPROVE — Independent Validation Verdict

- **Timestamp (UTC):** 2026-07-01T01:05:21Z
- **Driver:** `scratchpad/leg2_motion_reprove_driver.py --live` (run twice, strictly sequential)
- **Golden run (never touched):** `state/config/runs/8d819b8d-01dd-4ed5-a07d-12c31d764d9b` (run.json mtime 2026-06-30 06:36:28, pre-dates both runs → untouched)
- **Protocol:** FIRST-RUN-STANDS honored. No infra re-runs needed (both first renders succeeded). No mocks — real Kling API. No commit / no push / no source edit.
- **Setup disclosure (scope of what this proves):** each live render was a REWIND-RECOVER of golden run `8d819b8d` with a B2 `kling-v1-6` text2video motion slide INJECTED into the copied run's 07D.5 `motion_planner` contribution — so this evidence proves continuation-walk kira (07E) dispatch + per-run isolation + real mp4 download + two-run coexistence, but it does NOT prove that 07D.5 independently authored a motion-worthy plan on a live full walk (that is a separate concern, filed as a follow-on).

## ENV (masked)
OPENAI_API_KEY present (len=164, sk-pro…oc0A); KLING_ACCESS_KEY present (len=32, APAhNe…FBhn); KLING_SECRET_KEY present (len=32, TbpRhN…4pyE); KLING_API_TOKEN present (len=57, api-ke…U9Sw).

## Global-dir before/after snapshot — `runs/kira-motion/motion/`
- **Before (pre-run):** 2 mp4 — slide-01.mp4 (md5 4aaba316b8e89e6d8a9337dfa9a0fc59), slide-02.mp4 (md5 dce943f229aa06a78b2dbec4f548cfa7)
- **After BOTH trials:** 2 mp4 — identical md5s. **NO new mp4 written to global dir.** ✅

## TRIAL_A — trial_id `10621848-c057-424c-96eb-3e414381e0dc`
- mp4: `state/config/runs/10621848-…/motion/b2-title-motion.mp4` — **1,270,099 bytes**
- box sigs: ftyp ✅ moov ✅ mdat ✅ (hexdump: `0000 0020 6674 7970 6973 6f6d` = `ftypisom`)
- receipt: status=**success**, actual_cost_usd=**0.28**, request_id `e995f677-01f6-4cf0-ae39-7ffd50b2a144`, task_id `901099753319694374`, task_status `succeed`, final_unit_deduction `2`
- run.json: rewritten by continuation walk; references motion_asset_path + motion_receipts + b2-title-motion.mp4 ✅
- walk end-status: `paused-at-error` at **downstream node 09 (storyboard_publisher)** — reason `[storyboard.input.missing-irene]` (golden fixture has no irene Pass-2). NOT a motion-node error.

## TRIAL_B — trial_id `839b8727-ba95-4069-8fa6-6679d3079980`
- mp4: `state/config/runs/839b8727-…/motion/b2-title-motion.mp4` — **1,532,485 bytes**
- box sigs: ftyp ✅ moov ✅ mdat ✅
- receipt: status=**success**, actual_cost_usd=**0.28**, request_id `d517670b-7670-4019-a206-462addf75077`, task_id `901100788255162463`
- run.json: rewritten by continuation walk; references motion asset ✅
- walk end-status: `paused-at-error` at downstream node 09 (same storyboard/irene-Pass-2 fixture precondition).

## Coexistence
- A mp4 md5 `59494077eae4716fdd784d866921553c`; B mp4 md5 `fccab41e2a3079704189c216ae06fb71` — **distinct files, distinct run-scoped dirs, neither overwritten.** ✅

## Per-AC verdict
| AC | Criterion | Verdict |
|----|-----------|---------|
| AC#1 | mp4 under `state/config/runs/<TRIAL>/motion/`, NOT global; global gained no new mp4 | **PASS** (both trials; global unchanged) |
| AC#2 | run.json (re)written by continuation walk + references motion asset | **PASS** (both). CAVEAT: terminal walk-status is `paused-at-error`, but at DOWNSTREAM node 09 storyboard_publisher (missing irene Pass-2 — a golden-fixture precondition), NOT at the motion node. The motion node itself completed cleanly and its contribution persisted. |
| AC#3 | real mp4 bytes — ftyp + moov/mdat, >100KB | **PASS** (A 1.27 MB, B 1.53 MB; all box sigs present) |
| AC#3b | receipt status=success + actual_cost_usd>0 (real paid call, not 0-credit floor) | **PASS** (both $0.28, real Kling task_ids + request_ids, task_status succeed) |
| AC#4 | both mp4s exist, distinct files in distinct dirs, neither overwritten | **PASS** |

## OVERALL VERDICT: **PASS**
The Leg-2 motion-isolation fix is proven LIVE: kira's paid text2video render routes its receipt + downloaded mp4 to the per-run dir `state/config/runs/<trial_id>/motion/` on a recover/continuation walk, the global `runs/kira-motion/motion/` is never written, two independent trials coexist without collision, and each fired a genuine paid Kling call ($0.28 each, real task/request ids). The `paused-at-error` terminal status is a downstream storyboard/irene-Pass-2 fixture precondition, orthogonal to (and not a regression of) the motion isolation being validated.

**Total live spend: $0.56** (2 × $0.28).
