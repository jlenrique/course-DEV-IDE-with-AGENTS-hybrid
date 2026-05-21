# Migration Story 6.5: HUD per-step expandable summaries surface real-time captured and locked content

**Status:** review
**Sprint key:** `migration-6-5-hud-per-step-expandable-summaries`
**Epic:** Slab 6 - Post-MVP Production Capability (`migration-epic-6-post-mvp-production`)
**Pts:** ~4
**Gate:** single-gate (HUD operator-experience enhancement; no schema-shape risk; no runtime substrate change)
**K-target:** ~1.4x (target 20 / floor 15 — bumped 2026-04-28 per party-mode M-R3 NON-BLOCKING to accommodate 33-step parametrize expansion + pack-version-mismatch case)
**Authored:** 2026-04-28 via `bmad-create-story` workflow from the Slab 6 trial-experience bundle seed.

## Governance

This story completed Gate 1 operator-run `bmad-party-mode` green-light with Winston, Murat, Paige, and Amelia on 2026-04-28. Gate 2 implementation is complete and the story is in `review`; Gate 3 `bmad-code-review`, Gate 4 triage, and Gate 6 close remain future work.

Binding readings completed at authoring T1:
- `_bmad-output/implementation-artifacts/codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md`
- `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md`
- `docs/dev-guide/composition-specification.md` Sections 3 and 11
- `docs/dev-guide/substrate-inventory-checklist.md`
- `docs/dev-guide/specialist-anti-patterns.md`
- `docs/dev-guide/pipeline-manifest-regime.md`
- `_bmad-output/implementation-artifacts/codex-handoff-pre-trial-adhoc-and-hud-batch-dev.md`
- `scripts/utilities/run_hud.py`
- `scripts/utilities/pipeline_manifest.py`
- `docs/operator/hud-guide.md`
- `state/config/pipeline-manifest.yaml`
- `tests/test_run_hud.py`

## Party-mode green-light (BINDING; ratified 2026-04-28 in --solo mode)

- Convened: Winston + Murat + Paige + Amelia (4-voice panel per discipline doc §5)
- Verdict: unanimous GREEN-WITH-RIDERS — no architectural impasse; no §11 migration trigger fire
- Direction ratified: existing-artifact derivation (NOT new emitters); `<details>` + sessionStorage interaction; pull-based `--watch` refresh
- 7 BINDING riders applied to spec; 4 NON-BLOCKING apply at code-review or close

**BINDING riders:**
- **W-R1:** Per-step summary derivation must be O(N) over manifest steps. Bundle artifact scan happens ONCE per HUD render, not per-step. Memoize artifact lookups by step id within a single render pass.
- **M-R1:** Add `test_per_step_summary_handles_pack_version_mismatch` — artifact locked at older pack-version; summary renders with explicit `[pack version mismatch]` annotation; does NOT crash or silently misrepresent.
- **M-R2:** AC-A test pin parametrizes across ALL 33 hud_tracked steps; per-step derivation function existence pinned individually; missing-derivation auto-FAIL.
- **P-R1:** Define summary-template style guide IN SPEC: sentence length cap (~30 words); terminology consistency ("locked" not "frozen"; "artifact" not "file"); missing-data wording standard ("no locked artifact yet" verbatim per AC-B). Tests assert per-step summary compliance.
- **P-R2:** Update `docs/operator/hud-guide.md` with new section: expand/collapse semantics + sessionStorage behavior + warning/blocker auto-expand; operator can disable auto-expand if desired.
- **A-R1:** Per-step derivation functions MUST be PURE (no side effects, no IO outside reading artifact bytes; no logging from derivation function). Side effects + IO live at calling layer.
- **A-R2:** Phase 1 pre-flight — enumerate all 33 hud_tracked steps; identify which have known artifact-derivation source vs which fall to "no locked artifact yet" path. Surface as decision_needed if more than 5 steps have NO known artifact path (suggests scope deferral or new-emitter discussion).

**NON-BLOCKING riders (apply at code-review or close):**
- **W-R2:** If derivation surfaces unanticipated need for new artifact emitters, HALT-and-surface; file as deferred follow-on.
- **M-R3:** K-target 18 → 20; floor 13 → 15 to accommodate parametrize expansion + pack-version-mismatch case.
- **P-R3:** Add screenshots or mock layouts to `docs/operator/hud-guide.md` showing expanded vs collapsed per-step summary.
- **A-R3:** Effort estimate add ~0.5 day for HUD integration test surface (existing `tests/test_run_hud.py` extension).

## T1 Readiness Block

Predecessor state:
- Slab 6.2 is closed.
- Batch 3 HUD modernization is in `review`; live code already has migrated-runtime panels and `--watch`.
- `docs/dev-guide/migration-story-governance.json` already pins 6-5 as single-gate.

Live substrate:
- HUD implementation is `scripts/utilities/run_hud.py`, not `scripts/run_hud.py`.
- HUD step list is manifest-sourced through `scripts.utilities.pipeline_manifest.hud_steps(load_manifest())`.
- Current per-step rendering already supports gate summaries, metrics, conditions, blockers, evidence, and outputs from gate sidecars.
- Bundle artifact scan exists but is generic; it does not derive human-readable per-step summaries from locked artifacts.
- The live manifest has 33 HUD-tracked steps, not the seed's approximate 14 step types.
- `scripts/utilities/run_hud.py` and `tests/test_run_hud.py` are block-mode trigger paths; implementation must run the pipeline lockstep check.

T1 conclusion:
- No unanticipated architectural disagreement requires halting Gate 0.
- This story should derive summaries from existing artifacts first. New per-step emitters would expand pipeline runtime scope and should be deferred unless party-mode explicitly re-scopes.

## TEMPLATE Scope Decisions

Proposed default for Gate 1 ratification:
- Add a pure summary-derivation module for bundle artifacts.
- Render a `<details>` section inside each HUD step, closed by default except the current step and steps with warnings/blockers.
- Preserve `--watch` as pull-based regeneration. No push/event bus.
- Persist expand/collapse state in browser `sessionStorage`, consistent with existing HUD state preservation.
- Cover all manifest `hud_tracked` steps, with specific summaries where known artifacts exist and an honest "no locked artifact yet" message otherwise.

Out of scope:
- No production runner changes.
- No new per-step artifact emitters in this story.
- No manifest topology change.
- No redesign of HUD layout beyond per-step expandable summary content.
- No WebSocket, LangSmith webhook, or Postgres LISTEN/NOTIFY push path.

Decision-needed for party-mode:
- Ratify existing-artifact derivation as the default source.
- Ratify `<details>` + sessionStorage interaction model.
- Ratify pull-on-HUD-refresh cadence for live updates.

## Story

As an operator watching a production trial in the HUD,
I want every pipeline step to expose an expandable summary of the content captured and locked at that step,
so that I can inspect completed work without leaving the HUD or opening bundle files manually.

## Acceptance Criteria

### AC-6.5-A - Per-step summary derivation from existing artifacts

Given an active or selected bundle,
when HUD data is collected,
then each manifest `hud_tracked` step receives a summary object derived from existing bundle artifacts where available.

Examples:
- Step 01: preflight receipt / run constants
- Step 02: source authority map / source quality evidence
- Step 02A: operator directives
- Step 03: extraction report / ingestion evidence
- Step 04: ingestion quality receipt / Irene packet
- Step 08: narration script / segment manifest / perception artifacts
- Step 09: locked Pass 2 package status

Test pin: `tests/unit/hud/test_per_step_summary_derivation.py`.

### AC-6.5-B - Honest degradation when artifacts are absent

Given a step has no recognizable locked artifact yet,
when the HUD renders,
then the expandable summary says no locked artifact is available yet and does not fabricate content from neighboring steps.

Test pin: missing-artifact cases for representative early, middle, and late steps.

### AC-6.5-C - Expandable rendering inside each step

Given per-step summaries exist,
when `render_html(...)` runs,
then each pipeline step renders an accessible expandable details block containing summary title, artifact source, captured fields, and freshness timestamp where available.

Test pin: `tests/integration/hud/test_per_step_summary_rendering.py`.

### AC-6.5-D - Current step and warning states are inspection-friendly

Given the operator is watching the HUD during a run,
when a step is current or has blockers/warnings,
then its summary details block is open by default. Other completed steps are collapsed by default but can be expanded.

Test pin: HTML render assertions for current, blocker, and ordinary completed states.

### AC-6.5-E - Expand/collapse survives refresh

Given the HUD uses browser refresh and optional `--watch`,
when the operator expands or collapses a step,
then the state persists through refresh using existing sessionStorage patterns.

Test pin: render includes stable per-step details IDs and sessionStorage JS hooks.

### AC-6.5-F - Manifest naming alignment

Given the pipeline manifest is the source of truth,
when summary derivation maps artifacts to steps,
then it keys by manifest step ID and label, not hand-maintained parallel step names.

Test pin: no hardcoded full step-list literal in the summary module; parametrized test over `hud_steps(load_manifest())`.

### AC-6.5-G - Pipeline lockstep regime honored

Given this story touches `scripts/utilities/run_hud.py` and `tests/test_run_hud.py`,
when implementation closes,
then `python scripts/utilities/check_pipeline_manifest_lockstep.py` exits 0 and any generated pack changes, if any, flow through the generator. No hand-edited pack changes are expected.

### AC-6.5-H - Operator documentation updated

Given the HUD guide already documents panels and watch mode,
when per-step summaries land,
then `docs/operator/hud-guide.md` documents what the expandable summaries show, how refresh works, and why absent summaries are honest no-artifact states.

### AC-6.5-I - N-item and anti-pattern trace

The implementation must record:
- N4 PASS: HUD changes do not affect runtime execution or specialist isolation.
- N9 PASS-PENDING-OPERATOR: operator validates per-step summary readability at close.
- N10 PASS: anti-pattern catalog read at T1.
- A9 honored: step IDs and labels come from manifest projection.
- A11 honored: bundle paths use `Path`, relative paths are displayed safely, and Windows paths are escaped in HTML.

### AC-6.5-J - D12 close protocol

At close, update sprint-status, cite sandbox-AC PASS, cite lockstep check PASS, record operator readability evidence, and confirm no Composition Spec Section 11 trigger fired. No Section 10 Decision Log entry is expected unless implementation unexpectedly touches composition substrate.

## File Structure Requirements

Expected new files:
- `scripts/utilities/hud_per_step_summary.py`
- `tests/unit/hud/test_per_step_summary_derivation.py`
- `tests/integration/hud/test_per_step_summary_rendering.py`

Expected modified files:
- `scripts/utilities/run_hud.py`
- `tests/test_run_hud.py`
- `docs/operator/hud-guide.md`

Do not modify:
- `app/marcus/orchestrator/production_runner.py`
- `app/marcus/orchestrator/dispatch_adapter.py`
- `app/models/runtime/production_envelope.py`
- `state/config/pipeline-manifest.yaml` unless party-mode explicitly expands scope
- v4.2 prompt pack except through generator if a doc projection unexpectedly changes

## Testing Requirements

K-floor 13:
- 8 representative derivation cases across early/mid/late steps
- 2 no-artifact degradation cases
- 1 all-manifest-hud-steps coverage test
- 1 render integration test for details blocks
- 1 sessionStorage/stable-id render test

Target 18:
- add Windows path escaping, current-step default-open, blocker default-open, watch-mode refresh compatibility, and HTML escaping cases.

Required verification at implementation close:
- `pytest tests/test_run_hud.py tests/unit/hud tests/integration/hud -q --tb=short`
- `python scripts/utilities/check_pipeline_manifest_lockstep.py`
- `python scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-6-5-hud-per-step-expandable-summaries.md`
- `ruff check scripts/utilities/run_hud.py scripts/utilities/hud_per_step_summary.py tests/test_run_hud.py tests/unit/hud tests/integration/hud`

## Dev Agent Record

### Gate 2 Implementation Notes

- Added `scripts/utilities/hud_per_step_summary.py` with one bundle artifact scan per render and O(N) manifest-step derivation keyed by manifest step IDs.
- Covered all 33 `hud_tracked` steps with known derivation patterns or the exact honest fallback `no locked artifact yet`; Phase 1 pre-flight found 0 steps without known derivation source, so A-R2 did not fire.
- Integrated summaries into `scripts/utilities/run_hud.py` as per-step `<details>` blocks with stable IDs, artifact source/freshness/captured fields, default-open current/blocker states, and sessionStorage persistence.
- Updated `docs/operator/hud-guide.md` with expand/collapse semantics, refresh behavior, and honest absent-artifact wording.

### Tests / Evidence

- `.\.venv\Scripts\python.exe -m pytest tests/test_run_hud.py tests/unit/hud/test_per_step_summary_derivation.py tests/integration/hud/test_per_step_summary_rendering.py -q --tb=short` -> 77 passed in 9.14s.
- `.\.venv\Scripts\python.exe -m scripts.utilities.check_pipeline_manifest_lockstep` -> PASS.
- `$env:PYTHONPATH='.'; .\.venv\Scripts\python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` -> PASS.
- `.\.venv\Scripts\python.exe -m scripts.utilities.validate_migration_story_sandbox_acs _bmad-output/implementation-artifacts/migration-6-3-step-02a-prior-run-directives-as-defaults.md _bmad-output/implementation-artifacts/migration-6-4-irene-pass-2-authoring-template.md _bmad-output/implementation-artifacts/migration-6-5-hud-per-step-expandable-summaries.md` -> PASS across 3 story files.

### N-Item / Rider Trace

- N4 PASS: HUD display changes do not affect runtime execution or specialist isolation.
- N9 PASS-PENDING-OPERATOR: per-step summary readability remains for Gate 6 operator close evidence.
- A9 PASS: summary derivation is keyed by manifest step ID/label projection.
- A11 PASS: bundle paths use `Path`, relative path display, and HTML escaping.
- Section 11 trigger check: no Composition Spec Section 11 trigger fired.

### Decision Needed / Halt-And-Adapt

- `decision_needed`: none.
- Halt-and-adapt cycles: none.

### File List

- `scripts/utilities/hud_per_step_summary.py`
- `scripts/utilities/run_hud.py`
- `tests/test_run_hud.py`
- `tests/unit/hud/test_per_step_summary_derivation.py`
- `tests/integration/hud/test_per_step_summary_rendering.py`
- `docs/operator/hud-guide.md`
