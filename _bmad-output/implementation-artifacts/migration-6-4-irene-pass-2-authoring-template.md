# Migration Story 6.4: Irene Pass 2 authoring template encodes validator contract as explicit schema constraints

**Status:** review
**Sprint key:** `migration-6-4-irene-pass-2-authoring-template`
**Epic:** Slab 6 - Post-MVP Production Capability (`migration-epic-6-post-mvp-production`)
**Pts:** ~4
**Gate:** dual-gate (`schema_shape + invariant_preservation`)
**K-target:** ~1.4x (target 18 / floor 14 — bumped 2026-04-28 per party-mode M-R4 NON-BLOCKING to accommodate validator-oracle alignment tests + composition smoke)
**Authored:** 2026-04-28 via `bmad-create-story` workflow from the Slab 6 trial-experience bundle seed.

## Governance

This story completed Gate 1 operator-run `bmad-party-mode` green-light with Winston, Murat, Paige, Amelia, Quinn-R, and Mary on 2026-04-28. Gate 2 implementation is complete and the story is in `review`; Gate 3 `bmad-code-review`, Gate 4 triage, Gate 5 operator-side dual-gate evidence, and Gate 6 close remain future work.

Binding readings completed at authoring T1:
- `_bmad-output/implementation-artifacts/codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md`
- `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md`
- `docs/dev-guide/composition-specification.md` Sections 3, 10, 11
- `docs/dev-guide/substrate-inventory-checklist.md`
- `docs/dev-guide/specialist-anti-patterns.md`
- `docs/dev-guide/pydantic-v2-schema-checklist.md`
- `docs/dev-guide/story-cycle-efficiency.md`
- `docs/dev-guide/migration-story-governance.json`
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
- `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py`
- `app/specialists/irene/graph.py`
- `app/specialists/irene/state.py`
- `app/specialists/irene/expertise/README.md`
- `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md`
- `skills/bmad-agent-content-creator/references/pass-2-procedure.md`
- `skills/bmad-agent-content-creator/references/template-segment-manifest.md`
- `docs/workflow/trial-run-pass2-artifacts-contract.md`

## Party-mode green-light (BINDING; ratified 2026-04-28 in --solo mode)

- Convened: Winston + Murat + Paige + Amelia + Quinn-R + Mary (6-voice panel per discipline doc §5; dual-gate + harvest-gate review)
- Verdict: unanimous GREEN-WITH-RIDERS — no architectural impasse; no §11 migration trigger fire detected at spec authoring
- Direction ratified: Pydantic + JSON Schema + Markdown trio; layered validation (schema-first then procedural); locations as proposed
- 9 BINDING riders applied to spec; 5 NON-BLOCKING apply at code-review or close

**BINDING riders:**
- **W-R1:** Pydantic model is THE authoritative source of truth; JSON Schema regenerated from model (not hand-authored); Markdown references Pydantic field names + descriptions; lockstep tested.
- **W-R2:** Add `test_markdown_template_field_names_match_pydantic_model` — parses Markdown, extracts referenced field names, asserts subset of Pydantic model fields. Prevents drift.
- **W-R3:** Procedural validator alignment layer is UNIDIRECTIONAL — schema-first then procedural; document order in code as contractual.
- **M-R1:** Enumerate procedural-only rules explicitly in spec — name each (cluster arc continuity; spoken bridge cadence; narration cue presence; etc.) + the equivalence test that proves it's covered.
- **M-R2:** Add `test_schema_valid_but_procedural_rejected_fails_loud` — proves layered validation order works correctly.
- **M-R3:** Add `test_validator_oracle_alignment_full` — for each currently-validator-enforced rule, parametrized test asserts new template enforces same rule (schema OR procedural).
- **P-R1:** Include 3 worked examples in Markdown drawn from actual 2026-04-20 trial run B-Run §08 friction.
- **P-R2:** Cross-link template ↔ `validate-irene-pass2-handoff.py` bidirectionally; both directions tested.
- **A-R1:** Phase 1 pre-flight — verify new template loading pattern matches existing pure-LLM `_act` category. If shift detected (act-body category change), HALT-and-surface per Composition Spec §11 trigger 5.
- **A-R2:** If cluster arc continuity requires state-machine modeling beyond simple procedural, surface as decision_needed at Phase 2; do NOT silently expand scope.
- **QR-R1:** Add `tests/composition/test_irene_pass_2_template_composition_smoke.py` — exercises template through `ProductionDispatchAdapter`; verifies envelope contribution shape unchanged + Composition Smoke gate fires GREEN.
- **QR-R2:** Verify substrate inventory checklist N4 + N11 both PASS at code-review traceback.

**NON-BLOCKING riders (apply at code-review or close):**
- **M-R4:** K-target 16 → 18; floor 12 → 14 to accommodate alignment tests.
- **P-R3:** Add `docs/dev-guide/irene-pass-2-authoring.md` operator-facing companion guide.
- **A-R3:** Effort-estimate explicit phasing: 1d Pydantic + Schema lockstep; 1d procedural alignment; 1d Markdown + examples; 1d Irene `_act` integration + composition smoke; 1d halt-and-adapt buffer.
- **MA-R1:** Harvest review at story close — if cluster-arc continuity required state-machine modeling that worked cleanly, file as **A18 candidate** ("State-machine modeling rescues seemingly-procedural validation").
- **MA-R2:** Spec author explicitly enumerates which validator rules went schema vs procedural with rationale per rule (becomes A18 evaluation evidence base).

## T1 Readiness Block

Predecessor state:
- Slab 6.2 is closed; manifest dependencies are explicit with permanent runner fallback.
- `docs/dev-guide/migration-story-governance.json` already pins 6-4 as dual-gate.

Live substrate:
- Irene app scaffold exists at `app/specialists/irene/` and `_act` currently reads Markdown references through `_read_pass_2_references(...)`, including `pass-2-authoring-template.md`.
- A Markdown authoring template already exists at `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md`; this story must extend/align it, not create a duplicate Markdown source of truth.
- The strict post-hoc validator is `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`. It checks required envelope fields, Gary/perception alignment, segment-manifest/narration-script presence, behavioral intent parity, `visual_detail_load`, timing metadata, bridge cadence, cluster arc integrity, motion perception, and traceable visual references.
- The local anti-pattern catalog labels A6 as closed-enum red-rejection; the bundle seed uses A6 language for "implicit validator contract." This spec honors both: closed enums receive three rejection surfaces, and the validator contract becomes explicit at authoring time.

T1 conclusion:
- No unanticipated architectural disagreement requires halting Gate 0.
- The validator contract is not fully representable in JSON Schema because cluster arc continuity, spoken bridge cadence, and narration cue presence are procedural. The story therefore uses Pydantic/JSON Schema for structural constraints and a procedural validator-alignment layer for cross-artifact rules. This is a design constraint to ratify at Gate 1, not a halt.

## TEMPLATE Scope Decisions

Proposed default for Gate 1 ratification:
- Add `app/specialists/irene/authoring/pass_2_template.py` as the Pydantic v2 strict authoring contract for Pass 2 handoff and output metadata.
- Emit `schema/irene_pass_2_authoring.v1.schema.json` with parity and shape-pin tests.
- Update existing `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md` to reference the schema and inline the authoring guidance. Do not create a second Markdown template.
- Refactor the validator only enough to consume shared constants or helper checks where clean; do not force procedural cluster/bridge logic into schema if it becomes less readable or less correct.
- Keep Irene usable in isolated M3 harness mode and production runner composition mode.

Out of scope:
- No redesign of `ProductionEnvelope` or repeated-specialist Path Z behavior.
- No new Pass 2 creative policy beyond encoding the validator's current contract.
- No ElevenLabs theatrical-direction synthesis or model-swap/tag authoring.
- No broad rewrite of Irene's `_act`; loading stricter references is allowed, but a new act-body category requires halt-and-surface.

Decision-needed for party-mode:
- Ratify Pydantic + JSON Schema + Markdown guidance as the format trio.
- Ratify location: `app/specialists/irene/authoring/` for code, `schema/` for emitted JSON Schema, existing content-creator references for operator/Irene-facing Markdown.
- Ratify validation timing: authoring-time template plus post-hoc validator alignment; production runtime fail-closed only if the generated artifacts violate the current validator contract.

## Story

As an operator running Irene Pass 2 in the production pipeline,
I want the Pass 2 authoring template to encode the validator's strict contract as explicit schema constraints and inline guidance,
so that Irene can produce `segment-manifest.yaml`, `narration-script.md`, `perception-artifacts.json`, and `pass2-envelope.json` in one pass without exceptional post-hoc repair.

## Acceptance Criteria

### AC-6.4-A - Pydantic v2 authoring model and JSON Schema lockstep

Given the validator's current Pass 2 contract,
when the dev agent adds the authoring model family,
then it follows the Pydantic v2 checklist: `extra="forbid"`, `validate_assignment=True`, timezone-aware datetimes where used, closed enums with three red-rejection surfaces, JSON Schema parity, golden fixture, and shape-pin tests.

Test pin: `tests/unit/specialists/irene/test_pass_2_template_strict.py`.

### AC-6.4-B - Validator contract encoded without duplicate sources of truth

Given `validate-irene-pass2-handoff.py` is the current fail-closed oracle,
when the authoring template lands,
then every structurally expressible validator rule is represented in the model/schema or named as a procedural validation rule with a test proving alignment.

Minimum covered rules:
- required `gary_slide_output` and `perception_artifacts`
- absolute or normalized path matching between Gary slide output and perception source image paths
- valid `visual_detail_load` values
- required timing fields: `timing_role`, `content_density`, `duration_rationale`, `bridge_type`
- narration-script and segment-manifest behavioral-intent parity
- segment IDs matching script markers
- traceable `visual_references[].narration_cue`
- bridge cadence and cluster arc procedural rules documented as procedural checks, not silent gaps

Test pin: `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py`.

### AC-6.4-C - Existing validator fixtures remain green

Given current validator tests encode the post-hoc contract,
when the new template is introduced,
then existing `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py` still passes or is updated only for intentional stricter authoring diagnostics with explicit compatibility notes.

### AC-6.4-D - Irene consumes the template at composition time

Given Irene `_act` reads Pass 2 references,
when Pass 2 prompt assembly occurs,
then the authoring template/schema guidance is included in the prompt context for both isolated and production composition modes without bypassing the 9-node scaffold.

Test pin: focused test around `_read_pass_2_references(...)` / `_assemble_pass_2_prompt(...)`.

### AC-6.4-E - Markdown template and operator guide aligned

Given the existing Markdown authoring template is already referenced by Irene,
when schema files land,
then `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md` and a concise `docs/dev-guide/irene-pass-2-authoring.md` point to the schema, explain procedural rules, and show a minimal passing example.

### AC-6.4-F - N-item and anti-pattern trace

The implementation must record:
- N4 PASS: Irene isolated mode remains functional.
- N5 PASS: Pass 2 handoff/output shape remains stable and explicit.
- N7 PASS: existing validator fixtures and replay-relevant slices remain green.
- N9 PASS-PENDING-OPERATOR: operator validates the authoring guide/template during Gate 5.
- N10 PASS: anti-pattern catalog read at T1.
- N11 PASS: template declares isolated and composed usage.
- A6 honored: closed enums get three rejection surfaces; implicit validator contract becomes explicit.
- A12 honored: any manual ancillary step is either generator-emitted or documented as a deferred follow-on.
- P3 honored: Gate 1 party-mode includes a composition smoke discussion for isolated and composed template consumption.

### AC-6.4-G - Dual-gate operator evidence

At Gate 5, operator runs the authoring/validator evidence command against a representative Pass 2 fixture or B-Run-derived sample and pastes the result into the Dev Agent Record. The command must be Python-based and sandbox-AC compliant.

### AC-6.4-H - D12 close protocol

At close, update sprint-status, record sandbox-AC PASS, record operator dual-gate evidence, cite validator fixture status, and confirm no Composition Spec Section 11 trigger fired. A Section 10 Decision Log entry is only required if implementation unexpectedly changes composition substrate.

## File Structure Requirements

Expected new files:
- `app/specialists/irene/authoring/__init__.py`
- `app/specialists/irene/authoring/pass_2_template.py`
- `schema/irene_pass_2_authoring.v1.schema.json`
- `tests/fixtures/specialists/irene/pass_2_template_golden.json`
- `tests/unit/specialists/irene/test_pass_2_template_strict.py`
- `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py`
- `docs/dev-guide/irene-pass-2-authoring.md`

Expected modified files:
- `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md`
- `app/specialists/irene/graph.py` only if prompt-reference loading must point at the new contract
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py` only for shared constants/helpers and clearer diagnostics
- `skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py`
- `app/specialists/irene/expertise/README.md`

Do not modify:
- `ProductionEnvelope` / `SpecialistContribution` schema
- `ProductionDispatchAdapter`
- production runner dependency_map rules
- v4.2 pipeline topology

## Testing Requirements

K-floor 12:
- 4 strict model/schema checks
- 3 closed enum red-rejection surfaces
- 3 validator-alignment cases
- 1 Irene prompt/reference consumption test
- 1 existing validator fixture preservation run

Target 16:
- add cluster arc procedural alignment, bridge cadence procedural alignment, absolute path mismatch, and no-leak/JSON Schema parity cases as needed.

Required verification at implementation close:
- focused unit/integration tests above
- existing validator test module
- `python scripts/utilities/validate_migration_story_sandbox_acs.py _bmad-output/implementation-artifacts/migration-6-4-irene-pass-2-authoring-template.md`

## Dev Agent Record

### Gate 2 Implementation Notes

- Added `app/specialists/irene/authoring/pass_2_template.py` as the Pydantic v2 source of truth with strict assignment validation, closed enums, timezone-aware generated timestamps, structural cross-artifact checks, and named procedural-only rule declarations.
- Generated `schema/irene_pass_2_authoring.v1.schema.json` from the model and pinned parity with a golden fixture plus schema/Markdown lockstep tests.
- Updated the existing Irene authoring Markdown, validator cross-links, Irene expertise README, and `docs/dev-guide/irene-pass-2-authoring.md`; no duplicate Markdown source of truth was introduced.
- Verified Irene prompt composition consumes the template/schema guidance through `_read_pass_2_references(...)` and a `ProductionDispatchAdapter` composition smoke without changing contribution shape.
- A-R1 HALT trigger did not fire: Irene `_act` remains pure-LLM prompt assembly with stricter reference loading.
- A-R2 HALT trigger did not fire: cluster-arc continuity stayed a named procedural rule; no state-machine expansion was required.

### Tests / Evidence

- `.\.venv\Scripts\python.exe -m pytest tests/unit/specialists/irene/test_pass_2_template_strict.py tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py tests/specialists/irene/test_irene_pass2_authoring_prompt_consumption.py tests/composition/test_irene_pass_2_template_composition_smoke.py -q --tb=short` -> 13 passed in 1.44s.
- `.\.venv\Scripts\python.exe -m pytest skills/bmad-agent-marcus/scripts/tests/test_validate_irene_pass2_handoff.py -q --tb=short` -> 62 passed in 6.35s.
- `.\.venv\Scripts\python.exe -m scripts.utilities.validate_migration_story_sandbox_acs _bmad-output/implementation-artifacts/migration-6-3-step-02a-prior-run-directives-as-defaults.md _bmad-output/implementation-artifacts/migration-6-4-irene-pass-2-authoring-template.md _bmad-output/implementation-artifacts/migration-6-5-hud-per-step-expandable-summaries.md` -> PASS across 3 story files.

### N-Item / Rider Trace

- N4 PASS: isolated Irene prompt/reference flow remains functional.
- N5 PASS: Pass 2 handoff/output shape remains explicit and additive.
- N7 PASS: existing validator fixtures remain green.
- N9 PASS-PENDING-OPERATOR: Gate 5 dual-gate evidence still requires operator-selected representative Pass 2 sample.
- N11 PASS: docs and template declare isolated and composed usage.
- QR-R1 PASS: composition smoke covers `ProductionDispatchAdapter` path and unchanged contribution shape.
- Section 11 trigger check: no Composition Spec Section 11 trigger fired.

### Decision Needed / Halt-And-Adapt

- `decision_needed`: none at Gate 2.
- Cycle 2 decision_needed: URL-pattern Rust-regex fallback (operator-ratified 2026-04-28; documented in code at `app/specialists/irene/authoring/pass_2_template.py` LOCAL_PNG_PATH_PATTERN trade-off comment).
- Gate 5 evidence captured 2026-04-28 (see below).

### Operator Dual-Gate Gate-2 Evidence (AC-6.4-G; Gate 5)

- **Date:** 2026-04-28
- **Command:** `.venv\Scripts\python.exe scripts\operator\gate5_slab_6_4.py`
- **Started:** 2026-04-28T13:53:59.762114+00:00
- **Finished:** 2026-04-28T13:54:08.047333+00:00
- **validator-oracle alignment:** PASS — 63 passed in 1.90s
- **composition smoke:** PASS — 1 passed in 1.19s
- **strict + closed-enum + procedural-rule:** PASS — 19 passed in 1.43s
- **Total:** 83 passed in 4.52s aggregate
- **Operator witness:** Juan Leon (operator session)
- **Disposition:** PASS — substrate_shape gate cleared + invariant_preservation gate cleared. AC-6.4-G satisfied.

### Closeout Trace

- Implementation lineage: `162d129` (bundled) → `3dc6723` review (11 patch + 0 DN) → `c2df610` cycle 1 → `8b165e8` second-pass HALT (3 re-trace FAILs) → operator-ratified URL-pattern fallback → `1151bdc` cycle 2 → `e9ede93` third-pass CLEAN → operator Gate 5 ceremony PASS 2026-04-28
- Riders: 9 BINDING + 5 NON-BLOCKING all satisfied; cycle 2 patches (BH-1 + EH-1 + AA-1) all PASS at third-pass re-trace
- N-items: N4 + N5 + N7 + N9 + N11 PASS (N5 flipped FAIL → PASS post-cycle-2)
- Mary harvest-gate A18 disposition (operator-ratified 2026-04-28): **leave as candidate.** Cycle 2 work was procedural-validator-alignment expansion (50 enforcement points enumerated with rationale), not state-machine elevation. The 6 procedural rules (cluster arc continuity, bridge cadence, narration cue presence, etc.) use procedural alignment functions, not FSM/state-machine modeling. Revisit at next state-machine-shaped substrate work.
- Composition Spec §10 Decision Log: N/A (no substrate change; Irene `_act` body category unchanged per A-R1; QR-R1 composition smoke unchanged).
- Bundle progress: 3/3 closed (6.3 + 6.5 closed earlier same day; 6.4 closed via this trace). **First tracked trial UNBLOCKED.**
- Halt-and-adapt cycles: none.

### File List

- `app/specialists/irene/authoring/__init__.py`
- `app/specialists/irene/authoring/pass_2_template.py`
- `schema/irene_pass_2_authoring.v1.schema.json`
- `tests/fixtures/specialists/irene/pass_2_template_golden.json`
- `tests/unit/specialists/irene/test_pass_2_template_strict.py`
- `tests/integration/specialists/irene/test_pass_2_template_validator_alignment.py`
- `tests/specialists/irene/test_irene_pass2_authoring_prompt_consumption.py`
- `tests/composition/test_irene_pass_2_template_composition_smoke.py`
- `skills/bmad-agent-content-creator/references/pass-2-authoring-template.md`
- `skills/bmad-agent-marcus/scripts/validate-irene-pass2-handoff.py`
- `docs/dev-guide/irene-pass-2-authoring.md`
- `app/specialists/irene/expertise/README.md`
