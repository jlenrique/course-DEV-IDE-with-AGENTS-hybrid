---
name: memory-guidance
description: Session close discipline for Irene — what to save where at the end of every delegation
---

# Memory Guidance

End-of-session (or end-of-pass) discipline. Run before you close out a delegation cycle.

## 1. Write a session log

Path: `_bmad/memory/bmad-agent-content-creator/sessions/YYYY-MM-DD.md`. Append a dated section if a log for today already exists.

Capture per delegation:
- **Run ID** + **module/lesson** + **content type** + **pass** (1 or 2)
- **Writers delegated to** and brief summary (one line each)
- **Revision rounds per writer** — did prose come back aligned with behavioral intent on first pass?
- **Cluster decisions** — which slides got clustered, which didn't, why (concept density, visual complexity, pedagogical weight)
- **Perception confirmations** — HIGH/MEDIUM/LOW counts; any LOW escalated to Marcus
- **Motion decisions (if motion-enabled)** — static vs video vs manual-animation; any Gate 2M overrides
- **Operator feedback** — approved as-is, modified, rejected; what they said

One screen per delegation cycle. If longer, curate.

## 2. Curate sanctum files

After the session log, decide what's durable.

| If you learned… | Update |
|-----------------|--------|
| A writer→content-type pairing that consistently works (Sophia for dialogue, Paige for protocols) | `MEMORY.md` § Writer performance |
| A cluster-decision pattern that worked (or surprised you) | `MEMORY.md` § Cluster patterns |
| A new pedagogy framing the operator favors | `BOND.md` § Operator preferences |
| A revised delegation-brief template | `CREED.md` § Standing orders (or `./references/delegation-protocol.md` if durable change) |
| A new capability the operator taught you | `CAPABILITIES.md` § Learned + `capabilities/<slug>.md` |

Do **not** copy session logs wholesale into `MEMORY.md`. Curate. Promote durable, drop ephemeral.

## 3. Grooming rules

- **Curate > accumulate.** `MEMORY.md` stays under ~200 lines.
- **Every claim links home.** Pattern entries cite the session log where they first appeared.
- **Date and decay.** Stale entries (tool retired, cluster pattern no longer relevant) either refresh or remove.
- **Ad-hoc runs do not write here.** Ad-hoc disables durable sanctum writes (`docs/ad-hoc-contract.md`). Session logs still write; sanctum curation skips.
- **Writer performance stays current.** Over time, write-delegation patterns stabilize. Re-read `BOND.md` § writer roster on session start to avoid stale trust.

## 4. What not to save

- Secrets, tokens.
- Full narration scripts or lesson plans — reference the staging path; don't paste content.
- Transcripts of writer prose — save the delegation brief + behavioral-intent verdict, not the 500 words they produced.
- Duplicated content from `./references/delegation-protocol.md` or `./references/pedagogical-framework.md`. The sanctum isn't a cache of the skill.

## 5. Pass-boundary discipline

Between Pass 1 and Pass 2, some state lives in Marcus's run bundle (approved slides, perception artifacts, motion plan). Do **not** duplicate that into `MEMORY.md`. Log what Pass 1 decided; read Pass 2 inputs fresh from the envelope.

## 6. The final check

Before you exit:
- Log written.
- Sanctum updates committed to disk.
- Any unresolved delegation or escalation flagged in `MEMORY.md` with date stamp.
- Writer-performance deltas noted in `BOND.md` (if durable) or `MEMORY.md` (if context).
- `INDEX.md` updated if you created organic files.

Then return control to Marcus with your structured outbound envelope.
