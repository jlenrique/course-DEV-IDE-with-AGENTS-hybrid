---
baseline_commit: fc108553beaf6c03fa740fadf0e52c765fcc1ec7
---

# Story 36.1: Pre-work contract, deterministic frame, and Friction Scale

Status: done

## Story

As the Marcus-SPOC workbook runtime,
I want a strict `PreWorkBrief` contract, injectable Scene/Promise writer seams, and a deterministic three-beat frame with the weekly Friction Scale,
so that every presentation-support workbook begins with one stable honest ritual while later stories supply grounded semantics without changing the frame.

## Dependency Position

`38.0 -> 38.3b -> 36.1 -> {36.2 || 36.3} -> 36.4`

38.3b is done and supplies neutral `07W.1` topology/DI only. 36.1 unlocks 36.2 and 36.3; 36.4 remains blocked until both close.

## Acceptance Criteria

1. **Strict contract and fixed beat order**
   - Add `app/marcus/lesson_plan/prework_projection.py` with every load-bearing model using `ConfigDict(strict=True, extra="forbid", frozen=True, validate_assignment=True)` for Scene, Friction Scale, Promise vows, provenance/known losses, normalized writer requests/results, and aggregate `PreWorkBrief`.
   - Use closed literals/tuples and typed serializable fields; avoid open `Any` payloads where the shape is load-bearing.
   - Aggregate order is always Scene -> Friction Scale -> Promise. Semantic beats may be explicitly unavailable/degraded with stable losses, never filled with invented prose.
   - JSON/schema/round-trip shape pins pass. The module is M3-safe and imports no orchestrator, specialist, terminal producer, model client, or render dependency.

2. **Deterministic three-beat shell**
   - A pure full renderer accepts an already-authored `PreWorkBrief` and emits canonical Markdown in exact three-beat order. Full Markdown may differ when Scene/Promise differ.
   - A separate `render_deterministic_frame` helper emits only fixed headings/honesty shell/Friction text as UTF-8-compatible LF Markdown with one final newline. This helper—not the full semantic render—is the byte-golden target.
   - Beat headings, honesty copy, learner instructions, and the review hook are deterministic.
   - Repeats and materially different lesson/course/mode metadata yield byte-identical deterministic shell/Friction Scale text; future Scene/Promise prose receives structural pins, not byte goldens.

3. **Weekly Friction Scale contract**
   - One immutable, un-failable template includes: 0–10 rating; believable low anchor (`0` means present but not getting in the way, never “frictionless”); blocking high anchor; “locate it” field; one-honest-line field; ~20-second framing; explicit keep-this-mark/line-for-review instruction.
   - It contains no answer key, correctness language, learner value, stored rating, re-rating affordance, cross-week aggregation, or term-long self-portrait claim.

4. **Named writer protocols with honest offline stubs**
   - Define module-public `Protocol.__call__` contracts and export them through `prework_projection.__all__` (no package `__init__.py` change): `SceneComposer(request: SceneComposeRequest) -> SceneBrief` and `PromiseTransformer(request: PromiseTransformRequest) -> PromiseProjection`.
   - `SceneComposeRequest` is a strict normalized JSON-safe contract containing only extracted seed text, tuple source refs, and optional orienting hint. `PromiseTransformRequest` contains only strict normalized objective inputs (`objective_id`, text, status) and optional scene/friction context; it does not load planning artifacts itself.
   - Scene owns only extracted-seed -> Scene transformation; Promise owns only ratified-LO -> ability-vow transformation.
   - Stubs accept valid requests and return strict unavailable/degraded typed results with stable loss codes and deterministic marker; they do not simulate semantics, source claims, resolved objectives, or model output.
   - Do not define DeepDiveWriter/CheckWriter/ReflectionWriter. Do not instantiate model config/client. Live instantiation remains orchestrator-owned at `07W.1`.

5. **Input and integration boundaries**
   - Frame/Friction renderer does not read corpus, narration, run.json, research packets, or planning artifacts and does not infer adequacy/provenance/ratification.
   - Protocol inputs/outputs are typed and JSON-serializable so later implementations can replace stubs without changing `PreWorkBrief` or the renderer.
   - Do not replace/register `workbook_brief_stub@07W.1`, edit `workbook_wiring`, terminal `_act.py`, manifest/runner, or workbook rendering. Story 36.4 owns registration/consumption/integration.

6. **Honest empty and partial behavior**
   - Missing Scene and/or Promise semantics leaves an explicit not-authored/degraded record while the deterministic ritual stays structurally valid. The full renderer uses exact learner-safe copy: `Source-grounded Scene not yet authored.` and `Ratified-objective Promise not yet authored.` Internal loss codes never render. Scene-only, Promise-only, and neither states retain all three headings with no blank body.
   - No “objective unresolved” placeholder, generic scene, payoff claim, source claim, or learner-specific value is emitted. Invalid input fails Pydantic validation rather than coercing.

7. **Gate taxonomy and evidence**

   | Gate | Disposition | Witness | Owner |
   |---|---|---|---|
   | Strict contract/coercion rejection | FAIL | automated | 36.1 |
   | Three-beat order + deterministic frame/Friction exact copy | FAIL | automated byte golden | 36.1 |
   | Per-learner value/re-rate/aggregation/correctness language absent | FAIL | automated negative assertions | 36.1 |
   | M3 and no model SDK/config/client import or construction | FAIL | import-linter + focused AST denylist | 36.1 |
   | Scene provenance/payoff/faithfulness | NOT OWNED | deferred automated + operator spot-check | 36.2 |
   | Promise ratification | NOT OWNED | deferred automated | 36.3 |
   | Promise spoiler heuristic | WARN | deferred automated heuristic + operator spot-check | 36.3 |
   | Part-2/Part-4 semantics and DOCX integration | NOT OWNED | deferred golden/gates | 36.2/36.4 |

   Byte equality applies only to deterministic shell/Friction text. Leashed outputs are structural/gate-pinned only. The ~20-second framing is a copy-review target, not a timed automated claim.

8. **Focused verification**
   - Tests prove strict/frozen/extra rejection and explicit coercion reds (list-for-tuple, int-for-string/bool, invalid nested values), exact model dump and schema invariants (`required`, types, `additionalProperties`), round trip, beat order, byte identity across variants, full Friction copy, believable anchors, review hook, negative-language fences, honest stub/injected-spy behavior, empty/partial states, JSON serializability, and M3/no-model guard.
   - The AST denylist rejects orchestrator, specialists, render packages, and model SDK/config/client imports/construction. It does not falsely prohibit invoking the injected protocol.
   - Focused pytest, existing 38.3b neutral-factory regression, Ruff, and `git diff --check` pass. No paid/live run is required.

## Tasks / Subtasks

- [x] Define strict nested pre-work models and aggregate contract (AC: 1, 6)
- [x] Implement immutable Friction Scale and deterministic three-beat renderer (AC: 2-3)
- [x] Add SceneComposer/PromiseTransformer protocols and honest offline stubs (AC: 4-5)
- [x] Add contract/frame fixture and deterministic-shell golden (AC: 2, 7-8)
- [x] Add strictness, shape, order, determinism, negative-language, injection, serialization, and M3 tests (AC: 1-8)
- [x] Run focused regression and static checks (AC: 8)

### Review Findings

Review provenance: independent **Blind Hunter**, **Edge Case Hunter**, and **Acceptance Auditor** layers reviewed the scoped diff. Their overlapping state-integrity/optional-field findings were deduplicated into the six actionable patches below; Amelia remediated all six RED-first and the close battery independently reproduced 91/91 green.

- [x] [Review][Patch] Enforce authored versus unavailable/degraded marker/loss consistency for Scene and Promise results [app/marcus/lesson_plan/prework_projection.py:42]
- [x] [Review][Patch] Make orienting/context request fields genuinely optional with `= None` defaults and pin minimal schema construction [app/marcus/lesson_plan/prework_projection.py:101]
- [x] [Review][Patch] Reject whitespace-only text/IDs/seeds and empty tuple members across vows, objectives, source refs, and loss codes [app/marcus/lesson_plan/prework_projection.py:63]
- [x] [Review][Patch] Prevent authored semantic Markdown from forging/reordering beat headings or injecting extra Promise bullets while preserving legitimate Scene paragraphs [app/marcus/lesson_plan/prework_projection.py:201]
- [x] [Review][Patch] Enforce aggregate provenance consistency with Scene source refs and nested known losses [app/marcus/lesson_plan/prework_projection.py:133]
- [x] [Review][Patch] Strengthen the AST no-model witness against qualified and aliased SDK/config/client construction [tests/unit/marcus/lesson_plan/test_prework_projection_36_1.py:194]

## Dev Notes

### Authorized scope

- New `app/marcus/lesson_plan/prework_projection.py`
- New focused tests, preferably `tests/unit/marcus/lesson_plan/test_prework_projection_36_1.py`
- A named strict JSON contract fixture and a separate UTF-8 LF deterministic-frame Markdown golden under `tests/fixtures/`; no semantic Part-2/Part-4/skill/ambiguous fixture in 36.1
- This story and sprint ledger

No orchestrator, terminal producer, manifest, runner, research packet, glossary/trends, or render-engine edits.

### Contract guidance

Recommended nested shapes: `SceneBrief`, `FrictionScaleSpec`, `PromiseVow`, `PreWorkProvenance`, and `PreWorkBrief`. Use explicit availability/status literals and tuple `known_losses`. Provide a deterministic JSON payload projection for the future neutral factory adapter.

Do not import `TranscriptSegment` from the workbook specialist. Later Scene input should be a normalized lesson-plan contract. Do not use the terminal producer’s “objective statement unresolved” fallback; Story 36.3 must use `planning_context.load_planning_context` and ratified LO status.

### Friction template minimum content

- Rate this friction from 0 to 10.
- `0`: present, but not getting in the way.
- `10`: repeatedly blocks the work.
- Locate where it shows up.
- Write one honest line.
- Keep this mark and line for review after the presentation.

No value is stored by the producer; the learner writes into the artifact.

### Ownership fences

- 36.2: real Scene extraction, scenario harvest, archetype detection, adequacy/provenance/faithfulness, Part-2/Part-4/skill/ambiguous fixtures.
- 36.3: ratified-LO authority, ability-vow transform, unratified degrade, spoiler WARN.
- 36.4: assemble/register real `PreWorkBrief` at `07W.1`, terminal consumption, Markdown->DOCX, HIL/HAI parity, integrated golden and FR17 exclusions.

### References

- `_bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md` §§3, 5, 13
- `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` Story 36.1 + A4/A7/A9
- `_bmad-output/implementation-artifacts/38-3b-graph-topology-band-orchestrator.md`
- `app/marcus/lesson_plan/glossary_projection.py` and `trends_projection.py` for M3/injection/empty-honesty patterns only
- `app/marcus/lesson_plan/planning_context.py` for the later ratified-LO seam

## Dev Agent Record

### Agent Model Used

GPT-5 Codex (Amelia developer persona)

### Implementation Plan

- RED: pin the absent strict contract/module through focused contract, renderer, protocol, fixture, and boundary tests.
- GREEN: add the minimal M3-safe Pydantic contracts, immutable Friction Scale, pure renderers, and honest offline stubs.
- REFACTOR: format the focused surface and verify the complete Story 38.3b regression without widening integration scope.

### Debug Log References

- RED: focused collection failed with `ModuleNotFoundError` for `app.marcus.lesson_plan.prework_projection`.
- GREEN: focused Story 36.1 suite passed 13/13.
- REGRESSION: combined Story 36.1 + complete Story 38.3b slice passed 74/74; Ruff and `git diff --check` passed.
- REVIEW RED: six recorded patches produced 14 focused failures before production changes.
- REVIEW GREEN: expanded focused suite passed 30/30; combined Story 36.1 + complete Story 38.3b slice passed 91/91; Ruff and `git diff --check` passed.

### Completion Notes List

- Added strict/frozen/extra-forbid nested contracts with explicit Python coercion rejection and JSON round-trip pins.
- Added a separate deterministic-frame byte golden and learner-safe full semantic renderer for all partial states.
- Added exact public writer protocols, deterministic honest offline stubs, JSON-safe normalized requests/results, and AST/M3 boundary evidence.
- Preserved the 07W.1 neutral factory and all orchestrator, terminal, manifest, and render surfaces unchanged.
- Resolved all six review patches: bidirectional result honesty, optional request defaults, nonblank nested values, Markdown frame safety, exact aggregate provenance, and alias/qualified AST denylist coverage.

- Ultimate context engine analysis completed — comprehensive developer guide created.

### File List

- `_bmad-output/implementation-artifacts/36-1-prework-contract-frame-friction-scale.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/marcus/lesson_plan/prework_projection.py`
- `tests/fixtures/prework_36_1/deterministic_frame.md`
- `tests/fixtures/prework_36_1/prework_brief.json`
- `tests/unit/marcus/lesson_plan/test_prework_projection_36_1.py`

## Change Log

- 2026-07-12: Implemented Story 36.1 strict pre-work contracts, deterministic frame/Friction Scale, public writer protocols, honest offline stubs, fixtures, and focused boundary evidence; status set to review.
- 2026-07-12: Addressed all six code-review findings with RED/GREEN evidence; story remains in review for independent verification.
