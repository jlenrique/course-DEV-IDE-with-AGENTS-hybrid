---
baseline_commit: 6b64ef06
---

# Story 37.3: Check on Learning retrieval and grounded answer keys

Status: done

## Story

As the learner,
I want an active-recall self-check that tests every ability the presentation promised,
so that the Preview Promise becomes source-grounded proof rather than a rereading exercise or fabricated answer key.

## Dependency Position

`38.0 -> 38.3b -> {Epic 36, 37.1, 37.2a, 37.3, 37.4} -> 38.3a`

Stories 38.0, 38.3b, Epic 36, 37.1, and 37.2a are done. Story 37.3 is a writer-tranche sibling with no Ask-A, Deep Dive, research, render, persistence, or orchestration dependency. It must close before 38.3a.

## Acceptance Criteria

1. **Strict M3-safe Check contracts**
   - Add `app/marcus/lesson_plan/check_on_learning_projection.py` with strict, frozen, extra-forbid, JSON-safe models for source spans, ability-authorized source claims, request authority, atomic answer claims, retrieval items, writer candidate, inspectable gate receipt, and aggregate result.
   - Reject blank/coerced IDs/text/refs, duplicate IDs/refs, unknown literals, structurally invalid authority, contradictory status/payload/loss/marker states, and extra fields.
   - Authored candidates/results require nonempty items and answers, exact reconciliation, passing gate, and no losses/marker. Degraded/unavailable results expose no questions or keys and carry one stable typed loss/marker.
   - Schema, exact model dumps, JSON round trips, frozen assignment, and constructed-model revalidation are pinned.

2. **Authored Story-36.3 Promise is the only ability authority**
   - Request consumes and independently revalidates a structurally valid `PromiseProjectionResult`; ordered abilities derive only from `PromiseVow.objective_id` and text. Do not accept a parallel caller-supplied ability list or infer abilities from wording. Structurally valid degraded/unavailable Promise results remain constructible so the adapter can return typed honesty.
   - Authored eligibility requires Promise status `authored`, empty Promise gate failures, nonempty unique vows, retained nonblank authority refs aligned 1:1 with vows, and exact vow order. Promise unavailable pre-gates to typed unavailable; Promise degraded pre-gates to typed degraded; neither invokes the writer.
   - Trust boundary: a strictly revalidated `PromiseProjectionResult` with authored projection, empty failures, unique ordered vows, and aligned nonblank authority refs is the declared upstream authority. Constructor provenance authenticity is not proven by the current 36.3 contract and remains an explicit upstream residual/operator WARN; this story does not edit or rerun 36.3 authority resolution.
   - Non-authored/unproven Promise authority cannot author a Check. The pure projector does not rerun ratification or read `ratified-los.json`, `run.json`, or the filesystem.
   - Promise-to-proof is exact coverage: every declared vow has one or more items; every item targets exactly one declared ability; no unknown ability is credited. First occurrence/grouping follows Promise order; multiple distinct items per ability are allowed.

3. **Ability-authorized source authority precedes the writer**
   - Request carries ordered source spans and atomic source claims. Each source claim has a stable ID/text, exact source-span refs, and one or more declared `ability_refs` chosen upstream—not by the writer.
   - Unknown/duplicate span, claim, or ability refs fail request validation. Structurally valid empty/partial source authority remains representable for adequacy pre-gating: empty source returns typed unavailable; a promised ability with no permitted source claim returns typed degraded naming the exact missing ability IDs; neither invokes the writer.
   - This declared join prevents an answer grounded for ability B from falsely satisfying ability A. The gate exposes declared/covered/missing ability IDs and unknown claim/span/ability IDs in authority order.
   - Typed traces prove coverage of the declared source-bound answer inventory; they do not prove universal semantic correctness. Conservative false negatives and full semantic ability relevance remain operator WARN.

4. **Operational retrieval—not reread**
   - Every authored item has the closed posture `free_response_from_memory`; prompts and expected answers are structurally separate.
   - Closed v1 retrieval proxy: prompts have no answer/options/hint fields, enumerated-choice scaffold, worked-answer marker, transcript scaffold, slide/deck deixis, or instructions to reread/review/look above/consult the text.
   - A normalized complete expected answer or complete traced source claim copied into the prompt fails. Short ability terms and common vocabulary may appear; broader partial/paraphrase leakage and pedagogical quality remain an explicit operator WARN rather than a falsely complete semantic gate.
   - Question prompts are single safe learner-facing units; reject heading/blockquote/list-answer/newline injection and answer-key disclosure markers.

5. **Source-grounded expected answers**
   - Each item answer is deterministic composition of one or more atomic answer claims. Each answer claim traces to exactly one declared source claim and its exact source-span set; that source claim must authorize the item's target ability.
   - Unknown refs, span mismatch, ability-permission mismatch, hidden answer prose, and answer/claim composition divergence fail closed with inspectable diagnostics.
   - Ordered quantity fidelity is FAIL-mode per atomic answer claim, covering signs including U+2212, leading decimals, percentages, ranges, scientific notation, word numerals/ordinals, and complete simple/compound/superscript units. Bounded negation fidelity is also atomic FAIL-mode.
   - Full semantic paraphrase correctness remains an operator spot-check WARN; the writer may not use model priors, substitute an unrelated sourced fact, or emit a pending/generic answer as authored.

6. **All-or-nothing adequacy honesty**
   - If any promised ability lacks an item or legitimate grounded answer, the aggregate returns typed degraded/unavailable honesty with an empty learner payload—never a partial instrument presented as complete.
   - Empty source authority returns typed unavailable; partial per-vow source authority returns typed degraded with exact missing ability IDs. No items, invalid traces, or unusable answers cannot yield authored output. Pre-gate inadequacy carries no partial learner payload and invokes the writer zero times.
   - Stable loss codes distinguish unavailable writer/source/Promise authority, missing ability proof, reference validation, and gate failure.

7. **Dedicated one-call writer seam and anti-forgery aggregate**
   - Define `CheckOnLearningWriter(request) -> CheckOnLearningWriterCandidate` and a deterministic unavailable offline stub with no semantic/model work.
   - The pure adapter strictly revalidates request, then invokes the writer exactly once **iff** structural and adequacy pre-gates pass. It invokes zero times for malformed, unavailable/degraded Promise, empty source, or incomplete per-vow grounding, and never more than once. After invocation it revalidates the candidate, independently computes the gate, and follows a pinned propagate-writer-exception policy. Wrong return types fail closed.
   - Following hardened 37.2a, aggregate results embed typed authority and `candidate_snapshot: CheckOnLearningWriterCandidate | None`. The snapshot is `None` iff the eligibility pre-gate stops before writer invocation, paired with a canonical typed pre-gate disposition/loss and no-candidate digest convention. Eligible executions require a candidate snapshot and canonical candidate digest. Aggregate validation reruns authority adequacy, enforces snapshot absence/presence, recomputes applicable digests, reruns the candidate gate only when a snapshot exists, requires receipt equality, and reconciles authored/non-authored payload disposition.
   - Forged candidate presence on a pre-gate path and forged candidate absence on an eligible execution both fail validation.
   - Fully self-consistent forged PASS receipts/results with unsupported prompts/answers must fail unless they genuinely pass against the embedded valid authority.

8. **Review compatibility and ownership fences**
   - Evolve `review_projection.py` only to import/re-export the dedicated Check types under collision-free names while preserving Story 37.1's legacy generic `CheckWriter`, offline stub, pending `CheckOnLearningBeat`, exact five-beat frame, and Markdown bytes.
   - Do not activate Check content in `ReviewBrief`; Story 37.5 owns persistence, composition, Markdown/DOCX, golden, answer-key disclosure order, and terminal integration.
   - No dependency on `DeepDiveSkeletonResult`, Ask-A/B packets, research, citations/References, glossary, trends, learner responses, run/global/filesystem state, provider/model config, orchestrator, terminal producer, or renderer.
   - Do not edit Promise/Deep-Dive production modules, `prework_artifact.py`, workbook producer/wiring, runner, manifest/graph, `_act.py`, quiz/enrichment/collateral contracts, or render code.

9. **Gate taxonomy and evidence**

   | Gate | Disposition | Witness | Owner |
   |---|---|---|---|
   | Authored Promise authority and retained refs | FAIL-to-author | automated | 37.3 |
   | Exact Promise ability coverage/order/mapping | FAIL | automated mutations | 37.3 |
   | Produce-from-memory structure/no choices/reread scaffold | FAIL | automated | 37.3 |
   | Prompt contains complete answer/source passage | FAIL | automated | 37.3 |
   | Unknown claim/span/ability or trace mismatch | FAIL | automated | 37.3 |
   | Answer prose/atomic-claim composition | FAIL | automated | 37.3 |
   | Atomic numeric/unit/range/scientific/negation fidelity | FAIL | automated | 37.3 |
   | Missing grounded proof for any ability | DEGRADE, empty payload | automated | 37.3 |
   | Full semantic answer correctness/ability relevance/subtle leakage | WARN | operator spot-check | 37.3 |
   | Model/research/runtime/global-state independence | FAIL | shape/import guards | 37.3 |
   | Review render/disclosure/DOCX/golden | NOT OWNED | downstream integrated evidence | 37.5 |

10. **Focused verification**
   - Add structured Part-2-style request/candidate fixtures using real authored Promise-result shape plus a semantic assertion manifest. Semantic prompts/answers are structural/gate-pinned, not byte-goldened; offline stub is deterministic.
   - Parameterized mutations remove every promised ability individually; cover unknown/duplicate/reordered ability/item IDs, unknown claim/span, wrong span set, ability-permission mismatch, answer/prose divergence, complete-answer/source-copy leakage, reread/choice/hint injection, and all numeric/negation cases.
   - Test non-authored/constructed Promise, empty/thin source, wrong writer return, constructed request/candidate/result, forged receipt/result, conditional call counts (one for eligible authority; zero for non-authored Promise, empty source, and missing-vow grounding), exception propagation, offline determinism, multi-item-per-vow, shared source explicitly authorized for multiple vows, orphan source behavior, and Unicode/newline boundaries.
   - Positive reworded prompts/answers pass through declared traces without copying source prose into the prompt; every vow is covered and every answer trace resolves exactly.
   - Reuse the already-landed 36.2 Part-4/skill-build/boundary-classifier fixtures as dependency evidence for source adequacy; Story 37.5 owns integrated Part-2/Part-4/skill-build Review fixtures and Markdown/DOCX golden proof. Story 37.3 must not silently claim those integrated A9 obligations from its Part-2 contract fixture alone.
   - Run focused Story 37.3 tests plus complete Story 37.1, 37.2a, and 36.3 Promise regressions, the named 36.2 adequacy/classifier fixture tests, and neutral workbook-band/topology regression. Ruff and `git diff --check` pass.
   - No paid/live run is required: this story owns contract/writer/gate behavior only.

## Tasks / Subtasks

- [x] Define strict Promise/source authority, retrieval item/answer, candidate, receipt, and aggregate contracts (AC: 1-3, 5-7)
- [x] Implement Promise-to-proof, retrieval, answer grounding/fidelity, adequacy, and diagnostic gates (AC: 2-6, 9)
- [x] Implement dedicated writer, deterministic stub, one-call adapter, digest/snapshot binding, and aggregate gate replay (AC: 7)
- [x] Preserve/re-export Story 37.1 Check compatibility without activating Review content (AC: 8)
- [x] Add Part-2-style fixtures and exhaustive positive/mutation/boundary tests (AC: 1-10)
- [x] Run focused/dependency regressions plus Ruff/diff-check (AC: 10)
- [x] Complete independent Blind, Edge, and Acceptance review; remediate findings and obtain exact-current closure before `done` (AC: 9-10)

### Review Findings

- [x] [Review][Patch] Recursively revalidate constructed source-span, source-claim, answer-claim, item, Promise, and candidate children at every public aggregate boundary [app/marcus/lesson_plan/check_on_learning_projection.py:99]
- [x] [Review][Patch] Reject all Unicode line separators/control newlines and Unicode bullet/list injection in single-unit prompts and stable refs [app/marcus/lesson_plan/check_on_learning_projection.py:73]
- [x] [Review][Patch] Close retrieval-scaffold bypasses for reread/refer-back/consult-text, transcript/worked-example, numeric/yes-no/generic choose-one options, and select/pick forms [app/marcus/lesson_plan/check_on_learning_projection.py:473]
- [x] [Review][Patch] Reject complete short expected answers, complete traced source claims, and complete traced source-span copies in prompts while allowing ordinary shared ability vocabulary [app/marcus/lesson_plan/check_on_learning_projection.py:521]
- [x] [Review][Patch] Replace permissive quantity parsing with ordered witnesses using a closed unit lexicon; cover unsupported ordinals, word-number units, spaced/compound/superscript/SI-symbol units, and avoid treating ordinary following words as units [app/marcus/lesson_plan/check_on_learning_projection.py:404]
- [x] [Review][Patch] Normalize contracted negators and bind bounded negation witnesses to their atomic clause/proposition so relocation cannot preserve a false pass [app/marcus/lesson_plan/check_on_learning_projection.py:471]
- [x] [Review][Patch] Reject normalized generic/pending/unknown answer phrase families, not only exact placeholder literals [app/marcus/lesson_plan/check_on_learning_projection.py:631]
- [x] [Review][Patch] Treat exact answer source-span traces as sets with deterministic diagnostic order, not caller tuple order [app/marcus/lesson_plan/check_on_learning_projection.py:655]
- [x] [Review][Patch] Reject all unsafe Unicode control/format characters, raw HTML block/heading tags, and leading Unicode symbol/punctuation list markers in learner-facing single units [app/marcus/lesson_plan/check_on_learning_projection.py:65]
- [x] [Review][Patch] Make retrieval-scaffold detection syntax-specific: close inline numeric/yes-no/between/which-is-correct and answer-disclosure forms while allowing domain words such as choose, options, and transcript in genuine open questions [app/marcus/lesson_plan/check_on_learning_projection.py:529]
- [x] [Review][Patch] Make complete-copy leakage token-boundary aware for short claims/answers/spans so `AI` does not match inside `explain`, while exact one-token answers still fail [app/marcus/lesson_plan/check_on_learning_projection.py:628]
- [x] [Review][Patch] Replace the incomplete hard-coded unit universe with strict source-declared case-sensitive unit tokens used by quantity witnesses; cover mcg/ng/MB/GB/mW/MW/textual ranges/digit ordinals without treating prose words as units [app/marcus/lesson_plan/check_on_learning_projection.py:497]
- [x] [Review][Patch] Bind bounded negation to clause and relative token-position/occurrence so same-clause relocation fails while same-position lexical paraphrase can pass; normalize avoid/cannot/contractions [app/marcus/lesson_plan/check_on_learning_projection.py:598]
- [x] [Review][Patch] Expand generic-answer sentinels to TBA/N-A/indeterminate/unknown-response phrase families [app/marcus/lesson_plan/check_on_learning_projection.py:642]
- [x] [Review][Patch] Reject unsafe controls and every raw HTML tag in prompts and learner-facing answer claims, including script/iframe/details/aside forms [app/marcus/lesson_plan/check_on_learning_projection.py:153]
- [x] [Review][Patch] Close remaining retrieval syntax for embedded numeric labels, conditional yes/no, decide-between/pick-best, listen/study transcript/worked-example, and answer/solution/correct-response disclosure separators [app/marcus/lesson_plan/check_on_learning_projection.py:530]
- [x] [Review][Patch] Bind negation witnesses to exact relative token occurrence plus bounded neighboring scope tokens so same-bucket relocation/swap fails [app/marcus/lesson_plan/check_on_learning_projection.py:631]
- [x] [Review][Patch] Canonicalize equivalent textual/dash range connectors and case-insensitive digit ordinal suffixes while preserving changed endpoints/units as failures [app/marcus/lesson_plan/check_on_learning_projection.py:509]
- [x] [Review][Patch] Make complete-copy leakage collapse punctuation-separated acronyms before token-boundary comparison [app/marcus/lesson_plan/check_on_learning_projection.py:660]
- [x] [Review][Patch] Anchor generic-answer sentinel families to the whole normalized answer; include no-response/none/not-applicable/don't-know/unavailable/no-idea/TBC while allowing substantive uses of pending/unknown [app/marcus/lesson_plan/check_on_learning_projection.py:683]
- [x] [Review][Patch] Make consult/review/reread/transcript/worked-example and decide-between detection modifier/preamble tolerant rather than start-anchored or exact-determiner dependent [app/marcus/lesson_plan/check_on_learning_projection.py:527]
- [x] [Review][Patch] Recognize both yes/no orders, supplied categorical alternatives, and full numeric/alphabetic enumerator grammar including `(1)`, `1:`, `A:`, and labels beyond A-D [app/marcus/lesson_plan/check_on_learning_projection.py:541]
- [x] [Review][Patch] Expand disclosure markers to answer/solution/response/key/answer-key with colon, dash, equals, or copular `is` forms [app/marcus/lesson_plan/check_on_learning_projection.py:553]
- [x] [Review][Patch] Reject HTML comments/declarations as well as ordinary raw tags [app/marcus/lesson_plan/check_on_learning_projection.py:92]
- [x] [Review][Patch] Canonicalize equivalent range connectors and shared/repeated declared-unit placement into one ordered range witness [app/marcus/lesson_plan/check_on_learning_projection.py:590]
- [x] [Review][Patch] Reject punctuation-only answers and complete whole-answer NIL/not-known/not-enough-data/no-information/not-sure/undetermined sentinel families [app/marcus/lesson_plan/check_on_learning_projection.py:733]
- [x] [Review][Patch] Replace the open-ended prompt blacklist with a closed free-response grammar: optional `From memory` preamble plus approved production/question stems; reject every other consult/choice/hint/disclosure stem by construction while retaining structural option/enumerator guards [app/marcus/lesson_plan/check_on_learning_projection.py:527]
- [x] [Review][Patch] Canonicalize spaced ASCII-hyphen digit and word-number ranges before generic sign/minus normalization [app/marcus/lesson_plan/check_on_learning_projection.py:645]
- [x] [Review][Patch] Reject supplied alternatives, binary yes/no, whether/or, and categorical slash forms across every approved production while preserving ordinary prose such as `one or more` [app/marcus/lesson_plan/check_on_learning_projection.py:542]
- [x] [Review][Patch] Reject source-consultation clauses embedded after approved stems, including using/reviewing/consulting/referring/according-to/based-on forms [app/marcus/lesson_plan/check_on_learning_projection.py:594]
- [x] [Review][Patch] Detect hint/answer/solution/response/key disclosure headers after semicolon, colon, dash, sentence boundary, or mid-production separator [app/marcus/lesson_plan/check_on_learning_projection.py:622]
- [x] [Review][Patch] Reject Unicode circled-number enumerators and embedded Unicode bullets as supplied enumeration [app/marcus/lesson_plan/check_on_learning_projection.py:650]
- [x] [Review][Patch] Canonicalize signed and leading-decimal ranges across spaced/unspaced ASCII and Unicode hyphen connectors before sign normalization [app/marcus/lesson_plan/check_on_learning_projection.py:715]
- [x] [Review][Patch] Expand whole-answer sentinel closure to `not available` and equivalent answer/response/information/data-unavailable forms [app/marcus/lesson_plan/check_on_learning_projection.py:834]
- [x] [Review][Patch] Reject standalone versus/vs/vs-dot and pipe supplied alternatives while preserving numeric and word-number `or more` quantifier prose [app/marcus/lesson_plan/check_on_learning_projection.py:552]
- [x] [Review][Patch] Reject connector-shaped embedded source consultation, including by/while reading, with-reference/source, drawing-from, guided-by, and shown-in forms [app/marcus/lesson_plan/check_on_learning_projection.py:616]
- [x] [Review][Patch] Reject copular disclosure headers after commas and conjunctions as well as punctuation separators [app/marcus/lesson_plan/check_on_learning_projection.py:648]
- [x] [Review][Patch] Detect enclosed/dingbat/alphanumeric Unicode enumerators and paired embedded arrows/bullets structurally while preserving ordinary single-symbol prose [app/marcus/lesson_plan/check_on_learning_projection.py:681]
- [x] [Review][Patch] Canonicalize unspaced ASCII-hyphen word-number ranges without converting compound numbers such as `twenty-one` into ranges [app/marcus/lesson_plan/check_on_learning_projection.py:778]
- [x] [Review][Patch] Expand whole-answer sentinel closure to modifier-before-unavailable forms such as currently/temporarily/presently unavailable [app/marcus/lesson_plan/check_on_learning_projection.py:883]
- [x] [Review][Patch] Preserve equivalent compound ordinal and cardinal hyphen/space forms while retaining unspaced word-range parsing [app/marcus/lesson_plan/check_on_learning_projection.py:775]
- [x] [Review][Patch] Reject repeated standalone punctuation/symbol enumerators by token boundary and Unicode category while preserving ordinary punctuation, emphasis, and simple math [app/marcus/lesson_plan/check_on_learning_projection.py:675]
- [x] [Review][Patch] Preserve recognized fraction/scale-number compounds such as `one-half` and `one-hundredth` across hyphen/space forms without weakening word ranges or declared-unit parsing [app/marcus/lesson_plan/check_on_learning_projection.py:792]

### Review Triage Notes

- 2026-07-13 round 9: rejection of parenthesized symbolic math such as `(2) * (3) *
  (4)` is an intentionally permitted conservative retrieval false-negative/WARN, not an
  AC5 numeric-fidelity defect. The repeated-symbol guard remains unchanged; no patch was
  authorized or applied for that form.

## Dev Notes

### Authorized scope

- NEW `app/marcus/lesson_plan/check_on_learning_projection.py`
- UPDATE `app/marcus/lesson_plan/review_projection.py` only for collision-free dedicated Check import/re-export
- NEW `tests/unit/marcus/lesson_plan/test_check_on_learning_projection_37_3.py`
- NEW structured fixtures under `tests/fixtures/check_on_learning_37_3/`
- UPDATE Story 37.1 compatibility tests only if needed to prove unchanged bytes/API
- This story file and sprint ledger

No Promise/Deep-Dive implementation, persistence, orchestrator, graph, runner, terminal, workbook producer, research, quiz/collateral, glossary/trends, or render edits.

### Contract guidance

- Recommended models: `CheckSourceSpan`, `CheckSourceClaim`, `CheckAnswerClaim`, `RetrievalCheckItem`, `CheckOnLearningRequest`, `CheckOnLearningWriterCandidate`, `CheckGateReceipt`, and `CheckOnLearningResult`.
- Consume the complete `PromiseProjectionResult` snapshot. For writer eligibility, `projection.status` must be authored, gate failures empty, vows unique/nonempty, and authority refs nonblank/aligned. Structurally valid degraded/unavailable snapshots remain accepted request authority and pre-gate to typed honesty without invoking the writer. Revalidate constructed snapshots before use.
- Source authority belongs in the request. A source claim's `ability_refs` is the pre-writer authorization join; the candidate may only select among it.
- Require exactly one source claim per atomic answer claim. Compose learner answer prose deterministically from those atomic claim texts, then fidelity-check each against its traced source claim.
- Reuse/publicly factor 37.2a numeric/negation helpers only if doing so preserves module boundaries and tests; otherwise implement a focused equivalent without importing private gates or changing 37.2a.
- Retrieval proxy should be conservative and inspectable. Closed posture metadata is necessary but not sufficient; lexical/structural leakage guards are required, while subtle semantics remain WARN.

### Reuse and non-reuse

- Reuse `PromiseProjectionResult`/`PromiseVow` as authority and the hardened snapshot/digest/gate-replay pattern from 37.2a.
- Reuse source-span/claim concepts, but define the Check-specific ability authorization join; do not depend on the Deep Dive aggregate.
- Do not reuse `Exercise`, `assert_exercise_fidelity`, `QuizSpec`, or generic worked-answer mappings as the semantic gate: they prove only shape/nonblank refs, not retrieval or grounded answer content.
- Preserve Story 37.1 pending Check shell and generic compatibility seam until 37.5.

### Previous-story intelligence

- Story 37.2a required three review rounds to close hidden prose, quantity, and forged-result bypasses. Start 37.3 with deterministic learner-prose composition, atomic fidelity, typed authority/candidate snapshots, and aggregate gate replay rather than retrofitting them.
- Story 37.1's exact singleton losses and deterministic frame bytes remain invariants.
- Story 36.3 established the Promise authority chain; do not weaken it to loose objective IDs or rerun ratification here.

### Git intelligence

- `6b64ef06` is the Story 37.3 baseline and closes 37.2a.
- `490158ec` closed the deterministic Review frame and generic writer seams.
- `dab32211` closed Promise transformation/authority behavior.

### Latest technical information

No external library/provider/API upgrade is introduced. Repository-local Pydantic/pytest projection patterns are authoritative; no web research is required.

### References

- `_bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md` sections 3, 6, 11, 13 (FR8, NFR1, NFR3)
- `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` Story 37.3 and A4/A9
- `_bmad-output/implementation-artifacts/36-3-promise-transform-ratified-los.md`
- `_bmad-output/implementation-artifacts/37-1-review-frame-bookend.md`
- `_bmad-output/implementation-artifacts/37-2a-deep-dive-skeleton.md`
- `app/marcus/lesson_plan/promise_projection.py`
- `app/marcus/lesson_plan/prework_projection.py`
- `app/marcus/lesson_plan/review_projection.py`
- `app/marcus/lesson_plan/deep_dive_projection.py`
- `app/marcus/lesson_plan/collateral_spec.py`
- `app/marcus/lesson_plan/workbook_producer.py`
- `docs/project-context.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex (fresh developer agent `/root/dev_37_3`)

### Debug Log References

- 2026-07-13: Loaded the complete amended story, BMAD dev-story workflow,
  manual customization fallback, and project context at baseline `6b64ef06`.
- 2026-07-13 RED: `.venv/Scripts/python.exe -m pytest
  tests/unit/marcus/lesson_plan/test_check_on_learning_projection_37_3.py -q`
  failed collection with `ModuleNotFoundError` for the not-yet-created dedicated
  projection module.
- 2026-07-13 GREEN/REFACTOR: focused Story 37.3 suite `71 passed`; complete
  prescribed 37.3 + 37.1 + 37.2a + 36.3 + 36.2 + workbook-band + lockstep
  dependency battery `265 passed`; neutral 38.3b topology battery `63 passed`.
- 2026-07-13 quality: Ruff passed for all changed Python files; `git diff
  --check` passed; explicit pipeline lockstep exited 0 at
  `reports/dev-coherence/2026-07-13-0440/check-pipeline-manifest-lockstep.PASS.yaml`.
- 2026-07-13 review RED: eight adversarial patch families were pinned as executable
  witnesses; the focused suite reported `39 failed, 76 passed` before remediation.
- 2026-07-13 review GREEN/REFACTOR: focused Story 37.3 suite `115 passed`;
  prescribed dependency battery `309 passed`; expanded neutral topology/lockstep
  battery `67 passed`; Ruff and scoped `git diff --check` passed.
- 2026-07-13 review round 2 RED: six additional adversarial patch families were
  pinned as executable witnesses; the focused suite reported `34 failed, 123 passed`.
- 2026-07-13 review round 2 GREEN/REFACTOR: focused Story 37.3 suite `157 passed`;
  prescribed dependency battery `351 passed`; expanded neutral topology/lockstep
  battery `67 passed`; Ruff and scoped `git diff --check` passed.
- 2026-07-13 review round 3 RED: six additional precision patch families were pinned
  as executable witnesses; the focused suite reported `32 failed, 162 passed`.
- 2026-07-13 review round 3 GREEN/REFACTOR: focused Story 37.3 suite `194 passed`;
  prescribed dependency battery `388 passed`; expanded neutral topology/lockstep
  battery `67 passed`; Ruff and scoped `git diff --check` passed.
- 2026-07-13 review round 4 RED: six table-driven grammar patch families were pinned
  with rejection and legitimate-open-question controls; focused suite reported
  `37 failed, 201 passed`.
- 2026-07-13 review round 4 GREEN/REFACTOR: focused Story 37.3 suite `238 passed`;
  prescribed dependency battery `432 passed`; expanded neutral topology/lockstep
  battery `67 passed`; Ruff and scoped `git diff --check` passed.
- 2026-07-13 review round 5 RED: the closed-grammar architecture and spaced-ASCII-
  hyphen range families were pinned with production, preamble, Roman/hyphen enumerator,
  embedded disclosure, and positive ability-language witnesses; focused suite reported
  `15 failed, 267 passed`.
- 2026-07-13 review round 5 GREEN/REFACTOR: focused Story 37.3 suite `284 passed`;
  prescribed dependency battery `478 passed`; expanded neutral topology/lockstep
  battery `67 passed`; Ruff and scoped `git diff --check` passed.
- 2026-07-13 remediation round 6 RED: six final Blind/Edge structural families were
  pinned with all approved-production alternatives, embedded source consultation,
  separator/mid-production disclosures, Unicode enumeration, signed/decimal ranges,
  sentinel equivalents, and positive prose controls; focused suite reported
  `30 failed, 296 passed`.
- 2026-07-13 remediation round 6 GREEN/REFACTOR: focused Story 37.3 suite `326 passed`;
  prescribed dependency battery `520 passed`; expanded neutral topology/lockstep
  battery `67 passed`; Ruff and scoped `git diff --check` passed.
- 2026-07-13 remediation round 7 RED: six exact-current Blind/Edge structural
  families were pinned with versus/vs/pipe choices, quantifier positives, expanded
  embedded consultation, comma/conjunction disclosures, Unicode structural enumeration,
  unspaced word ranges, and modifier-unavailable sentinels; focused suite reported
  `28 failed, 330 passed`.
- 2026-07-13 remediation round 7 GREEN/REFACTOR: focused Story 37.3 suite `358 passed`;
  prescribed dependency battery `552 passed`; expanded neutral topology/lockstep
  battery `67 passed`; Ruff and scoped `git diff --check` passed.
- 2026-07-13 remediation round 8 RED: compound-ordinal hyphen/space equivalence
  and repeated standalone-symbol enumeration were pinned with cardinal, range,
  punctuation, emphasis, and math controls; focused suite reported `6 failed, 363 passed`.
- 2026-07-13 remediation round 8 GREEN/REFACTOR: focused Story 37.3 suite `369 passed`;
  prescribed dependency battery `563 passed`; expanded neutral topology/lockstep
  battery `67 passed`; Ruff and scoped `git diff --check` passed.
- 2026-07-13 remediation round 9 RED: the one-half and one-hundredth hyphen/space
  equivalence family was pinned without changing repeated-symbol math behavior; focused
  suite reported `2 failed, 369 passed`.
- 2026-07-13 remediation round 9 GREEN/REFACTOR: focused Story 37.3 suite `371 passed`;
  prescribed dependency battery `565 passed`; expanded neutral topology/lockstep
  battery `67 passed`; Ruff and scoped `git diff --check` passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Implementation plan: establish strict authority/candidate/result contracts first,
  drive retrieval and grounding gates RED-first, then bind the one-call adapter and
  compatibility re-exports before the full mutation/regression battery.
- Added the pure M3-safe Check contract with strict/frozen/extra-forbid authority,
  source, atomic answer, item, candidate, receipt, and aggregate models; JSON/schema
  round trips and constructed-model revalidation are pinned.
- Promise authority is consumed as the complete Story 36.3 result. Authored eligibility
  requires aligned refs and exact vow order; degraded/unavailable Promise, empty source,
  and per-vow source gaps pre-gate honestly with zero writer calls and empty payloads.
- Added the dedicated one-call writer seam and deterministic offline stub. Aggregate
  results bind typed authority and optional candidate snapshots to canonical digests,
  replay pre-gates/gates on validation, and reject candidate-presence/absence and
  self-consistent forged-PASS bypasses.
- Retrieval gates enforce free-response-from-memory posture, safe single-unit prompts,
  no choice/hint/reread/transcript/slide/deck/answer-key scaffolds, and no complete
  expected-answer or traced-source copy. Subtle semantic leakage stays operator-WARN.
- Expected answers are deterministic atomic-claim composition. Each atomic claim traces
  exactly one ability-authorized source claim and exact span set; ordered quantity,
  complete unit/range/scientific notation, and bounded negation fidelity fail closed.
- Story 37.1 generic `CheckWriter`, pending Check beat, five-beat frame, and bytes remain
  unchanged while dedicated Check types/functions are collision-free re-exports only.
- Added real Promise-shaped Part-2 fixtures plus exhaustive authority, mutation,
  Unicode, numeric/unit, negation, call-count, exception, offline, multi-item/shared
  source, orphan-source, anti-forgery, compatibility, and M3 boundary tests. Integrated
  Review rendering/golden evidence remains explicitly owned by Story 37.5.
- Closed all eight recorded review patches with recursive child revalidation, complete
  line/list controls, expanded retrieval-proxy rejection, short/source-span leakage
  checks, closed-unit ordered numeric witnesses, clause-bound contraction-aware
  negation, generic-answer families, and order-insensitive exact trace sets with
  deterministic diagnostics.
- Closed all six second-round review patches: Unicode control/format and HTML/list
  injection rejection; syntax-specific retrieval scaffolds with open-question positive
  controls; token-boundary short-copy detection; strict source-declared case-sensitive
  quantity units with textual-range/digit-ordinal witnesses; clause/occurrence/relative-
  position negation parity with contraction/cannot/avoid normalization; and expanded
  generic sentinel families. Request fixture, semantic manifest, and schema assertions
  now pin the quantity-unit authority contract.
- Closed all six third-round review patches with universal learner-text control/raw-HTML
  rejection, the remaining syntax-specific retrieval/disclosure forms and positive
  domain controls, exact clause/occurrence/normalized-negator/scope-bound negation
  witnesses, canonical equivalent range connectors and case-insensitive digit ordinals,
  punctuation-collapsed acronym leakage checks, and whole-answer generic sentinels that
  preserve substantive pending/unknown prose.
- Closed all six fourth-round review patches with table-driven, modifier/preamble-
  tolerant source-scaffold grammar; both-order yes/no, categorical, and complete
  numeric/alphabetic enumerators; anchored disclosure-header families; HTML comment/
  declaration rejection; shared/repeated range-unit canonicalization; and punctuation-
  only plus expanded whole-answer sentinels. Legitimate open-question controls remain
  authored.
- Closed both fifth-round architectural patches: retrieval acceptance now starts from a
  closed free-response grammar (optional exact `From memory,` plus approved question or
  production stems), with supplied-alternative, choice, enumerator, disclosure, HTML,
  and leakage guards retained as structural defenses. Spaced ASCII-hyphen digit and
  word ranges canonicalize before sign/minus handling. Legitimate choose/transcript/
  options language remains authored when expressed through an approved production.
- Closed all six final Blind/Edge structural findings: approved stems now reject binary,
  whether/or, terminal-or, and categorical-slash supplied alternatives without blocking
  ordinary prose; embedded consultation and separator/mid-production disclosure clauses
  fail closed; circled numbers and embedded bullets are enumeration; signed and leading-
  decimal ranges canonicalize across ASCII/Unicode connectors; and equivalent whole-
  answer unavailable sentinels are unusable.
- Closed all six round-seven exact-current structural findings: versus/vs/pipe options
  fail while numeric/word quantifier idioms remain authored; connector-plus-source
  consultation and comma/conjunction disclosures fail; Unicode enumeration uses
  character-name/category structure with single-symbol positive controls; unspaced word
  ranges canonicalize without breaking compound numbers; and modifier-before-
  unavailable whole answers are unusable.
- Closed both round-eight exact-current Edge findings: compound cardinal and ordinal
  numbers canonicalize across hyphen/space forms without weakening word-range parsing;
  repeated standalone punctuation/symbol markers fail as structural enumeration while
  normal punctuation, inline emphasis, and simple numeric/variable math remain authored.
- Closed the round-nine AC5 finding: recognized fraction and scale-number compounds
  canonicalize across hyphen/space forms while ordinary word ranges, compound
  cardinal/ordinal behavior, and strict declared-unit parsing remain unchanged.
- Exact-current round-nine Blind, Edge, and Acceptance reviews all PASS. The root
  combined Story 37.3/37.1 verification reports `392 passed`; Ruff and
  `git diff --check` pass. Cora pre-closure classified the exact file set `warn` with
  `permit_closure: true`; Story 37.3 is therefore closed at `done`.

### File List

- `_bmad-output/implementation-artifacts/37-3-check-on-learning-retrieval.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/marcus/lesson_plan/check_on_learning_projection.py`
- `app/marcus/lesson_plan/review_projection.py`
- `tests/fixtures/check_on_learning_37_3/request.json`
- `tests/fixtures/check_on_learning_37_3/writer_candidate.json`
- `tests/fixtures/check_on_learning_37_3/semantic_manifest.json`
- `tests/unit/marcus/lesson_plan/test_check_on_learning_projection_37_3.py`

## Change Log

- 2026-07-13: Story created from FR8/NFR1 and current Promise/Review/Deep-Dive contracts; exact Promise coverage, retrieval proxy, ability-authorized grounding, anti-forgery aggregate, and ownership fences pinned; status ready-for-dev.
- 2026-07-13: Fresh developer implemented the strict Promise-to-proof retrieval and
  grounded-key contract RED-first, preserved Review compatibility, added exhaustive
  fixtures/tests, and passed prescribed dependency/topology/quality gates; status review
  pending independent Blind/Edge/Acceptance closure.
- 2026-07-13: Remediated all eight triaged review findings RED-first; focused,
  dependency, topology/lockstep, Ruff, and whitespace gates pass. Status remains review
  pending independent Blind/Edge/Acceptance closure.
- 2026-07-13: Remediated all six second-round review findings RED-first; focused,
  dependency, topology/lockstep, Ruff, and whitespace gates pass. Status remains review
  pending independent Blind/Edge/Acceptance closure.
- 2026-07-13: Remediated all six third-round review findings RED-first; focused,
  dependency, topology/lockstep, Ruff, and whitespace gates pass. Status remains review
  pending independent Blind/Edge/Acceptance closure.
- 2026-07-13: Remediated all six fourth-round review findings RED-first; focused,
  dependency, topology/lockstep, Ruff, and whitespace gates pass. Status remains review
  pending independent Blind/Edge/Acceptance closure.
- 2026-07-13: Remediated both fifth-round architectural review findings RED-first;
  focused, dependency, topology/lockstep, Ruff, and whitespace gates pass. Status
  remains review pending independent Blind/Edge/Acceptance closure.
- 2026-07-13: Remediated all six final Blind/Edge structural findings RED-first;
  focused, dependency, topology/lockstep, Ruff, and whitespace gates pass. Status
  remains review pending exact-current independent Acceptance closure.
- 2026-07-13: Remediated all six round-seven exact-current Blind/Edge findings
  RED-first; focused, dependency, topology/lockstep, Ruff, and whitespace gates pass.
  Status remains review pending exact-current independent Acceptance closure.
- 2026-07-13: Remediated both round-eight exact-current Edge findings RED-first;
  focused, dependency, topology/lockstep, Ruff, and whitespace gates pass. Status
  remains review pending exact-current independent Acceptance closure.
- 2026-07-13: Remediated the round-nine AC5 fraction/scale compound finding RED-first;
  documented the permitted conservative parenthesized-math false-negative; focused,
  dependency, topology/lockstep, Ruff, and whitespace gates pass.
- 2026-07-13: Exact-current Blind, Edge, and Acceptance reviews PASS after round nine;
  root combined verification reports `392 passed`, and Cora permits closure in warn
  mode. Status advanced to done.
