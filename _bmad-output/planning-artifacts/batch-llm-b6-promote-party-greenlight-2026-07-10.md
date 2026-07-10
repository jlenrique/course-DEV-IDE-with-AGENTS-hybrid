# Party + checklist — batch-llm-b6-promote (2026-07-10)

**Seats:** John | Winston | Amelia | Murat — **4/4 GO-WITH-AMENDMENTS**  
**Sprint-status evidence:**
- `batch-llm-b3-batch-wait-pause: done`
- `batch-llm-b4-cost-report: done`
- `batch-llm-b6-land-switch: done`

## Claim fence (binding)

Batch is a **normal opt-in production option** via `trial start --llm-execution-mode batch`.  
Default remains **realtime**. Pause/continue: `trial resume-batch`. Cost report: `runs/<id>/llm_batch/cost-report.json`.

**Non-claims:** production-default Batch; all-node tiering; workbook batch; byte-identical prose; live invoice accuracy; live T3/T4 parity; A2/B5 shipped.

## Docs/help touched

- `docs/STATE-OF-THE-APP.md` current snapshot
- `app/marcus/cli/trial.py` `--llm-execution-mode` help

## Residuals (non-blocking)

- `batch-llm-a2-perception-harness`
- `batch-llm-b5-prompt-cache`
- `batch-llm-a1-ext-all-node-tiering`
