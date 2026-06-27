# P4 — Deterministic Materializer + Marcus Gate Knob — Design Strawman (for party round R4)

**Purpose:** A PURE deterministic writer (ZERO LLM) that projects the enriched in-graph corpus (P1 typed components + P2 universal-md front-matter/citation resolution + P3 pedagogy overlay) to disk as universal-md files, idempotently, behind a Marcus-owned one-gate "materialize sub-knob". The manifest is an ALWAYS-complete in-graph LEDGER; materialization is an operator-directed PROJECTION of a subset + a coverage receipt. Charter §P4 / §pipeline step 4–5.

**Status:** STRAWMAN for R4 (party consensus before dev). Winston leads (pure-writer is his line); Marcus (gate knob + manifest-as-ledger + coverage receipt owner); Murat (determinism/idempotency test bar); Texas (universal-md emit contract — confirm P4's disk writer reuses his record builder losslessly).

## Inputs already locked (verified as-built)
- `G0EnrichmentResult` (`app/marcus/lesson_plan/g0_enrichment.py`) carries: `typed_components`, `provisional_los`, `citation_resolutions` (P2), `pedagogy_annotations` (P3), reconcile, fingerprint, model_id.
- Texas's `universal_md.build_component_record(...)` (`skills/bmad-agent-texas/scripts/pass0/universal_md.py:60-135`) builds the universal-md RECORD in-memory (front-matter dict + `<<<CLEAN_BODY>>>` body) — **NO disk emit today**. `emit_front_matter` is a CLOSED contract (`universal_markdown_preamble.py:74-79`, RED on foreign keys).
- `ComponentSelection` (`app/models/state/component_selection.py`) = canonical deck/motion/workbook selection; rides RunState; participates in the two-part composition digest.

## What P4 builds (proposed)
1. **`materialize_corpus(...)` pure writer** — new module `app/marcus/lesson_plan/corpus_materializer.py` (SPOC-side, sibling to g0_enrichment.py / pedagogy_annotation.py). Pure function `(result, selection_filter, out_root) -> MaterializationReceipt`. Reuses `build_component_record` for each component (NO re-derivation); the ONLY new behavior is the disk-IO seam: write each record to `<out_root>/corpus/<part-or-type>/<component_id>.md` with the full front-matter (Texas P2 + Irene P3 overlay merged) + clean body.
2. **Idempotency** by `(component_id, content_fingerprint, transform_version)` — same input → byte-identical files; re-run skips unchanged files (or writes identical bytes). A content-hash sidecar / index makes the skip decision deterministic.
3. **Manifest-as-ledger + coverage receipt** — `MaterializationReceipt{materialized: tuple[component_id], retained_in_graph: tuple[component_id], n_materialized, n_total, mode, filter}` ("materialized 47 of 188; 141 retained in-graph"). EVERY component is accounted for (materialized ∪ retained = all); un-materialized ≠ unaccounted.
4. **Marcus one-gate materialize sub-knob** — at the EXISTING G0E (or the existing G0R) gate, a Marcus-SPOC decision-card knob: `materialize_mode ∈ {by-type, by-Part, named-subset, none}` (+ optional subset filter). NO new gate code (A2 lockstep). Default = `none` (regression firewall; deck-default byte-identical). The knob directs the PROJECTION; the ledger is always complete regardless.

## Binding design rules (from R1/R2/R3 + charter)
- **ZERO LLM in the writer** (charter §determinism; Winston's line). P4 is replay-safe pure deterministic.
- **A2 one gate:** the materialize knob rides an EXISTING gate (G0E or G0R); mint NO new gate code, NO new walk side-effect. (Confirm at R4 which gate the knob attaches to — G0E enrich vs G0R ratify; the materialize decision logically follows enrichment + ratification.)
- **A6 / DRY (hard):** P4 MUST NOT reimplement `run_wrangler` bundle-write (source extraction, different tree `bundle/`) or `workbook_producer` DOCX emit. P4 writes `corpus/` universal-md only. Reuse `build_component_record`; add only the IO seam.
- **Provenance is RED (charter):** every materialized file carries `{locator + verbatim-excerpt sha (content_fingerprint)}`; absent/mismatched at write time = hard fail. A transform is never a silent rewrite (verbatim quoted with annotation around it — already the P2 body contract).
- **Completeness vs materialization:** the ledger accounts for ALL components; materialization is optional projection + coverage receipt.
- **Idempotency / determinism:** same `(result fingerprint, selection_filter, transform_version)` → byte-identical corpus tree.

## Live test plan (Murat bar; reuse P1/P2/P3 assets, cheap, FOREGROUND)
- Method-level first contact: materialize ONE component to disk; assert the file's front-matter content_fingerprint matches the frozen in-graph value (provenance-RED holds) before the full projection.
- Full projection on the 3-slice slice: assert (a) byte-identical re-run (determinism); (b) coverage receipt math (materialized + retained = total, no double-count); (c) each materialized file's fingerprint ties back to the frozen manifest; (d) provenance-RED fires on an injected hash-mismatch (M5-style); (e) `none` mode writes nothing + deck-default byte-identical (regression firewall); (f) by-type / by-Part / named-subset each project exactly the intended subset.
- NO live LLM needed for P4 (pure writer) — but the corpus it writes must be the LIVE-enriched P3 output (so P4's live test rides P3's Stage-2 enriched result, not an offline fixture).

## Open questions for R4
1. **Gate attach:** does the materialize knob ride G0E (enrich) or G0R (ratify)? (Materialize logically AFTER ratification, but G0R is the S3 LO loop — confirm against `marcus_spoc.py` gate handling whether a knob can attach there without a new gate code.)
2. **Out-root + tree shape:** `<run_dir>/corpus/<Part>/<component_id>.md` vs `<...>/<type>/<component_id>.md` — by-Part or by-type as the on-disk default? (The `mode` knob can override; the question is the default tree.)
3. **Is P4 needed for the goal's terminal DoD at all,** or can P5 consume the in-graph enriched result directly (in-memory) and P4 (disk projection) be a thin convenience the final bundle doesn't strictly require? (Charter says P4 before P5; the original /goal says "do P4/P5 if the posting needs them, else defer cleanly." R4 should rule on whether the Descript bundle needs disk-materialized corpus or can ride the in-graph result — this scopes P5.)
4. **Index file:** does P4 emit a top-level `corpus/INDEX.md` / `manifest.json` ledger artifact (the always-complete ledger on disk), or is the ledger purely the in-memory `MaterializationReceipt`?
