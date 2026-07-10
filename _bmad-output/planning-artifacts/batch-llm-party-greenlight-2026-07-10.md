# Party green-light — Batch LLM Execution Mode (2026-07-10)

**Branch:** `dev/batch-mode-2026-07-10`  
**Seats (independent Family A):** John (PM), Winston (Architect), Amelia (Dev), Murat (TEA)  
**Consensus:** **4/4 GO-WITH-AMENDMENTS**  
**Orchestrator:** agrees — treat as approval to fold MUST amendments and author stories (no redundant Checkpoint-1 hold).

## Inputs
- `epic-batch-llm-execution-mode-spec-2026-07-01.md` (research-amended)
- `research/technical-litellm-batch-hookup-research-2026-07-10.md`
- Brief corrections in `openai-batch-mode-run-option-brief-2026-07-01.md`

## Verdicts (summary)
| Seat | Verdict | Headline MUST |
|---|---|---|
| John | GO-WITH-AMENDMENTS | Fence A1-EXT off B6 path; perception-first claim envelope |
| Winston | GO-WITH-AMENDMENTS | Distinct batch-wait pause; resume-from-receipt; shared parse; JSONL size AC; batch profile ≠ forced gpt-5.5 |
| Amelia | GO-WITH-AMENDMENTS | Lock `app/runtime/llm_batch/`; pin `litellm>=1.90.2,<2`; narrow A1 to vision; named T0–T3 paths |
| Murat | GO-WITH-AMENDMENTS | Anti-`batch_completion` hermetic guard; T4 shape≠bytes; B6 land vs promote; hermetic vs liveproof fences |

## Binding claim envelope
**May claim (v1):** opt-in SPOC `execution_mode=batch` for 07G; contract-equivalent perception; pause/resume without duplicate side effects; cost/latency report; realtime unchanged; LiteLLM declared+wired (Files+Batches).

**Must not claim:** all-node tiering; workbook batch; multi-provider beyond openai first; replacing `make_chat_model`; promote-to-default before B3+B4; byte-identical realtime↔batch prose; liveproof from hermetic-only green.

## Next
1. MUST amendments folded into epic (done same session).
2. Story-ready file: `_bmad-output/implementation-artifacts/batch-llm-execution-mode-stories-2026-07-10.md`
3. Sprint-status Kanban rows under `epic-batch-llm-execution-mode`
4. First dispatch: **A0** RED-first

## Non-impasse
No Quinn synthesis required — amendments are surgical, not contradictory.
