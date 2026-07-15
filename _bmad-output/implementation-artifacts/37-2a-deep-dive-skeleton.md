---
baseline_commit: 490158ec
---

# Story 37.2a: Deep Dive skeleton from source-bound narration claims

Status: done

## Story

As the Marcus-SPOC workbook runtime,
I want a strict Deep Dive skeleton contract that re-voices source narration into ability-organized read-prose while preserving every declared VO claim and exposing source-supported depth,
so that the later research-enrichment pass starts from an honest, traceable skeleton rather than a transcript, disjoint rewrite, or model-prior invention.

## Dependency Position

`38.0 -> 38.3b -> {Epic 36, 37.1, 37.2a, 37.3, 37.4} -> 38.3a -> 38.1 -> 37.2b`

Stories 38.0 and 38.3b are done, and Epic 36 plus Story 37.1 provide already-landed contracts consumed by this implementation. Under the ratified DAG, Story 37.2a belongs to the dependency-unlocked writer tranche and has **no Ask-A dependency**. It must close before 38.3a; Story 37.2b remains blocked until 38.1 supplies Ask A.

## Acceptance Criteria

1. **Strict M3-safe Deep Dive skeleton contracts**
   - Add `app/marcus/lesson_plan/deep_dive_projection.py` with strict, frozen, extra-forbid, JSON-safe models for ordered narration/source spans, source claims, ratified ability inputs, writer request, ability-grouped skeleton sections, skeleton claims, bold-term markers, gate receipt, and aggregate result.
   - Reject blank IDs/text/source refs, non-string coercion, duplicate span/claim/ability IDs, structurally unknown closed literals, contradictory status/payload/loss combinations, and extra fields. Cross-object referential errors (unknown claim/span/ability references in a writer result) are accepted only into the validation adapter, never into an authored result, so the adapter can emit an inspectable failed/degraded gate receipt naming the exact IDs.
   - Authored output requires nonempty sections/claims/prose, exact ability/source/claim reconciliation, no unavailable marker/losses, and a passing gate. Unavailable/degraded output carries no authored prose/terms and has stable typed losses/marker.
   - Schema/model-dump/JSON-round-trip pins make the contract inspectable and stable.

2. **Typed source-bound claim inventory is the extraction method**
   - Each normalized source claim has a stable `claim_id`, atomic claim text, one or more resolvable narration/deck `source_span_refs`, and a closed role: `vo` (heard narration claim) or `source_supported_delta` (mechanism/why/caveat/reasoning already supported by those source spans but omitted from the glance/VO claim set).
   - Claim IDs and source-span bindings are supplied at the typed writer boundary from extracted source authority; the projector does not invent them, infer them from word overlap, call an LLM to grade itself, or read global/filesystem state.
   - The conservative false-negative posture is binding: uncertain semantic equivalence is not silently credited. Missing/unresolved declared coverage fails or degrades with explicit IDs for inspection; an operator may spot-check semantics outside this pure projector.
   - This v1 gate proves coverage of the declared source-bound inventory, not universal semantic equivalence. The limitation is recorded as an operator-WARN, never represented as complete automated semantic audit.

3. **Operational A3 proper-superset gate**
   - Compute claim/concept sets by stable IDs/traces, never raw string containment or bag-of-words: `VO_claim_ids <= skeleton_trace_claim_ids` and, for `authored`, at least one `source_supported_delta` claim is present in the skeleton.
   - The gate receipt exposes covered VO IDs, missing VO IDs, used delta IDs, unknown claim/source references, and pass/fail status—not only a Boolean.
   - Contract-construction errors fail validation without a receipt. Structurally valid writer results with unresolved cross-object references fail closed through the adapter and return the typed non-authored result plus a gate receipt listing the unknown/missing IDs; they are never silently normalized or credited.
   - Removing any VO claim from the skeleton fails. A disjoint rewrite with superficial vocabulary overlap fails. Verbatim/paraphrase-only VO with no source-supported delta cannot be `authored`; thin source returns typed degraded/unavailable honesty.
   - A reworded skeleton passes when its structured trace covers every declared VO claim and at least one allowed delta; prose need not contain the source sentence verbatim.
   - Structural chrome, headings, metadata, duplicated claims, new vocabulary alone, or bold markers do not count as depth.
   - Do not reuse `WorkbookProducer._assert_workbook_superset_of_vo` as this gate; its legacy lexical overlap behavior remains untouched until integration ownership.

4. **Transform-only, ability-organized read-prose**
   - Writer input consists only of ordered source spans/claims and ordered ratified ability inputs; ability order follows the supplied ratified Promise/LO authority.
   - Every authored section maps to exactly one supplied ability ID; every supplied ability has exactly one section; unknown, duplicate, missing, or reordered ability sections fail.
   - Every skeleton claim maps to a supplied claim ID and resolvable source span(s). No model-prior facts, research-derived enrichment, fabricated mechanism/evidence, unsupported numeric change, or contradiction may be represented as source-backed.
   - Output is self-contained learner read-prose and carries no `REVOICE-REQUIRED` marker, transcript blockquote scaffold, slide deixis, voice-profile footer, or empty-narration placeholder.
   - Numeric fidelity is FAIL-mode across digits, decimals, percentages, ranges, signs/units, and pinned word-form numeral witnesses. Bounded automated negation/source-trace proxies run; full prose faithfulness/non-contradiction/depth quality remains an explicit operator WARN.

5. **Bold inline term markers with machine-readable parity**
   - Authored skeleton prose may bold source-authorized load-bearing terms using safe `**term**` markers and emits a canonical nonblank deduplicated `bold_terms` tuple for downstream 07W.2/39.1 consumers.
   - The exact canonical term set in metadata equals the terms marked in prose. Reject marker/metadata mismatch, blank or duplicate terms, unmatched/nested markup, heading/newline injection, and terms absent at a valid prose boundary.
   - This story produces markers only—no glossary definitions, links/anchors, Ask-A provenance, targeted top-up, or glossary rendering.

6. **Typed `DeepDiveWriter(skeleton)` seam and honest offline stub**
   - Define the dedicated callable `DeepDiveWriter(request: DeepDiveSkeletonRequest) -> DeepDiveSkeletonResult` and deterministic offline stub in the M3-safe lesson-plan layer.
   - Evolve `review_projection.py` only as needed to import/re-export the dedicated Deep Dive writer types while preserving Story 37.1's five-beat frame, `DeepDiveBeat` pending default, Bookend bytes, Check/Reflection protocols, and public compatibility.
   - A pure validation/composition adapter invokes an injected writer exactly once, validates its exact return type/result, computes gates independently, and returns authored only when all gates pass. Writer exceptions propagate or become a stable typed execution failure per one pinned policy; wrong return types and invalid constructed models fail closed.
   - Offline stub is deterministic unavailable, performs no semantics/model call, and cannot pass the authored gate.

7. **No Ask-A, orchestration, persistence, or render integration**
   - Request/result shapes contain no `ResearchPacket`, Ask-A digest/pool, citations, enrichment sentences, Tracy/Texas data, References, model config, run directory, or filesystem path.
   - Import/AST guards reject research-packet/enrichment resolvers, orchestrator, specialist/provider/model SDK/config/client, terminal producer, renderer, and global/run-state reads.
   - Do not edit `prework_artifact.py` or activate its reserved `deep_dive_skeleton: None` slot; digest-bound persistence/receipt reconciliation belongs to 38.3a/37.5 integration.
   - Do not edit `workbook_wiring.py`, `production_runner.py`, pipeline manifest/graph, terminal `_act.py`, `workbook_producer.py`, or `prose_uplift.py`. Live writer instantiation/positioning remains at orchestrator-owned 07W.1; Review composition/render remains 37.5.

8. **Honest adequacy and boundary behavior**
   - Empty/blank narration, missing ratified ability authority, or no declared VO claims fail request validation. A structurally valid writer result with unresolved source/claim/ability references cannot yield authored output and returns the pinned non-authored adapter result with exact referential failures in its gate receipt.
   - Thin source that covers VO but offers no legitimate delta returns typed `degraded` with stable `deep_dive_depth_delta_unavailable`; it does not fabricate a mechanism, citation, or glossary term to satisfy the proper-superset gate.
   - Stable input ordering is preserved. Multiple spans/abilities, one claim serving multiple abilities only when explicitly traced, orphan spans/claims, duplicate refs, and Markdown/Unicode/newline boundaries are covered by tests.

9. **Gate taxonomy and evidence**

   | Gate | Disposition | Witness | Owner |
   |---|---|---|---|
   | Strict contract/reference/status reconciliation | FAIL | automated | 37.2a |
   | Declared VO claim-set coverage | FAIL | automated mutation tests | 37.2a |
   | Source-supported strict depth delta | FAIL for authored; otherwise DEGRADE | automated | 37.2a |
   | Numeric fidelity, including word-form witnesses | FAIL | automated | 37.2a |
   | Source trace and bounded negation/faithfulness proxy | FAIL | automated | 37.2a |
   | Full semantic equivalence/non-contradiction/depth quality | WARN | operator prose spot-check | 37.2a |
   | Ability coverage/order | FAIL | automated | 37.2a |
   | Bold marker/metadata parity and Markdown safety | FAIL | automated | 37.2a |
   | Ask-A/research/model/global-state independence | FAIL | import/AST + shape negatives | 37.2a |
   | Citation coverage/reject-uncited enrichment | NOT OWNED | downstream A2 gate | 37.2b |
   | References, glossary entries/links, render/DOCX/golden | NOT OWNED | downstream integration | 37.5/39.1 |

10. **Focused verification**
   - Add a structured Part-2-style request/result fixture and semantic assertion manifest. Authored prose is structurally/gate-pinned, not byte-goldened; only the deterministic offline stub may be byte/shape stable.
   - Mutation tests cover every missing VO claim, missing delta, unknown/duplicate claim/span/ability, disjoint rewrite, invalid numeric/negation/source trace, ability coverage/order drift, bold-term mismatch/injection, wrong writer return, constructed-model bypass, thin/empty source, and forbidden Ask-A fields/imports.
   - Positive tests prove non-verbatim claim-equivalent prose can pass via declared trace IDs, source ordering remains stable, and an offline fixture succeeds without any Ask-A artifact.
   - Run focused Story 37.2a tests, complete Story 37.1 regression, Epic-36 Promise contract regression, and neutral workbook-band/topology regression. Ruff and `git diff --check` pass.
   - No paid/live run is required: this story owns the typed skeleton contract, gate, and offline seam. Live instantiation and integrated workbook proof belong to later DAG nodes.

## Tasks / Subtasks

- [x] Define strict source-span, source-claim, ability, skeleton, term-marker, gate, request/result contracts (AC: 1-2, 4-5, 8)
- [x] Implement deterministic claim-set proper-superset, source/numeric/negation, ability, and bold-marker gates (AC: 2-5, 8-9)
- [x] Implement the dedicated DeepDiveWriter seam, honest stub, and injected validation adapter (AC: 6)
- [x] Preserve/re-export Story 37.1 compatibility without changing its deterministic frame (AC: 6-7)
- [x] Add structured Part-2-style fixtures and exhaustive positive/mutation/boundary tests (AC: 1-10)
- [x] Run focused and dependency regressions plus Ruff/diff-check (AC: 10)
- [x] Complete independent Blind, Edge, and Acceptance review; remediate findings and obtain exact-current closure before `done` (AC: 9-10)

### Review Findings

- [x] [Review][Patch] Revalidate constructed `DeepDiveSkeletonRequest` instances before invoking the writer so empty/invalid authority cannot pass vacuously [app/marcus/lesson_plan/deep_dive_projection.py:357]
- [x] [Review][Patch] Make rendered section prose a deterministic composition of its structured claim text, preventing untraced learner-facing prose from bypassing source/numeric/negation gates [app/marcus/lesson_plan/deep_dive_projection.py:361]
- [x] [Review][Patch] Prove every bold term is source-authorized by a traced source claim, not merely present in prose and metadata [app/marcus/lesson_plan/deep_dive_projection.py:325]
- [x] [Review][Patch] Preserve numeric witnesses in source order and cover spaced units, leading decimals, expanded word numerals, and clean hyphen/en-dash/em-dash ranges [app/marcus/lesson_plan/deep_dive_projection.py:299]
- [x] [Review][Patch] Pin one source claim per skeleton claim so numeric and negation fidelity cannot be swapped across aggregated propositions [app/marcus/lesson_plan/deep_dive_projection.py:371]
- [x] [Review][Patch] Reconcile every gate diagnostic with pass/fail status and add the missing exhaustive request/result/boundary mutations promised by AC10 [app/marcus/lesson_plan/deep_dive_projection.py:256]
- [x] [Review][Patch] Preserve Unicode minus, scientific notation, and complete compound-unit/superscript witnesses in numeric fidelity [app/marcus/lesson_plan/deep_dive_projection.py:343]
- [x] [Review][Patch] Bind gate/result receipts to canonical request authority and candidate payload digests, with declared-ID partition reconciliation [app/marcus/lesson_plan/deep_dive_projection.py:263]
- [x] [Review][Patch] Bind authored aggregates to the typed request/candidate snapshots and re-run the pure gate during result validation; unkeyed digest consistency alone is not gate authenticity [app/marcus/lesson_plan/deep_dive_projection.py:390]

## Dev Notes

### Authorized scope

- NEW `app/marcus/lesson_plan/deep_dive_projection.py`
- UPDATE `app/marcus/lesson_plan/review_projection.py` only for dedicated type import/re-export compatibility
- NEW `tests/unit/marcus/lesson_plan/test_deep_dive_projection_37_2a.py`
- NEW structured fixtures under `tests/fixtures/deep_dive_37_2a/`
- UPDATE Story 37.1 tests only if needed to prove unchanged public compatibility/frame bytes
- This story file and sprint ledger

No pre-work artifact/digest, orchestrator, graph, runner, terminal producer, workbook renderer, research, citations, glossary, trends, Check, Reflection, or mode-parity edits.

### Contract guidance

- Prefer dedicated types such as `NarrationSourceSpan`, `SourceClaim`, `DeepDiveAbilityInput`, `DeepDiveSkeletonClaim`, `DeepDiveAbilitySection`, `BoldTermMarker`, `DeepDiveGateReceipt`, `DeepDiveSkeletonRequest`, and `DeepDiveSkeletonResult`.
- Keep prose claims distinct from source claims: a skeleton claim may be reworded, but it must trace to one or more declared source claim IDs and source spans. Gate on IDs/references; operator spot-check the actual semantic equivalence.
- Define `vo_claim_ids` from claims with role `vo`; define permitted delta IDs from `source_supported_delta`. Authored trace IDs must cover all VO IDs and use at least one permitted delta ID. Unknown IDs always fail.
- Do not claim a source-supported delta merely because prose has more tokens. This contract intentionally replaces the legacy lexical AC-8 heuristic for the new skeleton path without editing legacy code.
- Ability cardinality is exact: one section per supplied ability, in supplied order; every section has at least one claim; a claim may be referenced in more than one section only when the result explicitly carries that mapping and does not duplicate its identity.
- Bold terms should be extracted/validated from Markdown with a conservative closed parser/regex that rejects malformed/nested markers. Canonicalize by exact display text after trimming; do not silently case-fold distinct terms unless the contract explicitly stores a canonical key.
- Numeric fidelity should compare source-bound claim text against skeleton claim prose at the traced-claim level, not across unrelated sections. Pin the repository's existing digit/word-form handling patterns where reusable without importing terminal code.

### Existing code to preserve

- `review_projection.py`: Story 37.1 exact five-beat frame, generic Check/Reflection writer seams, and Bookend behavior.
- `prework_projection.py`: `PromiseVow` identity/text and strict status patterns; consume normalized ability inputs rather than re-running ratification.
- `workbook_producer.py`: legacy `ProseRevoicer`, transcript model/loader, and lexical superset gate remain unchanged and are not sufficient for A3.
- `prose_uplift.py`: existing deixis vocabulary is useful reference only; do not import its empty placeholder or voice-profile footer into the skeleton contract.
- `prework_artifact.py`: reserved `deep_dive_skeleton: None` and digest schema remain untouched.
- `workbook_wiring.py`: neutral topology/position remains untouched.

### Previous-story intelligence

- Story 37.1 established exact singleton known-loss invariants after review; carry bidirectional status/payload/loss validation into every new result.
- Epic 36 exposed constructed-model and invalid writer-return bypasses; validate injected outputs independently and include constructed-instance mutation witnesses.
- Deterministic shells are byte-goldened; leashed semantic prose is only structural/gate-pinned (A9).
- Terminal remains deterministic-consume and model-free; semantic writer execution is upstream and injected.

### Git intelligence

- `490158ec` is the Story 37.2a baseline and closed 37.1.
- `f82dddf9` closed Epic 36's live pre-work integration.
- `fc108553` established the neutral 07W.1/07W.3 band positions that must not change here.

### Latest technical information

No external library/provider/API upgrade is introduced. Repository-pinned Pydantic, pytest, and Python patterns are authoritative; no web research is needed for this pure local contract/gate story.

### References

- `_bmad-output/planning-artifacts/workbook-presentation-support-redesign-2026-07-12.md` sections 6-8, 11, 13 (FR7, NFR1, NFR3)
- `_bmad-output/planning-artifacts/epics-presentation-support-workbook-2026-07-12.md` Story 37.2 plus binding A1, A2, A3, A4, A9 and ratified ownership boundary
- `_bmad-output/implementation-artifacts/37-1-review-frame-bookend.md`
- `_bmad-output/implementation-artifacts/38-3b-graph-topology-band-orchestrator.md`
- `app/marcus/lesson_plan/review_projection.py`
- `app/marcus/lesson_plan/prework_projection.py`
- `app/marcus/lesson_plan/prework_artifact.py`
- `app/marcus/lesson_plan/workbook_producer.py`
- `app/marcus/lesson_plan/prose_uplift.py`
- `tests/integration/marcus/test_workbook_band_wiring.py`
- `docs/project-context.md`

## Dev Agent Record

### Agent Model Used

GPT-5 Codex (fresh Story 37.2a developer)

### Debug Log References

- RED: `.venv/Scripts/python.exe -m pytest -q tests/unit/marcus/lesson_plan/test_deep_dive_projection_37_2a.py` failed collection with `ModuleNotFoundError: app.marcus.lesson_plan.deep_dive_projection` before implementation.
- GREEN/refactor: focused Story 37.2a suite passed `31 passed`; combined Story 37.2a + Story 37.1 + Epic-36 projection + neutral workbook-band dependency regression passed `192 passed`.
- Quality: Ruff passed on both implementation modules and the new test module; `git diff --check` passed.
- Review-remediation RED: 13 failures exposed all six accepted review gaps before production patches; the expanded focused suite then passed `50 passed`.
- Review-remediation regression: Story 37.2a + complete 37.1 + Epic-36 projection + neutral workbook-band passed `211 passed`; Ruff and `git diff --check` passed.
- Second-closure RED: `6 failed, 52 passed` exposed Unicode-minus/scientific/compound-unit gaps plus absent authority/candidate receipt pins and inventory reconciliation.
- Second-closure GREEN: expanded focused suite passed `57 passed`; full dependency battery passed `218 passed`; Ruff and `git diff --check` passed.
- Final-closure RED/GREEN: the fully self-consistent forged-PASS witness first failed because no validation error was raised, then the expanded focused suite passed `58 passed`; full dependency battery passed `219 passed`; Ruff and `git diff --check` passed.

### Completion Notes List

- Ultimate context engine analysis completed - comprehensive developer guide created.
- Added strict frozen JSON-safe source-span, source-claim, ratified-ability, skeleton, term, request/result, and inspectable gate-receipt contracts.
- Added an ID/trace-based A3 proper-superset gate with exact VO coverage, required source-supported depth delta, source reconciliation, numeric and bounded-negation fidelity, ability order/cardinality, transform-only prose, and bold-marker parity checks.
- Added a one-call injected `DeepDiveWriter` adapter with constructed-model revalidation, propagating exception policy, typed fail-closed degraded/unavailable results, and a deterministic honest offline stub.
- Re-exported the dedicated skeleton seam from the Review projection without changing the Story 37.1 five-beat frame or legacy placeholder writer surface.
- Added Part-2-style structured fixtures, a semantic manifest, and exhaustive positive/mutation/boundary tests. No Ask-A, research, provider, persistence, orchestration, or rendering integration was introduced.
- Remediated all six accepted review findings: request revalidation, deterministic prose/claim binding, traced-source bold authorization, ordered quantity parsing, one-source-claim-per-skeleton-claim fidelity, and bidirectionally reconciled gate diagnostics with the promised mutation matrix.
- Clarified `DeepDiveWriterCandidate` as the semantic name for the canonical `DeepDiveWriter` protocol's untrusted pre-gate return while retaining the longer public compatibility name; full ability-semantic equivalence remains the explicitly declared operator WARN.
- Added complete ordered quantity witnesses for U+2212 signs, `e` and coefficient/exponent scientific notation, compound unit separators, and superscript exponents.
- Added canonical request-authority and candidate-payload SHA-256 pins, declared VO/delta/ability/span inventories, exact coverage partitions, subset/diagnostic reconciliation, authored-result payload recomputation, and a public pure authority-digest helper for downstream comparison. This is contract evidence only; no persistence integration was added.
- Closed unkeyed-digest forgery by carrying revalidated typed authority and candidate snapshots on the aggregate, recomputing both pins, rerunning `_gate(authority, candidate)`, requiring exact receipt equality, and reconciling authored/non-authored payload, status, marker, and loss disposition against the recomputed result.
- Exact-current Blind, Edge, and Acceptance closure all PASS after replaying every prior exploit; Cora pre-closure classified the exact eight-file window as `warn`/non-pipeline and returned `permit_closure=true`; omission/invention/alteration counts are 0/0/0.

### File List

- `_bmad-output/implementation-artifacts/37-2a-deep-dive-skeleton.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `app/marcus/lesson_plan/deep_dive_projection.py`
- `app/marcus/lesson_plan/review_projection.py`
- `tests/fixtures/deep_dive_37_2a/request.json`
- `tests/fixtures/deep_dive_37_2a/writer_result.json`
- `tests/fixtures/deep_dive_37_2a/semantic_manifest.json`
- `tests/unit/marcus/lesson_plan/test_deep_dive_projection_37_2a.py`

## Change Log

- 2026-07-13: Story created from the ratified DAG and A1/A3/A4/A9 contracts; claim extraction, strict proper-superset, false-negative posture, no-Ask-A fence, and downstream ownership pinned; status set ready-for-dev.
- 2026-07-13: Fresh developer implemented the strict source-bound Deep Dive skeleton contract, gates, offline seam, fixtures, and dependency regressions; status moved to review pending independent Blind/Edge/Acceptance closure.
- 2026-07-13: RED-first review remediation completed for all six triaged patches; expanded focused and dependency regressions green; story remains in review for exact-current closure.
- 2026-07-13: Second closure remediation completed for numeric witness completeness and digest-bound receipt/result authenticity; story remains in review for fresh exact-current closure.
- 2026-07-13: Final closure remediation completed for typed-snapshot aggregate authenticity and full pure-gate replay; story remains in review for fresh exact-current closure.
- 2026-07-13: Exact-current three-layer closure PASS; Cora permits closure; final dependency battery 219 passed plus Ruff/diff-check green; marked done.
