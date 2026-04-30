---
name: learning-objective-decomposition
code: LO
description: Break course/module/lesson objectives into per-asset targets; trace and flag orphans
---

# Learning Objective Decomposition (LO)

Authoritative content lives in [pedagogical-framework.md](./pedagogical-framework.md). This file registers the capability with its unique code so it surfaces in CAPABILITIES.md.

## Summary

Decomposition breaks course-level learning objectives down through module → lesson → asset. Every artifact (slide, narration segment, assessment item) traces to at least one learning objective. Orphaned artifacts get flagged to Marcus.

## When to invoke

- Pass 1 intake when the context envelope contains `learning_objectives` at module level but the lesson breakdown needs to be computed.
- Mid-Pass-1 when a slide brief is being designed and the objective-to-slide mapping needs to be explicit.

## Procedure (condensed)

1. Read `state/config/course_context.yaml` for the module/lesson objective hierarchy.
2. For each lesson objective, identify the content artifact(s) that will satisfy it.
3. For each artifact, annotate the target objective(s) in the output template.
4. Flag any content element that doesn't trace to an objective — these must be cut or justified.

See [pedagogical-framework.md](./pedagogical-framework.md) for the full framework and [template-lesson-plan.md](./template-lesson-plan.md) for the output annotation structure.
