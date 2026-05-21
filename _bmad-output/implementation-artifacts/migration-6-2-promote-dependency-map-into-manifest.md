# Migration Story 6.2: Promote dependency_map declaration into pipeline manifest (Slab 6 trial-experience bundle prerequisite)

**Status:** ready-for-dev (pre-authored 2026-04-27 in operator session immediately after Slab 6.1 patch dispatch; activates at Slab 6.1 formal close)
**Sprint key:** `migration-6-2-promote-dependency-map-into-manifest`
**Epic:** Slab 6 — Post-MVP Production Capability (`migration-epic-6-post-mvp-production`); precedes Slab 6.3 + 6.4 + 6.5 per `codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md` Phase 0 prerequisite.
**Pts:** ~1 (single-gate; manifest schema extension + runner consumes manifest-declared deps; preserves runner-layer fallback for backward-compat).
**Gate:** single-gate (governance-JSON entry to be added at filing; rationale: minor schema extension; no new substrate; preserves backward-compat via fallback retention; no composition-shape change).
**K-target:** ~1.4× (target ~12 / floor ~9 — bumped 2026-04-27 per party-mode M-R3 to accommodate M-R1 + M-R2 fail-loud test additions).

**Predecessors:**
- Slab 6.1 (`migration-6-1-production-graph-runner.md`) CLOSED — runner ships with `_default_dependency_map_for(specialist_id)` deterministic fallback at the runner layer
- Slab 6.1 bmad-code-review DFR-6.1-1 / AA-2 — operator-ratified deferral of manifest promotion to this Slab-6.2 prerequisite story
- Composition Specification §3.6 (dependency_map sourcing) — names manifest as the post-Slab-6.2 source-of-truth
- Composition Specification §10 Decision Log — 2026-04-27 row: "Dependency_map source: deterministic fallback at runner layer ... manifest promotion deferred as Slab-6.2 prerequisite story"

**Authorship provenance:** authored 2026-04-27 in operator session immediately after Slab 6.1 patch dispatch authored. Cite Codex Slab 6.1 implementation (commit `d5cfad8`) + bmad-code-review report at `_bmad-output/implementation-artifacts/6-1-code-review-2026-04-27.md` (DFR-6.1-1).

**Governance (BINDING per `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md`):**
- This spec was authored solo in operator session and has NOT yet passed bmad-party-mode green-light. Status `ready-for-party-mode-greenlight` per sprint-status.yaml.
- **Gate 1 BEFORE Gate 2 (dev):** bmad-party-mode green-light with Winston + Murat + Paige + Amelia minimum per CLAUDE.md §2. Status flips to `ready-for-dev` only after green-light + applied riders.
- **Gate 3 (post-implementation):** bmad-code-review with three-layer (Blind Hunter + Edge Case Hunter + Acceptance Auditor) + N-item trace deliverable section (BINDING per Slab 6.0 governance) per CLAUDE.md §3.
- **Composition Specification at `docs/dev-guide/composition-specification.md` is normative for Option B evolution.** Honor §3 invariants throughout dev. Detect §11 migration trigger conditions; HALT and surface if any fire. File §10 Decision Log entry at close (this story IS substrate-affecting per dependency_map sourcing change).
- **Substrate Inventory Checklist at `docs/dev-guide/substrate-inventory-checklist.md`** N-items applicable: N4 (isolation invariant), N5 (state-flow contract — directly improved), N7 (replay regression), N9 (operator-witnessed evidence). Trace per substantive review focus list at code-review.
- **Anti-pattern catalog at `docs/dev-guide/specialist-anti-patterns.md`** read at T1; A12 partially mitigated by this story; A9 alignment verified.
- **Halt-and-surface triggers** per discipline doc §6: substrate disagreement; §11 migration trigger fire; decision_needed surfaces; N-item FAIL; new anti-pattern; cross-cutting impact beyond IN-SCOPE list.

**Party-mode green-light (BINDING; ratified 2026-04-27 in --solo mode):**
- Convened: Winston (architect) + Murat (test architect) + Paige (tech writer) + Amelia (dev)
- Verdict: unanimous GREEN-WITH-RIDERS — no architectural impasse; no §11 migration trigger fire; spec structurally sound
- 8 BINDING riders applied to spec (W-R1, W-R2, M-R1, M-R2, M-R3 K-floor bump, P-R1, P-R2, A-R1, A-R2)
- 3 NON-BLOCKING riders apply at close (W-R3 circular-check verification, M-R4 isolated `_resolve_dependency_map` unit test, P-R3 deferred-inventory `Last refreshed:` line update, A-R3 effort-estimate bump 4-6 → 5-7 hr)
- **Fallback retention is PERMANENT** (W-R1 + P-R1 binding consistency): runner-layer fallback IS the resolution mechanism for any node that opts out of explicit manifest declaration; not deprecated; not transitional. Future-reader test: someone reading 12 months from now must NOT think the fallback should be ripped out.
- **Likely halt candidates named** (A-R2): (a) `app/manifest/compiler.py` validator may not admit new optional field cleanly; (b) circular-dependency check may need new logic if existing only inspects implicit `node.upstream:` field per W-R3.

---

## Why this story exists

Slab 6.1 shipped with a runner-layer deterministic fallback for `dependency_map` because the v4.2 pipeline manifest does not yet declare per-node dependency input keys. The fallback works for the current bounded-MVP composition (Texas → CD = `source_bundle`; other downstream = `upstream_output`), but it has three substantive limitations:

1. **Implicit coupling.** The fallback table is in code (`_default_dependency_map_for(specialist_id)`), not in the manifest. Adding a new specialist with a non-default dependency shape requires editing the runner, not the manifest.
2. **Specialist evolution friction.** When Slab 6 trial-experience bundle introduces new specialists (Step 02A surface; HUD instrumentation surfaces) or changes existing ones (Irene Pass 2 authoring template), each may need new dependency entries. Editing the runner per specialist is the procedural-coupling pattern A12 named.
3. **Non-linear topology blind spot.** Branch/conditional manifest topologies (DFR-6.1-4 candidate) cannot declare dependencies cleanly without manifest-level dependency declarations.

This story closes the gap before Slab 6 trial-experience bundle implementation begins. After this lands:
- Manifest-declared dependency keys are the source-of-truth
- Runner-layer fallback is preserved as the resolution mechanism for nodes that don't declare keys (fully backward-compatible)
- Adding/modifying a specialist edits the manifest, not the runner

**Operator preference (binding, unchanged):** "do it right, no band-aids, only rational trade-offs that get named in writing." Halt-and-surface if substrate disagrees with spec. Same pattern as 3.1 + 5a.3 + A15 + A16 + A17 + Slab 6.0 + Slab 6.1 instances.

---

## T1 Readiness Block

1. **Governance:** single-gate (rationale: minor schema extension; no new substrate; preserves backward-compat via fallback retention; no composition-shape change). Add to `docs/dev-guide/migration-story-governance.json` as Slab-6.2 entry; version bump.

2. **Substrate inheritance (BINDING):**
   - `state/config/pipeline-manifest.yaml` — current manifest; extends with per-node `dependencies:` field
   - `app/manifest/compiler.py` — manifest validator + compiler; extends to validate new field shape
   - `app/marcus/orchestrator/production_runner.py` — `_default_dependency_map_for(specialist_id)` preserved as fallback; new `_resolve_dependency_map(node)` reads manifest first, falls back if absent
   - `tests/integration/marcus/test_production_runner_invocation.py` — existing fallback contract test preserved + extended for manifest-declared cases
   - `docs/dev-guide/composition-specification.md` §3.6 — flip from "current shape: runner-layer fallback" to "current shape: manifest-declared with runner-layer fallback for unspecified nodes"

3. **Reusable substrate (existing pieces this story PRESERVES):**
   - `ProductionEnvelope` + `SpecialistContribution` + `ProductionDispatchAdapter` (Slab 6.0; do NOT modify)
   - `production_runner.py` core run loop (do NOT modify; only the dependency_map resolution path changes)
   - 14 × `app/specialists/<name>/graph.py` — specialists unchanged
   - All chain tests + isolation tests + composition smoke tests (must remain GREEN)

4. **NOT-existing substrate (the gap this story closes):**
   - **Manifest-declared dependency keys** at the per-node level
   - **Manifest validator extension** for the new schema field
   - **Runner-layer manifest-first resolution** path (currently fallback-only)

5. **Severance posture:** primary repo at `upstream/master @ 3ed7c56` remains frozen reference; FR60 backport stays closed.

---

## TEMPLATE scope decisions

**Decision #1 — Bounded scope (per R1):** This story builds the manifest-promotion ONLY:
- Pipeline manifest schema extends with `dependencies: dict[str, str]` field per specialist node (downstream-input-key → upstream-specialist-id)
- Manifest validator + compiler accept + validate new field
- Production runner reads manifest dependencies first, falls back to `_default_dependency_map_for(...)` if not declared (**fallback retention is PERMANENT per party-mode W-R1 + P-R1 ratification — not deprecated; not transitional; the fallback IS the resolution mechanism for any node that opts out of explicit declaration**)
- Pipeline manifest current entries get explicit dependency declarations matching current fallback behavior (Texas → CD `source_bundle`; other downstream `upstream_output` if applicable)
- Test surface covers manifest-declared + fallback-resolved + missing-upstream cases (fail-loud, not silent fallback per Composition Spec §3.6)

NOT in scope:
- Multi-pass / repeated specialist node handling (still Path Z from Slab 6.1; Path X / Y deferred)
- Branch/conditional traversal (still iterates manifest order; DFR-6.1-4 deferred)
- Generator-emit of manifest dependency stub on new specialist creation (deferred as `2c-4-generator-emit-manifest-dependency-stub`; separate follow-on; **per P-R2: when generator-emit lands, it consumes THIS story's manifest format as its emission contract — flag the coupling for that future story's authoring**)
- Anti-pattern A12 retirement (manifest-declared dependencies don't fully retire A12; that's the generator-emit work)

**Decision #2 — Schema shape:** dependencies declared at the manifest node level as `dependencies: dict[str, str]` (downstream-input-key → upstream-specialist-id). Example:

```yaml
# state/config/pipeline-manifest.yaml
nodes:
  - id: cd-node-1
    specialist: cd
    dependencies:
      source_bundle: texas  # cd's "source_bundle" input key reads texas's contribution
  - id: irene-node-1
    specialist: irene
    dependencies:
      upstream_output: cd  # irene's "upstream_output" reads cd's contribution
```

Empty `dependencies:` (or missing field) triggers fallback to `_default_dependency_map_for(specialist_id)`.

**Decision #3 — Resolution rule:** runner-layer dependency resolution at trial start:

```python
def _resolve_dependency_map(node: ManifestNode) -> dict[str, str]:
    """Resolve dependency_map for a manifest node.

    Manifest declaration is source-of-truth; falls back to deterministic
    default if not declared. Per Composition Spec §3.6 post-Slab-6.2.
    """
    if node.dependencies:
        return node.dependencies
    return _default_dependency_map_for(node.specialist)
```

**Decision #4 — Backward-compat:** all existing manifest entries that don't declare `dependencies:` continue to work via fallback. Migration is opt-in per node. Slab 6.1 trial envelope shape unchanged.

---

## Story

As an **operator preparing to evolve specialist behavior during Slab 6 trial-experience bundle implementation and subsequent trial work**,
I want **dependency_map declarations to live in the pipeline manifest (with runner-layer fallback preserved for backward-compat)**,
So that **adding/modifying specialists edits the manifest rather than the runner; the source-of-truth for cross-specialist coupling is in one place; and Slab 6 trial-experience bundle implementation + future composition evolutions can declare dependencies cleanly without procedural-coupling friction**.

---

## Acceptance Criteria

### AC-Slab-6.2-A — Pipeline manifest schema extension

- **Given** Decision #2 schema shape
- **When** dev extends `state/config/pipeline-manifest.yaml` schema validator + manifest itself
- **Then** per-node `dependencies: dict[str, str]` field accepted (downstream-input-key → upstream-specialist-id); empty/missing field is valid (triggers fallback); circular dependencies rejected at compile time per existing manifest invariant.
- **Test pin:** `tests/integration/manifest/test_manifest_dependencies_field.py` — 4 tests: schema-accepts-empty / schema-accepts-declared / schema-rejects-circular / schema-rejects-non-dict-shape.

### AC-Slab-6.2-B — Production runner manifest-first resolution + fail-loud on missing upstream

- **Given** Decision #3 resolution rule + Composition Spec §3.6 fail-loud rule
- **When** dev wires `_resolve_dependency_map(node)` into the production runner's specialist invocation loop
- **Then** runner reads manifest-declared dependencies first; falls back to `_default_dependency_map_for(specialist_id)` for unspecified nodes; existing Slab 6.1 fallback contract preserved; missing-upstream fails loud with `MissingUpstreamContributionError` naming both `specialist_id` AND `downstream_input_key`.
- **Test pin:** `tests/integration/marcus/test_production_runner_dependency_resolution.py` — 6 tests:
  1. `test_manifest_declared_precedence` — manifest dep declared; runner reads it (not fallback)
  2. `test_fallback_on_empty_dependencies_field` — empty `dependencies: {}`; runner falls back to `_default_dependency_map_for(...)`
  3. `test_fallback_on_missing_dependencies_field` — manifest entry has no `dependencies:` key at all; runner falls back
  4. `test_missing_upstream_dependency_fails_loud` (per M-R1 BINDING) — manifest declares dep on `phantom-specialist` not in run; raises `MissingUpstreamContributionError(specialist_id="phantom-specialist", downstream_input_key="...")` with both fields in message
  5. `test_upstream_ran_but_no_contribution_fails_loud` (per M-R2 BINDING) — upstream specialist ran but its contribution absent from envelope; raises `MissingUpstreamContributionError` with explanatory message
  6. `test_fallback_path_unchanged_for_undeclared_node` (per W-R2 BINDING) — pick ONE existing manifest node currently using runner-layer fallback (e.g., Texas → CD); do NOT add `dependencies:` declaration; verify trial-run output identical to pre-implementation baseline (regression-prevention)

### AC-Slab-6.2-C — Existing manifest entries promoted to declared dependencies

- **Given** the current Slab 6.1 fallback table (Texas → CD `source_bundle`)
- **When** dev declares dependencies in the manifest matching current fallback behavior
- **Then** trial behavior unchanged from Slab 6.1; envelope contributions accumulate identically; replay-regression slices PASS.
- **Test pin:** N/A (covered by AC-B + replay regression in AC-G).

### AC-Slab-6.2-D — Composition Specification §3.6 update

- **Given** the manifest-as-source-of-truth shift
- **When** dev updates `docs/dev-guide/composition-specification.md` §3.6
- **Then** §3.6 reflects manifest-declared with runner-layer fallback as the resolution mechanism; §10 Decision Log row added; §12 known limitation #1 flips from RESOLVED-WITH-DEFERRAL to RESOLVED.

### AC-Slab-6.2-E — Live smoke unaffected

- **Given** the existing Slab 6.1 live smoke at `tests/live/test_production_trial_smoke.py`
- **When** operator runs the smoke post-Slab-6.2
- **Then** test PASSES with identical contribution ordering + cost shape to Slab 6.1 baseline (same texas + irene chain works).
- **Test pin:** existing live smoke; no new test required.

### AC-Slab-6.2-F — Specialist isolation invariant preserved

- **Given** the chain-test + isolation discipline from Slab 6.0
- **When** dev verifies post-implementation
- **Then** `tests/composition/test_specialist_isolation_preserved.py` PASSES; all per-specialist `tests/specialists/<name>/test_*.py` PASS.
- **Test pin:** existing isolation tests; verify post-implementation.

### AC-Slab-6.2-G — Replay regression slice unchanged

- **Given** the existing 5a.1 replay regression suite
- **When** dev runs the slice post-implementation
- **Then** slice GREEN at the same coverage as Slab 6.1 close (the pre-existing pack-hash drift per `replay-regression-pack-hash-drift-pre-slab-6.1` remains deferred; this story does not introduce additional drift).

### AC-Slab-6.2-H — Anti-pattern catalog unchanged

NO new entries expected. If a NEW pattern surfaces (e.g., manifest-declared dependency on a not-yet-registered specialist), file as harvest candidate per Mary harvest-gate.

### AC-Slab-6.2-I — TEMPLATE compliance

R1, R6, R8 honored. Slab-6.2 — establishes the precedent for substrate-relocation stories that move responsibility from one layer to another while preserving backward-compat.

### AC-Slab-6.2-J — D12 close protocol (single-gate)

1. **Invariant preservation:** all 15 invariants from 5a.4 matrix REMAIN preserved (this story relocates dependency_map source; doesn't modify any invariant). FR34 HIL machinery preserved (orthogonal). FR43 frozen-graph-version-ceremony respected.
2. **Anti-pattern harvest:** no new entries expected; verify A12 (procedural-coupling) is partially mitigated (manifest-declared dependencies move some procedural coupling out of code, but generator-emit work is still pending per `2c-4-generator-emit-manifest-dependency-stub`).
3. **Migration-guide update:** §"Production Runner" augmented — manifest-as-source-of-truth-for-dependencies pattern documented.
4. **TEMPLATE compliance:** R1, R6, R8.
5. **Sprint-status flip + Composition Spec §10/§12 update + deferred-inventory entry status flip** (see AC-K + AC-L).

### AC-Slab-6.2-K — Sprint-status state-flips at filing AND close

At filing: `migration-6-2-promote-dependency-map-into-manifest: ready-for-dev`. At close: `migration-6-2-promote-dependency-map-into-manifest: done`. Slab 6 trial-experience bundle stories (`migration-6-3-*`, `migration-6-4-*`, `migration-6-5-*`) UNBLOCKED at this story's close.

### AC-Slab-6.2-L — Deferred-inventory entry status flip

The entry filed at Slab 6.1 close (`migration-6-2-promote-dependency-map-into-manifest`) flips from FILED-AS-DEFERRED to RESOLVED-AT-Slab-6.2-CLOSE. Composition Spec §12 known limitation #1 flips from RESOLVED-WITH-DEFERRAL to RESOLVED.

---

## File Structure Requirements

### NEW files

- `tests/integration/manifest/test_manifest_dependencies_field.py` (AC-A; 4 tests)
- `tests/integration/marcus/test_production_runner_dependency_resolution.py` (AC-B; 3 tests)

### MODIFIED files

- `state/config/pipeline-manifest.yaml` — extend with `dependencies:` per-node field; declare current Texas → CD `source_bundle` + any other downstream that currently uses fallback (per AC-C)
- `app/manifest/compiler.py` — extend manifest validator to accept + validate new field shape
- `app/marcus/orchestrator/production_runner.py` — wire `_resolve_dependency_map(node)` per Decision #3; preserve `_default_dependency_map_for(...)` as fallback path
- `docs/dev-guide/composition-specification.md` — §3.6 update + §10 Decision Log row + §12 known limitation #1 flip
- `docs/dev-guide/langgraph-migration-guide.md` — §"Production Runner" augmented per AC-J item 3
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-K
- `_bmad-output/planning-artifacts/deferred-inventory.md` — per AC-L; entry flip
- `docs/dev-guide/migration-story-governance.json` — Slab-6.2 single-gate entry + version bump

### DO NOT MODIFY

- `app/models/runtime/production_envelope.py` — Slab 6.0 substrate
- `app/marcus/orchestrator/dispatch_adapter.py` — Slab 6.0 substrate
- `app/models/runtime/production_trial_envelope.py` — Slab 6.1 close shape
- 14 × `app/specialists/<name>/graph.py` — specialists unchanged
- `marcus/orchestrator/m3_trial.py` — deterministic harness preserved
- `app/gates/resume_api.py` — FR34 gate machinery preserved
- All `tests/specialists/<name>/test_*.py` — isolated-execution tests must remain GREEN
- All `tests/composition/test_*.py` — composition + isolation tests must remain GREEN

---

## Testing Requirements

**K-target ~1.4× (target ~10 / floor ~7).**

K-floor calculation:
- AC-A: 4 (schema-accepts-empty + schema-accepts-declared + schema-rejects-circular + schema-rejects-non-dict-shape)
- AC-B: 3 (manifest-declared-precedence + fallback-on-empty + fallback-on-missing-field)

= **7 K-floor**. RIDER candidates during dev: AC-A add edge case (schema-accepts-self-referential-empty? not really meaningful); AC-B add edge case (manifest-declared-with-typo-upstream-id; should fail fast at trial start, not silent fallback) → +1 = **8 K-floor**. Honest target ~10 if more edge cases surface.

**Sandbox-AC PASS expected** (uses shipped Pydantic v2 + standard pytest; no live API).

---

## Substrate Inventory Checklist application

- **N4 (Per-component isolation invariant preserved post-composition):** existing isolation tests must remain GREEN (AC-F)
- **N5 (Cross-component state-flow contract):** this story directly improves N5 by making dependency declarations explicit + manifest-source-of-truth
- **N7 (Replay regression verifies execution path):** AC-G covers
- **N9 (Operator-witnessed evidence at story close):** operator runs live smoke (AC-E) confirming behavior unchanged

N1, N2, N3, N6, N8, N10, N11, N12 are N/A for this story (no new external resources; no composition-vote shape change; no live-API smoke gate change; no gate-precedence change; no cost machinery change; no architecture-authoring; no composition-mode change; no auth model change).

**Mandatory N-item trace section** in the bmad-code-review deliverable for this story per Slab 6.0 governance.

---

## Anti-pattern catalog application

- **A12 (Procedural-coupling between specialist + ancillary surfaces):** this story PARTIALLY mitigates A12 by moving dependency declarations out of code into manifest. Full A12 retirement requires the generator-emit work (`2c-4-generator-emit-manifest-dependency-stub`) which is a separate follow-on.
- **A9 (Epic-doc structural-name drift):** verify manifest dependency keys align with specialist contribution output keys; if drift surfaces, file as A9 fourth/fifth instance per harvest-gate.

---

## Effort estimate

**~5-7 hr Codex time** (per A-R3 NON-BLOCKING bump from 4-6 → 5-7 to accommodate M-R1 + M-R2 test additions + likely golden refresh + halt-and-adapt cycles). Single-gate; small surface; backward-compat preserves existing tests as proof-of-no-regression. Phasing:

- Phase 1 — Pre-flight + design (~1.5 hr; per A-R1 BINDING): Run existing manifest validator against all current `state/config/pipeline-manifest.yaml` entries; record baseline pass count (this becomes the regression baseline against post-implementation runs). Read existing manifest + compiler + runner. Design `_resolve_dependency_map(node)` shape. Verify backward-compat path. Verify circular-dep rejection happens at compile time per AC-A claim (per W-R3 NON-BLOCKING) — if not currently true, add minimal circular-check to `app/manifest/compiler.py` (~10 LOC).
- Phase 2 — Implementation (~2 hr): Schema extension + validator + runner resolution wiring. Implement `MissingUpstreamContributionError` exception type with `specialist_id` + `downstream_input_key` fields per Composition Spec §3.6 fail-loud rule.
- Phase 3 — Tests (~1.5-2 hr): Author 9 K-floor tests (4 in AC-A + 6 in AC-B per M-R1 + M-R2 + W-R2 additions; M-R4 NON-BLOCKING isolated `_resolve_dependency_map` unit test as time allows). Promote existing manifest entries. Verify all pre-existing tests GREEN. Refresh manifest goldens if YAML output ordering shifts.
- Phase 4 — D12 close (~1 hr): Composition Spec §3.6 + §10 Decision Log + §12 known limitation #1 flip + sprint-status + deferred-inventory entry status flip (with `Last refreshed:` line update per P-R3 NON-BLOCKING) + governance JSON + migration guide.

**Halt-and-adapt budget built in. Likely halt candidates named explicitly per A-R2 BINDING:**
- (a) `app/manifest/compiler.py` validator may not admit new optional field cleanly — Codex pre-flights at Phase 1; if surfaced, ~30-60 min refactor of validator schema declaration (still in budget)
- (b) Circular-dependency check may need new logic if existing manifest validator only inspects implicit `node.upstream:` field rather than performing full graph traversal — Codex verifies at Phase 1 per W-R3; if minimal addition needed, lands in Phase 2

If either halt surfaces a substrate disagreement that can't be resolved in this story's budget, HALT and surface to operator per discipline doc §6.

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_

### T1 Readiness + substrate verification

_(Verify Slab 6.1 close state at dev start; confirm `_default_dependency_map_for(...)` still in place; confirm Composition Spec §3.6 reflects pre-Slab-6.2 state.)_

### Implementation summary

_(Codex fills at close.)_

### Verification

_(Codex fills at close: pytest counts; ruff; lint-imports; sandbox-AC validator.)_

### Operator-witnessed evidence (single-gate; no operator dual-gate required)

Single-gate story; operator validates at close via re-run of existing live smoke per AC-E (no new operator ceremony required).
