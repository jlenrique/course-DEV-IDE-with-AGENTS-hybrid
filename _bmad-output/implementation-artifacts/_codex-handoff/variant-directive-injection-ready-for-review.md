# Variant Directive Injection - Ready For Review

Date: 2026-06-23

Source prompt: `_bmad-output/implementation-artifacts/codex-dev-prompt-variant-directive-injection.md`

## T1 Report

- `app/composers/section_02a/directive_model.py` `Directive` uses `ConfigDict(extra="forbid", validate_assignment=True)` and previously had no `gamma_settings` field.
- `write_directive_yaml` serializes `Directive.model_dump(mode="json")`; the implementation keeps existing null-field output stable and removes only `gamma_settings` when it is `None`.
- `_gamma_settings_from_directive` in `production_runner.py` already reads the raw YAML key `gamma_settings`, so the model field serializes under that exact name.
- Touched files are data-plane only: no pack/manifest/4-file-lockstep path was touched.

## Before / After

Before:

- `compose_and_write(..., gamma_settings=...)` was not accepted.
- `Directive` rejected `gamma_settings` because extras are forbidden.
- Trial start had no `--gamma-settings-file` seam.

After:

- `Directive.gamma_settings` is additive and optional.
- `Directive.model_dump(mode="json")` omits `gamma_settings` when `None`.
- `compose_and_write` overlays `gamma_settings` before `write_directive_yaml`; the digest is computed over the final directive.
- `trial start --gamma-settings-file <path>` loads a YAML/JSON list of objects and threads it into `compose_and_write`.
- Absent CLI flag threads `None` and preserves legacy directive bytes.

## RED Transcript

Command:

```powershell
.venv\Scripts\python.exe -m pytest tests\composers\section_02a\test_composer_directive_model_shape.py tests\marcus_cli\test_compose_section_02a_directive_adapter.py tests\marcus_cli\test_cli_adapter_run_id_thread_through.py tests\integration\marcus\test_production_runner_threads_directive.py -q
```

Pre-fix result:

```text
5 failed, 18 passed

- KeyError: 'gamma_settings' in start-trial compose kwargs
- TypeError: start_trial() got an unexpected keyword argument 'gamma_settings_file'
- KeyError: 'gamma_settings_file' in start_trial_cli threading
- ValidationError: gamma_settings extra input forbidden on Directive
- TypeError: compose_and_write() got an unexpected keyword argument 'gamma_settings'
```

Post-fix result:

```text
23 passed
```

## Test Results

Passed:

- `ruff check` on touched Python/tests: all checks passed.
- `lint-imports`: 15 kept, 0 broken.
- Targeted RED suite: `23 passed`.
- Section 02A / CLI focused suite: `67 passed, 18 skipped`.
- Real-path trial-475 threading pin: `1 passed`.
- Contracts baseline: `278 passed, 1 skipped, 14 failed` (same ambient contract debt class observed before this prompt; failures are unrelated to the directive-injection seam).

Known ambient failures seen during broader checks:

- Forensic fixture hash mismatch in `test_section_02a_to_wrangler_subprocess_roundtrip.py`.
- Existing contract-suite failures around provider roster status, missing `marcus/lesson_plan/schema/*`, transform-registry exemptions, state-config key collisions, 30-1 zero-edit pin, and retired `marcus` namespace/log-boundary checks.

## Legacy Byte Identity

Pre-change no-`gamma_settings` golden was captured before implementation:

```text
sha256 06b587cc99b654967409b5170c5c532c6c7cb3d16d2ebb6b7e463afe173b5b57
```

Pinned output remains:

```yaml
run_id: 11111111-1111-4111-8111-111111111111
corpus_dir: C:/tmp/corpus
sources:
- ref_id: src-001
  locator: lesson.md
  provider: local_file
  role: primary
  description: Primary lesson source.
  expected_min_words: 500
  excluded_reason: null
composed_at: '2026-06-23T12:00:00Z'
schema_version: 1
```

No `gamma_settings` key is emitted when absent.

## Sample

Sample `gamma-settings.yaml`:

```yaml
- variant_id: A
- variant_id: B
```

Resulting directive excerpt:

```yaml
gamma_settings:
- variant_id: A
- variant_id: B
```

That raw key is read by `_gamma_settings_from_directive` and reaches Gary's runner payload as:

```python
[{"variant_id": "A"}, {"variant_id": "B"}]
```

## Fences

- No diff in `state/config/pipeline-manifest.yaml`.
- No diff in `docs/workflow/production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md`.
- No diff in `.cursor/rules/bmad-sprint-governance.mdc`, `.github/copilot-instructions.md`, or `CLAUDE.md`.
- No new top-level runtime payload key beyond the already-declared `gamma_settings`.
- No pack/manifest/lockstep edit.

