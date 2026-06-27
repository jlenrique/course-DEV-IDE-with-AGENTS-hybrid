# P2 — Texas pass-0 Design Strawman (for party round R2)

**Purpose:** turn the frozen P1 `G0EnrichmentResult` (typed components) into a clean, provenance-anchored **universal-md** corpus, and **resolve citations live** (resolved|failed, never fabricated). Lossless; no paraphrase at this layer.

**Status:** STRAWMAN for R2 party green-light (Tier-2 pack bump → party consensus required BEFORE dev). Authority once ratified: appended to `p5-arc-party-record-2026-06-26.md`.

## Binding inputs already decided (party R1)
- **A1 (placement):** resolution/normalization LOGIC lives Texas-side, sibling to `skills/bmad-agent-texas/scripts/retrieval/`, routing through `app/specialists/texas/retrieval_dispatch.py::dispatch_retrieval` + `TexasRow` + `retrieval/normalize.py`. A THIN runner brick under `app/marcus/orchestrator/` calls it (mirror `research_wiring.py` Option-A). One-way dep arrow; verify `lint-imports`.
- **A2 (one gate):** ENRICH the frozen `G0EnrichmentResult` feeding the EXISTING G0E gate. No new gate code, no new walk side-effect.
- **A3 (freeze):** P2 live resolution frozen in a fingerprint-keyed cache (mirror `run_g0_enrichment`'s `<run_dir>/...-cache/<fp>.json`); dispatch once, frozen `resolved|failed` replay-deterministic.
- **A4 (RED groundedness, HARD):** before freezing `content_fingerprint`, verify `verbatim_excerpt` ⊆ parent-source bytes. **Markdown-normalize first** (P1 live finding F1: strict substring false-rejects 27% of faithful extractions on `\$`/`> `/whitespace). Non-grounded → hard fail OR explicit `resolution_status: ungrounded`, never a silent sha.
- **A5 (PubMed gap):** DECISION FOR R2 — (a) add a `pubmed` `RetrievalAdapter`, OR (b) resolve DOIs via `scite` and drop PubMed from P2 v1. Strawman recommends **(b)** for v1 (scite is live/OAuth-proven; fewer moving parts) — Texas to confirm scite can dereference a bare DOI→metadata.
- **A6 (DRY):** reuse S1 LO schema (`learning_objective.py`), `g0_enrichment` hashing primitives, `retrieval/normalize.py`. Do NOT force-reuse `figure_tokens`/`collateral_spec`.
- **Shared front-matter writer:** slim `universal_markdown_preamble.emit_front_matter(...)` in Texas's tree, EXPORTED, consumed by both `run_wrangler` and the workbook producer (one front-matter contract for P5).

## Universal-md shape (charter §3, Texas layer only at P2)
Front-matter: `component_id, type, part, locator, source_ref, verbatim_excerpt, content_fingerprint(sha256), extraction_provenance, resolution_status(resolved|unresolved|failed|ungrounded), resolved_ref, normalization_version`. Body = clean normalized text with verbatim quoted + annotation around it. (Irene's pedagogy overlay is P3, not P2.)

## Live test plan (Murat M1–M5; cost-bounded, reuse P1 asset)
Input = the P1 captured components for the 3-slice slice (7 reference_citation rows incl. the fail-probe `doi:10.9999/jihs.2099.deadbeef`).
- **M4 method-level first contact:** resolve ONE real citation live (e.g. JAMA `doi:10.1001/jama.2019.13978`) via the chosen seam, confirm the DOI INDEPENDENTLY dereferences, BEFORE building the batch normalizer.
- **Then prove ONE fail:** the fail-probe → `resolution_status: failed`, `resolved_ref is None` (no fabricated DOI).
- **A4 RED executable:** inject a hash/substring mismatch → assert hard-fail (M5).
- **Lossless:** front-matter `content_fingerprint` matches frozen P1 excerpt sha; body verbatim == source.
- Cache-busted + receipt-bearing; first-run-stands; deterministic judge (DOI dereferences / no-DOI-on-failed / sha match), not LLM eyeball.

## Open questions for R2 (Texas leads; Winston/Irene/Murat)
1. A5 (a) vs (b) — scite-only-for-v1 vs add pubmed adapter. Confirm scite dereferences a bare DOI.
2. Where exactly does the thin runner brick attach so it enriches the frozen G0EnrichmentResult without minting a new gate/side-effect (A2)? (Likely inside/after `run_g0_enrichment`, before G0E freeze.)
3. Does universal-md materialize to DISK at P2, or stay in-graph until P4 materializer? (Charter: manifest=ledger always; materialization is P4's operator-directed projection. Strawman: P2 produces the enriched in-graph representation + front-matter; DISK writing is P4.)
4. `normalization_version` = `tex-norm-v1`; what canonical-normalization rules (whitespace, markdown unescape) — reuse `retrieval/normalize.py`?
