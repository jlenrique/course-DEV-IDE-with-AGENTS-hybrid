# Party green-light — batch-llm-b3-batch-wait-pause (2026-07-10)

**Seats:** John | Winston | Amelia | Murat — independent  
**Consensus:** **4/4 GO-WITH-AMENDMENTS** → proceed

## MUST folded

1. Distinct `waiting_for_provider_batch`; CLI `trial resume-batch`; operator message with trial/batch/receipt + resume command
2. `WaitingForProviderBatch` ≠ `SpecialistDispatchError`; catch before error-pause in **both** walks
3. Non-blocking production batch path; resume polls receipt only (zero create_file/create_batch/submit)
4. Terminal failed/expired/cancelled fail-loud; no realtime fallback
5. T5 double-resume hermetic; claim fence hermetic only
6. Envelope/schema/golden updates; named RED tests

B4 stays separate; B6-promote still needs B3+B4.
