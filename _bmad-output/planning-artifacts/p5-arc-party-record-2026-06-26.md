# Party-Mode Record — P5 Downstream-Consumption Arc (autonomous /goal)

**Branch:** `dev/p5-downstream-consumption-2026-06-26` (fresh from master `38c5357`).
**Goal:** design→implement→live-test→iterate until a BMAD team signs off on LIVE runs of **P1**, then **P2**, then **P3**; push live tests progressively downstream; final test = Desmond aggregates a deck+motion+workbook bundle into a Descript project (do P4/P5 if the posting needs them, else defer cleanly). No mocks; reuse assets; cost-bounded via a curated 3-slide slice.
**Pipeline (charter `preplanning-content-preparation-charter-2026-06-26.md`):** P1 component-extraction (BUILT) → P2 Texas pass-0 (provenance-normalize→universal-md + live citation resolution) → P3 Irene pass-1 (pedagogy overlay) → P4 materializer → P5 consumption.

---

## Round 1 — Arc sequencing + P1 sign-off approach + 3-slide slice
**Team (tailored):** Winston (architecture/DRY), Murat (test strategy / live-run sign-off bar). Spawned as independent persona subagents (autonomous-session party pattern).
**Outcome:** **GREEN-WITH-AMENDMENTS, 2/2, no impasse.** Arc sequencing approved; P1 to proceed to T11 + fresh 3-slide live test + party CLOSE.

### Winston (architecture) — 6 binding amendments
- **A1 — P2 code placement:** resolution/normalization LOGIC lives Texas-side (sibling to `skills/bmad-agent-texas/scripts/retrieval/`, routing through `app/specialists/texas/retrieval_dispatch.py::dispatch_retrieval` + `TexasRow` + `retrieval/normalize.py`); a THIN runner brick under `app/marcus/orchestrator/` calls it (mirrors `research_wiring.py` Option-A attach). Dependency arrow one-way — verify `lint-imports`.
- **A2 — ONE gate only:** P2/P3 ENRICH the frozen `G0EnrichmentResult` feeding the EXISTING G0E gate. Mint NO new gate codes, NO new walk side-effects.
- **A3 — Freeze P2 live resolution** in a fingerprint-keyed cache (mirror `run_g0_enrichment`'s `<run_dir>/...-cache/<fp>.json`); dispatch fires once, frozen `resolved|failed` is replay-deterministic.
- **A4 — RED groundedness seam (HARD-MANDATORY):** before freezing `content_fingerprint`, verify `verbatim_excerpt` is a substring of parent-source bytes; non-resolving → hard fail OR explicit `resolution_status: ungrounded`, never a silent sha. (Collects the `SourceRef.quoted_span` containment debt the LO schema deferred to "S2 runtime" = P2. Fold the cheap substring assertion into the P1 live run too, to catch root poisoning before P2 is built.)
- **A5 — Close the PubMed gap before P2 dev opens:** either add a `pubmed` `RetrievalAdapter` (wrap the MCP tool, deterministic query/refine, identity_key DOI/PMID) OR resolve DOIs via `scite` and drop PubMed from P2 v1.
- **A6 — DRY surface:** do NOT force-reuse `figure_tokens`/`collateral_spec` (downstream/QA SSOTs). DO reuse the S1 LO schema (`app/.../learning_objective.py`), the `g0_enrichment` hashing primitives, and `retrieval/normalize.py`.
- **Shared front-matter note:** build a slim shared `universal_markdown_preamble.emit_front_matter(...)` in Texas's tree, EXPORTED, consumed by BOTH `run_wrangler` and the workbook producer — so P5 consumers read ONE front-matter contract, not a P2-private one.

### Murat (test strategy) — 5 binding amendments + per-stage live sign-off evidence
- **M1 — Cache-busted + receipt-bearing:** every live sign-off clears/misses the corpus-fingerprint cache; asserts real model id (≠ offline marker containing "offline") + non-zero spend. No CLOSE rests on a cache replay or offline marker.
- **M2 — Curate the slice (DONE):** the slice must GUARANTEE P2 sees ≥1 resolving citation AND ≥1 failing citation, and P3 sees ≥1 LO with ≥1 load-bearing component referencing it. (Slice carved + a fail-probe citation `doi:10.9999/jihs.2099.deadbeef` added.)
- **M3 — Deterministic judge, first-run-stands, no retry-to-green:** each stage's live assertion is structural/deterministic (refs resolve, enums valid, sha matches, DOI dereferences), never an LLM eyeball. First live run's outcome is the record; a failed live run is a code/prompt FINDING to fix, not a die to re-roll. Re-run only after a code/prompt change, and say so.
- **M4 — Method-level incremental checkpoints (no-defer):** P1 first live call returns ≥1 typed component with sha tie-back before full reconcile; P2 resolve ONE real citation live (single call, DOI dereferences) before building the batch normalizer, then prove ONE fail; P3 annotate ONE component live with resolving lo_refs before the full overlay. Culminating per-stage run = confirmation; E2E = confirmation-of-confirmations.
- **M5 — Provenance RED is an executable gate:** include a test that INJECTS a hash mismatch and asserts hard-fail (an invariant never seen red is theater).

**Per-stage live sign-off evidence (Murat):**
- **P1:** cache-busted live run; real model_id + non-zero spend; live reconcile holds on messy output; every excerpt a verbatim substring (RED); no parent outside enumerated set; + 3-layer T11 + party CLOSE.
- **P2:** SAME live run shows ≥1 citation resolving to a DOI that independently dereferences AND ≥1 failing with reason + `resolved_ref is None`; front-matter `content_fingerprint` matches frozen P1 excerpt sha; body verbatim == source (no paraphrase); + T11 + CLOSE.
- **P3:** referential integrity (every lo_ref/assessment_link/teaches_after id exists); bloom + pedagogical_role red-reject out-of-enum (3-surface); coverage (load-bearing annotated, non-load-bearing skipped); input is P2's .md (front-matter present, proving layering); + T11 + CLOSE.

---

## P1 Execution — T11 3-layer adversarial review (verdict: SHIP-WITH-FOLLOWONS)
Independent confirmation of Winston A4: the verbatim-substring groundedness check promised at `learning_objective.py:161` is NOT implemented. Remediate before next live E2E:
- **[MUST-1]** `g0_enrichment_wiring.py:~613` — live LO parse unguarded per-row; one malformed row aborts the whole pre-pass (discards already-extracted components). Fix: per-row try/except, skip+log.
- **[MUST-2]** `g0_enrichment_wiring.py:~487/~553` — live payload assumed dict-of-list; crashes on top-level list/string. Fix: guard `isinstance` dict/list; treat bad shape as zero rows (coverage fallback covers files).
- **[SHOULD-A4]** `g0_enrichment_wiring.py:~400` — no excerpt/quoted_span verbatim-substring check (charter provenance-RED). Fix: verify excerpt ⊆ source; RED or flag on mismatch. (= Winston A4 + the deferred SourceRef.quoted_span debt.)
- **[SHOULD]** `:~265/:~316` — `read_text(utf-8)` only; a cp1252 outline → UnicodeDecodeError → collapses to one whole-file component (defeats P1). Fix: utf-8→cp1252/latin-1 fallback before binary path. (Operator on Windows; source is KING.)
- **[SHOULD]** AC-S2-7 default-OFF byte-identity claimed-but-not-tested (asserts `!=G0E`, passes on upstream crash). Fix: pin first pause == G1.
- **[SHOULD/known]** huge-doc + many-file context-budget chunking (already a noted follow-on).
- **[NIT]** DRY the two type-models (`source_type.py:182/276` dup validators); TypedSource dead-code; de-tautologize AC-S2-4 variance + AC-S2-5 two-walk tests.
**Remediation plan:** fix MUST-1, MUST-2, SHOULD-A4, cp1252 RED-first this session as part of P1 CLOSE; batch the rest as P1 follow-ons.

## P1 — PARTY CLOSE (SIGNED OFF ✅)
**Live evidence:** real gpt-5 on the 3-slice slice, 11,841 tokens (≠ offline marker), 26 typed components (other:13/reference_citation:7/slide:3/narration:3) + 9 provisional LOs, reconcile clean, ZERO fabrication, fail-probe citation captured for P2. Evidence: `_bmad-output/implementation-artifacts/evidence/p1-live-3slice-extraction-20260627T010737Z.json`.
**Remediation (RED-first):** MUST-1 per-row LO guard, MUST-2 payload-shape guard, A4 markdown-normalized groundedness advisory flag (`flagged_ungrounded`/`n_ungrounded`; 26/26 grounded on captured asset; fabricated-excerpt RED test fires), cp1252 fallback. 8 new tests green; brick suite 46 passed; ruff clean; lint-imports no new breaks.
**Verdicts:** T11 **SHIP-CONFIRMED**; Winston **GREEN-CLOSE**; Murat **GREEN-CLOSE**. Unanimous, no impasse.
**Carried P1 follow-ons (batched, non-blocking):** default-OFF byte-identity baseline assertion; multi-file/huge-doc context-budget chunking; DRY the two type-model validators (`source_type.py`); `TypedSource` dead-code disposition (relates to pre-existing C3); de-tautologize AC-S2-4 variance + AC-S2-5 two-walk tests.
**Pre-registered P2 entry conditions (Murat):** (1) the SHIPPED groundedness judge is the markdown-NORMALIZED one (strict substring is not the judge); (2) markdown-normalization is mandatory before P2's groundedness check runs against resolved-citation bodies; (3) P2 must prove BOTH resolve and fail paths on ONE live run (failed→no-DOI; resolved→DOI independently dereferences).

## Status
- Round 1 CLOSED green; **P1 SIGNED OFF** (T11 SHIP-CONFIRMED + Winston/Murat GREEN-CLOSE). Next: commit P1 checkpoint + push; open **R2** (P2 Texas pass-0 design green-light, add Texas + Irene) per `p2-texas-pass0-design-strawman-2026-06-26.md`.
- Next party rounds: **R2** = P2 Texas pass-0 DESIGN green-light (add Texas + Irene) — Tier-2 pack bump requires party consensus before dev. **R3** = P3 Irene pass-1 DESIGN. **R-close** per stage = party CLOSE on the live run.
