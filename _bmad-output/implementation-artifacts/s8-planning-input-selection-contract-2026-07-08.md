# S8 Planning-Input Selection Contract - 2026-07-08

## Scope

This checkpoint canonicalizes the remaining S8 bridge from a ratified
lesson-planning input artifact into the already-built production selection edge:

`ratified wrapper -> LessonPlanningInputBundle.component_selection -> BUNDLE_CATALOG -> ComponentSelection -> local production runner`

It does not add a new composer, projector family, external hosting path,
concierge/proofing helper, or alternate orchestration lane.

## Inputs

The production-facing artifact is a local YAML/JSON wrapper accepted by
`trial start --lesson-plan-collateral-intent <path>` and resolved by
`app/marcus/lesson_plan/collateral_selection.py`.

Allowed ratified wrapper fields:

- `ratification_status: ratified`
- `bundle_id`: optional closed `BUNDLE_CATALOG` id
- `collateral`: optional `CollateralSpec`
- `input_bundle`: optional `LessonPlanningInputBundle`
- `source_ref`: optional local provenance reference; remote refs are refused

At least one of `bundle_id`, `collateral`, or `input_bundle` is required for a
ratified wrapper to select production components.

## Selection Rules

- Non-ratified wrappers preserve the production default and do not override
  manual/default selection.
- `input_bundle.component_selection` must match exactly one closed
  `BUNDLE_CATALOG` record. Arbitrary component maps do not select production.
- If multiple claims are present, they must select the same catalog bundle.
  Example: `bundle_id` and `input_bundle.component_selection` must agree.
- Workbook bundle selection still requires workbook collateral unless the
  ratified artifact supplies a valid `CollateralSpec` with
  `declaration: present`. This prevents a source-planning bundle from promising
  a workbook component without the lesson-plan collateral payload the workbook
  producer consumes.
- The resolved output remains the existing `ComponentSelection` model passed to
  the local production runner. No new selection schema is introduced.

## Product Boundary

This is Marcus-SPOC local runtime product work. It makes the local runtime's
component selection derivable from a ratified planning-input artifact. It is not
course-specific HAI/PHS ingestion, not a proofing-run affordance, and not an
externally hosted app surface.

## Trigger-Path Governance

The active shadow monitor carried F-201: S8 selection work must treat
`app/marcus/lesson_plan/composition.py` and
`app/models/state/component_selection.py` as trigger-path watch surfaces.

This checkpoint deliberately avoids those files. The adapter stays in
`app/marcus/lesson_plan/collateral_selection.py`, which already owns the S8
catalog-to-`ComponentSelection` resolver. The checkpoint also avoids
`app/marcus/lesson_plan/bundle_catalog.py`, `app/marcus/cli/front_door.py`, and
`state/config/pipeline-manifest.yaml`.

F-202 staging hygiene remains binding: stage explicit paths only and do not
absorb monitor ledgers, run directories, or stray evidence.

## Deferred Work Kept Out

- Real HAI 510 lecture-video/slide/readings ingestion.
- Real PHS 620 Confluence/Canvas ingestion.
- PHS B-2 module renames.
- Operator LO-ratification surface.
- Course/SME styleguide, voice, attribution, and approval routing.
- Collateral projector families beyond the existing workbook/deck/motion
  component selection.
- Batch LLM/LiteLLM token-efficiency mode.
- Trust-complete hardening from prior arcs.
- Knowledge graph / onboarding regeneration and stale tracker cleanup.

## BMAD Party Green-Light

The spawned S8 scope round converged on a thin adapter plus contract artifact:

- John: `CONCUR` - preserves product boundary; done bar is adapter, focused
  tests, contract/prose artifact, focused regression/local CLI witness, and
  explicit non-scope.
- Winston: `CONCUR` - preserves architecture boundary because the adapter stays
  inside the existing selection resolver and resolves only through the catalog.
- Amelia: `CONCUR` - implementable slice is `collateral_selection.py` only, with
  success/conflict/no-match tests and no trigger-path edits.

The first green-light attempt could not spawn the fourth test-architect seat
because the current thread hit its agent limit. That was tracked by the shadow
monitor as F-302 rather than treated as complete by implication.

A supplemental full-seat done-bar round then spawned John, Winston, Amelia, and
Murat after stale subagent slots were closed:

- John: `CONCUR-WITH-FINDINGS` - S8 may close only when this checkpoint is
  committed, the prose/workflow-direction lane is complete, live validation is
  recorded, F-301/F-302 are discharged, and no HAI/proofing shortcut enters
  production behavior.
- Winston: `CONCUR-WITH-FINDINGS` - architecture close requires exact
  `BUNDLE_CATALOG` identity semantics, preservation of the `282ea82f` edge,
  clean trigger-path governance, and real downstream consumer clarity.
- Amelia: `CONCUR-WITH-FINDINGS` - commit this checkpoint separately from the
  remaining prose lane, keep validation tied to edited components, and do not
  call S8 complete before final post-remediation concurrence.
- Murat: `CONCUR-WITH-FINDINGS` - full S8 close requires focused regression,
  live local runtime witness, prose/workflow verification, clean shadow-monitor
  dispositions, and, for an S8-full-arc claim, an operator-named corpus plus HIL
  composed proof. If that proof is deferred, only this checkpoint can close.

F-302 is therefore discharged for the planning-input checkpoint. It remains a
recorded done-bar condition for any later "S8 complete" claim.

## Code Review Gate

BMAD code-review layers ran after implementation:

- Blind Hunter:
  - Finding 1: integration test depended on generated Story D
    `input-bundle.yaml`; remediated by building the input bundle in-test from the
    committed course root + verified module-metadata proposal.
  - Finding 2: explicit workbook bundle without collateral needed an unambiguous
    regression pin; remediated with
    `test_workbook_bundle_requires_collateral_payload_even_without_collateral`.
- Edge Case Hunter:
  - Finding 1: `collateral.declaration == "none"` was treated as a positive
    deck+motion claim and could conflict with explicit deck-only selection;
    remediated so `collateral: none` is neutral when another non-workbook claim
    is present, while still preserving default behavior when it is the only
    claim.
  - Finding 2: duplicate catalog selections would resolve first-match; remediated
    by requiring exactly one matching catalog bundle and adding a monkeypatched
    duplicate-catalog regression.
- Acceptance Auditor: no findings.

Post-remediation focused validation is green.

## Final Party Close

Post-review BMAD party-mode close round:

- John: `CLOSE/CONCUR` - product boundary and validation bar satisfied; no
  product objection.
- Winston: `CLOSE/CONCUR` - architecture and trigger-path governance satisfied;
  next gate clear.
- Murat: `CLOSE/CONCUR` - testing/live-validation bar met; do not claim "S8
  complete." This is the planning-input selection contract / collateral
  selection path checkpoint, with unrelated untracked strays excluded.

## Validation Plan

Completed validation:

- Focused resolver tests:
  `.\.venv\Scripts\python.exe -m pytest tests\marcus\lesson_plan\test_collateral_selection.py -q`
  -> final post-review result: `15 passed in 8.29s`.
- S8 focused integration regression:
  `.\.venv\Scripts\python.exe -m pytest tests\marcus\lesson_plan\test_collateral_selection.py tests\integration\marcus\test_trial_cli.py tests\integration\marcus\test_front_door_selection_threading.py -q`
  -> final post-review result: `32 passed in 10.78s`; pre-commit re-run:
  `32 passed in 12.45s`.
- Ruff on touched Python files:
  `.\.venv\Scripts\python.exe -m ruff check app\marcus\lesson_plan\collateral_selection.py tests\marcus\lesson_plan\test_collateral_selection.py tests\integration\marcus\test_trial_cli.py`
  -> `All checks passed!`.
- Local CLI witness using a ratified wrapper carrying `input_bundle`, proving
  the receipt records the resolved catalog bundle and the local runner path:
  - Witness root:
    `.tmp/s8-planning-input-selection-contract`
  - Intent:
    `.tmp/s8-planning-input-selection-contract/ratified-input-bundle-intent.yaml`
  - Source bundle:
    `_bmad-output/implementation-artifacts/evidence/s7p2-story-d-input-bundles-20260708T111746/hai-510/input-bundle.yaml`
  - Final post-review command:
    `.\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input tests/fixtures/trial_corpus/README.md --operator-id operator_test --trial-id 12345678-1234-4234-8234-123456789ac1 --allow-offline-cost-report --runs-root .tmp\s8-planning-input-selection-contract\runs-final --lesson-plan-collateral-intent .tmp\s8-planning-input-selection-contract\ratified-input-bundle-intent.yaml`
  - Result: exit `0`; `trial-start.json` recorded
    `lesson_plan_collateral_bundle_id: narrated-deck-with-motion`;
    `run_summary.yaml` recorded `component_selection: {deck: true, motion: true, workbook: false}`;
    `run.json` exists.
  - Pre-commit current-state witness:
    `.\.venv\Scripts\python.exe -m app.marcus.cli trial start --preset production --input tests/fixtures/trial_corpus --operator-id operator_test --trial-id 8ace18c2-df69-49df-990a-e97404090102 --allow-offline-cost-report --auto-confirm-directive --runs-root .tmp\s8-planning-input-selection-contract\runs-close --lesson-plan-collateral-intent .tmp\s8-planning-input-selection-contract\ratified-input-bundle-intent.yaml`
  - Current-state result: exit `0`; `trial-start.json` recorded
    `lesson_plan_collateral_bundle_id: narrated-deck-with-motion`;
    `run_summary.yaml` recorded `component_selection: {deck: true, motion: true, workbook: false}`;
    `run.json` exists. The HAI bundle is fixture evidence for the generic
    `LessonPlanningInputBundle` path; no HAI-specific production resolver logic
    is introduced.
- `git diff --check` and diff-path audit proving trigger-path files remained
  untouched:
  - `git diff --check -- <checkpoint paths>` -> pass.
  - Trigger-path audit -> `trigger-path-audit=pass`; no changes to
    `app/marcus/lesson_plan/composition.py`,
    `app/models/state/component_selection.py`,
    `app/marcus/lesson_plan/bundle_catalog.py`,
    `app/marcus/cli/front_door.py`, or
    `state/config/pipeline-manifest.yaml`.
