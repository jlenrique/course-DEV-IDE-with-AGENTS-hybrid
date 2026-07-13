---
baseline_commit: 4666b7a5c53747e74729f4072a929b065a499a01
---

# Story 36.3: Promise transform — ratified LOs to pertinent-ability vows

Status: done

## Story

As the Marcus-SPOC workbook runtime,
I want the Promise transformed from operator-ratified learning objectives into pertinent-ability vows,
so that pre-work foreshadows what learners can notice and begin without replacing the objectives, claiming finality early, or handing over the answer.

## Dependency Position

`38.0 -> 38.3b -> 36.1 -> {36.2 || 36.3} -> 36.4`

Stories 36.1 and 36.2 are done. Story 36.3 is the next permitted node. Story 36.4 remains blocked until 36.3 closes.

## Binding Authority Ruling

The epic's phrase “Irene's ratified lesson plan (`lesson_plan_from_run`)” names lineage and intent, not sufficient ratification evidence. Irene cannot ratify. The operator-produced `<run_dir>/ratified-los.json` is the Promise LO SSOT; `lesson_plan_from_run(run_dir)` is required only as the authored-plan lineage witness. Never infer ratification from Irene authorship, filename, loader defaults, or plan presence.

The strict resolver accepts exactly two extant proof variants:

1. **Canonical G0R row:** validates as canonical `LearningObjective` with `status="ratified"` (including its existing source-ref, adequacy, and Bloom invariants).
2. **Plan-dialogue row:** explicit `status="ratified"`, `actor="operator"`, `source="plan-dialogue"`, nonblank open-id `objective_id`, and nonblank `statement`; blank Bloom is permitted only for this named legacy producer shape.

Mixed variants are allowed only when every row independently validates. Missing status/actor/source must never be defaulted into the plan-dialogue variant. Corrupt or wrong-shaped artifacts raise a named strict resolver error; genuine absence/empty substrate returns an honest unavailable resolution.

**Lineage reconciliation is exact, not semantic:** Irene's plan must carry `planning_provenance.ratified_los_path == "ratified-los.json"` and `planning_provenance.ratified_los_digest == "sha256:" + sha256(exact artifact bytes)`. Missing/mismatched path or digest degrades with `promise_ratified_lo_lineage_unverified`, zero transformer calls. Do not compare plan-unit IDs/text to authority rows: Irene legitimately re-authors those. `coverage_lo_status` is advisory and never ratification proof.

**Variant-recognition ladder:** malformed JSON, non-object root, non-list `ratified_los`, non-object row, blank/invalid ID or statement, duplicate ID, or an explicit `status="ratified"` row matching neither complete authority variant raises `PromiseObjectiveResolutionError`. A structurally recognizable row (valid ID + statement) whose status is missing, unknown, provisional, or refined degrades the whole resolution with `promise_plan_not_ratified`. A row that declares `status="ratified"` and either `actor` or `source` as plan-dialogue evidence but lacks the exact counterpart (`actor="operator"`, `source="plan-dialogue"`) degrades with `promise_plan_dialogue_authority_unproven`; fields are never defaulted.

## Acceptance Criteria

1. **Strict ratified-LO resolver and lineage**
   - Add an M3-safe, read-only resolver under `app/marcus/lesson_plan/` that requires an authored Irene lesson-plan lineage witness and independently reads `ratified-los.json` as authority.
   - It returns a strict/frozen resolution containing ordered normalized `ObjectiveInput`s, authority variant/refs, availability, stable losses, and operator warnings.
   - Only a nonempty, all-ratified, unique-ID set is eligible. Preserve file order; never sort, filter to a partial final set, infer IDs, or replace statements.
   - Missing plan lineage or absent/empty objective substrate is unavailable with distinct stable losses. Any provisional/refined/unknown/missing status or mixed ratification degrades with `promise_plan_not_ratified`; incomplete declared plan-dialogue proof degrades with `promise_plan_dialogue_authority_unproven`; missing/mismatched provenance path/digest degrades with `promise_ratified_lo_lineage_unverified`. The binding variant-recognition ladder above controls fail-loud errors.

2. **Closed production composition seam**
   - Extend, never bypass, Story-36.1's `PromiseTransformer(PromiseTransformRequest) -> PromiseProjection` contract.
   - Implement the sole pure entry point `compose_promise_projection(request: PromiseProjectionRequest, transformer: PromiseTransformer) -> PromiseProjectionResult`.
   - Pre-compose gates pass before one strict transform request is formed. Eligible input invokes the injected transformer exactly once; any pre-gate failure invokes it zero times. Unexpected transformer runtime exceptions propagate.
   - Wrong return type/shape or a non-authored return degrades with stable `promise_transformer_contract_invalid`; no partial authored prose survives.

3. **Respect-not-replace mapping**
   - An authored result has exactly one vow per ratified objective in identical order. `PromiseVow.objective_id` sequence equals the input sequence exactly: no drop, duplicate, addition, substitution, repair, or reorder.
   - Each vow is one nonblank Markdown-safe line and cannot inject reserved pre-work headings, newline/list structures, or a pre-added Markdown bullet.
   - Exact ID/cardinality/order is the automated respect-not-replace proof. Semantic LO fidelity remains named WARN/operator LO-vs-vow review; do not claim machine semantic proof.

4. **Pertinent-ability and half-rhyme posture**
   - Extend `PromiseTransformRequest` with the required literal `transformation_posture: Literal["pertinent_ability_first_move"]`. That posture means: frame each objective as a capability to see, name, distinguish, or take a first move on; do not claim completed solution or mastery. The injected-spy test must prove the exact literal reaches the transformer. Scene/Friction context remains orientation only.
   - Exact leashed prose is never byte-matched and no mandatory stock prefix is imposed. Pertinence, deliverable scope, half-rhyme quality, and mastery overclaim remain named operator WARN checks.

5. **Legacy placeholder elimination**
   - An authored Promise may not contain a normalized variant of `objective statement unresolved` (Unicode NFKC, casefold, punctuation/whitespace tolerant) or an unresolved marker.
   - A match is automated FAIL-to-author with `promise_unresolved_placeholder`; discard every vow. The Part-2 ratified fixture proves the placeholder is absent.

6. **Spoiler heuristic is WARN-only**
   - `PromiseProjectionRequest` carries explicit `forbidden_resolution_spans`; never infer answers from model priors or arbitrary corpus text.
   - Heuristic: NFKC/casefold/punctuation/whitespace normalization; WARN on normalized forbidden-span containment or meaningful-token recall `>= 0.80` with at least four shared tokens. Shorter generic spans cannot trigger the overlap heuristic.
   - A match records `promise_spoiler_heuristic_match` plus the always-present `promise_no_spoiler_operator_check`, but does not downgrade an otherwise structurally valid Promise. Semantic paraphrase leakage remains operator judgment.
   - Part-2 uses the real Q5 answer/resolution as an independent forbidden span; a copied answer WARNs, while a capability vow remains authored without a false positive.

7. **Ratification honesty and all-or-nothing finality**
   - Absent plan/objective substrate -> unavailable, no vows, stable marker/loss, zero transformer calls.
   - Present but any objective unproven/unratified/mixed -> degraded, no vows, `promise_plan_not_ratified`, zero calls.
   - Source adequacy verdict remains advisory: a canonical ratified LO with thin/gap adequacy transforms and records an operator warning; it is never silently dropped.
   - Empty supposedly-ratified list has its own pinned loss. No path publishes a partial Promise.

8. **Post-transform structural gates**
   - Exact objective coverage/order, strict return type, authored-state honesty, reserved headings, multiline/list injection, placeholder elimination, and digit-form numeral multiset preservation are automated FAIL-to-author gates.
   - Any failure discards all authored vows and returns degraded with deterministic evidence. Do not repair transformer output.
   - Semantic objective fidelity, spoiler meaning beyond declared spans, half-rhyme, and pertinent-ability quality remain explicit operator WARNs.

9. **Structured fixtures and A9 golden semantics**
   - Add `tests/fixtures/prework_36_3/` families for: Part-2 ratified success with real Q5 forbidden span; plan-dialogue proof; canonical thin/gap adequacy; unratified/mixed set; absent/empty; and spoof/malformed/post-transform boundaries.
   - Fixture authority coordinates resolve to real course/design sources or named app-produced artifact shapes. No self-declared fake coordinate passes unverified.
   - Deterministic resolution/gate receipts may be canonical-serialization pinned. Vow prose is structural/gate-pinned only, never byte-goldened.

10. **M3/offline and focused evidence**
   - Production changes remain lesson-plan only: no orchestrator, specialists, terminal/render, workbook producer, provider/model client/config, research, Scene semantics, or `07W.*` registration.
   - Injected spies/stubs prove request formation and exact call count without credentials. Strict/extra/coercion/serialization pins and 36.1/36.2 regressions remain green.
   - Focused pytest, Ruff, and diff check pass. No paid/live run; Story 36.4 owns integration and rendered evidence.

## Gate Taxonomy

| Gate | Disposition | Witness |
|---|---|---|
| plan/objective substrate absent or empty | FAIL-to-author -> unavailable | automated |
| explicit ratification proof missing/mixed/non-ratified | FAIL-to-author -> degraded | automated |
| corrupt/wrong-shaped authority artifact | fail-loud resolver error | automated |
| objective ID/text/order/uniqueness | FAIL-to-author | automated |
| transformer strict return and authored state | FAIL-to-author | automated |
| exact vow ID/cardinality/order mapping | FAIL-to-author | automated |
| unresolved placeholder/reserved heading/multiline/list injection | FAIL-to-author | automated |
| digit-form numeral multiset preservation | FAIL-to-author | automated mutations |
| declared-answer exact/near-verbatim heuristic | WARN | automated + operator |
| source adequacy thin/gap | WARN, never drop | automated + operator |
| objective semantic fidelity / pertinent ability / half-rhyme / true no-spoiler | WARN | operator spot-check |
| exact leashed wording | no gate / never byte-match | structural gates only |

## Tasks / Subtasks

- [x] Define strict Promise objective resolution/request/result/gate receipt contracts (AC: 1-10)
- [x] Implement strict run resolver for Irene lineage + explicit `ratified-los.json` authority variants (AC: 1, 7, 9)
- [x] Extend the closed PromiseTransformer request/return seam additively (AC: 2-4)
- [x] Implement one-call composition plus pre/post structural gates and honest dispositions (AC: 2-8)
- [x] Implement WARN-only declared-span spoiler heuristic and operator warnings (AC: 4, 6, 8)
- [x] Add real Part-2, plan-dialogue, canonical thin, unratified/mixed, absent/empty, and spoof/mutation fixtures (AC: 5-9)
- [x] Add strictness, resolver, mapping, mutation, call-count, M3, serialization, and regression tests (AC: 1-10)
- [x] Run focused regression/static checks (AC: 10)

## Dev Notes

### Authorized scope

- `app/marcus/lesson_plan/prework_projection.py` additive Promise contract changes if required
- New `app/marcus/lesson_plan/promise_projection.py`
- Existing pure `planning_context.py` or `workbook_enrichment.py` only if strictly necessary; prefer a new strict resolver to avoid widening permissive legacy behavior
- `tests/unit/marcus/lesson_plan/test_prework_projection_36_3.py`
- `tests/fixtures/prework_36_3/**`
- 36.1 fixture update only if an additive schema requires it
- Story and sprint ledger

No orchestrator, specialist, terminal producer, `_act.py`, renderer/DOCX, manifest/runner, `workbook_wiring`, `07W.*`, Scene/36.2 behavior, review/deep-dive/research, or live model instantiation.

### Existing seams to reuse

- `app/marcus/lesson_plan/prework_projection.py`: `ObjectiveInput`, `PromiseVow`, `PromiseProjection`, `PromiseTransformRequest`, `PromiseTransformer`
- `app/marcus/lesson_plan/learning_objective.py`: canonical lifecycle/invariants; Irene cannot ratify, operator owns refined->ratified
- `app/marcus/lesson_plan/workbook_enrichment.py::lesson_plan_from_run`: lineage/context only
- `app/marcus/lesson_plan/planning_context.py`: identifies `ratified-los.json` as authoritative but is intentionally permissive; do not inherit its missing-status default
- `app/marcus/cli/plan_dialogue_cli.py::_write_ratified_los`: explicit plan-dialogue proof variant
- `app/marcus/orchestrator/production_runner.py::_apply_g0r_ratification`: canonical G0R writer shape (read for contract only; no import)

### Part-2 spoiler witness

Use the actual Chapter-2 Q5 scenario/answer source under `course-content/courses/tejal-apc-c1-m1-p2-trends/assessments/chapter-2-knowledge-check.md`. Keep answer/reference text independent from the transformed vow so the heuristic test is not circular.

### Ownership fences

- 36.3 owns strict LO resolution and pure Promise composition only.
- 36.4 owns `07W.1` instantiation/persistence, terminal consumption, Markdown->DOCX, mode parity, and integrated Part-2 golden.
- Do not change the 38.3b neutral `workbook_brief_stub` identity/output yet.

## Dev Agent Record

### Agent Model Used

GPT-5.4 / Amelia developer workflow

### Debug Log References

- RED: focused 36.3 collection failed because `promise_projection` did not yet exist.
- GREEN: initial focused Stories 36.1–36.3 regression — 104 passed.
- REVIEW RED: reproduced ten deduplicated authority, seam-bypass, Unicode, spoiler, heading, order, and fixture-evidence findings, including a returned model missing `vows` entirely.
- REVIEW GREEN: focused Stories 36.1–36.3 regression — 122 passed.
- STATIC: focused Ruff — all checks passed.

### Completion Notes List

- Added exact-byte digest/path lineage validation and closed canonical-G0R / plan-dialogue authority recognition without inferred ratification.
- Added frozen resolution, request, result, and gate-receipt contracts plus all-or-nothing one-call Promise composition.
- Added exact mapping, Markdown structure, placeholder, numeral, contract-shape, and WARN-only declared-answer spoiler checks.
- Added Part-2 Q5, plan-dialogue, canonical thin, mixed, empty, spoof, and mutation evidence; no live/provider path was used.
- Review remediation revalidates all transformer output from its dumped shape, rejects bypassed nested values and Unicode line separators, and preserves propagation of transformer runtime failures.
- Final narrow remediation moves every returned-object attribute access and dump inside the contract-invalid boundary, so missing model fields degrade without swallowing transformer execution exceptions.
- Review remediation makes corrupt authority fail loud before absent-lineage disposition, enforces the exact legacy blank-Bloom proof shape, and validates all rows independent of ordering.
- Review remediation closes blank-context, stopword-only spoiler, reserved-label punctuation, and non-vacuous six-fixture coordinate/evidence boundaries.

### Mandatory Layered Review Record

- **Blind Hunter:** independent implementation review reported 4 findings across the transformer boundary (including the final missing-`vows` constructed-model bypass), exact plan-dialogue Bloom authority, and blank outer context. Amelia reproduced and remediated every witness. Final closure re-review PASS: missing fields degrade as `promise_transformer_contract_invalid`, transformer runtime exceptions still propagate, 37/37 focused tests.
- **Edge Case Hunter:** independent branch/boundary review reported 4 findings: malformed-authority precedence, stopword-only spoiler safety, punctuated reserved-label injection, and Unicode line/paragraph separators. Amelia remediated all four. Closure re-review PASS with 37/37 focused tests and no adjacent regression.
- **Acceptance Auditor:** independent AC1–AC10 trace reported 3 findings: order-dependent fail-loud row validation, non-exact legacy Bloom proof, and vacuous fixture/source-coordinate evidence. The Bloom item overlaps Blind review; the deduplicated patch set totals 10 findings. Amelia remediated all three. Closure re-review PASS with 122/122 combined 36.1–36.3 tests, Ruff clean, and real-source span/coordinate evidence.
- **Disposition:** 10/10 deduplicated findings resolved. No accepted deferrals. All three original reviewer layers re-inspected the remediated diff and returned PASS.

### File List

- `_bmad-output/implementation-artifacts/36-3-promise-transform-ratified-los.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/marcus/lesson_plan/prework_projection.py`
- `app/marcus/lesson_plan/promise_projection.py`
- `tests/fixtures/prework_36_3/canonical-thin.json`
- `tests/fixtures/prework_36_3/empty.json`
- `tests/fixtures/prework_36_3/part2-ratified-success.json`
- `tests/fixtures/prework_36_3/plan-dialogue-proof.json`
- `tests/fixtures/prework_36_3/spoof-malformed-boundaries.json`
- `tests/fixtures/prework_36_3/unratified-mixed.json`
- `tests/unit/marcus/lesson_plan/test_prework_projection_36_1.py`
- `tests/unit/marcus/lesson_plan/test_prework_projection_36_3.py`

## Change Log

- 2026-07-13: Implemented Story 36.3 strict authority resolution and pure Promise composition; moved to review.
- 2026-07-13: Addressed mandatory code-review findings — 10 deduplicated items resolved; retained review status.
- 2026-07-13: All three closure re-reviews PASS; Cora/Audra closure PASS with O/I/A 0/0/0; final 122/122 combined tests + Ruff/diff-check green; marked done.
