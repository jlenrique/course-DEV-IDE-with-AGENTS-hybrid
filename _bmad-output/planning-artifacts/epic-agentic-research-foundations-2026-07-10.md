# EPIC SPEC — Agentic Research Foundations (Tracy Detective Service)

**Status:** PROMOTED / CLOSED (2026-07-10) — R0–R7 done; close letter `agentic-research-foundations-promote-2026-07-10.md`  
**Branch (proposed):** `dev/agentic-research-foundations-2026-07-10`  
**Type:** Brownfield mini-epic — borrows Epic 17 + Epic 28 + braid S3/S6; does **not** reopen S8; does **not** require novel HAI/PHS content ingest  
**Product goal:** Improve the **Marcus-SPOC runtime** so research is a flexible, robust, value-adding **service** for higher-ed production — not a DOI dump. Proofing runs may discover defects; they are not the design target.

**Party:** John / Winston / Amelia / Murat — 4/4 GO-WITH-AMENDMENTS. Quinn synthesis on R7: **Teeth-Thin / TRAIL-Resilient**. Record: `agentic-research-foundations-party-greenlight-2026-07-10.md`.  
**Promote:** Detective flag remains default **OFF**. Next: `workbook-research-products-glossary-and-trends`.

---

## Operator intent (binding)

Wire foundations so specialty agents can pursue information **agentically / detective-like (Tracy)** in service of:

| Mode | Intent | Today |
|------|--------|-------|
| **(a) Confirm credibility** | Corroborate / challenge course claims with evidence; surface credibility | Scite metadata exists; unused as detective loop; G2 = resolvability only |
| **(b) Fill gaps** | Pursue missing evidence for Irene-identified gaps / research_goals | One-shot Scite search per goal; no iterative pursuit |
| **(c) Enrich** | Embellish with high-quality related scholarship | Topical search only; no embellish posture runtime |

**Evidence policy:** Prefer peer-reviewed journals; allow the full **hierarchy of evidence** when credibility of each source is **explicitly surfaced** (never silent equivalence of a blog and a systematic review).

**Access assumption:** Operator can provide **Jefferson library** credentials. Architect the Texas library provider seam; live-enable when creds present.

### Standing invariant — research consumer availability (operator 2026-07-10)

Wrangled research is a **run service**, not a workbook-only side effect. Current foundations stories and **all future** research/workbook specs MUST keep triangulated, credibility-labeled research available to appropriate consumers across the workflow (workbook writers/projectors, Irene retrieval intake, operator/SPOC receipts, future collateral). Fail-loud or record-empty — never silent fabricate. Post-foundations productization of this invariant: mini-epic `workbook-research-products-glossary-and-trends` (encyclopedia glossary + research-trends/hot-topics backmatter) — strawman `epic-workbook-research-products-glossary-trends-2026-07-10.md`.

### ⛔ LIVE-TEST BINDING (operator 2026-07-10 — epic-wide)

**Authentically live-test every component as it is implemented and validated.** Hermetic tests are necessary but **never sufficient** to close a story. Each R-story done-bar includes a first-run-stands live arm on the real production seam (Scite OAuth, Consensus when enabled, Jefferson when creds present, flag-ON detective path, real pause disposition for R7). Novel HAI/PHS content is still out of scope — use Tejal / ratified existing runs as the live corpus. Concierge/proofing convenience is not the design target.

---

## Honest current state (do not rediscover)

**Live canonical path (braid S3/S6):**
`Irene Pass-1 research_goals` → `research_wiring` @ `04.55` → `DeterministicPostureSelector` → Texas dispatcher → **Scite-only** → `research_entries` → workbook DOI block.

**Borrow, don't rebuild:** Epic 28 postures/bridge/fixtures; Epic 17 triangulator/modes (thin-slice); `27-2.5` + `evidence-bolster` + `irene-retrieval-intake`; Texas Shape-3 + SciteProvider. **No** product path via parallel `scripts/api_clients/` (Epic 17 client paths superseded).

---

## Binding party decisions (R0 locks — do not relitigate)

| # | Decision | Binding |
|---|----------|---------|
| 1 | Tracy | **Posture-aware deterministic** intent shaping; optional LLM refine OFF / TRAIL. No LLM Tracy graph in foundations ship claim. |
| 2 | Triangulation | **Required for (a) corroborate** (Scite∩Consensus or fail-loud / explicit `single_provider` receipt). **Optional for (b)/(c)** with hierarchy + peer-review flags. |
| 3 | Operator gate (Quinn) | **R7 = hard pause teeth** when detective flag ON (approve/reject/defer before Pass-2 spend). **TRAIL = resume/recover resilience.** Advisory never closes `tracy-complete`. Live-test proves teeth. |
| 4 | Library | Seam + hermetic + **live when Jefferson creds available**; fence live only if creds absent (document fence). |
| 5 | Flag | `MARCUS_RESEARCH_DETECTIVE_LIVE` default **OFF** until R3+R4 hermetic **and** live green; distinct from `MARCUS_RESEARCH_DISPATCH_LIVE`. Flag-OFF path bit-identical to today. |
| 6 | Claim fence | Foundations ≠ semantic claim↔source audit; ≠ SME prose auto-rewrite; G2 stays resolvability-only. |

### R1 seam (Amelia MUST)

Production path owns **one** call site: make `DeterministicPostureSelector` posture-aware **or** implement `PostureDispatcher` **and** swap `IreneTracyBridge` / `research_wiring` to it. No dual fantasy. Keep OFF-path selector as degrade.

---

## Story sequence (binding)

```text
R0  Charter + claim envelope + evidence-hierarchy taxonomy + live-test matrix
R1  Posture runtime on production seam (flag-gated); live Scite posture arms
R2  Consensus live enablement + evidence-bolster (borrow 27-2.5); live Scite∩Consensus
R3  Triangulator atop Texas rows (thin 17-1); live composite scores
R4  Credibility surfacing on research_entries + workbook/receipt; live field witness
R5  Jefferson / institutional library Texas provider; live when creds present
R6  Irene retrieval intake (thin); live consume rows; no fabricate-cite
R7  Hard pause teeth (Quinn); live disposition → Pass-2; resume/recover = TRAIL
── promote foundations ──
── NEXT (operator 2026-07-10): workbook-research-products-glossary-and-trends ──
TRAIL: 17-2/17-3/17-4 · semantic claim audit · PubMed v2 · OpenAlex · ERIC (opt) · LoC primary-source · tracy-gate-resume-recover · LLM Tracy refine
```

---

## Non-goals (v1 foundations)

- Novel HAI/PHS content processing  
- Workbook visual/layout redesign  
- Full Epic 17 modes as ship claim  
- Semantic claim-support audit  
- Claiming full Epic-28 resume/recover inside R7  
- Designing code merely to make concierge proofing runs pass  

---

## Success metrics (foundations done-bar)

| Metric | Bar |
|--------|-----|
| Live-test | Every R0–R7 story has authentic live evidence pack (or documented creds-absent fence for R5 only) |
| Postures | All three postures live-dispatch; hermetic fixtures green |
| Triangulation | Live Scite∩Consensus composite for corroborate |
| Credibility | Every live `research_entries` row carries hierarchy tier + peer-review flag + provenance |
| Gate | Flag-ON live: Pass-2 blocked until disposition; proceeds only after |
| Claims | Close letter matches envelope; no overclaim |

---

## Artifact targets

| Artifact | Path |
|----------|------|
| This spec | `_bmad-output/planning-artifacts/epic-agentic-research-foundations-2026-07-10.md` |
| Stories SSOT | `_bmad-output/implementation-artifacts/agentic-research-foundations-stories-2026-07-10.md` |
| Party record | `_bmad-output/planning-artifacts/agentic-research-foundations-party-greenlight-2026-07-10.md` |
| Kanban | `sprint-status.yaml` |

---

## Guardrails

- Marcus-SPOC product only (CRITICAL DESIGN GUARDRAIL)  
- Texas Shape-3 = retrieval SSOT  
- Two-walks: stay on `04.55` hook; no new manifest node  
- Party consensus + orchestrator agreement = approval  
- **Live-test every component** (operator 2026-07-10)  
