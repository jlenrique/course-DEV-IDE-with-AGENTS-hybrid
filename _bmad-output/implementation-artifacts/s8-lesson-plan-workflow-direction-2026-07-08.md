# S8 Lesson-Plan Workflow Direction - 2026-07-08

## Purpose

This artifact completes the S8 prose/workflow-direction checkpoint enough for
downstream consumers to understand what a ratified lesson plan must say after
the selection edge exists.

This is a prose/workflow checkpoint only. It must not be described as full S8
closure. The 2026-07-08 full-seat BMAD done-bar round ruled that an
"S8 complete" claim also requires an operator-named corpus plus HIL composed
proof through the local Marcus-SPOC runtime.

## Product Boundary

Target: Marcus-SPOC local runtime orchestrator.

Non-targets:

- External hosting.
- BMAD-persona Marcus proofing or concierge convenience.
- Real HAI/PHS source ingestion.
- PHS B-2 module renames.
- Operator LO-ratification UX.
- Course/SME routing completion.
- New collateral projector families.
- Batch LLM/LiteLLM token-efficiency mode.
- Trust-complete hardening from prior arcs.

## Ratified Lesson-Plan Direction

A ratified lesson plan is product instruction. It must be clear enough for the
local runtime and downstream agents to know:

- why this lesson is being produced now;
- which source posture applies;
- which collateral bundle was selected;
- which assets are ready, missing, or operator-held;
- which workflow should run next;
- what evidence downstream consumers must preserve.

The lesson plan must not treat a syllabus-only fixture as source-complete
content. It may use syllabi to describe requirements, learner profile, course
purpose, and missing-source gaps, but source-grounded content claims require
real content-bearing source references.

## Source Posture

| Posture | Example | Runtime meaning | Lesson-plan language |
| --- | --- | --- | --- |
| New-build, pending real content | HAI 510 | Course skeleton and syllabus-derived requirements are available; recorded lecture videos, slides, and readings are still pending. | "Plan around pending lecture video/slides/readings; create asset tasks and gaps, not source-grounded lesson content." |
| Enhancement of complete existing course | PHS 620 future Confluence/Canvas access | The course exists elsewhere and later ingestion should enrich or refactor existing material. | "Enhance from authorized current course content after ingestion; preserve source provenance and current-course intent." |
| Syllabus/reference-only fixture | Current HAI 510 and PHS 620 containers | Useful for course identity, objectives, requirements, and gap discovery; not a complete production source. | "Reference-only; source availability gaps remain open." |
| Operator-named composed proof corpus | S8 close proof, not yet selected here | Must exercise the local Marcus-SPOC runtime with HIL verdicts. | "Use the named corpus as runtime proof evidence; do not backfill course ingestion claims." |

## Required Prose Blocks

### Lesson-Plan Rationale

The rationale block must answer:

- what learner/job-to-be-done this lesson serves;
- what source posture applies;
- why the selected collateral bundle fits the lesson;
- which gaps prevent stronger source-grounded claims;
- what the downstream workflow must preserve.

Minimum shape:

```yaml
rationale:
  learner_need: "<plain-language need>"
  source_posture: "new_build_pending_content | enhancement_existing_course | reference_only_fixture | operator_named_runtime_proof"
  production_intent: "<why Marcus-SPOC should run this path>"
  selected_bundle_id: "<closed BUNDLE_CATALOG id>"
  component_selection:
    deck: true
    motion: true
    workbook: false
  source_limits:
    - "<gap or boundary>"
  downstream_invariants:
    - "selection resolves through BUNDLE_CATALOG"
    - "source-grounded claims require content-bearing refs"
```

### Asset-Building Task List

The asset task list must be explicit and machine-readable enough for downstream
consumers to tell whether a task is ready, blocked, operator-held, or deferred.

Minimum task record:

```yaml
asset_tasks:
  - task_id: "asset-task-001"
    kind: "lecture_video | slide_deck | reading | workbook_collateral | motion_plan | styleguide | approval"
    status: "ready_from_source | required_gap | operator_hold | deferred | validated"
    source_refs:
      - path: "<local or later-ingested source path>"
        locator: "<optional locator>"
        role: "content | requirement | reference"
    required_for:
      - "deck"
      - "motion"
    downstream_consumer: "Irene | Gary | Kira | workbook_producer | Marcus-SPOC | reviewer"
    validation_needed: "<test, HIL, checksum, or receipt>"
    gate_to_clear: "<named gate or later story>"
```

Rules:

- `ready_from_source` requires at least one content-bearing source ref.
- `required_gap` may cite a syllabus/reference requirement but must not claim
  source-grounded content.
- `operator_hold` names the decision or input needed from the operator.
- `deferred` must cite the deferred lane; it cannot silently disappear.
- Workbook tasks require valid workbook collateral, not just
  `component_selection.workbook: true`.

### Workflow Selection

Workflow selection is the bridge from ratified plan prose to the existing local
runtime component selection.

Rules:

- `LessonPlanningInputBundle.component_selection` can select production
  components only by exact match to a closed `BUNDLE_CATALOG` record.
- Default deck+motion remains the production baseline when no workbook
  collateral is ratified.
- Deck+motion+workbook is valid only when a ratified `CollateralSpec` supplies
  present workbook collateral.
- `collateral: none` is neutral when another non-workbook claim is present.
- Missing real sources produce asset tasks and gap records, not synthesized
  source-grounded lesson claims.
- Real HAI/PHS ingestion is a later authorized story, not an S8 shortcut.
- Batch/LiteLLM optimization remains deferred and cannot alter this runtime
  contract.

Minimum workflow block:

```yaml
workflow_selection:
  bundle_id: "narrated-deck-with-motion"
  resolution_path:
    - "ratified wrapper"
    - "LessonPlanningInputBundle.component_selection"
    - "BUNDLE_CATALOG exact match"
    - "ComponentSelection"
    - "local production runner"
  selected_workflow: "deck_motion"
  deferred_workflows:
    - name: "workbook"
      reason: "No ratified workbook collateral payload."
    - name: "real_hai_ingestion"
      reason: "Videos/slides/readings pending."
  live_validation_required: true
```

### Downstream-Consumer Clarity

Every ratified plan must identify the consumers and what they are allowed to
trust.

| Consumer | Consumes | Trust boundary |
| --- | --- | --- |
| Marcus-SPOC front door / runner | `ComponentSelection`, directive, run receipts | Trusts only catalog-resolved selection and runtime receipts. |
| Irene | rationale, source posture, learner objectives, scoped gaps | May reason from requirements; source-grounded prose requires content refs. |
| Gary | deck selection, styleguide resolution, source-detail instructions | Must preserve source detail; no fixture-specific shortcut. |
| Kira | motion selection and motion tasks | Runs only when motion component is selected and source/brief inputs exist. |
| Workbook producer | workbook collateral and enriched corpus | Runs only with workbook component plus valid collateral payload. |
| Reviewer/HIL | rationale, asset tasks, gate evidence | Can approve, hold, or reject; verdict becomes run evidence. |

## Checkpoint Acceptance

This prose/workflow checkpoint is acceptable when:

- the artifact states the source posture, rationale shape, asset task-list
  shape, workflow-selection rules, downstream consumers, and deferred work;
- state/context docs link to it as workflow-direction evidence, not S8 close
  proof;
- validation confirms it matches the committed selection-edge behavior;
- trigger-path audit remains clean;
- the commit message avoids "S8 complete" language.

It remains invalid to claim full S8 complete until the S8-full close conditions
below are also satisfied.

## Full S8 Acceptance

Before a lesson plan is ratified for this S8 path, the artifact must state:

- ratification status and operator/HIL authority;
- source posture and source limits;
- selected `bundle_id`;
- resolved `component_selection`;
- asset-building task list with statuses;
- downstream consumers and trust boundaries;
- explicit deferred items;
- local runtime validation command or witness requirement.

Before S8 itself can close, the run must also satisfy the canonical composed
proof bars carried from the 2026-07-06 party record:

- operator-named corpus;
- local runner environment attestation at trial start;
- per-node receipts for canonical nodes;
- gate transcript showing real operator verdicts, not scripted defaults;
- workbook citations traceable to same-run research rows when workbook is in
  scope;
- explicit side-door absence assertion;
- final BMAD party concurrence that S8, not merely this prose lane, is closed.

## Prose-Lane Validation

Current validation for this checkpoint:

- `git diff --check -- docs\STATE-OF-THE-APP.md docs\project-context.md _bmad-output\implementation-artifacts\s8-lesson-plan-workflow-direction-2026-07-08.md`
  -> pass.
- `rg` reference check confirms the state/context docs reference this artifact,
  the operator-named corpus + HIL composed proof gate, `f69ed471`,
  `narrated-deck-with-motion`, and `component_selection`.
- Runtime-evidence consistency check against local witness
  `8ace18c2-df69-49df-990a-e97404090102` -> pass:
  `trial-start.json` records `lesson_plan_collateral_bundle_id:
  narrated-deck-with-motion`; `run_summary.yaml` records
  `component_selection: {deck: true, motion: true, workbook: false}`.
- Trigger-path audit -> pass; no diffs to
  `app/marcus/lesson_plan/composition.py`,
  `app/models/state/component_selection.py`,
  `app/marcus/lesson_plan/bundle_catalog.py`,
  `app/marcus/cli/front_door.py`, or
  `state/config/pipeline-manifest.yaml`.
- BMAD prose-lane review: John `CONCUR-WITH-FINDINGS`, Winston `CONCUR`,
  Paige `CONCUR`, Murat `CONCUR-WITH-FINDINGS`; findings were limited to
  keeping this scoped as a checkpoint and recording validation evidence.

## Current Checkpoint Status

Closed or landed:

- S8 first selection-edge runtime slice: `282ea82f`.
- Planning-input selection checkpoint: `f69ed471`.

This artifact supplies the missing prose/workflow-direction contract for the
remaining lane. It is ready for review and runtime-alignment validation, but it
does not replace the operator-named corpus plus HIL composed proof required for
full S8 close.

## Shadow-Monitor Dispositions

- F-201 trigger-path watch: this prose artifact does not touch
  `app/marcus/lesson_plan/composition.py` or
  `app/models/state/component_selection.py`.
- F-202 staging hygiene: commit this artifact by explicit path only.
- F-301 uncommitted checkpoint: discharged by `f69ed471`.
- F-302 fourth-seat/substitute: discharged for the planning-input checkpoint by
  the supplemental full-seat done-bar round; still a final S8 close condition.
- F-303 HAI fixture shortcut watch: HAI remains fixture evidence for source
  posture and input-bundle behavior only; no HAI-specific production runtime
  logic is authorized.
