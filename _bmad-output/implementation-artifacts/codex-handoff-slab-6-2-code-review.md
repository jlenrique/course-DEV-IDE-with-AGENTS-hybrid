# Codex dispatch: bmad-code-review on Slab 6.2 dependency_map manifest promotion

**Session:** 2026-04-27 (operator-authorized post-Slab-6.2-implementation)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Slab 6.2 implementation landed in commit `01631b6` (`feat(slab-6.2): promote dependency_map declaration into pipeline manifest`)
- Codex-side verification: dispatch-requested focused regression → 24 passed; broader manifest/runner regression → 80 passed; 11 new dependency tests passed; ruff clean on touched code/test files; manifest compile still 33 nodes / 34 edges (no topology drift); pre-existing tests remained GREEN
- No decision_needed items surfaced; no halt triggers fired
- All 8 BINDING party-mode riders applied per spec; M-R4 NON-BLOCKING isolated unit test included; W-R3 + P-R3 + A-R3 NON-BLOCKING items pending close protocol
- Story status: `review` (correctly held pending bmad-code-review per CLAUDE.md §3 + discipline doc Gate 3)
- Composition Spec §3.6 + §10 + §12 updates landed; migration guide §"Production Runner" augmented; governance JSON version bumped + amendment log entry; sprint-status flipped to review

**Operator dispositions (BINDING; informs Acceptance Auditor):**
- All 8 spec-applied BINDING riders (W-R1 PERMANENT framing; W-R2 regression-prevention test; M-R1 + M-R2 fail-loud tests; M-R3 K-floor 7→9 + target 10→12; P-R1 §3.6 PERMANENT language; P-R2 generator-emit cross-ref; A-R1 Phase 1 pre-flight; A-R2 named halt candidates) per ratified party-mode green-light. Acceptance Auditor independently traces; does NOT re-litigate.
- 3 NON-BLOCKING riders apply at this code-review or formal close: W-R3 circular-check verification (Codex implementation included this); M-R4 isolated `_resolve_dependency_map` unit test (Codex implementation included this); P-R3 deferred-inventory `Last refreshed:` line update (applies at formal close, not code review).

**Mission:** independent multi-layer code review on the Slab 6.2 diff per single-gate rationale. Surface any defects before formal `done` flip. Same template as Slab 6.0 + 6.1 reviews — three layers (Blind Hunter + Edge Case Hunter + Acceptance Auditor) + triage + N-item trace deliverable section.

## Why this dispatch exists

Slab 6.2 is single-gate per `migration-story-governance.json` ("minor schema extension; no new substrate; preserves backward-compat via fallback retention; no composition-shape change"). Single-gate stories do NOT require operator-witnessed dual-gate gate-2 live evidence per `docs/dev-guide/story-cycle-efficiency.md`. They DO require bmad-code-review per CLAUDE.md §3 before flipping to done.

**Operator preference (binding):** "do it right, no band-aids, only rational trade-offs that get named in writing." Three-layer review with aggressive DISMISS rubric for cosmetic NITs per `docs/dev-guide/story-cycle-efficiency.md`.

## Scope

**Diff input:** Slab 6.2 implementation changes in commit `01631b6`. Compute file list at run time via `git show 01631b6 --stat`. Per Codex report, 9 files:
- `app/manifest/schema.py` — `NodeSpec.dependencies: dict[str, str] | None` field
- `app/manifest/compiler.py` — `_validate_dependency_cycles(...)` cycle check; called at compile
- `app/marcus/orchestrator/production_runner.py` — `_resolve_dependency_map` manifest-first + permanent fallback retention; `MissingUpstreamContributionError` exception + `_ensure_upstream_contributions_present(...)` fail-loud per Composition Spec §3.6
- `state/config/pipeline-manifest.yaml` — per-node `dependencies:` declarations (Texas → CD `source_bundle`; downstream `upstream_output`)
- `tests/integration/manifest/test_manifest_dependencies_field.py` (NEW) — 4 AC-A schema tests
- `tests/integration/marcus/test_production_runner_dependency_resolution.py` (NEW) — 7 tests (AC-B 1-3 + M-R1 + M-R2 + W-R2 + M-R4)
- `docs/dev-guide/composition-specification.md` — §3.6 + §10 Decision Log + §12 known limitation #1 RESOLVED
- `docs/dev-guide/langgraph-migration-guide.md` — §"Production Runner" augment
- `docs/dev-guide/migration-story-governance.json` — version bump + amendment log entry

NOT in scope (treat any modification as substantive finding):
- `app/models/runtime/production_envelope.py` (Slab 6.0 substrate)
- `app/marcus/orchestrator/dispatch_adapter.py` (Slab 6.0 substrate)
- `app/models/runtime/production_trial_envelope.py` (Slab 6.1 close shape)
- 14 × `app/specialists/<name>/graph.py` (specialists unchanged)
- `marcus/orchestrator/m3_trial.py` (deterministic harness preserved)
- Anti-pattern catalog (no new entries expected; A12 partial mitigation already named)

**Spec inputs (Acceptance Auditor reads these):**
- `_bmad-output/implementation-artifacts/migration-6-2-promote-dependency-map-into-manifest.md` — primary spec; party-mode-ratified BINDING riders applied; 12 ACs + Decisions + party-mode block
- `_bmad-output/implementation-artifacts/codex-handoff-slab-6-2-promote-dependency-map.md` — the dispatch that drove this implementation
- `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md` — BINDING governance per CLAUDE.md
- `docs/dev-guide/substrate-inventory-checklist.md` — N1–N12; Auditor MUST trace per-N applicability
- `docs/dev-guide/composition-specification.md` — particularly §3.6 (dependency_map sourcing), §10 Decision Log, §12 known limitation #1
- `docs/dev-guide/specialist-anti-patterns.md` — A12 (procedural-coupling) + A9 (Epic-doc structural-name drift) + A17 + P3 entries

**Mode:** `"full"` (Acceptance Auditor activates).

## Disposition rules

Standard:
- **`patch` items:** Codex addresses in commits before declaring done
- **`defer` items:** file as deferred-inventory entries with explicit reactivation gates
- **`dismiss` items:** justify in close note; aggressive DISMISS per story-cycle-efficiency.md for cosmetic NITs
- **`decision_needed` items:** HALT and surface to operator with each option's tradeoff

Important: 8 operator-ratified BINDING riders + 3 NON-BLOCKING riders are BINDING; do NOT re-litigate. Trace whether the diff CORRECTLY implements them (different from re-deciding).

## Specific things to review for substantively (Acceptance Auditor focus)

1. **NodeSpec.dependencies field shape correctness** — Pydantic v2 type `dict[str, str] | None`; Field default; validator behavior on non-dict shapes (per AC-A test 3); empty dict accepted (per AC-A test 1); declared dict accepted (per AC-A test 2). Verify field doesn't accidentally become required (would break existing manifest entries that omit it).

2. **`_validate_dependency_cycles(...)` correctness (W-R3 NON-BLOCKING)** — verify the cycle check actually detects cycles end-to-end. Cycle detection algorithm (DFS with path tracking); error message names the offending cycle nodes; called at BOTH compile-time entry points (per Codex's grep showing lines 398 + 423). Test pin: AC-A test 4 (`test_schema_rejects_circular_dependencies_at_compile_time`) covers; verify it actually exercises the cycle path, not just declaration.

3. **`_resolve_dependency_map(node, specialist_id, production_envelope)` precedence + permanent fallback (W-R1 + P-R1 BINDING)** — manifest-declared dependencies precede fallback; fallback used when `node.dependencies` is None OR empty dict. Verify code comments + docstrings frame fallback as PERMANENT (not deprecated/transitional). Grep for any "TODO" / "deprecated" / "transitional" / "temporary" comments near the fallback function or its call site — those would be substantive findings.

4. **`MissingUpstreamContributionError` exception design** — exception class signature includes `specialist_id` + `downstream_input_key` + `downstream_specialist_id` (3-field signature per `production_runner.py:251`); error message text includes all three values; raises BEFORE any state mutation (fail-loud at the dependency resolution boundary, not after partial work).

5. **`_ensure_upstream_contributions_present(...)` fail-loud coverage (M-R1 + M-R2 BINDING)** — function iterates dependency_map; checks each upstream specialist's contribution presence in envelope; raises with explicit field naming per Composition Spec §3.6 fail-loud rule. Test pins AC-B test 4 + 5 (M-R1 + M-R2) cover; verify they assert the EXCEPTION TYPE + the specific message fields, not just "exception raised."

6. **`_default_dependency_map_for(...)` PERMANENT framing (W-R1)** — function docstring + any nearby comments describe fallback as the resolution mechanism for nodes that opt out of explicit declaration; NOT as "until manifest promotion lands" or similar transitional language.

7. **Pipeline manifest declarations correctness** — verify each `dependencies:` entry in `state/config/pipeline-manifest.yaml` matches the prior runner-layer fallback behavior (Texas → CD = `source_bundle`; downstream specialists = `upstream_output: <prior-specialist-id>`). Verify AT LEAST one node intentionally omits `dependencies:` to exercise the permanent-fallback path (per W-R2 regression-prevention test requirement).

8. **W-R2 regression-prevention test (AC-B test 6) correctness** — `test_fallback_path_unchanged_for_undeclared_existing_manifest_node` — pins ONE existing manifest node WITHOUT `dependencies:` declaration; verifies trial-run output identical to pre-implementation baseline. Verify the test actually picks an existing node (not synthetic), runs the full resolution path, asserts envelope contributions identical.

9. **M-R4 NON-BLOCKING isolated unit test correctness** — `test_resolve_dependency_map_prefers_declared_map` (per Codex screen output line 291) — verify it tests `_resolve_dependency_map(...)` in isolation (not via runner integration); pins the precedence rule at the function boundary.

10. **Composition Spec §3.6 update language (W-R1 + P-R1 BINDING)** — verify §3.6 text includes the explicit "fallback retention is permanent" framing. Auditor reads the actual updated §3.6 in `docs/dev-guide/composition-specification.md` and confirms a future reader cannot interpret fallback as transitional.

11. **Composition Spec §10 Decision Log row + §12 known limitation #1 flip** — verify §10 has the new row dated 2026-04-27 naming the manifest promotion + permanent fallback; verify §12 known limitation #1 flipped from RESOLVED-WITH-DEFERRAL → RESOLVED with concrete commit cite.

12. **Migration guide §"Production Runner" augment (AC-J item 3)** — verify documentation accurately describes the manifest-as-source-of-truth pattern + permanent fallback semantics + `MissingUpstreamContributionError` fail-loud behavior.

13. **Schema-pin drift refresh correctness** — Codex reported "schema-pin drift for NodeSpec and PipelineManifest" was refreshed because the schema extension is intentional. Verify the schema-pin tests now pin the NEW shape (not stale), and the refresh wasn't accidentally suppressed by removing the test.

14. **Path A-prime invariants honored** — no specialist code modified; no envelope/adapter changes; no Slab 6.0 substrate touched; no Slab 6.1 trial envelope shape changed. Grep `app/specialists/` and `app/models/runtime/production_envelope.py` and `app/marcus/orchestrator/dispatch_adapter.py` for any modifications in this commit.

## Required deliverable section

Triaged punch list at `_bmad-output/implementation-artifacts/6-2-code-review-2026-04-27.md` with:

- Per-layer findings (Blind Hunter / Edge Case Hunter / Acceptance Auditor)
- Per-finding triage classification (patch / defer / dismiss / decision_needed)
- For each `patch`: which commit addresses it
- For each `defer`: which deferred-inventory entry was filed
- For each `dismiss`: justification (1-2 sentences max)
- For each `decision_needed`: option list + tradeoffs surfaced to operator
- **Required §Substrate Inventory Checklist Trace section (BINDING per Slab 6.0 governance + discipline doc Gate 3)** — 12-row table covering N1–N12 with verdict (PASS / FAIL / N/A / decision_needed) + concrete trace evidence per row. Pre-populated applicability:

  | N-item | Applicability | Pre-populated guidance |
  |---|---|---|
  | N1 — External-provider resource ID validity | N/A | No new external resource IDs introduced |
  | N2 — Composition exercise before vote | N/A | No vote-shape change |
  | N3 — Live-API smoke before MVP close | N/A | Migration already SHIPPED; no MVP gate fires |
  | N4 — Per-component isolation invariant preserved | applicable | Specialists unchanged; verify via specialist isolation slice still GREEN |
  | N5 — Cross-component state-flow contract | applicable | Directly improved by this story; manifest now declares state-flow explicitly |
  | N6 — Gate boundary scope hierarchy | N/A | No gate semantics changes |
  | N7 — Replay regression verifies execution path | applicable | Verify 5a.1 replay-regression slice still GREEN; pack-hash drift remains pre-existing per `replay-regression-pack-hash-drift-pre-slab-6.1` |
  | N8 — Cost machinery integration with real trace data | N/A | No cost-engineering changes |
  | N9 — Operator-witnessed evidence at M-gate vote | applicable | Single-gate story; dev-side evidence (Codex 24+80 passes); operator confirms at close |
  | N10 — Anti-pattern catalog read at architecture-authoring time | N/A | Spec authored 2026-04-27; party-mode-ratified; no new architecture |
  | N11 — Composition mode declared alongside isolated mode | N/A | Per Composition Spec §3.6; no composition-mode change |
  | N12 — Auth model verified via probe | N/A | No new external auth surface |

  Auditor verifies each independently against the actual diff and updates verdicts with concrete evidence (test paths, commit SHA, code references). FAIL verdicts auto-promote to `patch` with bidirectional linkage.

- Final sentence: "All `patch` items addressed in commits; all `defer` items filed in deferred-inventory; all `dismiss` items justified above; `decision_needed` items surfaced to operator; substrate inventory trace complete with N-items 1–12 verdicts recorded. Slab 6.2 ready for `review → done` flip pending operator confirmation." (Or per FAIL/decision_needed override variant.)

## Things NOT to flag

- Pre-existing replay-regression pack-hash drift (`replay-regression-pack-hash-drift-pre-slab-6.1` — already deferred)
- Slab 6.0 + 6.1 substrate (out of scope; only flag if accidentally modified)
- Anti-pattern catalog absence of new entries (A12 partial mitigation already named at spec; no new entries expected)
- Pre-existing dirty working-tree state from prior cycles (already cleaned at session-wrap commits)
- Cosmetic NITs that don't change behavior, schema, or contract — apply aggressive DISMISS per `docs/dev-guide/story-cycle-efficiency.md`
- The 8 operator-ratified BINDING riders themselves (Auditor traces correctness; does not re-decide)

## Sequencing

Same as prior reviews:
1. Three layers run in parallel (Blind Hunter + Edge Case Hunter + Acceptance Auditor)
2. Triage merges + classifies
3. Codex addresses `patch` items in commits
4. Codex files `defer` items in deferred-inventory
5. Codex documents `dismiss` justifications
6. Codex surfaces `decision_needed` items to operator (do NOT silently choose)

## Closeout protocol (after triage clears + operator confirmation; per discipline doc Gate 6)

When all triage items are resolved AND operator confirms:
1. Codex commits any `patch` items as themed commits; follow `fix(slab-6.2): ...`
2. Codex flips `migration-6-2-promote-dependency-map-into-manifest: review → done` in `sprint-status.yaml` with summary annotation
3. Codex updates `_bmad-output/planning-artifacts/deferred-inventory.md`:
   - Flip `migration-6-2-promote-dependency-map-into-manifest` entry from FILED-AS-DEFERRED to RESOLVED-AT-Slab-6.2-CLOSE
   - Update file header `Last refreshed:` line per P-R3 NON-BLOCKING
4. Codex verifies Composition Spec §12 known limitation #1 reads RESOLVED (already landed in implementation; verify no stale text remains)
5. **UNBLOCK:** Slab 6.3 + 6.4 + 6.5 are now eligible for bundle dispatch hand-off (`codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md` Phase 1: Codex runs `bmad-create-story` per seed)

## Substrate Inventory Checklist availability

Per Slab 6.0 governance + discipline doc, every Codex slab dispatch from this point forward must:
1. Read the checklist at T1
2. Identify which N-items apply
3. Have the Acceptance Auditor (in code review) verify each applicable N-item is honored
4. File N13+ extensions if a NEW substrate concern surfaces

For this Slab 6.2 review: N4 + N5 + N7 + N9 applicable per pre-populated table above; N1, N2, N3, N6, N8, N10, N11, N12 N/A with explicit rationale.

## What this dispatch does NOT do

- Does NOT touch any code (review-only; patches happen as separate commits per finding)
- Does NOT modify Slab 6.0 + 6.1 substrate (out of scope; flag if accidentally modified)
- Does NOT modify anti-pattern catalog or Composition Specification §1-§9 / §11 / §13 / §14
- Does NOT trigger Slab 6.3 / 6.4 / 6.5 work (separate bundle dispatch; opens after this close)
- Does NOT re-litigate operator-ratified party-mode BINDING riders (Auditor traces correctness)
