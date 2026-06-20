# P2-2 Codex Handoff - Ready for Review

Story: `p2-2-perception-artifact-vision-node`
Status: ready for Claude T11 review
Branch observed: `fidelity-perception-arc-2026-06-19`

## Implementation Summary

- Added the PNG-grounded `vision` specialist at `app/specialists/vision/` with provider seam, retry policy, repeatability comparator, LangGraph scaffold, payload contract, and model config.
- Extended `PerceptionArtifact` additively with `confidence_score`, `provider_model_id`, `source_png_path`, and excluded `provenance`; `extra="forbid"` and closed confidence/coverage enums remain enforced.
- Wired manifest node `07G` inside the existing v4.2 pack lineage and bumped `data_plane_vocabulary_version` to `dp-v1.3`; no `v4.3` generator or pack family was created.
- Wired G5 to consume `perception_artifacts` from `vision` and removed the dormant `perception-not-wired` pass path. Default behavior is enforce.
- Added `FIDELITY_GATE=warn` as the required break-glass override. It records a warn fidelity status plus the annotation `fidelity gate OVERRIDDEN by operator — narration unverified`; it is not a clean pass and should be reconsidered/removed at P2-3 close.
- Regenerated `state/config/schemas/perception-artifact.schema.json` and `docs/workflow/production-prompt-pack-v4.2-gen-narrated-lesson-with-video-or-animation.md`.
- Updated schema changelog and cross-trial learnings. The deferred grounding-leg repair remains open for P2-3.

## New / Changed Tests

- `tests/models/perception/test_perception_artifact_schema_parity.py`: asserts provenance exists on the model but is excluded from dumps/schema, emitted schema parity holds, closed enums reject bad values, and the P2-1 fixture still validates additively.
- `tests/specialists/vision/test_vision_provider_and_act.py`: verifies per-slide artifact emission, explicit `not_covered` for unreadable PNGs, retry on timeout/5xx only, and no retry for 4xx or quality failures.
- `tests/specialists/vision/test_vision_repeatability.py`: quarantined repeatability calibration; identical fixture is stable, perturbed negative control fails.
- `tests/specialists/vision/test_vision_live_roundtrip.py` and `test_vision_silent_drift_canary.py`: live/operator evidence hooks; deselected in default local runs.
- `tests/specialists/quinn_r/test_ac12_detector_red_on_produced_artifact.py`: proves the produced perception artifact trips the detector on unsupported narration and clears on faithful narration.
- `tests/specialists/quinn_r/test_quinn_r_g5_perception_enforcement.py`: proves default enforcement, `FIDELITY_GATE=warn` downgrade with annotation, and non-retryable fidelity tag behavior.
- `tests/specialists/quinn_r/test_fidelity_detector.py`: shape pin updated exactly for additive public fields; old dormant-perception tripwire replaced with `test_g5_manifest_supplies_perception_projection`.
- `tests/specialists/quinn_r/test_quinn_r_g5_qa_body.py`: stale P2-1 absent-perception pass expectation replaced with a P2-2 Class-A `FidelityError` expectation.
- `tests/integration/marcus/test_package_builders.py`: manifest projection pin updated for `dp-v1.3`, node `07G`, and G5 node `13` perception projection.
- `tests/contracts/test_manifest_payload_contracts.py` and `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py`: allowlist/consumer contract updates for `vision`.

## Version Governance

- No `v4.3` lineage was created. Discriminator used: `PerceptionArtifact` is an internal envelope contribution consumed by the detector, not a learner-facing pack-lineage content deliverable.
- `dp-v1.3` records the topology refinement: `07F -> 07G -> 08`, with G5 consuming `perception_artifacts` from `vision`.
- Frozen v4.2 pack SHA check passed: `tests/contracts/test_frozen_pack_shas.py` reported `4 passed, 1 skipped`.
- Lockstep passed with exit 0: `reports/dev-coherence/2026-06-20-1353/check-pipeline-manifest-lockstep.PASS.yaml`.

## AC-13 Calibration

- Repeatability thresholds are pinned in `app/specialists/vision/repeatability.py`:
  - `bbox_iou_min = 0.90`
  - `text_edit_distance_max = 8.0`
  - `element_jaccard_min = 1.0`
- Quarantined tests prove the identical golden fixture is stable and the perturbed negative control is rejected.

## Verification

Passed:

- Focused P2-2 suite: `46 passed, 2 deselected`.
- Quinn-R suite: `84 passed`.
- Marcus integration: `193 passed, 1 skipped`.
- Audit suite: `34 passed`.
- Manifest payload/audit focused slice: `9 passed`.
- Frozen pack SHA contract: `4 passed, 1 skipped`.
- Sandbox AC validator: `PASS - no sandbox-AC violations across 1 story file(s)`.
- Ruff touched surfaces: all checks passed.
- Import-linter: `15 kept, 0 broken`.
- `git diff --check`: clean.
- Pipeline manifest lockstep: exit 0, trace above.

Known validation limits / non-P2 failures:

- `tests/parity -q -n0` remains red with 5 unrelated pre-existing failures: NFR-CG6 governance version pin, Trial-475 silent-bypass expectation, Trial-475 runner monkeypatch signature drift, missing `tests/fixtures/frozen_paths`, and Vera G3 missing-artifact fixture behavior.
- `tests/contracts -q -n0` remains red with 14 unrelated repository-drift failures, including the longstanding zero-test-edit range guard, fit-report schema/path/canonical caller drift, single-writer routing, provider roster status, Quinn-R legacy path, transform-registry exemptions, and state-config key collision.
- Full `pytest tests -q -n0` was attempted and hit the 304-second tool timeout before a usable report was emitted.

## T11 Remediation Addendum - 2026-06-20

Remediated the T11 hand-back prompt at `_bmad-output/implementation-artifacts/codex-remediation-prompt-p2-2-t11.md`:

- F1: replaced the vacuous repeatability self-compare with held-out equivalent fixture coverage plus one negative fixture per threshold.
- MF1: tightened money-unit matching so `$5 to enroll`, `$4 tax`, and `$5 there` normalize as bare money, not trillion/billion units; added fixture-backed adversarial corpus.
- M3: added structured `scope` metadata to Quinn-R content errors and limited `FIDELITY_GATE=warn` to narration-scope failures. Structural artifact validation, duplicate slide ids, missing artifacts, and evidence-quality failures still raise under warn.
- F2: implemented the ratified Option A in `test_33_1a_verbatim_extraction.py`: closed allowlist, Check-9 invariant enrollment meta-test, and 07G generated-section order/body assertion.
- Should-fixes folded: `quarantined` is excluded from default pytest addopts, silent-drift canary no longer self-compares, provider slide/model mismatches fail loud, provider model id is read from `model_config.yaml`, and bounded retry now covers timeout, 408, 429, 5xx, and tagged transport errors.

F1 mutation table:

| Threshold | Negative fixture | Strict result | Degenerate mutation | Mutated result |
| --- | --- | --- | --- | --- |
| `bbox_iou_min` | `slide-01-provider-response-bbox-negative.json` | RED, only `bbox_iou[...]` reason | set to `0.0` | GREEN |
| `element_jaccard_min` | `slide-01-provider-response-element-negative.json` | RED, only `element_jaccard` reason | set to `0.0` | GREEN |
| `text_edit_distance_max` | `slide-01-provider-response-text-negative.json` | RED, only `text_edit_distance` reason | set to `10000.0` | GREEN |

Remediation verification:

- Blocking P2-2 lane including F2: `55 passed, 7 deselected`.
- Quarantined repeatability lane: `5 passed`.
- Focused remediation file set: `37 passed, 1 deselected`.
- Marcus integration: `193 passed, 1 skipped`.
- Focused contracts: `14 passed, 1 skipped`.
- Audit suite: `34 passed`.
- Ruff touched remediation surfaces: all checks passed.
- Import-linter: `15 kept, 0 broken`.
- Lockstep: exit 0, trace `reports/dev-coherence/2026-06-20-1729/check-pipeline-manifest-lockstep.PASS.yaml`.
- `git diff --check`: clean.

Baseline-diff attestation:

- Created detached clean worktree `.tmp/p2-2-baseline-4455c04` at `4455c04`.
- Current P2-2 tree `tests/contracts -q -n0`: `14 failed, 276 passed, 1 skipped`.
- Clean `4455c04` `tests/contracts -q -n0`: `14 failed, 274 passed, 1 skipped`; same contract failure ids reproduce, and `test_33_1a_verbatim_extraction` is now green on the P2-2 tree.
- Current P2-2 tree `tests/parity -q -n0`: `5 failed, 354 passed, 18 skipped`.
- Clean `4455c04` `tests/parity -q -n0`: `7 failed, 352 passed, 18 skipped`. The current five parity-red test ids are all red on the clean worktree; the clean worktree additionally fails compositor determinism/Trial-475 replay due missing baseline assets/subprocess environment.

## T11 Notes

- AC-14-B operator live round-trip evidence is still pending; default local runs deselect the live provider tests.
- No narration was repaired in this story, and no test or fixture was changed to make a real run green by repair.
- Real-run fidelity RED is the EXPECTED P2-2 outcome; root-cause repair lands at P2-3; deferred entry stays open.
- Ambient untracked `runs/` directories were present/generated during validation and were not used as committed test inputs.
