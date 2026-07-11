# W0 — Workbook Research Products charter

**Story:** `workbook-w0-charter-consumer-matrix`  
**Date:** 2026-07-10  
**Status:** done  
**Party:** GO-WITH-AMENDMENTS — `workbook-research-products-party-greenlight-2026-07-10.md`  
**Epic:** `epic-workbook-research-products-glossary-trends-2026-07-10.md`

---

## Claim fence (locked)

| Claim | In this mini-epic? |
|-------|-------------------|
| Encyclopedia-style glossary entries informed by tier-labeled research rows | YES |
| Backmatter research-trends + bounded hot-topics callout from packet evidence | YES |
| Shared research packet available to named consumers (not workbook-only) | YES |
| Live Tejal arm: non-vacuous glossary + trends; no fabricate-cite | YES (W4) |
| Semantic claim↔source audit | NO (TRAIL) |
| Detective / Consensus / Jefferson default-ON | NO |
| Novel providers / HAI/PHS ingest / full workbook redesign | NO |
| “Verified scholarship” beyond research-informed synthesis | NO |

Products may claim: **research-informed synthesis from tier-labeled, provenance-bearing rows.**  
Products may **not** claim: verified claim↔source semantic audit.

---

## Scope fence (party MUST)

Learner-facing workbook products + consumer-availability invariant only. Additive to existing `workbook_producer` / run-dir seams. Detective flag remains default **OFF**.

---

## Consumer matrix

| Consumer | Access mode | Artifact / path pattern | Notes |
|----------|-------------|-------------------------|-------|
| Glossary writer (W2) | Read run packet via shared reader | `run.json` contribution `research_wiring` @ `04.55` → `research_entries` (+ credibility fields) | Encyclopedia articles; must retain provenance |
| Trends / hot-topics projector (W3) | Same shared reader | Same `research_entries` + triangulation metadata when present | Bounded callout; no forecasting theater |
| Irene Pass-2 / retrieval intake | Intake packet on contribution | `research_intake` key (R6) via `app.specialists._shared.research_intake` / `irene.retrieval_intake` | Fabricate-cite RED already |
| SPOC / operator receipt | Disk + envelope | `run.json` + optional landing/disposition receipts when detective ON | Operator visibility of wrangled rows |
| Future collateral projectors | Shared reader (not orchestrator import) | Same packet contract | Named now; implement later |

**Access rule:** Prefer one SSOT packet (entries + hierarchy + provenance + triangulation). Fail-loud or record-empty — never silent fabricate.

---

## SSOT gap check (feeds W1)

| Surface today | Location | M3-safe? |
|---------------|----------|----------|
| Mint at `04.55` | `research_wiring` → `research_entries` + `research_intake` | Orchestrator (OK) |
| Workbook read | `app.marcus.lesson_plan.workbook_enrichment.research_entries_from_run` | YES (neutral lesson_plan) |
| Irene consume | `app.specialists._shared.research_intake.consume_research_entries` | YES (_shared) |
| Orchestrator envelope helper | `research_wiring.research_entries_from_envelope` | Specialists must **not** import |

**Verdict:** Foundations left a usable workbook reader and a separate Irene intake path. **W1 is still required as a thin shape-pin / shared facade** so ≥2 consumers (glossary + trends, and ideally SPOC witness) resolve the **same** packet contract with empty/corrupt failure modes documented — **not** a new packet builder. If W1 finds `research_entries_from_run` already sufficient, it shrinks to pin + fixture + dual-consumer live witness only (John/Winston synthesis).

---

## Story sequence (ratified)

```text
W0 (this) → W1 thin reader/shape-pin → W2 glossary → W3 trends/hot-topics → W4 live Tejal
```

LIVE-TEST every story. Hermetic alone ≠ done. Corpus = Tejal / ratified runs.

---

## Evidence / done-bar for later stories (Murat)

W4 evidence pack must include:
1. ≥1 encyclopedia glossary article with source-backed metadata  
2. ≥1 trends/hot-topics section with cited claims  
3. Consumer matrix rows with path/id + access mode + witness result  

Negative: missing/malformed/unsupported → fail closed or mark unusable.
