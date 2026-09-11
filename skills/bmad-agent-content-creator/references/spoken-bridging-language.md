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

## Configured phrase lists

These are the live default substrings from `pedagogical_bridging.spoken_bridge_policy` in `state/config/narration-script-parameters.yaml`. Re-read that file each Pass 2; a run may override them. Matching is case-insensitive substring, not paraphrase.

**Intro-class** (`intro`, and the intro half of `both`):

- `in this section`
- `let's turn to`
- `we'll begin`
- `welcome`
- `to start`

**Outro-class** (`outro`, the outro half of `both`, and the forward-pull half of a `cluster_boundary` seam):

- `next, we'll`
- `to wrap up`
- `moving forward`
- `in summary`
- `that brings us`

Natural cluster-boundary pulls may also use: `now we`, `now look`, `turn to`, `look at`, `from here`, `that sets up`, `let's look`, `let's take`, `into the next`, `the next`.

## Authoring rules

1. For every segment with `bridge_type: intro`, the **spoken narration** must include at least one natural intro-class cue (section orient, welcome beat, or explicit pivot) that matches one of the configured `intro_phrase_patterns` substrings (case-insensitive), unless the production run disables enforcement.
2. For `bridge_type: outro`, include at least one outro-class cue (handoff, summary stitch, forward pointer) matching `outro_phrase_patterns`.
3. For `bridge_type: both`, include **both** an intro-class and an outro-class cue somewhere in the same segment's narration (order flexible; avoid mechanical bookending if it harms flow).
4. For `bridge_type: cluster_boundary`, write a **two-part seam**: one sentence synthesizing what the prior cluster established, then one sentence pulling the learner toward the next topic. Do **not** treat this as `both`. Do not force an intro-class substring (`in this section`, `we'll begin`). The second sentence must contain a forward-pull cue from the outro-class list or the natural seam-pull list above.
5. For `bridge_type: none`, do **not** add fake bridges solely to satisfy cadence metadata. Move the explicit bridge to the next segment where `bridge_type` is non-`none` and cadence allows.

## Delegation to writers

When Irene delegates narration prose, the delegation brief must state:

- The required `bridge_type` for that segment.
- The configured cadence caps (minutes/slides) so the writer knows how many segments need explicit bridges across the lesson.
- The `bridge_frequency_scale` so the writer knows whether bridges should be **minimal** (short clause), **moderate** (sentence), or **rich** (short paragraph beat).
- Whether the segment is inside a cluster, at a cluster seam, or at a tension pivot.

Returned prose must be edited so the **Narration** body satisfies the patterns above before Irene locks the manifest.

## Validator

The handoff validator may emit advisory cue/seam-shape notes. Fail-closed spoken-bridge *quality* and G4-18 teaching-scope are Vera-agentic (G4-12 + G4-18). `cluster_boundary` is a two-part seam, not `both`. See `skills/bmad-agent-fidelity-assessor/references/gate-evaluation-protocol.md`.
