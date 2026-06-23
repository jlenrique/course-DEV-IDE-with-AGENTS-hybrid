# P2-4c S2 Ready for Review

Date: 2026-06-23
Executor: Codex
Status: READY FOR REVIEW - no commit, no sprint-status flip

## Scope Executed

- Added per-element role-tier vocabulary support for `1`, `2`, `2_5`, `3`, `4`.
- Extended the live vision prompt to request `role_tier` and `role_tier_reason` per `visual_elements[]` entry.
- Validated provider-emitted `role_tier` values at the `VisionProviderResponse` boundary.
- Populated `PerceptionArtifact.image_roles` in deterministic classification.
- Added `image_role_flags` side-channel for:
  - `tier_2_5_candidate`
  - `tier_3_quarantined`
- Added deterministic S2 hard gates/backfill:
  - small icon/logo locks tier 4
  - tier 3 ruled out when internal labels are absent
  - edge-bleed overlapping image with no internal labels favors tier 1
  - chart/table with caption backfills `2_5`
  - central labeled diagram backfills quarantined `3`
  - photo backfills `2`
  - empty `visual_elements=[]` on HIGH/perceived now emits controlled tuple + `image_roles=[]`
- Added agreement/scoring harness:
  - `2_5` folds to `2`
  - `3` excluded from scored top-1 as quarantine
  - Cohen's kappa + soft-middle kappa
  - confusion matrix artifact shape
  - rubric metadata for all tiers

## Files Changed

- `app/models/perception/perception_artifact.py`
- `app/models/perception/__init__.py`
- `app/specialists/vision/payload_contract.py`
- `app/specialists/vision/provider.py`
- `scripts/utilities/reading_path_classifier.py`
- `scripts/utilities/image_role_scoring.py`
- `state/config/schemas/perception-artifact.schema.json`
- `tests/models/perception/test_perception_artifact_schema_parity.py`
- `tests/specialists/vision/test_image_role_tiers.py`
- `tests/specialists/vision/test_reading_path_classifier.py`
- `tests/specialists/vision/test_vision_provider_and_act.py`
- `tests/specialists/vision/test_vision_unclassifiable_error_pause.py`

## Validation

Baseline before edits:

```text
pytest tests/models/perception/test_perception_artifact_schema_parity.py tests/specialists/vision/test_reading_path_classifier.py tests/specialists/vision/test_vision_provider_and_act.py tests/specialists/vision/test_vision_unclassifiable_error_pause.py -q -p no:randomly
66 passed
```

S2 slice:

```text
pytest tests/specialists/vision/test_image_role_tiers.py tests/specialists/vision/test_vision_provider_and_act.py::test_perception_prompt_demands_per_element_role_tier tests/specialists/vision/test_vision_provider_and_act.py::test_parse_response_accepts_role_tier_and_rejects_out_of_vocab_value tests/models/perception/test_perception_artifact_schema_parity.py::test_image_role_flags_schema_enum_is_public_and_closed tests/specialists/vision/test_vision_unclassifiable_error_pause.py::test_empty_visual_elements_emit_controlled_empty_image_roles_without_pause -q -p no:randomly
15 passed
```

Focused regression:

```text
pytest tests/models/perception/test_perception_artifact_schema_parity.py tests/specialists/vision/test_reading_path_classifier.py tests/specialists/vision/test_image_role_tiers.py tests/specialists/vision/test_vision_provider_and_act.py tests/specialists/vision/test_vision_unclassifiable_error_pause.py tests/contracts/test_reading_path_parity.py tests/specialists/irene/test_irene_reading_path_conformance.py tests/specialists/vision/test_vision_recorded_real_replay.py tests/unit/specialists/irene/test_pass_2_template_strict.py -q -p no:randomly
115 passed
```

Additional checks:

```text
ruff check touched S2 files
All checks passed

python scripts/utilities/check_pipeline_manifest_lockstep.py
lockstep-check exit=0

lint-imports
Contracts: 15 kept, 0 broken

git diff --check
no output
```

Schema parity rerun after LF normalization:

```text
pytest tests/models/perception/test_perception_artifact_schema_parity.py -q -p no:randomly
27 passed
```

## Review Notes

- Tier 3 remains emittable only as quarantined side-channel and is excluded from scored top-1 through `fold_scored_tier("3") is None`.
- `image_roles` are currently emitted for positioned `visual_elements`; non-empty artifacts with no positioned geometry still fail through the existing controlled `vision.reading-path.unclassifiable` path.
- Existing untracked `runs/` directories were present before this S2 run and were not modified intentionally.
