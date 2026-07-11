# R0 — Claim envelope + live-test matrix

**Story:** `research-r0-charter-taxonomy-live-matrix`  
**Date:** 2026-07-10  
**Status:** done (charter artifacts)

## Claim envelope (what foundations will claim)

| Claim | In foundations? |
|-------|-----------------|
| Posture-aware detective intents (a corroborate / b gap_fill / c embellish) on production path | YES |
| Scite + Consensus triangulation for corroborate | YES |
| Evidence hierarchy + peer-review + provenance on every research row | YES |
| Hard pause before Pass-2 when detective flag ON (teeth) | YES (R7) |
| Jefferson library Texas provider seam + live when creds | YES (R5) |
| Irene intake consumes rows without fabricating cites | YES (R6) |
| Semantic claim↔source audit | NO (TRAIL) |
| Full Epic 17 related-resources / inline / hypothesis modes | NO (TRAIL) |
| Full Epic-28 resume/recover atomicity | NO (TRAIL `tracy-gate-resume-recover`) |
| LLM Tracy graph as production default | NO (TRAIL) |
| Novel HAI/PHS content processing | NO |
| Workbook layout redesign | NO |
| Workbook encyclopedia glossary + research-trends/hot-topics | NO (post-foundations mini-epic `workbook-research-products-glossary-and-trends`) |
| G2 becomes claim-support | NO (stays resolvability) |

**Standing invariant (operator 2026-07-10):** wrangled research must remain available to appropriate consumers throughout the run (not workbook-only). Applies to foundations remainder and the post-foundations mini-epic.

## Locked party decisions (verbatim)

1. Deterministic posture-aware selector; LLM refine OFF.  
2. Triangulation required for corroborate; optional for gap_fill/embellish.  
3. R7 hard pause teeth; TRAIL resume/recover (Quinn).  
4. Jefferson seam + live when creds.  
5. `MARCUS_RESEARCH_DETECTIVE_LIVE` default OFF until R3+R4 hermetic+live green.  
6. Claim fence as table above.

## Live-test matrix (operator binding)

| Story | Live arm | Creds | Evidence path pattern |
|-------|----------|-------|------------------------|
| R0 | N/A (charter) | — | this artifact |
| R1 | Scite posture dispatch ≥1 corroborate + ≥1 gap_fill from Tejal/fixture goals | Scite OAuth | `_bmad-output/implementation-artifacts/evidence/research-r1-*/` |
| R2 | Scite∩Consensus dual retrieve | Scite + Consensus | `…/evidence/research-r2-*/` |
| R3 | Live composite / contradiction on dual rows | same | `…/evidence/research-r3-*/` |
| R4 | Live-minted rows show hierarchy fields | same | `…/evidence/research-r4-*/` |
| R5 | Jefferson authenticated fetch | Jefferson library | `…/evidence/research-r5-*/` or **creds-absent fence doc** |
| R6 | Intake consumes live rows; no fabricate | Scite (+Consensus) | `…/evidence/research-r6-*/` |
| R7 | Flag-ON → block Pass-2 → disposition → proceed | Scite + detective flag | `…/evidence/research-r7-*/` |

**Rule:** Hermetic green alone ≠ story done. First-run-stands live pack required (except R0; R5 may fence if creds absent).

## Taxonomy pointer

`docs/dev-guide/research-evidence-hierarchy.md`
