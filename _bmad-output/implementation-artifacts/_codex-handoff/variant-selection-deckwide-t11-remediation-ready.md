# Variant Selection Deckwide T11 Remediation - Ready

Date: 2026-06-23

Source prompt: `_bmad-output/implementation-artifacts/codex-remediation-prompt-variant-selection-deckwide-t11.md`

## Scope Executed

Claude T11 handed back one MUST-FIX plus a SHOULD-FIX guard cluster. The original deck-wide selection mechanism was not reworked; this pass only tightened the missing invariants and validators:

- MF-1: selected variant filtering now asserts the surviving slide set equals the original pre-filter slide set.
- SF-1/SF-2: Gamma enum sentinel handling is per-knob, not global.
- SF-3: `image_style_preset="custom"` now requires a non-empty `image_style`.
- SF-4: non-list `keywords` now fails before generation.
- SF-5: parseable-but-non-dict `cache_prefix` now raises instead of silently disabling selection.
- NIT: per-variant theme resolution now reuses the already fetched `list_themes()` window.

## Before / After

Before:

- A partial-coverage selection could silently drop a slide if that slide existed only in the non-selected variant.
- Values such as `dimensions="auto"`, `language="balanced"`, `text_mode="auto"`, and `image_model="balanced"` skipped validation and could reach Gamma.
- `custom` image style preset could be emitted without a prompt.
- `keywords` as a string was accepted and later dropped.
- `cache_prefix="[]"` or `"123"` returned `None`, producing a no-op.

After:

- Selected variants must retain exactly one row for every original `slide_id`; missing slide IDs are named in `VariantSelectionError`.
- Each enum knob only omits values that are legitimate for that knob.
- Bad enum/theme/custom/keywords inputs raise before any Gamma generation call.
- Corrupted parseable non-object cache prefixes raise `VariantSelectionError`.

## RED Transcript

Command:

```powershell
.venv\Scripts\python.exe -m pytest tests\unit\marcus\orchestrator\test_deckwide_variant_selection_filter.py tests\specialists\gary\test_gary_gamma_dispatch.py::test_gary_enum_validation_blocks_bad_knobs_before_generation tests\specialists\gary\test_gary_gamma_dispatch.py::test_gary_custom_style_preset_requires_non_empty_style tests\specialists\gary\test_gary_gamma_dispatch.py::test_gary_keywords_must_be_a_list_before_generation -q
```

Pre-fix result:

```text
8 failed, 7 passed

Failed: DID NOT RAISE VariantSelectionError
- test_deckwide_variant_selection_rejects_partial_selected_coverage
- test_deckwide_variant_selection_rejects_parseable_non_dict_cache_prefix

Failed: DID NOT RAISE GaryActError
- image_model="balanced"
- dimensions="auto"
- language="balanced"
- text_mode="auto"
- custom preset without image_style
- keywords as a string
```

Post-fix targeted result:

```text
15 passed in 6.92s
```

## Verification

Passed:

- `ruff check` on touched Python files: all checks passed.
- Focused remediation suite: `71 passed`.
- Adjacent Marcus/G2B suite: `17 passed`.
- Storyboard/package suite: `29 passed`.
- Contract suite: `278 passed, 1 skipped, 14 failed`.

The 14 contract failures match the ambient contract debt identified by T11 (`tests/contracts/` baseline-diff attestation); this remediation introduced zero new contract-red categories.

## AC Evidence

- MF-1: partial selected coverage now raises and names the dropped `slide_id`.
- Existing filter cases remain green: doubled A/B filtered, absent pick no-op, zero-match fail-loud, duplicate selected row fail-loud.
- SF-1/SF-2: bad values for `amount`, `image_style_preset`, `image_model`, `image_source`, `dimensions`, `language`, and `text_mode` all raise `gamma.settings.invalid` before generation; `client.generate_calls == []`.
- Theme bad-input path still raises before generation via `gamma.theme.invalid`.
- SF-3: bare `custom` preset without `image_style` raises before generation.
- SF-4: non-list `keywords` raises before generation.
- SF-5: valid JSON non-dict `cache_prefix` raises `VariantSelectionError`.
- Theme resolver uses one fetched theme window for run-level and per-variant validation.

## Byte-Identity Wording

Corrected statement: the legacy no-`gamma_settings` Gamma wire request remains unchanged on the no-settings path. The returned receipt dict intentionally has additive `gamma_settings`/`variant_gamma_settings` metadata from the variant-control work; the unchanged guarantee is the Gamma request shape, not byte-identical receipt output.

## Fences

- No diff in `state/config/pipeline-manifest.yaml`.
- No diff in `docs/workflow/production-prompt-pack-v5-narrated-lesson-with-video-or-animation.md`.
- No diff in `.cursor/rules/bmad-sprint-governance.mdc`, `.github/copilot-instructions.md`, or `CLAUDE.md`.
- No new top-level payload key.
- No pack/manifest/lockstep edit.
- Live Gamma legs remain operator-gated; B live gate was already cleared per T11 review.

