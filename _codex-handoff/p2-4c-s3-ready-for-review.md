# P2-4c S3 Ready for Review

Date: 2026-06-23
Executor: Codex
Status: READY FOR REVIEW - no commit, no sprint-status flip

## Scope Executed

- Added S3 triggered escalation utility at `scripts/utilities/reading_path_escalation.py`.
- Added versioned escalation lexicons at `state/config/reading-path-escalation-lexicons.yaml`.
- Added RED-first S3 tests at `tests/specialists/vision/test_reading_path_escalation.py`.
- Implemented upstream-frozen escalation predicate over S1/S2 signals:
  - `macro_margin_low`
  - `opposition_cue_hit`
  - `callout_kind_present`
  - `numbered_without_transform`
  - `low_conf_role_elements`
  - `tuple_disagreement`
  - `low_confidence`
  - `tier_candidate_hit`
- Implemented always-on `escalation_ledger` emission.
- Implemented over-escalation and zero-escalation tripwires.
- Implemented single-shot S3 tuple-delta call path using house `make_chat_model` with `gpt-5.5`.
- Implemented parse seam for:
  - `layout_delta`
  - `callout_intents`
  - `process_kind`
  - `role_overrides`
- Implemented tuple-delta merge over existing S1/S2 tuple.
- Preserved S2 `None` role sentinels; S3 does not coerce unscored roles to a default tier.

## RED-First Evidence

```text
pytest tests/specialists/vision/test_reading_path_escalation.py -q -p no:randomly
RED before implementation: ModuleNotFoundError for scripts.utilities.reading_path_escalation
GREEN after implementation: 8 passed
```

## Ledger Sample

```json
{
  "total": 2,
  "escalated": 1,
  "escalation_rate": 0.5,
  "slides": [
    {
      "slide_id": "plain",
      "escalate": false,
      "subpredicates": {
        "macro_margin_low": false,
        "opposition_cue_hit": false,
        "callout_kind_present": false,
        "numbered_without_transform": false,
        "low_conf_role_elements": false,
        "tuple_disagreement": false,
        "low_confidence": false,
        "tier_candidate_hit": false
      },
      "fired": [],
      "trigger_reason": "none",
      "low_conf_role_element_count": 0
    },
    {
      "slide_id": "ambiguous",
      "escalate": true,
      "subpredicates": {
        "opposition_cue_hit": true
      },
      "fired": ["opposition_cue_hit"],
      "trigger_reason": "opposition_cue_hit"
    }
  ]
}
```

The fixture ledger rate is intentionally 50% because it is a two-slide unit fixture. The tripwire test separately proves over-escalation fails above 20% on a baseline-rate ledger and zero-escalation fails when known ambiguity is present.

## Validation

```text
pytest tests/models/perception/test_perception_artifact_schema_parity.py tests/specialists/vision/test_reading_path_classifier.py tests/specialists/vision/test_image_role_tiers.py tests/specialists/vision/test_reading_path_escalation.py tests/specialists/vision/test_vision_provider_and_act.py tests/specialists/vision/test_vision_unclassifiable_error_pause.py tests/contracts/test_reading_path_parity.py tests/specialists/irene/test_irene_reading_path_conformance.py tests/specialists/vision/test_vision_recorded_real_replay.py tests/unit/specialists/irene/test_pass_2_template_strict.py -q -p no:randomly
129 passed
```

Additional checks:

```text
ruff check touched S3 files
All checks passed

python scripts/utilities/check_pipeline_manifest_lockstep.py
lockstep-check exit=0

lint-imports
Contracts: 15 kept, 0 broken

git diff --check
no output
```

Contract ambient baseline:

```text
pytest tests/contracts -q -p no:randomly
278 passed, 1 skipped, 14 failed
```

Baseline-diff attestation:

- Clean HEAD SHA: `b3fc5c94c5fb377288aaf165c77740d2e0f0fd34`.
- The 14 contract failures match the known ambient failures from S2/P11 and are outside S3 touched files.
- Focused S1/S2/S3 regression battery is green.

## Live Smoke

`OPENAI_API_KEY` was not present in this shell, so the live `gpt-5.5` smoke leg was not executed. The production path is wired through `request_live_tuple_delta()` using the house `make_chat_model` adapter with `per_call_override="gpt-5.5"`; no production-path fixture is used.

## Review Notes

- S3 does not run automatically inside `with_classified_reading_path`; callers use `run_s3_escalation()` after S1/S2 tuple emission so the S3 call remains triggered and single-shot.
- `parse_tuple_delta()` clears volunteered delta fields for unfired jobs, enforcing the "only fired jobs" contract.
- Malformed tuple-delta responses degrade to the S1/S2 artifact and mark the ledger row as `degraded`.
- `callout_intent` remains outside primary-key scoring; S3 only populates the existing nullable field.
