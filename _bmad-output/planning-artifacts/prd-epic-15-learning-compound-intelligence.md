---
title: PRD — Epic 15: Learning & Compound Intelligence
status: SKELETON (pre-Trial-3 cleanup S5 Tier-2; awaiting first-trial evidence)
authoredAt: 2026-05-07
authority: pre-S5 review (Mary lead + Murat + Winston) — recommended skeleton-now-fill-post-Trial-3
reactivationTrigger: first-tracked-trial-completes (Trial-3 PASS or PARTIAL-PASS); operator party-mode at that point ratifies full PRD
---

# Epic 15 — Learning & Compound Intelligence

## Status

**SKELETON.** Authored at pre-Trial-3 cleanup S5 Tier-2 (2026-05-07) per Mary recommendation: skeleton-now means post-Trial-3 PASS reactivation is <1 session of operator + party-mode work, not 1+ week. Full PRD authoring fires when Trial-3 reaches PASS or PARTIAL-PASS.

## Operator-directive context

The operator's standing intent: convert tracked production runs into organizational intelligence — not just per-trial postmortems but *compound* learning where Trial-N+1 benefits structurally from Trial-N's evidence. Per `epics.md` §Epic 15 seed: 15-1 through 15-7 (7 stories total).

## Reactivation triggers

- **15-1-lite-marcus** (Epic 33 meta-test) unblocks the chain's first link — provides the learning-event-ledger infrastructure that 15-2+ consumes
- **First tracked trial completes** (Trial-3 PASS or PARTIAL-PASS) — evidence base for 15-2 retrospective artifact
- **Operator party-mode ratification** — required before Epic 15 dispatch (per Pipeline Manifest Regime: Epic 15 introduces learning-event-schema as load-bearing contract; Tier-2 minimum, possibly Tier-3 if pack-family implications)

## Scope (skeleton — full FRs/NFRs at reactivation)

Seven stories per the existing seed at `_bmad-output/planning-artifacts/epics.md §Epic 15`:

1. **15-1 Learning Event Ledger** — schema + capture + persistence; the substrate every other story consumes
2. **15-2 Per-Trial Retrospective Artifact** — automated postmortem-shape evidence pack consumed by `bmad-retrospective` skill
3. **15-3 Upstream Feedback Routing** — Trial-N learnings inform Trial-N+1 launch decisions (corpus shape; specialist roster; gate set)
4. **15-4 Synergy Scorecard** — cross-specialist coordination signals; "where did this trial cohort outperform expected"
5. **15-5 Pattern Condensation** — `cross-trial-learnings.md` synthesis automated (manual at S3; automated at 15-5)
6. **15-6 Workflow-Family Ledger** — narrated-lesson-vs-deck-vs-podcast cross-pack-family learning
7. **15-7 Calibration Harness** — calibration tripwire + engagement decay reports become input to next-trial budget

## Dependencies (mandatory predecessors before 15-1 dispatch)

- **`docs/trials/methodology.md`** S3 deliverable — provides the per-trial postmortem shape Epic 15 consumes
- **`docs/trials/cross-trial-learnings.md`** S3 deliverable — provides the manual register that 15-5 will automate
- **First tracked trial postmortem** — provides the first concrete evidence base
- **`bmad-retrospective` skill** — already exists; Epic 15 supplements not replaces

## Success criteria (skeleton; refine at full PRD)

- 15-1 lands learning-event-schema + capture + persistence; per-PR CI green; substrate for 15-2+
- 15-2 produces retrospective-artifact-shape that operator can read in <15 min; matches Trial-3 postmortem manual shape
- 15-3 produces measurable Trial-N+1 launch-decision input (e.g., corpus shape recommendation; specialist roster delta)
- 15-4 produces cross-specialist signal that party-mode reads at retrospective; orthogonal to existing tripwire ledger
- 15-5 automated `cross-trial-learnings.md` synthesis matches manual S3 cadence (per 3 trials OR Epic-close)
- 15-6 ledger captures cross-pack-family learning when 2+ pack families ship
- 15-7 calibration harness output becomes binding input to next-trial budget

## Open questions (defer to full-PRD authoring)

- Schema authority: pydantic v2 model + JSON schema (four-file-lockstep per `pydantic-v2-schema-checklist.md`)?
- Storage: per-trial JSON + cross-trial digest? Database? File-based ledger?
- Privacy / data-classification: trial transcripts contain operator notes; what's redaction discipline?
- Retention: how long do per-trial ledger entries persist? Compaction at year-boundary?
- Integration with `app/marcus/orchestrator/`: read-only consumer? Active feedback channel?

## Authoring plan (full PRD)

When reactivation fires (post-Trial-3 PASS):
1. Convene party-mode (John + Mary + Winston + Quinn-R + operator)
2. Use `methodology.md` + `cross-trial-learnings.md` + Trial-3 postmortem as evidence base
3. Author full PRD using `bmad-create-prd` workflow; ratify FRs/NFRs/scope per BMAD discipline
4. File epic story specs for 15-1 through 15-7; populate sprint-status entries
5. Dispatch 15-1 (the substrate) first; subsequent stories chain on it

## References

- `_bmad-output/planning-artifacts/epics.md §Epic 15` — original seed
- `docs/trials/methodology.md` — pre-S5 S3 deliverable; binding input
- `_bmad-output/planning-artifacts/deferred-inventory.md` §Backlog Epics — Epic 15 status entry (shows reactivation trigger "at least one tracked trial run completed")
- `_bmad-output/implementation-artifacts/15-1-lite-marcus.md` — Epic-33 meta-test that unblocks 15-1 (already authored)
- `_bmad-output/implementation-artifacts/codex-dev-prompt-15-1-lite-marcus.md` — Codex dev-prompt for 15-1-lite-marcus
- Named follow-ons in deferred-inventory: `15-1-lite-irene` and `15-1-lite-gary` (file when 15-1-lite-marcus closes CLEAN)
