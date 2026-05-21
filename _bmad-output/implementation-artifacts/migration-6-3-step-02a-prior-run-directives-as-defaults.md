# Migration Story 6.3: Step 02A surfaces prior-run operator directives as named defaults

**Status:** review
**Sprint key:** `migration-6-3-step-02a-prior-run-directives-as-defaults`
**Epic:** Slab 6 - Post-MVP Production Capability (`migration-epic-6-post-mvp-production`)
**Pts:** ~1
**Gate:** single-gate (minor operator-experience enhancement; no schema-shape risk; no substrate change)
**K-target:** ~1.4x (target 8 / floor 6 — bumped 2026-04-28 per party-mode M-R3 NON-BLOCKING to accommodate M-R1 + M-R2)
**Authored:** 2026-04-28 via `bmad-create-story` workflow from the Slab 6 trial-experience bundle seed.

## Governance

This story completed Gate 1 operator-run `bmad-party-mode` green-light with Winston, Murat, Paige, and Amelia on 2026-04-28. Gate 2 implementation is complete and the story is in `review`; Gate 3 `bmad-code-review`, Gate 4 triage, and Gate 6 close remain future work.

Binding readings completed at authoring T1:
- `_bmad-output/implementation-artifacts/codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md`
- `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md`
- `docs/dev-guide/composition-specification.md` Section 3 invariants and Section 11 triggers
- `docs/dev-guide/substrate-inventory-checklist.md`
- `docs/dev-guide/specialist-anti-patterns.md`
- `docs/dev-guide/migration-story-governance.json`
- `scripts/generators/v42/templates/sections/02A-operator-directives.md.j2`
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` Section 02A
- `scripts/utilities/validate-operator-directives.py`
- `scripts/utilities/run_constants.py`
- `skills/bmad-agent-marcus/SKILL.md` and `skills/bmad-agent-marcus/references/`

## Party-mode green-light (BINDING; ratified 2026-04-28 in --solo mode)

- Convened: Winston + Murat + Paige + Amelia (4-voice panel per discipline doc §5)
- Verdict: unanimous GREEN-WITH-RIDERS — no architectural impasse; no §11 migration trigger fire
- Direction ratified: helper + Step 02A pack amendment (NOT Marcus PR-* extension)
- 6 BINDING riders applied to spec; 3 NON-BLOCKING apply at close

**BINDING riders:**
- **W-R1:** Bound helper to ONE responsibility (find latest valid `operator-directives.md` for same `lesson_slug`; tiebreak by mtime descending). NO scoring, NO multi-candidate selection logic, NO cross-lesson resolution.
- **W-R2:** Spec must explicitly name "helper does NOT call into Marcus PR-* surface" as architectural invariant.
- **M-R1:** Add `test_invalid_prior_directives_falls_through_to_no_prior_path` (validator-rejected prior file should NOT surface as default).
- **M-R2:** Add `test_deterministic_tiebreak_on_identical_mtime` (suggested rule: lexicographic `run_id` descending).
- **P-R1:** Step 02A pack template change must be ADDITIVE — do NOT modify existing prose; preserve in-flight bundle backward-compat.
- **P-R2:** Add `docs/operator/step-02a-prior-run-defaults.md` operator-facing doc.
- **A-R1:** Helper signature accepts `bundle_root: Path` parameter explicitly (testable in isolation).

**NON-BLOCKING riders (apply at close):**
- **M-R3:** K-floor 4 → 6; K-target 6 → 8 to accommodate M-R1 + M-R2.
- **P-R3:** Cross-link from Marcus skill SKILL.md.
- **A-R2:** Phase 1 pre-flight — verify `tests/fixtures/golden_trace/` bundle layout matches operator's `state/config/runs/` layout.

## T1 Readiness Block

Predecessor state:
- Slab 6.2 is closed; manifest `dependencies` are promoted and Composition Spec Section 12 known limitation #1 is resolved.
- `sprint-status.yaml` already carries `migration-6-3-step-02a-prior-run-directives-as-defaults` as a backlog story and `docs/dev-guide/migration-story-governance.json` already pins 6-3 as single-gate.

Live substrate:
- Step 02A prose lives in `scripts/generators/v42/templates/sections/02A-operator-directives.md.j2` and the generated v4.2 pack.
- Step 02A already says Marcus may present an existing in-bundle `operator-directives.md` on resume.
- `scripts/utilities/validate-operator-directives.py` validates one directives file but does not search prior bundles.
- Run constants expose `run_id` and `lesson_slug`; bundle naming and examples under `tests/fixtures/golden_trace/` show prior-run carry-forward fields.

T1 drift handled without halt:
- The seed names `scripts/run_hud.py` elsewhere in the bundle; this story does not touch HUD.
- The seed frames the home as Marcus PR-* extension or Step 02A pack amendment. The low-regression path is a pure helper plus Step 02A template/procedure amendment; party-mode may still ratify Marcus PR-* wiring if Winston prefers it.

## TEMPLATE Scope Decisions

Proposed default for Gate 1 ratification:
- Add a small deterministic helper that scans sibling tracked source bundles for the most recent valid `operator-directives.md` with the same `lesson_slug`.
- Amend Step 02A generated pack prose so Marcus always presents the found prior directives as named defaults with source attribution (`run_id`, bundle date or mtime, path) before writing the current run's directives.
- Require explicit operator choice: `accept prior defaults`, `modify prior defaults`, or `replace from scratch`.
- Preserve the existing validator and current in-bundle resume behavior.

Out of scope:
- No change to `ProductionEnvelope`, `ProductionDispatchAdapter`, production runner, manifest dependency mechanics, or gate precedence.
- No new operator CLI requirement in dev-agent ACs.
- No automatic overwrite of the current run's `operator-directives.md` without explicit accept/modify/replace.
- No semantic merge of multiple prior runs.

Decision-needed for party-mode, not a Gate 0 halt:
- Whether the helper is surfaced as a Marcus PR-* capability extension, a Step 02A pack-only helper, or both. The spec recommends helper + Step 02A amendment to minimize cross-Marcus regression risk.

## Story

As an operator resuming or repeating a lesson run,
I want Step 02A to surface the most recent same-lesson `operator-directives.md` as named defaults with source attribution,
so that I can accept, modify, or replace prior directives without re-entering stable instructions by hand.

## Acceptance Criteria

### AC-6.3-A - Prior directives discovery

Given a current bundle with `run-constants.yaml` containing `lesson_slug`,
when Step 02A prepares the operator directives poll,
then it scans prior tracked source bundles for valid `operator-directives.md` files with the same `lesson_slug`, excludes the current bundle, and chooses the most recent candidate deterministically.

Test pin: `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py::test_discovers_latest_same_lesson_prior_directives`.

### AC-6.3-B - Named defaults with source attribution

Given a prior directives candidate exists,
when Marcus presents Step 02A,
then the operator sees the prior directives as named defaults with `run_id`, date or mtime, source bundle path, and the three directive categories preserved.

Test pin: render/presentation unit asserts all source-attribution fields and directive sections are present.

### AC-6.3-C - Explicit accept / modify / replace required

Given named defaults are presented,
when the operator responds,
then Step 02A writes `operator-directives.md` only after one explicit choice:
- accept prior defaults unchanged
- modify prior defaults and write the modified content
- replace from scratch

The resulting file must pass `validate_operator_directives(...)`.

Test pin: three tests covering accept, modify, and replace write paths.

### AC-6.3-D - No prior bundle degrades cleanly

Given no prior same-lesson directives exist,
when Step 02A starts,
then the current poll behaves as it does today and records either operator directives or the explicit "No operator directives" acknowledgment.

Test pin: no-prior-bundle path preserves current output shape.

### AC-6.3-E - Current in-bundle resume behavior preserved

Given the current bundle already contains `operator-directives.md`,
when Step 02A resumes,
then Marcus presents the current file for reconfirmation before searching older bundles, preserving the existing resume rule.

Test pin: current-bundle directives take precedence over older defaults.

### AC-6.3-F - Pack and docs updated through generated source

Given v4.2 pack generation is manifest/template-driven,
when Step 02A prose changes,
then the change lands in `scripts/generators/v42/templates/sections/02A-operator-directives.md.j2` and the generated pack is regenerated through the v4.2 generator, not hand-edited.

Test pin: pipeline lockstep check remains green if generated pack changes.

### AC-6.3-G - N-item and anti-pattern trace

The implementation must record:
- N4 PASS: Marcus and source-bundle behavior remain isolated; production composition substrate unchanged.
- N9 PASS-PENDING-OPERATOR: operator validates the accept/modify/replace workflow at close.
- N10 PASS: anti-pattern catalog read at T1.
- A8 honored: repeated/resumed runs are first-class.
- A11 honored: path handling uses `Path` and no string-built Windows-hostile paths.

### AC-6.3-H - D12 close protocol

At close, update sprint-status, cite sandbox-AC PASS, record operator-visible evidence for the defaults workflow, and confirm no Composition Spec Section 11 trigger fired. No Section 10 Decision Log entry is expected unless implementation unexpectedly touches composition substrate.

## File Structure Requirements

Expected new files:
- `scripts/utilities/operator_directives_defaults.py` - pure helper for prior-bundle scan and default selection.
- `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py` - focused integration tests.

Expected modified files:
- `scripts/generators/v42/templates/sections/02A-operator-directives.md.j2`
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` (regenerated only)
- `docs/operator/trial-run-runbook.md` or the closest existing operator runbook surface
- Possibly `skills/bmad-agent-marcus/capabilities/` if Gate 1 chooses PR-* surfacing

Do not modify:
- `app/models/runtime/production_envelope.py`
- `app/marcus/orchestrator/production_runner.py`
- `app/marcus/orchestrator/dispatch_adapter.py`
- `state/config/pipeline-manifest.yaml` unless party-mode explicitly expands scope

## Testing Requirements

K-floor 4:
- present prior bundle
- no prior bundle
- explicit accept/modify/replace path
- current-bundle resume precedence

Target 6:
- add same-lesson filtering, invalid prior directives ignored, deterministic tie-break on mtime/run_id as needed.

Required verification at implementation close:
- focused pytest for the new test file
- `python scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-6-3-step-02a-prior-run-directives-as-defaults.md`
- if generated pack changes: `python scripts/utilities/check_pipeline_manifest_lockstep.py`

## Dev Agent Record

### Gate 2 Implementation Notes

- Implemented `scripts/utilities/operator_directives_defaults.py` as a pure Step 02A helper with explicit `bundle_root: Path`, current-bundle resume precedence, same-lesson prior-run discovery, invalid-prior fallthrough, deterministic mtime/run_id tiebreak, and explicit accept/modify/replace write choices.
- Updated the Step 02A v4.2 template additively, regenerated the production prompt pack and fixture hash, and added operator-facing documentation plus Marcus skill/runbook cross-links.
- Preserved the architectural invariant that the helper does not call Marcus PR-* surfaces and does not touch production composition substrate.

### Tests / Evidence

- `.\.venv\Scripts\python.exe -m pytest tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py tests/generators/v42 -q --tb=short` -> 16 passed in 2.01s.
- `.\.venv\Scripts\python.exe -m scripts.utilities.validate_migration_story_sandbox_acs _bmad-output/implementation-artifacts/migration-6-3-step-02a-prior-run-directives-as-defaults.md _bmad-output/implementation-artifacts/migration-6-4-irene-pass-2-authoring-template.md _bmad-output/implementation-artifacts/migration-6-5-hud-per-step-expandable-summaries.md` -> PASS across 3 story files.
- `.\.venv\Scripts\python.exe -m scripts.utilities.check_pipeline_manifest_lockstep` -> PASS.

### N-Item / Rider Trace

- N4 PASS: Marcus/operator defaults helper remains isolated; no runtime composition substrate changes.
- N5 PASS: Step 02A output remains the existing `operator-directives.md` contract.
- N9 PASS-PENDING-OPERATOR: accept/modify/replace readability remains for Gate 6 operator close evidence.
- A-R2 pre-flight PASS: fixture bundle layout is compatible with the operator run-bundle pattern used by the helper tests.
- Section 11 trigger check: no Composition Spec Section 11 trigger fired.

### Decision Needed / Halt-And-Adapt

- `decision_needed`: none.
- Halt-and-adapt cycles: none.

### File List

- `scripts/utilities/operator_directives_defaults.py`
- `tests/integration/marcus/test_step_02a_prior_run_directives_as_defaults.py`
- `scripts/generators/v42/templates/sections/02A-operator-directives.md.j2`
- `docs/workflow/production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md`
- `tests/generators/v42/fixtures/expected_pack/fixture_pack.md`
- `tests/generators/v42/fixtures/pack_sha_fixture.txt`
- `docs/operator/step-02a-prior-run-defaults.md`
- `docs/operator/trial-run-runbook.md`
- `skills/bmad-agent-marcus/SKILL.md`
