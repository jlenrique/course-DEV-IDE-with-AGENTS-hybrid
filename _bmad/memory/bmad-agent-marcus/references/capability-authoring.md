---
name: capability-authoring
description: How Marcus's owner can teach Marcus a new capability and register it in the sanctum
---

# Capability Authoring

Marcus is evolvable. The owner can teach new capabilities over time. This file describes the framework so that added capabilities behave consistently with the built-in set and show up in CAPABILITIES.md automatically.

## When to add a new capability

Good fit:
- A recurring operational pattern the owner wants Marcus to handle without re-explaining.
- A new orchestration route (e.g., "when X condition, delegate to Y specialist with Z envelope").
- A new HIL gate style or review sequence (e.g., "introduce a motion sanity check between Gate 2 and Gate 2M").

Not a fit (push back gently):
- Code or API work — Marcus does not do those directly. If the capability requires code, the capability is for a **specialist**, not for Marcus. Offer to file it against the right specialist agent instead.
- Authorship (writing prose, generating slides, rendering video) — belongs to Irene, Gary, Kira, etc. Marcus orchestrates, does not author.
- Anything that would bypass a quality gate — Marcus's job is to uphold gates, not automate their skipping.

## Anatomy of a capability prompt

Every Marcus capability is a markdown file with frontmatter in `_bmad/memory/bmad-agent-marcus/capabilities/<slug>.md` (and a reference copy in `skills/bmad-agent-marcus/capabilities/<slug>.md` if you want it to survive re-scaffolding).

```markdown
---
name: <human-readable capability name>
code: <2-3 letter code, e.g. PR, HC, MM>
description: <one-line description used in CAPABILITIES.md table>
---

# <Capability Name>

## When to invoke
Describe the situation that triggers this capability.

## Inputs
What Marcus needs to have or ask for before executing.

## Procedure
Numbered steps. Include any delegation targets and envelope shape.

## Outputs / artifacts
What gets produced and where it's written.

## Gates / checkpoints
Which HIL gates this passes through or generates.

## Examples
At least one worked example from a real run.
```

The scaffold discovers capabilities by scanning references (and, by convention, `capabilities/`) for `name:` + `code:` frontmatter. Capabilities without both fields are ignored.

## Process when the owner says "I want you to do X"

1. **Clarify scope.** Ask the owner what triggers it, what inputs it needs, what success looks like, what failure looks like. Capture in working notes.
2. **Propose a code.** Pick a 2-3 letter code that doesn't collide. Current built-ins: CM, PR, HC, MM, SP, SM, SB. Avoid overloading.
3. **Draft the prompt.** Use the anatomy above. Keep it actionable; no hedging language.
4. **Confirm with the owner.** Walk them through the draft. Accept edits.
5. **Write the file.** `capabilities/<slug>.md` in the sanctum. Re-run the scaffold's capability scan (or wait until next session — scaffolding auto-discovers on First Breath; mid-session, update `CAPABILITIES.md` manually with the new row).
6. **Log it.** Session log entry: "learned capability <code> <name> — <one-line why>."
7. **Use it.** Next time the trigger fires, invoke the capability by name or code. Confirm with the owner that it did what they wanted. Refine on the next iteration.

## Governance

- **No capability overrides the Three Laws or the Creed.** If a proposed capability would violate fidelity gates, the asset-lesson pairing invariant, or the execution-mode boundary, push back.
- **Capabilities are Marcus-owned.** They do not mutate other agents' behavior. If the new capability requires a behavior change in Texas or Irene, file the change against that agent instead.
- **Deprecation is okay.** If a learned capability turns out to be flawed or redundant, remove the file and remove the CAPABILITIES.md row. Log the deprecation in the session log.
