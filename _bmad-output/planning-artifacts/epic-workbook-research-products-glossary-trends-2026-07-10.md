# Mini-epic strawman — Workbook Research Products (post-foundations)

**Status:** CLOSED / PROMOTED (2026-07-10) — W0–W4 done; close letter `workbook-research-products-close-2026-07-10.md`  
**Parent:** `epic-agentic-research-foundations-2026-07-10.md` (PROMOTED)  
**Inventory id:** `workbook-research-products-glossary-and-trends`  
**Type:** Brownfield mini-epic / add-on story cluster  
**Product goal:** Turn wrangled detective research into **learner-facing workbook products** (encyclopedia-style glossary + research-trends backmatter), while ensuring research remains a **first-class run artifact** available to every appropriate consumer in the Marcus-SPOC workflow.

**Party:** John / Winston / Amelia / Murat — 4/4 GO-WITH-AMENDMENTS. Record: `workbook-research-products-party-greenlight-2026-07-10.md`.  
**Stories SSOT:** `workbook-research-products-stories-2026-07-10.md`  
**Close:** Detective flag remains default **OFF**.

---

## Operator intent (binding)

When workbook structure is next updated:

1. **Glossary component** — each glossary item is an **encyclopedia article**, not a dictionary gloss. Research (Tracy detective + Texas triangulation + credibility fields) supplies **highly credible input** to the writer that authors those entries. Writers do not invent scholarship; they synthesize from wrangled, tier-labeled rows.
2. **Research trends / hot topics** — every workbook’s **backmatter** includes a research-trends section with a **hot-topics** callout, powered by the new research capability (enrich / gap-fill / triangulated literature signals — not a static marketing blurb).

### Standing invariant — research consumer availability (current + future specs)

**Wrangled research must be made available to the appropriate consumers throughout the app’s workflow/run.** Foundations already mint `research_entries` (+ triangulation receipt) at `04.55`; this mini-epic and all future research/workbook specs MUST:

- Treat triangulated / credibility-labeled research as a **durable run contribution** (envelope + on-disk), not a one-shot DOI dump for the workbook alone.
- Name **consumers** explicitly (at minimum: workbook glossary writer, workbook trends projector, Irene Pass-2 / retrieval intake, operator receipt / SPOC surfaces, future collateral projectors).
- Fail-loud or record-empty when a named consumer expects research and it is absent/corrupt — never silent fabricate.
- Prefer **one SSOT research packet** (entries + hierarchy + provenance + triangulation) over per-consumer re-fetch.

*Direction may flip if substrate evolves* (e.g. a dedicated research ledger node) — revalidate at green-light.

---

## Proposed story sketch (not yet party-ratified)

| ID | Intent |
|----|--------|
| **W0** | Charter: glossary encyclopedia contract + trends/hot-topics contract + consumer matrix (who reads research where) |
| **W1** | Research packet SSOT / consumer API (if foundations leave gaps) — hermetic + live witness that ≥2 consumers read the same packet |
| **W2** | Glossary component in workbook structure + writer intake from credible research rows |
| **W3** | Backmatter research-trends + hot-topics callout projector |
| **W4** | Live Tejal (or ratified corpus) workbook arm: glossary entries + trends section non-vacuous; no fabricated cites |

Exact story count / gate mode = party at green-light after foundations promote.

---

## Non-goals (this mini-epic)

- Replacing Agentic Research Foundations R0–R7 work
- Semantic claim↔source audit (remains TRAIL)
- Full workbook visual redesign beyond glossary + trends sections
- Novel HAI/PHS ingest

---

## Reactivation trigger

**Agentic Research Foundations promote letter closed** (R0–R7 done, or R5 creds-absent fence accepted) **and** operator/party pulls this mini-epic next (operator-stated: immediately after foundations).

---

## Related

- Foundations TRAIL table: `agentic-research-foundations-stories-2026-07-10.md`
- Deferred inventory: `workbook-research-products-glossary-and-trends`
- Workbook producer / S7–S8 collateral structure (extend, don’t fork)
