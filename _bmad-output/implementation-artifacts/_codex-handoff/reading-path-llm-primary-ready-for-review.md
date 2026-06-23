# Reading Path LLM-Primary Ready For Review

Date: 2026-06-23

## Scope

Implemented the reading-path LLM-primary remediation from the canonical
`reading-path-llm-primary` prompt. The live `gpt-5.5` tuple producer is now the
authoritative producer for `PerceptionArtifact` reading-path tuple fields.
Deterministic geometry remains only as `reading_path_geometry` telemetry.

No prompt pack or manifest files were modified.

## Implementation Notes

- Added public perception fields: `dominant_image_role`, `reading_path_source`,
  `reading_path_degraded`, `reading_path_rationale`, and
  `reading_path_geometry`; regenerated
  `state/config/schemas/perception-artifact.schema.json`.
- Added `with_llm_primary_reading_path` in
  `scripts/utilities/reading_path_classifier.py`.
  - Calls live `gpt-5.5` through `make_chat_model("vision", per_call_override="gpt-5.5")`.
  - Parses strict JSON into the v1.1 tuple axes.
  - Retries only bounded transport/parse failures.
  - Safe-degrades to plain `top_down` (`single_text_block` +
    `dense_exposition`) with `reading_path_source="safe_default"` and
    `reading_path_degraded=true`.
- Wired `app/specialists/vision/_act.py` to use the LLM-primary producer.
- Converted Irène reading-path order enforcement from production hard-block to
  observable warning telemetry (`reading_path_conformance_warnings`).
- Added `vision` to the specialist summary roster so production runs do not
  crash after the vision node emits spans.
- Updated P2-4b measurement scripts to score the LLM-primary output over the
  frozen fresh perception corpus without S3 escalation or gold relabeling.

## Live Measurement

Command:

```powershell
.venv\Scripts\python.exe scripts\analysis\reading_path_p2_4b_measure_fresh.py
```

Report:

`_bmad-output/implementation-artifacts/reading-path-holdout-rescan-2026-06-23/llm-primary-reading-path-measurement.json`

Report SHA256:

`6A3FA8C693887462FAEC18DD9550030E55A2AEAB3EAACE815F8D9C020FEC147C`

Gold SHA256:

`56473484F1D296C04D5A569865B8C6D5EE296FB55AB0AC193BAF6B9EB3DE20A8`

Result:

- Subject: `llm-primary reading-path classifier`
- Substrate: `frozen fresh@2026-06-23 role_tier-aware perceptions`
- Classified: 14/14
- Load errors: 0
- Primary-key top-1: 0.500
- Full tuple: 0.357
- Per-axis: macro 0.857, image_role 0.643, text 0.929, cadence 0.857
- Degraded rows: 0
- Hard blocks: 0

This live first-run result does not meet the old 0.85 primary-key target. It
does satisfy the remediation's production-safety property: no degraded rows and
no reading-path hard blocks during measurement.

## Production Smoke

Command sequence used the production CLI over the frozen corpus:

```powershell
.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input course-content/courses/tejal-apc-c1-m1-p2-trends --operator-id operator_juan --auto-confirm-directive --max-specialist-calls 30
.venv\Scripts\python.exe -m app.marcus.cli trial resume --trial-id 386912d6-be57-4227-a1af-3f02e9872462 --verdict-file state\config\runs\386912d6-be57-4227-a1af-3f02e9872462\verdict-G1-approve.json --max-specialist-calls 80
.venv\Scripts\python.exe -m app.marcus.cli trial resume --trial-id 386912d6-be57-4227-a1af-3f02e9872462 --verdict-file state\config\runs\386912d6-be57-4227-a1af-3f02e9872462\verdict-G2B-approve.json --max-specialist-calls 80
.venv\Scripts\python.exe -m app.marcus.cli trial resume --trial-id 386912d6-be57-4227-a1af-3f02e9872462 --verdict-file state\config\runs\386912d6-be57-4227-a1af-3f02e9872462\verdict-G2C-approve.json --max-specialist-calls 120
.venv\Scripts\python.exe -m app.marcus.cli trial recover --trial-id 386912d6-be57-4227-a1af-3f02e9872462 --max-specialist-calls 160
.venv\Scripts\python.exe -m app.marcus.cli trial resume --trial-id 386912d6-be57-4227-a1af-3f02e9872462 --verdict-file state\config\runs\386912d6-be57-4227-a1af-3f02e9872462\verdict-G3-approve.json --max-specialist-calls 160
.venv\Scripts\python.exe -m app.marcus.cli trial resume --trial-id 386912d6-be57-4227-a1af-3f02e9872462 --verdict-file state\config\runs\386912d6-be57-4227-a1af-3f02e9872462\verdict-G4-approve.json --max-specialist-calls 200
.venv\Scripts\python.exe -m app.marcus.cli trial resume --trial-id 386912d6-be57-4227-a1af-3f02e9872462 --verdict-file state\config\runs\386912d6-be57-4227-a1af-3f02e9872462\verdict-G4A-approve.json --max-specialist-calls 200
```

Final run registry:

`state/config/runs/386912d6-be57-4227-a1af-3f02e9872462/run.json`

Result:

- Status: `completed`
- Paused gate: `null`
- Paused error tag: `null`
- Vision contributions: 1
- Perception artifacts: 6
- Reading-path sources: `llm_primary`
- Reading-path degraded count: 0

During the first G2C resume, the run reached vision and then exposed two
production-blocking seams unrelated to LLM tuple generation:

1. `vision` was missing from the specialist summary roster.
2. Irène still hard-blocked on reading-path order conformance.

Both are patched in this remediation. The recovered run then completed.

## Validation

```powershell
.venv\Scripts\python.exe -m ruff check app\specialists\vision\_act.py app\specialists\irene\graph.py app\models\state\specialist_summary_artifacts.py app\models\perception\perception_artifact.py app\models\perception\__init__.py scripts\utilities\reading_path_classifier.py scripts\analysis\reading_path_p2_4b_measure_fresh.py scripts\analysis\reading_path_p2_4b_run.py tests\specialists\vision\test_vision_provider_and_act.py tests\specialists\vision\test_vision_unclassifiable_error_pause.py tests\specialists\vision\test_reading_path_classifier.py tests\specialists\irene\test_irene_reading_path_conformance.py tests\models\perception\test_perception_artifact_schema_parity.py
```

Result: pass.

```powershell
.venv\Scripts\python.exe -m pytest tests\specialists\vision\test_vision_provider_and_act.py tests\specialists\vision\test_vision_unclassifiable_error_pause.py tests\specialists\irene\test_irene_reading_path_conformance.py tests\models\perception\test_perception_artifact_schema_parity.py tests\specialists\vision\test_reading_path_classifier.py tests\specialists\vision\test_image_role_tiers.py tests\analysis\test_reading_path_p2_4b_run.py tests\analysis\test_reading_path_p2_4b_score.py
```

Result: 120 passed.

Earlier focused run before updating the legacy vision hard-block tests:

- 100 passed across Irène reading-path, perception schema parity, classifier,
  image-role tiers, and P2-4b analysis tests.

## Baseline-Diff Attestation

- Did not edit `claude-goal.txt`; it was already dirty in the worktree.
- Did not edit prompt packs or manifests.
- New generated/runtime artifacts from the production smoke exist under
  `state/config/runs/386912d6-be57-4227-a1af-3f02e9872462`, `runs/`, and
  `exports/`.
- The LLM-primary measurement report is intentionally added under
  `_bmad-output/implementation-artifacts/reading-path-holdout-rescan-2026-06-23/`.
