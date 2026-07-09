---
title: 'Planning-context → Irene Pass-1 handoff (purpose/audience/LOs/source assessment)'
type: 'feature'
created: '2026-07-09'
status: 'backlog-next'
story_key: 'planning-context-to-irene-pass1-handoff'
gate_mode: 'dual-gate'
baseline_commit: '20246475'
context:
  - '{project-root}/_bmad-output/planning-artifacts/lesson-plan-rationale-platform-positioning-2026-07-07.md'
  - '{project-root}/_bmad-output/implementation-artifacts/phase2-evolutionary-claim-envelope-2026-07-09.md'
  - '{project-root}/_bmad-output/implementation-artifacts/phase2-evolutionary-planning-to-selection-bridge.md'
  - '{project-root}/_bmad-output/planning-artifacts/deferred-inventory.md'
---

<!-- PARKED backlog-next (2026-07-09). Do NOT start until Phase-2 bridge
     step-1 closeout is fully banked and the operator opens this story.
     Draft only — party green-light not yet binding for implementation. -->

<!-- Operator-directed next evolutionary glue after Phase-2 bridge PARTIAL-MET
     (`20246475`). Step 2→3: elicited/ingested planning context must reach
     Irene Pass-1 as structured inputs, then flow downstream via existing
     lesson_plan / run.json consumers. Canonical evolution rule §4.1 applies.
     Party green-light required before code; consensus + orchestrator = approval. -->

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Purpose, audience, LOs, and source assessment can be elicited/recorded (G0R `ratified-los.json`, Phase-2 `planning-ratification.json`, course-source bundles), but Irene Pass-1 still plans almost exclusively from `extracted.md`. Structured planning context does not reach Irene; `ratified-los.json` is largely orphaned; Phase-2 ratification stops at `ComponentSelection`.

**Approach:** Thread an optional structured **`planning_context`** into Irene Pass-1 (runner context + prompt section). Prefer operator-ratified / Phase-2 companion + G0R LOs when present. Corpus remains the topic/source-of-truth for content; planning context governs purpose, audience, LO framing, and gap awareness. Downstream continues to consume Irene’s `lesson_plan` via existing `run.json` / package-builder paths — no parallel selection engine.

**Claim fence:** Does not claim interactive SPOC planning REPL, full lecture ingestion, SME routing, projector family, or W5 compose. Does not redesign S8 resolver. Does not replace corpus grounding with planning-context-only planning.

## Boundaries & Constraints

**Always:**
- Marcus-SPOC product path only.
- Additive optional payload key; absent context = today’s behavior (backward compatible).
- Corpus (`extracted.md`) remains the ONLY topic/source planning basis; planning context is framing, not a second corpus.
- Prefer reading existing on-disk artifacts: `planning-ratification.json` (purpose/audience/assessment/gaps) and/or `ratified-los.json` (G0R LOs).
- When context is present, Irene prompt includes an explicit structured section; plan emission should reflect LO/purpose/audience framing (testable).
- Downstream proof = existing consumers still read `lesson_plan` from envelope (compatibility pin); optional assert that plan units cite/align with provided LOs when context present.
- Dual-gate; live-test as built; shadow-monitor for this handoff.
- Styleguide registry: never ad-hoc-edit approved guides.

**Ask First:**
- Changing Irene Pass-1 JSON emission schema beyond using existing `learning_objective` fields.
- Making planning_context mandatory (breaking absent path).
- Injecting full `LessonPlanningInputBundle` into Irene (too wide this slice).

**Never:**
- Parallel selection engine; S8 reopen; planning-context-only plans that ignore corpus.
- Silent drop of provided LOs when context is present (fail loud or explicit degrade receipt).
- Interactive REPL buildout in this story.

## I/O & Edge-Case Matrix

| Scenario | Input | Expected | Error |
|----------|-------|----------|-------|
| No planning artifacts | Normal trial | Irene unchanged vs baseline | N/A |
| `planning-ratification.json` in run_dir | purpose/audience/assessment | Runner threads `planning_context`; prompt section present | Malformed JSON fail loud |
| `ratified-los.json` only | G0R LOs | Context carries LOs; purpose/audience may be empty/optional | Empty LO list = treat as absent LOs |
| Both present | Companion + G0R LOs | Merge: purpose/audience/assessment from companion; LOs prefer G0R when non-empty else companion | Conflict policy: G0R LOs win for LO list |
| Context present | Pass-1 act | Plan units’ learning objectives align with provided LO set (non-vacuous overlap / coverage receipt) | If model ignores, fail-loud verify or explicit degrade — party picks at green-light |
| Overclaim in purpose | Affirmative full-lecture claim | Reject or strip via existing overclaim guard | Fail loud |

</frozen-after-approval>

## T1 Readiness

- [x] Prior bridge PARTIAL-MET at `20246475`
- [x] Seam map: `irene_pass1/payload_contract.py`, `_act.assemble_pass1_prompt`, `production_runner._runner_payload_for_specialist`, `ratified-los.json`, `planning_ratification.write_ratification_artifacts`
- [x] Dual-gate designated
- [ ] Party green-light this story
- [ ] Shadow-monitor ledger for handoff arc

## Code Map (target)

| Area | Path | Role |
|------|------|------|
| Context model + loader | `app/marcus/lesson_plan/planning_context.py` (NEW) | Load/merge planning-ratification + ratified-los → `PlanningContext` |
| Runner thread | `app/marcus/orchestrator/production_runner.py` `_runner_payload_for_specialist` | Add `planning_context` for irene_pass1 when loadable |
| Trial copy (thin) | `app/marcus/cli/trial.py` | If companion path known / sits beside intent, ensure available under run_dir |
| Irene contract | `app/specialists/irene_pass1/payload_contract.py` | Add `planning_context` to consumed keys |
| Irene prompt | `app/specialists/irene_pass1/_act.py` | Structured planning-context section; corpus still primary |
| Tests | `tests/marcus/lesson_plan/test_planning_context.py`, `tests/specialists/irene_pass1/...` | RED-first absent/present/merge/prompt |

## Tasks & Acceptance

### AC-H1 — Optional PlanningContext loader
Load from run_dir artifacts; merge rules as matrix; malformed fail loud; absent → None.

### AC-H2 — Runner threads to Irene Pass-1
When context loadable, `_runner_payload_for_specialist` includes `planning_context` for irene_pass1 only.

### AC-H3 — Prompt surfaces structured context
`assemble_pass1_prompt` includes purpose/audience/LOs/gap summary when present; corpus section remains the ONLY topic basis.

### AC-H4 — Backward compatible absent path
No artifacts → byte-stable behavior vs pre-story for prompt corpus path (no required context section).

### AC-H5 — Downstream continuity pin
Existing package_builder / lesson_plan-from-run paths still resolve `lesson_plan` from envelope (compatibility test).

### AC-H6 — Claim fence
Story/evidence state: does not claim REPL, full lecture ingestion, or S8 redesign.

## Dev Notes

- Keep planning_context as runner context (chartered like `min_cluster_floor`), not a fake dependency projection of corpus content.
- Prefer small JSON-serializable dict in payload for prompt dump.
- Party must pick LO-alignment verify strength (soft receipt vs fail-loud) at green-light — default proposal: **soft coverage receipt on plan output** this slice; fail-loud only if context present and plan has zero LOs / empty plan_units.

## Definition of Done

- AC-H1..H6 green; dual-gate party close; shadow-monitor dispositioned; inventory `course-purpose-and-operator-owned-lo-inputs` updated (partial or MET for Pass-1 signature slice); STATE/project-context next-frontier updated; commit+push.
