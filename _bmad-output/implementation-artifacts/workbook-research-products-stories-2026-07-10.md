# Workbook Research Products — Stories SSOT (2026-07-10)

**Status:** W0–W4 **done** / mini-epic **CLOSED** (2026-07-10) — close letter `workbook-research-products-close-2026-07-10.md`  
**Epic:** `_bmad-output/planning-artifacts/epic-workbook-research-products-glossary-trends-2026-07-10.md`  
**Party:** `workbook-research-products-party-greenlight-2026-07-10.md`  
**Parent:** Agentic Research Foundations (promoted)  
**Branch:** `dev/agentic-research-foundations-2026-07-10` (continue) or operator-named follow-on branch

> **LIVE-TEST:** Hermetic necessary, not sufficient. Corpus = Tejal / ratified runs. No fabricate-cite. Detective default OFF.

---

## Sequencing

```text
W0 → W1 → W2 → W3 → W4
```

---

## Story W0 — Charter, consumer matrix, claim fence

**Status:** done (2026-07-10)  
**AC:**
1. Consumer matrix names ≥ glossary writer, trends projector, Irene intake, SPOC/operator receipt, future collateral — with access mode + artifact path pattern.
2. Claim fence locked: research-informed synthesis from tier-labeled rows; **not** semantic claim audit.
3. SSOT gap check: document whether foundations `research_entries` + existing `research_entries_from_run` suffice for ≥2 consumers, or W1 must add a thin shared reader.
4. Scope fence + MUST amendments from party folded verbatim.
5. Kanban epic + W0…W4 rows present.

**DoD:** Charter artifact committed; party amendments not relitigated.

**Delivered:** `workbook-w0-charter-consumer-matrix-2026-07-10.md` — W1 = thin shape-pin (not new builder).

---

## Story W1 — Thin research-packet reader / shape-pin

**Status:** done (2026-07-10)  
**Depends:** W0  
**AC:**
1. Shared reader (or documented adoption of existing) usable by ≥2 consumers without importing `marcus.orchestrator`.
2. Hermetic fixture pins packet shape + empty/corrupt failure modes.
3. **LIVE:** ≥2 consumers resolve the same live/ratified packet (witness in evidence pack).
4. No duplicate packet builder if foundations already mint SSOT.

**DoD:** Hermetic + live consumer witness.

**Delivered:**
- `app/marcus/lesson_plan/research_packet.py` — M3-safe facade; `load_research_packet` + glossary/trends resolvers; shared `packet_digest`
- Hermetic: `tests/unit/marcus/lesson_plan/test_research_packet_w1.py` (8 passed)
- Live: `evidence/workbook-w1-*/` — 21 R4 live entries; dual-consumer same digest; Irene intake same rows; empty fail-closed
- Script: `scripts/utilities/run_workbook_w1_live_evidence.py`
- No new packet builder (mint remains `04.55`)

---

## Story W2 — Glossary encyclopedia component

**Status:** done (2026-07-10)  
**Depends:** W1 (or W0 if W1 shrunk to pin-only and reader already shared)  
**AC:**
1. Workbook structure gains encyclopedia-style glossary entries (not dictionary glosses).
2. Writer intake from credibility-labeled research rows; provenance retained.
3. RED hermetic: missing provenance / fabricate path / empty research.
4. **LIVE:** ≥1 non-vacuous glossary article with source-backed metadata on Tejal/ratified corpus.

**DoD:** Hermetic + live glossary witness; additive to `workbook_producer` only.

**Delivered:**
- `app/marcus/lesson_plan/glossary_projection.py` — `GlossaryArticleBrief` + default encyclopedia writer + run intake via W1 packet
- `compose_workbook` / `produce` gain `## Research Glossary` (after Answer Key, before References); G2 audits glossary `source_ref`s
- `_act.py` wires `glossary_inputs_from_run` into workbook inputs
- Hermetic: `tests/unit/marcus/lesson_plan/test_glossary_w2.py` (7 passed)
- Live: `evidence/workbook-w2-20260711T005835Z/` — 3 non-vacuous articles from R4 rows; MD+DOCX; G2 clean
- Script: `scripts/utilities/run_workbook_w2_live_evidence.py`

---

## Story W3 — Research trends + hot-topics backmatter

**Status:** done (2026-07-10)  
**Depends:** W1  
**AC:**
1. Backmatter research-trends section + bounded hot-topics callout.
2. Claims tied to packet evidence; confidence/provenance labeled.
3. RED hermetic: model-prior-only topics rejected or marked unusable.
4. **LIVE:** non-vacuous trends/hot-topics section with cited claims.

**DoD:** Hermetic + live trends witness.

**Delivered:**
- `app/marcus/lesson_plan/trends_projection.py` — trends + bounded hot-topics; injected model-prior → `unusable`
- `## Research Trends` after References; G2 audits usable trend/hot-topic `source_ref`s
- `_act.py` wires `trends_inputs_from_run`
- Hermetic: `tests/unit/marcus/lesson_plan/test_trends_w3.py` (6 passed)
- Live: `evidence/workbook-w3-*/` — 5 trends + 3 hot topics; fabricated inject rejected; MD+DOCX
- Script: `scripts/utilities/run_workbook_w3_live_evidence.py`

---

## Story W4 — Live Tejal workbook arm

**Status:** done (2026-07-10)  
**Depends:** W2 + W3 schema-stable  
**AC:**
1. Narrow claim: Tejal workbook arm consumes research → glossary + trends, non-fabricated.
2. Markdown/DOCX parity from same composed model.
3. Consumer matrix witness rows filled with paths + results.
4. Detective OFF path: no fabricate; empty/recorded handling honest.

**DoD:** Live evidence pack with Murat’s three witnesses.

**Delivered:**
- Live: `evidence/workbook-w4-20260711T021418Z/` — Tejal MD+DOCX with glossary + trends; G2 clean; detective OFF empty honest
- Consumer matrix: 5/5 PASS (glossary, trends, Irene, SPOC, future collateral)
- Hermetic: `tests/unit/marcus/lesson_plan/test_workbook_w4_empty_honesty.py`
- Script: `scripts/utilities/run_workbook_w4_live_evidence.py`
- Close letter: `workbook-research-products-close-2026-07-10.md`

---

## TRAIL (not this mini-epic)

| ID | Note |
|----|------|
| `braid-workbook-semantic-claim-citation-audit` | Claim↔source faithfulness |
| Detective / Consensus / Jefferson default-ON | Policy |
| Full workbook visual redesign | Out of scope |
| Novel HAI/PHS ingest | Out of scope |
