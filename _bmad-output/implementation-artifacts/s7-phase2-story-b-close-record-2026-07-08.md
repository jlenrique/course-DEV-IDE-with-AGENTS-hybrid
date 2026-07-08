# S7 Phase 2 Story B Close Record

Date: 2026-07-08
Branch: `dev/workbook-2026-07-06`
Story: B - Syllabus-derived module metadata proposal

## Scope

Story B closes deterministic syllabus extraction into proposal artifacts only:

- `.docx` syllabus extraction through `python-docx`
- `.doc` MHTML extraction through stdlib `email` and `html.parser`
- source-anchored course/module metadata proposal models
- frozen extracted-text fixtures for clone-stable tests
- live-safe proposal evidence for the two seeded course containers

No course-container mutation, folder rename, bucket scaffolding, remote fetch, LMS ingestion, or LLM extraction is in scope. Applying proposed PHS module slugs remains B-2 and is operator-gated.

## Shadow-Monitor Findings Reviewed

Active monitor file reviewed at close:
`_bmad-output/implementation-artifacts/claude-shadow-monitor-s7-phase2-2026-07-08.md`

- F-102 remains binding: commit by explicit Story B path list only; do not stage stray run dirs, goal files, prior monitor ledgers, or unrelated evidence.
- F-103 remains open as a Story A process backfill obligation. Story B does not close or waive it.
- F-104 and F-105 remain Story A review-lane items.
- F-106 is already accepted/closed by the Story C close record; Story B is now the active extraction/proposal item.

## Review And Remediation

BMAD code-review lanes:

- Blind Hunter raised proposal-quality issues around Confluence `Page:` slug noise, fallback title source locators, and missing-record shape guarding. All were patched and rechecked clean.
- Edge Case Hunter raised output path fencing, suspicious MHTML decode rejection, blank row anti-fabrication, and frozen/non-empty source anchors. All were patched and rechecked clean.
- Acceptance Auditor raised a close blocker that `verified` status was not bound to the Story B sentinel counts. The builder now requires explicit expected learning-objective counts and optional required-title sentinel; reduced-LO and wrong-title fixtures return `format_unsupported`. Recheck cleared Story B for close.

Party-mode close concurrence:

- John: CONCUR, conditioned on documenting F-103, F-102, and B-2 operator gate.
- Amelia: CONCUR, conditioned on explicit close record and explicit path staging.
- Murat: CONCUR, conditioned on close record, F-102 staging discipline, and F-103 remaining open for Story A.

## Validation

Latest local validation:

- `.venv\Scripts\ruff.exe check app/marcus/course_source scripts/utilities/extract_syllabus_module_metadata.py tests/marcus/course_source/test_syllabus_metadata.py` - pass
- `.venv\Scripts\python.exe -m pytest -n0 tests/marcus/course_source` - 40 passed
- `git diff --check` - pass
- `git status --short -- course-content/courses` - clean

Live-safe evidence:

- `hai_extraction_status=verified`
- `hai_course_learning_objectives=6`
- `hai_module_records=4`
- `hai_sentinel_bound_verified=pass`
- `hai_existing_slugs_aligned=pass`
- `hai_fields_anchored=pass`
- `phs_extraction_status=verified`
- `phs_course_title=Teaching and Learning Seminar`
- `phs_course_learning_objectives=12`
- `phs_module_records=15`
- `phs_sentinel_bound_verified=pass`
- `phs_no_mojibake_sentinel=pass`
- `phs_slug_divergence_explained=pass`
- `phs_slug_noise_removed=pass`
- `phs_fields_anchored=pass`
- `proposal_only_course_content_status_unchanged=pass`
- `proposal_only_course_content_status_clean=pass`

## Close Decision

Story B is complete and may be committed. B-2 remains a separate operator-gated action for applying any PHS slug proposals. Story A gate-trail backfill remains open and must not be lost.
