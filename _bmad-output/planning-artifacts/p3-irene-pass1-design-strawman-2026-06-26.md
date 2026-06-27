# P3 — Irene pass-1 Pedagogical Annotation Overlay — Design Strawman (for party round R3)

**Purpose:** Irene reads Texas's clean **universal-md** corpus (NOT raw source) and adds a pedagogy OVERLAY on load-bearing components — pointing at the extracted LOs, never re-authoring them. Charter §P3.

**Status:** STRAWMAN for R3 (Tier-2 → party consensus before dev). Irene leads; Winston (arch/DRY), Murat (test bar), Texas (upstream producer — confirm the overlay doesn't fight the lossless layer).

## Inputs already locked
- P2 universal-md output (R2 ratified): per-component record with front-matter {component_id, type, part, locator, source_ref, verbatim_excerpt, content_fingerprint, resolution_status, resolved_ref, normalization_version, doc_ordinal} + body `<<<CLEAN_BODY>>>`/`<<<PROVENANCE_ANNOTATION>>>`; `provisional_los[]` carried through with verbatim ids; `citation_resolutions` keyed by component_id.
- Irene's R2 required-shapes (her own pre-flight) — P2 guarantees them.

## Overlay schema (charter §3 Irene layer; additive, keyed by component_id)
`PedagogyAnnotation{component_id, lo_refs: list[str] (⊆ provisional_los ids), bloom: Literal[remember|understand|apply|analyze|evaluate|create], pedagogical_role: Literal[definition|motivation|worked_example|synthesis|assessment|practice], sequence:{teaches_after: list[component_id], prerequisite_concepts: list[str]}, assessment_link: component_id|None, teachable: bool, companion: component_id|None, transform_model, transform_version, generated_at}`.
Additive field on the enrichment result (e.g. `pedagogy_annotations: tuple[...]`); do NOT touch closed `TypedComponent`. SPOC-side LLM (Irene), NOT in the deterministic composer.

## Binding design rules (from R1/R2 + charter)
- **A2 one gate:** enrich the same frozen result / G0E gate; no new gate (or, if a distinct G0R-style Irene gate already exists from S3, reuse it — confirm at R3 whether P3 rides G0E enrich or the existing S3 refinement loop). NO new walk side-effect.
- **A6 DRY:** reuse S1 LO schema ids; reuse `_normalize_for_groundedness`; do NOT force-reuse figure_tokens (that's Pass-2 narration QA, downstream).
- **Referential integrity (Murat, hard):** every lo_ref ∈ provisional_los ids; assessment_link ∈ component ids; teaches_after ids exist. 3-surface enum red-reject on bloom + pedagogical_role.
- **teachable rule (Irene):** any component with resolution_status ungrounded/failed → teachable:false regardless of type.
- **Reads clean corpus:** P3 input MUST be P2's universal-md (front-matter present) — assert the layering holds (not raw source).
- **Determinism on sequencing:** teaches_after computed from numeric doc_ordinal (not lexical locator).

## Load-bearing types (annotate) vs skip (Irene R2)
- Annotate: slide, narration, quiz, workbook, assignment_instructions, discussion_forum, motion_script_storyboard.
- Skip: reference_citation (evidence — only pointed-at via companion), other (scaffolding), learning_objective (targets, not annotated).

## Live test plan (Murat M-bar; reuse P2 assets, cheap)
- Method-level first contact: annotate ONE component live (a slide) with a resolving lo_ref BEFORE the full overlay pass.
- Full pass on the 3-slice slice (6 annotatable: 3 slide + 3 narration): assert referential integrity (lo_refs ⊆ los; teaches_after exist), enum membership, coverage (load-bearing annotated, non-load-bearing skipped), input-is-P2-md, ungrounded→teachable:false.
- Cache-busted + receipt-bearing (real model id, non-zero spend); deterministic judge (refs resolve / enums valid), first-run-stands; M5-style: inject a fabricated lo_ref → asserted-red.

## Open questions for R3
1. Does P3 ride the G0E enrich (A2) OR the existing S3 Irene refinement loop / a G0R gate? (Confirm against the as-built S3 wiring — irene_refinement_wiring.py.) AVOID re-authoring overlap with S3.
2. Is `companion` (citation↔slide) in v1 scope or deferred?
3. assessment_link: the 3-slice slice has zero quiz components → contract present but unexercised. Add a quiz component to the slice to exercise it, or accept unexercised-with-note?
