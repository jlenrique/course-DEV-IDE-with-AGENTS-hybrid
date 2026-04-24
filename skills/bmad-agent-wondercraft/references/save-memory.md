---
name: save-memory
code: SM
description: Save session notes + curate durable learnings at session close
---

# Save Memory

## When

- At session close (Marcus-directed return, or operator exit).
- At explicit operator request ("save that", "remember this").
- After a capability invocation produces a surprising outcome worth distilling.

## How

1. Append raw session notes to `{sanctum}/sessions/{today}.md` (create file if absent).
2. Review today's session for durable patterns:
   - Voice pairings that worked (note content-type + voice combo + outcome).
   - Music bed choices that landed (mood → bed key + audience profile).
   - Cost / budget learnings (e.g., "2-minute Wondercraft dialogue runs ~0.8 credits — cheaper than expected").
   - Descript workflow preferences (operator's touch-point style).
3. Distill each into a single-line entry under the matching `MEMORY.md` section.
4. If a BOND.md field fills in (program context, voice roster, etc.), update it.
5. If PERSONA.md evolution log needs a row, add it.

## What NOT to save

- Per-episode minutiae (that's what session logs are for).
- Anything derivable from `state/config/` files (style guide, pronunciation dictionaries).
- Verbatim API responses.
