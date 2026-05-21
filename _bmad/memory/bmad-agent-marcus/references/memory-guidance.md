---
name: memory-guidance
description: Session close discipline for Marcus — what to save where at the end of every session
---

# Memory Guidance

End-of-session discipline. Run before you close out.

## 1. Write a session log

Path: `_bmad/memory/bmad-agent-marcus/sessions/YYYY-MM-DD.md`. If a log already exists for today, append a new dated section rather than overwriting.

Capture:
- **Run ID** (if an active tracked run).
- **Phase / gate** you advanced through or halted at.
- **Delegations issued** — who you routed to, what inputs, outcome.
- **HIL gate decisions** — what the operator approved, modified, or rejected; rationale if given.
- **Exceptions** — anything that surprised you or needed judgment beyond the runbook.
- **Open questions** — things the operator didn't resolve that future sessions need to surface.

One screen max. If it's longer, the next step is curating it, not keeping all of it.

## 2. Curate sanctum files

After the session log exists, decide what's durable.

| If you learned… | Update |
|-----------------|--------|
| A new pattern worth reusing (e.g., "operator prefers storyboard before Gate 2M for motion runs") | `MEMORY.md` |
| A new routing / delegation protocol | `CREED.md` (standing orders) |
| A shift in operator preference, accessibility constraint, or voice rule | `BOND.md` |
| A new capability the operator taught you | `CAPABILITIES.md` (`Learned` section) + `capabilities/<slug>.md` with the full prompt |
| A correction to your voice, tone, or default framing | `PERSONA.md` |

Do **not** copy the session log into `MEMORY.md` wholesale. Curate — pull the durable lessons; leave the event log where it is.

## 3. Grooming rules

- **Curate > accumulate.** If `MEMORY.md` exceeds ~200 lines, it's time to condense: merge duplicates, drop stale items, promote recurring patterns into `CREED.md`.
- **Every claim links home.** When `MEMORY.md` cites a pattern, link the session log where it first appeared so the provenance is inspectable.
- **Stale items decay.** Date every `MEMORY.md` entry. When a dated entry's subject has changed upstream (new epic, new prompt pack version, new agent), either refresh or remove the entry.
- **Ad-hoc runs do not write here.** Ad-hoc mode disables durable sanctum writes by contract (`docs/ad-hoc-contract.md`). Session logs still write; sanctum curation skips.

## 4. What not to save

- Secrets, tokens, API keys — never. Refer by name ("ELEVENLABS_API_KEY is in .env") not value.
- Full artifact content (PDFs, PNGs, MP4s) — reference by path; the content lives in the bundle.
- Transcripts of operator conversation — keep the decisions + rationale, drop the dialogue.
- Duplicated content from SKILL.md or reference files — the sanctum isn't a cache of the skill.

## 5. The final check

Before you exit:
- Log written.
- Sanctum updates committed to disk (not deferred to "later").
- Any unresolved operator question flagged in `MEMORY.md` with a date stamp.
- Any experiment or exception that might affect the next run noted in `BOND.md` (if operator-preference) or `MEMORY.md` (if context).
- `INDEX.md` updated if you added any organic files to the sanctum.

Then say goodnight.
