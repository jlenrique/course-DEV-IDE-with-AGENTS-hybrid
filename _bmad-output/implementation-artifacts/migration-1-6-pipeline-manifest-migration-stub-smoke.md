# Migration Story 1.6: Pipeline Manifest Migration from Primary + Stub Empty-Graph Smoke

**Status:** ready-for-dev
**Sprint key:** 1-6-pipeline-manifest-migration-stub-smoke
**Epic:** Slab 1 Substrate (migration Epic 1)
**Milestone anchored:** M1 — empty-manifest-loaded graph runs end-to-end §01→§15 via CLI per architecture M1 acceptance bar.
**Pts:** 3 | **Gate:** dual (manifest schema change) | **K-target:** ~1.4×

## Story

As a **dev agent landing the migrated v4.2 pipeline manifest**,
I want **the primary repo's `state/config/pipeline-manifest.yaml` (v4.2 narrated-lesson-with-video-or-animation pack — 15 steps) reshaped to the migration's `PipelineManifest` schema (from 1.4) with stub specialist callables wired (real specialists land in Slab 2), then loaded + compiled + invoked end-to-end §01→§15 via the smoke harness from 1.1c**,
So that **M1's "empty-manifest-loaded graph runs end-to-end §01→§15 via CLI" acceptance bar has its evidence pack ready, the v4.2 topology is preserved across the migration, and Slab 2 specialist migrations can drop into a known-good 15-step skeleton without re-deriving topology**.

## Acceptance Criteria

All ACs dev-agent-executable. Schema-shape-touching story (the migrated manifest is itself an instance of the 1.4 schema; if the schema needs minor extensions to fit v4.2, those are part of this story and round-trip back to 1.4's golden fixtures — coordinate).

### AC-1.6-A — Migrated v4.2 manifest authored

- **Given** the primary repo carries `state/config/pipeline-manifest.yaml` for the v4.2 production prompt pack (15 numbered steps §01-Source-Wrangle through §15-Assembly-Bundle); **per Winston/Amelia amendment 2026-04-22**, the v4.2 schema-delta inventory was completed at Story 1.4 authoring time (NOT deferred to this story's mid-implementation discovery), so `PipelineManifest` already accommodates v4.2's full field set when 1.6 opens
- **When** the dev agent authors the migration's version at `state/config/pipeline-manifest.yaml` (overwriting 1.1c's stub) conforming to 1.4's `PipelineManifest` schema:
  - `version: "v4.2-migration-stub"`
  - `lane: "run_graph"`
  - `frozen_graph_version: "v42"` (matches the existing `runtime/graphs/v42/` directory from 1.1b)
  - `entrypoint: "01_source_wrangle"`
  - `nodes`: 15 entries, one per v4.2 step; each `specialist_id` is the canonical specialist name (e.g., `texas`, `gary`, `irene`, `kira`, `quinn-r`, etc.); each `scaffold_node` is `"act"` (the central scaffold node — Slab 2 expands to all 9); each `model_config_ref` points to the per-specialist `app/specialists/{name}/model_config.yaml` (stub paths in 1.6; full configs land in Slab 2)
  - `edges`: serial chain §01 → §02 → ... → §15 (no conditionals in 1.6; conditionals + dispatch envelopes are Slab 2/3 territory)
- **Then** `app/manifest/loader.load("state/config/pipeline-manifest.yaml")` succeeds; the migrated manifest validates against the 1.4 schema with NO schema-extension surgery required at this story (1.4 absorbed the inventory). If a residual delta surfaces despite the upstream inventory pass, it is escalated to party-mode amendment of 1.4's golden fixtures in a sibling commit, NOT silently extended in 1.6.

### AC-1.6-B — Stub specialist callables registered

- **Given** the manifest references 15 `specialist_id` values that don't yet have real `app/specialists/{name}/graph.py` modules (full migration is Slab 2)
- **When** the dev agent authors `app/specialists/_stub/passthrough_specialist.py` exporting a `passthrough_node(state) -> dict` callable + a registration mechanism so the compiler from 1.4 resolves any `specialist_id` to `passthrough_node` at this stage
- **Then** the compiler from 1.4 produces a compiled `StateGraph` with all 15 nodes wired to the passthrough; each node returns the input state unchanged (no-op — Slab 2 will replace with real 9-node specialist scaffolds).

### AC-1.6-C — End-to-end §01→§15 smoke

- **Given** AC-1.6-A + AC-1.6-B are green
- **When** the dev agent extends `app/smoke_test.py` (from 1.1c) with a `run_full_smoke() -> dict` function that loads the migrated manifest, compiles, invokes from `entrypoint`, and threads through all 15 nodes; OR adds a CLI flag `--full` to `python -m app.smoke_test --full`
- **Then** the full smoke runs §01→§15 end-to-end; stdout shows `smoke ok (full)` + 15-node count; checkpoint after §15 is persisted in Postgres (skip-on-unreachable per sandbox-AC); LangSmith trace shows 15 spans with the contract tag set per node (skip when LANGSMITH_API_KEY unset).

### AC-1.6-D — M1 evidence test fixture

- **Given** M1 acceptance requires this end-to-end run as evidence
- **When** the dev agent authors `tests/end_to_end/test_full_pipeline_smoke.py` calling `run_full_smoke()` and asserting:
  - 15 nodes executed (count from a side-effect counter or LangSmith span count)
  - Final state has the deterministic post-§15 payload shape
  - Checkpoint write succeeded (or skipped cleanly)
- **Then** the test passes; this becomes part of the M1 evidence pack referenced by Slab 1 closeout (1.7).

### AC-1.6-E — Cache hit rate baseline (FR54 measurement)

- **Given** M1 acceptance includes "≥60% cache hit rate on second invocation"
- **When** the dev agent authors `tests/end_to_end/test_cache_hit_rate_baseline.py` that runs `run_full_smoke()` twice in succession + reads cache hit metadata from LangSmith spans (or the OpenAI client's cache reporting if available)
- **Then** on the second run, the cache hit rate ≥60% across LLM-invoking nodes — but **note**: in 1.6, the specialists are passthroughs (no LLM calls), so the test is a **scaffold** that asserts "0 LLM calls observed; cache-hit-rate baseline measurement deferred to first Slab 2 specialist landing." Mark with `pytest.skip(...)` until real specialists land. The fixture + plumbing exists; the assertion deferred.

## Tasks / Subtasks

- [ ] **T1 — Read T1 Bundle** §1 (D6 manifest, D8 frozen-graph), §2 (FR4, FR8, FR54), §6.
- [ ] **T2 — Read primary repo's v4.2 pipeline manifest** at `state/config/pipeline-manifest.yaml` (current primary version) to understand the 15-step topology + naming conventions. Inventory the 15 specialist names that need stub registration.
- [ ] **T3 — Author migrated manifest** per AC-1.6-A, conforming to 1.4 schema; coordinate schema extensions back to 1.4 if needed.
- [ ] **T4 — Author passthrough specialist + registration** per AC-1.6-B.
- [ ] **T5 — Extend `app/smoke_test.py`** with `run_full_smoke()` + CLI flag per AC-1.6-C.
- [ ] **T6 — End-to-end test** per AC-1.6-D.
- [ ] **T7 — Cache hit rate scaffold** per AC-1.6-E (skipped assertion).
- [ ] **T8 — Run validators + tests.**
- [ ] **T9 — Commit.** `feat(migration): Slab 1 Story 1.6 — pipeline manifest migration from primary + stub empty-graph smoke`

## Dev Notes

### Why the manifest migrates now (not at Slab 2)

Slab 2 lands the real specialists, but the topology contract (manifest shape + 15-step ordering + serial vs branching wiring) needs to land before specialist work begins so each specialist migration story has a slot to drop into. 1.6 lands the topology + passthrough scaffolding; Slab 2 stories swap passthroughs for real `app.specialists.{name}.graph` modules.

### v4.2 vs v4.1

Primary repo carries both v4.1 (narrated-deck-video-export) and v4.2 (narrated-lesson-with-video-or-animation, motion-enabled). The migration only carries v4.2 (per architecture decision — primary continues to maintain v4.1; migration's first frozen graph is v4.2). Confirm at T1 that the migrated manifest is v4.2-shape, not v4.1-shape.

### Schema-extension coordination with 1.4

If v4.2's manifest needs a field not in 1.4's `PipelineManifest` schema (e.g., a step ordinal, or a v4.2-specific metadata block), extend the schema in this story with the four-file-lockstep updates and note in the commit body that 1.4's golden fixtures were updated. Do NOT extend silently — review-quality issue.

### Cache-hit-rate plumbing without assertion

AC-1.6-E lands the measurement fixture but defers the actual assertion until real LLM-invoking specialists exist. This is the right shape: the M1 acceptance bar is "≥60% on second invocation" for runs that include LLM calls; in 1.6's passthrough world, there are no LLM calls to cache. Don't fake the test green — keep it explicitly skipped with a documented re-enablement trigger.

### Project Structure Notes

**New files:**
- `app/specialists/_stub/__init__.py`
- `app/specialists/_stub/passthrough_specialist.py`
- `tests/end_to_end/test_full_pipeline_smoke.py`
- `tests/end_to_end/test_cache_hit_rate_baseline.py`

**Modified:**
- `state/config/pipeline-manifest.yaml` (rewrite from 1.1c stub to v4.2-migration-stub shape)
- `app/smoke_test.py` (add `run_full_smoke()` + `--full` flag)
- `app/manifest/schema.py` (potentially — if v4.2 needs schema extension; coordinate with 1.4)
- `app/manifest/__init__.py` (potentially — register passthrough resolver)
- 1.4's golden fixtures (if schema extended)

## References

- Bundle: [Set-A T1 Context Bundle](../planning-artifacts/slab1-story-set-A-t1-bundle.md)
- Architecture D6 (manifest-as-graph-config), D8 (frozen-graph)
- PRD FR4 (resume), FR8 (manifest topology), FR54 (cache hit rate baseline)
- **Per Paige amendment 2026-04-22:** stable references via the pipeline-manifest-regime pointer chain (NOT raw filename), since the v4.2 pack file may move/rename during the migration:
  - Primary repo's manifest: `state/config/pipeline-manifest.yaml` (resolved by `frozen_graph_version: "v42"` field — stable identifier even if pack files move)
  - The frozen-graph-v42 pack lives where the manifest's `frozen_graph_version: "v42"` resolves; trace via `app/manifest/loader.py`'s `frozen_graph_version` validation logic (1.4 AC-1.4-C) rather than raw `production-prompt-pack-v4.2-narrated-lesson-with-video-or-animation.md` filename. Pipeline-manifest-regime authority: [`docs/dev-guide/pipeline-manifest-regime.md`](../../docs/dev-guide/pipeline-manifest-regime.md) (per CLAUDE.md §Pipeline lockstep regime).

## Dev Agent Record

_(placeholder)_
