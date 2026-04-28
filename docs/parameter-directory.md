# Parameter Directory

Master reference for creative-control parameters.

This document is the canonical operator and agent-facing index for parameter governance across the production pipeline. Originally created as part of Story `20c-7` (Parameter Audit & Registry Schema), it now reflects the complete Wave 2B parameter surface including Creative Director (CD) agent outputs, experience profiles, and the 11-key `narration_profile_controls` surface.

## How to Use This Directory

- Audience: operators, story implementers, and reviewers making parameter decisions.
- Use this first when adding or changing a parameter in any creative-control story.
- Source-of-truth rule: lifecycle status (`implemented` / `planned`) is governed by `state/config/parameter-registry-schema.yaml`.
- Change protocol: update this directory and the registry schema in the same change set.
- Expected outcome: every parameter has a clear family, owner path, and lifecycle status before merge.

## Scope and Sources

- Run constants source: `scripts/utilities/run_constants.py`
- Narration-time sources:
  - `state/config/narration-script-parameters.yaml`
  - `state/config/narration-grounding-profiles.yaml`
  - `state/config/elevenlabs-voice-profiles.yaml`
- Assembly-time sources:
  - `skills/bmad-agent-content-creator/references/template-segment-manifest.md`
  - `state/config/fidelity-contracts/g4-narration-script.yaml`
  - `state/config/fidelity-contracts/g6-composition.yaml`
- Machine-readable registry schema: `state/config/parameter-registry-schema.yaml`

## Family 1: Run Constants (Operational)

These parameters freeze run identity, execution mode, budget, and baseline routing.

| Parameter | Type | Allowed / Shape | Status | Source |
| --- | --- | --- | --- | --- |
| `run_id` | string | non-empty | implemented | `run_constants.py` |
| `lesson_slug` | string | non-empty | implemented | `run_constants.py` |
| `bundle_path` | string | non-empty, resolves to bundle dir | implemented | `run_constants.py` |
| `primary_source_file` | string | non-empty path | implemented | `run_constants.py` |
| `optional_context_assets` | list[string] | list or comma-separated string normalized to list | implemented | `run_constants.py` |
| `theme_selection` | string | non-empty | implemented | `run_constants.py` |
| `theme_paramset_key` | string | non-empty | implemented | `run_constants.py` |
| `execution_mode` | enum | `tracked/default`, `ad-hoc` (+ aliases) | implemented | `run_constants.py` |
| `quality_preset` | enum | `explore`, `draft`, `production`, `regulated` | implemented | `run_constants.py` |
| `double_dispatch` | boolean | true/false | implemented | `run_constants.py` |
| `motion_enabled` | boolean | true/false | implemented | `run_constants.py` |
| `motion_budget.max_credits` | float | positive number | implemented | `run_constants.py` |
| `motion_budget.model_preference` | enum | `std`, `pro` | implemented | `run_constants.py` |
| `cluster_density` | enum | `none`, `sparse`, `default`, `rich` | implemented | `run_constants.py` |
| `slide_mode_proportions` | object | distribution map for `literal-text`, `literal-visual`, `creative` | implemented | `scripts/utilities/run_constants.py` |
| `experience_profile` | enum | `visual-led`, `text-led`, `none` | implemented | `scripts/utilities/run_constants.py` |
| `schema_version` | integer | optional | implemented | `run_constants.py` |
| `frozen_at_utc` | string | optional timestamp | implemented | `run_constants.py` |
| `frozen_note` | string | optional | implemented | `run_constants.py` |
| `parent_slide_count` | integer | 1-50, operator-confirmed | implemented | `slide_count_runtime_estimator.py` → `run-constants.yaml` |
| `target_total_runtime_minutes` | float | 0.5-60, operator-confirmed | implemented | `slide_count_runtime_estimator.py` → `run-constants.yaml` |
| `estimated_total_slides` | float | system-derived from profile | implemented | `slide_count_runtime_estimator.py` (parent × expansion factor) |
| `avg_slide_seconds` | float | system-derived from profile | implemented | `slide_count_runtime_estimator.py` (target_runtime / estimated_total) |

## Family 2: Narration-Time (Irene + Voice Policy)

These parameters control script style, pedagogical pacing, grounding stance, and voice profile preference.

### High-leverage narration controls

| Parameter | Type | Allowed / Shape | Status | Source |
| --- | --- | --- | --- | --- |
| `narration_density.target_wpm` | integer | recommended 130-170 range downstream | implemented | `narration-script-parameters.yaml` |
| `narration_density.mean_words_per_slide` | integer | positive | implemented | `narration-script-parameters.yaml` |
| `narration_density.min_words_per_slide` | integer | positive | implemented | `narration-script-parameters.yaml` |
| `narration_density.max_words_per_slide` | integer | positive | implemented | `narration-script-parameters.yaml` |
| `slide_echo.default` | enum | `verbatim`, `paraphrase`, `inspired` | implemented | `narration-script-parameters.yaml` |
| `visual_narration.visual_references_per_slide` | integer | target references per slide | implemented | `narration-script-parameters.yaml` |
| `visual_narration.visual_references_tolerance` | integer | +/- tolerance | implemented | `narration-script-parameters.yaml` |
| `pedagogical_bridging.transition_style` | enum | `conceptual`, `sequential`, `question_driven`, `narrative_arc` | implemented | `narration-script-parameters.yaml` |
| `pedagogical_bridging.bridge_frequency_scale` | enum | `minimal`, `moderate`, `rich` | implemented | `narration-script-parameters.yaml` |
| `pedagogical_bridging.spoken_bridge_policy.enforcement` | enum | `off`, `warn`, `error` | implemented | `narration-script-parameters.yaml` |
| `engagement_stance.posture` | enum | `lecturer`, `collegial_guide`, `coach`, `storyteller` | implemented | `narration-script-parameters.yaml` |
| `source_depth.creative_slides` | enum | `describe_visual`, `teach_behind`, `full_synthesis` | implemented | `narration-script-parameters.yaml` |
| `source_depth.literal_slides` | enum | `confirm_visible`, `light_enrich`, `full_synthesis` | implemented | `narration-script-parameters.yaml` |
| `runtime_variability.allowed_timing_roles[]` | enum[] | anchor/concept/evidence/etc. | implemented | `narration-script-parameters.yaml` |
| `runtime_variability.allowed_density_levels[]` | enum[] | `light`, `medium`, `heavy` | implemented | `narration-script-parameters.yaml` |
| `runtime_variability.bridge_cadence.require_intro_or_outro_every_minutes` | float | positive | implemented | `narration-script-parameters.yaml` |
| `runtime_variability.bridge_cadence.require_intro_or_outro_every_slides` | integer | positive | implemented | `narration-script-parameters.yaml` |
| `profiles.creative.slide_role` | enum | profile-defined | implemented | `narration-grounding-profiles.yaml` |
| `profiles.literal-text.slide_role` | enum | profile-defined | implemented | `narration-grounding-profiles.yaml` |
| `profiles.literal-visual.slide_role` | enum | profile-defined | implemented | `narration-grounding-profiles.yaml` |
| `default_profile` | string | profile key | implemented | `elevenlabs-voice-profiles.yaml` |
| `content_type_profiles.<type>` | string | profile key | implemented | `elevenlabs-voice-profiles.yaml` |
| `narration_profile_controls.narrator_source_authority` | enum | `source-grounded`, `balanced`, `slide-led` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.slide_content_density` | enum | `lean`, `adaptive`, `dense` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.elaboration_budget` | enum | `low`, `medium`, `high` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.connective_weight` | enum | `light`, `balanced`, `heavy` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.callback_frequency` | enum | `sparse`, `moderate`, `frequent` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.visual_narration_coupling` | enum | `loose`, `balanced`, `tight` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.rhetorical_richness` | enum | `restrained`, `balanced`, `expressive` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.vocabulary_register` | enum | `accessible`, `professional`, `specialist` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.arc_awareness` | enum | `low`, `medium`, `high` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.narrative_tension` | enum | `low`, `medium`, `high` | implemented | `narration-script-parameters.yaml` |
| `narration_profile_controls.emotional_coloring` | enum | `neutral`, `warm`, `vivid` | implemented | `narration-script-parameters.yaml` |

## Family 3: Assembly-Time (Manifest + Composition)

These parameters govern how narration and visuals are staged and synchronized in composition.

| Parameter | Type | Allowed / Shape | Status | Source |
| --- | --- | --- | --- | --- |
| `duration_estimate_seconds` | float/null | pre-audio estimate | implemented | `template-segment-manifest.md` |
| `timing_role` | enum/null | anchor/concept/evidence/etc. | implemented | `template-segment-manifest.md` |
| `content_density` | enum/null | `light`, `medium`, `heavy` | implemented | `template-segment-manifest.md` |
| `visual_detail_load` | enum/null | `light`, `medium`, `heavy` | implemented | `template-segment-manifest.md` |
| `duration_rationale` | string/null | rationale text | implemented | `template-segment-manifest.md` |
| `bridge_type` | enum/null | `none`, `intro`, `outro`, `both`, `pivot`, `cluster_boundary` | implemented | `template-segment-manifest.md` |
| `transition_in` | enum | `fade`, `cross-dissolve`, `cut`, `none` | implemented | `template-segment-manifest.md` |
| `transition_out` | enum | `fade`, `cross-dissolve`, `cut`, `none` | implemented | `template-segment-manifest.md` |
| `music` | enum/null | `duck`, `swell`, `out`, `continue`, `null` | implemented | `template-segment-manifest.md` |
| `narration_duration` | float/null | authoritative post-TTS duration | implemented | `template-segment-manifest.md` |
| `visual_duration` | float/null | per visual segment duration | implemented | `template-segment-manifest.md` |
| `motion_type` | enum | `static`, `video`, `animation` | implemented | `template-segment-manifest.md` |
| `motion_asset_path` | string/null | approved motion asset path | implemented | `template-segment-manifest.md` |
| `motion_duration_seconds` | float/null | motion runtime | implemented | `template-segment-manifest.md` |
| `motion_status` | enum/null | `pending`, `generated`, `imported`, `approved`, `null` | implemented | `template-segment-manifest.md` |
| `onset_delay` | float/null | delay before narration starts for segment | implemented | `template-segment-manifest.md`, `validate-irene-pass2-handoff.py`, `precomposition_validator.py` |
| `dwell` | float/null | hold duration after narration completes | implemented | `template-segment-manifest.md`, `validate-irene-pass2-handoff.py`, `precomposition_validator.py` |
| `cluster_gap` | float/null | additional gap at cluster boundaries | implemented | `template-segment-manifest.md`, `validate-irene-pass2-handoff.py`, `precomposition_validator.py` |
| `transition_buffer` | float/null | minimum transition safety buffer between segments | implemented | `template-segment-manifest.md`, `validate-irene-pass2-handoff.py`, `precomposition_validator.py` |

## Governance Notes

- New parameters should be added to:
  - this directory,
  - `state/config/parameter-registry-schema.yaml`,
  - and relevant validation contracts/tests in the same change.
- Implementation checklist before merge:
  - parameter appears in `parameter-registry-schema.yaml` with required fields
  - status in this directory matches schema status
  - validation tests for registry schema remain green
- Parameter owners:
  - Run constants: Marcus/runtime utilities
  - Narration-time: Irene + narration contracts
  - Assembly-time: Irene manifest + Compositor/ElevenLabs/Kira + G6 checks

### Party Mode Decision Checkpoints

Re-run Party Mode consensus before:

- introducing backward-incompatible registry schema changes
- changing strictness policy (fail-fast versus permissive-ignore) for unknown keys
- adding merge/release-blocking automation based on registry compliance
- reclassifying large groups of parameters across families or statuses

---

## Migration Runtime Parameters (post-SHIP; added 2026-04-28)

The pre-migration parameter sections above are CREATIVE-CONTROL parameters owned by Irene, the CD agent, and the v4.x prompt-pack family. The migrated runtime introduces additional parameter surfaces that were not in scope for the Story 20c-7 audit. This section catalogs them for completeness.

### Cost engineering (Slab 5a.3)

| Parameter | Source | Type | Purpose | Operator authority |
|---|---|---|---|---|
| `MARCUS_TRIAL_BUDGET_USD` | Environment variable | float | Soft-cap budget telemetry per trial; emits warning when crossed; no hard-stop | Set in `.env`; default unset means no budget alerting |
| Per-tier model assignment | `runtime/config/model_cascade.yaml` | YAML | Marcus / mid-tier / narrow-task model IDs (e.g., gpt-5 / gpt-5-mini / gpt-5-nano) | Operator-editable; A15 counter-pattern requires catalog membership |
| Per-tier pricing | `runtime/config/openai_pricing.yaml` | YAML | Per-million-token rates per model tier | Operator-editable when OpenAI rate-cards change |
| Per-trial cost report path | `state/config/runs/<trial-id>/cost-report.{json,md}` | Generated | Per-trial cost breakdown by specialist + tier | Read-only artifact |

### Production runner (Slab 6.1)

| Parameter | Source | Type | Purpose | Operator authority |
|---|---|---|---|---|
| `production_clone_launch_evidence` | `ProductionTrialEnvelope` field | bool | Flips `True` ONLY after at least one real specialist call completes via adapter; offline mode keeps `False` per AC-6.1-F | Set by runner; not operator-editable |
| `--allow-offline-cost-report` | `app/marcus/cli/trial.py` flag | CLI bool | Allows trial to proceed without `OPENAI_API_KEY`; produces synthetic cost report; evidence stays `False` | Operator passes flag at trial start |
| `gate_overrides` | Production runner parameter | dict[str, GateMode] | Promotes named per-specialist gates to production-blocking; default: all per-specialist gates non-blocking under production composition | Operator opt-in for safety-critical promotion |

### Composition envelope (Slab 6.0)

| Parameter | Source | Type | Purpose | Operator authority |
|---|---|---|---|---|
| `dependency_map` per specialist | `state/config/pipeline-manifest.yaml` per-node `dependencies:` field (Slab 6.2) | dict[downstream-input-key, upstream-specialist-id] | Manifest-declared cross-specialist coupling; runner falls back to `_default_dependency_map_for(specialist_id)` for nodes that omit declaration (PERMANENT fallback) | Per-specialist filing time |
| `composition_mode` | `RunState` field | Literal["isolated", "composed"] | Indicates whether specialist runs in M3 harness (isolated) or production runner (composed); affects gate handling | Set by runtime; not operator-editable |

### LangSmith integration

| Parameter | Source | Type | Purpose | Operator authority |
|---|---|---|---|---|
| `LANGSMITH_API_KEY` | Environment variable | str | Required for trace upload; auto-skips test classes when missing | `.env` |
| `LANGSMITH_PROJECT` | Environment variable | str | LangSmith project name for trace organization | `.env` |
| `LANGSMITH_TRACING` | Environment variable | bool string | Enables tracing when set to `true`; default off | `.env`; usually set by environment of the production run |

### Pipeline manifest pack version

| Parameter | Source | Type | Purpose | Operator authority |
|---|---|---|---|---|
| `pack_version` | `runtime/graphs/v42/pack-version.txt` (frozen); `state/config/pipeline-manifest.yaml::pack_version` (live) | str | Identifies the prompt-pack version family (currently v4.2) | Tier-1 (patch) dev-agent authority; Tier-2 (minor) + Tier-3 (major) require party-mode per `docs/dev-guide/pipeline-manifest-regime.md` §"Pack Versioning Policy" |
| `block_mode_trigger_paths` | `state/config/pipeline-manifest.yaml::block_mode_trigger_paths` | list[str] | Paths that, when modified in a diff, trigger pre-closure block-mode hook | Operator + party-mode |

### Operator-facing CLI flags (frequently used)

| Flag | Surface | Type | Purpose |
|---|---|---|---|
| `--preset production` | `app.marcus.cli trial start` | str | Selects production graph runner (vs M3 deterministic harness) |
| `--input <corpus-path>` | `app.marcus.cli trial start` | path | Corpus directory or file for the trial |
| `--allow-offline-cost-report` | `app.marcus.cli trial start` | bool | See above |
| `--require-live-llm` | pytest fixture (DEFERRED per `2a.2-followon-require-live-llm-flag`) | bool | Future: fail (not skip) when `@llm_live` tests would auto-skip |

### See also

- `docs/dev-guide/sources-of-truth.md` §2 "Models + cascade" — SSOT registry
- `docs/dev-guide/composition-specification.md` §3 — composition substrate
- `docs/operator/validation-scripts.md` — operator-run validation scripts (consume these parameters)
- `.env.example` — REQUIRED/RECOMMENDED/OPTIONAL env-var categorization
