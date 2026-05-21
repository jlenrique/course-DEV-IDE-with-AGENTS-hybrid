# Codex dispatch: Slab 6.2 — promote dependency_map into pipeline manifest (Slab 6 trial-experience bundle prerequisite)

**Session:** 2026-04-27 (operator-authorized post-bmad-party-mode green-light)
**Branch:** `dev/langchain-langgraph-foundation`
**Predecessor state:**
- Slab 6.1 CLOSED 2026-04-27 (commits `d5cfad8` + `6ca5f43` + `0f91e95` + `61fede4` + `e6787e3` + `97842ac`); migration unconditionally SHIPPED
- Slab 6.2 spec authored in operator session immediately post-Slab-6.1; party-mode green-light applied 2026-04-27
- Sprint-status flag flipped to `ready-for-dev` after BINDING riders applied to spec
- Composition Spec + Substrate Inventory Checklist + anti-pattern catalog standing as governing references
- Slab 6 trial-experience bundle governance discipline doc at `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md` (BINDING for all Slab 6.x stories)

**Mission:** implement the Slab 6.2 spec at `_bmad-output/implementation-artifacts/migration-6-2-promote-dependency-map-into-manifest.md`. Promote `dependency_map` declaration from runner-layer fallback (`_default_dependency_map_for(specialist_id)` in `app/marcus/orchestrator/production_runner.py`) into pipeline manifest per-node `dependencies: dict[str, str]` field. Preserve runner-layer fallback as PERMANENT resolution mechanism for nodes that opt out of explicit declaration (NOT deprecated; NOT transitional). Add fail-loud `MissingUpstreamContributionError` for missing-upstream cases per Composition Spec §3.6.

**Operator preference (binding, unchanged):** "do it right, no band-aids, only rational trade-offs that get named in writing." Halt-and-surface if substrate disagrees with spec. Same pattern as 3.1 + 5a.3 + A15 + A16 + A17 + Slab 6.0 + Slab 6.1 instances.

## Why this dispatch exists

Slab 6.1 close ratified deferring dependency_map manifest promotion to this story (DFR-6.1-1 / AA-2). Codex's deterministic fallback (Texas → CD = `source_bundle`; other downstream = `upstream_output`) is the current Slab 6.1 close shape; manifest promotion is the Slab 6 trial-experience bundle prerequisite to keep specialist evolution clean.

Per the bmad-party-mode green-light (2026-04-27 --solo Winston + Murat + Paige + Amelia; unanimous GREEN-WITH-RIDERS):
- Architecture sound (Path A-prime invariants honored; envelope alongside cache_prefix; specialists unchanged; adapter remains only translation surface)
- 8 BINDING riders applied to spec — read updated spec verbatim before T1
- 3 NON-BLOCKING riders apply at close (W-R3 + M-R4 + P-R3 + A-R3)

## Governance discipline (BINDING)

Read `_bmad-output/implementation-artifacts/slab-6-trial-experience-bundle-governance-discipline.md` at T1. Key bindings for this story:

- **Six-gate sequence:** Spec authoring (DONE) → bmad-party-mode green-light (DONE — unanimous GREEN-WITH-RIDERS) → bmad-dev-story (THIS DISPATCH) → bmad-code-review with three-layer + N-item trace deliverable (next dispatch after this lands) → triage + operator dispositions → single-gate dev-side acceptance → formal close.
- **Composition Specification at `docs/dev-guide/composition-specification.md` is normative for Option B evolution.** Honor §3 invariants throughout dev. Detect §11 migration trigger conditions; HALT and surface if any fire. File §10 Decision Log entry at close (this story IS substrate-affecting per dependency_map sourcing change).
- **Substrate Inventory Checklist N-items applicable:** N4 (isolation invariant preserved), N5 (state-flow contract — directly improved), N7 (replay regression), N9 (operator-witnessed evidence at close).
- **Anti-pattern catalog:** A12 (procedural-coupling) PARTIALLY mitigated; A9 (Epic-doc structural-name drift) alignment verified.
- **Halt-and-surface triggers** per discipline doc §6: substrate disagreement; §11 migration trigger fire; decision_needed surfaces; N-item FAIL exceeding story budget; new anti-pattern; cross-cutting impact beyond IN-SCOPE.

## Scope (per ratified spec)

**IN SCOPE:**
1. Pipeline manifest schema extends with `dependencies: dict[str, str]` field per specialist node (downstream-input-key → upstream-specialist-id)
2. Manifest validator + compiler accept + validate new field; circular-dependency rejection happens at compile time (per W-R3 NON-BLOCKING — verify existing validator covers this; if not, add minimal circular-check ~10 LOC)
3. Production runner reads manifest dependencies first via new `_resolve_dependency_map(node)` function; falls back to existing `_default_dependency_map_for(specialist_id)` for unspecified nodes
4. **Fallback retention is PERMANENT** (W-R1 + P-R1 BINDING): the fallback IS the resolution mechanism for any node that opts out of explicit declaration; do NOT frame as deprecated or transitional in any code comment, docstring, or doc update
5. Pipeline manifest current entries get explicit dependency declarations matching current fallback behavior (Texas → CD = `source_bundle`; other downstream specialists per existing fallback table)
6. New `MissingUpstreamContributionError` exception type with `specialist_id` + `downstream_input_key` fields; raised when manifest declares dependency on specialist absent from envelope (per Composition Spec §3.6 fail-loud rule)
7. Test surface per spec AC-A (4 tests) + AC-B (6 tests per M-R1 + M-R2 + W-R2 BINDING additions) = 10 tests against K-floor 9 (+1 over floor; meets target ~12 with M-R4 NON-BLOCKING isolated unit test as time allows)
8. Composition Spec §3.6 update at AC-D — text MUST include explicit "fallback retention is permanent" framing per W-R1 + P-R1 BINDING

**NOT in scope:**
- Multi-pass / repeated specialist node handling (still Path Z from Slab 6.1; Path X / Y deferred per `slab-6-1-multi-pass-envelope-path-x-or-y`)
- Branch/conditional traversal (still iterates manifest order; `slab-6-1-runner-compiled-edge-traversal` deferred)
- Generator-emit of manifest dependency stub (deferred as `2c-4-generator-emit-manifest-dependency-stub`; cross-ref P-R2 BINDING — when that future story lands, it consumes THIS story's manifest format as its emission contract)
- Anti-pattern A12 retirement (manifest-declared dependencies don't fully retire A12; that's the generator-emit work)
- LangSmith trace_id real binding (deferred as `slab-6-1-langsmith-runner-trace-id-real-binding`)
- ProductionTrialEnvelope lifecycle invariants (deferred as `production-trial-envelope-lifecycle-invariants`)

**DO NOT MODIFY (per Path A-prime + Slab 6.0 invariants):**
- `app/models/runtime/production_envelope.py` (Slab 6.0 substrate)
- `app/marcus/orchestrator/dispatch_adapter.py` (Slab 6.0 substrate)
- `app/models/runtime/production_trial_envelope.py` (Slab 6.1 close shape)
- 14 × `app/specialists/<name>/graph.py` (specialists unchanged)
- `marcus/orchestrator/m3_trial.py` (deterministic harness preserved)
- Anti-pattern catalog (no new entries expected; if NEW pattern surfaces, propose to Mary harvest-gate per discipline doc §3)

## Phasing (per ratified spec; 5-7 hr Codex)

- **Phase 1 — Pre-flight + design (~1.5 hr; per A-R1 BINDING):**
  - Run existing manifest validator against all current `state/config/pipeline-manifest.yaml` entries; record baseline pass count (this becomes regression baseline)
  - Read existing manifest + compiler + runner; design `_resolve_dependency_map(node)` shape; verify backward-compat path
  - Verify circular-dep rejection happens at compile time per AC-A claim (per W-R3 NON-BLOCKING) — if not currently true, add minimal circular-check to `app/manifest/compiler.py` (~10 LOC) in this phase

- **Phase 2 — Implementation (~2 hr):**
  - Schema extension to `state/config/pipeline-manifest.yaml` validator + compiler
  - Wire `_resolve_dependency_map(node)` into production runner's specialist invocation loop
  - Implement `MissingUpstreamContributionError` exception type with `specialist_id` + `downstream_input_key` fields
  - Promote existing manifest entries with explicit `dependencies:` declarations matching current fallback behavior (Texas → CD `source_bundle`; etc.)

- **Phase 3 — Tests (~1.5-2 hr):**
  - Author 9 K-floor tests (4 in AC-A + 6 in AC-B per M-R1 + M-R2 + W-R2 BINDING additions)
  - M-R4 NON-BLOCKING: add isolated `_resolve_dependency_map(node)` unit test if time permits
  - Verify all pre-existing tests GREEN (no regression)
  - Refresh manifest goldens if YAML output ordering shifts (golden-fixture refresh budget: ~0.5 hr; in budget per A-R3 5-7 hr estimate)

- **Phase 4 — D12 close (~1 hr):**
  - Composition Spec `docs/dev-guide/composition-specification.md` §3.6 update per AC-D + W-R1/P-R1 BINDING (PERMANENT fallback framing)
  - Composition Spec §10 Decision Log entry — manifest dependency promotion landed; fallback PERMANENT
  - Composition Spec §12 known limitation #1 flip from RESOLVED-WITH-DEFERRAL → RESOLVED
  - Sprint-status flip `migration-6-2-promote-dependency-map-into-manifest: review` (NOT done — bmad-code-review fires next)
  - Deferred-inventory `migration-6-2-promote-dependency-map-into-manifest` entry status preserved as DEFERRED-CONTINUES until bmad-code-review + close
  - Migration guide §"Production Runner" augmented per AC-J item 3 — manifest-as-source-of-truth-for-dependencies pattern documented

## Halt candidates named explicitly (per A-R2 BINDING)

If either of these surfaces during dev:
- (a) `app/manifest/compiler.py` validator may not admit new optional field cleanly — pre-flight at Phase 1; if surfaced, ~30-60 min refactor of validator schema declaration (still in budget)
- (b) Circular-dependency check may need new logic if existing manifest validator only inspects implicit `node.upstream:` field rather than performing full graph traversal — verify at Phase 1 per W-R3; if minimal addition needed, lands in Phase 2

If either halt surfaces a substrate disagreement that can't be resolved in this story's budget, HALT and surface to operator per discipline doc §6.

## Disposition rules

Standard halt-and-surface discipline:
- **Substrate disagreement:** if Slab 6.0/6.1 substrate doesn't admit the spec as written, HALT and surface
- **`decision_needed` items:** name each option + tradeoff; do not silently choose
- **N-item FAIL during dev:** auto-promote to in-story `patch` work; do not defer
- **NEW anti-pattern surfaces:** propose to Mary harvest-gate per discipline doc §3
- **§11 migration trigger fire:** HALT and surface; operator + party-mode evaluate

## Deliverable

When implementation lands and all tests pass:
1. Codex commits the implementation as themed commit(s); follow `feat(slab-6.2): promote dependency_map declaration into pipeline manifest` convention
2. Codex sets `migration-6-2-promote-dependency-map-into-manifest` status annotation in `sprint-status.yaml` to "Implementation landed; awaiting bmad-code-review + formal close"; story status flips `ready-for-dev → review`
3. Codex final report names: tests passing (Codex-side); files changed; pre-flight regression baseline + post-implementation comparison; any decision_needed items surfaced; N-item trace summary; halt-and-adapt cycles encountered
4. **Next dispatch (separate, fires after this lands):** bmad-code-review on Slab 6.2 diff with three-layer + N-item trace deliverable section per discipline doc §4 + Slab 6.0 governance template

## Closeout (after bmad-code-review triage clears)

Post-bmad-code-review formal close protocol per discipline doc §1 Gate 6:
1. Sprint-status flip `review → done` with summary annotation
2. Deferred-inventory `migration-6-2-promote-dependency-map-into-manifest` entry flips RESOLVED-AT-Slab-6.2-CLOSE
3. `Last refreshed:` line update to `_bmad-output/planning-artifacts/deferred-inventory.md` header (per P-R3 NON-BLOCKING)
4. Composition Spec §12 known limitation #1 flips RESOLVED-WITH-DEFERRAL → RESOLVED
5. UNBLOCK Slab 6.3 + 6.4 + 6.5: operator runs `bmad-create-story` against bundle dispatch seeds (`codex-handoff-slab-6-3-through-6-5-trial-experience-bundle.md` Phase 1)

## Substrate Inventory Checklist availability

Per Slab 6.0 governance + bundle discipline doc, this dispatch honors the standing N1–N12 trace discipline. Subsequent Codex dispatches per Slab 6.x story continue to require:
1. Read the checklist at T1
2. Identify which N-items apply to the story in scope (this story: N4 + N5 + N7 + N9)
3. Have the Acceptance Auditor (in code review) verify each applicable N-item is honored
4. File N13+ extensions if a NEW substrate concern surfaces

## What this dispatch does NOT do

- Does NOT touch Slab 6.0 substrate (envelope + adapter; out of scope; treat any modification as substantive finding)
- Does NOT modify Slab 6.1 production runner core composition/invocation logic — only adds the dependency-resolution layer
- Does NOT pre-author the bmad-code-review dispatch (separate hand-off when implementation lands)
- Does NOT touch Slab 6.3 / 6.4 / 6.5 work (separate bundle dispatch already authored)
- Does NOT modify anti-pattern catalog or Composition Specification §1-§9 / §11 / §13 / §14 (only §3.6 + §10 + §12 updates per ACs at close)
