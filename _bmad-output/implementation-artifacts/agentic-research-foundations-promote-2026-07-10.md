# Agentic Research Foundations — Promote / Close Letter

**Date:** 2026-07-10 (UTC close stamp 2026-07-11T003255Z last live pack)  
**Branch:** `dev/agentic-research-foundations-2026-07-10`  
**Epic:** `_bmad-output/planning-artifacts/epic-agentic-research-foundations-2026-07-10.md`  
**Stories SSOT:** `_bmad-output/implementation-artifacts/agentic-research-foundations-stories-2026-07-10.md`  
**Party green-light:** `agentic-research-foundations-party-greenlight-2026-07-10.md` (4/4 GO-WITH-AMENDMENTS + Quinn R7 Teeth-Thin)  
**Kanban:** `epic-agentic-research-foundations` → **done**; `research-foundations-promote` → **done**

---

## Verdict

**FOUNDATIONS PROMOTED / CLOSED.** R0–R7 delivered with authentic live evidence (R5 accepted under documented Chrome-session fence). Product goal remains the **Marcus-SPOC runtime** research service — not concierge proofing.

`MARCUS_RESEARCH_DETECTIVE_LIVE` remains **default OFF** (opt-in). Party has **not** promoted the flag to default-ON; R3+R4 live green satisfied the *eligibility* precondition, not an automatic flip. Flag-OFF path stays bit-identical.

---

## Claim envelope (shipped vs TRAIL)

| Claim | Status |
|-------|--------|
| Posture-aware detective intents (a corroborate / b gap_fill / c embellish) on production path | **SHIPPED** (R1) |
| Scite + Consensus triangulation for corroborate | **SHIPPED** (R2–R3) |
| Evidence hierarchy + peer-review + provenance on every research row | **SHIPPED** (R4) |
| Jefferson library Texas provider seam; live when session available | **SHIPPED** seam+hermetic (R5); **live fenced** `chrome_running_quit_required` |
| Irene intake consumes rows; fabricate-cite RED | **SHIPPED** (R6 thin) |
| Hard pause before Pass-2 when detective flag ON (approve\|reject\|defer) | **SHIPPED** (R7 Teeth-Thin) |
| Semantic claim↔source audit | **TRAIL** `braid-workbook-semantic-claim-citation-audit` |
| Full Epic 17 related-resources / inline / hypothesis | **TRAIL** 17-2/3/4 |
| Full Epic-28 resume/recover atomicity | **TRAIL** `tracy-gate-resume-recover` |
| LLM Tracy graph as production default | **TRAIL** |
| Consensus / Jefferson default-ON policy | **TRAIL** (policy after foundations) |
| OpenAlex / ERIC / LoC primary-source adapters | **TRAIL** (usual-suspects) |
| Workbook encyclopedia glossary + research-trends/hot-topics | **NEXT** `workbook-research-products-glossary-and-trends` |
| Novel HAI/PHS ingest; workbook layout redesign; G2→claim-support | **OUT OF SCOPE** |

**Standing invariant (binding):** wrangled research remains available to appropriate run consumers (not workbook-only).

**Teeth vs TRAIL (Quinn):** R7 = hard pause teeth only. Resume/recover completeness is explicitly **not** claimed.

---

## Live evidence index (canonical packs)

| Story | Pack | Result |
|-------|------|--------|
| R0 | `research-r0-charter-taxonomy-live-matrix-2026-07-10.md` | Charter / matrix (no network) |
| R1 | `evidence/research-r1-20260710T211425Z/` | PASS — Scite corroborate + gap_fill |
| R2 | `evidence/research-r2-20260710T215111Z/` | PASS — Scite∩Consensus dual live |
| R3 | `evidence/research-r3-20260710T233619Z/` | PASS — title-bridge; 5 dual_provider clusters |
| R4 | `evidence/research-r4-20260710T233843Z/` | PASS — 21/21 non-vacuous credibility fields |
| R5 | `evidence/research-r5-20260711T002458Z/` | **FENCED** — `chrome_running_quit_required` (operator: quit optional; fence accepted) |
| R6 | `evidence/research-r6-20260711T002804Z/` | PASS — 21 consumed; fabricate RED |
| R7 | `evidence/research-r7-20260711T003255Z/` | PASS — landing → block → advisory RED → approve unlocks |

Live scripts: `scripts/utilities/run_research_r{1–7}_live_evidence.py`.

---

## Production surfaces (pointer)

| Surface | Path |
|---------|------|
| Wiring / detective flag | `app/marcus/orchestrator/research_wiring.py` |
| Citation + credibility | `research_citation.py`, `research_credibility.py` |
| Hard-pause gate | `research_detective_gate.py` (Pass-2 node `08`) |
| Irene intake (thin) | `app/specialists/_shared/research_intake.py` |
| Triangulator | `skills/bmad-agent-texas/scripts/retrieval/triangulator.py` |
| Consensus / Scite / Jefferson | Texas providers under `skills/bmad-agent-texas/scripts/retrieval/` |
| Hierarchy taxonomy | `docs/dev-guide/research-evidence-hierarchy.md` |

---

## TRAIL filed in deferred-inventory

Confirmed present under Agentic Research Foundations section:

- `tracy-gate-resume-recover`
- `braid-workbook-semantic-claim-citation-audit`
- `openalex-retrieval-adapter` / `eric-retrieval-adapter` / `loc-primary-source-adapter`
- Epic 17-2/3/4 + `p2-pubmed-adapter-v2` (elsewhere / stories TRAIL table)
- **`workbook-research-products-glossary-and-trends`** — **reactivated NEXT** (operator: immediately after this promote)

---

## Next

1. Party green-light + stories for **`workbook-research-products-glossary-and-trends`** (strawman already filed).  
2. Optional later: upgrade R5 fence → live after Chrome quit / SSO cookie copy.  
3. Optional later: party decision to default-ON detective / Consensus / Jefferson — **not** part of this promote.

---

## Sign-off

Orchestrator close: R0–R7 ACs met against claim envelope; live index complete; detective default OFF; TRAIL + next mini-epic filed. Promote story **done**.
