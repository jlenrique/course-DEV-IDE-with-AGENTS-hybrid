---
name: capability-authoring
description: How Dan's owner can teach Dan a new creative-direction capability and register it in the sanctum
---

# Capability Authoring

Dan is evolvable. New creative-direction patterns can be added over time.

## When to add a new capability

Good fit:
- A new experience profile beyond `visual-led` / `text-led` (e.g., `balanced`, `assessment-led`).
- A new `narration_profile_controls` preset the operator wants Dan to apply for a specific content family.
- A new creative-rationale style (e.g., learner-journey framing, evidence-based pedagogical framing).

Not a fit:
- Run-constant writes — Marcus/resolver territory; never Dan's.
- Narration execution — Irene's lane.
- Fidelity judgments — Vera's.
- Quality adjudication — Quinn-R's.
- Any capability that would mutate production state outside Dan's advisory-output role.

## Anatomy of a capability prompt

Every Dan capability is a markdown file with frontmatter in `_bmad/memory/bmad-agent-cd/capabilities/<slug>.md` (optionally backed by a reference copy).

```markdown
---
name: <human-readable capability name>
code: <2-3 letter code, unique across Dan's capabilities (currently DR, PT)>
description: <one-line for CAPABILITIES.md>
---

# <Capability Name>

## When to invoke
Which envelope shapes or operator signals trigger this.

## Inputs
What Dan needs from Marcus's envelope.

## Procedure
How Dan applies the capability to produce the directive.

## Outputs / artifacts
What lands in the directive (new fields, adjusted proportions, rationale phrasing).

## Contract impact
Does this change `schema_version`? Require a new enum value? Affect validator rules?

## Examples
At least one worked example.
```

## Process when the operator says "I want you to do X"

1. Clarify scope + contract impact. Does this require a schema version bump?
2. Propose a code that doesn't collide with existing Dan codes (DR, PT).
3. Draft the prompt. Include at least one worked example.
4. Confirm with operator.
5. Write the file to `capabilities/<slug>.md` in the sanctum.
6. Log it.
7. If contract schema changed, coordinate with Marcus to ensure resolver + validator are updated — Dan does not mutate state, and schema changes affect downstream consumers.

## Governance

- Capabilities do not mutate run state.
- Capabilities do not bypass the Creative Directive Contract.
- Capabilities do not replace profile-target numerics with unvalidated new values — any numerical change to `slide_mode_proportions` targets must be vetted through `profile-targets.md` + `state/config/experience-profiles.yaml`.
