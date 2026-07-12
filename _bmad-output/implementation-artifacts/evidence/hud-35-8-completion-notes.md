# Story 35.8 — Legacy retirement + import fences — Completion Notes

**Branch:** dev/hud-revival-2026-07-11 (working tree only — no commit by dev agent)
**ADs:** 8, 12, paradigm arrows. **Sequenced after 35.5 (render retarget) + 35.9 (contract enrichment).**

## Summary

Retired the legacy static-HTML HUD generator and its data layer; added the
notifier-lane import fence; documented the two non-import-linter-expressible
rules. `run_hud.py` survives as a manifest-derived stub so the pipeline regime
(L1 lockstep) and its two lockstep pins keep their import surface.

## Deleted vs stubbed (grep-driven)

Grep of `run_hud` / `hud_data_sources` importers across `app scripts tests`
drove every decision:

| File | Disposition | Why |
| --- | --- | --- |
| `scripts/utilities/run_hud.py` | **STUBBED** (1466 → ~80 LOC) | `PIPELINE_STEPS` is imported by production `check_pipeline_manifest_lockstep.py` (line 21) and by the `test_projection_equality.py` / `test_marcus_workflow_runner_32_1.py` lockstep pins — so the import surface MUST survive. Kept `PIPELINE_STEPS = hud_steps(load_manifest())` (pure manifest projection); deleted the entire HTML render surface, `collect_hud_data`, all `_render_*` panels, and the **silent wrong-run fallback** (`_query_active_run_id` coordination.db reader → `_find_latest_bundle` newest-mtime chain — the April defect, AD-8). `main()` now prints a deprecation pointer at `python -m app.hud.server` / `trial hud` and returns exit code 2. |
| `scripts/utilities/hud_data_sources.py` | **DELETED** | Grep proof: the only importers were `run_hud.py` (now stubbed, import removed) and `tests/unit/hud/test_hud_data_sources.py` (deleted with it). No other production code imports it (remaining hits are docstrings/comments in `app/hud/__init__.py`, `app/hud/server.py`, `pyproject.toml`, and docs that name it only to say "never import this"). |
| `tests/test_run_hud.py` | **REDUCED** to a retirement smoke test | Removed the two story-35.0 `retired-by-35.8` `pytest.mark.skip`s. New file pins: (a) stub CLI exits non-zero (== `DEPRECATION_EXIT_CODE` = 2) and names `app.hud.server` + `trial hud`; (b) `PIPELINE_STEPS` still exposed + manifest-shaped; (c) retired symbols (`collect_hud_data`/`render_html`/`_query_active_run_id`) do not reappear. File kept (not deleted) so its `block_mode_trigger_paths` row and the `test_33_4_*` trigger-path consistency tests stay valid. |
| `tests/integration/hud/test_per_step_summary_rendering.py` | **DELETED** | Exercised the deleted generator internals (`hud.collect_hud_data` / `hud.render_html`). |
| `tests/integration/hud/test_hud_watch_mode.py` | **DELETED** | Exercised the deleted generator CLI watch mode (`hud.main([...--watch...])`). |
| `tests/unit/hud/test_hud_data_sources.py` | **DELETED** | Imported the deleted `hud_data_sources` module directly. |

`run_hud.py` and `tests/test_run_hud.py` both **kept as stubs**, so their
`state/config/pipeline-manifest.yaml::block_mode_trigger_paths` rows remain
valid — **no manifest edit was required** (`hud_data_sources.py` was never a
trigger-path row; grep-confirmed). `progress_map.py` / `test_progress_map.py`
untouched.

## Import-linter contracts added (`pyproject.toml`)

- **HUD2 (new):** `forbidden` — `source_modules = ["app.notify"]`,
  `forbidden_modules = ["app.marcus.orchestrator", "app.gates", "scripts"]`,
  `include_external_packages = true`. Mirror of the existing HUD1 (`app.hud`)
  fence. Covers "app.notify ↛ orchestrator" (task 4 bullet) AND "app.notify ↛
  hud_data_sources" (the whole-`scripts` fence, since `hud_data_sources` lived
  under `scripts/`). Verified `app/notify/service.py` imports only the
  contract (`app.models.runtime.operator_surface`) + stdlib + apprise, so the
  contract lands KEPT.
- **"nothing may import hud_data_sources" — documented, not a new global
  contract.** The module is DELETED (no import possible). A truly global
  `anything → hud_data_sources` contract would require adding `scripts` to
  `[tool.importlinter].root_packages`, pulling the entire `scripts/` tree into
  contract analysis (large unrelated surface, likely pre-existing violations +
  major slowdown). Declined deliberately: `app` is the sole root_package, and
  the only two app-side layers AD-3/AD-8 binds — `app.hud` (HUD1) and
  `app.notify` (HUD2) — already forbid the whole `scripts` tree, a strictly
  stronger fence than naming one deleted module. Documented inline in
  pyproject.toml.
- **AD-4 consumer-must-not-strict-parse — documented as in-code-enforced.**
  Not import-linter-expressible: the strict producer model and
  `read_operator_surface_lenient` are same-module symbols in
  `app.models.runtime.operator_surface`; import-linter is module-granular, not
  symbol-granular. Enforced in-code + by HUD server route tests. Note added to
  pyproject.toml.

Result: **18 contracts kept, 0 broken** (was 17; +HUD2).

## Guard allowlist edit

`tests/contracts/test_30_1_zero_test_edits.py` — added the four touched
`tests/` paths to `_ALLOWED_MODIFIED_PATHS_UNDER_TESTS` (the guard treats
M/D/R identically) with a story-35.8 comment block: `tests/test_run_hud.py`
(M), and the three deleted suites (D). The guard compares `20cd0744..HEAD`
(committed range) so it is green on the current uncommitted tree; the
allowlist keeps it green once the orchestrator commits.

## Verification (all green except the ONE sanctioned pre-existing red)

- `.venv/Scripts/python.exe scripts/utilities/check_pipeline_manifest_lockstep.py` → **exit 0** (PASS trace written).
- `lint-imports --config pyproject.toml` → **18 kept, 0 broken** (exit 0).
- `ruff check` on changed files → **All checks passed!**
- `python -m scripts.utilities.run_hud` (real CLI smoke) → prints deprecation
  pointer, **exit 2**.
- `pytest tests/hud tests/notify tests/unit/marcus tests/contracts tests/unit/models tests/test_progress_map.py`
  → **1364 passed, 1 skipped, 1 failed** — the single failure is the
  story-sanctioned pre-existing red
  `tests/contracts/test_transform_registry_lockstep.py::test_every_format_covered_or_exempted`.
- Targeted retirement + regime pins
  (`test_run_hud.py`, `test_projection_equality.py`,
  `test_marcus_workflow_runner_32_1.py`, `test_preclosure_hook.py`,
  `test_30_1_zero_test_edits.py`, `test_33_4_*`, `test_schema.py`,
  `test_companion_assertion_per_path.py`, `tests/unit/hud`, `tests/integration/hud`)
  → all pass except the two below.

## Deviation — second pre-existing red (NOT introduced by 35.8)

`tests/unit/hud/test_per_step_summary_derivation.py` has 2 failures
(`test_all_manifest_hud_steps_have_known_derivation_source`,
`test_each_manifest_step_has_pinned_derivation_function`): manifest step
`07D.5` has no `derive_step_07d_5_summary` in `hud_per_step_summary.py`.
**Confirmed pre-existing** — fails identically on clean HEAD (`e524f42c`) with
my changes stashed. It is unrelated to legacy retirement (touches
`hud_per_step_summary.py` + the manifest `07D.5` node, neither owned by 35.8),
so left untouched per kill-switch / no-scope-creep discipline. Flag for the
07D.5 motion-plan-producer owner; candidate for a `LOCKSTEP_EXEMPTIONS`-style
follow-on. The story spec's "only ONE pre-existing red" claim should be
updated to name this second one.

## Files changed

```
 M pyproject.toml                                              (+HUD2 contract + 2 doc notes)
 M scripts/utilities/run_hud.py                                (1466 → ~80 LOC stub; PIPELINE_STEPS kept)
 D scripts/utilities/hud_data_sources.py
 M tests/test_run_hud.py                                       (reduced to retirement smoke test)
 D tests/integration/hud/test_hud_watch_mode.py
 D tests/integration/hud/test_per_step_summary_rendering.py
 D tests/unit/hud/test_hud_data_sources.py
 M tests/contracts/test_30_1_zero_test_edits.py                (allowlist: +4 paths)
```
