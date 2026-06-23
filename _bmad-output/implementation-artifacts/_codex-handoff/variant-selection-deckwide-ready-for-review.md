# Variant Selection Deckwide Remediation - Ready for Review

Date: 2026-06-23

## Scope Executed

Canonical prompt: `_bmad-output/implementation-artifacts/codex-dev-prompt-variant-selection-deckwide.md`

Implemented D1/D3/D7 remediation:

- Deck-wide G2B selected variant now filters Gary `gary_slide_output` by `dispatch_variant` before downstream production consumption.
- The filter fails loud on absent Gary rows, zero selected matches, missing `slide_id`, or duplicate selected rows per slide.
- Gamma settings remain under the existing `gamma_settings` carrier; no new top-level payload key was added.
- Theme resolution/validation now resolves name or id against `list_themes(limit=theme_limit)` and fails loud for absent themes.
- Gamma control surface now validates and emits reachable text/image/card knobs for both standard and per-variant production paths.
- `DEFAULT_VARIANT_PAIR` is locked to the required A/B looks.
- Gamma 401 retry is scoped only to warm `/generations` POSTs after successful auth validation.

## T1 Seam Report

- `gary_slide_output` rows carry `dispatch_variant`.
- G2B is node `07B-gate`; G2C is `07C`; vision/perception starts after `07F` at `07G`.
- The production filter belongs after G2B selection merge and before downstream graph consumption of Gary output.
- Irene `_slide_roster` consumes all `gary_slide_output`; unfiltered A/B output would double the roster.
- `gamma_settings` is the existing carrier; no new top-level payload key is required.

## Before / After

Before:

- G2B could record `selected_variant_id`, but downstream production still saw both A and B Gary rows.
- Variant Gamma settings supported only the narrow arc knobs.
- Theme validation and 401 retry behavior were not centralized enough for this prompt.

After:

- Selected deck-wide variant produces exactly one Gary row per `slide_id` before downstream production.
- Absent `selected_variant_id` is a no-op for legacy/single-dispatch runs.
- Full Gamma setting validation/dispatch covers text amount, tone, audience, language, text mode, image source/model/stylePreset/style, dimensions, and keywords.
- `stylePreset` and `style` are coherent: named presets do not emit `style`; `custom` may emit `style`.

## RED Transcript

Command:

```powershell
@'
rows = [
    {"slide_id": "slide-01", "dispatch_variant": "A", "file_path": "a1.png"},
    {"slide_id": "slide-01", "dispatch_variant": "B", "file_path": "b1.png"},
]
selected_variant_id = "B"
# Pre-filter behavior: selected_variant_id is recorded but no production-envelope filter consumes it.
assert rows == [r for r in rows if r.get("dispatch_variant") == selected_variant_id], rows
'@ | .venv\Scripts\python.exe -
```

Output:

```text
Traceback (most recent call last):
  File "<stdin>", line 7, in <module>
AssertionError: [{'slide_id': 'slide-01', 'dispatch_variant': 'A', 'file_path': 'a1.png'}, {'slide_id': 'slide-01', 'dispatch_variant': 'B', 'file_path': 'b1.png'}]
```

## Verification

Passed:

- `ruff check` on touched Python files: all checks passed.
- `pytest tests\unit\marcus\orchestrator\test_deckwide_variant_selection_filter.py tests\specialists\gary\test_gary_gamma_dispatch.py tests\unit\api_clients\test_gamma_client_generation_id.py tests\test_creative_directive_schema.py tests\test_creative_directive_validator.py tests\unit\marcus\orchestrator\test_card_candidate_binding.py tests\integration\marcus\test_production_runner_threads_directive.py tests\unit\marcus\orchestrator\test_select_verb_binding.py -q`: 60 passed.
- `pytest tests\integration\marcus\test_beta_picker_contract_ratchet.py tests\integration\marcus\test_woken_gate_cards.py tests\unit\marcus\cli\test_marcus_spoc_narration.py tests\unit\marcus\orchestrator\test_card_candidate_binding.py -q`: 17 passed.
- `pytest tests\integration\marcus\test_package_builders.py tests\integration\marcus\test_storyboard_publisher.py tests\integration\marcus\test_storyboard_generator_seam_handshake.py -q`: 29 passed.

Evidence covered:

- Deck-wide selected B filter keeps only B rows and recomputes the Gary contribution digest.
- Absent selection preserves byte-identity of the envelope object.
- Zero-match and duplicate selected slide rows fail loud.
- No-settings single dispatch preserves the existing Gamma call shape.
- Theme name resolution passes; absent real-looking theme fails before generation.
- Closed enum validation fails before generation.
- Named `stylePreset` suppresses free-form `style`; `custom` emits both.
- Warm `/generations` 401 retries; cold 401 fails fast without sleep.

## Byte Identity / Baseline Diff

- No diff in `state/config/pipeline-manifest.yaml`.
- No diff in `docs/workflow/production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md`.
- No diff in `.cursor/rules/bmad-sprint-governance.mdc`, `.github/copilot-instructions.md`, or `CLAUDE.md`.
- No Studio/Playwright path was introduced.
- No theme-picker path was introduced.
- No new top-level production payload key was introduced.

## B Gating

Structural B dispatch/remediation is implemented and covered by unit/integration tests.

Live B 201 plus visual eye-check is still gated because `GAMMA_API_KEY` is missing in this environment. That live leg should remain blocked until a validated key is available.

