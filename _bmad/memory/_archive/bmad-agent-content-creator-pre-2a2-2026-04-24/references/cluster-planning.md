---
name: cluster-planning
code: CP
description: Umbrella capability — full Pass 1 cluster planning workflow coordinating CD, NA, DC, IB, CS
---

# Cluster Planning (CP, Umbrella Capability)

Authoritative content is distributed across the five cluster-intelligence refs. This file registers the umbrella capability with its unique code and lists the coordination sequence.

## Summary

Cluster planning is the Pass 1 workflow for deciding which slides become cluster heads, selecting template structures, generating interstitial briefs, assigning narrative arcs + master behavioral intent, and planning bridges. It coordinates five underlying capabilities in a specific order.

## When to invoke

- Pass 1 when the context envelope includes `cluster_density` ≠ none.
- Pass 1 when the operator explicitly requests cluster evaluation even at low density.
- Pre-Gate 1.5 cluster-plan quality gate.

## Procedure (coordinating sequence)

1. **CD — Cluster decision criteria** — evaluate each slide for clustering potential (concept density, visual complexity, pedagogical weight, operator input). See `./cluster-decision-criteria.md`.
2. **CS — Content sequencing** — order candidate clusters so the narrative progresses simply→complex, known→novel. See `./content-sequencing.md`.
3. **DC — Cluster density controls** — apply run-level `CLUSTER_DENSITY` and per-slide overrides; assign interstitial counts. See `./cluster-density-controls.md`.
4. **NA — Narrative arc schema** — assign `narrative_arc` and `master_behavioral_intent`; determine `develop_type` for develop-position slides. See `./cluster-narrative-arc-schema.md`.
5. **IB — Interstitial brief specification** — for each selected interstitial, generate the constrained 6-field brief that Gamma will consume. See `./interstitial-brief-specification.md`.
6. **Bridge planning** — emit cluster-boundary + cluster-position bridge tags for Pass 2 (Irene reads these in `./spoken-bridging-language.md`).
7. **Populate cluster manifest fields** — write cluster_id, cluster_role, cluster_position, parent_slide_id, interstitial_type, isolation_target, narrative_arc, cluster_interstitial_count, double_dispatch_eligible.

## Outputs

- Expanded cluster plan (part of the Pass 1 lesson plan + slide brief return).
- Interstitial briefs appended to the slide brief for Gary's dispatch.

## Gates

- Passes through G1.5 cluster-plan quality gate before Gary dispatch.
