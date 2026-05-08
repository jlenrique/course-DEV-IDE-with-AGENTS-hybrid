---
title: Trial-Run Methodology — Standing Operations Document
authoredAt: 2026-05-07
authority: pre-Trial-3 cleanup S3 (party-mode-ratified at post-S3 review)
operator-directive: "Every run is, in effect, a trial run. We will always find glitches and/or opportunities. We need a robust mechanism for tracking and reflecting back on runs." (Juanl, 2026-05-07)
status: active; consult before launching any tracked trial
---

# Trial-Run Methodology

This document standardizes the cadence for production trial runs and the artifacts they produce. It is **NOT a PRD**. It is a **standing operations document** in the spirit of an SRE incident-postmortem template — applied per trial, refreshed as patterns emerge.

## §1 — Purpose & framing

Every production trial — Trial-3 onward — is an instance of an ongoing observation cadence. We do not treat trials as one-off ceremonies; we treat them as a **continuous learning surface**. Each trial produces evidence we collect, decisions we ratify, and learnings we file. Across trials we build cross-trial pattern detection that no single trial can produce alone.

This methodology serves three audiences:
1. **Operator (Juanl)** — needs unambiguous launch + reflection guidance under attention pressure.
2. **Future-self at Trial-(N+1) launch** — needs to find prior learnings before re-encountering them.
3. **Post-trial reviewers (party-mode)** — need a forensic shape that supports interpretation + ratification of trial outcomes.

Relationship to other artifacts:
- **`bmad-retrospective` skill** — fires at Epic-close; consumes per-trial postmortems as input.
- **Epic 15 (Learning & Compound Intelligence)** — the LEDGER infrastructure that this methodology eventually feeds (post-Trial-3 PASS reactivation).
- **`deferred-inventory.md`** — backlog work; this methodology fires reactivation triggers.
- **Anti-pattern catalogs** (`specialist-anti-patterns.md` + `dev-agent-anti-patterns.md`) — substrate/process anti-patterns; trial postmortems file new entries here.
- **Architecture decision log** (`architecture-langchain-langgraph-migration.md` §10) — D-entries; trial postmortems may shift or add.

## §2 — Run taxonomy

Three classes of "run." Methodology coverage differs per class:

| Class | Description | Postmortem? | Logged where? |
|---|---|---|---|
| **Tracked trial** | Operator-launched; full pipeline (G0 → G5); evidence-bearing; intent to ratify substrate readiness. **Trial-3 onward.** | YES (mandatory; per-run trio: launch + log + postmortem) | `docs/trials/trial-N/` |
| **Dev-cycle trial** | Single-story `bmad-dev-story` execution; Codex-driven; bounded scope. | OPTIONAL (only if high-signal) | per-story spec close + `_codex-handoff/` verdict |
| **Operator session work** | Planning, governance, sprint authoring, retrospectives. | NO (covered by `bmad-retrospective` at Epic close) | `SESSION-HANDOFF.md` + `next-session-start-here.md` |

Most of this document focuses on **tracked trials**. Dev-cycle trials inherit some elements (verdict framing) but skip the per-run trio.

## §3 — Evidence taxonomy

What we collect at each trial. Mapped to where it lives on disk.

| Evidence class | Source | Disk location |
|---|---|---|
| Pre-flight state snapshot | Operator + preflight runner | `docs/trials/trial-N/launch.md` (operator captures); `<bundle>/preflight-results.json` (runner emits) |
| Runtime artifacts (transcripts, run-id directories) | Production runner | `state/config/runs/<trial-id>/` |
| Gate decisions + verbs | Operator at each HIL surface | `docs/trials/trial-N/log.md` (operator records); `<run-dir>/run/decisions/` (runner persists) |
| Trial transcript | `Trial3Transcript` schema (FR-7c-51) | `<run-dir>/run/trial-transcript.json` |
| Tripwire firings | Tripwire ledger | `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` |
| Anti-pattern hits | Postmortem author | `docs/trials/trial-N/postmortem.md` (with filing target per §7) |
| Cycle metrics | wall-clock + cost | `docs/trials/trial-N/postmortem.md` |
| Cross-trial pattern emergence | Postmortem author at trio close | `docs/trials/cross-trial-learnings.md` (per §7) |

## §4 — Reflection cadence

Three tiers:

| Tier | When | Artifact | Owner |
|---|---|---|---|
| **Per-run** | Trial close (within 48h) | `docs/trials/trial-N/postmortem.md` | Operator + party-mode optional |
| **Cross-trial** | Per 3 trials OR per Epic close, whichever first | `docs/trials/cross-trial-learnings.md` synthesis section | Operator + Mary harvest-gate |
| **Epic-boundary** | Epic close | `bmad-retrospective` skill output | Multi-agent party-mode |

The per-run tier is mandatory for tracked trials. The cross-trial tier is a synthesis pass — it does NOT duplicate per-run findings; it identifies patterns across them. The epic-boundary tier is the existing `bmad-retrospective` mechanism; it consumes per-run postmortems.

## §5 — Verdict framing

Four verdicts per tracked trial:

| Verdict | Condition | Downstream action |
|---|---|---|
| **PASS** | Trial completes G0 → G5; transcript shape valid; ≥9-of-11 specialists exercised; tripwire ledger green; broad-regression delta ≤ 0 | Postmortem authored; deferred-inventory triggers fire (e.g., Epic 15 reactivation post-first-tracked-trial); next trial planned |
| **PARTIAL-PASS** | Trial reaches at least G3 with major-stage progress but does not reach G5 cleanly. Operator decides whether evidence base is sufficient for the trial's stated hypothesis. | Postmortem authored; explicit hypothesis-vs-evidence reconciliation; deferred-inventory entries filed for incomplete sections; re-run scheduled OR substrate gap escalated |
| **STRUCTURED-STOP** | Trial halts cleanly at a fail-loud point (specialist guardrail engaged; CI gate refused; etc.). The substrate honors its contracts; the run does not produce trial evidence but DOES produce diagnostic evidence. | Postmortem authored; finding(s) filed per §7; re-run after substrate fix lands. Trial-2 set the precedent (`trial-2-postmortem-2026-05-04.md`) |
| **FAIL** | Substrate behaves UNEXPECTEDLY (silent corruption, contract violation that didn't fail loud, data loss). Distinct from STRUCTURED-STOP because the runtime did NOT honor its contracts. | Operator escalation; party-mode investigation; halt all subsequent dev work until root cause identified; this is a HIGH-severity event |

Operator at trial-close declares verdict in `postmortem.md`. Verdicts are operator authority; party-mode review may dispute (PARTIAL-PASS ↔ STRUCTURED-STOP boundary is the most common dispute).

## §6 — Per-run trio contract

Each tracked trial produces exactly THREE artifacts under `docs/trials/trial-N/`:

| Artifact | When filled | Voice | Length target |
|---|---|---|---|
| **`launch.md`** | BEFORE trial starts | Pre-flight checklist + intentions prose + taped-highlight-reel | 1-2 pages; reads in 5 minutes |
| **`log.md`** | DURING trial OR compiled-from-runtime-artifacts immediately after | Append-only timeline pre-templated by gate; evidence-paste appendix | Variable; minimal interpretation, maximum fidelity |
| **`postmortem.md`** | Shape A AT trial close (mandatory; 15 min) + Shape B DEFERRED 48h (structured findings) | Reflection: 5 questions then structured forensic findings | Shape A 1 page; Shape B variable |

Templates at `docs/trials/trial-N-templates/{launch,log,postmortem}.md`. Each template carries a filled-example block at the top so the operator anchors against shape rather than authoring from blank.

## §7 — Filing-disposition matrix (load-bearing)

When a `postmortem.md` finding surfaces, the operator (or post-trial party-mode) routes it via four sequential questions. **First YES wins; do not file in two places.**

| # | Question | If YES, file at | Rationale |
|---|---|---|---|
| 1 | Is this a substrate or process anti-pattern reproducible *outside* the trial context? | `docs/dev-guide/specialist-anti-patterns.md` (substrate) OR `docs/dev-guide/dev-agent-anti-patterns.md` (process). Subject to format-freeze v1 + Mary harvest-gate (documented burn or party-mode consensus). | Anti-pattern catalog is for reusable failure-modes with prescriptive remediation. |
| 2 | Is this *backlog work* — substrate enhancement, follow-on story, deferred capability? | `_bmad-output/planning-artifacts/deferred-inventory.md` §Named-But-Not-Filed Follow-Ons (with reactivation trigger). | Deferred-inventory is for queued-but-not-filed work units. |
| 3 | Is this an *architectural decision shift* — a previously-locked D-entry needs revision OR a NEW D-entry is warranted? | `_bmad-output/planning-artifacts/architecture-langchain-langgraph-migration.md` §10 Decision Log (D15+; party-mode-gated). | D-Log is the architectural decision register; mutations are governance. |
| 4 | Is this a **pattern only meaningful when seen across multiple trials** OR a per-trial run-shape learning (cadence / evidence-collection / methodology adjustment)? | `docs/trials/cross-trial-learnings.md` | The cross-trial register fills the run-shaped slot no other register covers. |

**Postmortem hygiene check:** every finding has exactly ONE filing destination. The `postmortem.md` template's "Routing summary" sub-section enumerates findings → filing destinations and confirms zero double-filings + zero unfiled findings.

**Bidirectional citation discipline (trigger fires):**
- Trigger NAMED in deferred-inventory entry (existing convention)
- Trigger FIRES in `cross-trial-learnings.md` Trial-N entry: `## Trial-N reactivation triggers fired`
- Inventory entry CLOSURE strikethrough cites `cross-trial-learnings.md §Trial-N`
- Cross-trial entry cites the inventory entry name
- BOTH cite each other; never one-way

## §8 — Lifecycle & maintenance

This document itself is **subject to revision** based on accumulated trial experience.

- **Tier-1 prose updates** (clarifications; example refreshes): operator authority. Append `## Revisions` log entry.
- **Tier-2 structural changes** (verdict definitions; cadence changes; new sections): party-mode-ratified. Quinn-R + Murat + Mary minimum.
- **Tier-3 governance changes** (filing-disposition rule changes; trio template structural changes): full party-mode + operator sign-off. Lockstep with `CLAUDE.md` deferred-inventory governance section.

Owner: operator + Mary harvest-gate jointly. Refresh trigger: every 3 trials OR at every Epic-close retrospective, whichever first.

## §9 — Sample CLAUDE.md amendment (proposed; lands at S5 or S6)

To codify the filing-disposition + trigger discipline so future sessions don't reinvent:

> **Trial-postmortem governance.** Trial-run postmortems consult `docs/trials/cross-trial-learnings.md` AND file their harvest entries per the four-question routing discipline at `docs/trials/methodology.md §7`. Reactivation-trigger firings are recorded bidirectionally (inventory entry strikethrough cites cross-trial entry; cross-trial entry cites inventory entry). Cross-trial pattern synthesis fires every 3 trials OR at Epic-close. Methodology updates per `methodology.md §8` lifecycle protocol.

## References

- `_bmad-output/implementation-artifacts/trial-3-readiness-checklist.md` — Trial-3 launch playbook (folded into trial-3/launch.md as prereq section)
- `_bmad-output/implementation-artifacts/trial-2-postmortem-2026-05-04.md` — Trial-2 postmortem (template seed for Shape B structured findings)
- `docs/operator/hil-verb-legend.md` — operator verb legend (cross-linked from launch.md)
- `docs/operator/corpus-preparation-guide.md` — corpus prep guide (cross-linked from launch.md prereq)
- `_bmad-output/planning-artifacts/pre-trial-3-cleanup-plan.md §S3` — this methodology's authorship trace
- `_bmad-output/implementation-artifacts/sprint-status.yaml::tripwire_events` — tripwire ledger consulted at postmortem
