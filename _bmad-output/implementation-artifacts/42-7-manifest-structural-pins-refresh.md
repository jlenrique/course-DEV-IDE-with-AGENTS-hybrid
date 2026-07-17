---
id: 42-7
epic: 42
status: ready-for-dev   # rider R3 from the Epic-42 sign-off; pre-existing manifest-pin debt surfaced by 42-5
depends_on: null
gate_mode: single-gate   # test-pin + golden-fixture refresh (no app-source manifest change)
baseline_commit: 39f006ac
lockstep: true   # manifest shape pins + golden fixtures are lockstep governance
---

# Story 42.7: Refresh the stale manifest structural pins to the live 52-node manifest — rider R3

Status: done  # 2026-07-17 dev complete + review PASS; rider R3 RESOLVED — 9 stale pins refreshed to the live 52-node manifest

## Dev Agent Record + Review — 2026-07-17

**Dev complete (fresh Claude dev agent). Baseline `39f006ac`. Reviewed inline (hermetic; no windows). APPROVE.**

### What changed
- Node count `45 → 52` (test_compiler, change-detector kept hardcoded + history extended `45→47→51→52`, attributed via per-commit `git show`: 45→47 g0-ratify-gate G0R `b59679ce`; 47→51 07W workbook band `fc108553`; 51→52 G0S `8d485ace`).
- Gate topology counts (unfolded 21 / folded 9 active pause points) **converted to DERIVED** from an independent structural SSOT (not the renderer's own fold logic → still a genuine guard, not a tautology).
- `production_gate_ids` frozenset += G0R, G0S; fold-emit mapping + fold-with declarations += G0R/G0S (change-detector pins updated with the new live values).
- Golden schema fixtures `schema_pin_{pipeline_manifest,node_spec}.json` regenerated from `model_json_schema()`.
- Files: `tests/unit/manifest/{test_compiler,test_gate_topology_cli,test_production_gate_ids_derived,test_gate_fold_manifest_emit,test_manifest_fold_with_declarations}.py` + `tests/fixtures/manifest/schema_pin_*.json`.

### Review verification
- Full `tests/unit/manifest/` = **74 passed** (9 named pins green); `check_pipeline_manifest_lockstep.py` exit 0 (enforced gate unaffected); ruff clean; import-linter 18/0.
- Diff scope = only `tests/unit/manifest/**` + `tests/fixtures/manifest/*.json` (no manifest yaml / app source — the `gamma-styleguide-picks.jsonl` dirty file is pre-existing, not this story).
- **Golden regen confirmed ADDITIVE-ONLY (orchestrator verified):** `dependencies`/`fold_target` preserved (reordered, not removed); the only additions are OPTIONAL `dependency_projections` + `ProjectionSpec` `$def` (the data-plane key-projection feature) + optional `data_plane_vocabulary_version` — NEITHER is in any `required` array; the 2 new `required` blocks are the new `ProjectionSpec`'s own (`['from','key']`), not a narrowing of an existing model. No breaking schema change.
- **AC-3 judgment sound:** change-detector pins (node count, gate-id set) stayed hardcoded (their design is to force a conscious update); pure counts (gate topology) derived-from-live so they self-maintain.

**Findings:** none. Clean, careful governed-fixture refresh.

## Story

As a maintainer,
I want the `tests/unit/manifest/` structural pins to match the live 52-node manifest (and, where sensible, be derived-from-live so they self-maintain),
so that the suite is green and future manifest changes don't silently drift these pins again.

## Why (rider R3)

The Epic-42 sign-off (`epic-42-signoff-party-record-2026-07-17.md`) filed R3: ~9 `tests/unit/manifest/` pins are stale vs the live manifest. They drifted BEFORE this arc — `test_compiler.py::test_compile_real_repo_root_with_migrated_v42_manifest` hardcodes `len(m.nodes) == 45` (comment history 37→40→43→45) while the live manifest was already **51 nodes** at `516ca453` and is **52** now (G0S from 42-5). The 07W workbook band + wave 39/40 stories + G0-S2 grew the manifest without updating these hardcoded pins. The ENFORCED lockstep gate (`check_pipeline_manifest_lockstep.py`) and the DYNAMIC sync pin (`test_production_gate_id_literal_stays_in_sync_with_manifest`) are green — only these older hardcoded pins lag.

## The 9 stale pins (baselined pre-existing, net-new to fix)

1. `test_compiler.py::test_compile_real_repo_root_with_migrated_v42_manifest` — `len(m.nodes) == 45` → live 52.
2. `test_gate_topology_cli.py::test_unfolded_topology_lists_all_declared_gates` + `::test_folded_topology_lists_active_pause_points_only` — `output.count("|") == 19` (gate count).
3. `test_production_gate_ids_derived.py::test_production_gate_ids_from_live_manifest` — the live production-gate-id set (add G0S + any other gates added since).
4. `test_gate_fold_manifest_emit.py::test_emit_live_manifest_produces_expected_mapping` + `::test_emit_lists_all_declared_gate_codes` — expected fold mapping / gate-code list.
5. `test_manifest_fold_with_declarations.py::test_live_manifest_declares_canonical_fold_with_values` — canonical fold-with values.
6. `test_schema_pin.py::test_live_schema_matches_pinned_fixture[pipeline_manifest]` + `[node_spec]` — committed GOLDEN fixtures `tests/fixtures/manifest/schema_pin_{pipeline_manifest,node_spec}.json` (regenerate from live schema).

## Acceptance criteria

1. **All 9 pins green against the LIVE manifest.** Update each hardcoded value to the live manifest's actual value (52 nodes; the real gate count/set incl. G0S; the real fold mapping/values), with a documented drift-history comment (extend the existing `37→40→43→45→52` style so the WHY is auditable — name what added the nodes: 07W band, wave 39/40, G0-S2, G0S).
2. **Golden schema fixtures regenerated correctly.** `schema_pin_pipeline_manifest.json` + `schema_pin_node_spec.json` regenerated from the CURRENT live schema (the model's `model_json_schema()`), reviewed for sanity (not blindly overwritten) — confirm the diff is only the legitimate additive growth (new node/gate kinds, G0S), not an unexpected structural change.
3. **Prefer DERIVED-from-live where safe (anti-drift).** Where a pin is a pure count that WILL drift again (e.g. node count, gate count), convert it to derive the expected value from the live manifest / a single source of truth rather than a fresh hardcode — UNLESS the hardcode is load-bearing as an intentional change-detector (in which case keep it hardcoded with the history comment, so a manifest change is a conscious pin update). Document the choice per pin.
4. **No app-source manifest change.** This is a TEST + golden-fixture refresh only — do NOT edit `state/config/pipeline-manifest.yaml` or any manifest app source. The live manifest is authoritative (it compiles, the enforced lockstep gate passes, runs work); the pins are catching up to it.
5. **Net-new = 0 elsewhere.** Consumer-wide check: the 9 pins go green; no OTHER test regresses. Confirm `check_pipeline_manifest_lockstep.py` still exit 0 (the enforced gate is unaffected).

## Scope fences (hard NO)

- NO change to `state/config/pipeline-manifest.yaml` or manifest app source (`app/manifest/**`) — the manifest is authoritative; pins catch up.
- NO weakening/deletion of a pin to make it pass — update it to the correct live value or derive it; a change-detector pin stays a change-detector.
- NO blind golden overwrite — review the schema-fixture diff for legitimacy.
- Only `tests/unit/manifest/**` + `tests/fixtures/manifest/*.json` (+ TW-7c-4 allowlist if a new test file).

## Validation

- The 9 named pins green; `tests/unit/manifest/` fully green.
- `check_pipeline_manifest_lockstep.py` exit 0; ruff clean; import-linter 18/0.
- Baseline-diff: net-new = 0 (the 9 flip red→green; nothing else changes).

## References
- `epic-42-signoff-party-record-2026-07-17.md` (rider R3); `deferred-inventory.md` `manifest-structural-pins-stale-vs-live`.
- `docs/dev-guide/pipeline-manifest-regime.md` (lockstep governance for manifest shape).
