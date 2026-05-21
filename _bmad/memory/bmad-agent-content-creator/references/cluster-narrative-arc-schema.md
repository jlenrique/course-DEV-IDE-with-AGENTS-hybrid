---
name: cluster-narrative-arc-schema
code: NA
description: Cluster narrative arc schema — narrative_arc field rules, master_behavioral_intent subordination, develop sub-type assignment
---

# Cluster Narrative Arc Schema

This document defines the schema for cluster-level narrative arcs and behavioral intent in interstitial slide clusters. It establishes the value rules for the `narrative_arc`, `master_behavioral_intent`, and `develop_type` fields used by downstream cluster work.

## Scope

This reference defines how Irene should populate and validate:

- `narrative_arc`
- `master_behavioral_intent`
- `develop_type`

All three are represented in the segment manifest template consumed by downstream cluster planning, narration, and review flows.

## Narrative Arc Field Schema

### Sentence Structure

The `narrative_arc` field contains a single sentence describing the cluster's learner journey.

Format:

`From [start state] to [end state] through/via [mechanism]`

- **start state:** the learner's cognitive or affective position entering the head slide
- **end state:** the learner's position leaving the resolve slide
- **mechanism:** what the cluster does to move the learner between states

The sentence must be specific enough that a narration writer and review gate can verify each segment serves it.

### Quality Bar

Pass:
- `From overload awareness to capacity management through targeted interventions`
- `From confusion to clarity through progressive disclosure`
- `From skepticism to confidence through evidence-based reasoning`

Fail:
- `From introduction to understanding`
- `From problem to solution`
- `From start to finish through explanation`

The failure mode is always the same: the sentence is generic enough to fit almost any cluster and therefore guides nothing.

### Inheritance Rule

The `narrative_arc` is set on the head slide and inherited by all cluster members.

## Sophia's Four-Beat Framework Mapping

Cluster positions map to Sophia's narrative beats as follows:

| Sophia Beat | Cluster Position | Narrative Role |
|---|---|---|
| orient | establish | Plant the hook, state the thesis, orient the learner |
| complicate | tension | Introduce the "yes but", contrast, complication |
| illuminate | develop | Deepen, reframe, or exemplify to move the learner through the tension |
| resolve | resolve | Land the meaning, echo the head, close the arc |

When all four beats are present, the canonical beat order is:

`establish -> tension -> develop -> resolve`

Shorter clusters may collapse one middle beat for a 2-interstitial structure, but `develop` should not be documented as the default beat before `tension`.

## Master Behavioral Intent Schema

### Definition

The `master_behavioral_intent` is the cluster-level behavioral directive. It sets the dominant affect for the cluster and constrains the allowable segment-level `behavioral_intent` values.

### Vocabulary

Use the same enumerated vocabulary as segment-level `behavioral_intent`:

- `credible`
- `alarming`
- `provocative`
- `reflective`
- `moving`
- `clear-guidance`
- `attention-reset`

Fail examples:
- `make it feel important`
- `emotionally strong`
- `be persuasive somehow`

Those are free-form instructions, not contract values.

### Subordination Rule

Segment-level `behavioral_intent` values must serve, not contradict, the cluster's `master_behavioral_intent`. A segment may intensify or modulate the master intent, but it may not reverse it.

Valid combination:
- Master: `alarming`
- Establish: `credible`
- Tension: `alarming`
- Resolve: `clear-guidance`

Invalid combination:
- Master: `credible`
- Tension: `provocative`

That second pairing asks the cluster to build trust and then undercut it with a contradictory affect.

## Develop Sub-Type Assignment Rules

Each `develop`-position interstitial must use one of these sub-types:

- `deepen` - extend the establish concept
- `reframe` - change the frame of reference
- `exemplify` - provide a concrete case or instance

Within a cluster, each `develop` interstitial must use a distinct sub-type.

Assignment guidance:
- `deepen` for unpacking an idea already introduced
- `reframe` for misconception correction or perspective shift
- `exemplify` for abstract concepts that need a concrete case

## C1M1 MVP Example

**Cluster Topic:** Cognitive Load Theory

- `narrative_arc`: `From overload awareness to capacity management through targeted interventions`
- `master_behavioral_intent`: `clear-guidance`
- Establish: `credible`
- Tension: `alarming`
- Develop: `exemplify`
- Resolve: `clear-guidance`

This pattern works because the cluster earns trust, surfaces consequence, clarifies through example, and then lands on an actionable instructional takeaway.

## Contract Authority

This schema is the authoritative contract for:

- Irene Pass 1 cluster planning (Epic 20B)
- Interstitial brief writing
- Narration alignment validation
- Storyboard cluster rendering

All downstream cluster-aware agents and gates must honor these rules.
