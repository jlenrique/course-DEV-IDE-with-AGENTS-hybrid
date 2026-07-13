---
baseline_commit: 36ada1ef
---

# Story 37.4: Closing Reflection shifted-question transfer

Status: done

## Story

As the learner,
I want a closing reflection that applies the lesson abilities to my own friction,
so that I measure capability gained rather than pain relieved.

## Dependency Position

`38.0 -> 38.3b -> {Epic 36, 37.1, 37.2a, 37.3, 37.4} -> 38.3a`

Stories 38.0 and 38.3b, Epic 36, and Stories 37.1, 37.2a, and 37.3 are done.
Story 37.4 is the final writer-tranche sibling before 38.3a. It has no Ask-A,
Ask-B, Deep Dive, Check, research, render, persistence, or orchestration dependency.

## Acceptance Criteria

1. **Strict M3-safe Closing Reflection contracts**
   - Add `app/marcus/lesson_plan/reflection_projection.py` with strict, frozen,
     extra-forbid, JSON-safe models for request authority, a structured writer
     candidate, an authored shifted-question prompt, inspectable gate receipt, and
     aggregate result.
   - Reject blank/coerced IDs, duplicate or unknown ability refs, unknown closed
     literals, contradictory status/payload/loss/marker states, extra fields, and
     invalid constructed-model instances. Pin schemas, exact dumps, JSON round trips,
     frozen assignment, and recursive public-boundary revalidation.
   - Authored results require eligible authority, exact ordered ability binding, a
     canonical prompt, a passing gate, no losses, and no unavailable marker.
     Degraded/unavailable results expose no learner prompt and carry one stable typed
     loss plus the canonical marker.

2. **The authored Story-36.3 Promise is the only ability authority**
   - Request consumes and independently revalidates a complete
     `PromiseProjectionResult`; it derives abilities only from ordered
     `PromiseVow.objective_id` and text. Do not accept a parallel caller-supplied
     ability list or infer abilities from prompt wording.
   - Eligibility requires Promise status `authored`, empty Promise gate failures,
     nonempty unique vows, and unique nonblank authority refs aligned 1:1 with vow
     order. A structurally valid degraded/unavailable Promise pre-gates to matching
     typed honesty and invokes the writer zero times.
   - This story trusts the strictly revalidated Promise snapshot as declared upstream
     authority; it does not rerun Story 36.3 ratification, read `ratified-los.json`,
     read `run.json`, or access the filesystem.
   - The candidate binds every declared ability exactly once in Promise order and maps
     each to one closed capability lens: `name`, `see`, or `do`. Missing, unknown,
     duplicate, partial, or reordered refs cannot author a Reflection. The lens mapping
     is the bounded semantic decision owned by the leashed writer; full pedagogical
     fitness of each mapping remains an operator WARN.

3. **Authentic pre-work callback authority, never the learner's value**
   - Request carries a complete strict `PreWorkBrief` snapshot or an explicit absent
     state that pre-gates to typed unavailable honesty with zero writer calls. The
     snapshot is recursively revalidated; its `friction_scale` must strictly equal the
     Epic-36 `FRICTION_SCALE`, including the `keep this ... for review` hook, and its
     embedded Promise must equal `PromiseProjectionResult.projection` exactly.
   - Compute a canonical digest from the embedded `PreWorkBrief`; never accept a
     caller-declared digest as proof. Canonical serialization is UTF-8 JSON from
     `model_dump(mode="json")` with sorted keys, compact separators, and
     `ensure_ascii=False`; digest with SHA-256 and prefix `sha256:`. Bind the
     result/receipt to that digest and recompute it during aggregate validation.
     Missing, forged, cross-prework-substituted, or Promise-mismatched lineage fails
     before writer invocation. This proves exact structural snapshot/callback binding,
     not historical provenance that the runtime previously emitted the snapshot.
   - The request/candidate/result models contain no rating, location, honest line,
     learner response/value, previous value, delta, cross-week state, or term-long
     portrait field. They never accept, infer, persist, echo, or serialize the learner's
     actual beat-2 ink.
   - The authored prompt refers to the learner's own earlier friction mark, location,
     and honest line through canonical callback language only. It does not claim the
     producer knows those values or that the content was generated per learner.

4. **Closed shifted-question composition measures capability, not cure**
   - The writer candidate carries only one ordered `(ability_ref, capability_lens)`
     binding per declared Promise vow; it cannot supply arbitrary learner-facing prose.
     The adapter deterministically derives an ordered learner-visible ability-cue tuple
     from the authoritative `(objective_id, vow_text)` plus the selected closed lens.
     Changing vow text with IDs held constant must change the cue payload; cue
     removal/reordering/text drift fails exact reconciliation.
   - Every cue exposes the exact authoritative vow text with its `name`/`see`/`do`
     lens. Reject unsafe vow display text containing raw HTML, controls, heading/list/
     blockquote/link/image injection, or multiline structure; do not silently rewrite
     authority. Legitimate Unicode and numerals remain allowed and are not treated as a
     re-rate merely because they occur in trusted ability copy.
   - Represent the final shifted question as three typed deterministic clauses and pin
     their canonical copy:
     1. `Return to the friction mark, location, and honest line you wrote before the presentation.`
     2. `With the lesson abilities above in mind, what can you now name, see, or do about that friction?`
     3. `Write one concrete move you will make this week.`
   - The learner-facing payload is the ordered ability cues plus those three clauses.
     It is structurally reconciled from revalidated authority and canonical constants;
     a candidate/result cannot forge alternate wording, headings, lists, HTML,
     controls, answer/scoring fields, extra questions, or extra move requests.
   - There is no 0-10 re-rate, rate-again, new-score, before/after delta, pain-drop,
     cure, friction-reduction, success-grade, answer-key, or evaluation affordance.
     Positive tests prove ordinary ability vows containing legitimate numerals remain
     valid because vow prose is displayed only in typed ability cues, never
     interpolated into the three canonical clauses.

5. **Dedicated bounded writer seam and deterministic offline stub**
   - Define a collision-free dedicated protocol such as
     `ClosingReflectionWriter(request) -> ReflectionWriterCandidate` and a deterministic
     unavailable offline stub. Preserve Story 37.1's generic `ReflectionWriter`,
     `ReviewWriterRequest`, and `offline_reflection_writer` public API unchanged.
   - The pure adapter strictly revalidates request authority, invokes the dedicated
     writer exactly once iff authored Promise and pre-work callback authority are eligible,
     strictly revalidates the exact return type, computes the gate independently, and
     follows a pinned propagate-writer-exception policy. It invokes zero times on every
     ineligible path and never more than once.
   - The writer maps every declared ability, in authority order, to exactly one closed
     `name`/`see`/`do` lens. That mapping changes the learner-visible cue payload and is
     the seam's only semantic choice. It cannot omit/reorder abilities, alter vow text,
     author the final clauses, grade the learner, or introduce model-prior prose.

6. **Anti-forgery aggregate and all-or-nothing honesty**
   - Aggregate results embed typed Promise and `PreWorkBrief` request authority and
     `candidate_snapshot: ReflectionWriterCandidate | None`, canonical authority and
     candidate digests, the recomputed pre-work digest, and an inspectable receipt.
     Snapshot presence is exact: `None`
     iff eligibility stops before writer invocation; eligible execution requires a
     candidate snapshot and candidate digest.
   - Aggregate validation recursively revalidates authority/candidate snapshots,
     recomputes digests and visible ability cues, reruns pre-gates and the pure gate,
     requires receipt equality, and reconciles authored/non-authored payload
     disposition. Fully self-consistent forged PASS results fail unless they genuinely
     pass against both embedded Promise and pre-work authority.
   - Missing Promise or pre-work callback authority returns typed unavailable; incomplete or
     invalid ability binding returns typed degraded. Neither may expose a partial
     prompt as complete. Stable losses distinguish Promise authority, pre-work callback
     authority, writer contract, ability binding, and gate failure.
   - When more than one condition is present, emit exactly one loss by this precedence:
     invalid/constructed request (fail closed before execution); non-authored Promise;
     absent pre-work; prework-Promise/callback mismatch; writer unavailable; wrong or
     invalid writer contract; ability/lens binding failure; generic gate failure.
     Promise `unavailable`/`degraded` status is preserved; absent pre-work is
     `unavailable`; all later invalidity is `degraded`.

7. **Preserve Review compatibility; activation belongs to Story 37.5**
   - Update `app/marcus/lesson_plan/review_projection.py` only for collision-free
     imports/re-exports of dedicated 37.4 types/functions.
   - Preserve Story 37.1's exact five-beat order, headings, watchwords, ownership,
     Bookend callback, generic writer seam, byte-golden Markdown, and
     `ClosingReflectionBeat(status="pending", prompt=None)` default.
   - Do not activate the authored prompt in `ReviewBrief`, render Markdown/DOCX, edit
     the terminal producer, or persist any Reflection artifact. Story 37.5 owns Review
     assembly/render/goldens and must render the ordered ability cues adjacent to the
     canonical clauses without altering their binding; Story 37.6 owns HIL/HAI
     encounter-label parity.

8. **No research, provider, runtime, graph, or global-state coupling**
   - Request/result shapes and imports contain no Deep Dive, Check, Ask-A/B,
     `ResearchPacket`, citations, glossary, trends, References, answer keys, model
     config/client/SDK, orchestrator, specialist, run directory, renderer, or
     filesystem dependency.
   - Do not edit `workbook_wiring.py`, `production_runner.py`, the pipeline manifest or
     graph, `prework_artifact.py`, terminal `_act.py`, or workbook producer/render code.
     Live writer instantiation/positioning remains orchestrator-owned at `07W.3`.
   - Import/AST guards prove M3 safety, no global reads, no provider/model calls, and no
     learner-state storage surface.

9. **Gate taxonomy and evidence**

   | Gate | Disposition | Witness | Owner |
   |---|---|---|---|
   | Strict contract/status/reference reconciliation | FAIL | automated | 37.4 |
   | Authored Promise authority + exact ordered ability binding | FAIL-to-author | automated mutations | 37.4 |
   | PreWorkBrief lineage/digest + canonical friction hook; no learner value | FAIL-to-author / unavailable when absent | automated substitutions | 37.4 |
   | Ordered visible vow/lens cue parity | FAIL | causal mutations | 37.4 |
   | Canonical name/see/do shifted question + exactly one move | FAIL | exact clause reconciliation | 37.4 |
   | No re-rate/cure/score/evaluation affordance | FAIL | canonical-template and negative shape tests | 37.4 |
   | Unsafe prompt/heading/HTML/control injection | FAIL | automated | 37.4 |
   | Full pedagogical relevance of the canonical transfer question | WARN | operator spot-check | 37.4 |
   | M3/model/global-state independence | FAIL | import/AST | 37.4 |
   | Review activation, MD/DOCX, golden, mode parity | NOT OWNED | downstream integration | 37.5 / 37.6 |

10. **Focused verification**
    - Add structured request/candidate/semantic-manifest fixtures under
      `tests/fixtures/reflection_37_4/`. The deterministic final prompt and offline stub
      are exact-pinned; authority/candidate/gate/result shapes and digests are pinned.
    - Mutation tests cover every Promise eligibility/state defect, missing/corrupt/
      substituted pre-work authority, prework digest mutation, prework-Promise mismatch,
      unknown/duplicate/missing/reordered ability ref, changed vow text with IDs held
      constant, cue removal/reordering/text drift, wrong writer return, constructed-model
      bypass, forged receipt/digest/snapshot/result, learner-state/parallel-ability
      fields, prompt injection, and all ownership fences.
    - Positive controls cover multiple abilities, Unicode-safe vow text, legitimate
      numerals and ordinary `rate`/`score` words in trusted vows, two distinct Promise
      sets producing distinct visible cues, deterministic frame repeatability, JSON
      round trips, exactly-one writer call, zero-call pre-gates, and strict exception
      propagation.
    - Run the focused 37.4 suite plus complete Story 37.1, Story 36.3 Promise, Story
      37.2a, and Story 37.3 regressions; run neutral workbook-band topology/manifest
      lockstep tests, Ruff, and `git diff --check`.
    - No paid/live run is required here. Integrated Review render and the final live
      Marcus-SPOC workbook witness belong to downstream stories and the overall goal.

## Tasks / Subtasks

- [x] Define strict Promise/pre-work authority, lens binding, visible cue, clause, receipt, and aggregate contracts (AC: 1-4, 6)
- [x] Implement pure eligibility, canonical shifted-question composition, binding, and anti-forgery gates (AC: 2-6)
- [x] Implement the dedicated one-call writer protocol and honest deterministic stub (AC: 5)
- [x] Preserve/re-export Story 37.1 compatibility without activating Review render (AC: 7-8)
- [x] Add fixtures and exhaustive positive/mutation/boundary tests (AC: 1-10)
- [x] Run focused/dependency/topology regressions plus Ruff/diff-check (AC: 10)
- [x] Complete independent Blind, Edge, and Acceptance review; remediate findings and obtain exact-current closure before `done` (AC: 9-10)

### Review Findings

- [x] [Review][Patch] Reject reference-style Markdown link and image injection in authoritative vow text [app/marcus/lesson_plan/reflection_projection.py:81]
- [x] [Review][Patch] Permit safe ZWJ/ZWNJ Unicode while continuing to reject controls and bidi formatting [app/marcus/lesson_plan/reflection_projection.py:88]
- [x] [Review][Patch] Reject duplicate ability cues when ShiftedQuestionPrompt is validated independently [app/marcus/lesson_plan/reflection_projection.py:239]
- [x] [Review][Patch] Make ReflectionGateReceipt reject impossible eligible failure states, empty candidate binding, and duplicate bound refs [app/marcus/lesson_plan/reflection_projection.py:336]
- [x] [Review][Patch] Enforce the writer protocol's exact ReflectionWriterCandidate return type rather than accepting subclasses [app/marcus/lesson_plan/reflection_projection.py:562]
- [x] [Review][Patch] Complete AC10 mutation coverage for unknown refs, pre-work digest, cue drift, forged receipt fields, and reference-style Markdown [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:203]
- [x] [Review][Patch] Reject every unescaped Markdown reference/link/image form, including short, numeric, non-ASCII, nested, and escaped-bracket labels [app/marcus/lesson_plan/reflection_projection.py:82]
- [x] [Review][Patch] Reconcile standalone pre-gate declared ability refs with Promise versus pre-work failure dispositions [app/marcus/lesson_plan/reflection_projection.py:350]
- [x] [Review][Patch] Reconcile standalone pre-work digest nullability with absent, mismatch, and eligible dispositions [app/marcus/lesson_plan/reflection_projection.py:350]
- [x] [Review][Patch] Add exact mutation witnesses for the second-round Markdown and pre-gate receipt state-space defects [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:241]
- [x] [Review][Patch] Reject CommonMark thematic-break injection for hyphen, asterisk, and underscore marker families [app/marcus/lesson_plan/reflection_projection.py:77]
- [x] [Review][Patch] Add full-request mutation witnesses for compact and spaced thematic-break forms [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:230]
- [x] [Review][Patch] Reject CommonMark setext-heading underline injection, including marker-only equals forms [app/marcus/lesson_plan/reflection_projection.py:77]
- [x] [Review][Patch] Require authoritative vow text to contain a visible non-format character while preserving in-word ZWJ/ZWNJ [app/marcus/lesson_plan/reflection_projection.py:94]
- [x] [Review][Patch] Reject incomplete CommonMark raw-HTML block openers that end after a recognized tag name [app/marcus/lesson_plan/reflection_projection.py:76]
- [x] [Review][Patch] Add contextual rendering and full-request mutations for setext, visually blank joiners, and incomplete raw-HTML openers [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:230]
- [x] [Review][Patch] Require at least one visible base character so standalone variation selectors and combining marks cannot author a blank cue [app/marcus/lesson_plan/reflection_projection.py:207]
- [x] [Review][Patch] Add full-request witnesses for default-ignorable variation selectors and combining-format marks plus attached-mark controls [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:380]
- [x] [Review][Patch] Exclude non-control Unicode filler letters and blank symbols from the visible-base predicate [app/marcus/lesson_plan/reflection_projection.py:207]
- [x] [Review][Patch] Permit Unicode tag characters only inside a structurally valid subdivision-flag emoji sequence [app/marcus/lesson_plan/reflection_projection.py:220]
- [x] [Review][Patch] Add full-request witnesses for Hangul fillers and Braille blank plus visible-content controls [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:380]
- [x] [Review][Patch] Add valid and malformed subdivision-flag emoji sequence boundary tests [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:494]
- [x] [Review][Patch] Replace the sample-only invisible-base denylist with the complete semantic blank/filler ranges required by the runtime Unicode database [app/marcus/lesson_plan/reflection_projection.py:207]
- [x] [Review][Patch] Restrict subdivision-flag tag payloads to lowercase ASCII tag letters and digits, rejecting TAG SPACE, punctuation, and uppercase [app/marcus/lesson_plan/reflection_projection.py:217]
- [x] [Review][Patch] Add full-request witnesses for ideographic, Egyptian-hieroglyph, and SignWriting blank-space characters [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:380]
- [x] [Review][Patch] Add malformed subdivision-tag payload tests for spaces, punctuation, uppercase, interruption, and termination boundaries [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:494]
- [x] [Review][Patch] Restrict invisible emoji tag exceptions to the pinned closed RGI subdivision-flag payloads rather than arbitrary hidden text [app/marcus/lesson_plan/reflection_projection.py:234]
- [x] [Review][Patch] Degrade a non-callable writer argument through the typed writer-contract-invalid path without attempting invocation [app/marcus/lesson_plan/reflection_projection.py:714]
- [x] [Review][Patch] Add full-request hidden-prose tag mutations and exact RGI subdivision-flag positive controls [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:494]
- [x] [Review][Patch] Add a non-callable writer boundary witness with typed loss and zero invocation [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Reject hostile nested model subclasses and recursively normalize exact gate and prompt base models before aggregate equality checks [app/marcus/lesson_plan/reflection_projection.py:702]
- [x] [Review][Patch] Apply exact owned-model type checks consistently to aggregate authority and candidate snapshots before replay [app/marcus/lesson_plan/reflection_projection.py:702]
- [x] [Review][Patch] Close rejected coroutine writer returns before typed contract degradation to avoid unawaited-coroutine warnings [app/marcus/lesson_plan/reflection_projection.py:816]
- [x] [Review][Patch] Add hostile equality/model-dump subclass, constructed nested-model, and coroutine-warning boundary witnesses [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Use trusted unbound serialization and replace aggregate nested fields with normalized exact copies so instance-level serializer shadowing cannot preserve forged state [app/marcus/lesson_plan/reflection_projection.py:715]
- [x] [Review][Patch] Exact-type and trusted-normalize Promise and PreWorkBrief snapshots before invoking any instance-dispatched method [app/marcus/lesson_plan/reflection_projection.py:351]
- [x] [Review][Patch] Exact-type and trusted-normalize nested ability focuses, cues, and clauses at standalone public model boundaries [app/marcus/lesson_plan/reflection_projection.py:412]
- [x] [Review][Patch] Cancel scheduled Task/Future returns from the synchronous writer seam before typed contract degradation [app/marcus/lesson_plan/reflection_projection.py:837]
- [x] [Review][Patch] Add exact-base instance serializer-shadow, nested hostile-model, normalized-storage, and scheduled-awaitable cleanup witnesses [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Serialize untrusted exact models through the expected class-owned Pydantic serializer so instance-shadowed serializer state cannot forge normalization [app/marcus/lesson_plan/reflection_projection.py:352]
- [x] [Review][Patch] Cancel Task/Future returns through trusted unbound asyncio methods and contain cleanup failures before typed degradation [app/marcus/lesson_plan/reflection_projection.py:873]
- [x] [Review][Patch] Add instance-level Pydantic serializer-shadow and Future/Task cancel-shadow/closed-loop cleanup witnesses [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Dispose an unstarted rejected Task bound to a closed event loop without pending-task or unawaited-coroutine diagnostics [app/marcus/lesson_plan/reflection_projection.py:863]
- [x] [Review][Patch] Add closed-loop pending Task destruction, logging, garbage-collection, and strict-warning witnesses [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Dispose rejected never-started Tasks on open but idle loops without requiring the caller to advance the foreign loop [app/marcus/lesson_plan/reflection_projection.py:864]
- [x] [Review][Patch] Suppress pending-task diagnostics only after the rejected Task coroutine is proven closed [app/marcus/lesson_plan/reflection_projection.py:884]
- [x] [Review][Patch] Preserve diagnostics when a rejected coroutine catches GeneratorExit and remains suspended [app/marcus/lesson_plan/reflection_projection.py:884]
- [x] [Review][Patch] Add open-idle-loop and GeneratorExit-resistant Task lifecycle witnesses under forced GC and strict warnings [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Do not close a rejected Task coroutine while its open event loop still owns a scheduled step; request trusted cancellation and let that loop finalize it [app/marcus/lesson_plan/reflection_projection.py:887]
- [x] [Review][Patch] Document the safe ownership distinction between closed-loop disposal and open-loop cancellation finalization [app/marcus/lesson_plan/reflection_projection.py:863]
- [x] [Review][Patch] Add an open-idle-loop resume witness proving later loop advancement yields cancellation with no RuntimeError or unretrieved exception [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Cancel a rejected Task's Future/Task waiter chain through trusted base methods before falling back to Task cancellation [app/marcus/lesson_plan/reflection_projection.py:887]
- [x] [Review][Patch] Add raising/side-effect Future-waiter subclass and nested Task-waiter cancellation witnesses [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Request cancellation on the owning rejected Task when its trusted-cancelled waiter is already terminal or returns false [app/marcus/lesson_plan/reflection_projection.py:898]
- [x] [Review][Patch] Ensure waiter-originated cancellation cannot silently clear the owning Task's cancellation request before its next suspension [app/marcus/lesson_plan/reflection_projection.py:898]
- [x] [Review][Patch] Add completed-but-unconsumed waiter and cancellation-catching coroutine lifecycle witnesses [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Exclude instance-level Future cancel shadows before permitting Task.cancel to dispatch through its waiter [app/marcus/lesson_plan/reflection_projection.py:890]
- [x] [Review][Patch] Schedule the next bounded owning-Task cancellation retry after every trusted cancellation until terminal or budget exhaustion [app/marcus/lesson_plan/reflection_projection.py:920]
- [x] [Review][Patch] Add inherited-base Future subclass with instance cancel shadow and zero-hook witness [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Add repeated cancellation-catching witness that consumes multiple retries and proves finite exhaustion behavior [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Schedule bounded owning-Task retries through the trusted thread-safe event-loop method across loop ownership boundaries [app/marcus/lesson_plan/reflection_projection.py:906]
- [x] [Review][Patch] Add a debug event loop running in another thread with cancellation-catching Task and clean bounded-retry witness [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Suppress trusted serializer mismatch warnings so strict recursive validation—not warning policy—controls typed writer-contract degradation [app/marcus/lesson_plan/reflection_projection.py:363]
- [x] [Review][Patch] Marshal standalone Future cancellation to its running owner loop while retaining trusted unbound base cancellation [app/marcus/lesson_plan/reflection_projection.py:1024]
- [x] [Review][Patch] Add warnings-as-errors constructed candidate with non-model focus witness [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Add standalone Future on a foreign debug-loop with awaiting Task wakeup and clean terminal-state witness [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]
- [x] [Review][Patch] Preflight exact nested graph types before trusted serialization so schema-shaped foreign models cannot be coerced into valid owned models [app/marcus/lesson_plan/reflection_projection.py:363]
- [x] [Review][Patch] Apply pre-serialization graph preflight at writer candidate and aggregate/request/prompt public normalization boundaries [app/marcus/lesson_plan/reflection_projection.py:363]
- [x] [Review][Patch] Add schema-shaped unrelated BaseModel substitutions under strict UserWarning for focuses, cues, clauses, and aggregate nested graphs [tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py:620]

## Dev Notes

### Authorized scope

- NEW `app/marcus/lesson_plan/reflection_projection.py`
- UPDATE `app/marcus/lesson_plan/review_projection.py` only for collision-free
  dedicated imports/re-exports
- NEW `tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py`
- NEW structured fixtures under `tests/fixtures/reflection_37_4/`
- UPDATE Story 37.1 tests only if needed to prove unchanged compatibility/bytes
- This story file and `_bmad-output/implementation-artifacts/sprint-status.yaml`

No pre-work artifact/persistence, Deep Dive, Check, research, Ask-A/B, citation,
References, glossary, trends, mode, orchestrator, graph, runner, terminal producer,
workbook render, provider, model-client, or global-state edits.

### Contract guidance

- Prefer dedicated names such as `ReflectionRequest`, `ReflectionAbilityFocus`,
  `ReflectionWriterCandidate`, `ReflectionAbilityCue`, `ShiftedQuestionPrompt`,
  `ReflectionGateReceipt`, `ReflectionResult`, and
  `ClosingReflectionWriter`; avoid collision with Story 37.1's generic
  `ReflectionWriter`.
- Treat the Promise and complete `PreWorkBrief` snapshots as embedded authority. Copy
  the recursive revalidation, snapshot/digest, receipt replay, and zero/one-call
  architecture already hardened in 37.2a/37.3; do not merely trust `isinstance`, a
  copied `FRICTION_SCALE`, or a caller-provided digest.
- One normative anti-forgery invariant governs every layer: canonicalize the embedded
  typed snapshots, recompute SHA-256 digests, rerun eligibility and the pure gate, and
  reconcile visible cues/clauses/receipt/status/payload from those snapshots. Repeated
  AC references describe witnesses of this same invariant, not separate algorithms.
- Keep all final clauses and vow text out of the writer candidate. The writer returns
  exact ordered ability refs plus one closed lens per ref; the adapter joins those refs
  to authoritative vow text and owns the frozen learner-facing clauses. This bounded
  semantic choice avoids both a ceremonial identity writer and an arbitrary-prose
  blacklist.
- Do not interpolate learner data into any output. Store visible lesson-level vow/lens
  cues as typed payload adjacent to, not spliced into, the fixed question clauses.
  Full pedagogical fitness of each lens mapping is WARN, not a falsely complete gate.
- Preserve all current 37.1 pending-shell behavior. Story 37.4 produces the dedicated
  authored contract only; 37.5 will replace the pending slot during assembly.

### Existing code to preserve

- `review_projection.py`: exact five-beat frame, generic Reflection protocol/stub,
  Bookend callback, pending Closing Reflection shell, and byte-golden renderer.
- `promise_projection.py`: `PromiseProjectionResult` is the upstream ability authority;
  do not rerun resolution or ratification.
- `prework_projection.py`: recursively revalidate the complete `PreWorkBrief`, reconcile
  its Promise to Story 36.3 authority, and verify `FRICTION_SCALE`; never add response
  fields.
- `deep_dive_projection.py` and `check_on_learning_projection.py`: reuse the hardened
  aggregate-validation architecture and collision-free re-export pattern, not their
  semantic gates.
- `workbook_wiring.py`: `07W.3` topology/stub remains untouched.

### Previous-story intelligence

- Story 37.3 required nine remediation rounds after arbitrary prompt prose created an
  open-ended structural grammar. The closed 37.4 candidate/template split is binding;
  do not reintroduce free learner-facing writer prose.
- Stories 37.2a and 37.3 both exposed forged/constructed snapshot and receipt paths.
  Embed exact typed authority/candidate snapshots, recompute digests, and rerun gates.
- Story 37.1's singleton loss and byte-golden frame are load-bearing compatibility
  contracts. New dedicated types must not alter its pending Reflection behavior.
- Deterministic shell bytes may be exact-goldened; semantic authority binding is
  structural/gate-pinned. The terminal leaf remains deterministic-consume/model-free.

### Git intelligence

- `490158ec` established the five-beat Review frame and generic writer seams.
- `6b64ef06` established the dedicated sibling-module/re-export pattern and hardened
  authority/candidate/gate binding.
- `36ada1ef` reinforced recursive revalidation, typed snapshots/digests, and the cost
  of open-ended learner-facing grammar.

### Latest technical information

No external library/provider/API upgrade is introduced. Repository-pinned Pydantic,
pytest, Ruff, and Python patterns are authoritative; web research is unnecessary for
this pure local contract/gate story.

### References

- `_bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md` sections 6, 10, 11, and 13 (FR10; NFR1-NFR8)
- `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` Story 37.4, A4, A7, A9, and ratified DAG/ownership decision
- `_bmad-output/implementation-artifacts/37-1-review-frame-bookend.md`
- `_bmad-output/implementation-artifacts/37-2a-deep-dive-skeleton.md`
- `_bmad-output/implementation-artifacts/37-3-check-on-learning-retrieval.md`
- `_bmad-output/implementation-artifacts/38-3b-graph-topology-band-orchestrator.md`
- `app/marcus/lesson_plan/review_projection.py`
- `app/marcus/lesson_plan/promise_projection.py`
- `app/marcus/lesson_plan/prework_projection.py`
- `tests/unit/marcus/lesson_plan/test_review_projection_37_1.py`
- `tests/integration/marcus/test_workbook_band_wiring.py`
- `tests/test_check_pipeline_manifest_lockstep.py`
- `docs/project-context.md`

## Dev Agent Record

### Agent Model Used

Codex (GPT-5)

### Debug Log References

- RED: focused Story 37.4 collection failed with `ModuleNotFoundError` for the
  intentionally absent `reflection_projection` module.
- GREEN: 34 focused Story 37.4 tests passed after implementation and self-review
  hardening.
- Dependency regression: 521 tests passed across Stories 37.4, 37.1, 36.3, 37.2a,
  and 37.3.
- Neutral topology/lockstep regression: 24 tests passed across workbook-band wiring,
  pipeline-manifest lockstep, and lockstep-script integration.
- Ruff passed for all scoped Python files; `git diff --check` passed.
- Review remediation RED: 22 focused failures proved all six review patch families,
  including reference-style Markdown, ZWJ/ZWNJ, duplicate cues, receipt shapes, exact
  writer return type, and the missing AC10 mutations.
- Review remediation GREEN: 84 focused tests, 571 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-two RED: 13 focused failures proved short/numeric/non-ASCII/nested/
  escaped-bracket reference forms and both directions of the pre-gate declared-ref and
  pre-work-digest state-space defects.
- Review round-two GREEN: 111 focused tests, 598 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-three RED: 8 focused failures proved uncovered compact hyphen/asterisk/
  underscore and whitespace-interspersed underscore thematic-break forms.
- Review round-three GREEN: 134 focused tests, 621 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-four RED: 140 focused failures and 155 passes proved the setext,
  joiner-only, and exhaustive CommonMark type-1/type-6 incomplete raw-block gaps;
  six additional case/attribute boundary variants were added before implementation.
- Review round-four GREEN: 301 focused tests, 788 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-five RED: 9 focused failures and 312 passes proved standalone variation
  selectors/default-ignorable combining marks could satisfy the prior visibility test.
- Review round-five GREEN: 321 focused tests, 808 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-six RED: 12 focused failures and 341 passes proved that Hangul fillers
  and Braille blank could satisfy visibility while valid subdivision flags were rejected.
- Review round-six GREEN: 353 focused tests, 840 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-seven RED: 15 focused failures and 374 passes proved five newly covered
  semantic blanks plus combinations and eight invalid subdivision-tag payload shapes.
- Review round-seven GREEN: 389 focused tests, 876 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-eight RED: 13 focused failures and 383 passes proved nine arbitrary
  hidden tag payloads were accepted and four non-callable writer objects raised.
- Review round-eight GREEN: 396 focused tests, 883 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-nine RED: 3 focused failures and 402 passes reproduced an unclosed native
  coroutine, hostile gate/prompt equality bypass, and hostile request serialization.
- Review round-nine GREEN: 405 focused tests, 892 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-ten RED: 10 focused failures and 407 passes proved instance serializer
  shadows, forged exact children, retained hostile nested types, and pending async returns.
- Review round-ten GREEN: 417 focused tests, 904 dependency tests, and 24 neutral
  topology/manifest tests passed; scoped Ruff and `git diff --check` passed.
- Review round-eleven RED: 8 focused failures and 420 passes proved exact-instance
  serializer-state bypasses and instance-dispatched Future/Task cancellation hooks.
- Review round-eleven GREEN: 428 focused tests, 915 dependency tests, and 24 neutral
  topology/manifest tests passed; strict RuntimeWarning, Ruff, and diff checks passed.
- Review round-twelve RED: 1 focused failure and 427 passes reproduced both the asyncio
  pending-Task destruction log and unawaited native-coroutine warning after forced GC.
- Review round-twelve GREEN: 428 focused tests, 915 dependency tests, and 24 neutral
  topology/manifest tests passed; strict RuntimeWarning, Ruff, and diff checks passed.
- Review round-thirteen RED: 1 focused failure and 429 passes reproduced the open-idle
  loop leak at `CORO_CREATED`, including pending-Task and unawaited-coroutine diagnostics.
- Review round-thirteen GREEN: 430 focused tests, 917 dependency tests, and 24 neutral
  topology/manifest tests passed; strict RuntimeWarning, Ruff, and diff checks passed.
- Review round-fourteen RED: 1 focused failure and 429 passes proved adapter-side closing
  corrupted an open-idle loop's later cancellation turn with coroutine-reuse RuntimeError.
- Review round-fourteen GREEN: 430 focused tests, 917 dependency tests, and 24 neutral
  topology/manifest tests passed; strict RuntimeWarning, Ruff, and diff checks passed.
- Review round-fifteen RED: 3 focused failures and 430 passes proved unbound Task
  cancellation still dispatched hostile Future/Task waiter cancellation overrides.
- Review round-fifteen GREEN: 433 focused tests, 920 dependency tests, and 24 neutral
  topology/manifest tests passed; strict RuntimeWarning, Ruff, and diff checks passed.
- Review round-sixteen RED: 4 focused failures and 433 passes proved terminal-waiter
  races, swallowed first cancellation, hostile completed waiters, and nested catch paths.
- Review round-sixteen GREEN: 437 focused tests, 924 dependency tests, and 24 neutral
  topology/manifest tests passed; strict RuntimeWarning, Ruff, and diff checks passed.
- Review round-seventeen RED: 3 focused failures and 437 passes proved an inherited-base
  Future instance shadow and the prior one-retry stop across success/exhaustion paths.
- Review round-seventeen GREEN: 440 focused tests, 927 dependency tests, and 24 neutral
  topology/manifest tests passed; strict RuntimeWarning, Ruff, and diff checks passed.
- Review round-eighteen RED: 1 focused failure and 441 passes proved a debug loop rejected
  the foreign-thread initial waiter wakeup before the retry chain could begin.
- Review round-eighteen GREEN: 442 focused tests, 929 dependency tests, and 24 neutral
  topology/manifest tests passed; strict RuntimeWarning, Ruff, and diff checks passed.
- Review round-nineteen RED: 2 focused failures and 442 passes proved a serializer mismatch
  warning escaped strict degradation and foreign Future cancellation stranded its waiter.
- Review round-nineteen GREEN: 444 focused tests, 931 dependency tests, and 24 neutral
  topology/manifest tests passed; RuntimeWarning/UserWarning, Ruff, and diff checks passed.
- Review round-twenty RED: 3 focused failures and 446 passes proved foreign focus, Promise,
  and PreWork models were schema-coerced before exact nested ownership was enforced.
- Review round-twenty GREEN: 449 focused tests, 936 dependency tests, and 24 neutral
  topology/manifest tests passed; RuntimeWarning/UserWarning, Ruff, and diff checks passed.

### Completion Notes List

- Added strict frozen request, bounded writer-candidate, ability-cue, canonical-clause,
  gate-receipt, and aggregate-result contracts with recursive boundary validation.
- Bound the authored Promise and complete PreWorkBrief snapshots through canonical
  SHA-256 digests, exact Friction Scale equality, Promise/pre-work reconciliation,
  deterministic replay, and forged snapshot/receipt/result rejection.
- Kept learner-facing composition closed: the injected writer chooses only one
  `name`/`see`/`do` lens per Promise ability; the adapter owns exact vow/lens cues and
  the three pinned shifted-question clauses.
- Implemented deterministic zero-call pre-gates, exactly-one eligible writer call,
  unchanged exception propagation, stable single-loss precedence, and the honest
  offline unavailable stub.
- Re-exported only dedicated Story 37.4 symbols from Review; the Story 37.1 five-beat
  shell, generic ReflectionWriter API, pending Closing Reflection beat, and renderer
  bytes remain unchanged.
- Added exact request/candidate/semantic-manifest fixtures plus authority, mutation,
  injection, anti-forgery, strict-schema, frozen-model, no-learner-value, determinism,
  M3 import, and ownership-fence tests.
- Independent Blind, Edge, and Acceptance review remains intentionally unchecked for
  the mandatory fresh review agents; this developer handoff does not claim `done`.
- Resolved all six recorded review patches RED-first: reference-style full/collapsed/
  shortcut link and image forms now fail without rejecting ordinary bracket notation;
  ZWNJ/ZWJ are permitted while other controls and bidi formats fail; standalone prompts
  reject duplicate refs; standalone receipts admit only structurally reachable shapes;
  writer subclasses fail the exact-return contract; and AC10 now has direct mutations
  for unknown refs, pre-work digest, cue drift, forged receipts, and reference markup.
- Story and ledger remain `review`; fresh exact-current Blind/Edge/Acceptance closure is
  still required before the independent-review task or story may be marked complete.
- Resolved all four round-two patches RED-first. A small closed delimiter scanner now
  rejects every bracket-bearing Markdown reference/link/image surface, including short,
  numeric, Unicode, nested, collapsed/full/shortcut, image, and escaped-closing-bracket
  forms, while ordinary non-markup prose remains valid.
- Standalone receipts now require empty declared refs for Promise-unavailable/degraded,
  nonempty declared refs for pre-work-absent/mismatch/eligible, the null pre-work digest
  exactly for absent pre-work, and a present digest for mismatch/eligible. Promise
  short-circuit receipts intentionally accept either pre-work digest shape.
- Resolved both round-three patches RED-first. A deterministic CommonMark thematic-break
  recognizer rejects three-or-more marker-only `-`, `*`, or `_` families in compact or
  space/tab-interspersed form while preserving fewer-than-three compact markers and
  ordinary prose containing marker characters. Existing block/link guards remain intact.
- Resolved all four round-four patches RED-first. Marker-only equals and hyphen setext
  underlines now fail, joiners require at least one non-whitespace/non-format visible
  character, and a closed case-insensitive CommonMark type-1/type-6 tag inventory rejects
  incomplete raw-block starts at end-of-line or recognized boundaries. Contextual
  `markdown-it` reproductions pin heading promotion and adjacent-line raw-block capture;
  ordinary comparisons and near-match tag names remain valid.
- Resolved both round-five Unicode patches RED-first. Visibility now requires at least
  one character outside Unicode control/format and combining-mark categories, while
  remaining language-neutral: multilingual letters/numbers and learner-visible symbols
  or punctuation qualify, and legitimate selectors/marks/ZWJ/ZWNJ remain valid when
  attached to a visible base.
- Resolved all four round-six Unicode patches RED-first. The closed visibility exclusion
  names Hangul choseong/jungseong/compatibility/halfwidth fillers and Braille blank while
  allowing them beside actual visible content. A structural scanner admits tag-spec
  characters only after U+1F3F4, requires one or more tag-spec characters and U+E007F,
  and rejects isolated, malformed, reordered, interrupted, or unterminated sequences.
- Resolved all four round-seven Unicode patches RED-first. Named inclusive ranges now
  cover Hangul fillers, Braille blank, ideographic half-fill space, Egyptian hieroglyph
  full/half blanks, and SignWriting wall/floor-plane spaces while preserving U+2420 and
  multilingual neighbors. Subdivision flags now admit only tag-encoded lowercase ASCII
  letters and digits; tag space, punctuation, uppercase, interruptions, and malformed
  termination/order fail at the full-request boundary.
- Resolved all four round-eight patches RED-first. A named closed RGI registry admits
  only tag-encoded `gbeng`, `gbsct`, and `gbwls`; arbitrary hidden prose and other
  alphanumeric payloads fail while multiple valid flags remain supported. Eligible
  non-callable writer objects are never invoked and normalize to the deterministic typed
  writer-contract-invalid degradation; callable exceptions still propagate unchanged.
- Resolved all four round-nine patches RED-first. Aggregate replay requires exact runtime
  authority, candidate, gate, and prompt base types before invoking owned-model methods,
  recursively revalidates their Python dumps, and compares only normalized objects.
  Constructed-invalid exact bases fail while valid Python/JSON round trips remain stable.
  Rejected native coroutine returns are closed before deterministic contract degradation;
  non-native awaitables degrade and callable-thrown exceptions still propagate.
- Resolved all five round-ten patches RED-first. Every nested dump now dispatches through
  trusted unbound serialization; request, candidate, prompt, and result validators replace
  owned fields with recursively validated exact copies, stripping instance shadows and
  hostile nested subclasses while rejecting forged exact-base internals. The synchronous
  writer seam closes native coroutines, cancels scheduled Tasks/Futures, and leaves generic
  awaitables unexecuted; callable exceptions continue to propagate unchanged.
- Resolved all three round-eleven patches RED-first. Normalization now takes an expected
  exact model type and calls that class's compiled Pydantic serializer directly, bypassing
  instance `__pydantic_serializer__` shadows and returning canonical stored graphs. Task
  and Future cleanup dispatches through trusted unbound asyncio methods, bypasses hostile
  `cancel` overrides, and contains closed-loop or cleanup failures before typed degradation.
- Resolved both round-twelve patches RED-first. If trusted Task cancellation raises or a
  closed loop leaves the rejected Task nonterminal, cleanup obtains the coroutine through
  unbound `Task.get_coro`, closes only a native coroutine, and disables only that Task's
  pending-destruction diagnostic through the trusted slot descriptor. Forced GC emits no
  asyncio error or unawaited warning, task bodies/callbacks never run, and running-loop
  cancellation behavior remains unchanged.
- Resolved all four round-thirteen patches RED-first. Rejected Tasks on any non-running
  loop are disposed without advancing that loop; diagnostic suppression occurs only when
  the Task is terminal or trusted `inspect.getcoroutinestate` proves `CORO_CLOSED` after
  the single native close attempt. GeneratorExit-resistant coroutines remain suspended and
  retain the observable pending diagnostic. Active-loop Tasks still cancel normally, and
  hostile Task hooks, task bodies, and callbacks are never invoked by cleanup.
- Round fourteen supersedes round thirteen's open-idle disposal assumption. Every open
  loop owns its live scheduled Task step whether currently running or idle: the adapter
  requests trusted cancellation only and never closes the coroutine or suppresses its
  diagnostics. A later loop turn cleanly reaches `cancelled` without executing the body,
  RuntimeError, InvalidStateError, or unretrieved exceptions. Only a proven closed loop
  permits native-coroutine disposal and proof-gated pending-diagnostic suppression;
  GeneratorExit-resistant closed-loop behavior remains observable.
- Round fifteen reads each Task's waiter through the Task-owned descriptor and recursively
  cancels Task waiters with a cycle guard or Future waiters through the unbound Future base
  method. Outer Tasks remain owned by an open loop and cancel when it advances, without
  dispatching hostile waiter overrides; closed-loop proof-gated disposal is retained.
- Round sixteen gives base-cancel-safe Future waiters an immediate unbound Task cancellation
  request, including the completed-but-unconsumed race, then uses bounded public `call_soon`
  retries to restore cancellation after one caught request or across a nested Task wakeup.
  A hostile completed Future's already-queued wakeup cannot be preempted without invoking
  its override or editing the foreign loop queue; its hook remains untouched and the retry
  cancels at the next suspension before any post-suspension side effect. The adapter never
  advances the loop, mutates its ready queue, or suppresses closed-loop proof requirements.
- Round seventeen requires both exact class-level Future cancellation resolution and no
  instance-level `cancel` shadow before allowing Task cancellation to dispatch through a
  waiter. Trusted `object.__getattribute__` inspection and bound-base-method identity shape
  checks fail closed for proxy, malformed, or hostile instance state; an absent instance
  dictionary is accepted only when the resolved bound method still has the trusted base
  shape. The open-loop retry budget is exactly five owner requests (initial plus four
  scheduled turns), schedules again after every request while live, and stops at terminal
  state or exact exhaustion.
  A coroutine that deliberately catches all five may continue cooperatively after exhaustion;
  the adapter stays finite and neither advances nor edits the foreign loop.
- Round eighteen marshals the entire initial cleanup request to a running foreign loop's
  owner thread, then schedules every bounded retry through the trusted unbound
  `BaseEventLoop.call_soon_threadsafe`. Debug loops therefore perform waiter cancellation
  and all five owner requests on their owning thread without instance scheduler dispatch,
  non-thread-safe diagnostics, loop advancement, or ready-queue edits. Same-thread running,
  idle-open, and closed-loop ownership behavior is preserved.
- Round nineteen disables only class-owned Pydantic serializer mismatch warnings because
  every serialized payload is immediately strict-revalidated; validation exceptions remain
  visible and malformed exact candidates deterministically degrade to writer-contract loss.
  Standalone Futures now obtain their loop through unbound `Future.get_loop` and marshal a
  contained unbound `Future.cancel` callback through trusted `call_soon_threadsafe` when the
  running loop is foreign. Same-thread, idle, closed-loop, hostile-hook, and Task paths remain
  unchanged.
- Round twenty preflights the runtime type graph through trusted `object.__getattribute__`
  before every class-owned serialization. Candidate focuses, prompt cues/clauses, request
  Promise/PreWork snapshots, directly embedded Promise and PreWork models, and aggregate
  authority/candidate/gate/prompt graphs must be exact owned classes; foreign or subclassed
  models are rejected without method dispatch. Writer candidates normalize to the canonical
  contract-invalid candidate, while standalone request/prompt/result validation fails loudly.
  Warning suppression remains downstream of this ownership gate and strict revalidation.
- Exact-current closure is complete: fresh Blind, Edge, and Acceptance layers all PASS;
  root verification reproduced 936 dependency tests under strict RuntimeWarning/UserWarning,
  24 neutral topology/manifest tests, scoped Ruff, and clean diff checks. Cora pre-closure
  classified the exact eight-file window `warn` and returned `permit_closure=true`.

### File List

- `_bmad-output/implementation-artifacts/37-4-closing-reflection-shifted-question.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/marcus/lesson_plan/reflection_projection.py`
- `app/marcus/lesson_plan/review_projection.py`
- `tests/fixtures/reflection_37_4/request.json`
- `tests/fixtures/reflection_37_4/writer_candidate.json`
- `tests/fixtures/reflection_37_4/semantic_manifest.json`
- `tests/unit/marcus/lesson_plan/test_reflection_projection_37_4.py`

## Change Log

- 2026-07-13: Drafted from FR10/NFR1-NFR8, the ratified workbook DAG, and hardened
  37.1/37.2a/37.3 contracts; pending BMAD party green-light and create-story validation.
- 2026-07-13: BMAD party returned GO-WITH-AMENDMENTS; folded authentic PreWorkBrief
  lineage/digest, learner-visible Promise cues, and bounded name/see/do lens mapping
  while retaining deterministic final clauses and all ownership fences.
- 2026-07-13: Fresh create-story checklist validation PASS; folded deterministic loss
  precedence, canonical digest serialization, and the honest structural-not-historical
  snapshot claim. Ultimate context engine analysis complete; status ready-for-dev.
- 2026-07-13: Implemented the strict Promise/pre-work-bound shifted-question contract,
  deterministic lens/cue composition, anti-forgery replay, offline honesty stub,
  collision-free Review re-exports, fixtures, and exhaustive regression evidence;
  moved to review for independent Blind/Edge/Acceptance closure.
- 2026-07-13: Resolved six review findings RED-first; exact-current evidence is 84
  focused, 571 dependency, and 24 topology/manifest tests passing with scoped Ruff and
  diff check clean. Status remains review pending fresh three-layer closure.
- 2026-07-13: Resolved four round-two review findings RED-first; exact-current evidence
  is 111 focused, 598 dependency, and 24 topology/manifest tests passing with scoped
  Ruff and diff check clean. Status remains review pending fresh three-layer closure.
- 2026-07-13: Resolved two round-three thematic-break findings RED-first; exact-current
  evidence is 134 focused, 621 dependency, and 24 topology/manifest tests passing with
  scoped Ruff and diff check clean. Status remains review pending fresh closure.
- 2026-07-13: Resolved four round-four setext/visibility/raw-block findings RED-first;
  exact-current evidence is 301 focused, 788 dependency, and 24 topology/manifest tests
  passing with scoped Ruff and diff check clean. Status remains review pending closure.
- 2026-07-13: Resolved two round-five Unicode visibility findings RED-first;
  exact-current evidence is 321 focused, 808 dependency, and 24 topology/manifest tests
  passing with scoped Ruff and diff check clean. Status remains review pending closure.
- 2026-07-13: Resolved four round-six Unicode filler/subdivision-flag findings RED-first;
  exact-current evidence is 353 focused, 840 dependency, and 24 topology/manifest tests
  passing with scoped Ruff and diff check clean. Status remains review pending closure.
- 2026-07-13: Resolved four round-seven semantic-blank/tag-alphabet findings RED-first;
  exact-current evidence is 389 focused, 876 dependency, and 24 topology/manifest tests
  passing with scoped Ruff and diff check clean. Status remains review pending closure.
- 2026-07-13: Resolved four round-eight RGI-registry/non-callable-writer findings
  RED-first; exact-current evidence is 396 focused, 883 dependency, and 24 topology/
  manifest tests passing with scoped Ruff and diff check clean. Status remains review.
- 2026-07-13: Resolved four round-nine aggregate-subclass/coroutine-lifecycle findings
  RED-first; exact-current evidence is 405 focused, 892 dependency, and 24 topology/
  manifest tests passing with scoped Ruff and diff check clean. Status remains review.
- 2026-07-13: Resolved five round-ten trusted-normalization/async-cleanup findings
  RED-first; exact-current evidence is 417 focused, 904 dependency, and 24 topology/
  manifest tests passing with scoped Ruff and diff check clean. Status remains review.
- 2026-07-13: Resolved three round-eleven serializer-state/cancel-dispatch findings
  RED-first; exact-current evidence is 428 focused, 915 dependency, and 24 topology/
  manifest tests passing with strict warning, Ruff, and diff checks clean. Status review.
- 2026-07-13: Resolved two round-twelve closed-loop Task disposal findings RED-first;
  exact-current evidence is 428 focused, 915 dependency, and 24 topology/manifest tests
  passing with strict warning, Ruff, and diff checks clean. Status remains review.
- 2026-07-13: Resolved four round-thirteen idle-loop/proof-gated Task findings RED-first;
  exact-current evidence is 430 focused, 917 dependency, and 24 topology/manifest tests
  passing with strict warning, Ruff, and diff checks clean. Status remains review.
- 2026-07-13: Resolved three round-fourteen Task-ownership findings RED-first, superseding
  open-idle disposal; exact-current evidence is 430 focused, 917 dependency, and 24
  topology/manifest tests passing with strict warning, Ruff, and diff checks clean.
- 2026-07-13: Resolved two round-fifteen trusted waiter-chain findings RED-first;
  exact-current evidence is 433 focused, 920 dependency, and 24 topology/manifest tests
  passing with strict warning, Ruff, and diff checks clean. Status remains review.
- 2026-07-13: Resolved three round-sixteen cancellation-race findings RED-first with
  immediate base-safe owner cancellation and bounded next-suspension retries; exact-current
  evidence is 437 focused, 924 dependency, and 24 topology/manifest tests passing with
  strict warning, Ruff, and diff checks clean. Status remains review.
- 2026-07-13: Resolved four round-seventeen instance-shadow and finite-retry findings
  RED-first; exact-current evidence is 440 focused, 927 dependency, and 24 topology/manifest
  tests passing with strict warning, Ruff, and diff checks clean. Status remains review.
- 2026-07-13: Resolved two round-eighteen cross-thread scheduler findings RED-first;
  exact-current evidence is 442 focused, 929 dependency, and 24 topology/manifest tests
  passing with strict warning, Ruff, and diff checks clean. Status remains review.
- 2026-07-13: Resolved four round-nineteen serializer-warning and standalone-Future
  ownership findings RED-first; exact-current evidence is 444 focused, 931 dependency, and
  24 topology/manifest tests passing with RuntimeWarning/UserWarning strictness plus clean
  Ruff and diff checks. Status remains review.
- 2026-07-13: Resolved three round-twenty nested-graph preflight findings RED-first;
  exact-current evidence is 449 focused, 936 dependency, and 24 topology/manifest tests
  passing with RuntimeWarning/UserWarning strictness plus clean Ruff and diff checks. Status
  remains review.
- 2026-07-13: Fresh exact-current Blind, Edge, and Acceptance reviews PASS; root reproduced
  936 dependency and 24 topology/manifest passes with strict warnings, scoped Ruff, and clean
  diff checks. Cora pre-closure returned warn/permit; Story 37.4 closed `done`.
