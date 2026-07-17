---
id: 40-2
epic: 40
status: proposed   # NEW operator requirement 2026-07-17; needs party green-light; queued behind the Epic-42 goal (do NOT derail Epic 42)
depends_on: 40-1   # extends the cover producer (placeholder hero → selected real art)
gate_mode: single-gate   # candidate; party to confirm
anchor_provenance: HEAD 482cf78a
---

# Story 40.2: Workbook cover art — select the most thematically resonant image from a curated trove

Status: proposed  # operator requirement 2026-07-17; captured, awaiting green-light

## Story

As the learner opening a workbook,
I want the cover to carry a real, thematically resonant illustration chosen from a curated art trove — not a text placeholder —
so that the workbook has an authentic, on-theme front door, without the cost/latency of live Gamma generation.

## Operator requirement (verbatim intent, 2026-07-17)

> When creating a cover page for a workbook, the responsible agent chooses cover art from the **most thematically resonant** art available in the trove at `C:\Users\juanl\Box\OIIE\TEJAL\WORKBOOK cover art`. The app must have a **settings variable** specifying the location of the workbook cover-art trove.

## The trove (witnessed 2026-07-17)

- Path: `C:\Users\juanl\Box\OIIE\TEJAL\WORKBOOK cover art` (a Box-desktop-synced LOCAL directory — disk files, per the corpus-directory-scope convention: local path ⇒ disk-file access, not a live fetch).
- Contents: **23 files (22 PNG + 1 JPG)**, healthcare / physician-leadership themed (TEJAL SME).
- **Descriptive filenames encode each image's theme** — e.g. `Administrative_waste_breakdown__six_categories…png`, `Digital_Front_Door_journey__five_connected_stages…png`, `Root_causes_of_clinician_burnout_as_a_hub…png`, `single_figure_at_center_of_complex_organizational_maze…png`, `physician_in_white_coat_at_round_table_with_colleagues…jpg`. These names are the primary thematic-match signal (no separate metadata needed for v1).

## Guide review REQUIRED before dev (operator directive 2026-07-17 — [[feedback_review_guides_before_gates_agents_services]])

Before building, review: `docs/dev-guide/course-source-asset-record-boundary.md` (this reads EXTERNAL local files — the asset-record boundary governs how external assets enter the run), the workbook-producer substrate (Story 40-1 code map), the settings convention (how app settings/env vars are defined + surfaced — 42-3's `RUN_SETTINGS_TOGGLES`), and `docs/admin-guide.md` on asset hosting / `.env` key management. This is NOT a gate/agent/service, but it IS a new app setting + an external-asset intake, so the boundary + settings conventions apply.

## Proposed acceptance criteria (party to ratify)

1. **Trove-location setting.** A new app setting (env var, e.g. `MARCUS_WORKBOOK_COVER_ART_TROVE`, resolved through the same config path the other MARCUS_* settings use) specifies the trove directory. Default MAY point at the operator's Box path but MUST be overridable; absent/unset degrades honestly (fall back to 40-1's placeholder hero, never a fabricated image). Decide with the party whether this ALSO surfaces as a 17th entry in 42-3's `RUN_SETTINGS_TOGGLES` standing readout (it would trip 42-3's keep-in-sync guard — by design; add it there if the operator wants it run-visible) or stays an app-global config only.
2. **Thematic-resonance selection.** The responsible agent (the cover producer / a CD-style selector) picks the MOST thematically resonant image from the trove by matching the lesson theme / LO statements / section titles (the same signals 40-1's art-brief already derives) against the trove filenames (descriptive names are the v1 signal). Deterministic tie-break + provenance record (which image chosen, why, match score/rationale) written to the cover receipt/art-brief sidecar. A live-LLM selection is acceptable per the no-mocks directive if a semantic match is warranted; a deterministic keyword-overlap selector is the cheaper first cut — party to choose.
3. **Real image embedded in the cover (MD + DOCX), replacing the placeholder.** The chosen image is embedded in the cover hero slot — this SUPERSEDES 40-1's text placeholder. NOTE 40-1's fence: `_render_docx_body` skips `![…](…)` image-syntax lines, so DOCX image embedding needs real handling (python-docx `add_picture` or equivalent), not markdown image syntax. MD carries the image; DOCX embeds it; B8 byte-determinism preserved (same trove + same inputs ⇒ same image ⇒ byte-identical). Honest degrade to the 40-1 placeholder when the trove is absent/unreadable or no image is a reasonable match.
4. **Provenance + trust.** The cover receipt records: trove path, chosen filename, selection method + rationale, and a digest of the chosen image bytes (so a later audit can verify the shipped cover matches the selection). Never a fabricated final-art claim; the selection is honest ("selected from curated trove," not "generated").
5. **No Gamma dependency.** This is the SELECT-from-trove path — no Gamma call. (Gamma generation stays the separate deferred non-goal; this is the pragmatic curated alternative.)

## Scope fences (proposed)

- **NO Gamma generation** (this is trove-selection).
- **NO fabricated art claim** — honest "selected from curated trove"; honest degrade to placeholder when trove absent.
- **NO copying the whole trove into the repo** — read from the configured external path at produce time; embed only the chosen image into the deliverable.
- Reuse 40-1's art-brief theme derivation; do NOT re-derive the lesson theme separately.
- Respect the asset-record boundary (external asset intake) per the dev guide.

## Intersections

- **40-1** (cover producer): this replaces the placeholder hero with a real selected image + adds DOCX image embedding (which 40-1 deferred).
- **42-3** (settings readout): the trove-location setting is a candidate 17th `RUN_SETTINGS_TOGGLES` entry (party decides run-visible vs app-global).
- **Cross-SME note:** the current trove is TEJAL-specific (healthcare). A cross-SME workbook would need its own trove or a generic fallback — note for the Phase-2 cross-SME lane; v1 may be TEJAL-scoped.

## References

- Operator requirement 2026-07-17 (this session).
- `_bmad-output/implementation-artifacts/40-1-cover-placeholder-hero-toc-provenance.md` (the cover producer this extends).
- `docs/dev-guide/course-source-asset-record-boundary.md`, `docs/admin-guide.md` (asset/settings conventions — REQUIRED pre-dev review).
- Trove: `C:\Users\juanl\Box\OIIE\TEJAL\WORKBOOK cover art` (23 files, witnessed 2026-07-17).

## Status note

**PROPOSED — captured 2026-07-17, needs party green-light. NOT started (Epic 42 completion is the active goal + Stop-hook condition).** Queued as an Epic-40 follow-on. Also filed in `deferred-inventory.md` §Named-But-Not-Filed.
