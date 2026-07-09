# Workbook Artifact — Completeness Research Report (party-mode consensus)

**Date:** 2026-07-06 · **Session:** 15 (Class P — party-mode research, READ-ONLY, no production code edited)
**Branch:** `dev/workbook-2026-07-06` (freshly cut from `master` @ `ad89cb76`; zero commits at report time)
**Method:** 3 parallel evidence-gathering agents (code / planning / tests+live-output) → tailored 4-seat BMAD party (Winston, Murat, John, Paige) → consensus verdict. Corroborated against `docs/ONBOARDING.md` (regenerated 2026-07-05, graph baseline `b3ab2137`).

---

## Consensus verdict

**~58% complete — stated as "60%, medium confidence"** (John's framing; Winston/Murat/Paige concur).

> **One sentence:** The workbook's *machinery* is essentially built and honestly gated, but it has been proven only as a **structural artifact for a single frozen lesson (tejal)** through a **side-door standalone driver** — it is **not yet a generalized product capability, not yet proven in-graph, and the one produced document is a scaffold, not a learner-ready deliverable.**

### Per-axis scores

| Axis | Voice | Score | Verdict |
|---|---|---:|---|
| Design/spec + deliverable quality | Paige | 55% | Spec/schema/gates ~85%; the produced document is a skeleton (placeholder prose, unchecked review, empty citations) — deliverable quality alone ~25-30% |
| Production-workflow wiring / in-graph | Winston | 55% | Registry wiring ~80% and genuinely real; but never proven via a real composed graph run — the proof went *around* the graph |
| Live-proof + test maturity | Murat | 68% | Render/artifact-witness pipeline production-grade proven; content-correctness (semantic audit, numeral gate, revoicer) unproven |
| Scope vs deferred backlog | John | 55% | Mechanics real; hardcoded to one lesson = working spike, not product capability |

No impasse — the four voices converged without needing the Quinn/John escalation chain.

---

## What is genuinely DONE (high confidence)

- **Producer engine** `app/marcus/lesson_plan/workbook_producer.py` (1073 lines) — `WorkbookProducer(ModalityProducer)`, status `"ready"`. Markdown canonical → DOCX via `python-docx`. Composes S0-S7.
- **Structural fidelity gates** all implemented FAIL-mode: G1 numeric, G2 citation, G3 exercise, AC-5 100% segment coverage, AC-8 dual-coding (workbook ⊇ VO) superset.
- **Pydantic schema family** `collateral_spec.py` (WorkbookSpec/WorkbookSection/Exercise/DepthDeltaContract, closed `BloomLevel` enum, `extra="forbid"`) + JSON-schema mirror `collateral_spec.v1.schema.json`.
- **In-graph specialist** `app/specialists/workbook_producer/` — node **07W** "Companion Workbook Producer", 9-node scaffold, deterministic (no LLM, `model_config_ref: null`), terminal sidecar. Shipped `b914bb9e`.
- **Registry wiring all green** — pipeline-manifest (07W, `insertion_after:15`, `gate:false`, depends_on compositor), dispatch-registry, capability-overlay (`capability_state: wired`, `in_dispatch/in_manifest/real_module: true`, `registry_status: active`), modality_registry (`status:"ready"`), composition.py (`WORKBOOK_NODE_ID="07W"`), bundle_catalog (`narrated-deck-with-workbook`).
- **Enrichment consumption** `workbook_enrichment.py` projects frozen G0 enriched card → WorkbookSpec (gated `MARCUS_G0_ENRICHMENT_ACTIVE`, default OFF).
- **Test suite** — 78 passed / 1 skipped / 1 failed across `tests/marcus/lesson_plan/test_workbook_producer.py` (13 ACs, no-mocks), `tests/specialists/workbook_producer/test_workbook_producer_brick.py` (6 floors, real fixture run-dir), `test_workbook_s0_s7.py`, `test_workbook_enriched_consumption.py`. Notable maturity signal: AC-7 (embedded image) was hardened from a vacuous "any image part" check (python-docx's blank template ships a thumbnail) to asserting a real slide PNG lands in `word/media/*`.
- **Real artifact on disk** — `_bmad-output/artifacts/workbooks/tejal-apc-c1-m1-p2-trends@1.docx` (15.4 MB OOXML, 18 embedded slide PNGs) + `...@1.md` (34 KB canonical). Git-committed `4374af80`.

Prior arc trail (all `done` in `docs/STATE-OF-THE-APP.md`): Braid S2 producer (`2cac27b`) → S3 build-out first REAL DOCX (`4374af80`) → P5-S1 consumes enriched corpus (`f07e89c`, byte-verified) → 07W in-graph brick (`b914bb9e`). Design spike `_bmad-output/planning-artifacts/workbook-component-design-2026-06-25.md`; spec `spec-braid-s2-workbook-producer.md`, `spec-07w-workbook-producer-brick.md`.

---

## Ranked residual gap list (consensus, load-bearing first)

1. **In-graph adapter hardcoded to tejal Ch2/Ch3 constants** (`app/specialists/workbook_producer/_act.py` — `_CH2_KC`/`_CH3_KC`, `_FURTHER_READING`). The single biggest demo→product gap; the capability is parameterized by one lesson's structure. **Not even formally tracked as a workbook follow-on** — that absence is itself a gap (Winston + John, emphatic). *Needs a ticket with an owner + trigger before anyone calls this "done."*
2. **No end-to-end composed in-graph run** with `MARCUS_G0_ENRICHMENT_ACTIVE=1` on a **non-tejal** corpus, reaching 07W via the real dispatcher and consuming a live run-dir (not the test fixture). The proven DOCX came from `scripts/utilities/produce_tejal_workbook.py` (standalone driver) — side door, not front door (Winston).
3. **Word-form numeral gate bypass** (`braid-workbook-wordform-numeral-gap`). G1 is symbol-only (`$`/`%`); "forty-two percent" passes un-audited. A **known bypass in an existing gate**, flagged material to the very lesson shipped — documented ≠ contained (Murat + John).
4. **Deliverable not learner-ready** (Paige). The shipped artifact self-declares incompleteness three times: every transcript segment carries `REVOICE-REQUIRED: writer (Paige/Sophia)` (placeholder voicing, not authored prose); unchecked `IRENE_REVIEW_MARKER` + Human Review Checkpoint footer (no editorial review executed); "Cited research" section reads "live-research leg deferred… no DOI'd entries injected." Needs: a real re-voice pass + executed Irene review + resolution of the empty citation section.
5. **Semantic claim↔source audit** (`braid-workbook-semantic-claim-citation-audit`; L2 `SEMANTIC_TRIPWIRE` is a stub) — zero automated proof the prose doesn't hallucinate against source; relies on operator spot-check (Murat + John).
6. **One test failure not yet isolated** — re-run `test_ac12_dp6_fresh_required_blocks_reuse_stamp` with `-n 0` (single-worker) to confirm it's a Windows/xdist shared-output-dir concurrency artifact, not a reuse-blocking logic defect (Murat: "believed environmental, not proven environmental").
7. Spec teeth missing for **voicing + review gates** (named in the ownership model but not encoded as pass/fail ACs like AC-8/AC-9); **stale `bundle_catalog.py` `mechanism_only_never_produced` tag** (a real DOCX now exists); `braid-collateral-id-uniqueness`.

### Correctly fenced / genuinely optional (defer without guilt)
- `braid-workbook-pdf-render-leg` (DOCX-only is a legitimate v1 boundary; no PDF lib on disk)
- `braid-workbook-worksheet-fill-in-affordances` (answer blanks / lined areas — enhancement)
- `braid-open-ended-asset-design-pattern` (generative asset design vs predefined spec — now trigger-eligible since Slice 1 shipped, but not blocking)

---

## Notes for the next session
- The `dev/workbook-2026-07-06` branch is empty and uncharted. If it targets workbook work, **gap #1 (adapter generalization)** is the obvious first target — it converts a one-lesson spike into a product capability and is the item John will not let the team round up past 60% without.
- The deferred `braid-workbook-*` items live in `_bmad-output/planning-artifacts/deferred-inventory.md`.
- Full evidence and the four unabridged party voices are preserved in the session-15 conversation and mirrored in `SESSION-HANDOFF.md`.
