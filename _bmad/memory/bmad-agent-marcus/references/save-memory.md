---
name: save-memory
code: SM
description: Immediate session-context persistence to the Marcus sanctum
---

# Save Memory

Immediately persist the current session context to the sanctum at `{project-root}/_bmad/memory/bmad-agent-marcus/`.

## Process

Update `index.md` with current session context: active production run, progress state, outstanding tasks, user preferences, and next steps. Checkpoint `patterns.md` and `chronology.md` if significant changes occurred during this session.

**Mode-aware:** In ad-hoc mode, only update the transient ad-hoc session section of `index.md`. Do not write to `patterns.md` or `chronology.md`.

## Output

Confirm save with brief summary: "Memory saved. [brief summary of what was updated]"
