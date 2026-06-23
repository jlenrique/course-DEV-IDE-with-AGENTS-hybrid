# P2-4c S1 ready for review

Date: 2026-06-23
Branch: `fidelity-perception-arc-2026-06-19`
Codex scope: T1-T10 only. No commit, no status flip.

## T11 remediation addendum

Authority: `_bmad-output/implementation-artifacts/codex-remediation-prompt-p2-4c-s1-t11.md`.

Remediation status: complete, no commit/status flip.

Implemented hand-back items:
- MF-A: `derive_primary_name` is now total for `card_grid`, `two_pane`, `center_out`, and `diagram_driven`; the bad `card_grid -> top_down` pin was corrected to `grid_quadrant`.
- MF-B/SF-4: S1 no longer upgrades opposition cues to `comparison_pair`/`two_up_comparison`; it keeps coordinate peers at `multi_column` and emits `reading_path_flags=["oppositional_cue"]` as the S3 side-channel.
- MF-C/SF-2: transform detection is structural; prose-only verbs like "then/produces/launch" in one text blob do not emit `enumerated_process`; process ordering is pinned by connector structure.
- SF-1: `center_out` and `diagram_driven` are now macro-layout values and derive through `derive_primary_name`, removing the forced-primary bypass.
- SF-3: `card_grid` is reachable before `multi_column` and has a precedence shape-pin.
- NIT: dead `_looks_z`, `_looks_f_pattern`, `_has_ordinal`, and `_SCORERS` are removed; S1 None-ness for `image_roles` and `callout_intent` is pinned.
- Governance: AC-S1-8 in the spec now explicitly records D1 un-quarantine of `multi_column`.

Remediation RED-first evidence:
- Tests added/changed first, then run before production fixes:
  - `.\.venv\Scripts\python.exe -m pytest tests\utilities\test_reading_path_derivation.py tests\specialists\vision\test_reading_path_classifier.py -q -p no:randomly`
  - Result before fixes: `12 failed, 23 passed`.
  - Failures covered direct `two_pane`, `card_grid`, `center_out`, `diagram_driven` derivation; missing `reading_path_flags`; prose transform over-fire; grid shadowing; forced-primary drift.
- After remediation fixes:
  - Same slice: `35 passed in 3.59s`.
  - Schema/model + classifier + derivation slice: `59 passed in 3.54s`.
  - Expanded reading-path/vision/Irene slice: `110 passed in 6.79s`.

Baseline-diff attestation:
- Clean HEAD SHA: `829bc53`.
- T11 review recorded stash-proof that `tests/contracts` had 14 ambient failures on clean HEAD.
- Codex remediation reran a non-destructive detached clean worktree at `829bc53` and reproduced `14 failed, 278 passed, 1 skipped`.
- Current remediated tree `tests/contracts`: `14 failed, 278 passed, 1 skipped`.
- Failure names match the ambient set; remediation added zero new contract reds.

Remediation validation:
- `.\.venv\Scripts\python.exe -m pytest tests\contracts\test_reading_path_parity.py tests\models\perception\test_perception_artifact_schema_parity.py tests\utilities\test_reading_path_derivation.py tests\specialists\vision\test_reading_path_classifier.py tests\specialists\vision\test_vision_provider_and_act.py tests\specialists\vision\test_vision_unclassifiable_error_pause.py tests\specialists\vision\test_vision_recorded_real_replay.py tests\specialists\irene\test_irene_reading_path_conformance.py tests\unit\specialists\irene\test_pass_2_template_strict.py -q -p no:randomly`
  - Result: `110 passed in 6.79s`.
- `.\.venv\Scripts\python.exe scripts\utilities\check_pipeline_manifest_lockstep.py`
  - Result: `lockstep-check exit=0`
  - Trace: `reports/dev-coherence/2026-06-23-0130/check-pipeline-manifest-lockstep.PASS.yaml`.
- `.\.venv\Scripts\ruff.exe check ...`
  - Result: `All checks passed!`.
- `.\.venv\Scripts\lint-imports.exe`
  - Result: `15 kept, 0 broken`.
- `git diff --check`
  - Result: exit 0; warning only that `state/config/schemas/perception-artifact.schema.json` will normalize CRLF to LF.

## Baseline and dirty-worktree fence

- Opening branch: `fidelity-perception-arc-2026-06-19`.
- Opening `git status --short`: clean tracked tree; pre-existing untracked `runs/` artifacts only.
- Focused clean baseline before edits:
  - `.\.venv\Scripts\python.exe -m pytest tests/contracts/test_reading_path_parity.py tests/models/perception/test_perception_artifact_schema_parity.py tests/specialists/vision/test_reading_path_classifier.py tests/specialists/irene/test_irene_reading_path_conformance.py tests/specialists/vision/test_vision_provider_and_act.py tests/specialists/vision/test_vision_unclassifiable_error_pause.py -q -p no:randomly`
  - Result: `38 passed in 7.81s`.
- Step-1a Cora gate: `next-session-start-here.md` recorded proceed/no blocking findings; the two reading-path slivers were folded into S1 fixtures.
- Additional untracked files present by handoff and left untouched: `_bmad-output/implementation-artifacts/codex-dev-prompt-p2-4c-s2.md`, `_bmad-output/implementation-artifacts/codex-dev-prompt-p2-4c-s3.md`, `_bmad-output/implementation-artifacts/reading-path-gap-resolution-G2-G3-2026-06-22.md`, plus ambient `runs/`.

## Implementation summary

- Added tuple sibling fields to `PerceptionArtifact`: `macro_layout`, `image_roles`, `text_substructure`, `narration_cadence`, `callout_intent`.
- Widened `ReadingPath` additively; no legacy value removed.
- Added `scripts/utilities/reading_path_derivation.py::derive_primary_name(...)` and a shape-pin test.
- Reworked the deterministic classifier to populate geometry-derived tuple axes in `with_classified_reading_path`, with S1-only `image_roles=None` and `callout_intent=None`.
- Implemented D1/D3: 2-wide coordinate peers emit counted `multi_column`; numeral-only peer lists downgrade to `peer_boxes`/derived top-down; true transform sequences emit `enumerated_process`.
- Tightened z behavior: the old z fixture now resolves to `split_image_text`; `z_pattern` remains in the enum/lockstep as an alias-compatible retained value.
- Added observable batch summary + `assert_default_ceiling` for default/top_down degradation.
- Normalized/clamped bboxes so `cx > 1.0` and inverted coordinates do not skew buckets.
- Updated the four-file reading-path lockstep plus grammar examples and bumped manifest `data_plane_vocabulary_version` to `dp-v1.6`.

## AC evidence

- AC-S1-1: `ReadingPath` widened in `app/models/perception/perception_artifact.py`; parity lockstep includes retained aliases and new primary names.
- AC-S1-2: optional tuple sibling fields added with closed Literal types and `validate_assignment=True` inherited from the model config.
- AC-S1-3: derivation module added and pinned by `tests/utilities/test_reading_path_derivation.py`.
- AC-S1-4: classifier now derives macro/text/cadence axes; `_looks_z` no longer claims focal-hero split slides.
- AC-S1-5: P2-4a red-rejection/error-pause tests remain green; no enum value removed.
- AC-S1-6: registry, classifier tuple, lint tuple, segment schema, grammar headings, and parity test all updated; lockstep exits 0.
- AC-S1-7: default-degradation batch summary and ceiling assertion added and tested.
- AC-S1-9: unclassifiable HIGH/perceived artifacts still route to `vision.reading-path.unclassifiable`; empty `visual_elements` is now pinned explicitly.

## RED to green transcript

- RED run after tests only:
  - `tests/utilities/test_reading_path_derivation.py`: missing `scripts.utilities.reading_path_derivation`.
  - `tests/models/perception/test_perception_artifact_schema_parity.py`: missing tuple Literal exports.
  - `tests/specialists/vision/test_reading_path_classifier.py`: missing `assert_default_ceiling`.
- Interim RED after first implementation:
  - 9 failures covering schema projection, numbered-list downgrade, transform order, multi-column/two-pane S1 behavior, default over-labeling, and bbox normalization.
- GREEN after fixes:
  - Tuple/schema/classifier focused suite: `42 passed in 4.52s`.
  - Parity + tuple/schema/classifier + manifest projection edge: `45 passed in 6.57s`.
  - Existing Irene/vision consumers: `29 passed in 6.13s`.
  - Final expanded reading-path slice: `85 passed in 6.95s`.

## Validation

- `.\.venv\Scripts\python.exe -m pytest tests/contracts/test_reading_path_parity.py tests/models/perception/test_perception_artifact_schema_parity.py tests/specialists/vision/test_reading_path_classifier.py tests/specialists/vision/test_vision_provider_and_act.py tests/specialists/vision/test_vision_unclassifiable_error_pause.py tests/specialists/vision/test_vision_recorded_real_replay.py tests/specialists/irene/test_irene_reading_path_conformance.py tests/unit/specialists/irene/test_pass_2_template_strict.py -q -p no:randomly`
  - Result: `85 passed in 6.95s`.
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py`
  - Result: `lockstep-check exit=0`
  - Trace: `reports/dev-coherence/2026-06-23-0045/check-pipeline-manifest-lockstep.PASS.yaml`.
- `.\.venv\Scripts\ruff.exe check ...`
  - Result: `All checks passed!`.
- `.\.venv\Scripts\lint-imports.exe`
  - Result: `15 kept, 0 broken`.
- `git diff --check`
  - Result: exit 0; warning only that `state/config/schemas/perception-artifact.schema.json` will normalize CRLF to LF.
- `.\.venv\Scripts\python.exe -m scripts.generators.v42.render --manifest state/config/pipeline-manifest.yaml --output docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md`
  - Result: exit 0 with runpy warning; no on-disk `-gen` diff. Lockstep Check-9 still passed after the render.

## Diff summary

Tracked modified files: 15. New tracked-intended files: 2.

Core files:
- `app/models/perception/__init__.py`
- `app/models/perception/perception_artifact.py`
- `scripts/utilities/reading_path_classifier.py`
- `scripts/utilities/reading_path_derivation.py`
- `scripts/validators/pass_2_emission_lint.py`

Lockstep/config/docs:
- `state/config/pipeline-manifest.yaml`
- `state/config/reading-path-patterns.yaml`
- `state/config/schemas/perception-artifact.schema.json`
- `state/config/schemas/segment-manifest.schema.json`
- `skills/bmad-agent-content-creator/references/pass-2-grammar-riders-examples.md`

Tests:
- `tests/contracts/test_reading_path_parity.py`
- `tests/integration/marcus/test_package_builders.py`
- `tests/models/perception/test_perception_artifact_schema_parity.py`
- `tests/specialists/vision/test_reading_path_classifier.py`
- `tests/specialists/vision/test_vision_provider_and_act.py`
- `tests/specialists/vision/test_vision_unclassifiable_error_pause.py`
- `tests/utilities/test_reading_path_derivation.py`

Numstat for tracked modified files before this handoff: `1026 insertions / 97 deletions` across 15 files, excluding the two new files and this handoff.

## Deviations and T11 notes

- The generated v4.2 `-gen` witness was regenerated but did not change on disk; the dp bump is not rendered into the pack. Check-9/lockstep passed after regeneration.
- `multi_column` is treated as un-quarantined per v1.1 D1 and the Codex S1 prompt, superseding the older A3 quarantine language still present in historical catalog text.
- `image_roles` and `callout_intent` are schema-present but intentionally unpopulated in S1.
- S3 oppositional upgrade is not implemented; explicit opposition cues still classify as S1 `multi_column`.
- No production-path mocks were added. Recorded-real replay remains test-only behind the existing parse seam.
