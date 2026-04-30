---
name: external-agent-registry
description: Irene's delegation targets — BMad writer agents and editorial reviewers
---

# External Agent Registry

Irene delegates all prose writing and editorial review. She does not author prose herself. This registry is the canonical list of delegation targets with the context each expects.

## External Agents

| Capability | Target Agent | Status | Context Passed |
|------------|-------------|--------|----------------|
| Technical explanatory writing (procedures, protocols, data narratives) | `bmad-agent-tech-writer` (Paige) | active | Delegation brief: objective, Bloom's level, audience, format, terminology, length |
| Narrative writing (case studies, vignettes, first-person explainers) | `bmad-cis-agent-storyteller` (Sophia) | active | Delegation brief: scenario premise, objective, characters, emotional arc, pedagogical purpose |
| Slide narrative design (visual hierarchy, attention flow, slide-script pairing) | `bmad-cis-agent-presentation-master` (Caravaggio) | active | Delegation brief: content outline, slide count, visual hierarchy, key visuals, pairing requirements |
| Prose polish (grammar, clarity, flow on individual pieces) | `bmad-editorial-review-prose` | active | Drafted prose from writer, original delegation brief for context |
| Structural coherence (assembled multi-piece artifacts) | `bmad-editorial-review-structure` | active | Assembled artifact, learning objective map, sequencing rationale |

## Delegation Protocol Reference

Full delegation workflow, writer selection matrix, brief templates, and review criteria: `./delegation-protocol.md`.

## Pairing Rules

- **Narration script + segment manifest** always ship together to downstream consumers (ElevenLabs, Kira, Compositor).
- **Slide brief + lesson plan** always ship together to Gary.
- **Case-study dialogue + segment manifest** pair for multi-voice ElevenLabs synthesis.

## Non-Delegation Interfaces

Irene also reads from and returns to:

- **Marcus** — inbound context envelope, outbound structured return (artifact paths, writer delegation log, pairing references, recommendations, scope violations).
- **Vera (fidelity-assessor)** — post-return; Vera validates fidelity at G1 / G2 / G4 against Irene's artifacts. Irene does not invoke Vera directly.
- **Quinn-R (quality-reviewer)** — post-return; Quinn-R runs pre-composition and post-composition passes. Irene does not invoke Quinn-R directly.
- **Compositor** — consumes Irene's completed segment manifest.
- **Creative Director (CD)** — Irene does not invoke CD; CD's resolved `narration_profile_controls` arrive in `state/config/narration-script-parameters.yaml` via Marcus.
