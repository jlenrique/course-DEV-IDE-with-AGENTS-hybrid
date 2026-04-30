# Cluster Manifest Reference

This reference summarizes the interstitial slide cluster schema extension (Story 19.1) for Marcus's use in explaining cluster fields to the HIL operator.

## Cluster Fields Summary

The segment manifest now includes these additive fields for clustered presentations:

- `cluster_id` (string, nullable): Unique identifier for the cluster; null for non-clustered runs
- `cluster_role` (enum, nullable): Membership role: `head` (first in cluster) or `interstitial` (supporting slides)
- `cluster_position` (enum, nullable): Narrative position in cluster arc: `establish` (orient), `develop` (deepen/reframe/exemplify), `tension` (complicate), `resolve` (land meaning)
- `develop_type` (enum, nullable): Sub-type for `develop` position: `deepen` (unpack), `reframe` (recontextualize), `exemplify` (illustrate)
- `parent_slide_id` (string, nullable): For interstitials, references the head slide's `id`
- `interstitial_type` (enum, nullable): Visual strategy: `reveal` (zoom/isolate), `emphasis-shift` (highlight one element), `bridge-text` (key phrase), `simplification` (reduce complexity), `pace-reset` (rest visual)
- `isolation_target` (string, nullable): Specific element from head slide to surface (e.g., "working memory box")
- `narrative_arc` (string, nullable): One-sentence emotional journey (e.g., "From confusion to clarity through progressive disclosure")
- `cluster_interstitial_count` (int, nullable): Planned interstitial count for cluster (1-3)
- `double_dispatch_eligible` (boolean, nullable): Whether segment can use double-dispatch; defaults true, false for interstitials in MVP

## Full Schema Reference

See `skills/bmad-agent-content-creator/references/template-segment-manifest.md` for the complete canonical schema, including field descriptions, migration notes, and examples.

## MVP Context

- Clusters are additive to existing workflows (narrated-deck-video-export / narrated-lesson-with-video-or-animation)
- Head establishes topic, interstitials progressively disclose elements without introducing new concepts
- Supports 1-3 interstitials per cluster, 3 clusters per C1M1 presentation
- Decision criteria from 20a-1, brief spec from 20a-2

## Related Stories

- 19.1: Schema foundation (this reference)
- 20a-1: Cluster decision criteria
- 20a-2: Interstitial brief specification standard