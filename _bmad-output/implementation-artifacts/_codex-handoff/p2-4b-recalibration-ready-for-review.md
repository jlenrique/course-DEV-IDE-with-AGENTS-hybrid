# P2-4b Recalibration Handoff

## 0. Frozen Gold

- Gold file: `_bmad-output/implementation-artifacts/reading-path-holdout-gold-labels.json`
- SHA256: `56473484F1D296C04D5A569865B8C6D5EE296FB55AB0AC193BAF6B9EB3DE20A8`
- Attestation: gold labels, frozen fresh perceptions, and scoring math were not relabeled or changed for this run.

## 1. Scope Executed

Subject/substrate for every number below: `(built-classifier, frozen-fresh-14, gold-known-to-dev)`.

- A geometry: tightened macro discrimination for two-pane comparisons, true 2x2 card grids, photo-pair columns, multi-column peer lanes, and numbered-chip non-columns.
- B image role: added authoritative `dominant_image_role` to `PerceptionArtifact`; moved dominant fold out of `reading_path_p2_4b_run.py`; ignored text panels as slide-level image-role evidence; retained per-element `image_roles`.
- B perceiver rubric: sharpened future live `role_tier` prompt for decorative tone/mood/hero/banner/side-panel photos.
- C escalation: narrowed `callout_kind_present` to genuine question/quiz/CTA ambiguity, removed tier-2.5 from escalation by itself, and wired the P2-4b leg-3 measurement to the real escalation ledger ceiling.

## 2. Seam Numbers

Baseline from canonical fair measurement:

- primary-key: `1/14 = 0.071`
- full-tuple: `0/14 = 0.000`
- macro: `7/14 = 0.500`
- image_role: `3/14 = 0.214`
- escalation: `13/14 = 0.929`

Post-recalibration deterministic fixture over the frozen perceptions:

- post-A macro seam: `14/14 = 1.000`
- post-B image_role seam: `14/14 = 1.000`
- post-C escalation seam: `2/14 = 0.143`
- primary-key: `14/14 = 1.000`
- full-tuple: `14/14 = 1.000`
- default/degraded rows: `0`

Live leg-3 re-measure:

- report: `_bmad-output/implementation-artifacts/reading-path-holdout-rescan-2026-06-23/honest-built-classifier-measurement.json`
- primary-key: `14/14 = 1.000`
- full-tuple: `14/14 = 1.000`
- macro/image_role/text/cadence: all `14/14 = 1.000`
- escalation: `2/14 = 0.143`, fired `{"callout_kind_present": 2}`, degraded `0`

Quantization caveat: `n=14`, so one slide is about `0.071`. This is a consumed/non-naive conformance dev set, not a fresh generalization claim.

## 3. Validation

Passed:

- `python -m pytest tests\analysis\test_reading_path_p2_4b_recalibration.py tests\analysis\test_reading_path_p2_4b_run.py tests\analysis\test_reading_path_p2_4b_score.py tests\specialists\vision\test_reading_path_classifier.py tests\specialists\vision\test_reading_path_escalation.py tests\utilities\test_reading_path_derivation.py tests\models\perception\test_perception_artifact_schema_parity.py -q` -> `96 passed`
- `python -m ruff check ...` on touched P2-4b files -> passed
- `python scripts\analysis\reading_path_p2_4b_measure_fresh.py` -> live first-run passed with the numbers above

Full-suite baseline-diff attestation:

- `python -m pytest -q` completed with `4892 passed, 80 failed, 27 skipped, 2 xfailed`.
- Failures are broad ambient repo drift, not localized P2-4b regressions: HUD/private API pins, dispatch registry roster drift, structural-walk manifest counts, schema pins, fit-report contract files, replay/cache fixtures, model-id denylist contradiction, and preflight environment checks.

## 4. File List

Intentional P2-4b files:

- `_bmad-output/implementation-artifacts/reading-path-holdout-rescan-2026-06-23/honest-built-classifier-measurement.json`
- `app/models/perception/perception_artifact.py`
- `app/specialists/vision/provider.py`
- `scripts/analysis/reading_path_p2_4b_measure_fresh.py`
- `scripts/analysis/reading_path_p2_4b_run.py`
- `scripts/analysis/reading_path_holdout_rescan.py`
- `scripts/utilities/reading_path_classifier.py`
- `scripts/utilities/reading_path_escalation.py`
- `state/config/schemas/perception-artifact.schema.json`
- `tests/analysis/test_reading_path_p2_4b_recalibration.py`

Pre-existing/unrelated dirty state observed and not claimed as remediation:

- `claude-goal.txt`
- untracked `runs/**`
- line-ending-only status noise on coverage/vision recording fixtures after the broad suite

## 5. Review Notes

- No slide-id keyed classifier rules were added.
- The analysis scaffold `_dominant_image_role` was deleted; the runner reads classifier-emitted `dominant_image_role`.
- The measurement script asserts the real escalation ledger ceiling, so future over-escalation fails the P2-4b run instead of hiding in a synthetic tripwire.
