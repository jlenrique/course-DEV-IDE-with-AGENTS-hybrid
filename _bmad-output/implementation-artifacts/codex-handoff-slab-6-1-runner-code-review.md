# Codex dispatch: bmad-code-review on Slab 6.1 runner-consumes-substrate rewire

**Session:** 2026-04-27 (operator-authorized post-Slab-6.1-implementation-and-operator-witnessed-live-smoke)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Slab 6.0 (`migration-6-0-production-envelope-substrate.md`) CLOSED 2026-04-27 (commits `072724c` + `7812d3e`; review at `6-0-code-review-2026-04-27.md`)
- Slab 6.1 rewire LANDED 2026-04-27 (commit `d5cfad8` — `feat(slab-6.1): rewire production runner to consume Slab 6.0 substrate`)
- Codex-side verification: focused Slab 6.1 suite → 49 passed; composition + isolation + cost + trace slices included; ruff clean on touched files
- **Codex-side live smoke: `pytest tests/live/test_production_trial_smoke.py -m live -q --tb=short` → 1 passed in 31.75s**; envelope contributions `['texas', 'irene']`; cost report `total_cost_usd = 0.0325215`; texas + irene reached through adapter (real LLM-invoking path exercised)
- Story status: `review` (correctly held pending bmad-code-review per CLAUDE.md §3)
- Substrate Inventory Checklist standing at `docs/dev-guide/substrate-inventory-checklist.md` (N1–N12 binding)
- Composition Specification standing at `docs/dev-guide/composition-specification.md` (Option B / Path A-prime; §3 + §10 + §12 will be updated post-review)

**Operator dispositions ratified 2026-04-27 (BINDING; informs Acceptance Auditor):**
1. **dependency_map source — DEFERRED.** Codex's deterministic fallback (Texas → CD maps as `source_bundle`; other downstream calls use `upstream_output`) is accepted as Slab 6.1 close shape. Manifest promotion filed as `migration-6-2-promote-dependency-map-into-manifest` (~1pt) Tier A prerequisite story. Composition Spec §3.6 + §10 + §12 will document this known fallback at close.
2. **Multi-pass / repeated specialist nodes — RATIFIED PATH Z.** Accept "first contribution wins" semantics as Slab 6.1 contract. Codex's current behavior (skip duplicate specialist contributions after first) is the agreed close shape. Path X (node-scoped contribution identity) and Path Y (per-pass envelope) filed as deferred enhancements when actual multi-pass production need emerges. Composition Spec §3.1 + §10 + §12 will document this known limitation at close.
3. **Replay regression pre-existing pack-hash drift — DEFERRED, NOT A SLAB-6.1 BLOCKER.** Drift (`013b7ef → 19cde78` + override confirm token / cost field diffs) is unrelated to Slab 6.1 rewire. Filed as `replay-regression-pack-hash-drift-pre-slab-6.1` deferred-inventory entry. Investigate separately (likely needs golden refresh after Slab 6.0 substrate landed but before 6.1 rewire).

**Mission:** independent multi-layer code review on the Slab 6.1 rewire diff per the dual-gate `substrate_shape` + `operator_acceptance_gate` rationale. Operator-side live smoke just cleared (Codex-side 31.75s pass). The remaining formal-close gate is independent code review with triage discipline. **Do not take Codex's self-dispositions as conclusive — Acceptance Auditor independently traces all three ratified-disposition items against the actual diff.**

## Why this dispatch exists

Slab 6.1 (`migration-6-1-production-graph-runner.md`) is dual-gate per `substrate_shape` (composition layer is new substrate) + `operator_acceptance_gate` (first real production trial is operator-verified). Codex-side live smoke just cleared (1 passed in 31.75s; cost $0.0325215; texas + irene contributions present). Operator-side dual-gate gate-2 will run after triage clears. The remaining formal-close gate is independent code review with triage discipline.

This is `bmad-code-review`, NOT the lighter `bmad-review-adversarial-general` standalone — three layers (Blind Hunter + Edge Case Hunter + Acceptance Auditor) + triage into patch / defer / dismiss / decision_needed. The Acceptance Auditor layer is load-bearing here because:
1. The Slab 6.1 spec has 12 ACs (A through L) plus the integration-exercise AC per A16 counter-pattern
2. Operator has ratified three specific dispositions (named above) — Auditor independently re-traces each against the diff
3. The substrate this rewire consumes (Slab 6.0 envelope + adapter) is fresh; integration correctness has to be verified end-to-end, not assumed

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Three substantive A16 instances surfaced today across M2/M3/Slab-6.1 prep work; the A16 prevention pattern is working but only because we've been running integration-exercise checks. This code review is the next instance of that discipline — it should surface anything subtle in the production-runner composition that the live smoke didn't exercise.

## Scope

**Diff input:** Slab 6.1 implementation changes in commit `d5cfad8` ("feat(slab-6.1): rewire production runner to consume Slab 6.0 substrate"). Compute the actual file list at run time via `git show d5cfad8 --stat`. Per Codex's report, ~18 files across:
- `app/marcus/orchestrator/production_runner.py` (rewired specialist invocation loop; replaces `_invoke_specialist_probe` with `ProductionDispatchAdapter.invoke_specialist`; carries `ProductionEnvelope` through graph traversal)
- `app/models/runtime/production_trial_envelope.py` (extended with embedded `production_envelope` field)
- `schema/production_trial_envelope.v1.schema.json` (regenerated; embedded envelope shape)
- `tests/fixtures/runtime/production_trial_envelope_golden.json` (regenerated)
- `tests/integration/marcus/test_production_runner_invocation.py` (updated assertions: adapter path, not probe path)
- `tests/integration/marcus/test_production_runner_gate_pause_resume.py` (per-specialist gate semantics under adapter dispatch)
- `tests/integration/marcus/test_production_clone_launch_evidence_discipline.py` (live mode runs through adapter)
- `tests/live/test_production_trial_smoke.py` (envelope contributions + LangSmith trace assertions)
- `app/manifest/compiler.py` (compiler/CLI support)
- `app/marcus/cli/trial.py` (CLI wiring)
- `state/config/dispatch-registry.yaml` (registry updates if any)
- `docs/dev-guide/langgraph-migration-guide.md` (§"Production Runner" updates)
- `_bmad-output/implementation-artifacts/sprint-status.yaml` (annotation update)
- pytest config + 1-2 other support files

NOT in scope (per Path A-prime + Slab 6.0 invariants; treat any modification as substantive finding):
- 14 × `app/specialists/<name>/graph.py` — specialists must remain unchanged
- `marcus/orchestrator/m3_trial.py` — deterministic harness preserved
- `app/models/runtime/production_envelope.py` — Slab 6.0 substrate; do not modify
- `app/marcus/orchestrator/dispatch_adapter.py` — Slab 6.0 substrate; do not modify
- `app/models/state/run_state.py` — `production_envelope` field already added in Slab 6.0
- Anti-pattern catalog (`docs/dev-guide/specialist-anti-patterns.md`) — A17 + P3 already filed
- Composition Specification (`docs/dev-guide/composition-specification.md`) — operator updates §3 + §10 + §12 at close, not Codex via review

**Spec inputs (Acceptance Auditor reads these):**
- `_bmad-output/implementation-artifacts/migration-6-1-production-graph-runner.md` — primary spec (already re-scoped per Slab 6.0 AC-J; line 14 rescope note: "imports and consumes ProductionEnvelope + ProductionDispatchAdapter from Slab 6.0")
- `_bmad-output/implementation-artifacts/codex-handoff-slab-6-1-runner-consumes-substrate.md` — the dispatch that drove this implementation
- `docs/dev-guide/substrate-inventory-checklist.md` — N1–N12 standing checklist; Acceptance Auditor MUST trace per-N applicability
- `docs/dev-guide/composition-specification.md` — Option B contract; particularly §3.1 (envelope invariants), §3.3 (adapter), §3.5 (gate precedence), §3.6 (dependency_map sourcing), §3.7 (persistence)
- `docs/dev-guide/specialist-anti-patterns.md` A15 + A16 + A17 + P3 entries — prevention patterns this story addresses
- `docs/dev-guide/pydantic-v2-schema-checklist.md` — four-file-lockstep contract for `ProductionTrialEnvelope`
- `_bmad-output/implementation-artifacts/m5-decision.md` Verdict-Integrity Annotations + Slab 6.0 substrate-ratification waypoint
- `_bmad-output/upstream-state.md` condition #3 (will RESOLVE at this story's close)
- `_bmad-output/implementation-artifacts/6-0-code-review-2026-04-27.md` — Slab 6.0 review for shape reference

**Mode:** `"full"` (Acceptance Auditor activates; do NOT use `"no-spec"` mode).

**Project context:** existing `docs/project-context.md` + `CLAUDE.md` for repo conventions.

## Disposition rules

- **`patch` items:** Codex addresses in this dispatch before declaring done. Each `patch` becomes a small commit with descriptive message referencing this review file.
- **`defer` items:** file as deferred-inventory entries in `_bmad-output/planning-artifacts/deferred-inventory.md` with explicit reactivation gates; do NOT silently shelve.
- **`dismiss` items:** explain in close note why the dismissal is justified (cosmetic NIT vs real finding). Aggressive DISMISS rubric per `docs/dev-guide/story-cycle-efficiency.md` for cosmetic-only NITs.
- **`decision_needed` items:** HALT and surface to operator with each option's tradeoff. Do not silently choose. Same halt-and-surface pattern as A15/A16/A17 + Slab 6.0 instances.

**Important:** the three operator-ratified dispositions above (dependency_map deferral; multi-pass Path Z; replay-regression-drift deferral) are BINDING — do NOT re-litigate them. Acceptance Auditor independently traces whether the diff CORRECTLY implements them; that's different from re-deciding the dispositions themselves.

## Specific things to review for substantively (Acceptance Auditor focus)

The reviewers should pay particular attention to:

1. **AC-A real-handler resolution unchanged from Slab 6.0 close** — `compile_run_graph(...)` should still resolve specialist graph builders for the run lane per Slab 6.0 close shape. If the rewire modified compiler-side resolution, verify it's intentional + correct.

2. **AC-B production runner specialist invocation via `ProductionDispatchAdapter`** — verify the rewire actually replaces `_invoke_specialist_probe` (the one-shot `handle.chat.invoke` pattern from the pre-HALT first attempt) with `adapter.invoke_specialist(specialist_id=..., envelope=current_envelope, dependency_map=...)` calls. Specifically:
   - Grep for any remaining `handle.chat.invoke(` calls in `production_runner.py` outside of fallback / debug paths — if any specialist is invoked via `handle.chat.invoke` as the primary path, that's a substantive finding (compose-without-invoke vestige)
   - Verify `_invoke_specialist_probe` is removed OR explicitly demoted to a non-production diagnostic helper
   - Verify the adapter call uses the FULL specialist subgraph (not just `_plan` + `_act`); the per-specialist `gate_decision` interrupt should fire within `invoke_specialist`
   - Verify envelope is carried through graph traversal correctly: returned-envelope-with-new-contribution becomes input to the next specialist call

3. **AC-C `ProductionTrialEnvelope` four-file-lockstep integrity post-extension** — model + JSON Schema + 5+ shape-pin tests + golden fixture all present and consistent for the new embedded `production_envelope: ProductionEnvelope` field. Verify:
   - `model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)` preserved
   - Embedded envelope is properly typed (not `dict[str, Any]` shortcut)
   - Schema emission matches Pydantic model exactly (no drift)
   - Golden fixture round-trips
   - Existing trial envelope shape pins still pass (no silent contract regression)

4. **AC-D HIL gate pause/resume per FR34 — preserved under adapter dispatch** — verify production-level gate-node execution still persists LangGraph checkpoint + emits the right DecisionCard kind (G1/G2C/G3/G4) + accepts `OperatorVerdict` via `app/gates/resume_api.py::resume_from_verdict` + restores state from checkpoint. Tamper-evidence (decision-card-digest binding + anti-replay tuple per Story 3.3 W-R1-3.3-2) preserved. NO bypass paths.

5. **AC-E LangSmith trace binding with trial_id under adapter dispatch** — verify the trace context wraps the entire trial invocation; specialist node calls become child runs within the parent trace; `app/runtime/economics.py::measure_trial_cost(trial_id)` filter actually finds spans by `extra.metadata.trial_id == trial_id`. Specifically: the adapter should propagate trace context into specialist subgraph invocations so per-specialist spans appear as children of the trial span, not as orphaned root spans.

6. **AC-F evidence discipline under adapter dispatch** — `production_clone_launch_evidence` flips to `True` ONLY after at least one real specialist call completes through the adapter (NOT the probe). Offline mode (per `--allow-offline-cost-report` or absent OPENAI_API_KEY) keeps evidence at `False`. No silent paths to `True` without real adapter invocation.

7. **AC-G live smoke assertions** — `tests/live/test_production_trial_smoke.py` should now assert envelope contributions present at trial close + LangSmith trace shows child runs from adapter invocations. Verify the test isn't just asserting "trial ran" but is actually exercising envelope semantics. Live smoke landed at 31.75s with $0.0325215 cost + contributions `['texas', 'irene']` per Codex's report.

8. **Path A-prime invariants honored under rewire** — the operator-binding decision was: envelope ALONGSIDE `cache_prefix`, NOT replacing or wrapping it; specialists STAY UNCHANGED; adapter at runner layer is the ONLY surface that bridges. Verify no silent shortcuts in the rewire:
   - No specialist code reads `production_envelope` directly (grep `production_envelope` in `app/specialists/`)
   - No direct mutation of `cache_state.cache_prefix` from envelope-aware code outside the adapter
   - Adapter remains the only surface holding knowledge of both shapes

9. **Operator-ratified disposition #1 traceability (dependency_map fallback)** — Codex's report says: "Manifest does not declare dependency input keys. Current runner uses deterministic fallback: Texas -> CD maps as source_bundle; other downstream calls use upstream_output." Verify:
   - The fallback mechanism is clearly named in code (a function with a self-descriptive name like `_default_dependency_map_for(specialist_id)` — not a magic dict literal buried in the runner loop)
   - The fallback is documented inline with a comment pointing at the deferred Slab-6.2 manifest promotion follow-on
   - The fallback is testable in isolation (unit test for `_default_dependency_map_for(...)` independently from the runner)
   - Behavior under "downstream specialist requests dependency for upstream that didn't run" is fail-loud, not silent fallback (per Composition Spec §3.6 resolution rule)

10. **Operator-ratified disposition #2 traceability (multi-pass Path Z; "first contribution wins")** — Codex's report says: "Current runner skips duplicate specialist contributions after the first." Verify:
    - The skip behavior is explicit and documented in code (with a comment naming Path Z + pointing at deferred Path X / Path Y enhancement candidates)
    - The skip emits a clear log/trace event so operator can see "specialist X was invoked again at node N but envelope already contains specialist X contribution; new contribution skipped per Slab 6.1 Path Z contract"
    - There is at least ONE test asserting the skip behavior (e.g., `test_production_runner_repeated_specialist_node_skips_duplicate_contribution`)
    - The skip does not silently corrupt envelope state or break replay regression

11. **Operator-ratified disposition #3 traceability (replay-regression pack-hash drift)** — Codex's report says: "frozen graph/golden-trace slices passed, but replay suites still fail on pre-existing pack-hash drift: expected 013b7ef..., got 19cde78..., with diffs in override confirm token/cost fields." Verify:
    - The drift is genuinely pre-existing (Acceptance Auditor: check git blame on the failing assertion lines; if the assertion was authored after Slab 6.0 close, drift is post-Slab-6.0; if before, drift is genuinely pre-existing)
    - The Slab 6.1 rewire does not introduce additional drift in the same files (Acceptance Auditor: run replay-regression suite locally; compare failure set against Codex's reported drift; new failures = substantive finding)
    - The deferred-inventory entry filing is correctly scoped (just the pack-hash drift; not a broader replay-regression problem)

12. **Substrate Inventory Checklist N-item trace per the new standing discipline** — Acceptance Auditor MUST trace each applicable N-item against the diff. Per the Slab 6.1 dispatch's pre-flagged N-items: N2, N3, N4, N5, N6, N7, N8, N9, N11. N1, N10, N12 are N/A. See §"Required deliverable section" below for the trace section schema.

## Things NOT to flag

- Substrate inheritance from prior Slabs (don't re-litigate Slab 5a closure or M5 reframe or Slab 6.0 close)
- Per-specialist code in `app/specialists/<name>/graph.py` (specialists are scaffold-conformant; out of Slab 6.1 scope)
- Dispatch adapter internals (Slab 6.0 substrate; out of scope unless Slab 6.1 silently modified it)
- Anti-pattern catalog or Composition Specification updates (operator handles at close, not via review)
- Cost-engineering machinery (5a.3 closed; out of scope unless production runner misuses it)
- Live-smoke tests in `tests/live/` for non-OpenAI providers (Batch 3 work; out of scope)
- WondercraftClient or NotionClient or ScittProvider (not invoked by Slab 6.1; out of scope)
- Tier A trial-experience bundle work (separate dispatch; not yet started)
- The three pre-existing dirty-tree files unrelated to Slab 6.1 work
- Cosmetic NITs that don't change behavior, schema, or contract — apply aggressive DISMISS per `docs/dev-guide/story-cycle-efficiency.md`
- The three operator-ratified dispositions themselves (do NOT re-decide; do trace whether the diff implements them correctly)

## Sequencing

Same as Slab 6.0 review:
1. Three layers run in parallel (Blind Hunter + Edge Case Hunter + Acceptance Auditor)
2. Triage merges + classifies
3. Codex addresses `patch` items in commits
4. Codex files `defer` items in deferred-inventory
5. Codex documents `dismiss` justifications
6. Codex surfaces `decision_needed` items to operator (do NOT silently choose)

## Required deliverable section

Triaged punch list at `_bmad-output/implementation-artifacts/6-1-code-review-2026-04-27.md` (or appropriate date if review crosses day boundary) with:

- Per-layer findings (Blind Hunter / Edge Case Hunter / Acceptance Auditor)
- Per-finding triage classification (patch / defer / dismiss / decision_needed)
- For each `patch`: which commit addresses it
- For each `defer`: which deferred-inventory entry was filed
- For each `dismiss`: justification (1-2 sentences max)
- For each `decision_needed`: option list + tradeoffs surfaced to operator
- **Required §Substrate Inventory Checklist Trace section (BINDING; first-class deliverable per Slab 6.0 governance)** — explicit per-N-item table covering ALL twelve N-items (N1–N12) from `docs/dev-guide/substrate-inventory-checklist.md`. Schema:

  | N-item | Applicability to Slab 6.1 | Trace evidence | Verdict |
  |---|---|---|---|
  | N1 — External-provider resource ID validity | not-applicable | Slab 6.1 introduces no new external resource IDs (OpenAI/LangSmith already covered by 5a.3 lint guard + cascade catalog) | N/A |
  | N2 — Composition exercise before vote | applicable | live smoke `pytest tests/live/test_production_trial_smoke.py -m live -q` PASSED 31.75s (operator-witnessed expected at close) | PASS |
  | N3 — Live-API smoke before MVP close | applicable | same live smoke PASSED with envelope contributions `['texas', 'irene']` + cost $0.0325215 | PASS |
  | N4 — Per-component isolation invariant preserved post-composition | applicable | `tests/composition/test_specialist_isolation_preserved.py` PASSED post-rewire | (Acceptance Auditor verifies test ran post-rewire) |
  | N5 — Cross-component state-flow contract | applicable | dependency_map fallback mechanism documented; envelope dependency flow covered; CD input built from Texas contribution | (Acceptance Auditor verifies fail-loud on missing upstream) |
  | N6 — Gate boundary scope hierarchy | applicable | per-specialist interrupts recorded by adapter; production G1/G2C/G3/G4 remain pause boundary | (Acceptance Auditor verifies precedence rule documented + tested) |
  | N7 — Replay regression verifies execution path | applicable | frozen graph/golden-trace slices PASSED; pre-existing pack-hash drift filed as deferred per disposition #3 | PASS-WITH-DEFER |
  | N8 — Cost machinery integration with real trace data | applicable | `measure_trial_cost(trial_id)` filter still finds spans correctly; cost report `total_cost_usd = 0.0325215` from real OpenAI invocation | PASS |
  | N9 — Operator-witnessed evidence at M-gate vote | applicable | Codex-side smoke 31.75s PASS; operator-side gate-2 expected at close (formal close protocol) | PASS-PENDING-OPERATOR |
  | N10 — Anti-pattern catalog read at architecture-authoring time | not-applicable | Spec authored in prior session per A15+A16+A17 entries; no new architecture authoring in this story | N/A |
  | N11 — Composition mode declared alongside isolated mode | applicable | Path A-prime declares both modes via Slab 6.0 substrate; Slab 6.1 consumes; CompositionSpec §3 documents | PASS |
  | N12 — Auth model verified via probe | not-applicable | No new external auth surface introduced; existing OPENAI_API_KEY + LANGSMITH_API_KEY paths unchanged | N/A |

  Rules for the trace section (binding per Slab 6.0 governance):
  1. **All twelve rows present.** No N-item may be omitted. "not-applicable" is a valid disposition but must be explicitly named with 1-sentence rationale.
  2. **Trace evidence must cite concrete artifacts** (test file path + count, AC ID + spec line, commit SHA, etc.). Hand-waving fails the trace.
  3. **Verdicts:** PASS = N-item satisfied with concrete evidence; FAIL = N-item applicable but evidence missing or insufficient (becomes a `patch` triage item in the same review); N/A = explicitly not-applicable per the rationale rule above; decision_needed = the N-item's applicability or evidence shape requires operator judgment. The PASS-WITH-DEFER + PASS-PENDING-OPERATOR variants above are valid where the underlying disposition is recorded explicitly.
  4. **FAIL verdicts auto-promote to `patch` items** in the main triage above and link bidirectionally (the `patch` item references the N-row; the N-row references the `patch` item ID).
  5. **N13+ extensions:** if Codex discovers a NEW substrate concern during review that doesn't fit any N-item, propose an N13+ entry in this section AND file a parallel proposal at `docs/dev-guide/substrate-inventory-checklist.md` per the checklist's extension protocol. New N-items require operator ratification before becoming standing.
- Final sentence: "All `patch` items addressed in commits; all `defer` items filed in deferred-inventory; all `dismiss` items justified above; `decision_needed` items surfaced to operator; substrate inventory trace complete with N-items 1–12 verdicts recorded. Slab 6.1 ready for `review → done` flip pending operator dual-gate gate-2 confirmation." (Or, if any `decision_needed` items are open OR any N-item FAIL verdicts remain unpatched, replace with: "Operator decision needed on N items above before `done` flip can proceed; substrate inventory trace shows X FAIL / Y decision_needed verdicts.")

## Closeout (after triage clears + operator dual-gate gate-2 cleared)

When all triage items are resolved AND operator runs live smoke with operator-witnessed evidence:
1. Codex commits any `patch` items as themed commits; follow `fix(slab-6.1): ...` or `feat(slab-6.1): ...` convention
2. Codex flips `migration-6-1-production-graph-runner: review → done` in `sprint-status.yaml`
3. Codex updates `_bmad-output/upstream-state.md` condition #3 — flip from REFRAMED-AS-SLAB-6.0-SUBSTRATE-+-SLAB-6.1-RUNNER to RESOLVED-2026-04-XX
4. Codex updates `_bmad-output/planning-artifacts/deferred-inventory.md` `5a-2-production-graph-entrypoint-substrate-gap` — flip from DEFERRED-CONTINUES to RESOLVED-2026-04-XX
5. Codex files three NEW deferred-inventory entries per operator dispositions:
   - `migration-6-2-promote-dependency-map-into-manifest` (~1pt; Tier A prerequisite — promote dependency_map declaration into manifest or registry; closes Composition Spec §12 open question)
   - `slab-6-1-multi-pass-envelope-path-x-or-y` (Path X node-scoped contribution identity OR Path Y per-pass envelope; reactivation when actual multi-pass production need emerges)
   - `replay-regression-pack-hash-drift-pre-slab-6.1` (investigate root-cause; likely needs golden refresh after Slab 6.0 substrate landed)
6. Codex updates `_bmad-output/implementation-artifacts/m5-decision.md` — file Slab 6.1 close annotation parallel to the Slab 6.0 substrate-ratification waypoint; M5 condition #3 RESOLVED at this story's close → migration verdict promotes from "SHIP for bounded-MVP scope" to unqualified SHIP
7. Codex updates `docs/dev-guide/composition-specification.md`:
   - §3.1 (envelope invariants) — add note about Path Z "first contribution wins" + cross-link to Path X / Path Y deferred entry
   - §3.6 (dependency_map sourcing) — add note about current deterministic fallback + cross-link to migration-6-2 deferred entry
   - §10 (Decision Log) — add three rows: dependency_map fallback ratified; multi-pass Path Z ratified; persistence shape = full embed (per Codex's choice)
   - §12 (Open questions) — flip resolved items; add new known-limitation rows for Path Z + dependency_map fallback
8. Codex updates `next-session-start-here.md` if present (per Slab 6.0 close finding, this file appears ignored/untracked by repo policy; Codex notes whether this still holds)

## Substrate Inventory Checklist availability

Per Slab 6.0 governance, this code review honors the standing N1–N12 trace discipline. Future Codex slab dispatches continue to require:
1. Read the checklist at T1
2. Identify which N-items apply to the slab in scope
3. Have the Acceptance Auditor (in code review) verify each applicable N-item is honored
4. File N13+ extensions if a NEW substrate concern surfaces

For this Slab 6.1 review specifically, the N-item table above is pre-populated with operator-anticipated applicability; Acceptance Auditor verifies each entry independently against the actual diff and updates verdicts accordingly.

## What this dispatch does NOT do

- Does NOT touch Slab 6.0 substrate (envelope + adapter; out of scope; treat any modification as substantive finding)
- Does NOT re-litigate the three operator-ratified dispositions (do trace whether diff implements them correctly; do not re-decide them)
- Does NOT update Composition Specification or anti-pattern catalog (operator handles at close)
- Does NOT pre-author Slab 6 trial-experience bundle work (separate dispatch already authored at `codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md` for hand-off after Slab 6.1 formal close)
