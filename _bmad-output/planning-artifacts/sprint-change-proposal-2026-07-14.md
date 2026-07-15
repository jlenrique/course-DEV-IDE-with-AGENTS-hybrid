# Sprint Change Proposal — Story 38.3a Amendment 6

Status: approved for deterministic implementation and review only
Approval: unanimous native BMAD party `GO-WITH-AMENDMENTS` (John, Winston, Murat, Amelia), with the orchestrating agent concurring, 2026-07-14
Live-run authority: not granted

## 1. Issue Summary

The single governed Marcus-SPOC trial `4cee7689-0f97-424b-bd6d-adfc9e63b37c` stopped at Irene Pass-1 node `04A` with `irene-pass1.authority-invalid`: unit `u03i1` supplied `cannot rely on static training`, while the authoritative source says `We can no longer rely on static training.` The strict exact-authority validator correctly rejected the near-paraphrase before workbook, Deep Dive, or Ask-A production.

The defect is architectural: the LLM currently authors byte-sensitive `source_refs`. This places a deterministic invariant inside an agentic judgment seam and violates the established Hourglass/Leaky-Neck rule. The same trial also showed two evidence-control gaps: the failed Irene attempt disappeared from the local cost breakdown, and the preflight retained only an aggregate input-tree digest while including an expected writable `state/config/runs/**` namespace.

Evidence is frozen in `_bmad-output/implementation-artifacts/evidence/workbook-live-hil/postflight-4cee7689-0f97-424b-bd6d-adfc9e63b37c.md`. No retry, attach, recovery, or second start occurred.

## 2. Impact Analysis

### Epic and dependency impact

- Epic 38 remains viable and its dependency order is unchanged.
- Story 38.3a remains the active barrier; Story 38.1 and every downstream story remain blocked behind its verified live acceptance.
- No new epic or story is required. This is a direct amendment to Story 38.3a.
- Epics 36, 37, 39, and 40 require no scope, order, or acceptance change.

### Product and architecture impact

- The PRD goals, FR16 demand-driven research flow, NFR1 anti-fabrication, NFR2 determinism, and NFR8 evidence remain unchanged; the correction makes them more true.
- Existing Hourglass, provenance, and deterministic-neck architecture already requires this direction. No architecture-document rewrite is needed.
- No UX/HUD behavior changes.
- No pipeline graph, manifest, Texas contract, workbook renderer, or broad repository harmonization change.

### Technical impact

- Irene Pass-1 must select stable exact-span catalog IDs rather than author literal authority strings.
- Deterministic projection must materialize the exact `source_refs` bytes before the existing independent validator runs.
- Pass-1 temporal authority needs a versioned receipt that binds selected IDs, projected bytes, source identity, and catalog digest, with explicit read-only legacy handling.
- Irene provider attempts need crash-safe local journaling and exact-or-explicitly-unavailable cost posture even when later validation rejects the candidate.
- Governed preflight evidence needs a retained per-file identity manifest with narrow declared writable exclusions.

## 3. Recommended Approach

Use a direct adjustment inside Story 38.3a.

1. Build a pure digest-bound exact-span catalog from authenticated `source_sections`.
2. Give Irene only stable catalog IDs to select in ordered `source_ref_ids`.
3. Project selected IDs deterministically to literal `source_refs`; retain `resolve_exact_anchor_source()` as an independent final validator.
4. Reject unknown, stale, duplicate, cross-source, or nonconvergent IDs. Do not use fuzzy matching, paraphrase repair, stemming, nearest-match, prefix insertion, or free-text fallback.
5. Journal request/catalog/model identity before dispatch and raw response/provider evidence immediately after return, before parsing or validation. Ambiguous calls are never automatically recalled.
6. Record every attempted call with known usage/cost or an explicit unavailable reason and trace/request correlation.
7. Retain a reconstructable per-file preflight manifest; exclude only enumerated expected output namespaces and inventory those outputs separately.

Effort: medium. Risk before correction: high for live acceptance (`P3 × I3 = 9`). Risk after deterministic projection and adversarial review: low enough for a separately authorized live attempt.

Rollback is not recommended: the strict validator and existing Amendment-5 work are correct. MVP/goal reduction is not acceptable because it would weaken provenance and the required conforming-workbook outcome.

## 4. Detailed Change Proposal

### Story 38.3a — Tasks / Subtasks

Old:

- The remaining task combined deterministic verification, review, and a live attempt.

New:

- Add Amendment-6 tasks for exact-span catalog construction, ID-only model selection, deterministic projection, versioned temporal authority, crash-safe call/candidate evidence, failed-attempt cost truthfulness, and reconstructable preflight identity.
- Require witnessed-case RED coverage plus mutation, concurrency, ambiguity, cost, and identity tests.
- Keep the live task gated behind deterministic GREEN, mandatory code review, and a new party authorization.

### Other artifacts

- Sprint ledger: keep Story 38.3a and Story 38.1 `in-progress`; update comments only for the new correction boundary.
- PRD, epic ordering, architecture, UX, graph, and manifest: no change.

## 5. Implementation Handoff

Classification: direct story adjustment with medium technical complexity; no backlog reorganization.

- Developer: implement Amendment 6 test-first within the named seams; preserve all failed trials.
- Test Architect: verify exact mismatch, mutation, concurrency, ambiguous-call, cost, and identity evidence cases.
- Architect/PM: confirm the correction preserves deterministic-neck and story-scope boundaries.
- Independent reviewers: run Blind Hunter, Edge Case Hunter, and Acceptance Auditor on one exact tree.
- Party: after deterministic and review GREEN, decide whether one fresh governed live acceptance is authorized.

Success requires all Amendment-6 deterministic tests and dependency gates to pass, the existing strict validator to remain independent and unchanged in semantics, failed-attempt evidence/cost posture to be truthful, preflight identity to be reconstructable, mandatory code review to close, and a separately authorized live run to reach `completed` with the required workbook/Deep-Dive/Ask-A evidence.

## Checklist Disposition

- [x] Trigger and evidence identified.
- [x] Epic and future dependency impact assessed; no resequencing or new epic required.
- [x] PRD, architecture, UX, testing, observability, and documentation conflicts assessed.
- [x] Direct adjustment selected; rollback and scope reduction rejected.
- [x] Story edits and implementation handoff defined.
- [x] Sprint status remains honest and unchanged in state.
- [x] Approval recorded through the repository-authorized party-consensus mechanism.

---

# Amendment 7 — Irene deterministic JSON-framing processor v2

Status: approved for deterministic implementation and review
Approval: John/PM and Winston/architect `GO-WITH-AMENDMENTS`; Murat/test concurs on the bounded parser and gates but proposed same-run replay; Quinn adjudicated the sole dispute in favor of the immutable first-run-stands boundary. The orchestrating agent concurs, 2026-07-14.
Live-run authority: no retry authorized; the failed witness remains frozen

## 1. Issue Summary

Governed Marcus-SPOC trial `30850735-dea3-4444-bc7b-513239eae55b` made one Irene Pass-1 provider call and stopped at node `04A`. The provider returned a substantively complete candidate with eight authored plan units, six workbook sections, five research goals, and three-to-six digest-shaped source-span IDs per unit. Strict JSON decoding failed at byte 18,663 only because one surplus final `}` followed the complete top-level object. The legacy parser then discarded the whole candidate, synthesized unanchored `unit-1`, and the independent authority validator correctly rejected that synthetic unit.

The exact Irene attempt cost `$0.20435` and is fully accounted. Raw/provider evidence is durable. The trial is a failed first-run-stands witness and must not be resumed, reclassified, completed, or mutated.

## 2. Impact Analysis

- Epic 38 and the dependency DAG remain viable and unchanged.
- Story 38.3a remains the active dependency barrier; Story 38.1 and all downstream work stay blocked.
- No new epic/story, graph, runner, manifest, UX/HUD, PRD, or workbook-render change is required.
- The defect is in the deterministic provider-response framing neck. Correcting it strengthens NFR1 anti-fabrication, NFR2 determinism, and NFR8 evidence without relaxing source authority.
- `with_structured_output` is deferred unless repeated evidence justifies a larger provider-contract redesign; it would change wire request/response shape and require a complete Pass-1 provider schema.

## 3. Recommended Approach

Use a direct Story 38.3a adjustment:

1. Promote new production calls to `irene-pass1-response-processor.v2`; bind v2 in the pre-dispatch journal identity/request digest.
2. Decode strict JSON first with duplicate-key rejection. Only after an exact trailing-extra-data failure may v2 remove one final non-whitespace byte when that byte is `}` and the remainder uniquely parses as one top-level object. No other repair is permitted.
3. Remove the synthetic `unit-1` fallback from the current production path. Framing or root-shape failure stops with a stable Pass-1 diagnostic.
4. Before semantic gates or artifact publication, atomically persist a digest-protected processing receipt binding the raw-response digest, journal/executed processor versions, action (`strict-json` or `drop-one-surplus-final-rbrace`), exact removed byte/offset, processed-candidate digest, parse/result status, and digest recipe.
5. Reprocessing a durable v2 response must reproduce the receipt byte-for-byte with zero provider calls. Receipt tampering/version mismatch fails closed. Economics counts the attempt once.
6. Legacy v1 remains allowlisted only for immutable validation/audit, economics, exact historical reproduction, and explicitly labeled read-only offline counterfactual analysis. Product runtime never upgrades a v1 journal into v2 or publishes artifacts from it.
7. The frozen response may be copied only into external offline regression/counterfactual evidence labeled `NONPASSING/COUNTERFACTUAL`; every frozen-run file/hash must remain unchanged.

Effort: medium. Risk: high until receipt/replay/version boundaries are proven; low enough for a later separately authorized fresh v2 trial after deterministic review closure.

## 4. Detailed Story Change

Story 38.3a gains Amendment-7 tasks for:

- the exact one-surplus-final-brace processor v2;
- fail-loud removal of current synthetic unanchored fallback;
- `candidate_decoded`/equivalent crash-safe processing receipt state;
- explicit supported-version validation and legacy-v1 read-only economics/audit behavior;
- adversarial suffix/prefix/internal-syntax/duplicate-key/root-shape tests;
- receipt tamper, crash/replay, zero-recall, and exactly-once economics tests;
- frozen-byte/hash preservation and an external offline counterfactual witness.

All decoded candidates still traverse unchanged source-span projection, cluster/floor handling, Pass-1 authority, planning-context, publication, and completed-replay gates. No source ID, source text, collateral value, or semantic plan field is repaired.

## 5. Implementation Handoff and Success Criteria

Classification: direct story adjustment with medium technical complexity.

- Developer: implement RED-first processor/receipt/version changes in Irene and its call journal.
- Test Architect: verify the complete adversarial framing and replay/economics matrix.
- Independent reviewers: Blind Hunter, Edge Case Hunter, and Acceptance Auditor on one exact tree.
- Operator boundary: receive a new detailed pre-live report before any fresh paid attempt.

Success requires focused/dependency/static/architecture GREEN, exact v1 audit/economics compatibility, v2 receipt/replay zero recall, immutable frozen hashes, a labeled offline counterfactual, and fresh three-way ZERO FINDINGS. A later fresh v2 trial—not the frozen trial—must supply live acceptance.

## Checklist Disposition

- [x] Triggering story, defect class, frozen evidence, and cost identified.
- [x] Epic/dependency impact assessed; no resequencing or new epic/story.
- [x] PRD, architecture, UX, graph, testing, observability, and documentation impacts assessed.
- [x] Direct adjustment selected; fail-only and provider-schema redesign rejected for this amendment.
- [x] Story tasks, evidence boundary, implementation handoff, and success gates defined.
- [x] First-run-stands disagreement resolved through Quinn; no human impasse remains.
- [x] Approval recorded through the repository-authorized party-plus-orchestrator mechanism.
