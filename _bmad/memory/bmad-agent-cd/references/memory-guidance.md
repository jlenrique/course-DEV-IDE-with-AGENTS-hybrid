---
name: memory-guidance
description: Session close discipline for Dan — what to save where at the end of every directive cycle
---

# Memory Guidance

End-of-directive discipline. Run before you close out.

## 1. Write a session log

Path: `_bmad/memory/bmad-agent-cd/sessions/YYYY-MM-DD.md`. Append a dated section if today already has a log.

Capture per directive:
- **Run ID** + **module/lesson** + **requested experience profile** (if explicit) + **resolved profile**
- **slide_mode_proportions** produced
- **narration_profile_controls** notable deltas from defaults
- **creative_rationale** — one-line summary of the framing reasoning
- **Operator feedback** (if relayed via Marcus) — approved, modified, or rejected the directive
- **Contract validator result** — pass/fail, any edits required

One screen per directive. If longer, curate.

## 2. Curate sanctum files

After the session log, decide what's durable.

| If you learned… | Update |
|-----------------|--------|
| A profile tuning that consistently worked for a content type | `MEMORY.md` § Profile tuning patterns |
| A narration-profile-control preference the operator has stabilized on | `BOND.md` § Operator preferences |
| A new creative-directive shape the operator favors | `CREED.md` § Standing orders |
| A new capability (e.g., a third experience profile beyond visual-led/text-led) | `CAPABILITIES.md` § Learned |
| A shift in how you phrase creative rationale | `PERSONA.md` |

Do not copy the session log wholesale into `MEMORY.md`. Curate.

## 3. Grooming rules

- **Curate > accumulate.** `MEMORY.md` stays under ~200 lines.
- **Every claim links home.** Pattern entries cite the session log.
- **Date and decay.** Stale entries get refreshed or removed.
- **Ad-hoc runs do not write here.** Ad-hoc disables durable sanctum writes. Session logs still write; sanctum curation skips.
- **Contract version matters.** Every profile-target or directive-shape pattern cites the `schema_version` it was produced against.

## 4. What not to save

- Secrets, tokens.
- Full directive YAML bodies — reference the run ID; directive itself lives in the run bundle.
- Transcripts of operator conversation — keep decisions and rationale, drop dialogue.
- Duplicated content from `./references/creative-directive-contract.md` or `./references/profile-targets.md`. The sanctum isn't a cache of the skill.

## 5. The final check

Before you exit:
- Log written.
- Sanctum updates committed to disk.
- Any unresolved profile question flagged in `MEMORY.md` with date stamp.
- Any operator-preference shift noted in `BOND.md`.
- `INDEX.md` updated if organic files added.

Return control to Marcus.
