# Ambient `tests/contracts/` Debt Triage — 2026-06-23

**Charge:** Diagnose (NOT fix) the 14 pre-existing ambient contract-test failures tracked by deferred-inventory item `ambient-contract-test-suite-debt`. Baseline-proven pre-existing on clean HEAD `829bc53`; NOT caused by the in-flight reading-path / perception (S2) work.

**Diagnosis run:** `.venv/Scripts/python.exe -m pytest <nodeid> -q` on the 14 named nodes only (no full-suite run — avoided in-flight S2 noise per charge). All 14 reproduced as failing.

## Headline root-cause distribution

| Class | Count | Tests |
|---|---|---|
| **(a) STALE PIN** (substrate legitimately moved; safe re-pin) | **13** | all fit_report (4) + coverage_manifest (1) + canonical-caller (1) + dispatch-monopoly (1) + single-writer-routing (1) + quinn-r-gate (1) + 33-2 disjoint-keys (1) + transform-registry (1) + provider-roster (1) + 30-1 zero-edit (1) |
| **(b) REAL CONTRACT DRIFT** (producer/consumer genuinely diverged) | **0** | — |
| **(c) ENVIRONMENTAL** (missing dep/path outside repo) | **0** | — |

**Dominant single cause: the `app/` migration severance.** Production code + schemas + the retrieval package moved under `app/marcus/`, `app/...`, and `state/config/` gained a second pipeline manifest, but ~11 of the 14 contract tests still pin the OLD repo-root paths (`marcus/...` without the `app/` prefix) or were authored before a second manifest / new registry sections / promoted provider existed. None of the failures reflects a genuine producer↔consumer divergence — in every case the producing substrate is correct and the *test's pinned reference* is stale.

> **Note on the legacy root `marcus/` tree:** a stale duplicate `marcus/{intake,lesson_plan,orchestrator}/` still exists at repo root alongside the canonical `app/marcus/`. The fit_report/coverage/quinn tests resolve to the root `marcus/...schema/...` path which has NO schema files (they live only under `app/marcus/...`). This root tree is itself latent cleanup debt (cf. `migration-tech-debt-app-marcus-stub-disposition` direction-flip precedent in CLAUDE.md) but is out of scope for this triage.

---

## Per-test table

| # | Test (nodeid) | Root cause | 1-line evidence | Difficulty | Safe in isolated pass? |
|---|---|---|---|---|---|
| 1 | `test_fit_report_v1_schema_stable.py::test_fit_report_schema_file_exists` | (a) STALE PIN — path | `SCHEMA_PATH` = `parents[2]/"marcus"/...` but schema lives at `app/marcus/lesson_plan/schema/fit_report.v1.schema.json` (confirmed present) | trivial | YES |
| 2 | `…::test_fit_report_schema_title_and_version` | (a) STALE PIN — path | same `FileNotFoundError` on `marcus/.../fit_report.v1.schema.json`; only `app/marcus/...` exists | trivial | YES |
| 3 | `…::test_fit_report_property_coverage_matches_pydantic` | (a) STALE PIN — path | same path miss; `from app.marcus.lesson_plan.schema import FitReport` import itself succeeds (6 fields) | trivial | YES |
| 4 | `…::test_fit_diagnosis_property_coverage_matches_pydantic` | (a) STALE PIN — path | same path miss | trivial | YES |
| 5 | `…::test_fit_diagnosis_fitness_enum_matches` | (a) STALE PIN — path | same path miss | trivial | YES |
| 6 | `test_coverage_manifest_json_schema_parity.py::test_coverage_manifest_json_schema_parity` | (a) STALE PIN — path | identical `SCHEMA_PATH = parents[2]/"marcus"/...` drift; file is at `app/marcus/lesson_plan/schema/coverage_manifest.v1.schema.json` | trivial | YES |
| 7 | `test_fit_report_canonical_caller.py::test_emit_fit_report_not_imported_outside_canonical_callers` | (a) STALE PIN — prefix | walks `app/marcus` but `ALLOWED_PRODUCTION_IMPORT_PREFIXES` are root `marcus/orchestrator/`; offender is a *comment* at `app/marcus/orchestrator/write_api.py:151` ("…see emit_fit_report.") — no real import | trivial | YES |
| 8 | `test_30_2b_dispatch_monopoly.py::test_dispatch_is_sole_orchestrator_caller` | (a) STALE PIN — prefix | `_ALLOWED_CALLERS` are root `marcus/orchestrator/{dispatch,write_api}.py`; test walks `app/marcus/orchestrator`, relativizes to `app/marcus/...` → allow-set never matches | trivial-moderate | YES |
| 9 | `test_marcus_single_writer_routing.py::test_intake_and_orchestrator_packages_route_through_write_api` | (a) STALE PIN — prefix | identical `app/` vs root prefix mismatch in `_ALLOWED_APPEND_EVENT_CALLERS` | trivial-moderate | YES |
| 10 | `test_quinn_r_gate_no_log_boundary.py::test_quinn_r_gate_does_not_call_lesson_plan_log_write_surface` | (a) STALE PIN — path | reads `Path("marcus/lesson_plan/quinn_r_gate.py")` (relative, root); file is at `app/marcus/lesson_plan/quinn_r_gate.py` → `FileNotFoundError` | trivial | YES |
| 11 | `test_33_2_state_config_disjoint_keys.py::test_pipeline_manifest_keys_do_not_shadow_other_state_configs` | (a) STALE PIN — scope | test globs ALL `state/config/*.yaml`; new Slab-1 `pipeline-manifest-substrate-stub.yaml` (legit second manifest, docstring self-identifies as smoke stub) shares `nodes/edges/pack_version/...` → false collision | trivial-moderate | YES |
| 12 | `test_transform_registry_lockstep.py::test_every_format_covered_or_exempted` | (a) STALE PIN — constants | registry gained 2 new sections ("Box (fetch layer)", "Image (intake via sensory-bridges)"); both have REAL wiring in `run_wrangler.py` (`wrangle_box_file` @ line 765, image dispatch @ 768) but the test's `REGISTRY_METHOD_TO_EXTRACTOR`/`LOCKSTEP_EXEMPTIONS` constants weren't updated in lockstep | moderate | YES (with care — see below) |
| 13 | `test_provider_directory_roster_placeholders.py::…[consensus-retrieval-ratified]` | (a) STALE PIN — value | consensus adapter was promoted from stub → live, so supersession contract flips status `ratified`→`ready` (same pattern the test already documents for scite); pinned row still expects `ratified`. Got `'ready'` | trivial | YES |
| 14 | `test_30_1_zero_test_edits.py::test_no_preexisting_test_files_modified_in_30_1` | (a) STALE PIN — baseline | pins baseline `4911fc4` (reachable); 965 test files added/modified since then across many subsequent epics + the `app/` migration. Test's own docstring mandates rollforward at each downstream story close — never done | moderate-hard | YES (see ownership note) |

---

## Recommended cleanup-pass batch order

**Batch 1 — trivial path/prefix re-pins (tests 1–10).** Pure substrate-relocation drift; the producing artifacts are all correct and present. Fix by updating each test's `SCHEMA_PATH` / `Path(...)` / `ALLOWED_*` prefix from `marcus/...` → `app/marcus/...`. Highest-confidence, lowest-risk, ~10 one-line edits. Do these first; they clear 10 of 14 with near-zero judgment.
  - 1–6, 10: change the `marcus` path segment to `app/marcus` (or insert `"app"` into the `Path(...).parents[2] / ...` chain).
  - 7–9: change the `ALLOWED_*` prefix constants to `app/marcus/...` so the allow-set matches the walked tree. (Verify-after: test 7's only "offender" is a comment, so once the prefix matches it goes green; confirm no genuine new importer exists — grep already shows none.)

**Batch 2 — single-value / scope re-pins (tests 11, 13).** Still trivial-moderate but need one judgment call each:
  - **13 (provider consensus):** flip the parametrize row `("consensus", "retrieval", "ratified")` → `("consensus", "retrieval", "ready")`. The supersession is intended behavior the test already documents for scite — pure re-pin.
  - **11 (disjoint-keys):** add `pipeline-manifest-substrate-stub.yaml` to an exclusion set (mirror the existing `pipeline-manifest.yaml` skip) OR scope the glob to non-stub manifests. The stub is a sanctioned Slab-1 artifact; the contract's intent (no *accidental* shadowing) is preserved by exempting the deliberate second manifest.

**Batch 3 — registry lockstep (test 12).** Moderate; **owner input recommended (Texas).** Both new sections have real extractors, so the correct remediation is to ADD entries to `REGISTRY_METHOD_TO_EXTRACTOR` (Box, Image) with their dispatch-presence regexes, NOT to add bare exemptions. Confirm the regex shapes against the current `_fetch_source` source-text (the module docstring warns this is a source-inspection contract). Light Texas/retrieval-owner sanity check before committing the new regexes.

**Batch 4 — 30-1 zero-edit baseline rollforward (test 14).** Moderate-hard; **needs governance/owner decision.** This is the only one that is not a one-line re-pin. Options: (a) roll the `_PRE_30_1_BASELINE_COMMIT` forward to a recent clean post-migration commit and trim the allowlists per the test's documented rollforward policy, or (b) retire the pin if the Marcus-duality lane it guarded is closed. 965 changed test files means the historical invariant has fully lapsed. Recommend confirming with the Marcus-duality lane owner whether the invariant is still load-bearing before rolling forward vs retiring — do NOT silently expand the allowlist to 965 entries.

### Sequencing summary
1. **Batch 1** (tests 1–10) — do immediately, mechanical, clears 71%.
2. **Batch 2** (11, 13) — same pass, one judgment call each.
3. **Batch 3** (12) — same isolated pass, optional Texas confirm on regexes.
4. **Batch 4** (14) — separate; gate on lane-owner/governance input (rollforward vs retire).

All 14 are **safe to fix in an isolated cleanup pass** (no producer code change required, only test-pin updates). 13/14 are mechanical re-pins; only test 14 carries a governance question. None touches the S2-in-flight paths (`app/specialists/vision/*`, `app/models/perception/*`, `scripts/utilities/reading_path_*`).
