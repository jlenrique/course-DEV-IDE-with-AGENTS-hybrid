# Course Source Asset Record Boundary

Story S7 Phase-2 C defines `CanonicalAssetRecord` as an evidence-side shape.
Ingestion tags raw source observations; enrichment may later canonicalize them.
The record does not generate or project artifacts.

## Source vs Requirement

A syllabus row is requirement evidence. It can prove that a lecture, reading,
assignment, or discussion prompt is expected, but it does not prove that the
production content exists. Records derived from syllabus rows therefore use
`missing`, `required_gap`, or `inferred`.

`source_grounded` is reserved for records with content-bearing source refs. A
requirement ref alone cannot satisfy that status.

Lesson-objective-derived records enter as `inferred` or `needs_sme_review`.
They do not become `source_grounded` until content source refs support them.

## Vocabulary Reconciliation

Existing source-type vocabulary maps into the Story C asset-kind vocabulary as:

| Existing source type | Canonical asset kind |
| --- | --- |
| `assignment_instructions` | `assignment` |
| `discussion_forum` | `discussion_prompt` |
| `exercise_lab` | `lab` |
| `reference_citation` | `reading` |

The initial asset-kind enum uses `lecture`. A later governance bump may rename or
add `lecture_material` if downstream consumers need that distinction.
