# Governed Batch Run A — Pre-Run Authorization (Paid-Run Economy Protocol)

**Date:** 2026-07-16 · **Trial id (fresh, immutable):** `eea3555e-646f-48bd-838e-93c72e5161b2` · **Dispatcher:** Claude (dev/orchestrating agent), under the operator's standing authorization (run A UNGATED per the Winston+John joint ruling 2026-07-15; cost-not-a-constraint memory; operator 3-hour Epics-39/40 goal directive 2026-07-16).

## Pre-flight (plank 1 + M-D3-1a/1b + Amelia F1 skip≠green)

- **Witness replay STRICT: GREEN — 22 passed, 0 skipped, 0 failed** (`WITNESS_REPLAY_STRICT=1 pytest tests/live_witness_replay -n 0`, run at tree `72e17a05`).
- Families witnessed: `workbook-deep-dive-call.v1` (07W.1), `workbook-deep-dive-enrichment-call.v1` (07W.3, incl. frozen FAILED witness aa1ddff9 + PASS witness 838524b8), `workbook-glossary-render.v1` (fdbed233), + registry↔module meta-pin.
- **Drift flags:** clean — the STRICT suite pins `input_digest_drift == {}` and registry capture-digest tamper checks; all green. No prompt/model/config identity change since capture (no prompt or model edits landed in 39-1b — its surfaces are deterministic).

## Boarding manifest (M-D3-3 batch attribution — per-story verdict lines owed)

| Story | Status at boarding | Claim keyed to |
|---|---|---|
| 37-2b deep-dive enrichment | done-awaiting-live-witness (probe 838524b8 ENRICHED PASS) | 07W.3 enrichment + deep-dive deliverable-bar clause |
| 39-1 glossary render | done-awaiting-live-witness (probe fdbed233 PASS 7/7) | terminal 07W glossary render + glossary bar clause |
| 39-1b exercise MERGE | done-awaiting-live-witness (deterministic+T4 green @72e17a05; no probe owed) | terminal 07W exercise composition + exercise bar clause (labels / trim⇔loss / overlay-never-trimmed / blueprint cross-check) |

Boarding rule satisfied: all three greened offline independently. REACHED+PASS ⇒ flip to done citing this run id; NOT-REACHED ⇒ claim stays OPEN (no-evidence — never pass, never fail).

## Run posture (unchanged from handoff)

`marcus_spoc_live_test_runner.py start` · policy `tests/fixtures/marcus_spoc/workbook_live_hil_policy.json` · corpus `course-content/courses/tejal-apc-c1-m1-p2-trends` · `--encounter-mode recorded` · env `MARCUS_G0_DISPATCH_LIVE=1`, real key from `.env` (sentinel absent from shell — verified). **First-run-stands** (no retry-to-green; deterministic judge = the runner's machine bars).

## Standing rulings in force

- **Interim recovery policy (Option B):** a transient-family `workbook-review.enrichment-prior-failure` pause ⇒ **PARK the trial** (never restart, never edit the journal); deterministic-family pauses are correct behavior — investigate, don't retry.
- **Anticipated designed-honesty pause class:** an ENRICHED run whose glossary covered-entry body quotes a non-DOI pool-row TITLE carrying a %/$ numeral will G1-fail by design (P6 scope) — recognize as designed honesty, not a defect.
- AC 6 residual-duplication operator spot-check is DECLARED at this run (WARN taxonomy; John's seed pairs: admin-cost %, 73-day doubling, digital front door) — never claimed machine-caught.

## Attempt 1 — `eea3555e-646f-48bd-838e-93c72e5161b2`: START-REFUSED (frozen as evidence; first-run-stands)

- Both live G0 extraction calls TRUNCATED mid-JSON at the 32000 output-token ceiling (attempt: 51 components salvaged; sanctioned single required-output retry: 40 salvaged); pre-pass authored **0 provisional LOs** from 11 non-empty source files → invalid G0 output → `{"reason": "start-failed", "status": "refused"}`. Zero pipeline progress beyond G0; no gate reached; no journal contamination (PARK ruling family not implicated — this is G0-start, not 07W.3).
- **Corrective applied on its own production merits** (the runner's own diagnostic prescribes it): `G0_EXTRACTION_MAX_COMPLETION_TOKENS` 32000 → 64000 (`app/marcus/orchestrator/g0_enrichment_wiring.py`; parse-tolerance floor test `>= 32000` still green, 16/16). Mirrors the 37-2b attempt-1 (aa1ddff9) freeze→fix→fresh-attempt precedent.
- Attempt-1 run dir preserved at `runs/eea3555e-…` (run.json + runtime context only). Two paid G0 calls spent; no witness minted (a start-refusal licenses no claim).

## Attempt 2 — fresh id `648de559-786f-450b-9378-b86649bf7705`, same posture, ceiling 64000
