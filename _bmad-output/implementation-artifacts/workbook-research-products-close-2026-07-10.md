# Workbook Research Products — Close / Promote Letter

**Date:** 2026-07-10 (UTC close stamp via W4 pack `workbook-w4-20260711T021418Z`)  
**Epic:** `_bmad-output/planning-artifacts/epic-workbook-research-products-glossary-trends-2026-07-10.md`  
**Party:** `workbook-research-products-party-greenlight-2026-07-10.md` (4/4 GO-WITH-AMENDMENTS)  
**Stories SSOT:** `workbook-research-products-stories-2026-07-10.md`  
**Parent:** Agentic Research Foundations (already promoted)

---

## Verdict

**MINI-EPIC CLOSED.** W0–W4 delivered with hermetic + live evidence. Learner-facing workbook products now include encyclopedia **Research Glossary** and backmatter **Research Trends / hot-topics**, fed by the shared research packet — not workbook-only DOI dumps.

`MARCUS_RESEARCH_DETECTIVE_LIVE` remains **default OFF**.

---

## Claim envelope (shipped vs out-of-scope)

| Claim | Status |
|-------|--------|
| Shared M3-safe research packet reader (≥2 consumers, same digest) | **SHIPPED** (W1) |
| Encyclopedia glossary from credibility-labeled rows; provenance retained | **SHIPPED** (W2) |
| Research-trends + bounded hot-topics; model-prior → unusable | **SHIPPED** (W3) |
| Tejal live arm: glossary + trends non-fabricated; MD/DOCX parity | **SHIPPED** (W4) |
| Consumer matrix witness (glossary, trends, Irene, SPOC, future collateral) | **SHIPPED** (W4) |
| Semantic claim↔source audit | **TRAIL** |
| Detective / Consensus / Jefferson default-ON | **OUT** |
| Full workbook visual redesign / novel HAI/PHS | **OUT** |

---

## Live evidence index

| Story | Pack | Result |
|-------|------|--------|
| W0 | `workbook-w0-charter-consumer-matrix-2026-07-10.md` | Charter |
| W1 | `evidence/workbook-w1-20260711T003830Z/` | PASS — dual-consumer digest |
| W2 | `evidence/workbook-w2-20260711T005835Z/` | PASS — encyclopedia glossary |
| W3 | `evidence/workbook-w3-20260711T021204Z/` | PASS — trends + hot-topics |
| W4 | `evidence/workbook-w4-20260711T021418Z/` | PASS — Tejal MD+DOCX; 3 Murat witnesses |

---

## Production surfaces

| Surface | Path |
|---------|------|
| Packet reader | `app/marcus/lesson_plan/research_packet.py` |
| Glossary projection | `app/marcus/lesson_plan/glossary_projection.py` |
| Trends projection | `app/marcus/lesson_plan/trends_projection.py` |
| Compose blocks | `## Research Glossary` (pre-References), `## Research Trends` (post-References) |
| Act wiring | `app/specialists/workbook_producer/_act.py` |

---

## Next (optional / TRAIL)

- Semantic claim audit (`braid-workbook-semantic-claim-citation-audit`)
- OpenAlex / ERIC / LoC usual-suspect providers
- SME glossary writer replacing `GLOSSARY-WRITER-REQUIRED` stubs → **CLOSED** via TRAIL trio (`trail-trio-close-2026-07-10.md`); capability note retained (not human SME-reviewed)
- Detective default-ON policy (party decision — not this close)

---

## Sign-off

Orchestrator close: W0–W4 ACs met against claim envelope; Murat three witnesses present on W4; detective default OFF. Mini-epic **done**.
