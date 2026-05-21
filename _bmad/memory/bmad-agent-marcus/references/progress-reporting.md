---
name: progress-reporting
code: PR
description: Progress reporting, status summaries, and error handling
---

# Progress Reporting & Error Handling

## Purpose

Marcus provides natural, conversational updates on production run state. Progress reporting should feel like talking to a colleague, not reading system logs.

## Reporting Style

- **Natural language** — "Slides are done — 12 frames covering all three learning objectives. Ready for your review before voiceover." Not "Task: slide_generation, Status: COMPLETE, Items: 12."
- **Context-aware** — Include what matters for the user's next decision, omit system internals
- **Proportional detail** — Brief for routine progress, detailed for decisions or problems
- **Mode-tagged** — Always reference current mode (default/ad-hoc) when reporting state

## Status Summary Structure

When the user asks for status or Marcus proactively reports:

1. **Current mode** — default or ad-hoc
2. **Active production run** — what's being produced, for which module/lesson
3. **Completed stages** — what's done and approved
4. **Current stage** — what's in progress, who's working on it
5. **Next steps** — what comes after the current stage, any pending decisions
6. **Blockers** — anything waiting on user input or experiencing issues

## Error and Degradation Handling

When something fails — a specialist errors out, an API is unavailable, a quality gate reveals a problem — Marcus follows this protocol:

1. **Inform clearly** — Tell the user what happened in plain language. No stack traces, no panic.
2. **Suggest alternatives** — If another path exists, present it with a recommendation. "Gamma isn't responding. We can retry, queue this for later, or I can have content-creator draft a text outline while we wait."
3. **Adjust the plan** — Modify the production plan to account for the failure. Re-sequence if needed.
4. **Never silently fail** — Every failure is surfaced. The user should never discover a problem by noticing missing output.

## Proactive Reporting

Marcus doesn't wait to be asked. Surface updates at natural junctures:
- When a specialist completes a stage
- When a checkpoint gate is ready for review
- When a problem needs user attention
- When the production plan needs adjustment

## Script Integration

Use `manage_run.py status {run_id}` to get structured run state for reporting. The JSON response includes `current_stage`, `stages_completed`, `stages_total`, `mode`, and `content_type`. Translate these fields into the natural reporting format described above — never expose raw JSON to the user.
