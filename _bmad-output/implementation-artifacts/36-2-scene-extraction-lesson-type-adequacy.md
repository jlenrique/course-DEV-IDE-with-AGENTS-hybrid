---
baseline_commit: 0f7bcaad2c3a38947bf43f2256ee1033b0431645
---

# Story 36.2: Scene extraction, lesson-type detection, and adequacy gate

Status: done

## Story

As the Marcus-SPOC workbook runtime,
I want a Scene reverse-engineered from traceable presentation evidence with lesson-type-aware archetype selection and adequacy gates,
so that pre-work surfaces friction the presentation can genuinely pay off and degrades honestly when sources are thin.

## Dependency Position

`38.0 -> 38.3b -> 36.1 -> {36.2 || 36.3} -> 36.4`

36.1 is done. 36.2 alone does not unlock 36.4; 36.3 must also close.

## Acceptance Criteria

1. **Normalized source extraction and SME-scenario priority**
   - Add strict normalized Scene-source types under `app/marcus/lesson_plan/` for stable seed id, text, seed-provenance `source_ref`, source kind, optional originating slide key, and SME-scenario flag. Seed provenance and payoff targets are separate fields and may never be substituted for one another.
   - Select only traceable candidates. Eligible SME-authored scenarios outrank composed narration/body friction.
   - Within the same priority class, select by normalized `(source_ref, seed_id)` lexical order; duplicate IDs or refs are invalid. If decisive lesson-type signals coexist, classification is ambiguous rather than resolved by priority.
   - Part-2 fixture selects Chapter-2 Q5’s recurring patient-transport-delay scenario ahead of generic narration candidates.
   - Malformed, blank, or unreferenced candidates are excluded with stable losses; no seed is inferred.

2. **Pure lesson-type classifier and archetype**
   - A separate pure classifier deterministically maps decisive evidence to exactly: `fresh_pain -> external_friction`, `bridge_identity -> introspective_threshold`, or `skill_build -> difficulty_practice`.
   - Part 2 pins fresh-pain; Part 4 pins bridge-identity; a dry procedural fixture pins skill-build.
   - Classifier input is a strict closed feature record of boolean `fresh_pain`, `bridge_identity`, and `skill_build` evidence plus traceable evidence refs. Exactly one true feature produces `status=decisive`, its named class/archetype, and confidence `1.0`; zero true features produces `insufficient`; two or three produces `ambiguous`. Non-decisive results carry no class/archetype and never use a tie-break.

3. **Closed SceneComposer seam**
   - Extend, never bypass, Story-36.1’s `SceneComposer(SceneComposeRequest) -> SceneBrief` contract.
   - After adequacy passes, build the strict request from the selected normalized seed + lesson type/archetype and invoke the injected composer exactly once.
   - Leashed prose is shape/gate-pinned, never byte-matched. Missing seed binding, reserved-heading injection, or archetype mismatch prevents authored status and produces honest degradation.

4. **Provenance gate**
   - An authored Scene must bind exactly to its selected seed ref, and that ref must resolve in the normalized inventory. `SceneBrief.source_refs` has cardinality one and equals `(selected_seed.source_ref,)`.
   - Missing, unresolvable, blank, or mismatched provenance is automated FAIL-to-author with a stable loss and honest marker. Never substitute another ref.

5. **Payoff proxy plus honest human judgment**
   - The request carries one-or-more `payoff_slide_keys`; each key must resolve in the separately declared payoff-slide inventory. The selected seed's source ref remains its Q5/slide/narration provenance and is never rewritten as a payoff ref. No resolved payoff target is automated FAIL-to-author.
   - Membership is explicitly a proxy, not semantic proof. Record a named WARN/operator spot-check that the deck genuinely pays off the surfaced friction.

6. **Light faithfulness check**
   - Compare composed Scene to the cited seed using a conservative normalized meaningful-token/anchor overlap check that retains numerals and negation.
   - Missing meaningful overlap, changed/contradicted numerals, or dropped/flipped negation prevents authored status and degrades with evidence.
   - Executable proxy: Unicode NFKC + lowercase + curly-punctuation/contraction normalization; tokenize alphanumerics; discard a committed English stopword set except negators; meaningful-token recall is `|scene ∩ seed| / |seed|` and must be `>= 0.30` with at least two shared meaningful tokens (or all tokens when the seed has fewer than two). Protected anchors are digit-form numerals and the negators `no`, `not`, `never`, `without`; every seed anchor must remain in the Scene. A different, added, or dropped digit-form numeral FAILs. Word-form↔digit equivalence (including `ten percent` vs `10%`) is deliberately unsupported and records WARN/operator review, not a guessed equivalence. Negation scope/polarity beyond preservation is WARN.
   - Mutation tests cover curly apostrophes/contractions, punctuation, faithful paraphrase, digit numeral addition/drop/change, negator drop, and word-form/digit uncertainty. Semantic faithfulness beyond the proxy remains WARN/operator seed-vs-Scene spot-check; never claim machine proof.

7. **Adequacy and honest source request**
   - Minimum substrate before composition: usable traceable seed, resolvable payoff binding, and decisive archetype.
   - Adequate -> compose. Thin/ambiguous but grounded -> degraded/no authored text with stable losses and source-request marker. Absent/invalid -> unavailable.
   - The top-level request carries closed `requested_coverage` (`single_slide` or `full_deck`) and `required_capabilities` (closed values including `scene` and `motion`); inventory declares `available_coverage` and `available_capabilities`. Missing coverage/capability degrades before composition with stable loss `scene_source_scope_unsupported`.
   - Part-4 fixture covers both supported slide-1 bridge seed and an unsupported `full_deck` + `motion` request that degrades with `scene_source_scope_unsupported`. No thin-source path fabricates a Scene.

8. **Four structured fixture families and A9 semantics**
   - Add dedicated normalized fixtures for Part-2 gem, Part-4 adequacy, dry skill-build, and ambiguous boundary. Each pins source inventory, candidates, payoff set, expected class/gates/losses.
   - Part-2 provenance points to actual Q5 plus relevant payoff slide(s), not only README.
   - Deterministic extraction/classification/gate receipts may be byte-pinned after canonical serialization. Composed Scene prose is never byte-goldened.

9. **Gate taxonomy**

   | Gate | Disposition | Witness |
   |---|---|---|
   | source-ref resolution and selected-seed binding | FAIL-to-author | automated |
   | SME-scenario-first selection | FAIL when eligible scenario ignored | automated fixture |
   | payoff-set membership | FAIL-to-author | automated |
   | actual payoff sufficiency | WARN | operator spot-check |
   | decisive class/archetype | FAIL for invalid; ambiguous degrades | automated + operator |
   | minimum adequacy | FAIL-to-author into degraded/unavailable | automated |
   | anchor/numeral/negation faithfulness | FAIL-to-author | automated mutation |
   | semantic faithfulness beyond proxy | WARN | operator spot-check |
   | exact leashed prose wording | no gate / never byte-match | structural gates only |

10. **M3/offline and focused evidence**
   - Production modules remain lesson-plan-layer only: no orchestrator, specialists, terminal/render, provider SDK, model config/client, or live call.
   - Injected spy and deterministic test composer prove request formation and single invocation without credentials.
   - Strict/extra/coercion/serialization pins and all 36.1 regressions remain green. Focused pytest, Ruff, and diff check pass. No paid/live run.

## Tasks / Subtasks

- [x] Define strict normalized Scene seed/inventory/classification/gate receipt types (AC: 1-2, 4-9)
- [x] Implement scenario-first selection and separate lesson-type classifier (AC: 1-2)
- [x] Implement adequacy, provenance, payoff proxy, and faithfulness gates (AC: 4-7, 9)
- [x] Extend request/Scene contracts additively and orchestrate one injected composer call (AC: 3, 10)
- [x] Add Part-2, Part-4, skill-build, and ambiguous normalized fixtures (AC: 8)
- [x] Add shape, selection, classifier, mutation, honest-degrade, seam, M3, and regression tests (AC: 1-10)
- [x] Run focused regression/static checks (AC: 10)

### Review Follow-ups (AI)

- [x] [HIGH] Preserve exact digit-form anchor multisets when word numerals coexist; add mixed/add/drop/repeat mutations.
- [x] [MED] Degrade wrong composer return types as `scene_composer_contract_invalid` while propagating runtime exceptions.
- [x] [MED] Enforce the exact decisive lesson-type-to-archetype mapping.
- [x] [MED] Compare negation protected anchors as exact multisets; reject added/repeated negators.
- [x] [MED] Tokenize Unicode alphanumerics after NFKC and cover non-ASCII prose.
- [x] [HIGH] Replace false Part-2/Part-4 coordinates and resolve them against real course-source files.
- [x] [MED] Add a connected raw-candidate normalization boundary with stable indexed rejection losses.
- [x] [MED] Require nonempty unique evidence refs on public classification receipts.

## Dev Notes

### Closed integration seam

Implement the production-facing pure API `compose_scene_projection(request: SceneProjectionRequest, composer: SceneComposer) -> SceneProjectionResult`. `SceneProjectionRequest` strictly owns the normalized seed inventory, candidate IDs, lesson-type evidence, payoff-slide inventory/targets, requested coverage/capabilities, and available coverage/capabilities. `SceneProjectionResult` strictly owns the resulting `SceneBrief`, selected seed ID/ref (or `None`), classification receipt, deterministic gate receipt (FAIL losses), and named WARN/operator checks. It is the sole 36.2 entry point that may invoke the injected composer and is the stable seam Story 36.4 will consume. Helpers may remain public for focused testing, but fixture success through disconnected helpers is insufficient.

The composer is called exactly once only after extraction, classification, provenance, payoff, and scope adequacy pass. Its output then passes binding, heading, archetype, and faithfulness checks. Any pre-compose FAIL yields degraded/unavailable without a call; any post-compose FAIL discards authored text and returns degraded with stable evidence. Receipts are deterministic and prose-free.

### Authorized scope

- `app/marcus/lesson_plan/prework_projection.py` additive contract changes if required
- New pure lesson-plan module(s), preferably `scene_extraction.py` and a structurally separate classifier helper
- `tests/unit/marcus/lesson_plan/test_prework_projection_36_2.py`
- `tests/fixtures/prework_36_2/` four normalized fixture families
- 36.1 fixture update only if additive schema requires it
- Story and sprint ledger

No orchestrator, `workbook_wiring`, terminal producer, manifest/runner, renderer/DOCX, Promise/LO logic, research packets, or review/deep-dive edits.

### Input shape guidance

Use a strict normalized `SceneSeed`/inventory contract rather than importing downstream `TranscriptSegment`. Suggested source kinds: slide narration, slide body, assessment scenario. Preserve stable source ref and slide key separately. Do not reuse `source_type.py`; it classifies artifact kinds, not lesson pedagogy.

Part-2 anchor: `course-content/courses/tejal-apc-c1-m1-p2-trends/assessments/chapter-2-knowledge-check.md`, Q5 attending physician/recurring transport delay. Payoff slides cover system friction/navigation and leadership response.

Part-4 anchor: `course-content/courses/tejal-c1m1-p4-assessments-bridge/`, with one closing bridge slide/storyboard and explicit source gaps. Its slide-1 champion/10%-90%/leadership identity evidence may support a narrow bridge Scene but not a fictitious full lecture substrate.

### Faithfulness posture

The lexical proxy is intentionally light. Preserve negation and numerals as protected anchors; compare normalized meaningful token sets with a conservative threshold and explicit diagnostics. Do not import specialist fidelity code or claim full semantic verification.

### Ownership fences

- 36.3 owns ratified LO loading and Promise/spoiler behavior.
- 36.4 owns `07W.1` registration, persisted contribution, terminal consumption, MD->DOCX, mode parity, and integrated Part-2 golden.
- Do not change the 38.3b neutral `workbook_brief_stub` identity/output yet.

### References

- Workbook redesign §§3–5 and §13
- Epic Story 36.2 + binding A9/A10
- Closed Story 36.1 and `prework_projection.py`
- Part-2 and Part-4 curated course-source directories above

## Dev Agent Record

### Agent Model Used

OpenAI Codex (GPT-5)

### Implementation Plan

- Extend the closed 36.1 Scene contracts additively, keeping legacy construction valid.
- Isolate the pure lesson-type truth table from normalized seed extraction and gate orchestration.
- Drive the projection seam through RED-first fixtures and mutation tests, then verify 36.1 regression and Ruff.

### Debug Log References

- RED: the new 36.2 suite failed at collection because the classifier module did not exist.
- GREEN: focused 36.1+36.2 suite: 64 passed in 1.37s.
- Scoped lesson-plan regression: 117 passed in 18.25s.
- Ruff: all checks passed for the changed production and 36.1/36.2 test modules.
- A repository-wide run was attempted, emitted no progress, and was terminated; it is not used as Story-36.2 evidence. The story-required focused/static evidence is green.
- Review RED: new return-type, mapping, anchor-multiset, Unicode, real-coordinate, raw-normalization, and receipt-integrity witnesses failed against the first implementation.
- Review GREEN: 36.2 suite 55 passed in 1.40s; combined 36.1+36.2 suite 85 passed in 1.28s; Ruff all checks passed.

### Completion Notes List

- Added frozen, extra-forbid normalized Scene seed, request, classification, gate-receipt, and result contracts with duplicate/ref/capability validation.
- Added a structurally separate no-tie-break classifier for fresh-pain, bridge-identity, skill-build, insufficient, and ambiguous evidence.
- Added SME-scenario-first extraction plus pre-compose adequacy, provenance, payoff-set, evidence-ref, coverage, and capability gates.
- Extended the 36.1 composer seam additively; adequate projections form one strict request, invoke the injected composer once, and post-gate binding, archetype, headings, and lexical faithfulness.
- Added Unicode/contraction normalization, overlap, exact digit-anchor, and negator checks with operator WARNs for semantic/payoff and word-digit uncertainty.
- Added four fixture families with expected receipts and deterministic/mutation/M3 tests. No live/provider/orchestrator/render/Promise work was introduced.
- Resolved all eight independent review findings: exact protected-anchor accounting, validated composer returns, exact receipt mapping/ref integrity, Unicode tokens, real source coordinates, and a connected loss-preserving raw extraction boundary.

### Mandatory Layered Review Record

- **Blind Hunter:** independent implementation review found 3 actionable defects (mixed numeral masking, invalid composer-return crash, forged class/archetype receipt). Amelia reproduced and remediated all 3; closure re-review PASS with 55/55 focused tests.
- **Edge Case Hunter:** independent branch/boundary review found 5 actionable edge cases (digit multiplicity, added negation, Unicode token loss, class/archetype mismatch, classification evidence-ref invariants). Amelia remediated all 5; closure re-review PASS with 55/55 focused tests.
- **Acceptance Auditor:** independent AC1–AC10 trace found 3 actionable gaps (mixed-number bypass, false/vacuous fixture coordinates, missing stable raw-candidate rejection losses). These overlap the deduplicated 8-finding patch set; Amelia remediated all 3. Closure re-review PASS with 85/85 combined 36.1+36.2 tests and Ruff clean.
- **Deduplicated remediation:** 8/8 findings resolved (2 HIGH, 6 MEDIUM). No accepted deferrals. All three original reviewers re-inspected the remediated diff and returned PASS.
- **Closure:** Cora preclosure CLEAN/WARN (no pipeline-trigger paths; lockstep correctly not required). Audra closure-artifact audit PASS; AC evidence, automated verification, layered review, and remediated review all present; O/I/A = 0/0/0.

### File List

- `_bmad-output/implementation-artifacts/36-2-scene-extraction-lesson-type-adequacy.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/marcus/lesson_plan/lesson_type_classifier.py`
- `app/marcus/lesson_plan/prework_projection.py`
- `app/marcus/lesson_plan/scene_extraction.py`
- `tests/fixtures/prework_36_1/prework_brief.json`
- `tests/fixtures/prework_36_2/ambiguous_boundary.expected.json`
- `tests/fixtures/prework_36_2/ambiguous_boundary.json`
- `tests/fixtures/prework_36_2/part2_gem.expected.json`
- `tests/fixtures/prework_36_2/part2_gem.json`
- `tests/fixtures/prework_36_2/part4_bridge.expected.json`
- `tests/fixtures/prework_36_2/part4_bridge.json`
- `tests/fixtures/prework_36_2/skill_build.expected.json`
- `tests/fixtures/prework_36_2/skill_build.json`
- `tests/unit/marcus/lesson_plan/test_prework_projection_36_2.py`

## Change Log

- 2026-07-13: Implemented Story 36.2 extraction, classification, adequacy, provenance/payoff, faithfulness, fixture, and closed-composer-seam contracts; moved to review.
- 2026-07-13: Resolved 8 independent review findings (2 HIGH, 6 MED); 36.2 55/55, combined 36.1+36.2 85/85, Ruff green; remains in review.
- 2026-07-13: All three closure re-reviews PASS; Cora/Audra closure clean; final 85/85 combined tests + Ruff/diff-check green; marked done.
