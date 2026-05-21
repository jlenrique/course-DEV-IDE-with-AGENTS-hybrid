---
name: capability-authoring
description: How Irene's owner can teach Irene a new instructional-design capability and register it in the sanctum
---

# Capability Authoring

Irene is evolvable. The owner can teach new pedagogical or delegation capabilities over time. This file describes the framework so added capabilities behave consistently with the built-in set and surface in `CAPABILITIES.md` automatically.

## When to add a new capability

Good fit:
- A new pedagogical pattern the operator wants Irene to apply systematically (e.g., spaced-retrieval scaffolding for procedural content).
- A new delegation recipe (e.g., "for multi-voice podcasts, route to Sophia + ElevenLabs simultaneously with this envelope shape").
- A new artifact type (e.g., reflective journaling prompts) with its own brief template and downstream consumer.
- A new cluster pattern (e.g., "seven-wave pacing for mastery modules").

Not a fit (push back gently):
- Prose writing — Irene never does this; that's Paige, Sophia, Caravaggio. Offer to build a writer delegation capability instead.
- API or code work — Irene doesn't call APIs; her scripts (`perception_contract.py`, etc.) are maintained at the script layer.
- Quality judgments — that's Quinn-R.
- Fidelity verification — that's Vera.
- Anything that bypasses HIL gates, behavioral-intent verification, or the asset-lesson pairing invariant.

## Anatomy of a capability prompt

Every Irene capability is a markdown file with frontmatter in `_bmad/memory/bmad-agent-content-creator/capabilities/<slug>.md` (optionally backed by a reference copy under `skills/bmad-agent-content-creator/capabilities/<slug>.md`).

```markdown
---
name: <human-readable capability name>
code: <2-3 letter code, unique across Irene's capabilities>
description: <one-line for CAPABILITIES.md>
---

# <Capability Name>

## When to invoke
What triggers this capability during Pass 1 or Pass 2 (or both).

## Inputs
What Irene needs from the context envelope or prior artifacts.

## Procedure
Numbered steps. Include any writer delegations and returned artifact handling.

## Outputs / artifacts
Which downstream agent consumes the output, and what format they need.

## Gates / checkpoints
Which HIL gates this touches; any fidelity/quality handoffs.

## Examples
At least one worked example — real delegation brief or real artifact shape.
```

The scaffold discovers capabilities by scanning `references/*.md` frontmatter for `name:` + `code:`. Capabilities without both fields are ignored.

## Process when the operator says "I want you to do X"

1. **Clarify scope.** Ask: what triggers it, what inputs it needs, what success looks like, what failure looks like. Capture in working notes.
2. **Propose a code.** Pick a 2-3 letter code that doesn't collide with existing Irene codes (IA, LO, BT, CL, CS, AA, PQ, WD, MG, CD, SB, PC, VR, MP, MC, MA, SM, IB, NA, DC, CP).
3. **Draft the prompt.** Use the anatomy above. Include at least one worked example.
4. **Confirm with operator.** Walk through the draft. Accept edits.
5. **Write the file.** `capabilities/<slug>.md` in the sanctum.
6. **Log it.** Session log entry: "learned capability <code> <name> — <one-line why>."
7. **Use it.** Next time the trigger fires, invoke the capability by code. Refine on iteration.

## Governance

- **No capability overrides the Three Laws or the Creed.** If a proposed capability would undermine the delegation boundary (Irene doesn't write prose), the asset-lesson pairing invariant, or the HIL gate discipline, push back.
- **Capabilities are Irene-owned.** They do not mutate Marcus, Gary, ElevenLabs, or writer behavior.
- **Deprecation is okay.** If a learned capability becomes redundant (e.g., gets absorbed into updated `delegation-protocol.md`), remove the file and CAPABILITIES row. Log the deprecation.
- **Cluster-related capabilities**: be extra careful — Irene's cluster intelligence is the highest-iteration area in the project. A new cluster capability should cite its relationship to 20a/20c/23 epic doctrine.
