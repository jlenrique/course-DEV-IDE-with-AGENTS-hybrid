# Leg-2 — MOTION on the real substrate (B2/B3 + live Kling)

**Arc:** Concierge Production Substrate (branch `dev/concierge-production-substrate-2026-06-29`).
**Class:** S. **Status:** **done** (party GREEN-LIGHT 5/5 2026-06-30 → CLOSE 4/4 2026-07-01 [Murat/Winston/John/Kira]; 3-lane bmad-code-review 0 MUST-FIX + 4 SHOULD-FIX applied; live-proven $0.56; committed `4e3b77a5`, pushed). Follow-ons: `leg2-07d5-live-motion-authoring-full-walk`, `leg2-global-kira-motion-dir-retirement` (deferred-inventory).
**Gate mode:** single-gate structural (Murat) — this is runner payload-wiring + a pinning assertion + one live acceptance render; no authored content, so no content-fidelity gate. VO↔on-screen invariant untouched.

## Why (product value / guardrail)

On the real in-graph run path, kira (07E) writes `{slide_id}.mp4` to a **global** dir `REPO_ROOT/runs/kira-motion/motion/` because the runner only threads a run-scoped `bundle_path` when the `KIRA_MOTION_PLAN_PATH` seed env is set (`production_runner.py:1465-1472`). Two real SPOC runs whose motion nodes fire **cross-contaminate** each other's receipts + MP4s. This is a genuine data-integrity defect in the shipping SPOC runtime, independent of any proofing run — it earns its place per the design guardrail. The live render is the acceptance proof the fix works end-to-end, not the reason for it.

## Scout ground truth (SOLID)

- Two-walk architecture clean: START walk (`run_production_trial` :2027) pauses at G1 (node 04); CONTINUATION walk (`_continue_production_walk` :2763 via resume/recover) owns all post-G1 gates + motion nodes 07D.5/07E. Specialist dispatch is a **single shared site** `_dispatch_specialist_at_node` (:1807) → kira invocation is already walk-invariant.
- Motion nodes ordered 07C(G2C)→07D(G2M)→07D.5 `motion_planner` AUTO (deterministic, NO LLM, 0-credit motion floor :441-491)→07E `kira` AUTO (real Kling)→07F(G2F)→07G. Post-G1 → continuation walk only.
- Compose selection real + frozen-then-rehydrated (no re-default trap): `component_selection.py motion:bool`, `production_default deck+motion=True`; `composition.py:120-125` motion fragment binds `{07D,07D.5,07E,07F}`, included iff `selection.motion`. B2=deck+motion, B3=+workbook.
- Kling+kira proven live via a HAND harness (`runs/kira-motion-b2/` B2-PROOF: 3 real MP4s across kling-v1-6/v2-1-master/v2-master) — but NOT through the runner. **This harness is INVALID for a Leg-2 envelope proof** (Kira). Reuse only its `motion_plan.yaml` + source image as INPUTS.

## The fix (ratified)

In `app/marcus/orchestrator/production_runner.py`, `_runner_payload_for_specialist` (kira branch, ~:1465-1472) — **decouple**:
- Return `bundle_path = (runs_root / str(trial_id)).as_posix()` **UNCONDITIONALLY** whenever `runs_root` and `trial_id` are present (per-run isolation invariant).
- Add `motion_plan_path` **ONLY** when `KIRA_MOTION_PLAN_PATH` env is set (conditional seed/replay override — vestigial now that 07D.5 has landed, but preserved).
- Keep the fail-loud precondition: `runs_root is None or trial_id is None` → return `None` (non-run callers unchanged; never silently re-default to global).
- **Do NOT** change `kira/_act.py` (boundary already correct: `payload.get("bundle_path") or DEFAULT_BUNDLE_PATH`). **Do NOT** delete `DEFAULT_BUNDLE_PATH` (taxonomy-rebase territory → Leg-4).
- Keep all motion logic on the shared dispatch site (:1807); **no** per-walk gate-branch hooks (they're duplicated and rot).

## Acceptance / close bar (Murat; die-on-this = ⛔)

1. ⛔ `bundle_path = runs_root/<trial_id>` threaded **unconditionally**; NO global `runs/kira-motion` dir reachable on any walk.
2. ⛔ A real `ProductionTrialEnvelope`/`run.json` emitted BY the continuation walk (not the hand harness) referencing the motion asset.
3. ⛔ Real Kling mp4 in the run-scoped dir; bytes verify `ftyp/moov/mdat` (not size>0, not extension).
4. ⛔ **Non-vacuous isolation:** TWO continuation runs, distinct trial_ids → distinct dirs, hashes differ, neither overwritten; both mp4s coexist.
5. ⛔ **Start-walk-emits-no-motion:** pinning assertion — start walk halts at G1; run-scoped motion dir absent/empty; 07D.5/07E absent from the start-walk node set (asserted on the shared dispatch site).
6. Kling pinned `kling-v1-6`; `sound` **omitted** (sound:false → HTTP 1201); sequential dispatch (parallel-cap). Pick a genuinely motion-worthy slide so the render is a real Kling call, not a 0-credit floor artifact.
7. First-run-stands: the FIRST continuation live render is the verdict. No retry-to-green; a Kling 5xx is re-run only as infra, never as a quality do-over.

**Prove-path:** REWIND-RECOVER of a golden run (fresh walk compounds Texas `directive_path` / Gamma `brief-unmatched` flakes before motion is reached, burning first-run-stands on unrelated failures).

**Live vs offline:** MUST be real-API = the single B2 Kling render + its mp4 bytes. OFFLINE-OK = isolation two-run test, start-walk-no-motion assertion, envelope-schema validation.

## RED-first sequence (Amelia)

1. RED: kira payload with env UNSET returns run-scoped `bundle_path` (no `DEFAULT_BUNDLE_PATH`, no collision).
2. RED: env SET still returns BOTH `motion_plan_path` + `bundle_path` (regression pin).
3. RED: start-walk assertion — 07D.5/07E never fire pre-G1; run-scoped motion dir absent.
4. GREEN: implement the branch split. Full module suite green.
5. (Gated on 1-4 green) LIVE render through the runner continuation walk via rewind-recover; then the two-run coexistence assertion (AC#4) and byte verification (AC#3).

**Files:** `app/marcus/orchestrator/production_runner.py` (kira branch) + `tests/marcus/orchestrator/test_runner_payload_for_specialist.py` (isolation + env-branch regression) + `tests/marcus/orchestrator/test_start_walk_no_motion.py`. `.venv/Scripts/python.exe -m pytest`.

**Lockstep:** No pack bump — neither `production_runner.py` nor `kira/_act.py` is in `block_mode_trigger_paths`.

## Risks (owned)

- Collision hides inside a passing test (Murat) → AC#4 two-run coexistence is the mitigation.
- 07D.5 0-credit motion floor silently promoting slide-1 to manual animation (Kira) → pick a motion-worthy slide.
- Post-render download-to-disk (`kira/_act.py:266-269`) flips status→failure AFTER a paid Kling render on a path/permissions fault → the unconditional bundle_path fix MUST land before the live render so the download target is the isolated run dir.
