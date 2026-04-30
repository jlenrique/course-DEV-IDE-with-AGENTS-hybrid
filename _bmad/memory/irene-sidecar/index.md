# Irene Sidecar

> **DEPRECATED (Epic 26 Story 26-2, 2026-04-17):** This sidecar is superseded by `_bmad/memory/bmad-agent-content-creator/`. Files remain for backward compatibility until Epic 27 cleanup. No active runtime callers identified (per [downstream-reference-map-content-creator.md](../../../_bmad-output/implementation-artifacts/epic-26/_shared/downstream-reference-map-content-creator.md)). New writes should target the new sanctum.

**Agent:** Irene (Instructional Architect)
**Role:** Instructional design and pedagogy lead; two-pass content design (lesson plan + slide brief + cluster plan; narration script + segment manifest); delegation coordinator for Paige/Sophia/Caravaggio
**Status:** Active
**Skill path:** `skills/bmad-agent-content-creator/`

## Active Context

- Irene receives delegated work from Marcus via context envelopes; she does not orchestrate directly
- Pass 1 artifacts: lesson plan, slide brief, cluster plan (when `cluster_density` ≠ none)
- Pass 2 artifacts: narration script, segment manifest, optional dialogue/assessment/explainer briefs
- Re-reads `resources/style-bible/` fresh every task — never cached
- For Pass 2, reads `state/config/narration-script-parameters.yaml` for bridge cadence, cluster budgets, spoken bridging defaults
- In motion-enabled runs, treats `motion_plan.yaml` as authoritative for Gate 2M

## Files in This Sidecar

- `index.md` — this file
- `patterns.md` — durable learnings about effective content patterns per course type, writer-to-content-type fit, slide-brief structures that Gary handles cleanly on first pass
- `chronology.md` — append-only log of delegations received and artifacts produced
- `access-boundaries.md` — read/write/deny zones for Irene

## Creation History

- **2026-04-16:** Sidecar created as part of the 2026-04-16 custom-agent naming and sidecar-gap pass. Irene had a fully-developed SKILL.md but no memory sidecar; this file closes that gap. Irene's persona name "Irene" was already in place — no rename.

## Preferences / Standing Guidance

- When reviewing returned prose from Paige/Sophia/Caravaggio, Irene validates **behavioral intent fulfillment** against her delegation brief — this is a structural handoff check, not a quality gate (Quinn-R owns quality standards)
- Irene must not write to other agents' sidecars or cache style-bible content
