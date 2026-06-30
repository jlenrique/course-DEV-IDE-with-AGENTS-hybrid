# Coverage interlock COVERED arm — faithful positive-control LIVE walk (option C)

- **Verdict: NOT-CONVERGED** (legitimate; orchestrator falls back to close-path A)
- method: FRESH full real-runner walk on an engineered faithful positive-control corpus
  (`course-content/courses/coverage-faithful-probe`, single `70%` focal slide), live gpt-5
  G0 enrichment, deck-only `ComponentSelection(deck=True, motion=False, workbook=False)`.
- trial_id: `825136d0-c035-4410-a6e6-64a09f10ca64`
- run_dir: `state/config/runs/825136d0-c035-4410-a6e6-64a09f10ca64` (preserved)
- discipline: first-run-stands, NO retry-to-green, NO hand-doctored narration. One corpus,
  one real walk. The walk did not reach G3 → reported as NON-CONVERGED per charter.

## What happened (disk ground-truth)
The walk started, ran **live gpt-5 G0 enrichment** (real, ~88s), paused at **G0E** (approved),
paused at **G0R** (approved), then **error-paused at node 02 (Texas retrieval)** BEFORE reaching G3:

- `final_status`: paused-at-error
- error: `dispatch_retrieval missing required input: directive_path` (specialist `texas`, node `02`)
- gate_sequence: `G0E approve -> G0R approve -> paused-at-error`
- **G3 never reached; coverage-receipt.json never derived; gate never evaluated on a real receipt.**
- total walk seconds: 229.1
- ZERO ElevenLabs spend (never approached the audio seam).

## HONEST ROOT CAUSE — launch-recipe omission, NOT a narration-fidelity finding
`run_production_trial(...)` was launched WITHOUT a `directive_path` argument. The Texas
retrieval node (`02`) requires `directive_path` (the trial-475 silent-bypass guard:
`retrieval_dispatch.py` raises rather than silently no-op). The golden run threaded a
`directive.yaml`; this driver did not. So the walk error-paused at the retrieval node on the
continuation walk after G0R — a **driver/harness gap**, distinct from the documented
**narration figure-substitution gap** that the COVERED arm is meant to probe.

This run therefore neither confirms nor refutes the narration-fidelity question. The gate's
PASS arm STILL has not touched the real runner.

## Positive signal preserved (corpus engineering DID work at the annotation level)
`g0-enrichment.json` (live gpt-5) emitted the intended faithful coverage annotations:
- **Slide 2 (focal): all 3 source points carry `70%`** in `verbatim_text` → figure-bearing
  (`source_figs={percent:70}`) → would route through the figure-facet path and be
  `covered_in_narration` VERIFIED iff Irene Pass-2 narration carries `70%`.
- Slide 1 (framing): 3 must-cover NON-figure points (`detail_in_narration`) — the residual
  full-span block risk (would need verbatim-span carriage in narration).

Separately confirmed this session (read-only, from prior real run `1e385fd0` exports): the REAL
Irene Pass-2 generated narration DOES carry `%` tokens verbatim ("Over 70%", "55%", "34%",
"18%"), so `source_figs ⊆ figures(narration)` is genuinely achievable — the feasibility basis
that justified attempting C.

## Deterministic judge
- reached G3: **NO**
- non-vacuous receipt with ≥1 figure-token-verified covered_in_narration must-cover row: **N/A (no receipt)**
- `enforce_coverage_gate_before_audio(enrique)` raised/passed: **N/A (never evaluated)**
- **JUDGE: FAIL** against the option-C bar — no real-run figure-token-verified COVERED point
  was produced and the gate was never exercised; the walk error-paused before G3.

## Files
- `driver-result.json` — structured run result (gate_sequence, outcome, timings)
- `error-pause.json` — the node-02 Texas retrieval error-pause record
- `g0-enrichment.json` — live gpt-5 annotations (shows the engineered 70% figure points)
- `decision-card-G0E.json` / `decision-card-G0R.json` — the two gates that were approved
- `corpus-used/` — the engineered faithful positive-control corpus
- `driver.py` — the exact launch driver used
- `walk.log` — flushed live log
