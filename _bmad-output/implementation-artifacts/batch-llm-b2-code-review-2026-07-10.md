# Code review — batch-llm-b2-perception-route (2026-07-10)

**Gate:** single-gate `bmad-code-review`  
**Layers:** Blind Hunter | Edge Case Hunter | Acceptance Auditor (independent subagents)  
**Prior party:** Winston/Amelia/Murat 3/3 GO-WITH-AMENDMENTS

## Layer verdicts

| Layer | Verdict |
| --- | --- |
| Blind Hunter | PASS-WITH-FIXES |
| Edge Case Hunter | PASS-WITH-FIXES |
| Acceptance Auditor | PASS-WITH-FIXES |

## MUST-FIX folded

1. Malformed parse failures wrap with `custom_id` in message (AC4) — `test_malformed_batch_row_fail_loud_per_custom_id`
2. OFF pin asserts no `llm_batch/` dir and no run dir under `runs_root` (AC9)
3. `joined.unexpected_custom_ids` → fail-loud `vision.batch.unexpected-rows`
4. Receipt `row_count` mismatch → fail-loud `vision.batch.receipt-stale` (no join/re-submit)
5. Blank/duplicate `slide_id` → fail-loud `vision.batch.slide-id-invalid` before Files API
6. Multi-slide whole-act single submit pin — `test_act_batch_multi_slide_single_submit`
7. AC6 poll signature: story amended to document required receipt kwargs (`run_id`, `row_count`, `model`) plus injectable `sleep_fn`/`interval_s`/`timeout_s` (implementation kept; contract clarified)

## Post-fix validation

`pytest` B2 + llm_batch + vision provider/act → **65 passed**; ruff clean on touched files.

## Final gate verdict

**CLOSE B2 as done** (hermetic ON+OFF+T1/T2 claim fence intact; live T3 not claimed).

## Next (John sequence + operator BMAD loop)

B2 done → **create-story B6-land** (opt-in SPOC `realtime|batch`, default realtime, T7 OFF non-interference) → party green-light → implement → code-review → loop until flawless. B3+B4 only before B6-promote.
