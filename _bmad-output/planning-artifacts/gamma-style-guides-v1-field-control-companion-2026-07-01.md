# Gamma Style Guides V1 Field-Control Companion

Companion for `_bmad-output/planning-artifacts/gamma-style-guides-v1-draft-2026-07-01.yaml`.

This document is the control dictionary for the draft registry. The YAML should remain the compact data artifact: it stores the actual selected values for each style. This companion explains what each field means, what value choices exist, whether Gamma documents API control for those values, and whether this repo currently wires that control through Gary/runtime.

## Sources

- Gamma generate-from-text API guide: https://developers.gamma.app/guides/generate-api-parameters-explained
- Gamma generate-from-template API guide: https://developers.gamma.app/guides/create-from-template-api-parameters-explained
- Gamma header/footer formatting guide: https://developers.gamma.app/guides/header-and-footer-formatting
- Local client: `scripts/api_clients/gamma_client.py`
- Local Gary dispatcher/normalizer: `app/specialists/gary/_act.py`

## Control Status Legend

- `metadata`: Registry, provenance, validation, or operator-facing context. Not sent to Gamma.
- `runtime_policy`: Controls local runtime behavior or selection of API path.
- `documented+wired`: Documented by Gamma and currently wired through local Gary/client.
- `documented+client-only`: Documented by Gamma and passable by the raw client, but not exposed by Gary normalization/dispatch today.
- `documented+unwired`: Documented by Gamma, but not currently represented in local runtime wiring.
- `compiled`: Registry value must be transformed into one or more API fields or prompt instructions.
- `theme/template-owned`: Controlled by selected Gamma theme or template design, not by a documented per-request field.
- `ui-or-unknown`: Visible in Gamma UI or desired by operator, but no documented per-request API mapping is currently known.

Important correction from API docs: for `format: presentation`, documented `cardOptions.dimensions` values are `fluid`, `16x9`, and `4x3`. `letter`/`a4` are document-format dimensions; `1x1`/`4x5`/`9x16` are social-format dimensions. Custom aspect ratios and pixel dimensions are not documented as accepted API values.

## Registry Implementation Status Keywords

The registry may use a deliberately small `implementation_status` vocabulary at field level when useful, but option/value catalogs belong here or in a future machine schema rather than being repeated inside each style row.

| Keyword | Meaning |
| --- | --- |
| `in_use` | Currently wired and active in the local production path. |
| `available` | Documented or locally passable programmatic control exists, but this field/value is not necessarily active in the current production path. |
| `format_limited` | Programmatic control exists only for compatible Gamma formats, not necessarily for presentation decks. |
| `template` | Control should be supplied by Gamma theme/template design unless future API proof says otherwise. |
| `TBD` | No confirmed programmatic control path yet. |

## Value Catalog Placement

- Registry YAML rows should store selected values only.
- This companion should list human-readable value choices and UI-to-API translations.
- A future validator/schema should enforce machine-checkable allowed values.
- Vendor-owned enum lists should generally be linked to Gamma docs unless the app has an important translation or production rule to preserve.

## Registry-Level Fields

| YAML field | Status | Programmatic control / implementation note |
| --- | --- | --- |
| `schema_version` | metadata | Registry schema marker. Local validator should require exact supported version before promotion. |
| `status` | metadata | Draft/lifecycle marker for the registry file itself. Not sent to Gamma. |
| `registry_owner` | metadata | Ownership marker. CD/Dan-authored content should be promoted by governed runtime, not mutated directly by agents. |
| `runtime_target_path` | metadata | Planned production path, currently `state/config/gamma-style-guides.yaml`. Not runtime-active yet. |
| `source_design` | metadata | Provenance wrapper for why this registry exists. |
| `source_design.briefing` | metadata | Points to the design briefing that seeded the registry. |
| `source_design.seed_sources` | metadata | Lists existing local artifacts used to seed registry values. |

## Validation-Policy Fields

| YAML field | Status | Programmatic control / implementation note |
| --- | --- | --- |
| `validation_policy` | metadata/runtime_policy | Future validator contract; not consumed by Gary today. |
| `validation_policy.required_roster` | metadata/runtime_policy | Minimum roster expectations for a usable library. |
| `validation_policy.required_roster.min_style_guides` | runtime_policy | Future validator should enforce count. |
| `validation_policy.required_roster.min_classic_api_guides` | runtime_policy | Future validator should enforce at least one Classic `/generations` style. |
| `validation_policy.required_roster.min_studio_guides` | runtime_policy | Future validator should enforce at least one template/from-template style. |
| `validation_policy.completeness` | metadata/runtime_policy | Future completeness rules. |
| `validation_policy.completeness.null_or_default_fails_required_fields` | runtime_policy | Future validator should fail required values that are null/default placeholders. |
| `validation_policy.completeness.required_fields_are_surface_relative` | runtime_policy | Required fields depend on generation method; Classic and Studio have different surfaces. |
| `validation_policy.api_surface` | metadata/runtime_policy | Future API-surface rules. |
| `validation_policy.api_surface.allowed_generation_methods` | runtime_policy | Should map to local `classic_generation` and `template_generation`; local Gary currently calls them `api` and `studio`. |
| `validation_policy.api_surface.api_requires` | runtime_policy | Future validator should require theme/prompt/page settings for Classic styles. |
| `validation_policy.api_surface.studio_requires` | runtime_policy | Future validator should require template id, prompt lock, and export for Studio styles. |
| `validation_policy.api_surface.studio_forbids_classic_only_fields` | runtime_policy | Protects from sending Classic-only settings to `/generations/from-template`. |
| `validation_policy.provenance` | metadata/runtime_policy | Future provenance requirements. |
| `validation_policy.provenance.require_brand_binding` | runtime_policy | Future validator should require brand/source reference. |
| `validation_policy.provenance.require_styleguide_version` | runtime_policy | Future validator should require versioned style entries. |
| `validation_policy.provenance.require_origin_notes` | runtime_policy | Future validator should require human-readable origin rationale. |
| `validation_policy.live_proof` | runtime_policy | Promotion gates for live Gamma proof. |
| `validation_policy.live_proof.require_theme_or_template_existence_check` | runtime_policy | Should use `list_themes()` for themes; template existence likely requires live from-template probe or Gamma-side lookup if API exposes one. |
| `validation_policy.live_proof.require_differential_no_vacuous_green` | runtime_policy | Future proof must show styles differ materially, not just pass with identical output. |
| `validation_policy.live_proof.require_operator_eye_look_verdict` | runtime_policy | Human visual approval remains required for style quality. |

## Column-Model Fields

| YAML field | Status | Programmatic control / implementation note |
| --- | --- | --- |
| `column_model` | metadata | Human-readable flat-row model for reviewing style guides. Not sent to Gamma. |
| `column_model.note` | metadata | Explains the table model. |
| `column_model.field_types` | metadata | Defines the status taxonomy inside the YAML. |
| `column_model.field_types.api_field` | metadata | Means direct Gamma API field. |
| `column_model.field_types.api_documented_unwired` | metadata | Means documented API field not yet exposed by Gary. |
| `column_model.field_types.compiled_field` | metadata | Means local compiler must translate value before dispatch. |
| `column_model.field_types.runtime_policy` | metadata | Means local runtime behavior rather than Gamma field. |
| `column_model.field_types.metadata` | metadata | Means registry-only context. |
| `column_model.field_types.theme_or_template_owned` | metadata | Means controlled by theme/template selection or design. |
| `column_model.field_types.manual_or_ui_only` | metadata | Means no known current programmatic control. |
| `column_model.columns` | metadata | Dictionary of review-row field definitions. |
| `column_model.columns.<column>.field_type` | metadata | Local classification only. |
| `column_model.columns.<column>.gamma_mapping` | metadata | Intended Gamma API mapping or null. |
| `column_model.columns.<column>.applies_to` | metadata | Generation methods where the field is valid. |
| `column_model.columns.<column>.note` | metadata | Human guidance; not sent to Gamma. |

## Draft-Row / Flat Style Fields

These fields appear under `draft_rows[]` and correspond to `column_model.columns.*`.

| YAML field | Status | Programmatic control / implementation note |
| --- | --- | --- |
| `draft_rows[].style_guide_id` | metadata | Stable registry key. Should become the operator/Gary selector. |
| `draft_rows[].display_name` | metadata | Human label. Not sent to Gamma. |
| `draft_rows[].status` | metadata | Lifecycle state of a style row. |
| `draft_rows[].version` | metadata | Version of style definition. |
| `draft_rows[].generation_method` | runtime_policy | Selects Classic `/generations` vs template `/generations/from-template`. Local Gary currently uses `production_mode: api/studio`; registry compiler must bridge names. |
| `draft_rows[].intended_use` | metadata | CD/operator context. |
| `draft_rows[].theme_id` | documented+wired | Maps to `themeId`. Local Gary validates requested theme through `list_themes()` for Classic; from-template client also accepts `theme_id`. |
| `draft_rows[].theme_name` | metadata | Human label for theme. |
| `draft_rows[].template_id` | documented+wired | Maps to `gammaId` for `/generations/from-template`. Local Studio mode uses `studio_template_id`. |
| `draft_rows[].template_name` | metadata | Human label for template. |
| `draft_rows[].live_example_url` | metadata | Published exemplar URL for human review/calibration. Not sent to Gamma. |
| `draft_rows[].text_mode` | documented+wired | Maps to `textMode` for Classic. Local Gary validates `generate`, `condense`, `preserve`. Not documented for from-template. |
| `draft_rows[].text_amount` | documented+wired | Maps to `textOptions.amount` for Classic. Local Gary uses `amount`/`density`. |
| `draft_rows[].audience` | documented+wired | Maps to `textOptions.audience` for Classic. Local Gary wires it. |
| `draft_rows[].tone` | documented+wired | Maps to `textOptions.tone` for Classic. Local Gary wires it. |
| `draft_rows[].language` | documented+wired | Maps to `textOptions.language` for Classic. Local Gary currently validates only `en`. |
| `draft_rows[].image_source` | documented+wired | Maps to `imageOptions.source` for Classic. Local Gary wires and validates source values. From-template docs expose limited image options but not source in the same way. |
| `draft_rows[].image_model` | documented+wired | Maps to `imageOptions.model`. Local Gary wires and validates many model ids. |
| `draft_rows[].image_style_preset` | documented+wired | Maps to `imageOptions.stylePreset` for Classic. Local Gary wires it. From-template docs expose `imageOptions.style`, not the full Classic stylePreset surface. |
| `draft_rows[].custom_style_prompt` | documented+wired | Maps to `imageOptions.style` where supported. Local Gary sends `image_style` as `style`, especially for custom presets. |
| `draft_rows[].keywords` | compiled | Not a discrete Gamma API field. Current local pattern compiles keywords into `additionalInstructions` prose and/or custom image style text. |
| `draft_rows[].format_type` | documented+wired | Maps to `format` for Classic. Local client supports it; Gary currently hardcodes presentation behavior. |
| `draft_rows[].format_variant` | ui-or-unknown | Gamma UI concept in this draft; no documented per-request API field beyond `format` plus `cardOptions.dimensions`. |
| `draft_rows[].format_variant.value` | ui-or-unknown | Human/UI value, not directly wired. |
| `draft_rows[].format_variant.enforced` | metadata/runtime_policy | Future validator may enforce or warn. |
| `draft_rows[].format_variant.note` | metadata | Human explanation. |
| `draft_rows[].card_split` | documented+wired | Maps to `cardSplit` for Classic. Local Gary uses `inputTextBreaks` to preserve one chunk per slide. |
| `draft_rows[].num_cards_policy` | runtime_policy | Local runtime derives `numCards` from input slide count. Gamma documents `numCards`; registry should store policy, not fixed count. |
| `draft_rows[].additional_instructions` | documented+wired | Maps to `additionalInstructions` for Classic; local Gary adds invariant instructions and variant-specific text. |
| `draft_rows[].page_shape` | compiled | Operator-facing Page setup preset; compiler maps to `cardOptions.dimensions` when valid for selected format. |
| `draft_rows[].custom_full_bleed` | ui-or-unknown/theme/template-owned | Visible/reported in UI Custom section, but no documented generate/from-template field found. Likely template/UI controlled. |
| `draft_rows[].custom_full_bleed.value` | ui-or-unknown | Desired value only until API/template control is proven. |
| `draft_rows[].custom_full_bleed.observed` | metadata | Whether observed directly in screenshot. |
| `draft_rows[].custom_full_bleed.note` | metadata | Human note. |
| `draft_rows[].aspect_ratio` | documented+wired with format guard | Maps to `cardOptions.dimensions`. For presentation, only `fluid`, `16x9`, `4x3` are documented. |
| `draft_rows[].card_width` | ui-or-unknown | Visible in UI as M/L. No documented per-request API mapping found. Likely UI/template-owned. |
| `draft_rows[].content_alignment` | ui-or-unknown/theme/template-owned | Visible in UI as top/middle/bottom. No documented per-request API mapping found. |
| `draft_rows[].font_size` | theme/template-owned | Visible in UI as S/M/L. No documented per-request API field; likely theme/template/editor control. |
| `draft_rows[].show_card_backdrops` | ui-or-unknown/theme/template-owned | Visible UI toggle. No documented per-request API field found. |
| `draft_rows[].animations` | ui-or-unknown | Visible UI toggle. No documented generate/from-template parameter found. |
| `draft_rows[].dimensions` | documented+wired | Direct runtime value for `cardOptions.dimensions`; local Gary currently forces `16x9` for Classic unless overridden. |
| `draft_rows[].header_footer` | documented+client-only | Gamma documents `cardOptions.headerFooter`; raw client can pass it; Gary does not expose it today. |
| `draft_rows[].header_footer.value` | documented+client-only | Desired header/footer config. Final API shape is structured, not just boolean. |
| `draft_rows[].header_footer.enforced` | runtime_policy | Future validator/dispatcher flag. |
| `draft_rows[].header_footer.confidence` | metadata | Confidence in observed/default value. |
| `draft_rows[].header_footer.note` | metadata | Human note. |
| `draft_rows[].export_as` | documented+wired | Maps to `exportAs` for both Classic and from-template. Local client wires it; only one export per request. |
| `draft_rows[].brand_binding` | metadata/compiled | Points to brand/style bible. Not a Gamma API field; may compile into prompt constraints or theme/template selection. |
| `draft_rows[].coherence_rules` | metadata/runtime_policy | Style consistency rule for validator/human review. |
| `draft_rows[].provenance_source` | metadata | Origin of row values. |
| `draft_rows[].provenance_notes` | metadata | Human provenance explanation. |

## Nested Style-Guide Fields

These fields appear under `style_guides.<style_id>`. The same pattern applies to each listed style unless a note says Studio-only or Classic-only.

| YAML field | Status | Programmatic control / implementation note |
| --- | --- | --- |
| `style_guides` | metadata/runtime_policy | Registry keyed by style id. Runtime selector is not implemented yet. |
| `style_guides.<style_id>` | metadata/runtime_policy | One complete style definition. |
| `style_guides.<style_id>.status` | metadata | Lifecycle state. |
| `style_guides.<style_id>.version` | metadata | Style version. |
| `style_guides.<style_id>.generation_method` | runtime_policy | Selects Classic vs from-template. Needs compiler bridge to local Gary `production_mode`. |
| `style_guides.<style_id>.display_name` | metadata | Human name. |
| `style_guides.<style_id>.intended_use` | metadata | Human/CD context. |
| `style_guides.<style_id>.theme` | documented+wired/theme-owned | Theme object. Classic and from-template document `themeId`; theme content controls colors/fonts/layout tendencies outside per-request API. |
| `style_guides.<style_id>.theme.id` | documented+wired | Maps to `themeId`. |
| `style_guides.<style_id>.theme.name` | metadata | Human label. |
| `style_guides.<style_id>.live_example_url` | metadata | Published Gamma exemplar. Not sent to API. |
| `style_guides.<style_id>.studio_template` | documented+wired for Studio | Studio/from-template template descriptor. Local Gary uses `studio_template_id`. |
| `style_guides.<style_id>.studio_template.gamma_id` | documented+wired | Maps to `gammaId` for `/generations/from-template`. |
| `style_guides.<style_id>.studio_template.name` | metadata | Human label. |
| `style_guides.<style_id>.studio_template.source` | metadata | Local artifact/source that supplied template id. |
| `style_guides.<style_id>.studio_prompt_lock` | runtime_policy/compiled | Local prompt wrapper/guard for Studio design preservation. Not a discrete Gamma field. |
| `style_guides.<style_id>.studio_prompt_lock.wrapper_id` | metadata/runtime_policy | Identifies local prompt-lock strategy. |
| `style_guides.<style_id>.studio_prompt_lock.behavior` | compiled | Compiles into the `prompt` sent to `/generations/from-template`. |
| `style_guides.<style_id>.studio_prompt_lock.guard` | runtime_policy | Local post-generation validation guard. |
| `style_guides.<style_id>.studio_prompt_lock.guard.type` | runtime_policy | Guard algorithm type, e.g. aspect ratio minimum. |
| `style_guides.<style_id>.studio_prompt_lock.guard.min_ratio` | runtime_policy | Local guard threshold. |
| `style_guides.<style_id>.studio_prompt_lock.guard.expected_ratio` | runtime_policy | Expected output ratio for guard comparison. |
| `style_guides.<style_id>.prompt_editor` | mixed | Screenshot-faithful representation of Gamma's Prompt editor UI. This is the human/editor-facing grouping; `prompt_configuration` remains the normalized runtime/API grouping. |
| `style_guides.<style_id>.prompt_editor.source` | metadata | Source screenshot or observation id. |
| `style_guides.<style_id>.prompt_editor.content_mode` | compiled/runtime_policy | Freeform vs card-by-card content entry mode. Freeform distributes a long body across requested cards; card-by-card uses explicit card boundaries. |
| `style_guides.<style_id>.prompt_editor.content_mode.value` | compiled/runtime_policy | Current exemplar value: `freeform`. |
| `style_guides.<style_id>.prompt_editor.content_mode.options` | metadata/runtime_policy | Known UI choices: `freeform`, `card_by_card`. |
| `style_guides.<style_id>.prompt_editor.text_content` | documented+wired for Classic | Prompt editor Text content group: generation mode, amount, and language. |
| `style_guides.<style_id>.prompt_editor.text_content.mode` | documented+wired | UI choices map to Gamma `textMode`: `generate`, `condense`, `preserve`. |
| `style_guides.<style_id>.prompt_editor.text_content.mode.value` | documented+wired | Current screenshot value: `condense`. |
| `style_guides.<style_id>.prompt_editor.text_content.amount` | documented+wired with translation | UI choices map to local/Gamma amount values. Screenshot `minimal` compiles to local/API `brief`; `concise` should compile to `medium`; `detailed` and `extensive` are direct. |
| `style_guides.<style_id>.prompt_editor.text_content.amount.value` | documented+wired with translation | Current screenshot value: `minimal`. |
| `style_guides.<style_id>.prompt_editor.text_content.output_language` | documented+wired with translation | Current screenshot value `en-US` compiles to local Gamma `textOptions.language=en`. |
| `style_guides.<style_id>.prompt_editor.visuals` | mixed | Prompt editor Visuals group. Theme is API-controlled by id; Image source UI labels require translation. |
| `style_guides.<style_id>.prompt_editor.visuals.theme` | documented+wired/theme-owned | Selected Gamma theme. API sends `themeId`; colors/fonts/layout tendencies live in the theme itself. |
| `style_guides.<style_id>.prompt_editor.visuals.image_source` | documented+wired with translation | Exemplar value is normalized to `aiGenerated`. The screenshot label `Automatic` is treated as a UI witness, not the registry value, because the actual generated Gamma and API/runtime layer used AI-generated illustration behavior. |
| `style_guides.<style_id>.prompt_editor.visuals.art_style` | ui-or-api-custom | Captures Gamma UI art-style labels such as `Magazine`. Current Gamma API docs list named `stylePreset` values `photorealistic`, `illustration`, `abstract`, `3D`, `lineArt`, and `custom`; `Magazine` should be compiled as `stylePreset=custom` + free-text `imageOptions.style` unless future API proof exposes it as a stable preset. |
| `style_guides.<style_id>.prompt_editor.visuals.image_model` | documented+wired | UI `Auto-select model` maps to omitted/null `imageOptions.model`; Gamma then selects the model automatically. Expect more image-variety than a pinned model. |
| `style_guides.<style_id>.prompt_editor.format` | mixed | Prompt editor Format group. `presentation` maps to API `format`; default variant/card design mode need runtime interpretation. |
| `style_guides.<style_id>.prompt_editor.format.type` | documented+wired | Current screenshot value: `presentation`, maps to `format=presentation`. |
| `style_guides.<style_id>.prompt_editor.format.variant` | ui-or-unknown | Current screenshot dropdown value: `default`. No discrete documented API field beyond `format` and `cardOptions.dimensions`. |
| `style_guides.<style_id>.prompt_editor.format.card_design_mode` | runtime_policy | Current screenshot value: `classic`. Classic maps to `/generations`; Studio maps to `/generations/from-template`. |
| `style_guides.<style_id>.prompt_editor.format.requested_card_count` | documented+wired | Current screenshot value: `10`, maps to `numCards` in Freeform mode. |
| `style_guides.<style_id>.prompt_editor.additional_instructions` | documented+wired | Current screenshot value is empty. Empty/minimal guidance means no style-specific extra prompt is sent beyond system/runtime guardrails. |
| `style_guides.<style_id>.prompt_configuration` | compiled | Local grouping of prompt/API settings. |
| `style_guides.<style_id>.prompt_configuration.text_content` | documented+wired for Classic | Maps to `textMode` and `textOptions`. Not documented for from-template. |
| `style_guides.<style_id>.prompt_configuration.text_content.mode` | documented+wired | Maps to `textMode`. |
| `style_guides.<style_id>.prompt_configuration.text_content.amount` | documented+wired | Maps to `textOptions.amount`. |
| `style_guides.<style_id>.prompt_configuration.text_content.audience` | documented+wired | Maps to `textOptions.audience`. |
| `style_guides.<style_id>.prompt_configuration.text_content.tone` | documented+wired | Maps to `textOptions.tone`. |
| `style_guides.<style_id>.prompt_configuration.text_content.language` | documented+wired | Maps to `textOptions.language`. |
| `style_guides.<style_id>.prompt_configuration.visuals` | compiled/documented+wired | Local grouping of image API fields and prompt hints. |
| `style_guides.<style_id>.prompt_configuration.visuals.image_source` | documented+wired for Classic | Maps to `imageOptions.source`. |
| `style_guides.<style_id>.prompt_configuration.visuals.image_model` | documented+wired | Maps to `imageOptions.model`. |
| `style_guides.<style_id>.prompt_configuration.visuals.style_preset` | documented+wired for Classic | Maps to `imageOptions.stylePreset`. |
| `style_guides.<style_id>.prompt_configuration.visuals.custom_style` | documented+wired | Maps to `imageOptions.style` when used. |
| `style_guides.<style_id>.prompt_configuration.visuals.keywords` | compiled | Compiles into additional instructions or custom image style prose. |
| `style_guides.<style_id>.prompt_configuration.visuals.style_preset=custom` | documented+wired | Use for UI styles such as Magazine that are not in the documented named preset list; the actual style direction belongs in `custom_style`. |
| `style_guides.<style_id>.prompt_configuration.image_options` | documented+wired for Studio subset | From-template docs support limited `imageOptions` overrides such as model/style. Local Studio path can pass image options through client, but registry compiler is not implemented. |
| `style_guides.<style_id>.prompt_configuration.image_options.source` | documented+uncertain for Studio | Classic documents `source`; from-template docs emphasize model/style, so source requires live proof before relying on it. |
| `style_guides.<style_id>.prompt_configuration.image_options.model` | documented+wired | Maps to `imageOptions.model`. |
| `style_guides.<style_id>.prompt_configuration.image_options.style_preset` | documented+uncertain for Studio | Classic documents stylePreset; from-template surface is narrower. |
| `style_guides.<style_id>.prompt_configuration.image_options.custom_style` | documented+wired | Maps to `imageOptions.style` where supported. |
| `style_guides.<style_id>.prompt_configuration.image_options.keywords` | compiled | Prompt/style hints, not discrete API field. |
| `style_guides.<style_id>.prompt_configuration.format` | documented+wired for Classic | Local grouping for `format`, `cardSplit`, and generation count policy. |
| `style_guides.<style_id>.prompt_configuration.format.type` | documented+wired | Maps to Classic `format`. |
| `style_guides.<style_id>.prompt_configuration.format.variant` | ui-or-unknown | UI concept; no known discrete API field. |
| `style_guides.<style_id>.prompt_configuration.format.variant.value` | ui-or-unknown | Human/UI value. |
| `style_guides.<style_id>.prompt_configuration.format.variant.enforced` | runtime_policy | Future validator flag. |
| `style_guides.<style_id>.prompt_configuration.format.variant.note` | metadata | Human explanation. |
| `style_guides.<style_id>.prompt_configuration.format.card_split` | documented+wired | Maps to Classic `cardSplit`. |
| `style_guides.<style_id>.prompt_configuration.generation` | runtime_policy/documented+wired | Local grouping for `numCards` policy. |
| `style_guides.<style_id>.prompt_configuration.generation.num_cards` | runtime_policy/documented+wired | Gamma documents `numCards`; local runtime derives it from input count. |
| `style_guides.<style_id>.prompt_configuration.generation.num_cards.value` | runtime_policy | Usually `input_slide_count`. |
| `style_guides.<style_id>.prompt_configuration.generation.num_cards.note` | metadata | Human explanation. |
| `style_guides.<style_id>.prompt_configuration.additional_instructions` | documented+wired/compiled | Maps to Classic `additionalInstructions` or compiles into Studio `prompt`. |
| `style_guides.<style_id>.api_parameters` | documented/client-runtime mirror | Selected-value mirror of the Gamma request surface for this style. This is not an option catalog; it records the intended API payload shape. |
| `style_guides.<style_id>.api_parameters.endpoint` | runtime_policy/documented+wired | Selected Gamma endpoint. Classic uses `/generations`; Studio uses `/generations/from-template`. |
| `style_guides.<style_id>.api_parameters.payload_shape` | documented/client-runtime mirror | Selected Gamma payload fields and values for this style. |
| `style_guides.<style_id>.api_parameters.payload_shape.inputText` | documented+wired | Runtime-supplied source text. Stored as `runtime_supplied` because the style controls treatment, not content. |
| `style_guides.<style_id>.api_parameters.payload_shape.textMode` | documented+wired | Maps to `textMode`; Gary wires via `text_mode`. |
| `style_guides.<style_id>.api_parameters.payload_shape.format` | documented+wired | Maps to `format`; current exemplar uses `presentation`. |
| `style_guides.<style_id>.api_parameters.payload_shape.numCards` | documented+wired | Maps to `numCards`; current exemplar uses 10 from the Prompt editor screenshot. |
| `style_guides.<style_id>.api_parameters.payload_shape.cardSplit` | documented+wired | Maps to `cardSplit`; Gary currently uses `inputTextBreaks` to preserve section/card boundaries. |
| `style_guides.<style_id>.api_parameters.payload_shape.themeId` | documented+wired | Maps to `themeId`; Gary resolves/validates via `list_themes()`. |
| `style_guides.<style_id>.api_parameters.payload_shape.additionalInstructions` | documented+wired | Maps to `additionalInstructions`; current exemplar is empty/minimal, although Gary may add invariant runtime instructions. |
| `style_guides.<style_id>.api_parameters.payload_shape.textOptions` | documented+wired | Maps to `textOptions`; Gary wires `amount`, `tone`, `audience`, and `language`. |
| `style_guides.<style_id>.api_parameters.payload_shape.textOptions.amount` | documented+wired | API value corresponding to UI `Minimal`; local value is `brief`. |
| `style_guides.<style_id>.api_parameters.payload_shape.textOptions.tone` | documented+wired | API text option; not visible in the screenshot, but currently accepted by Gary. |
| `style_guides.<style_id>.api_parameters.payload_shape.textOptions.audience` | documented+wired | API text option; not visible in the screenshot, but currently accepted by Gary. |
| `style_guides.<style_id>.api_parameters.payload_shape.textOptions.language` | documented+wired | API text option; current local validator allows `en`. |
| `style_guides.<style_id>.api_parameters.payload_shape.imageOptions` | documented+wired/mixed | Image options group. Gary wires `source`, `model`, `stylePreset`, and `style` when present. |
| `style_guides.<style_id>.api_parameters.payload_shape.imageOptions.source` | documented+wired | Maps to `imageOptions.source`; current exemplar value is `aiGenerated`. |
| `style_guides.<style_id>.api_parameters.payload_shape.imageOptions.model` | documented+wired | Maps to `imageOptions.model`; null means use Gamma/default model behavior. |
| `style_guides.<style_id>.api_parameters.payload_shape.imageOptions.stylePreset` | documented+wired | Maps to `imageOptions.stylePreset`; current exemplar uses `illustration`. |
| `style_guides.<style_id>.api_parameters.payload_shape.imageOptions.style` | documented+wired | Maps to `imageOptions.style` for custom style prompts; null for this exemplar. |
| `style_guides.<style_id>.api_parameters.payload_shape.imageOptions.model=null` | documented+wired | Implements UI `Auto-select model`. This is intentionally less deterministic than a pinned model and can produce a wider visual mix across cards. |
| `style_guides.<style_id>.api_parameters.payload_shape.cardOptions` | documented+wired/client-only mixed | Card options group. Gary wires `dimensions`; raw client can pass `headerFooter`, but Gary does not expose it today. |
| `style_guides.<style_id>.api_parameters.payload_shape.cardOptions.dimensions` | documented+wired | Maps to `cardOptions.dimensions`; current exemplar value is `fluid`, matching the Default/Fluid page setup rather than any later publication override. |
| `style_guides.<style_id>.api_parameters.payload_shape.cardOptions.headerFooter` | documented+client-only | Gamma documents it and the raw client can pass it; Gary does not currently build the structured value. |
| `style_guides.<style_id>.api_parameters.payload_shape.sharingOptions` | documented+client-only | Gamma documents `sharingOptions`; raw client can pass it, but Gary style settings do not expose it. |
| `style_guides.<style_id>.api_parameters.payload_shape.exportAs` | documented+wired | Maps to `exportAs`; current exemplar uses `png`. |
| `style_guides.<style_id>.api_parameters.payload_shape.folderIds` | documented+client-only | Gamma documents `folderIds`; raw client can pass it, but Gary style settings do not expose it. |
| `style_guides.<style_id>.api_parameters.local_runtime` | runtime_policy | Local Gary surface summary. Shows what `gamma_settings` can accept today versus client fields that still need style-registry wiring. |
| `style_guides.<style_id>.api_parameters.local_runtime.gamma_settings_keys` | runtime_policy | Current accepted per-variant Gary settings from `GAMMA_SETTING_KEYS`. |
| `style_guides.<style_id>.api_parameters.local_runtime.notes` | metadata | Implementation note about Gary/client gaps. |
| `style_guides.<style_id>.page_settings` | compiled | Local grouping for page/export/share settings. |
| `style_guides.<style_id>.page_settings.page_setup` | mixed | Operator-facing Gamma Page setup values from screenshot/UI. Some map to API; most do not. |
| `style_guides.<style_id>.page_settings.page_setup.source` | metadata | Source of observed values. |
| `style_guides.<style_id>.page_settings.page_setup.shape_preset` | compiled | Maps to dimensions when valid: default/fluid -> `fluid`, traditional -> `16x9`, tall -> `4x3`. |
| `style_guides.<style_id>.page_settings.page_setup.shape_preset` | compiled | Operator-facing selected preset. Choices are documented in the Page Setup Field Dictionary below. |
| `style_guides.<style_id>.page_settings.page_setup.custom` | mixed | Custom page setup group; not fully visible in screenshot. |
| `style_guides.<style_id>.page_settings.page_setup.custom.full_bleed` | ui-or-unknown/theme/template-owned | No documented per-request API field found. |
| `style_guides.<style_id>.page_settings.page_setup.custom.aspect_ratio` | documented+wired with format guard | Maps to `cardOptions.dimensions` only for documented format-specific values. |
| `style_guides.<style_id>.page_settings.page_setup.aspect_ratio` | documented+wired with format guard | Maps to `cardOptions.dimensions`. Presentation-safe values are `fluid`, `16x9`, `4x3`. |
| `style_guides.<style_id>.page_settings.page_setup.card_width` | ui-or-unknown/theme/template-owned | UI M/L. No documented per-request API field found. |
| `style_guides.<style_id>.page_settings.page_setup.content_alignment` | ui-or-unknown/theme/template-owned | UI top/middle/bottom. No documented per-request API field found. |
| `style_guides.<style_id>.page_settings.page_setup.font_size` | theme/template-owned/ui-or-unknown | UI S/M/L. No documented per-request API field found; likely theme/template/editor controlled. |
| `style_guides.<style_id>.page_settings.page_setup.show_card_backdrops` | ui-or-unknown/theme/template-owned | UI toggle. No documented per-request API field found. |
| `style_guides.<style_id>.page_settings.page_setup.animations` | ui-or-unknown | UI toggle. No documented generate/from-template field found. |
| `style_guides.<style_id>.page_settings.page_setup.card_headers_footers` | documented+client-only | Maps to `cardOptions.headerFooter`; raw client can pass, Gary does not wire yet. |
| `style_guides.<style_id>.page_settings.card_options` | documented+wired/client-only mixed | Local grouping for `cardOptions`. |
| `style_guides.<style_id>.page_settings.card_options.dimensions` | documented+wired | Maps to `cardOptions.dimensions`; local Gary wires it. |
| `style_guides.<style_id>.page_settings.card_options.header_footer` | documented+client-only | Gamma documents `cardOptions.headerFooter`; local Gary does not wire it yet. |
| `style_guides.<style_id>.page_settings.card_options.header_footer.value` | documented+client-only | Desired value. Should become structured object for real API use. |
| `style_guides.<style_id>.page_settings.card_options.header_footer.implementation_status` | metadata/runtime_policy | Single-keyword status; currently `available` because Gamma documents the field and the raw client can pass it, but Gary does not wire it. |
| `style_guides.<style_id>.page_settings.card_options.header_footer.enforced` | runtime_policy | Future validator/dispatcher flag. |
| `style_guides.<style_id>.page_settings.card_options.header_footer.confidence` | metadata | Confidence in default/observed value. |
| `style_guides.<style_id>.page_settings.card_options.header_footer.note` | metadata | Human note. |
| `style_guides.<style_id>.page_settings.sharing_options` | documented+wired in client, not Gary-normalized | Gamma documents `sharingOptions`; raw client can pass it. Gary style registry compiler not implemented. |
| `style_guides.<style_id>.page_settings.sharing_options.access` | documented+unwired | Desired sharing policy. Needs mapping to documented `workspaceAccess`/`externalAccess`/email options. |
| `style_guides.<style_id>.page_settings.sharing_options.enforced` | runtime_policy | Future validator/dispatcher flag. |
| `style_guides.<style_id>.page_settings.folder_ids` | documented+wired in client, not Gary-normalized | Gamma documents `folderIds`; raw client can pass it. Gary registry compiler not implemented. |
| `style_guides.<style_id>.page_settings.folder_ids.value` | documented+unwired | Desired Gamma folder ids. |
| `style_guides.<style_id>.page_settings.folder_ids.enforced` | runtime_policy | Future validator/dispatcher flag. |
| `style_guides.<style_id>.page_settings.export` | documented+wired | Export settings group. |
| `style_guides.<style_id>.page_settings.export.export_as` | documented+wired | Maps to `exportAs`; client wires Classic and from-template. |
| `style_guides.<style_id>.page_settings.manual_finish_checklist` | metadata/runtime_policy | Studio/manual QA checklist, not sent to Gamma. |
| `style_guides.<style_id>.page_settings.manual_finish_checklist.enforced` | runtime_policy | Future workflow gate flag. |
| `style_guides.<style_id>.page_settings.manual_finish_checklist.items` | metadata/runtime_policy | Checklist text for human/automated review. |
| `style_guides.<style_id>.brand_binding` | metadata/compiled | Brand source binding. Not a Gamma field; can inform theme/template selection or prompt instructions. |
| `style_guides.<style_id>.brand_binding.id` | metadata | Brand binding id. |
| `style_guides.<style_id>.brand_binding.path` | metadata | Local path to brand/style bible. |
| `style_guides.<style_id>.brand_binding.auto_translation` | runtime_policy | Future compiler policy for translating brand into Gamma settings. |
| `style_guides.<style_id>.coherence_rules` | metadata/runtime_policy | Human/validator style consistency rules. |
| `style_guides.<style_id>.coherence_rules.theme_art_keywords_dimensions` | metadata/runtime_policy | Classic coherence rule. |
| `style_guides.<style_id>.coherence_rules.template_art_dimensions` | metadata/runtime_policy | Studio/template coherence rule. |
| `style_guides.<style_id>.provenance` | metadata | Provenance wrapper. |
| `style_guides.<style_id>.provenance.source` | metadata | Source artifact or decision. |
| `style_guides.<style_id>.provenance.established` | metadata | Establishment date. |
| `style_guides.<style_id>.provenance.notes` | metadata | Human explanation. |

## Affinity and Binding Fields

| YAML field | Status | Programmatic control / implementation note |
| --- | --- | --- |
| `affinity_layer` | runtime_policy/metadata | Optional recommendation layer. Must not silently override explicit operator style choice. |
| `affinity_layer.visual-led` | runtime_policy/metadata | Style recommendations for visual-led profile. |
| `affinity_layer.visual-led.preferred` | runtime_policy/metadata | Recommended style ids. |
| `affinity_layer.visual-led.compare_against` | runtime_policy/metadata | Suggested contrast styles for A/B testing. |
| `affinity_layer.text-led` | runtime_policy/metadata | Style recommendations for text-led profile. |
| `affinity_layer.text-led.preferred` | runtime_policy/metadata | Recommended style ids. |
| `affinity_layer.text-led.compare_against` | runtime_policy/metadata | Suggested contrast styles. |
| `variant_binding_examples` | metadata | Examples only; not runtime config. |
| `variant_binding_examples.single_variant` | metadata | Example one-style binding. |
| `variant_binding_examples.single_variant.gamma_settings` | metadata/runtime_policy example | Future directive shape. |
| `variant_binding_examples.single_variant.gamma_settings[].variant_id` | runtime_policy example | Variant id, e.g. A. |
| `variant_binding_examples.single_variant.gamma_settings[].styleguide` | runtime_policy example | Desired future styleguide selector. |
| `variant_binding_examples.a_b_comparison` | metadata | Example A/B binding. |
| `variant_binding_examples.a_b_comparison.gamma_settings` | metadata/runtime_policy example | Future directive shape for A/B. |
| `variant_binding_examples.a_b_comparison.gamma_settings[].variant_id` | runtime_policy example | Variant id. |
| `variant_binding_examples.a_b_comparison.gamma_settings[].styleguide` | runtime_policy example | Desired future styleguide selector. |
| `promotion_work_items` | metadata/runtime_policy | Implementation checklist for making the draft registry real. |

## Page Setup Witness: Classic A

The supplied screenshot is treated as a witness for the current Classic A Page setup:

| UI control | Observed value | Control status |
| --- | --- | --- |
| Slide shape | Default / Fluid | Maps to `cardOptions.dimensions=fluid`, but current production policy forces `16x9` for Descript-bound Classic output. |
| Card width | L | UI-visible; no documented per-request API mapping found. |
| Content alignment | Middle | UI-visible; no documented per-request API mapping found. |
| Font size | M | UI-visible; likely theme/template/UI controlled; no documented per-request API mapping found. |
| Show card backdrops | Off | UI-visible; no documented per-request API mapping found. |
| Animations | On | UI-visible; no documented generate/from-template parameter found. |
| Card headers & footers | Section visible, value not expanded | Gamma documents `cardOptions.headerFooter`; Gary does not wire it yet. Current false/default is inferred. |

## Page Setup Witness: Classic-Cards Fluid Visuals Magazine+AI-Direction Detailed

The supplied Page setup screenshot for `Classic-Cards_Fluid-Visuals_Magazine+AI-Direction_Detailed` is treated as the Page setup witness for the published exemplar at `https://the-economic-structural--1t485b6.gamma.site/`.

| UI control | Observed value | Registry value | Control status |
| --- | --- | --- | --- |
| Active setup tab | Cards | `active_tab: cards` | Metadata/UI witness only. |
| Format | Presentation | `format: presentation` | Maps to Gamma `format=configuration` conceptually and to API `format: presentation` for Classic generation. |
| Slide shape | Default / Fluid | `shape_preset: default_fluid`; `aspect_ratio: fluid`; `card_options.dimensions: fluid` | Maps to documented `cardOptions.dimensions=fluid` for `format=presentation`. |
| Card width | L | `card_width: L` | UI-visible; no documented per-request API mapping found. |
| Content alignment | Middle | `content_alignment: middle` | UI-visible; no documented per-request API mapping found. |
| Font size | M | `font_size: M` | UI-visible; no documented per-request API mapping found; likely theme/template/editor-owned. |
| Show card backdrops | Off | `show_card_backdrops: false` | UI-visible; no documented generate/from-template field found. |
| Animations | On | `animations: true` | UI-visible; no documented generate/from-template field found. For PNG export, this should not affect the still assets. |
| Card headers & footers | Section visible with empty Add elements area | `card_headers_footers: false`; `card_options.header_footer.value: false` | Gamma documents `cardOptions.headerFooter`, but Gary does not wire it today and the API shape is structured. |
| Background tab | Present but not opened | `background_tab: not_observed` | Not enough evidence to record background values for this style. |

No exact local request receipt was found for this published Gamma URL. Current API-shape values in the registry are therefore compiled from the Prompt editor and Page setup screenshots plus known Gamma/Gary mappings. Nearby receipts for other Gamma generations should not be used as the source of truth for this exemplar.

## Page Setup Field Dictionary

The YAML registry now represents every Page setup field/value visible in the screenshot or reported for the Custom subsection. The current Classic A values are copied from the screenshot; implementation status is intentionally stored in the YAML as a single keyword, while this companion gives the rationale.

| Field | Current A value | Represented values | Purpose | Programmatic control status |
| --- | --- | --- | --- | --- |
| `shape_preset` | `default_fluid` | `default_fluid`, `traditional_16x9`, `tall_4x3`, `custom` | Selects Gamma's broad page/card shape mode. | `default_fluid`, `traditional_16x9`, and `tall_4x3` compile to documented `cardOptions.dimensions` values for `format=presentation`: `fluid`, `16x9`, `4x3`. `custom` is a UI grouping, not a documented API value. |
| `custom.full_bleed` | `null` | `true`, `false` | Controls whether custom pages run edge-to-edge. | No documented generate/from-template parameter found. Treat as theme/template/UI-owned. For Studio, full bleed is effectively achieved by template design plus post-generation aspect guard, not a per-request API field. |
| `custom.aspect_ratio` | `null` | `fluid`, `traditional_16x9`, `tall_4x3`, `a4`, `letter`, `square` | Selects aspect ratio when using Custom. | Compiles to `cardOptions.dimensions` only for documented format-compatible values. For presentation: `fluid`, `16x9`, `4x3`. For document: `a4`, `letter`. For social: `square` maps to `1x1`. Registry validator must prevent format mismatch. |
| `aspect_ratio` | `fluid` | `fluid`, `traditional_16x9`, `tall_4x3`, `a4`, `letter`, `square` | Normalized aspect-ratio target independent of UI preset label. | Same mapping as `custom.aspect_ratio`. The exemplar remains `fluid`; any Descript/video 16:9 forcing is a runtime publication policy outside the style exemplar. |
| `card_width` | `L` | `M`, `L` | Controls the width of the card content area in Gamma's page layout. | Visible in UI; no documented generate/from-template field found. Likely editor/template layout control. Could potentially be encoded in a template, but not confirmed as API-controllable. |
| `content_alignment` | `middle` | `top`, `middle`, `bottom` | Controls vertical placement of content inside the card. | Visible in UI; no documented generate/from-template field found. Likely editor/template layout control, or indirectly influenced by prompt/template design. |
| `font_size` | `M` | `S`, `M`, `L` | Controls overall type scale. | Visible in UI; no documented per-request field found. Best treated as theme/template-owned. A Gamma theme may embody typography, but current API exposes only `themeId`, not individual font-size toggles. |
| `show_card_backdrops` | `false` | `true`, `false` | Controls whether Gamma renders a backdrop behind cards. | Visible in UI; no documented generate/from-template field found. Treat as theme/template/UI-owned until live API proof says otherwise. |
| `animations` | `true` | `true`, `false` | Controls Gamma presentation animations. | Visible in UI; no documented generate/from-template parameter found. Direct UI/editor control may be required. For exported PNGs, this has little or no effect on still assets. |
| `card_headers_footers` | `false` inferred | `true`, `false` | Controls header/footer regions on cards. | Gamma documents `cardOptions.headerFooter` and the raw local client can pass `card_options`; Gary does not expose it today. The real API shape is structured, not just boolean. |
| `card_options.dimensions` | `fluid` | `fluid`, `16x9`, `4x3` for presentation | Runtime-facing dimensions value for this style exemplar. | `in_use`: local Gary can send `cardOptions.dimensions`; this exemplar records the clean style value, not a publication override. |
| `card_options.header_footer` | `false` inferred | structured header/footer object eventually | Runtime-facing header/footer configuration. | Documented by Gamma, accepted by raw client, not wired through Gary. This is a good near-term implementation candidate. |

## Implementation Implications

1. The styleguide compiler should be format-aware before accepting dimension values. `a4`, `letter`, `1x1`, `4x5`, and `9x16` are not valid presentation dimensions per current docs.
2. Header/footer should be a near-term wiring candidate because Gamma documents it and the raw client already accepts `card_options`.
3. Card width, vertical alignment, font size, card backdrops, animations, and full bleed should be treated as theme/template/UI-owned until a documented API field or live API proof exists.
4. Studio/from-template styles should not inherit Classic-only fields by accident. The from-template API surface is narrower and template-owned layout is part of the contract.
5. The production safety policy that forces `16x9` for Descript-bound narrated video remains justified as a runtime/export override, but it should live outside clean style exemplars unless the style itself was authored as 16:9.
