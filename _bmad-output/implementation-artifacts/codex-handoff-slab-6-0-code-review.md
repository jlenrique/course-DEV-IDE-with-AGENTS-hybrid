# Codex dispatch: bmad-code-review on Slab 6.0 production envelope substrate

**Session:** 2026-04-27 (operator-authorized post-Slab-6.0-implementation-and-operator-witnessed-dual-gate)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Slab 6.0 implementation landed (Codex final report 2026-04-27): `ProductionEnvelope` + `SpecialistContribution` strict Pydantic v2 family + `ProductionDispatchAdapter` + `tests/composition/` tree + `ComposedSpecialistChainHarness` + Texas → cd chain test + isolation-preservation test + Composition Smoke template amendment + A17/P3 entries-present test
- Codex-side verification: `pytest tests/composition/ -q --tb=short` → 17 passed; AC unit + integration slice (4 files) → 14 passed; `RunState` schema-pin slice → 34 passed; isolation slice (composition-isolation + per-specialist state-shape) → 78 passed; OpenAI catalog membership → 2 passed; ruff clean across all touched directories; `lint-imports` 9 KEPT 0 BROKEN; sandbox-AC validator → PASS
- **Operator-side dual-gate gate-2 cleared 2026-04-27: `pytest tests/composition/ -q --tb=short` → 17 passed in 1.21s (operator-witnessed Juan Leon; recorded in `migration-6-0-production-envelope-substrate.md` Dev Agent Record §"Operator dual-gate gate-2 evidence" + `m5-decision.md` §"Slab 6.0 substrate-ratification waypoint")**
- Story status: `review` (correctly held pending bmad-code-review per CLAUDE.md §3)
- Working tree contains the Slab 6.0 implementation surface (NEW + MODIFIED files; no Codex commit yet — review fires against working tree state)

**Mission:** independent multi-layer code review on the Slab 6.0 diff per the dual-gate `substrate_shape` + `invariant_preservation` rationale. Surface any defects before formal `done` flip. The substrate this story ships will be consumed by Slab 6.1 (runner) + every future production-graph slab; defects here propagate.

## Why this dispatch exists

Slab 6.0 (`migration-6-0-production-envelope-substrate.md`) is dual-gate per `substrate_shape` (the production envelope is NEW substrate that downstream Slab 6.1 + 6.2 + ... depend on) + `invariant_preservation` (specialists must keep their existing isolated-execution contract; M3 + 5a.4 invariants preserved). Operator-side dual-gate gate-2 (Composition Smoke acceptance via `tests/composition/` PASS) just cleared. The remaining formal-close gate is independent code review with triage discipline.

This is `bmad-code-review`, NOT the lighter `bmad-review-adversarial-general` standalone — three layers (Blind Hunter + Edge Case Hunter + Acceptance Auditor) + triage into patch / defer / dismiss / decision_needed. The Acceptance Auditor layer is load-bearing here because the Slab 6.0 spec has 10 ACs (A through J) plus Path A-prime invariants; the auditor reads the spec + the substrate inventory checklist + the A17/P3 entries and traces the diff against each AC.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." A17 was the latest substrate-aware adaptation finding; Slab 6.0 closes A17 at the contract level. Code review must verify the contract actually closes A17, not just declares closure.

## Scope

**Diff input:** all Slab 6.0 implementation changes in working tree relative to `bf9aae5` (Slab 6.0 opener commit; the last commit before Codex's implementation).

NEW files (the substrate surface):
- `app/models/runtime/production_envelope.py` — `ProductionEnvelope` + `SpecialistContribution` Pydantic v2 strict
- `schema/production_envelope.v1.schema.json` — emitted JSON Schema
- `app/marcus/orchestrator/dispatch_adapter.py` — `ProductionDispatchAdapter`
- `tests/composition/__init__.py`
- `tests/composition/composed_specialist_chain_harness.py` — `ComposedSpecialistChainHarness` fixture
- `tests/composition/test_texas_to_cd_chain.py` — the load-bearing test (THE strict-AC HALT scenario succeeds here)
- `tests/composition/test_specialist_isolation_preserved.py` — invariant test
- `tests/unit/runtime/test_production_envelope_strict.py` — AC-A shape pins
- `tests/integration/marcus/test_dispatch_adapter.py` — AC-B contract pins
- `tests/migration/test_composition_smoke_template_present.py` — AC-D template amendment pin
- `tests/migration/test_a17_p3_entries_present.py` — AC-F catalog pin
- `tests/fixtures/runtime/production_envelope_golden.json` — AC-A golden

MODIFIED files (substrate boundary):
- `app/models/runtime/__init__.py` — re-export `ProductionEnvelope` + `SpecialistContribution`
- `app/models/state/run_state.py` — extends `RunState` with `production_envelope: ProductionEnvelope | None = None` field per Path A-prime Decision #2 (NEW alongside `cache_state`, NOT replacing)
- `docs/dev-guide/migration-story-governance.json` — Slab 6.0 inaugural entry
- `docs/dev-guide/langgraph-migration-guide.md` — §"Production Envelope Substrate" added per AC-I item 3
- `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md` — re-scoped to "runner consumes substrate" per AC-J
- `skills/bmad-create-story/templates/slab-opener-template.md` (or equivalent) — Composition Smoke gate amendment per AC-D + Decision #6

DO NOT review (out of scope per Path A-prime + AC-E):
- 14 × `app/specialists/<name>/graph.py` — specialists are unchanged; out of Slab 6.0 scope
- `marcus/orchestrator/m3_trial.py` — deterministic harness preserved; if modified, that's a substantive finding to flag
- `app/manifest/compiler.py` — Codex preserved-state from `c7d6447`; envelope work is runner-layer
- `app/gates/resume_api.py` — FR34 gate machinery preserved
- All `tests/specialists/<name>/test_*.py` — isolated-execution tests must remain GREEN; treat regressions as substantive findings
- Slab 6.1 surface (`production_runner.py`, `production_trial_envelope.py`, `tests/integration/marcus/test_production_runner_*.py`, `tests/live/test_production_trial_smoke.py`) — separate review (already triaged in `codex-handoff-slab-6-1-code-review.md`)
- Batch 3 ad-hoc surface (`adhoc_response.py`, `tests/integration/marcus/test_adhoc_*.py`) — separate review

**Spec inputs (Acceptance Auditor reads these):**
- `_bmad-output/implementation-artifacts/migration-6-0-production-envelope-substrate.md` — primary spec; 10 ACs (A through J) + 8 Decisions + four-file-lockstep + 5-line D12 close protocol + Operator dual-gate gate-2 evidence already pasted
- `docs/dev-guide/substrate-inventory-checklist.md` — **NEW standing checklist (N1–N12)**; Acceptance Auditor MUST trace Slab 6.0's deliverable against the relevant N-items (especially N2 composition exercise, N4 isolation invariant, N5 cross-component state-flow, N7 replay regression, N11 composition mode declared)
- `docs/dev-guide/specialist-anti-patterns.md` A15 + A16 + A17 + P3 entries — the prevention patterns this story addresses (A17 + P3 are precipitating)
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — four-file-lockstep contract for `ProductionEnvelope` + `SpecialistContribution`
- `_bmad-output/implementation-artifacts/m5-decision.md` Verdict-Integrity Annotation #2 — records the substrate-gap finding this story closes
- `_bmad-output/upstream-state.md` condition #3 — the M5 condition reframed as Slab 6.0 + 6.1 sequence

**Mode:** `"full"` (Acceptance Auditor activates; do NOT use `"no-spec"` mode).

**Project context:** existing `docs/project-context.md` + `CLAUDE.md` for repo conventions.

## Disposition rules (same as prior code reviews)

- **`patch` items:** Codex addresses in this dispatch before declaring done. Each `patch` becomes a small commit with descriptive message referencing this review file.
- **`defer` items:** file as deferred-inventory entries in `_bmad-output/planning-artifacts/deferred-inventory.md` with explicit reactivation gates; do NOT silently shelve.
- **`dismiss` items:** explain in the close note why the dismissal is justified (cosmetic NIT vs real finding). Aggressive DISMISS rubric per `docs/dev-guide/story-cycle-efficiency.md` for cosmetic-only NITs.
- **`decision_needed` items:** HALT and surface to operator with each option's tradeoff. Do not silently choose. Same halt-and-surface pattern as A15/A16/A17 instances.

## Specific things to review for substantively (Acceptance Auditor focus)

The reviewers should pay particular attention to:

1. **AC-A `ProductionEnvelope` four-file-lockstep integrity** — model + JSON Schema + 5 shape-pin tests + golden fixture all present and consistent. Verify: `model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)`; `schema_version: Literal["production-envelope.v1"]` red-rejects other strings; `contributed_at` is tz-aware (rejects naive datetime); `cost_usd >= 0.0`; `add_contribution` raises if `specialist_id` already present (immutability invariant — the load-bearing invariant for replay-regression). Cross-check JSON Schema emission matches Pydantic model exactly (no drift). Golden fixture round-trips.

2. **AC-B `ProductionDispatchAdapter.invoke_specialist(...)` contract correctness** — the adapter is the ONLY surface that knows about envelope-vs-cache_prefix shape differences. Verify:
   - Input construction: `dependency_map: dict[str, str]` (downstream-input-key → upstream-specialist-id) is correctly used to look up upstream contributions and inject them into the constructed `RunState.cache_state.cache_prefix` (or wherever the specialist expects to read its input). Specialists MUST NOT read from `production_envelope` directly.
   - Specialist invocation: adapter calls the specialist's compiled subgraph (NOT just the `_act` node directly — the full 9-node scaffold runs, including per-specialist `gate_decision`). If the adapter bypasses the specialist's gate, that's a substantive finding (it would re-introduce the Slab 6.1 first-attempt compose-without-invoke defect).
   - Output extraction: adapter pulls specialist output from `RunState.cache_state` after the subgraph completes, builds a `SpecialistContribution`, and appends to the envelope. Verify the SHA256 `output_digest` is computed against canonical JSON (sort_keys=True, separators=(",",":"))) so replay-regression is reproducible.
   - Returns updated envelope with new contribution appended; original envelope unmodified (immutability at the envelope level too — adapter copies + appends, doesn't mutate input).

3. **AC-C Texas → cd chain test is the load-bearing test** — this is the EXACT scenario that Codex's Slab 6.1 strict-AC HALT discovered failing. Verify:
   - Test exercises `ComposedSpecialistChainHarness` end-to-end with ≥2 real specialists (Texas + cd) through `ProductionDispatchAdapter`
   - Test asserts envelope-state propagation, NOT just output equality (the specific assertion shape — does the test check that cd's input was constructed by reading Texas's contribution from envelope? if it just checks final output equality without checking the data-flow path, that's a substantive finding)
   - Test pins envelope contribution accumulation (Texas contribution present + cd contribution present + ordering preserved + immutability honored)
   - Synthetic specialist outputs at the LLM-call boundary (cost ~$0); verify the test does NOT silently call live OpenAI

4. **AC-E specialist isolation invariant preserved** — `tests/composition/test_specialist_isolation_preserved.py` should parametrize across all 14 specialists (or collapse equivalently per Murat M-R18 same-property collapse rule). Verify:
   - Each specialist's isolated-execution path still works (build the scaffold, run `_plan` + `_act`, verify state shape)
   - No specialist contract was modified in the diff (cross-check `git status` against `app/specialists/<name>/graph.py` paths)
   - M3 deterministic harness at `marcus/orchestrator/m3_trial.py` is UNCHANGED (if modified, substantive finding — that's the replay-regression baseline)

5. **AC-D Composition Smoke gate amendment shape** — verify the amendment to `skills/bmad-create-story/templates/slab-opener-template.md` (or the equivalent template path Codex chose) actually contains:
   - Explicit "Composition Smoke" required step at slab-opener authoring time
   - PASS-or-FAIL records as vote-evidence
   - Failing-smoke disposition rules (re-scope OR defer OR explicit-composition-shape-vote with named gap)
   - Cross-check that `tests/migration/test_composition_smoke_template_present.py` actually exercises these elements (does the test grep for the literal step name + disposition wording, or does it just check for any line containing "composition"? the former is correct; the latter is a defect).

6. **AC-F A17 + P3 entries-present test** — verify `tests/migration/test_a17_p3_entries_present.py` actually checks the entries are in the correct subheadings (A17 under "Post-Cycle Harvest"; P3 under "Process Anti-Patterns") + four-field-format honored (Entry ID + Pattern Name + Counter-Pattern + Counter-Discipline / Counter-Test). If the test just greps for "A17" and "P3" anywhere in the file, that's insufficient.

7. **Substrate Inventory Checklist application traceability (NEW; per the standing checklist)** — for the Slab 6.0 implementation, the Acceptance Auditor MUST trace each relevant N-item:
   - **N2 (Composition exercise before vote):** does the Texas → cd chain test actually exercise composition end-to-end? Cited evidence: 17 passed in 1.21s.
   - **N4 (Per-component isolation invariant preserved post-composition):** does AC-E's parametrized test cover all 14 specialists?
   - **N5 (Cross-component state-flow contract):** is the dependency_map mechanism complete and tested? Are missing-dependency / circular-dependency cases handled?
   - **N7 (Replay regression verifies execution path):** does `output_digest` actually enable replay? Has 5a.1 replay regression been re-run after Slab 6.0 to confirm no breakage?
   - **N11 (Composition mode declared alongside isolated mode):** is composition mode now first-class in the contract via `ProductionEnvelope` + `ProductionDispatchAdapter`?

8. **Pydantic v2 strict on `RunState` extension** — verify the `production_envelope: ProductionEnvelope | None = None` field on `RunState`:
   - Doesn't break existing schema-pin tests (the cited 34 passed already covers this; cross-check the test count was actually 34 not, e.g., 33 silently suppressed)
   - JSON Schema for `RunState` correctly emits the new optional field
   - Default `None` is correct (specialists not running in composition mode keep envelope=None; isolated-execution paths unchanged)

9. **Path A-prime invariants honored** — the operator-binding decision was: envelope ALONGSIDE `cache_prefix`, NOT replacing or wrapping it; specialists STAY UNCHANGED; adapter at runner layer is the ONLY surface that bridges. Verify no silent shortcuts:
   - No specialist code reads `production_envelope` directly (grep for `production_envelope` in `app/specialists/`)
   - No direct mutation of `cache_state.cache_prefix` from envelope-aware code (grep for `cache_prefix` writes outside specialist scaffold)
   - Adapter is the only place that holds knowledge of both shapes

10. **Cost-engineering integration with envelope cost rollup (N8 from substrate inventory checklist)** — `SpecialistContribution.cost_usd` is captured per-contribution. Verify:
    - The cost field is populated correctly (not zero by default; actual cost flows from specialist execution)
    - Envelope-level cost rollup is straightforward (sum across contributions); even if not implemented yet, the contract makes it trivial

## Things NOT to flag

- Substrate inheritance from prior Slabs (don't re-litigate Slab 5a closure or M5 reframe)
- Per-specialist code in `app/specialists/<name>/graph.py` (specialists are scaffold-conformant; out of Slab 6.0 scope)
- Manifest compiler internals (per Path A-prime; envelope work is runner-layer; out of scope unless specialist code accidentally got modified)
- WondercraftClient or NotionClient or ScittProvider (not invoked by Slab 6.0; out of scope)
- Slab 6.1 surface (already triaged in separate dispatch)
- Batch 3 ad-hoc surface (already triaged or out of scope)
- Cosmetic NITs that don't change behavior, schema, or contract — apply aggressive DISMISS per `docs/dev-guide/story-cycle-efficiency.md`

## Sequencing

Same as prior reviews:
1. Three layers run in parallel (Blind Hunter + Edge Case Hunter + Acceptance Auditor)
2. Triage merges + classifies
3. Codex addresses `patch` items in commits
4. Codex files `defer` items in deferred-inventory
5. Codex documents `dismiss` justifications
6. Codex surfaces `decision_needed` items to operator (do NOT silently choose)

## Deliverable

Triaged punch list at `_bmad-output/implementation-artifacts/6-0-code-review-2026-04-27.md` with:
- Per-layer findings (Blind Hunter / Edge Case Hunter / Acceptance Auditor)
- Per-finding triage classification (patch / defer / dismiss / decision_needed)
- For each `patch`: which commit addresses it
- For each `defer`: which deferred-inventory entry was filed
- For each `dismiss`: justification (1-2 sentences max)
- For each `decision_needed`: option list + tradeoffs surfaced to operator
- **Required §Substrate Inventory Checklist Trace section (NEW; first-class deliverable, NOT optional)** — explicit per-N-item table covering ALL twelve N-items (N1–N12) from `docs/dev-guide/substrate-inventory-checklist.md`. Schema:

  | N-item | Applicability to Slab 6.0 | Trace evidence | Verdict |
  |---|---|---|---|
  | N1 — External-provider resource ID validity | applicable / not-applicable / partial | cite the specific test/file/line that exercises the item, OR explain why not-applicable | PASS / FAIL / N/A / decision_needed |
  | N2 — Composition exercise before vote | applicable | `tests/composition/test_texas_to_cd_chain.py` (operator dual-gate gate-2 PASS 17/17 in 1.21s) | PASS |
  | N3 — Live-API smoke before MVP close | … | … | … |
  | N4 — Per-component isolation invariant preserved post-composition | … | … | … |
  | N5 — Cross-component state-flow contract | … | … | … |
  | N6 — Gate boundary scope hierarchy | … | … | … |
  | N7 — Replay regression verifies execution path | … | … | … |
  | N8 — Cost machinery integration with real trace data | … | … | … |
  | N9 — Operator-witnessed evidence at M-gate vote | … | … | … |
  | N10 — Anti-pattern catalog read at architecture-authoring time | … | … | … |
  | N11 — Composition mode declared alongside isolated mode | … | … | … |
  | N12 — Auth model verified via probe | … | … | … |

  Rules for the trace section:
  1. **All twelve rows present.** No N-item may be omitted. "not-applicable" is a valid applicability disposition but must be explicitly named with a 1-sentence rationale (e.g., "N12 not-applicable; Slab 6.0 substrate doesn't introduce any external auth surface — composition tests use synthetic specialist outputs at the LLM-call boundary").
  2. **Trace evidence must cite concrete artifacts** (test file path + count, AC ID + spec line, commit SHA, etc.). Hand-waving like "covered by AC-E" without naming the specific test fails the trace.
  3. **Verdicts:** PASS = N-item satisfied with concrete evidence; FAIL = N-item applicable but evidence missing or insufficient (becomes a `patch` triage item in the same review); N/A = explicitly not-applicable per the rationale rule above; decision_needed = the N-item's applicability or evidence shape requires operator judgment.
  4. **FAIL verdicts auto-promote to `patch` items** in the main triage above and link bidirectionally (the `patch` item references the N-row; the N-row references the `patch` item ID).
  5. **N13+ extensions:** if Codex discovers a NEW substrate concern during review that doesn't fit any N-item, propose an N13+ entry in this section (Item / Verification / PASS criteria / Anti-patterns it would catch) AND file a parallel proposal at `docs/dev-guide/substrate-inventory-checklist.md` per the checklist's extension protocol. New N-items require operator ratification before becoming standing — propose, don't unilaterally add.
- Final sentence: "All `patch` items addressed in commits; all `defer` items filed in deferred-inventory; all `dismiss` items justified above; `decision_needed` items surfaced to operator; substrate inventory trace complete with N-items 1–12 verdicts recorded. Slab 6.0 ready for `review → done` flip pending operator confirmation." (Or, if any `decision_needed` items are open OR any N-item FAIL verdicts remain unpatched, replace with: "Operator decision needed on N items above before `done` flip can proceed; substrate inventory trace shows X FAIL / Y decision_needed verdicts.")

## Closeout (after triage clears)

When all triage items are resolved:
1. Codex commits the implementation surface (NEW files + MODIFIED files) as themed commit(s); follow `feat(slab-6.0): ...` convention.
2. Codex flips `migration-6-0-production-envelope-substrate: review` → `done` in `sprint-status.yaml`.
3. Codex updates `_bmad-output/upstream-state.md` condition #3 — the prior REFRAMED-AS-SLAB-6.0-SUBSTRATE-+-SLAB-6.1-RUNNER text gets a "Slab 6.0 CLOSED 2026-04-27 (or appropriate date); awaiting Slab 6.1 close" annotation.
4. Codex updates `next-session-start-here.md` if the project carries one.
5. Codex updates `_bmad-output/implementation-artifacts/m5-decision.md` §"Slab 6.0 substrate-ratification waypoint" — flip "remains `review` pending bmad-code-review" to "CLOSED <date> after bmad-code-review triage cleared."

## Substrate Inventory Checklist availability (NEW)

The standing N1–N12 substrate inventory checklist now lives at `docs/dev-guide/substrate-inventory-checklist.md`. It was authored 2026-04-27 specifically to prevent the ad hoc post-vote substrate discoveries that produced A15 + A16 + A17 + P3. Every Codex slab dispatch from this point forward must:
1. Read the checklist at T1
2. Identify which N-items apply to the slab in scope
3. Have the Acceptance Auditor (in code review) verify each applicable N-item is honored
4. If a NEW substrate concern surfaces during a slab that doesn't fit any N-item, file as N13+ extension via the checklist's extension protocol

For Slab 6.0 itself, the Acceptance Auditor focus list above (item 7) names the relevant N-items. Honor them.
