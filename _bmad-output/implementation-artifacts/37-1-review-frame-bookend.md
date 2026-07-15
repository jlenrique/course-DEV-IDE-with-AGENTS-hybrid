---
baseline_commit: f82dddf9
---

# Story 37.1: Review five-beat frame and Bookend

Status: done

## Story

As the Marcus-SPOC workbook runtime,
I want a strict deterministic five-beat Review frame with a friction-callback Bookend,
so that every presentation closes on the learner's own pre-work thread without pretending the runtime stores or knows the learner's response.

## Dependency Position

`38.0 -> 38.3b -> Epic 36 -> 37.1`

Stories 38.0, 38.3b, and Epic 36 are done. Story 37.1 is one dependency-unlocked writer node alongside 37.2a, 37.3, and 37.4. It does not depend on Ask A, research, or downstream Review semantics. Story 37.5 owns producer/terminal integration; 37.6 owns HIL/HAI encounter-label parity.

## Acceptance Criteria

1. **Strict Review contract and exact five-beat order**
   - Add `app/marcus/lesson_plan/review_projection.py` with strict, frozen, extra-forbid Pydantic-v2 contracts for the five Review beats and aggregate `ReviewBrief`.
   - The exact learner-facing headings are `Bookend`, `Deep Dive`, `Check on Learning`, `The Door Left Ajar`, and `Closing Reflection`; stable internal IDs may use snake-case equivalents. Their canonical order is fixed.
   - The watchword mapping is pinned: Bookend/engagement, Deep Dive/depth, Check/recall, Door-Ajar/engagement, Reflection/transfer.
   - Use closed literals, tuples, typed JSON-safe fields, and explicit availability/ownership metadata. Invalid types and unknown fields fail rather than coerce.
   - JSON/schema/round-trip shape pins prove the order, strictness, and ownership model.

2. **Deterministic frame and honest downstream slots**
   - A pure renderer emits all five headings exactly once and in order with LF line endings and one final newline.
   - The deterministic frame and Bookend shell are byte-identical across lessons, courses, repeated calls, and equivalent serialized inputs.
   - Deep Dive, Check, and Door-Ajar remain explicitly lesson-level unavailable/pending slots. The deterministic Check-on-Learning instrument/section shell renders, while questions and answers remain pending; no prose, questions, answer keys, trends, citations, research, glossary terms, or invented placeholder substance is authored.
   - Closing Reflection has only a deterministic learner-writing shell in this story; Story 37.4 owns its ability/friction-specific authored prompt.
   - Byte-golden assertions apply only to deterministic frame copy. Future leashed content receives structural/gate assertions, never byte matching.

3. **Bookend cashes the pre-work cheque without fabricating learner state**
   - Bookend accepts the strict Epic-36 `PreWorkBrief` lineage and emits a callback prompt that tells the learner to return to the friction rating, location, and honest line she wrote before the presentation.
   - Binding amendment A7 governs: `PreWorkBrief` contains the instrument and keep-this instruction, not the learner's response. Bookend must not accept, infer, persist, serialize, echo, or claim access to any learner rating, location, or line.
   - The callback does not ask the learner to re-rate the 0-10 scale and makes no cross-week aggregation or term-long self-portrait claim.
   - The exact Epic-36 hook (`Keep this mark and line for review after the presentation.`) is contractually cashed by the callback language.

4. **Learner-written versus lesson-level ownership is machine-pinned**
   - Exactly Bookend and Closing Reflection are marked learner-written.
   - Exactly Deep Dive, Check on Learning, and Door Left Ajar are marked lesson-level.
   - Beats 2-4 contain no learner-response fields and no language claiming per-learner generation or that lesson-level content is about a specific learner's friction.
   - The frame does not branch content or ownership by recorded/live encounter mode; mode-copy parity belongs to Story 37.6.

5. **Honest absent/corrupt lineage behavior**
   - Missing, unavailable, or invalid pre-work authority degrades Bookend locally with a stable typed status/known-loss marker; the remaining Review frame stays structurally composable.
   - Learner-facing copy never says "your previous rating" or implies a stored mark when authority is absent. Internal loss codes never leak into learner Markdown.
   - Corrupt or contradictory typed inputs fail validation; the projector does not search global state, `run.json`, the filesystem, or legacy artifacts to manufacture authority.

6. **M3-safe and model-free boundary**
   - `review_projection.py` remains in the `lesson_plan` layer and imports no orchestrator, specialist, terminal producer, provider SDK, model client/config, render dependency, or research packet.
   - It may reuse the Epic-36 `PreWorkBrief` contract; it must not duplicate or reinterpret Scene, Friction Scale, Promise, provenance, or gate logic.
   - Define named callable Protocols `DeepDiveWriter`, `CheckWriter`, and `ReflectionWriter` at the M3-safe lesson-plan seam, with deterministic offline stubs that return strict unavailable/pending results and make no model call. Story 37.1 does not invoke them during frame composition and does not define their downstream semantic success behavior; later stories replace/consume the seams without changing the frame contract.
   - No model call or injected semantic writer is invoked to build the deterministic frame.
   - Do not edit `workbook_wiring.py`, `production_runner.py`, `pipeline-manifest.yaml`, terminal `_act.py`, or workbook rendering. Preserve `workbook_review_stub@07W.3` unchanged.

7. **Downstream ownership fences**
   - Do not define or implement Deep Dive skeleton/enrichment semantics (37.2a/37.2b), retrieval questions or answer keys (37.3), shifted-question transfer semantics (37.4), References/render integration/golden (37.5), mode labels/parity (37.6), glossary (39.1), trends (39.2), or Cover (40.1).
   - If protocol-shaped placeholders are needed for typed composition, they are honest deterministic unavailable results only and may not swallow the named writer ownership assigned to later stories.

8. **Gate taxonomy and evidence**

   | Gate | Disposition | Witness | Owner |
   |---|---|---|---|
   | Strict contract, order, ownership, and coercion rejection | FAIL | automated | 37.1 |
   | Deterministic frame and Bookend exact copy | FAIL | automated byte golden | 37.1 |
   | Learner-value storage/echo/inference absent | FAIL | automated negative assertions | 37.1 |
   | Per-learner claims/fields in beats 2-4 absent | FAIL | automated negative assertions | 37.1 |
   | Re-rate and cross-week aggregation language absent | FAIL | automated negative assertions | 37.1 |
   | Missing/unavailable pre-work lineage | DEGRADE - Bookend-local unavailable; frame remains composable | automated | 37.1 |
   | Corrupt/contradictory typed pre-work input | FAIL validation | automated | 37.1 |
   | Callback wording usability | WARN | operator spot-check | 37.1 |
   | M3/no-model/no-global-state boundary | FAIL | import/AST tests | 37.1 |
   | Deep Dive, Check, Reflection, trends semantics | NOT OWNED | downstream gates | 37.2-37.4/39.2 |
   | Markdown-to-DOCX Review integration and Part-2 golden | NOT OWNED | downstream integrated evidence | 37.5 |

9. **Focused verification**
   - Tests prove strict/frozen/extra rejection, explicit coercion reds, exact schema/model dumps, JSON round-trip, five-beat order/watchwords, byte identity, callback semantics, exact ownership cardinality, and honest partial states.
   - Negative tests prove no learner-value fields/echo, numeric mark interpolation, re-rate, cross-week state, per-learner beats 2-4, downstream semantic payloads, global-state reads, model calls/imports, or heading/beat injection.
   - Run focused Story 37.1 tests plus Epic-36 pre-work contract/artifact regressions and the neutral `07W.3` band regression. Ruff and `git diff --check` pass.
   - No paid/live run is required because this story owns a deterministic contract/frame only. Live Review production evidence belongs to 37.5 and the final Epic 40 workflow audit.

## Tasks / Subtasks

- [x] Define strict Review beat/aggregate contracts with stable order, watchwords, ownership, and honest statuses (AC: 1, 4-5)
- [x] Implement the pure deterministic five-beat frame and Bookend callback (AC: 2-3)
- [x] Define A4 writer Protocols and deterministic honest stubs without invoking them in frame composition (AC: 6-7)
- [x] Add byte-golden and strict shape fixtures (AC: 1-3, 8-9)
- [x] Add ownership, negative-language, missing-lineage, injection, serialization, and M3 tests (AC: 3-9)
- [x] Run focused Epic-36 and neutral-band regressions plus static checks (AC: 9)
- [x] Complete independent Blind, Edge, and Acceptance review; remediate findings and obtain closure evidence before `done` (AC: 8-9)

### Review Findings

- [x] [Review][Patch] Pin every pending beat to exactly one canonical known-loss value; reject empty and duplicate loss tuples [app/marcus/lesson_plan/review_projection.py:100]

## Dev Notes

### Authorized scope

- NEW `app/marcus/lesson_plan/review_projection.py`
- NEW `tests/unit/marcus/lesson_plan/test_review_projection_37_1.py`
- NEW deterministic/shape fixtures under `tests/fixtures/review_37_1/`
- This story file and `_bmad-output/implementation-artifacts/sprint-status.yaml`

No orchestrator, graph, terminal producer, workbook renderer, research, glossary, trends, or existing Epic-36 production edits are authorized absent a separately documented product defect and scope amendment.

### Contract guidance

- Reuse the strict contract and pure renderer patterns in `prework_projection.py`; do not subclass or mutate `PreWorkBrief`.
- Recommended beat metadata: stable `beat_id`, heading, watchword, ownership (`learner_written` or `lesson_level`), status, optional deterministic learner prompt, and tuple `known_losses` with cross-field validators.
- Prefer a fixed aggregate with named beat fields whose model validator pins their IDs/order over an open arbitrary beat list.
- The Bookend's authority is the presence and shape of the pre-work instrument/hook, not a learner response. A valid callback can say: "Return to the friction mark, location, and honest line you wrote before the presentation. Re-read them before continuing." It must not invent the mark or ask for a new rating.
- Empty lesson-level slots must be explicit in the typed record while learner Markdown uses calm, non-technical pending/section-shell copy. Do not render internal markers or losses.

### Existing code to preserve

- `app/marcus/lesson_plan/prework_projection.py`: strict `PreWorkBrief`, exact Friction Scale, and keep-this hook. Consume; do not change.
- `app/marcus/lesson_plan/prework_artifact.py`: persisted/digest-bound pre-work authority. Story 37.1 does not add a Review artifact sidecar.
- `app/marcus/orchestrator/workbook_wiring.py`: `07W.3` remains the neutral `workbook_review_stub` until integration ownership lands.
- `tests/integration/marcus/test_workbook_band_wiring.py`: existing topology, idempotency, and neutral-stub assertions remain green.

### Previous-story intelligence

- Epic 36 established strict/frozen/extra-forbid contracts, explicit nonblank validation, bidirectional status/marker/loss consistency, aggregate provenance invariants, heading-injection safety, and deterministic-shell-only byte goldens. Carry these patterns forward.
- Story 36.4 proved that semantic authoring belongs upstream while the terminal remains deterministic-consume. Do not introduce a model client or terminal inference here.
- Epic 36's final live work exposed why semantic claims require separate gate evidence. Story 37.1 should not label unavailable downstream semantics complete merely because the shell renders.

### Git intelligence

- `f82dddf9` closed Epic 36 and is this story's baseline.
- `fc108553` established the neutral four-node workbook band and `07W.3` stub that this story must preserve.
- Recent workbook stories use RED-first focused tests, explicit scope fences, three independent review layers, Cora block-mode closure, Audra exact-current closure, then story/ledger `done` and a scoped commit/push.

### Latest technical information

No external library, provider API, or framework upgrade is introduced. Current repository-pinned Pydantic/Python/pytest patterns are authoritative; no web-version research is needed for this deterministic local contract story.

### References

- `_bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md` sections 6, 11, and 13 (FR5, FR6, NFR4)
- `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` Story 37.1 and binding amendments A4, A7, A9
- `_bmad-output/implementation-artifacts/36-1-prework-contract-frame-friction-scale.md`
- `_bmad-output/implementation-artifacts/36-4-wire-prework-part2-golden.md`
- `_bmad-output/implementation-artifacts/38-3b-graph-topology-band-orchestrator.md`
- `app/marcus/lesson_plan/prework_projection.py`
- `app/marcus/lesson_plan/prework_artifact.py`
- `app/marcus/orchestrator/workbook_wiring.py`
- `tests/integration/marcus/test_workbook_band_wiring.py`
- `docs/project-context.md`

## Dev Agent Record

### Agent Model Used

GPT-5.4 / Amelia developer workflow

### Implementation Plan

- RED-first: pin the strict aggregate/beat shapes, canonical Markdown bytes, callback semantics, honest absence, ownership cardinality, writer seams, and M3 boundary.
- GREEN: add one M3-safe lesson-plan module with closed Pydantic contracts, pure composition/render functions, and deterministic unavailable writer stubs.
- REFACTOR/verify: keep fixed copy centralized, strengthen AST import coverage, then run the complete Story 37.1 + Epic 36 + neutral-band regression set and static checks.

### Debug Log References

- RED: Story 37.1 collection failed because `review_projection` did not exist.
- GREEN: focused Story 37.1 suite — 13 passed.
- REGRESSION: Story 37.1 + Epic 36 pre-work + neutral `07W.3` band — 221 passed, 1 skipped.
- STATIC: focused Ruff and `git diff --check` passed.
- REVIEW RED: all eight empty/duplicate known-loss mutations across the four pending beat types validated when they should have failed.
- REVIEW GREEN: focused Story 37.1 — 21 passed; combined Story 37.1 + Epic 36 + neutral `07W.3` band — 229 passed, 1 skipped; Ruff and `git diff --check` passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added strict frozen five-beat contracts with exact order, headings, watchwords, ownership, and bidirectional status/loss consistency.
- Added a pure deterministic renderer and exact Bookend callback that consumes only typed `PreWorkBrief` authority and never accepts or echoes learner values.
- Added Bookend-local absence degradation while corrupt or contradictory typed authority fails validation; internal loss markers never render.
- Added named Deep Dive, Check, and Reflection writer Protocols plus deterministic unavailable stubs that frame composition cannot invoke.
- Added byte-golden/shape fixtures and negative tests for downstream-content invention, learner-state claims, re-rating, cross-week state, injection, global reads, forbidden imports, and model calls.
- No live or paid run was used; Story 37.1 owns deterministic contract/frame behavior only.
- Review remediation pins each pending beat to one exact canonical loss tuple, rejecting both empty and duplicate tuples without changing valid degraded Epic-36 authority behavior.
- Exact-current Blind, Edge, and Acceptance closure re-reviews all PASS with no remaining actionable finding; the Blind layer withdrew its degraded-Scene/Promise concern because the immutable Friction Scale is the Bookend authority.
- Cora pre-closure classified the exact six-file window `warn`, found no pipeline-trigger path, and returned `permit_closure=true`; Audra-style exact-current evidence audit is complete with omission/invention/alteration counts 0/0/0.

### File List

- `_bmad-output/implementation-artifacts/37-1-review-frame-bookend.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/marcus/lesson_plan/review_projection.py`
- `tests/fixtures/review_37_1/review_brief.json`
- `tests/fixtures/review_37_1/review_frame.md`
- `tests/unit/marcus/lesson_plan/test_review_projection_37_1.py`

## Change Log

- 2026-07-13: Story created from the ratified Epic 36-40 DAG, binding amendments, current Epic-36 contracts, and neutral Epic-38 topology; status set to ready-for-dev.
- 2026-07-13: Implemented Story 37.1 strict Review frame, Bookend callback, honest writer seams, fixtures, and guardrail tests; moved to review.
- 2026-07-13: Remediated the triaged review finding with eight RED mutations and exact one-item loss tuples; independent-review task complete, retained review status for closure.
- 2026-07-13: Exact-current three-layer closure PASS; Cora pre-closure permits closure; final 229 passed, 1 skipped combined regression plus Ruff/diff-check green; marked done.
