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

### Attempt 2 progress log

- G0 extraction SUCCEEDED at the 64k ceiling (the attempt-1 corrective held); G0E → G0R → G1 gates passed under policy (3 gate actions journaled).
- **paused-at-error at node 07 (gary/Gamma deck export), 3/3 auto-retries consistent:** `gamma.export.brief-unmatched` — Gamma FREE-TITLED two literal numeral-hero slides (briefed "Knowledge Growth Outpaces Static Training" → page `73`; "The Leadership Gap" → `18percent`); zero token overlap → bijective title matching cannot bind. Export otherwise perfect (7 pages / 7 briefs, sequential stems, 5/5 others matched, order-consistent gaps).
- Classification: **recoverable dispatch-family error-pause** (NOT the PARK family; NOT designed-honesty). Trial holds paused; journal + 3 gate verdicts intact; `resume-command.json` present.
- Corrective in ratification: order-consistent residual positional bind in the export matcher (amendment-class change to the party-pinned matcher contract; compact Winston+Murat ruling convened, mirrors the §10 apostrophe-amendment precedent). On RATIFY + pinned tests green → resume the paused trial (attach; error-pause recovery is the designed path — no journal edits, no restart).

### Attach refusal + operator-authority drive (recorded waiver)

- Post-recovery `attach` REFUSED: `governed-input-mutated-before-attach` — correct guard behavior: the preflight identity manifest digests the app/ tree, and two KNOWN mutations landed mid-flight: (1) the ratified matcher amendment `7c65cb5a` (the very fix that unblocked node 07), (2) the 38-2 dev agent's uncommitted band work (disjoint from this trial's remaining path: gates G2B→G4A + workbook band read the landed 39-1b-era code; the 38-2 edits activate node 07W.4 which this trial reaches only as the landed stub… the stub file IS under edit — noted, accepted: 07W.4 is model-free passthrough either way and the deliverable bar judges the output).
- **Operator ruling (standing goal directive + policy "operator authority overrides"):** continue the trial under OPERATOR authority via the runner's own drive loop (`_drive_paused_trial_impl` — same policy verdicts, same journal, same budgets, same `_assert_completed_workbook_deliverable` at completion), waiving ONLY the delegate's input-identity gate, consciously and on the record. No journal edits; no identity-manifest edits; first-run-stands unchanged.

### Attempt 2 terminal state: PARKED (Option B interim policy) — per-story verdict lines

Progress achieved: G0(64k) → G0E → G0R → G1 → [node-07 pause → ratified matcher amendment 7c65cb5a → recover] → G2B → G2C → G3 → G4 → G4A → 07W.1 (skeleton call) → 07W.2 (Ask-A packet minted) → **07W.3 FAILED: `workbook-review.enrichment-writer-output-invalid`** — the live enrichment writer emitted claims missing `role`/`source_claim_refs` on `sections.10.claims.0` (11-section skeleton — the richer 64k G0 extraction produced a materially longer lesson than every prior 07W.3 witness; NEW output-shape variance class, same family as the aa1ddff9 order-variance the normalizer v2 fixed). Failure journal persisted → **PARK per the Winston+John Option B ruling** (resume would hard-pause `enrichment-prior-failure`; no restart; no journal edits). Deck legs completed and published (storyboard-B receipt in exports/).

**Batch attribution (M-D3-3 — honest verdict lines):**

| Story | Verdict line |
|---|---|
| 37-2b deep-dive enrichment | **REACHED+FAILED-live-variance at 07W.3** — the surface executed and fail-loud rejected a new writer shape-variance class (missing claim fields on a long lesson). Claim stays OPEN; the variance is REAL production signal: writer-shape hardening (normalizer-v2 class) REQUIRED before run-A attempt 3. |
| 39-1 glossary render | **NOT-REACHED** (07W never ran) — no-evidence; claim stays OPEN. |
| 39-1b exercise MERGE | **NOT-REACHED** (07W never ran) — no-evidence; claim stays OPEN. |

All three stories remain `done-awaiting-live-witness`. Pre-conditions for attempt 3: (1) 07W.3 writer-shape hardening (fail-loud→recorded-degrade or prompt/normalizer fix — party-pattern same as normalizer v2), (2) fresh trial id, (3) STRICT pre-flight re-run. Two genuine production fixes were harvested by this run (G0 64k ceiling `801135a5`; gamma positional-bind amendment `7c65cb5a`) — the paid spend bought real product hardening per the SPOC guardrail.
