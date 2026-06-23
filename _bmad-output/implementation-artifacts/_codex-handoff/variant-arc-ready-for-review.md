# Variant Arc Ready for Review

Date: 2026-06-23

Canonical prompt:

- `_bmad-output/implementation-artifacts/codex-dev-prompt-variant-arc.md`

Spec:

- `_bmad-output/implementation-artifacts/spec-variant-arc-per-variant-gamma-settings.md`

## T1 Keying Report

- Gary's current generated rows already carry `dispatch_variant`.
- Export normalization already writes variant-labeled artifacts through `module_lesson_part=variant`; with variants A/B the materialized paths include the variant label.
- Storyboard/G2B already has a selectable `selected_variant_id` seam and projects variants from `gary_slide_output`.
- Gary previously read a single global `theme_id` and did not accept a per-variant settings dict.
- The real work in this pass was therefore adding optional directive-threaded `gamma_settings`, binding those settings per Gamma call, surfacing them at G2B, and preserving the absent-settings single-dispatch path.

## Implementation

- Added optional `gamma_settings` to both creative-directive schemas.
- Kept `theme`, `template`, and `image_style` open strings with documented known values.
- Kept `density` and `tone` as closed schema values.
- Updated the creative-directive validator for additive `gamma_settings` validation.
- Added Gary `DEFAULT_VARIANT_PAIR` as the smoke fixture pair:
  - A: `photographic`
  - B: `diagrammatic`
  - theme/template/density/tone held constant by default.
- Added Gary per-variant dispatch:
  - Presence of `gamma_settings` dispatches fixed variants A/B.
  - Partial settings fall back per variant to `DEFAULT_VARIANT_PAIR`.
  - Absence of `gamma_settings` preserves the existing single-dispatch behavior unless the legacy `double_dispatch` flag is set.
  - Per-variant settings flow into `theme_id`, `image_options.style`, `text_options.amount`, and `text_options.tone`.
- Added runner-side directive extraction:
  - Gary receives `gamma_settings` from `directive.yaml` only when present.
  - Missing/null settings are omitted from runner payload.
- Added G2B card surfacing:
  - `G2BCard.gamma_settings`
  - `pick_context` entry `{"kind": "gamma-settings", ...}`
  - Per-slide variant options now include each row's `gamma_settings`.

## Before / After

Before:

- No CD directive `gamma_settings` field.
- Gary had no per-variant settings input.
- Gary used a single global theme resolution for all calls.
- G2B surfaced variant ids and artifacts, but not the settings that produced them.

After:

- CD directives can optionally carry per-variant Gamma settings.
- Gary dispatches A/B with distinct per-variant settings when the field is present.
- G2B surfaces the settings alongside variant candidates.
- No-settings path remains single-dispatch and omits `gamma_settings` from runner payload.

## Validation

Ruff:

```powershell
.venv\Scripts\python.exe -m ruff check app\specialists\gary\_act.py app\specialists\gary\payload_contract.py app\marcus\orchestrator\production_runner.py app\models\decision_cards\g2b.py scripts\utilities\creative_directive_validator.py tests\specialists\gary\test_gary_gamma_dispatch.py tests\test_creative_directive_schema.py tests\unit\marcus\orchestrator\test_card_candidate_binding.py tests\integration\marcus\test_production_runner_threads_directive.py
```

Result:

- All checks passed.

Focused tests:

```powershell
.venv\Scripts\python.exe -m pytest tests\specialists\gary\test_gary_gamma_dispatch.py tests\test_creative_directive_schema.py tests\test_creative_directive_validator.py tests\unit\marcus\orchestrator\test_card_candidate_binding.py tests\integration\marcus\test_production_runner_threads_directive.py tests\unit\marcus\orchestrator\test_select_verb_binding.py -q
```

Result:

- 48 passed.

Nearby G2B/storyboard regression:

```powershell
.venv\Scripts\python.exe -m pytest tests\integration\marcus\test_beta_picker_contract_ratchet.py tests\integration\marcus\test_woken_gate_cards.py tests\unit\marcus\cli\test_marcus_spoc_narration.py tests\unit\marcus\orchestrator\test_card_candidate_binding.py -q
```

Result:

- 17 passed.

Package/storyboard publishing regression:

```powershell
.venv\Scripts\python.exe -m pytest tests\integration\marcus\test_package_builders.py tests\integration\marcus\test_storyboard_publisher.py tests\integration\marcus\test_storyboard_generator_seam_handshake.py -q
```

Result:

- 29 passed.

## Live Gamma Smoke

Status: blocked in this environment.

Reason:

- `GAMMA_API_KEY` is not present.

Evidence available:

- Mechanical per-variant dispatch tests prove two Gamma calls with distinct settings and distinct variant-keyed artifacts through the real Gary payload assembly, with the HTTP edge stubbed.

Evidence not available:

- No live Gamma two-render artifact hashes or paths were produced in this run.
- No operator eye-check at G2C was performed.

## Baseline-Diff Attestation

- No `state/config/pipeline-manifest.yaml` edit.
- No v4.2/v5 prompt-pack edit.
- No four-file lockstep edit.
- No slide-id special casing.
- No generalized N-variant fan-out; implementation remains fixed to A/B when `gamma_settings` is present.
- Existing dirty worktree state from earlier remediation was preserved.
