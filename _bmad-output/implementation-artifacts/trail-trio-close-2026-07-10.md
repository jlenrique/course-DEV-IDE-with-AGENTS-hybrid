# TRAIL trio — Close Letter (2026-07-10)

**Branch:** `dev/agentic-research-foundations-2026-07-10`  
**Party green-light:** `trail-trio-party-greenlight-2026-07-10.md` (4/4 GO-WITH-AMENDMENTS)  
**Party CLOSE:** `trail-trio-party-close-2026-07-10.md` (4/4 CLOSE-WITH-AMENDMENTS)  
**Product goal:** Marcus-SPOC runtime (not concierge proofing theater)

---

## Verdict

**TRAIL TRIO CLOSED under claim fences.** OpenAlex adapter + glossary writer polish + WARN-only semantic tripwire substrate shipped. Full semantic claim↔source audit remains **open TRAIL**.

`MARCUS_RESEARCH_DETECTIVE_LIVE` remains **default OFF**.

---

## What shipped

| Slice | Status | Evidence |
|-------|--------|----------|
| **OpenAlex** Texas `RetrievalAdapter` | **done** | Hermetic 5/5; LIVE `evidence/openalex-live-20260711T024437Z/` PASS (pos DOI + neg empty) |
| **Glossary SME polish** | **done** | Hermetic: no HTML stub in body; capability note; injectable writer pin |
| **Semantic WARN tripwire** | **done (thin)** | `SEMANTIC_TRIPWIRE` non-None; `audit_semantic_framing`; hermetic warn/skip/overlap pins |

### Code

- `skills/bmad-agent-texas/scripts/retrieval/openalex_provider.py` (+ register in `__init__.py`)
- `scripts/utilities/run_openalex_live_evidence.py`
- `app/marcus/lesson_plan/glossary_projection.py` — `GLOSSARY_CAPABILITY_NOTE`
- `app/specialists/_shared/source_fidelity_audit.py` — `SEMANTIC_TRIPWIRE` + `audit_semantic_framing`

### MUST-FIX folded at CLOSE

- OpenAlex: `authority_tier` left `None` (OA ≠ peer-reviewed)

---

## Claim envelope

### May claim

- OpenAlex: public-API **DOI metadata + OA link discovery** (Texas Shape-3)
- Glossary: research-informed encyclopedia **stub** with visible capability note; no invented findings beyond indexed title/metadata
- Semantic: **pipeline + disposition** WARN-only heuristic (`gates_production=False`)

### Must not claim

- OpenAlex PDF byte download, institutional SSO, arbiter/credibility scoring, or semantic validation
- Glossary is human **SME-reviewed** / oracle quality
- Semantic tripwire **catches all weak claims**, gates production, or makes L2 “support faithfulness”
- Glossary/semantic LIVE-proven beyond hermetic (OpenAlex alone has LIVE this session)

---

## Inventory / kanban

- 🟢 `openalex-retrieval-adapter` closed
- 🟢 `glossary-sme-writer-polish` closed
- 🟡/🟠 `braid-workbook-semantic-claim-citation-audit` remains open (full audit); WARN tripwire substrate noted
- Sprint: `research-trail-openalex-adapter` / `glossary-sme-polish` / `semantic-warn-tripwire` → done; `research-trail-semantic-claim-audit` stays deferred

---

## Residual TRAIL (not this close)

- Full semantic claim↔source audit calibration (≥3 workbook runs)
- ERIC / LoC adapters
- Tracy gate resume/recover; LLM Tracy refine
- Consensus/Jefferson default-ON policy
