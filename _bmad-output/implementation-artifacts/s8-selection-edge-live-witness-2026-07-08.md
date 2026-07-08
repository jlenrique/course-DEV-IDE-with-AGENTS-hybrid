# S8 Selection Edge Live Witness - 2026-07-08

## Scope

First production runtime slice for:

`ratified lesson-plan collateral intent -> curated bundle catalog -> ComponentSelection -> existing production runner / compose_manifest path`

No new composer was added. HAI/PHS remote course content was not ingested.

## Implementation

- Added `app/marcus/lesson_plan/collateral_selection.py`.
- Wired local `trial start --lesson-plan-collateral-intent <path>` through the existing `ComponentSelection` seam in `app/marcus/cli/trial.py`.
- Added `component_selection` to `run_summary.yaml` for runtime receipt clarity.
- Preserved manual/default path when intent is absent or unratified.
- Ratified intent wins only after closed local validation; conflicting explicit selection fails before run artifacts.

## Verification

Focused regression:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/marcus/lesson_plan/test_collateral_selection.py tests/integration/marcus/test_trial_cli.py tests/integration/marcus/test_front_door_selection_threading.py -q
```

Result: `25 passed in 9.27s`.

Lint:

```powershell
.\.venv\Scripts\python.exe -m ruff check app\marcus\lesson_plan\collateral_selection.py app\marcus\cli\trial.py app\marcus\orchestrator\production_runner.py tests\marcus\lesson_plan\test_collateral_selection.py tests\integration\marcus\test_trial_cli.py tests\integration\marcus\test_front_door_selection_threading.py
```

Result: `All checks passed!`.

## Live Local Runtime Witness

Standalone CLI witnesses ran under the repo venv with `MARCUS_G0_ENRICHMENT_ACTIVE=0` to keep the file-corpus fixture on the same local-runtime path used by existing integration tests.

Witness root:

`C:\Users\juanl\Documents\GitHub\course-DEV-IDE-with-AGENTS-hybrid\.tmp\s8-selection-edge-live-witness`

Positive ratified workbook intent:

- Trial id: `12345678-1234-4234-8234-123456789abd`
- Receipt: `.tmp/s8-selection-edge-live-witness/runs/12345678-1234-4234-8234-123456789abd/trial-start.json`
- `lesson_plan_collateral_bundle_id`: `narrated-deck-with-workbook`
- `run_summary.yaml component_selection`: `{deck: true, motion: true, workbook: true}`

Absent intent default:

- Trial id: `12345678-1234-4234-8234-123456789abe`
- Receipt: `.tmp/s8-selection-edge-live-witness/runs-absent/12345678-1234-4234-8234-123456789abe/run_summary.yaml`
- `run_summary.yaml component_selection`: `{deck: true, motion: true, workbook: false}`

Invalid ratified intent:

- Trial id: `12345678-1234-4234-8234-123456789abf`
- Exit code: `1`
- Error: `closed ratified intent validation failed`
- `run.json` exists: `False`

## Review Disposition

BMAD lanes found and the implementation remediated:

- Unratified intent must not override or conflict with manual/default selection.
- CLI must not consult front-door readiness before ratified intent precedence.
- CLI must not double-load the intent file.
- Invalid UTF-8/YAML intent files must stay inside `CollateralSelectionError`.
- Run-summary comments and tests must reflect composed-graph audit semantics.

Post-remediation focused verification is green.
