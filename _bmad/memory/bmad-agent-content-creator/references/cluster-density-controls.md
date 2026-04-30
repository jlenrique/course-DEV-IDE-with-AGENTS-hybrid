---
name: cluster-density-controls
code: DC
description: Cluster density controls — CLUSTER_DENSITY run constant, per-slide overrides, interstitial count assignment
---

# Cluster Density Controls

This document defines the operator controls for Irene's cluster density behavior, allowing controlled tuning of clustering intensity per production run.

## Run Constant: `cluster_density`

### Definition

`cluster_density` is a run-level constant that sets Irene's overall clustering target for a presentation. It follows the same pattern as `double_dispatch`: a structural decision set once per run.

### Format

```yaml
cluster_density: default   # none | sparse | default | rich
```

### Levels

#### `none`
- Target: 0 clusters
- Behavior: all cluster fields null; identical to pre-Epic-19 runs
- Use case: legacy compatibility, non-clustered presentations
- Default when absent: treat as `none`

#### `sparse`
- Target: 1-2 clusters per presentation
- Behavior: minimal clustering for short runs or novice audiences
- Use case: brief presentations, introductory content, time-constrained sessions

#### `default`
- Target: 3-5 clusters per presentation
- Behavior: standard clustering for typical course content
- Use case: most presentations in the 10-15 slide range

#### `rich`
- Target: 6+ clusters per presentation
- Behavior: dense clustering for complex, progressive-disclosure content
- Use case: high-density topics where clustering is the primary teaching strategy

## Per-Slide Operator Overrides

Operator overrides are specified in Prompt 2A `special_treatment_directives`:

```yaml
special_treatment_directives:
  - "Force cluster on [slide description or position] with [N] interstitials"
  - "Suppress cluster on [slide description or position]"
```

Examples:

```yaml
special_treatment_directives:
  - "Force cluster on the cognitive load theory slide with 2 interstitials"
  - "Suppress cluster on the module welcome slide"
  - "Force cluster on the working memory diagram with 3 interstitials"
```

### Parsing Rules

- Irene reads `operator-directives.md` during Pass 1.
- Force/suppress directives take precedence over the scoring framework.
- `cluster_interstitial_count` must be between 1 and 3.
- Ambiguous slide matching must produce an explicit warning or error.

## Interaction Rules

### Override Visibility

Operator overrides are logged in the cluster plan for Storyboard A review.

- Force on low-scoring slide: `Forced cluster on [slide]: scored LOW on concept density. Override honored.`
- Suppress on high-scoring slide: `Suppressed cluster on [slide]: scored HIGH on pedagogical weight. Override honored.`

### Density Cap Override

If `sparse` is set but operator forces 4 clusters via per-slide directives:

- Effective density becomes `default`
- Irene logs: `cluster_density: sparse overridden by 4 per-slide force directives - effective density: default.`

## Interstitial Count Assignment

### Default Heuristics

- 1 interstitial: single explanatory beat
- 2 interstitials: standard arc (`establish -> develop -> resolve`)
- 3 interstitials: full arc (`establish -> tension -> develop -> resolve`)

### Operator Override

`cluster_interstitial_count` can be set per forced cluster through Prompt 2A syntax.

### Error Handling

If operator specifies an invalid `cluster_interstitial_count`:

```text
Error: Invalid cluster_interstitial_count "4" for slide "cognitive load theory". Must be 1-3. Override rejected.
```

If a slide descriptor matches multiple slides:

```text
Warning: "Force cluster on the slide" matches 3 slides. Please specify slide 1, slide 2, or slide 3.
```

If a slide descriptor matches no slides:

```text
Error: "Force cluster on nonexistent slide" matches no slides. Override rejected.
```

## Precedence Rules

1. Per-slide force/suppress
2. Run-constant density
3. Irene judgment

If multiple overrides target the same slide, the last directive wins and Irene must log the outcome.

## Legacy Compatibility

- `cluster_density` absent means `none`
- Existing `run-constants.yaml` files remain valid
- Pre-cluster runs keep all cluster fields null

## Interactions with Other Constants

- `cluster_density: none` + `double_dispatch: true` should be treated as incompatible
- `cluster_density: rich` + `double_dispatch: false` should emit a warning about reduced fidelity
- `parent_slide_count`, `estimated_total_slides`, and `target_total_runtime_minutes` may constrain how many clusters are feasible

## Contract Authority

This schema is authoritative for:

- Irene Pass 1 cluster planning (Epic 20B)
- Prompt 2A template updates
- Run-constants validation
- Marcus preflight contract updates

## Integration with Decision Criteria

Density controls extend the operator-input criterion in `cluster-decision-criteria.md`. `cluster_density` expresses the run-level density preference, while per-slide overrides provide granular control.
