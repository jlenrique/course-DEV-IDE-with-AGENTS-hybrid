---
name: degradation-handling
description: Irene's exception-handling playbook for delegation failures, scope issues, and missing context
---

# Degradation Handling

When delegation or assembly encounters problems, Irene reports to Marcus with clear status and alternatives — she does not silently proceed, improvise, or absorb the degradation.

## Writer returns misaligned prose

- Provide specific pedagogical feedback tied to the behavioral intent from the delegation brief.
- Re-delegate (max **2 revision rounds per piece**).
- If still misaligned after 2 rounds, escalate to Marcus with the misalignment details and suggest an alternative writer or direct user input.
- Log the misalignment + resolution in the session log so writer-routing learnings accumulate in `MEMORY.md`.

## Missing learning objectives

- If the context envelope lacks learning objectives for the requested module/lesson, request clarification from Marcus before designing.
- **Never invent learning objectives.** If Marcus forwards operator input, validate it against the Bloom's taxonomy + cognitive load framework before proceeding.

## Content scope exceeds cognitive load guidelines

- Flag to Marcus: "This lesson covers 15 distinct concepts — recommend splitting into 2-3 sub-lessons for cognitive load management. Proceed as-is, or should I propose a split?"
- Do not silently compress or cut. Present options with pedagogical rationale.

## No course context available

- If `state/config/course_context.yaml` doesn't have the requested module/lesson mapped, offer to work from user-provided objectives or request Marcus obtain them.
- Do not invent module/lesson metadata.

## Perception contract escalation

- If `perception_contract.py::enforce_perception_contract` returns persistent LOW after retry, escalate to Marcus, not the operator. Marcus decides whether to proceed or halt the run.
- Never write narration against LOW-confidence perception without explicit Marcus authorization.

## Motion contract failures (Epic 14)

- If `motion_plan.yaml` references unknown slide IDs or incomplete non-static assignments, fail closed and return a scope violation to Marcus.
- Do not silently downgrade a non-static segment to static.

## Governance scope violation

- Any requested work outside `governance.allowed_outputs` or `governance.decision_scope.owned_dimensions` returns a `scope_violation` object to Marcus with:
  ```
  {detected, reason, requested_work, route_to: governance.authority_chain[0], details}
  ```
- Do not produce the out-of-scope portion. Return only the in-scope artifacts plus the violation notice.

## Delegation envelope malformed

- If the context envelope is missing `production_run_id`, `content_type`, `module_lesson`, `learning_objectives`, or the `governance` block, return `status: failed` with the missing-fields list. Do not proceed.

## Style-bible or tool-inventory unavailable

- Re-read attempts: try path twice with clear error handling.
- If still unreadable, escalate to Marcus with the specific path and error. Do not proceed with stale cached content (Irene does not cache these).
