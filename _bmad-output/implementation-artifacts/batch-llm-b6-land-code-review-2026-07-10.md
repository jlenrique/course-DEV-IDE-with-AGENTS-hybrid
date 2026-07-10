# Code review — batch-llm-b6-land-switch (2026-07-10)

**Gate:** single-gate `bmad-code-review`  
**Layers:** Blind Hunter | Edge Case Hunter | Acceptance Auditor (independent subagents)  
**Prior party:** John/Winston/Amelia/Murat **4/4 GO-WITH-AMENDMENTS**

## Layer verdicts

| Layer | Verdict |
| --- | --- |
| Blind Hunter | PASS-WITH-FIXES |
| Edge Case Hunter | PASS-WITH-FIXES |
| Acceptance Auditor | PASS-WITH-FIXES |

## MUST-FIX folded

1. T7 affirmative spies include `litellm.create_file` / `litellm.create_batch` + submit + batch route + no `llm_batch/` dir; production overlay seam exercised on default realtime
2. Real `start_trial` → `trial-start.json` receipt pins for `realtime` and `batch` (incl. wait-note); create_file/create_batch spies during start
3. Non-vision overlay strips any leaked `llm_execution_mode` key

## Post-fix validation

Hermetic B6 + RunState schema + vision OFF pins green; ruff clean on touched production files.

## Final gate verdict

**CLOSE B6-land as done** (opt-in switch claim fence; not promote; not B3 pause).

## Next

B3 `waiting_for_provider_batch` + B4 cost before **B6-promote**. Optional A2 harness. Live T3/T4/T5 remain production-claim evidence only.
