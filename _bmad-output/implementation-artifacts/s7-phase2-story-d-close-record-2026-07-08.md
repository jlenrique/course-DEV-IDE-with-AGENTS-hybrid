# S7 Phase 2 Story D Close Record - Lesson Planning Input Bundles

Date: 2026-07-08
Branch: `dev/workbook-2026-07-06`
Story: S7 Phase 2 D - lesson-planning input bundle substrate

## Scope Closed

Story D added a course-source-scoped `LessonPlanningInputBundle` substrate and CLI for downstream lesson-planning consumers without touching production lesson-plan trigger paths or course containers.

Implemented surface:

- `app/marcus/course_source/input_bundle.py`
- `scripts/utilities/build_lesson_planning_input_bundle.py`
- `tests/marcus/course_source/test_input_bundle.py`
- package exports in `app/marcus/course_source/__init__.py`
- live evidence in `_bmad-output/implementation-artifacts/evidence/s7p2-story-d-input-bundles-20260708T111746/`

The bundle carries source purpose and source availability through from Story A, consumes Story B verified module metadata proposals, emits Story C canonical requirement-gap asset records, includes scoped manifest/gap data, records operator focus, carries the production `ComponentSelection` shape, and explicitly marks styleguide fallback where no SME-specific guide is available.

## Product Boundary

PHS 620 and HAI 510 remain evidence fixtures. Story D is product-scoped to the Marcus-SPOC runtime orchestrator course-source substrate and does not promote either course's current proofing/container state into a design target.

The implementation does not edit or stage the Story D forbidden/trigger paths:

- `app/marcus/lesson_plan/composition.py`
- `app/models/state/component_selection.py`
- `app/marcus/lesson_plan/bundle_catalog.py`
- `app/marcus/cli/front_door.py`
- `state/config/pipeline-manifest.yaml`

## Live Validation

- `.venv\Scripts\ruff.exe check app/marcus/course_source/input_bundle.py app/marcus/course_source/__init__.py scripts/utilities/build_lesson_planning_input_bundle.py tests/marcus/course_source/test_input_bundle.py` - passed
- `.venv\Scripts\python.exe -m pytest -n0 tests/marcus/course_source/test_input_bundle.py` - 11 passed
- `.venv\Scripts\python.exe -m pytest -n0 tests/marcus/course_source` - 51 passed

Refreshed evidence assertions:

- `hai_source_purpose_new_build=pass`
- `phs_source_purpose_enhancement=pass`
- `hai_module_bound=pass`
- `phs_module_bound=pass`
- `hai_gap_count=pass`
- `phs_gap_count=pass`
- `hai_asset_record_count=pass`
- `phs_asset_record_count=pass`
- `hai_required_gap_records=pass`
- `phs_required_gap_records=pass`
- `hai_scoped_gap_summary=pass`
- `phs_scoped_gap_summary=pass`
- `hai_styleguide_fallback=pass`
- `phs_styleguide_fallback=pass`
- `component_selection_contract=pass`
- `course_content_status_clean=pass`

## Review Lanes

Blind Hunter recheck: `CONCUR`.

- Prior findings resolved: output fence, verified-proposal requirement, scoped gap-summary recompute, and public load/write round-trip.
- Validation checked: focused Story D pytest passed, refreshed evidence assertions passed, no trigger-path edits found.

Edge Case Hunter recheck: `CONCUR`.

- Prior Story D findings resolved.
- No material new blocker found in `input_bundle.py`, the builder script, exports, refreshed evidence, or the added public load/write round-trip test.

Acceptance Auditor recheck: Story D can close.

- D-D1 loader finding resolved by `load_input_bundle(path: Path) -> LessonPlanningInputBundle`.
- Loader is exported from both `app.marcus.course_source.input_bundle` and the package root.
- Public write/load round-trip is covered by `test_bundle_public_write_load_round_trip`.

## Party Mode Close

BMAD party-mode close round:

- John: `CONCUR` - product scope accepted; HAI/PHS remain fixtures; loader fix and validation are green.
- Amelia: `CONCUR` - implementation/boundary accepted; course-source scope and trigger/container fences hold.
- Murat: `CONCUR` - quality gate satisfied; loader, round-trip coverage, scoped bundle tests, and live evidence are sufficient.

Story D is considered accomplished and validated by the fully spawned BMAD party-mode team.

## Shadow Monitor Disposition

Active Claude shadow monitor reviewed at the major Story D design/decision points. POLL-005 reports no Story D product-code objection.

Carry-forward findings:

- F-102 remains binding: stage explicit path lists only; do not absorb unrelated strays.
- F-103 remains open: Story A still needs a visible process/gate-trail backfill or explicit waiver before final Phase-2 process close.

Story D does not claim F-103 resolved.

## Next Arc Note

The selection-edge spine `lesson-plan-directs-production-collateral-to-selection-edge` is filed as the immediate next arc. S8 prose work should interleave with that spine per operator priority rather than being treated as blocked behind it.
