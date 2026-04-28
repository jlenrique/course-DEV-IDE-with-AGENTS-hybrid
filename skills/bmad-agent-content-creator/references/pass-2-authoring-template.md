# Irene Pass 2 Authoring Template

Canonical authoring-time contract for Irene Pass 2 output.

Slab 6.4 source of truth: [`app/specialists/irene/authoring/pass_2_template.py`](../../../app/specialists/irene/authoring/pass_2_template.py).
Generated JSON Schema: [`schema/irene_pass_2_authoring.v1.schema.json`](../../../schema/irene_pass_2_authoring.v1.schema.json).
Procedural validator: [`skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`](../../bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py).

Validation order is contractual:

1. Schema-first validation with `IrenePass2AuthoringEnvelope`.
2. Procedural validation with `validate-irene-pass2-handoff.py`.

The Pydantic model is authoritative for field names, closed values, cardinality,
UTC timestamp shape, local PNG path shape, and cross-artifact identity checks.
The procedural validator remains authoritative for narration-prose checks,
bridge cadence, cluster arc continuity, behavioral-intent parity, motion
perception confirmation, and visual-reference traceability in spoken narration.

## Pydantic Field Inventory

Top-level fields:
`schema_version`, `run_id`, `generated_at_utc`, `composition_mode`,
`gary_slide_output`, `perception_artifacts`, `segment_manifest`,
`narration_script_markers`, `procedural_rules`.

Gary slide fields:
`slide_id`, `card_number`, `file_path`, `source_ref`.

Perception artifact fields:
`slide_id`, `source_image_path`, `visual_elements`.

Segment fields:
`id`, `slide_id`, `card_number`, `narration_text`, `behavioral_intent`,
`visual_file`, `visual_detail_load`, `timing_role`, `content_density`,
`duration_rationale`, `bridge_type`, `visual_references`, `cluster_id`,
`cluster_role`, `cluster_position`.

Visual reference fields:
`element`, `location_on_slide`, `narration_cue`, `perception_source`.

## Closed Values

- `composition_mode`: isolated, composed.
- `visual_detail_load`: light, medium, heavy.
- `content_density`: light, medium, heavy.
- `bridge_type`: none, intro, outro, pivot, both, cluster_boundary.
- `cluster_role`: head, interstitial.
- `cluster_position`: establish, tension, develop, resolve.
- `procedural_rules`: behavioral_intent_parity, bridge_cadence,
  cluster_arc_continuity, motion_perception_confirmation,
  narration_cue_presence, traceable_visual_references.

## Required Authoring Guarantees

- `generated_at_utc` is timezone-aware UTC.
- Every Gary `file_path`, perception `source_image_path`, and segment
  `visual_file` is a local PNG path.
- Every Gary slide has a matching perception artifact.
- Each perception `source_image_path` exactly matches the Gary `file_path` for
  the same `slide_id`.
- Each segment `visual_file` and `card_number` exactly match the Gary slide
  output for the same `slide_id`.
- Each segment `id` appears in `narration_script_markers`.
- If a segment has `cluster_id`, it must also have `cluster_role`.
- `procedural_rules` must list the complete validator-enforced rule set.

## Minimal Passing Shape

```yaml
schema_version: irene-pass-2-authoring.v1
run_id: PASS2-GOLDEN-001
generated_at_utc: 2026-04-28T10:00:00Z
composition_mode: composed
gary_slide_output:
  - slide_id: slide-01
    card_number: 1
    file_path: bundle/slide-01.png
    source_ref: slide-brief.md#Slide 1
perception_artifacts:
  - slide_id: slide-01
    source_image_path: bundle/slide-01.png
    visual_elements:
      - description: Clinician at workstation
segment_manifest:
  segments:
    - id: seg-01
      slide_id: slide-01
      card_number: 1
      narration_text: Notice the clinician at the workstation as the systems signal appears.
      behavioral_intent: credible
      visual_file: bundle/slide-01.png
      visual_detail_load: medium
      timing_role: concept-build
      content_density: medium
      duration_rationale: Medium density needs guided explanation while keeping visual attention on the workstation.
      bridge_type: none
      visual_references:
        - element: Clinician at workstation
          location_on_slide: center
          narration_cue: clinician at the workstation
          perception_source: slide-01
narration_script_markers:
  - seg-01
procedural_rules:
  - behavioral_intent_parity
  - bridge_cadence
  - cluster_arc_continuity
  - motion_perception_confirmation
  - narration_cue_presence
  - traceable_visual_references
```

## Worked Examples From B-Run Section 08

### Example 1: Empty Perception And Path Drift

B-Run Section 08 recorded an empty perception list and later path drift between
perception image paths and Gary slide outputs. The Pydantic contract prevents
that by requiring at least one perception artifact and by enforcing exact path
parity against the Gary output.

```yaml
gary_slide_output:
  - slide_id: slide-04
    card_number: 4
    file_path: bundle/gamma-export/slide-04.png
    source_ref: slide-brief.md#Slide 4
perception_artifacts:
  - slide_id: slide-04
    source_image_path: bundle/gamma-export/slide-04.png
```

If `perception_artifacts` is empty or `source_image_path` points elsewhere,
schema-first validation rejects the handoff before narration work proceeds.

### Example 2: Invalid Visual Detail Vocabulary

B-Run Section 08 recorded invalid visual-detail values. The Pydantic contract
uses the same closed density vocabulary as the procedural validator.

```yaml
visual_detail_load: heavy
content_density: medium
```

Values outside light, medium, and heavy are rejected by both Pydantic and the
generated JSON Schema.

### Example 3: Cluster Arc And Bridge Cadence

B-Run Section 08 recorded a cluster head resolving too early and a boundary
that lacked required bridge treatment. The schema makes cluster role and arc
position explicit so the procedural validator can reason over the sequence.

```yaml
cluster_id: c-u07
cluster_role: head
cluster_position: establish
bridge_type: cluster_boundary
```

For clustered segments, Irene must choose the role and position deliberately.
The procedural validator then rejects disordered arcs, resolve-without-middle
beats, missing callbacks, and cluster-boundary bridge-cadence failures.

## Operating Rule

Irene Pass 2 should author against this contract before emitting downstream
artifacts. If schema-first validation fails, repair the structured handoff
before invoking procedural validation. If procedural validation fails, repair the
specific validator-reported rule without loosening the Pydantic contract.
