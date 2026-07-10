# Agentic Research Foundations — Stories SSOT (2026-07-10)

**Status:** R0 done; R1 ready-for-dev; R2–R7 backlog  
**Epic:** `_bmad-output/planning-artifacts/epic-agentic-research-foundations-2026-07-10.md`  
**Party:** `agentic-research-foundations-party-greenlight-2026-07-10.md` (GO-WITH-AMENDMENTS + Quinn R7)  
**Branch:** `dev/agentic-research-foundations-2026-07-10`

> **LIVE-TEST (operator):** Every story closes only with authentic live evidence on the real seam. Hermetic is necessary, not sufficient. Corpus = Tejal / ratified existing runs — not novel HAI/PHS.

---

## Sequencing

```text
R0 → R1 → R2 → R3 → R4 → R5 → R6 → R7 → promote
TRAIL: 17-2/3/4 · semantic claim audit · PubMed v2 · tracy-gate-resume-recover · LLM Tracy refine
```

---

## Story R0 — Charter, taxonomy, live-test matrix

**Status:** done (2026-07-10)  
**AC:**
1. Evidence-hierarchy taxonomy doc (peer-reviewed preferred; full hierarchy allowed; credibility fields named).  
2. Claim envelope written (modes a/b/c; G2 ≠ claim-support; non-claims list).  
3. Live-test matrix: per-story live arm, credentials required, evidence path template.  
4. Six party decisions locked verbatim into R0 artifact.  
5. Kanban epic + R0…R7 rows filed.

**DoD:** Artifacts committed; party decisions not relitigated. (R0 is docs/contracts — live matrix is the “live” deliverable; no network required.)

**Delivered:**
- `docs/dev-guide/research-evidence-hierarchy.md`
- `_bmad-output/implementation-artifacts/research-r0-charter-taxonomy-live-matrix-2026-07-10.md`
- Kanban rows under `epic-agentic-research-foundations`

---

## Story R1 — Posture runtime on production seam

**Depends:** R0  
**AC:**
1. Single seam: posture-aware selector **or** dispatcher+swap (Amelia); flag-OFF path unchanged.  
2. All three postures emit `RetrievalIntent` without `NotImplementedError`.  
3. Hermetic: reuse `tests/fixtures/retrieval/tracy_smoke/`.  
4. **LIVE:** flag-ON (or temporary probe) Scite dispatch for ≥1 corroborate + ≥1 gap_fill intent from existing Tejal `research_goals` / fixture plan; evidence pack with intents + Texas rows.  
5. No Tracy→HTTP bypass; Texas dispatcher only.

**DoD:** Hermetic green + live evidence pack. Flag may remain default OFF after probe if R3+R4 not yet green (document).

**Paths:** `research_wiring.py`, `irene_bridge.py`, `posture_dispatcher.py` / selector, `test_braid_s3_research_wiring.py`, `test_tracy_postures.py`.

---

## Story R2 — Consensus live + evidence-bolster

**Depends:** R1  
**Borrow:** `27-2.5-consensus-adapter`, `evidence-bolster-control-surface`  
**AC:**
1. Consensus removed from deferred-only when bolster/detective path requests it; Texas directory honest.  
2. Evidence-bolster control surface (minimal) for corroborate.  
3. Hermetic cross_validate fixtures.  
4. **LIVE:** Scite∩Consensus dual-provider retrieve on ≥1 corroborate query; evidence pack.  
5. No Epic-17 parallel HTTP clients.

**DoD:** Hermetic + live dual-provider witness.

---

## Story R3 — Triangulator (thin 17-1)

**Depends:** R2  
**AC:**
1. Triangulator consumes `TexasRow`s + convergence — composite reliability + contradiction flags.  
2. Corroborate path requires triangulation or fail-loud / explicit `single_provider` receipt.  
3. Hermetic dual-provider fixtures.  
4. **LIVE:** composite score + contradiction (or explicit none) on real Scite∩Consensus rows.

**DoD:** Hermetic + live triangulated receipt.

---

## Story R4 — Credibility surfacing

**Depends:** R0 taxonomy, R3  
**AC:**
1. Every `research_entries` row: hierarchy tier + peer-review flag + provider provenance (fail-loud if missing).  
2. Workbook/operator receipt projects fields (additive; no layout redesign).  
3. Flag-OFF rows still mint/render.  
4. **LIVE:** inspect live-minted entries from R3 arm; fields present and non-vacuous.

**DoD:** Hermetic schema pins + live field witness.

---

## Story R5 — Jefferson / institutional library provider

**Depends:** R0 (seam design); may parallel R3/R4 after R2  
**AC:**
1. Texas `RetrievalAdapter` registered; follows `how-to-add-a-retrieval-provider.md`.  
2. Hermetic contract tests (stub).  
3. **LIVE when Jefferson creds available:** ≥1 authenticated full-text or metadata fetch; evidence pack. If creds absent: document fence + operator hold — do not fake live.  
4. Full-text additive; DOI/identity spine remains Scite/Consensus.

**DoD:** Registration + hermetic; live or explicit creds-absent fence.

---

## Story R6 — Irene retrieval intake (thin)

**Depends:** R4  
**Borrow:** `irene-retrieval-intake`  
**AC:**
1. Pass-2 / intake consumes triangulated rows; never fabricates cites.  
2. Hermetic fabricate-cite path RED.  
3. **LIVE:** flag-ON walk segment shows intake consuming real rows (Tejal/fixture); no silent injection without contract.

**DoD:** Hermetic + live intake witness.

---

## Story R7 — Hard pause teeth (Quinn)

**Depends:** R4 (credibility rows exist); ideally R6  
**AC:**
1. When `MARCUS_RESEARCH_DETECTIVE_LIVE=ON`, Pass-2 blocked until approve/reject/defer disposition written.  
2. Advisory-only **cannot** close this story.  
3. Explicit non-claim: resume/recover completeness = TRAIL (`tracy-gate-resume-recover`).  
4. Hermetic gate state machine.  
5. **LIVE:** flag-ON → landing-point → Pass-2 blocked → real disposition → Pass-2 proceeds only after (first-run-stands).

**DoD:** Hermetic + live teeth proof. Promote letter carries teeth vs TRAIL split.

---

## Promote — Foundations close

**Depends:** R0–R7 done (R5 may close with creds-absent fence if operator confirms)  
**AC:** Close letter; claim envelope; live evidence index; default flag still OFF unless party promotes ON; TRAIL list filed in deferred-inventory.

---

## TRAIL (not foundations)

| ID | Note |
|----|------|
| Epic 17-2 / 17-3 / 17-4 | Related-resources, inline citation, hypothesis packages |
| `braid-workbook-semantic-claim-citation-audit` | Claim↔source faithfulness |
| `p2-pubmed-adapter-v2` | Biomedical recall |
| `tracy-gate-resume-recover` | Pause resilience / atomicity |
| LLM Tracy refine | Optional refine on intents |
| Consensus/Jefferson default-ON | Policy after foundations |
