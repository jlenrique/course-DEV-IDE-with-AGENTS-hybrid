---
name: spoken-bridging-language
code: SB
description: Spoken pedagogical bridging — align manifest bridge_type with learner-heard intro/outro language per cadence + frequency scale
---

# Spoken Bridging Language (Irene Pass 2)

**Purpose:** Ensure learner-facing **audio** includes explicit connective tissue when the segment manifest marks `bridge_type` as `intro`, `outro`, `both`, or `cluster_boundary`. Metadata alone is not sufficient: ElevenLabs and learners only experience what appears in `narration_text` / the narration script body.

## Relationship to cadence and scale

- **When bridges must appear** is governed by `runtime_variability.bridge_cadence` in `state/config/narration-script-parameters.yaml` (`require_intro_or_outro_every_minutes`, `require_intro_or_outro_every_slides`). Future runs may tighten or loosen those caps; Irene must re-read them each Pass 2.
- Clustered runs may override cadence with `cluster_bridge_cadence_override: true`, which means seams between clusters should usually carry `bridge_type: cluster_boundary` before slide/minute caps force a generic bridge.
- **How prominent each bridge line is** (one short beat vs a fuller orient/summary) is guided by `pedagogical_bridging.bridge_frequency_scale` (`minimal` | `moderate` | `rich`). This does not replace cadence; it modulates verbosity once a bridge is warranted.
- Inside a cluster, `within_cluster_bridge_policy.default: none` suppresses routine bridge language. Only `cluster_position: tension` may use a brief pivot beat when the policy explicitly allows it.

## Authoring rules

1. For every segment with `bridge_type: intro`, the **spoken narration** must include at least one natural intro-class cue (section orient, welcome beat, or explicit pivot) that matches one of the configured `intro_phrase_patterns` substrings (case-insensitive), unless the production run disables enforcement.
2. For `bridge_type: outro`, include at least one outro-class cue (handoff, summary stitch, forward pointer) matching `outro_phrase_patterns`.
3. For `bridge_type: both`, include **both** an intro-class and an outro-class cue somewhere in the same segment's narration (order flexible; avoid mechanical bookending if it harms flow).
4. For `bridge_type: cluster_boundary`, write a two-part seam: one sentence synthesizing what the prior cluster established, then one sentence pulling the learner toward the next topic.
5. For `bridge_type: none`, do **not** add fake bridges solely to satisfy cadence metadata. Move the explicit bridge to the next segment where `bridge_type` is non-`none` and cadence allows.

## Delegation to writers

When Irene delegates narration prose, the delegation brief must state:

- The required `bridge_type` for that segment.
- The configured cadence caps (minutes/slides) so the writer knows how many segments need explicit bridges across the lesson.
- The `bridge_frequency_scale` so the writer knows whether bridges should be **minimal** (short clause), **moderate** (sentence), or **rich** (short paragraph beat).
- Whether the segment is inside a cluster, at a cluster seam, or at a tension pivot.

Returned prose must be edited so the **Narration** body satisfies the patterns above before Irene locks the manifest.

## Validator

Deterministic checks live in `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py` and use `pedagogical_bridging.spoken_bridge_policy` patterns from the same YAML file. Vera documents this as **G4-16** in `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md` (G4 deterministic checks list).
