# S7 Phase 2 Story A Close Backfill - Registry, Manifest Scan, and Broad-Root Guard

Date: 2026-07-08
Branch: `dev/workbook-2026-07-06`
Original Story A commit: `7174b366` (`feat(course-source): add Story A registry and source manifests`)
Backfill patch scope: this record plus the direct-adapter invalid-input and ignored-source gap regressions

## Backfill Status

This is a late process-backfill record. It does not claim that Story A's SOP/review/party close gates were visible in the repo before `7174b366` landed. The Claude shadow monitor finding F-103 was correct: Story A advanced without a visible on-time gate trail.

The purpose of this record is to make the missing trail visible now, run independent review on the current committed implementation, remediate material findings, and document the remaining process caveat honestly.

## Scope Reviewed

Story A implemented:

- broad-root refusal at `app/composers/section_02a/composer.py::_walk_corpus_files`
- fail-before-spend guard path in `app/composers/section_02a/cli_adapter.py`
- belt-and-suspenders `trial.py` input guard before env loading
- sibling package `app/marcus/course_source/`
- deterministic manifest scan, gap ledger, source manifest snapshots, and drift checker
- seed course `source_purpose` and `source_availability` declarations for HAI 510 and PHS 620
- live-safe Story A evidence under `_bmad-output/implementation-artifacts/evidence/s7p2-two-course-scan-20260708T101917Z/`

## Validation

Current validation after late review remediation:

- `.venv\Scripts\python.exe -m pytest -n0 tests/marcus/course_source tests/composers/section_02a/test_broad_root_guard.py tests/integration/marcus/cli/test_trial_course_root_guard.py` - 60 passed
- `.venv\Scripts\ruff.exe check app/marcus/course_source app/composers/section_02a/composer.py app/composers/section_02a/cli_adapter.py app/marcus/cli/trial.py tests/marcus/course_source tests/composers/section_02a/test_broad_root_guard.py tests/integration/marcus/cli/test_trial_course_root_guard.py` - passed
- `.venv\Scripts\python.exe -m scripts.utilities.check_course_source_manifests course-content/courses/aziz-nazha-hai-510-generative-ai-in-healthcare course-content/courses/juan-leon-phs-620-teaching-learning-seminar` - ok/ok

Committed Story A evidence reviewed:

- broad course-root real-entry refusal: `broad-root-refusal.log`
- lesson-leaf negative control: `negative-control.log`
- two-course scan assertions: `scripted-assertions.log`
- no app-side PHS/HAI slug literal evidence: `app-course-literal-grep.log`
- per-course manifest and gap-ledger YAML for HAI 510 and PHS 620

## Late Review Findings and Remediation

Blind Hunter: `CONCUR`.

- No material product/code blockers found.
- F-104 is a nit, not a blocker: raw guard text names `lesson_corpus_leaf` and fails before spend, but does not name the brief.
- F-105 accepted after review: HAI/PHS `source_purpose` and `source_availability` declarations match the binding operator clarification; env loading moved below input guards is correct.

Acceptance Auditor: Story A can be accepted via late backfill.

- F-103 remains a real process defect in timing, but this review can serve as late remediation evidence.
- F-104 is a non-blocking nit.
- F-105 ratified.
- Auditor also verified module-root refusal behavior during the late audit; the original committed evidence bundle does not include a separate module-root real-entry refusal log, so this record states that distinction explicitly.

Edge Case Hunter: initial two findings, both remediated.

1. `compose_and_write()` could construct the default chat model before rejecting missing or non-directory corpus inputs.
   - Fixed in `app/composers/section_02a/cli_adapter.py` by checking existence and directory shape before model construction.
   - Regression tests added for missing-path and file-path inputs.
2. Ignored local files with `source_role: source` could suppress the "no local production source" gap.
   - Fixed in `app/marcus/course_source/manifest_scan.py` by excluding `git_status: ignored` entries from the `real_sources` check.
   - Regression test added for ignored source-role entries.

Edge recheck: `CONCUR`; both prior findings resolved and no material blocker remains.

## Shadow Monitor Disposition

- F-102 remains binding staging hygiene.
- F-103 is now backfilled in-repo by this record plus late review/remediation. The timing defect remains part of the historical record and is not erased.
- F-104 is dispositioned as non-blocking and carried as a possible wording polish.
- F-105 is explicitly ratified by late review.

## Product Boundary

The implementation is for the Marcus-SPOC runtime orchestrator's course-source substrate. HAI 510 and PHS 620 remain evidence fixtures. The source declarations preserve the operator clarification:

- HAI 510 is a new-build course whose real source content will be lecture videos, slides, and readings when supplied.
- PHS 620 is an enhancement course whose real source content will come through authorized Confluence and Canvas access.
- Syllabi are reference/example sources and never prove source completeness.

Story A does not perform remote ingestion and does not require the real HAI/PHS source content.
