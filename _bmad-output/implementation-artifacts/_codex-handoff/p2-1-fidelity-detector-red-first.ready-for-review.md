# P2-1 Codex Handoff - Ready for Review

Story: `p2-1-fidelity-detector-red-first`
Status: ready for Claude T11 review
Branch observed: `fidelity-perception-arc-2026-06-19`

## Implementation Summary

- Added the shared consumed perception contract at `app/models/perception/perception_artifact.py` with legacy-identical fields plus `coverage`, Pydantic v2 `extra="forbid"`, and assignment validation.
- Added pure deterministic Quinn-R detector logic in `app/specialists/quinn_r/fidelity_detector.py`.
- Added `FidelityError` through the existing dual-base `_content_error` factory and wired `detect_fidelity` into `run_g5_checks`.
- Added `perception_artifacts` to Quinn-R consumed payload keys and updated existing G5 happy-path fixtures to carry explicit high-confidence perceived artifacts.
- Added P2-1 import-linter contract forbidding the detector from importing `sensory_bridges_dispatch`; import-linter now reports 14 kept / 0 broken.
- Added frozen offline fidelity fixtures:
  - `tests/fixtures/specialists/quinn_r/fidelity/slide01-red.json`
  - `tests/fixtures/specialists/quinn_r/fidelity/green-corpus/*.json`
  - `tests/fixtures/specialists/quinn_r/fidelity/green-corpus-manifest.json`
  - `tests/fixtures/specialists/quinn_r/fidelity/seeded-defects/*.json`
- Added `tests/specialists/quinn_r/test_fidelity_detector.py` covering RED-first evidence, green corpus FP=0, seeded defects, classifier two-sided pins, missing/low-confidence perception, and contract shape pins.
- Added P2-1 cross-trial learning and a non-closing backlink in deferred inventory. The grounding-leg row remains open for P2-2/P2-3/P2-4.

## Important Constraints Confirmed

- `_RETRYABLE_DISPATCH_TAGS` was not modified.
- The detector imports the shared model contract and stdlib only; it does not import or call sensory bridges or any vision provider.
- Tests use committed fixtures under `tests/fixtures/...`; they do not depend on untracked `runs/` directories.
- P2-1 does not make a production run green. It arms the detector and leaves the real grounding repair to P2-3.

## Verification

Passed:

- RED-first before implementation:
  - `.\.venv\Scripts\python.exe -m pytest tests\specialists\quinn_r\test_fidelity_detector.py -q`
  - Initial result: expected collection failure, `ModuleNotFoundError: No module named 'app.models.perception'`.
- P2 detector suite:
  - `.\.venv\Scripts\python.exe -m pytest tests\specialists\quinn_r\test_fidelity_detector.py -q`
  - Result: 8 passed.
- Focused Quinn-R/audio/error taxonomy regression:
  - `.\.venv\Scripts\python.exe -m pytest tests\specialists\quinn_r tests\specialists\test_audio_segment_grounding.py tests\contracts\test_specialist_error_taxonomy.py -q`
  - Result: 90 passed.
- Full Quinn-R suite:
  - `.\.venv\Scripts\python.exe -m pytest tests\specialists\quinn_r -q`
  - Result: 73 passed.
- Ruff:
  - `.\.venv\Scripts\ruff.exe check app\models\perception app\specialists\quinn_r\fidelity_detector.py app\specialists\quinn_r\_act.py app\specialists\quinn_r\quality_control_dispatch.py tests\specialists\quinn_r\test_fidelity_detector.py tests\specialists\quinn_r\test_quinn_r_g5_qa_body.py tests\specialists\quinn_r\test_quinn_r_act_node_dispatch.py tests\specialists\quinn_r\test_quinn_r_two_mode_dispatch.py tests\specialists\test_audio_segment_grounding.py`
  - Result: all checks passed.
- Import-linter:
  - `.\.venv\Scripts\lint-imports.exe --config pyproject.toml`
  - Result: 14 kept, 0 broken.
- Pipeline lockstep:
  - `.\.venv\Scripts\python.exe scripts\utilities\check_pipeline_manifest_lockstep.py`
  - Result: exit 0, trace `reports\dev-coherence\2026-06-19-1823\check-pipeline-manifest-lockstep.PASS.yaml`.

Known non-P2 failures:

- `.\.venv\Scripts\python.exe -m pytest tests\contracts -q` currently fails 14 tests from pre-existing repository drift, including provider roster status, legacy `marcus/` schema/path expectations, transform-registry exemptions, dispatch/canonical-caller guards, zero-test-edits historical guard, and state-config key collision. The P2-specific contract surfaces above passed.

## T11 Notes

- Green-corpus manifest uses `curator: "operator pending sign-off"` as required by the prompt; operator/party faithful-label sign-off is still needed before final close.
- The spec frontmatter is set to `ready-for-review`; final `done` flip remains with Claude T11.
- Ambient untracked `runs/` directories were present before/through this work and were not used as test inputs.
