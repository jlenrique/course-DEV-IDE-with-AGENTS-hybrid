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

## R2 Phase A — SYNTHESIZED DESIGN (Texas DD1–DD8 + Irene required-shapes + reconciliation)
Texas proved the critical path LIVE this session (scite `search_literature(dois=["10.1001/jama.2019.13978"])` → real JAMA paper dereferenced; fail-probe `doi:10.9999/jihs.2099.deadbeef` → `total:0` not-in-index, no fabrication).

**A5 RESOLVED → scite-only for v1; drop PubMed.** File `p2-pubmed-adapter-v2` in deferred-inventory (trigger: scite index-coverage gap marks real biomedical DOIs + bare-PubMed-URL citations `failed`; PubMed offers bare-id→metadata scite's search-index lacks).

**Buildable design:**
- **DD1 (seam correction — overrides strawman A1):** citation resolution routes through the IN-PROCESS `skills/bmad-agent-texas/scripts/retrieval/dispatcher.py::dispatch(RetrievalIntent(kind="direct_ref", ...))` (the OAuth-proven SciteProvider path `research_wiring` already uses) — NOT `retrieval_dispatch.py::dispatch_retrieval` (that's a subprocess shell-out for locator bundles; leave untouched).
- **DD2 module layout:** new Texas-side `skills/bmad-agent-texas/scripts/pass0/`: `citation_resolver.py`, `universal_md.py`, `universal_markdown_preamble.py` (EXPORTED `emit_front_matter(fields)->str`, shared with run_wrangler + workbook). Thin brick = EXTEND `app/marcus/orchestrator/g0_enrichment_wiring.py` via late-import (no new file/node). Dep arrow app/marcus→texas only; verify `lint-imports`.
- **DD3 attach (A2):** inside `build_enrichment_result(...)`, AFTER `flag_ungrounded_components`, BEFORE `G0EnrichmentResult(...)` construction → call `pass0.resolve_citations(typed, source_by_id, dispatch_live=...)`. Rides existing g0-enrichment node + existing fingerprint cache + existing G0E gate (two-walk parity inherited; no new side-effect). G0E card gains a resolution column.
- **DD4 schema (additive):** new `CitationResolution{component_id, doi|None, resolution_status: resolved|failed|ungrounded, resolved_ref:{title,doi,access_url,journal?,authors?,year?}|None, reason(no_doi_in_excerpt|not_in_index|dispatch_error), resolver_provider:"scite", normalization_version:"tex-norm-v1"}` + `citation_resolutions: tuple[...]` on `G0EnrichmentResult`. Do NOT add fields to the closed `TypedComponent`.
- **DD5 universal-md front-matter:** `emit_front_matter` writes component_id, type, part, locator, source_ref, verbatim_excerpt, content_fingerprint(sha256), extraction_provenance, resolution_status, resolved_ref, normalization_version + **doc_ordinal (Irene #3)**. Body = **demarcated** `<<<CLEAN_BODY>>>` (normalized verbatim span P3/P5 consume) + `<<<PROVENANCE_ANNOTATION>>>` (Irene #5) — NO paraphrase. DRY (A6): reuse `learning_objective.SourceRef`, `g0_enrichment` hashing, `retrieval/normalize.py`.
- **DD6 A4 RED (HARD):** reuse `g0_enrichment_wiring._normalize_for_groundedness` (blockquote-strip + `\$`→`$` + whitespace); at content_fingerprint freeze `verbatim_excerpt ⊆ md-normalized(parent_source)` else `resolution_status: ungrounded`/hard-fail — never a silent sha. Scope = excerpt-vs-source ONLY (never resolved-metadata-vs-source).
- **DD7 cache:** no separate cache — resolution serializes into the existing `<run_dir>/g0-enrichment-cache/<fp>.json`. One fingerprint, one freeze, replay-deterministic.
- **DD8 SciteProvider fix:** DOI-dereference via `search_literature({"dois":[doi],"limit":1})` (no term); `paper_metadata` tool is unverified — do not use.

**Irene required-shapes folded in (P2 must guarantee):** (1) stable `component_id` 1:1 with P1 (no silent re-split; emit P1→P2 map if ever split); (2) `provisional_los[]` carried through P2 untouched with verbatim ids (P3 validates `lo_refs ⊆ {provisional_los ids}`); (3) numeric `doc_ordinal` per component (string locator lexically mis-sorts); (4) `type` surfaced verbatim; (5) `clean_body` vs `provenance_annotation` demarcation; (6) `resolution_status`/groundedness readable (ungrounded/failed → P3 sets `teachable:false`); (7) co-locator linkage citation↔slide via shared locator/doc_ordinal.
**P3 load-bearing types (for P3 spec):** annotate slide/narration/quiz/workbook/assignment_instructions/discussion_forum/motion_script_storyboard; skip reference_citation/other/learning_objective.

**Live test plan (method-level, Murat M4):** M4a resolve JAMA DOI live (DONE this session — receipt: title echo) → `resolved`; M4b fail-probe → `failed`/`resolved_ref None`/`not_in_index` (DONE); M5 inject hash mismatch → hard-fail/ungrounded; lossless pin (front-matter fingerprint == frozen P1 excerpt sha; body byte-equals source span post tex-norm-v1); cache-busted + receipt-bearing + first-run-stands + deterministic judge.

**Open items (fix-forward, non-blocking):** DD8 SciteProvider reroute; disk materialization deferred to P4 (P2 stays in-graph).

## Resolved open questions
1. A5 → scite-only v1 (live-proven). 2. Attach = inside build_enrichment_result (DD3). 3. In-graph at P2; disk = P4. 4. tex-norm-v1 reuses `_normalize_for_groundedness` + `retrieval/normalize.py`.
