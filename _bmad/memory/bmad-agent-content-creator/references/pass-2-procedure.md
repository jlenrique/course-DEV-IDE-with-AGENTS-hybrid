---
name: pass-2-procedure
description: Irene's Pass 2 procedure — perception enforcement, narration with visual references, motion hydration and confirmation
---

# Pass 2 Procedure

> **Structural contract for segment-manifest emission** lives at [`./pass-2-authoring-template.md`](./pass-2-authoring-template.md). Read it before writing the manifest. Covers the three §7.1 failure modes (§6.3 no `motion_asset` legacy key; §6.4 `visual_file` on every non-null-visual-mode segment; §6.5 `motion_duration_seconds` carried forward from Motion Gate receipt). Pass 2 output is linted at end of Pack v4.2 §08 via [`scripts/validators/pass_2_emission_lint.py`](../../../scripts/validators/pass_2_emission_lint.py); failing lint blocks §08B Storyboard B.

Pass 2 begins after Gary generates slides and the operator approves them at HIL Gate 2. The context envelope includes approved `gary_slide_output`, may include prior `perception_artifacts` or `literal_visual_publish` staging receipts, and for motion-enabled runs includes `context_paths.motion_plan` / `motion_plan.yaml`.

## Intake

Pass 2 intake also consumes `narration_profile_controls` (11 keys from the Creative Director's creative directive, resolved into `state/config/narration-script-parameters.yaml` by the CD→resolver pipeline). These controls shape narration density, bridging weight, rhetorical register, and arc awareness. Read them from the active narration-script-parameters and apply them alongside bridge cadence and cluster word budgets.

## Retrieval intake (corroborate-only v1)

When retrieval artifacts are present, consume the Irene intake envelope before writing cluster narration. Required intake keys are `run_id`, `pass_2_cluster_id`, `suggested_resources_ref`, `intake_mode`, and `evidence_bolster_active`; `extraction_report_ref` is optional but expected in retrieval-enabled runs.

Scope lock for this version:

- Intake mode support is bounded to corroboration behavior (`intake_mode: corroborate`, or corroboration branch within `mixed`).
- The additive output field on a segment is `retrieval_provenance`.
- Full shape and worked examples live in [`./retrieval-intake-contract.md`](./retrieval-intake-contract.md).

Convergence-to-language mapping:

- Dual-source convergence (scite + consensus agreeing): `Corroborated by multiple independent sources, with support from peer-reviewed citation context and synthesis evidence.`
- Single-source convergence (scite only): `According to scite.ai citation-context analysis.`
- Single-source convergence (consensus only): `Per Consensus research synthesis.`
- Unknown or partial convergence: `According to available retrieval evidence.`

Graceful degradation rule:

- If the suggested-resources payload is empty for the cluster, or extraction rows yield no usable retrieval provenance, emit narration without intake phrasing and append `retrieval_empty_for_cluster_<cluster_id>` to `known_losses`.
- `evidence_bolster_active` governs whether corroboration phrasing is expected to appear when valid intake exists; it does not override empty-retrieval fail-closed behavior.

## Step 0 — Mandatory Perception Contract (Story 13.1)

Before any narration work, enforce the perception contract via `./scripts/perception_contract.py::enforce_perception_contract(envelope)`. This validates `perception_artifacts` presence, generates them inline via the image sensory bridge if absent, retries LOW-confidence slides once, and escalates persistent LOW to Marcus. Narration MUST NOT begin until this returns `status: "ready"` or Marcus authorizes proceeding despite LOW confidence.

See `skills/sensory-bridges/references/perception-protocol.md` for the five-step protocol.

## Step 1 — Parse and confirm perception

Read Gary's actual slide PNGs and metadata from `gary_slide_output`. Use `perception_artifacts[]` (canonical sensory bridge output, structured and confidence-scored) as the ground truth for what is visually on screen.

State interpretation with confidence per the universal perception protocol: "I see Slide N shows [description]. Confidence: HIGH/MEDIUM/LOW."

The `gary_slide_output[].visual_description` free-text field provides creative context; `perception_artifacts[]` provides auditable ground truth. Any `literal_visual_publish` metadata from Gary is provenance only; Irene still narrates from the approved local slide PNGs in `gary_slide_output`.

## Step 2 — Write narration with visual references, spoken bridges, and earned timing variance (Stories 13.2, 23.1)

Load `./runtime-variability-framework.md` and `./spoken-bridging-language.md`. Read `state/config/narration-script-parameters.yaml` for the active `bridge_cadence` caps (minutes and slides), cluster word budgets, and for `bridge_frequency_scale` / `spoken_bridge_policy` — these may change per run.

For each slide, run `./scripts/visual_reference_injector.py::inject_visual_references` to select visual elements from `perception_artifacts` and produce `visual_references[]` metadata. Weave `visual_references_per_slide` (from `narration-script-parameters.yaml`, default 2, ±1 tolerance) explicit deictic references into the narration flow. Each reference names a specific perceived visual element with spatial context and narrates an insight about it.

Write narration that *complements* the confirmed visual content (not duplicates — narrate the insight, not the structure). Use Marcus's `runtime_plan` as a planning signal, but make slide-length variation come primarily from slide purpose, concept density, and visual burden rather than from arbitrary expansion.

### Cluster-aware processing

When the manifest contains clustered segments (`cluster_id` present), process them cluster-by-cluster in manifest order so the head segment establishes the semantic envelope before any interstitials. Every clustered segment must still be grounded in its own perceived slide, not inferred from the head alone. Apply the cluster contract explicitly:

- **Head segments** (`cluster_role: head`) use `cluster_head_word_range` and establish the topic, hook, and cluster frame.
- **Interstitials** (`cluster_role: interstitial`) use `interstitial_word_range`, focus on the slide's `isolation_target`, and assume the visual carries most of the meaning; narration supplies the missing interpretation rather than reteaching the whole topic.
- Interstitials must not introduce new concepts outside the head segment's instructional scope. Treat the head slide's `source_ref` plus the current interstitial's perceived detail as the allowed semantic boundary.
- **Segment `behavioral_intent`** must serve the cluster's `master_behavioral_intent`. It may intensify or modulate the cluster affect, but it must not contradict or redirect it.

### Bridge cadence discipline

Follow the configured **bridge cadence** so explicit intros/outros appear often enough in **spoken** narration (not only as manifest tags): when `bridge_type` is `intro`, `outro`, `both`, `pivot`, or `cluster_boundary`, the learner-facing narration text must include natural connective language unless enforcement is off.

In clustered runs, suppress routine within-cluster bridges by default. Only `cluster_position: tension` may carry `bridge_type: pivot`, and that pivot should be a brief tonal turn rather than a full seam recap. Seams between clusters should use `bridge_type: cluster_boundary` with a two-part beat: one sentence synthesizing what the prior cluster established, then one sentence pulling the learner into the next topic.

Scale bridge verbosity with `bridge_frequency_scale` while respecting cadence caps. For every segment, record `timing_role`, `content_density`, `visual_detail_load`, a concise `duration_rationale`, and `bridge_type` when that segment carries an explicit bridge beat.

Produce narration script + segment manifest. Optionally produce dialogue scripts, assessment briefs, first-person explainers if requested. Return structured results to Marcus.

## Step 3 — Motion-enabled branch (Epic 14)

If `motion_enabled: true`, load `context_paths.motion_plan` / `motion_plan.yaml` and treat it as the source of truth for per-slide Gate 2M designations. Run `./scripts/manifest_visual_enrichment.py::apply_motion_plan_to_segments` so the segment manifest inherits `motion_type`, `motion_asset_path`, `motion_source`, `motion_duration_seconds`, `motion_brief`, and `motion_status` from the motion plan.

Fail closed on unknown `slide_id` mappings or incomplete non-static assignments. If `motion_enabled: false`, keep every segment explicitly static.

## Step 4 — Motion perception confirmation (Epic 14)

Before final handoff on any non-static segment, run `./scripts/perception_contract.py::enforce_motion_perception_contract(...)`. Approved/generated/imported motion assets must be readable and perception-confirmed before Irene returns the final manifest to Marcus.

Static segments bypass this step and remain governed by the approved slide PNG plus image perception artifacts.
