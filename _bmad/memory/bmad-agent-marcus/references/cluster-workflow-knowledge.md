---
name: cluster-workflow-knowledge
description: Marcus's knowledge of the interstitial slide cluster schema and workflow (Epics 19-24, 20c)
---

# Cluster Workflow Knowledge (Interstitial MVP)

Marcus understands the interstitial slide cluster schema extension (Story 19.1) and can explain cluster fields to the HIL operator.

## Cluster Fields

`cluster_id`, `cluster_role` (`head` | `interstitial`), `cluster_position` (`establish` | `develop` | `tension` | `resolve`), `develop_type` (`deepen` | `reframe` | `exemplify`), `parent_slide_id`, `interstitial_type` (`reveal` | `emphasis-shift` | `bridge-text` | `simplification` | `pace-reset`), `isolation_target`, `narrative_arc`, `cluster_interstitial_count`, `double_dispatch_eligible`.

## Cluster Workflow

Clusters are additive to `narrated-deck-video-export` / `narrated-lesson-with-video-or-animation`. Head establishes topic; interstitials progressively disclose elements without introducing new concepts. MVP supports 1-3 interstitials per cluster, 3 clusters per C1M1 presentation.

## Decision Criteria

Clusters used for complex topics needing progressive disclosure (from 20a-1). Brief spec (20a-2) defines editorial quality bar.

## Routing

For cluster requests, delegate to Irene for cluster-aware narration (Pass 2), ensure manifest includes cluster fields, validate at G4.

## HIL Communication

Explain clusters as "head slide + supporting interstitials" for progressive disclosure, cite `template-segment-manifest.md` for field details.

## Related Contracts

- **G1.5 cluster plan** — Irene Pass 1 cluster plan validation gate.
- **G4 cluster rules** — narration script with cluster bridges (see `state/config/fidelity-contracts/g4-narration-script.yaml`, Epic 23).
- **G3 generated slides** — cluster fields preserved through dispatch (Epic 19).
- **Storyboard A** — pre-Pass-2 clustered preview (Epic 22, story 22-1).
- **Storyboard B** — post-Pass-2 clustered preview with script context (Epic 22, story 22-2).
