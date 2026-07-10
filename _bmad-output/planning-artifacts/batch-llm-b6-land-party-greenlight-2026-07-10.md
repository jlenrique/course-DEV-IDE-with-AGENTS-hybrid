# Party green-light — batch-llm-b6-land-switch (2026-07-10)

**Seats:** John (PM) | Winston (Architect) | Amelia (Dev) | Murat (TEA) — independent subagents  
**Story:** `_bmad-output/implementation-artifacts/batch-llm-b6-land-switch.md`  
**Consensus:** **4/4 GO-WITH-AMENDMENTS** → proceed (party+orchestrator agreement = approval)

## Verdicts

| Seat | Verdict |
| --- | --- |
| John | GO-WITH-AMENDMENTS |
| Winston | GO-WITH-AMENDMENTS |
| Amelia | GO-WITH-AMENDMENTS |
| Murat | GO-WITH-AMENDMENTS |

## MUST folded into story

1. **John:** default realtime; opt-in only; vision-only; no promote; `llm_execution_mode` ≠ tracked/ad-hoc `execution_mode`; pause wording stub only; T7 affirmative spies
2. **Winston:** persist on `RunState`; CLI → `start_trial` → `run_production_trial` → `trial-start.json`; overlay **only** when `specialist_id=="vision"` **and** mode==`"batch"` (do **not** overlay `"realtime"`); no B3 status
3. **Amelia:** named RED tests + order (RunState → CLI → trial-start.json → dispatch → T7)
4. **Murat:** T7 spies on create_file/create_batch + no `llm_batch/` dir; claim fence hermetic; false-green pins for BATCH/empty/missing

## Binding sequence after land

Implement → code-review → done. B3+B4 before B6-promote only.
