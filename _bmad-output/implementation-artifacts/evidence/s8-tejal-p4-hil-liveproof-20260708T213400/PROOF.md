# S8 Tejal Part-4 HIL Composed Proof — Evidence

**Trial:** `9b6dc48b-031a-4b02-870c-ab7f76047c8d`  
**Corpus:** `course-content/courses/tejal-c1m1-p4-assessments-bridge`  
**Operator stand-in:** AFK HIL driver (`s8_hil_driver.py`) as `juanl`  
**Intent:** `s8-tejal-p4-ratified-collateral-intent.yaml` → `narrated-deck-with-workbook`  
**Date:** 2026-07-08 / 2026-07-09 UTC

## What this proves

1. **Compose completed** after ~8 minutes of live per-file LLM classification (the prior Codex timeout cut point).
2. **No `--auto-confirm-directive`.** G0 used scripted interactive confirm: **edit → confirm**.
3. **No `--allow-offline-cost-report`.**
4. **Styleguide** committed via pre-minted `selection_code` (D2 path) → `hil-2026-apc-crossroads-classic`.
5. **Bundle binding:** `lesson_plan_collateral_bundle_id: narrated-deck-with-workbook`; component selection deck+motion+workbook.
6. **HIL variety exercised:**
   - G0 confirm: `e` then `c`
   - G0E: `approve`
   - G0R: `approve` (ratified-los.json written)
   - G1: `edit` (inspection payload) then continue
7. Walk reached **Gary/Gamma export** after G1 and error-paused on known flake `gamma.export.brief-unmatched` (Part-4 is effectively a single-slide bridge deck — matches deferred `gamma-single-slide-deck-title-matcher-flake`).

## What this does NOT claim

- Full walk to `completed` / workbook terminal sidecar.
- `production_clone_launch_evidence: true` (start receipt stamped `registered-offline` / `skipped-no-langsmith-env` despite LangSmith keys present in `.env` — cost report still wrote a smith URL; triage separately).
- "S8 complete" without BMAD party concurrence.

## Recover

One `recover_production_trial` re-attempt after the error-pause is recorded in `recover1.json` (expected: same brief-unmatched class on single-slide Part-4).

## Artifacts

See this directory: driver log, HIL transcript, facts.json, directive, trial-start, run.json, run_summary, ratified-los, decision cards G0E/G0R/G1, recover1.json.
