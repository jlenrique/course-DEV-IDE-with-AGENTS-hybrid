# P2-3 Pass 2 Consumes Perceived Visuals - Ready for Review

Date: 2026-06-21
Branch: `fidelity-perception-arc-2026-06-19`
Baseline ancestor check: `3a0ad22` is an ancestor of working HEAD.

## Implementation Summary

- Irene Pass 2 now projects rich `app.models.perception.PerceptionArtifact`
  rows into a prompt-local `Visual authority - perceived slide evidence`
  region.
- Gary/brief visual expectations now render only in a separate demoted
  expected-plan region marked subordinate, stale-capable, and defer-to-perceived.
- Node `08` now receives `perception_artifacts` from `vision`; manifest
  vocabulary bumped `dp-v1.3` to `dp-v1.4`.
- Missing, not-covered, or low-confidence perception emits the detector-visible
  token `UNVERIFIED — no perceived authority`; Irene does not silently promote
  brief text into authority.
- The authoring-envelope `PerceptionArtifact` remains a minimal projection
  helper, with code-site decoy notes preventing runtime authority confusion.

## A3 Mutation Table

| Mutation | Expected failure surface | Evidence |
|---|---|---|
| M1 source revert: authority rebuilt from Gary/brief expectation | `$5.2T` / `line+bars` enters the authority region, while `$4.5T` photo evidence is no longer sole authority | Killed by `test_authority_region_uses_perceived_visuals_and_demotes_stale_brief` and held-out fixture assertions. |
| M2 section collapse: authority and expected-plan regions merged or reordered | Region extraction and ordering pins fail; demoted text can no longer be proven subordinate | Killed by `test_corpus_leads_perceived_authority_then_demoted_expected_plan` and region-boundary assertions in `test_irene_pass2_perceived_visual_authority.py`. |

## A7 Detector Evidence

Baseline pre-fix RED fixture:

- Narration: `The line chart and paired bars show $5.2T.`
- Perceived artifact: `$4.5T annual healthcare spend`, building photo, stat callout.
- Result: `FidelityError` from `detect_fidelity(...)`.

Post-fix GREEN fixture:

- Narration: `The building photo anchors the $4.5T scale.`
- Same perceived artifact.
- Result: `{'blocking': [], 'evaluated_segments': 1}`.

Held-out anti-overfit leg:

- Perceived: `74%` bar chart.
- Stale brief: `80%` line chart.
- Green narration passes on `74%` bar chart; stale `80%` line-chart narration raises `FidelityError`.

## A4 Headless Detector Confirmation

Confirmed before implementation that the P2-1 detector is headlessly invokable
on Pass-2-shaped narration:

- Artifact: slide-01, HIGH/perceived, extracted text `$4.5T annual healthcare spend. building photo.`
- Segment: `The building photo shows $4.5T.`
- Output: `{'blocking': [], 'evaluated_segments': 1}`.

## Validation

- `.\.venv\Scripts\python.exe -m pytest tests/specialists/irene -q` -> 38 passed.
- `.\.venv\Scripts\python.exe -m pytest tests/contracts/test_manifest_payload_contracts.py tests/integration/marcus/test_package_builders.py::test_manifest_declares_projection_edges -q` -> 5 passed.
- `.\.venv\Scripts\python.exe -m pytest tests/specialists/quinn_r/test_fidelity_detector.py tests/specialists/quinn_r/test_quinn_r_g5_perception_enforcement.py -q` -> 20 passed.
- `.\.venv\Scripts\python.exe -m ruff check app/specialists/irene/graph.py app/specialists/irene/authoring/pass_2_template.py app/specialists/irene/authoring/__init__.py tests/specialists/irene tests/end_to_end/test_cache_hit_rate_baseline.py tests/integration/marcus/test_package_builders.py tests/contracts/test_manifest_payload_contracts.py` -> passed.
- `.\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` -> exit 0, trace `reports/dev-coherence/2026-06-21-0258/check-pipeline-manifest-lockstep.PASS.yaml`.

## Regeneration Note

Ran the v4.2 generator after the manifest edit:

`.\.venv\Scripts\python.exe -m scripts.generators.v42.render --manifest state/config/pipeline-manifest.yaml --output docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md`

The generator emitted its existing runpy warning and produced no committed
pack diff because dependency projections are not rendered into the v4.2 pack
body. The lockstep check passed afterward. No v4.3 pack was created.
