# P2-4a Reading-Path Native Machinery - Ready For Review

Date: 2026-06-21
Branch: `fidelity-perception-arc-2026-06-19`
Story: `p2-4a-reading-path-native-machinery`

## Scope Delivered

- Added public rich-model `PerceptionArtifact.reading_path` as a closed
  7-pattern `Literal` enum with schema parity and TypeAdapter rejection.
- Added deterministic vision-adjacent classifier:
  `scripts/utilities/reading_path_classifier.py`.
- Wired Vision to classify HIGH-confidence perceived artifacts after provider
  parse, without adding provider fields or another model call.
- Added Irene reading-path cadence guidance in the Pass-2 prompt and a
  fail-loud `_assert_reading_path_conformance` check raising
  `Pass2ReadingPathError`.
- Rebuilt the native four-file lockstep:
  `state/config/reading-path-patterns.yaml`,
  `state/config/schemas/segment-manifest.schema.json`,
  `scripts/validators/pass_2_emission_lint.py`,
  `tests/contracts/test_reading_path_parity.py`.
- Folded in the §52 payload-tail rider: UNVERIFIED slides have Gary/brief
  visual strings redacted from the sorted JSON envelope tail while preserving
  the explicitly demoted expected-plan region.
- Bumped `data_plane_vocabulary_version` to `dp-v1.5`; `pack_version` remains
  `v4.2`. Regenerated the `v4.2-gen` witness; lockstep passed.

## RED-First Evidence

Initial targeted RED run:

```text
.venv/Scripts/python.exe -m pytest \
  tests/contracts/test_reading_path_parity.py \
  tests/specialists/vision/test_reading_path_classifier.py \
  tests/specialists/irene/test_irene_reading_path_conformance.py \
  tests/models/perception/test_perception_artifact_schema_parity.py \
  tests/specialists/vision/test_vision_provider_and_act.py \
  tests/specialists/irene/test_irene_pass2_perceived_visual_authority.py \
  tests/specialists/irene/test_irene_prompt_byte_stability_5x.py -q
```

Observed RED before implementation: missing native classifier module, missing
`Pass2ReadingPathError`, missing `ReadingPath`, missing registry/schema files,
Vision output lacked `reading_path`, prompt lacked cadence guidance, and the
old unredacted payload tail still leaked `$5.2T` outside the demoted region.

## Mutation Evidence

| Mutant | Kill Surface | Evidence |
| --- | --- | --- |
| M1 classifier returns naive/default order | `test_anti_vacuity_z_pattern_beats_dom_or_top_down_default` | The fixture is intentionally DOM-wrong; expected `z_pattern` order is `headline -> hero -> body -> cta`, not input order. |
| M2 conformance partition collapsed/no-op | `test_reading_path_conformance_rejects_wrong_order_narration` | Known-wrong narration order `body -> hero` must raise `Pass2ReadingPathError`. |
| Out-of-vocab enum widened (`triptych`) | `test_reading_path_pattern_lockstep`, schema parity tests | Registry/schema/classifier/lint parity expects exactly seven patterns; Pydantic and JSON Schema reject `triptych`. |
| Payload-tail rider removed | `test_missing_or_low_confidence_perception_never_falls_back_to_brief` | Full prompt count must match pre-envelope count for stale `$5.2T`, proving no extra envelope-tail leak. |

## Validation

```text
.venv/Scripts/python.exe -m pytest tests/contracts/test_reading_path_parity.py tests/models/perception/test_perception_artifact_schema_parity.py tests/specialists/vision tests/specialists/irene tests/specialists/quinn_r/test_fidelity_detector.py tests/integration/marcus/test_package_builders.py -q
97 passed in 57.31s

.venv/Scripts/python.exe -m ruff check app/models/perception app/specialists/vision app/specialists/irene scripts/utilities/reading_path_classifier.py scripts/validators/pass_2_emission_lint.py tests/contracts/test_reading_path_parity.py tests/specialists/vision/test_reading_path_classifier.py tests/specialists/irene/test_irene_reading_path_conformance.py tests/models/perception/test_perception_artifact_schema_parity.py tests/specialists/vision/test_vision_provider_and_act.py tests/specialists/irene tests/specialists/quinn_r/test_fidelity_detector.py tests/integration/marcus/test_package_builders.py
All checks passed!

.venv/Scripts/lint-imports.exe --config pyproject.toml
Contracts: 15 kept, 0 broken.

.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py
lockstep-check exit=0 trace=reports/dev-coherence/2026-06-21-0427/check-pipeline-manifest-lockstep.PASS.yaml

git diff --check
PASS (only CRLF normalization warning for state/config/schemas/perception-artifact.schema.json)
```

## Governance Notes

- `data_plane_vocabulary_version`: `dp-v1.4 -> dp-v1.5`.
- `pack_version`: unchanged at `v4.2`; this is a data-plane/topology refinement
  with a vision-adjacent classifier, not a new pack family.
- `docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md`
  was regenerated; no content diff remained after render.
- `_bmad-output/implementation-artifacts/SCHEMA_CHANGELOG.md` records
  `PerceptionArtifact v1.2` and `Data Plane Vocabulary dp-v1.5`.
- Deferred entry `pass2-envelope-payload-brief-unframed-in-prompt-tail` is
  struck with a P2-4a closure note.

## AC-9 Operator Gate

AC-9 real-slide >=80% conformance corpus is not claimed in this handoff. It
remains operator-gated and requires the operator-run frozen corpus evidence
after P2-4a code review.
