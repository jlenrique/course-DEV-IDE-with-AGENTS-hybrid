# Resume Directive Path Threading - Ready for Review

## Scope

Executed canonical prompt:
`_bmad-output/implementation-artifacts/codex-dev-prompt-resume-directive-path-threading.md`.

## T1 Precondition Report

- Confirmed persistence gap: gate checkpoints were written by `_write_checkpoint(...)` without `runner.directive_path` or `runner.bundle_dir`; `trial-start.json`/start context could have the directive while `checkpoint.json` did not.
- Confirmed resume read site: `resume_production_trial(...)` loaded `runner = checkpoint.get("runner") or {}` and called `_continue_production_walk(...)` without a directive path, so resumed dispatches saw `directive_path=None`.
- Confirmed recovery read site: `recover_production_trial(...)` read `runner.directive_path`/`runner.bundle_dir` directly from error-pause state. Error-pause already persisted them, but now shares the fallback resolver.
- Confirmed canonical path: `runs_root / str(trial_id) / "directive.yaml"`.
- Confirmed touched code is data-plane runner code in `app/marcus/orchestrator/production_runner.py`; no workflow-runner/block-mode trigger path edits.

## RED Transcript

Command:

```powershell
.venv\Scripts\python.exe -m pytest tests\integration\marcus\test_production_runner_resume_continues_execution.py -k "directive_path or reconstructs_canonical or legacy_payload" -q
```

Result before implementation:

- `test_gate_checkpoint_persists_directive_path_for_resume` failed with `KeyError: 'directive_path'`.
- `test_resume_reconstructs_canonical_directive_path_for_texas_and_gary` failed because resumed Texas payload was `None`.
- `test_resume_without_gamma_settings_preserves_gary_legacy_payload` passed.

## Implementation

- `_write_checkpoint(...)` now persists `runner.directive_path` and `runner.bundle_dir`.
- `_pause_at_gate(...)` now accepts and forwards directive/bundle values, covering start pauses and every later resume pause.
- Added canonical fallback helpers:
  - `_canonical_directive_path(...)`
  - `_resolve_resume_directive_path(...)`
  - `_resolve_resume_bundle_dir(...)`
- `resume_production_trial(...)` resolves the directive/bundle before `_continue_production_walk(...)`.
- `recover_production_trial(...)` uses the same resolver, preserving existing error-pause behavior while adding canonical fallback.

## Tests Added

- `test_gate_checkpoint_persists_directive_path_for_resume`
- `test_resume_reconstructs_canonical_directive_path_for_texas_and_gary`
- `test_resume_without_gamma_settings_preserves_gary_legacy_payload`

These exercise the real `resume_production_trial(...)` path, not only `_runner_payload_for_specialist(...)`.

## Verification

```powershell
.venv\Scripts\python.exe -m pytest tests\integration\marcus\test_production_runner_resume_continues_execution.py -k "directive_path or reconstructs_canonical or legacy_payload" -q
# 3 passed

.venv\Scripts\python.exe -m pytest tests\integration\marcus\test_production_runner_resume_continues_execution.py tests\integration\marcus\test_production_runner_threads_directive.py -q
# 14 passed

.venv\Scripts\python.exe -m pytest tests\integration\marcus\test_production_runner_gate_pause_resume.py tests\integration\marcus\test_production_runner_resume_invariants.py -q
# 11 passed

.venv\Scripts\python.exe -m pytest tests\unit\marcus\orchestrator\test_deckwide_variant_selection_filter.py tests\specialists\gary\test_gary_gamma_dispatch.py tests\unit\api_clients\test_gamma_client_generation_id.py -q
# 30 passed

.venv\Scripts\ruff.exe check app\marcus\orchestrator\production_runner.py tests\integration\marcus\test_production_runner_resume_continues_execution.py
# All checks passed

.venv\Scripts\lint-imports.exe
# 15 kept, 0 broken
```

Full contracts suite remains at the known unrelated baseline:

```powershell
.venv\Scripts\python.exe -m pytest tests\contracts -q
# 278 passed, 1 skipped, 14 failed
```

## Baseline Guard

Protected baseline diff check returned no files:

```powershell
git diff --name-only -- state/config/pipeline-manifest.yaml docs/workflow/production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md .cursor/rules/bmad-sprint-governance.mdc .github/copilot-instructions.md CLAUDE.md
```

## Review Notes

- Gary on resume receives `gamma_settings` when canonical `directive.yaml` contains them, enabling both A and B variant dispatch downstream.
- Texas on resume receives canonical `directive_path` and `bundle_dir`.
- Legacy directives without `gamma_settings` keep Gary's prior single-payload behavior: only `export_dir` is supplied.
