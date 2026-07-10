# PROOF — Planning-context → Irene Pass-1 handoff

**Stamp:** 20260709T180555 (remediated same session after dual-gate review)
**Baseline:** `5be7de46`
**Claim fence:** Does NOT claim interactive SPOC REPL, full lecture ingestion, S8 redesign, step-1 rebuild, or full compose liveproof.

## Components live-tested as built (per-component dumps)

| # | Component | AC | Dump | Result |
|---|-----------|----|------|--------|
| 1 | PlanningContext loader | H1 | `per-component/01-loader-H1.txt` | 9 passed |
| 2 | Runner thread | H2 | `per-component/02-runner-H2.txt` | 4 passed |
| 3 | Prompt + receipt + fail-loud + absent + continuity | H3/H5/H4/H6 | `per-component/03-prompt-receipt-H3H5H4H6.txt` | 10 passed |
| 4 | Floor strip regression | — | `per-component/04-regression-strip.txt` | 8 passed |

Also: aggregated `pytest-handoff.txt` (pre-remediation 20 passed).

## Review remediation folded

- BH-1/ECH-03: malformed artifacts → `SpecialistDispatchError` at runner
- BH-2/ECH-01/04/05: stopwords + touch-before-absent (fail-loud only on zero touch)
- BH-3/ECH-07: purpose/audience conflict across files fail-loud
- BH-4: scrub `planning_context` from envelope JSON (labeled section only)
- BH-5: consumer-shaped continuity pins (`irene-pass1.md` + contribution shape)
- ECH-06: skip lo_ignore on llm_format_fallback
- ECH-09: write `planning-context-coverage.json` before fail-loud raise

## Honesty signals (Murat three-signal)

- Loadable from run_dir artifacts
- In-prompt labeled section marker (not unlabeled JSON dump)
- Coverage receipt on output (or on-disk before fail-loud)
