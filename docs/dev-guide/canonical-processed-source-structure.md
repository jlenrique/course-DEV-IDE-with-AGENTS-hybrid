# Canonical processed-source structure (Mine 4A)

**Schema version:** 0.1  
**Authority:** Phase-2 six-mine greenlight (Amelia defaults) + this module.

## Lesson leaf (curated corpus)

Required directories (all must exist):

- `slides/`
- `references/`
- `assessments/`

Optional companions (not required for PASS): `urls.txt`, `README.md`.

## Run directory (processed trial artifacts)

Required files:

- `bundle/extracted.md`
- `g0-enrichment.json`

## Enrichment `kind` shape-pin (gates Mine 5 Drill)

Every `typed_components[]` entry in `g0-enrichment.json` MUST carry:

- `source_type` ∈ closed SourceType set (existing)
- `kind` ∈ `AssetKind` closed set, reconciled from `source_type` via
  `SOURCE_TYPE_TO_ASSET_KIND` / `ASSET_KIND_RECONCILIATION`

Missing or disagreeing `kind` → structured validation failure (not partial success).

## Closed AssetKind values

'reading', 'lecture', 'lab', 'assignment', 'assessment', 'discussion_prompt', 'syllabus', 'project_artifact'

## Closed source_type values (reference)

assignment_instructions, discussion_forum, exercise_lab, motion_script_storyboard, narration, quiz, reference_citation, rubric, slide, workbook + `other` escape hatch.

## OUT of Mine 4A

Automated normalize writeback to typed folders; historical backfill; cloud storage;
Drill projector (Mine 5); workbook prose (Mine 6).
