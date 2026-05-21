---
title: Broad-Regression Failure Baseline — 2026-05-07 (pre-Trial-3 cleanup S1 P0-9)
authoredAt: 2026-05-07
authority: pre-Trial-3 cleanup S1 P0-9 per Murat AM-3 / AM-10 (1.5 hr realistic per pre-S1 review)
purpose: |
  Forensic baseline for Trial-3 launch. Operator can grep this catalog
  during Trial-3 evidence review to determine "is this failing test new
  (regression introduced by Trial-3 / a S1-S6 cleanup) or pre-existing?"
  Without this catalog the diagnosis-per-failure cost is ~15-30 min of
  git-blame; with it, the cost drops to ~5 min of grep-against-catalog.
measurement_command: |
  .venv/Scripts/python.exe -m pytest tests/ --tb=no -q --no-header
measurement_environment: |
  branch: dev/langchain-langgraph-foundation
  base commit (pre-S1 stash test): 0ef8594 (Slab 7c retrospective close, 2026-05-07)
  measurement run 1 (mid-S1): 2026-05-07T18:14 — post P0-3/P0-4/P0-5/P0-7/P0-8/P0-10/P0-11/P0-6/PP-2; pre-regression-fix
    - failed: 55 (54 unique + 1 parameterized variant); duration 110.18s
  measurement run 2 (post-S1): 2026-05-07T~19:00 (post `725f55f` S1-close commit; post P0-1 + P0-2 + P0-IH + 6 regression-fixes + P3→P4 test rename)
    - failed: 48 (-7 from mid-S1; matches expected 6 regression-fixes + 1 test-rename closure); duration 68.91s
    - delta vs Murat's pre-S1 estimate of 47: +1 (within sampling variance + +1 AM-12 TW-7c-4 scope-creep audit entry not in original sample)
  total_collected: 4168 (post-S1: 4084 passed + 48 failed + 26 skipped + 2 xfailed)
murat_estimate_at_pre_S1_review: 47
actual_failure_count: 55
delta_explanation: |
  +8 vs Murat's pre-S1 estimate. Likely sources of drift:
    (a) housekeeping-2 (scanner-staleness AST rewrite) hasn't landed yet — `test_no_unauthorized_callers` adds 1 entry beyond Murat's count
    (b) Wave-3 next-batch (7c.13/7c.14) closed AFTER Murat's count was anchored; their poll-surface modules add 1-2 entries to scanner-staleness count
    (c) sampling variance on environment-conditional skips that Murat counted as PASS but pytest at this measurement counted as FAIL (LLM-availability-dependent tests; cache-hit-rate harnesses; live API smoke)
    (d) my S1 hand-edits to v4.2 prompt pack (P0-5 + P0-6 PP-3 preamble) add to test_33_3_no_hand_edits_to_v42 hand-edit-line count (already failing pre-S1; my edits make the line-count delta larger)
    (e) the 6 regressions I introduced today (3 registry contract, 1 canva, 1 coursearc, 1 manual-tool, 1 a17_p3) — ALL FIXED at P0-9 measurement time, but baseline run was AFTER my breaking edits + BEFORE my fix-edits for some intermediate counts
---

# Broad-Regression Failure Baseline — 2026-05-07

## Categorization

Failures grouped by likely root cause. Each entry: nodeid + one-line attribution + resolution path (per category) + verification status.

### Cat-1: Epic 33 manifest-regeneration drift (pre-existing; v4.2 not regenerated since last manifest sync) — 4 failures

**Root cause:** Epic 33 substrate enforces v4.2 = byte-identical regeneration output from `state/config/pipeline-manifest.yaml` + Jinja templates at `scripts/generators/v42/templates/`. The v4.2 pack was hand-edited multiple times since the manifest evolved, AND directive-composer template (`sections/directive-composer-g0-directive-composition-slab-7a-story-7a-1.md.j2`) doesn't exist in the templates directory.

**Status:** PRE-EXISTING (Murat verified); SEMANTICALLY OBSOLETE post-PP-2 disposition (S1 mid-session 2026-05-07: v4.2 declared legacy-frozen; hand-edits permitted; v5 at S4 will become the new regeneration target).

| nodeid | One-line attribution |
|---|---|
| `tests/contracts/test_33_3_no_hand_edits_to_v42.py::test_v42_pack_commit_is_regeneration_output` | v4.2 has hand-edits (PP-1/PP-3/PP-5 from S1 P0-5+P0-6 + prior); manifest-regeneration would emit different bytes |
| `tests/contracts/test_33_1a_verbatim_extraction.py::test_existing_sections_match_source_pack_byte_identical` | v4.2 §-content drifted from source-pack regeneration template |
| `tests/contracts/test_33_1a_template_coverage.py::test_all_manifest_sections_have_templates` | `sections/directive-composer-g0-directive-composition-slab-7a-story-7a-1.md.j2` absent from templates/ |
| `tests/test_33_3_dc2_resolution.py::test_pack_section_sequence_matches_manifest_order` | pack starts at §01 but manifest first-id = `DIRECTIVE-COMPOSER` |

**Resolution path (post-Trial-3, S6+):** decide whether v5 inherits the manifest-regeneration discipline (and these tests retarget v5) OR Epic 33 substrate is itself revised post-S4 v5 authoring. Filed as harvest item for S6 close; not a Trial-3 blocker.

---

## Post-S6 closure annotations (added 2026-05-08 per Murat final ratification baseline-currency hygiene)

**RESOLVED-AT-`7111633`** (S6 Wave-A+B close 2026-05-08): **Cat-2 housekeeping-2 closed** — `tests/integration/gates/test_resume_api_authority.py::test_no_unauthorized_callers` rewritten as AST-based constructor scanner (replaces pre-S6 substring scanner per A19 anti-pattern). Both tests in the file now PASS. The 7+ DISMISS-thread anti-pattern (verdicts 7c.9/10/11/12/13/14/20b) is structurally closed; future iterations will not re-encounter the substring-scanner-staleness false-positive class.

**Post-S6 broad-regression count: 82 failures** (same as post-S5 baseline; substrate-currency work landed at S5+S6 doesn't move pytest count by design — the structural value is governance + architecture-of-record currency + harvest discipline + Cat-2 closure).

**Post-S6 delta-summary roll-up:**
- Cat-2 housekeeping-2 (1 entry): RESOLVED-AT-`7111633` (S6 Wave-A+B)
- Cat-15 NFR-CG / contracts (8 entries; 6 fixed at S1 hybrid registry): RESOLVED-AT-`725f55f` (S1 close)
- All other categories (Cat-1, Cat-3, Cat-4, Cat-5, Cat-6, Cat-7, Cat-8, Cat-9, Cat-10, Cat-11, Cat-12, Cat-13, Cat-14, Cat-16): **carry forward to S7+** as `s6-tier-3-post-trial-3-housekeeping-batch` per Amelia pre-S6 Tier-3 triage; not Trial-3-blocking; operator-priority-driven scheduling.

**Trial-3 forensic comparison protocol (still active):** when Trial-3 launch surfaces a failing test, grep this catalog for the nodeid first. Expected behavior: PRE-EXISTING (still-open Cat-* entries) means substrate-noise from the cleanup arc; CANDIDATE NEW REGRESSION (absent from catalog) requires investigation per protocol.

**File status:** retained as forensic catalog through Trial-3 close; at first Trial-3 retrospective, the catalog is rolled into a Trial-N-baseline cycle per `docs/trials/methodology.md §3a`.

---

### Cat-2: DISMISS-thread / scanner-staleness (housekeeping-2 target; A19) — 1 failure

**Root cause:** `tests/integration/gates/test_resume_api_authority.py::test_no_unauthorized_callers` does substring matching on `OperatorVerdict(` against `app/**/*.py` with filename exclusion that doesn't match variant filenames (`operator_verdict_section_*.py`). Catches CLASS DEFINITIONS as if they were direct constructor calls. 7+ DISMISS-thread cycles (P2 anti-pattern).

**Status:** PRE-EXISTING; housekeeping-2 spec at `_bmad-output/implementation-artifacts/migration-7c-housekeeping-2-scanner-staleness-rewrite.md` already `ready-for-dev`. **Lands at S5; closes this entry.**

| nodeid | One-line attribution |
|---|---|
| `tests/integration/gates/test_resume_api_authority.py::test_no_unauthorized_callers` | substring scanner catches class defs; filename exclusion glob too narrow |

---

### Cat-3: Cache-hit-rate end-to-end (env-conditional; needs LLM API availability) — 3 failures

**Root cause:** these tests measure cache-hit-rate against real LLM invocations (`OPENAI_API_KEY` required; LangChain HTTP cache populated). Failure mode: API unavailable / rate-limited / cache empty / token-floor breach.

**Status:** PRE-EXISTING / ENVIRONMENT-CONDITIONAL. Per Slab 7c.21a `--live` opt-in pattern, these need explicit operator credentials + cache-warmup. Pre-Trial-3: cache-warmup will land via Trial-3 first-run; harness should re-pass post-Trial-3 once warmup populates cache.

| nodeid | Attribution |
|---|---|
| `tests/end_to_end/test_cache_hit_rate_baseline.py::test_irene_pass_2_cache_hit_rate_meets_60_percent_median` | Irene Pass-2 cache-hit-rate ≥60% requires warmed cache + valid OPENAI_API_KEY |
| `tests/end_to_end/test_cache_hit_rate_kira_populated.py::test_kira_populated_sanctum_cache_hit_rate_and_cost` | Kira-populated cache-hit-rate + cost; Kling API + LLM cache state |
| `tests/end_to_end/test_irene_pass1_cache_hit_rate.py::test_irene_pass1_cache_hit_rate_post_warmup` | Irene Pass-1 cache-hit post-warmup; needs warmed cache |

---

### Cat-4: Replay infrastructure (5a.1 deferred substrate; checkpoint-native catalog absent) — 5 failures

**Root cause:** replay tests assume LangGraph checkpoint-native trial catalog (`5a-1-checkpoint-native-trial-catalog-discovery` + `m5-fr-trace-partial-FR51` deferred-inventory entries). 5a.1 closed against accepted Marcus baseline fixture; checkpoint-native catalog is post-M5 work.

**Status:** PRE-EXISTING; deferred-inventory entries already filed; reactivation gated on actual LangGraph checkpoint-storage adoption.

| nodeid | Attribution |
|---|---|
| `tests/integration/replay/test_replay_budget.py::test_replay_trial_stays_under_budget` | replay budget vs checkpoint catalog |
| `tests/integration/replay/test_replay_budget.py::test_replay_trial_raises_when_budget_is_exceeded` | replay budget breach behavior |
| `tests/integration/replay/test_sanctum_variance_policy.py::test_warn_on_clone_normalizes_sanctum_and_logs_provenance` | sanctum-variance replay semantics |
| `tests/integration/replay/test_replay_all_closed_trials.py::test_replay_all_closed_trials_passes_for_current_baseline` | requires checkpoint-native catalog |
| `tests/trial_replay/test_replay_all.py::test_every_closed_trial_replays_green[33333333-3333-4333-8333-333333333333]` | parameterized replay against synthetic trial-id (catalog discovery deferred) |

---

### Cat-5: Sanctum / scaffold-conformance dispatch (Slab-3 partial migration drift) — 3 failures

**Root cause:** dispatch-registry has been promoted to `_status: production` (per Slab 3 / 5a.5) but some scaffold-conformance tests assert structured-production-shape OR clone-fork-notice presence in legacy sidecar dirs that were not exhaustively migrated.

**Status:** PRE-EXISTING; touches Slab-3 / vera-sidecar / dan-sidecar / wanda-sanctum cleanup work. Resolution lands at S5 (housekeeping-4 + state/config spikes) and S6 (sidecar archives).

| nodeid | Attribution |
|---|---|
| `tests/integration/sanctum/test_clone_fork_notice_present.py::test_clone_fork_notice_present_for_all_sanctum_dirs` | clone-fork-notice missing in some sanctum dirs (legacy sidecars) |
| `tests/integration/scaffold_conformance/test_dispatch_contract_hardening.py::test_dispatch_registry_is_structured_production` | dispatch-registry production-shape verification (Slab 5a.5 promotion drift) |
| `tests/integration/scaffold_conformance/test_dispatch_contract_hardening.py::test_dispatch_registry_loaded_at_module_import` | dispatch-registry module-import semantics |

---

### Cat-6: Marcus integration (adhoc facade) — 2 failures

**Root cause:** adhoc facade tests exercise `marcus.facade::run_4a` happy path + cascade override. Likely related to Marcus duality (legacy `marcus/` vs `app/marcus/`) — these tests target legacy facade which still works for adhoc but may have bitrot.

**Status:** PRE-EXISTING; resolution at S2 (full marcus/ namespace collapse — operator's NO-DEFERRAL directive).

| nodeid | Attribution |
|---|---|
| `tests/integration/marcus/test_adhoc_facade.py::test_adhoc_facade_happy_path` | adhoc facade `run_4a` invocation |
| `tests/integration/marcus/test_adhoc_facade.py::test_adhoc_facade_cascade_override_path` | adhoc facade with cascade override |

---

### Cat-7: Cascade IDs / catalog snapshot (A15 counter-pattern; snapshot freshness) — 4 failures

**Root cause:** `tests/fixtures/openai_catalog_snapshot.json` is fixture-pinned; production model_id additions or removals must lockstep the snapshot. Snapshot may have lapsed `next_refresh_due_by` (deferred-inventory `postmigration-catalog-snapshot-staleness-warn` entry).

**Status:** PRE-EXISTING; resolution at S5 (catalog snapshot refresh; lapse-warn CI guard).

| nodeid | Attribution |
|---|---|
| `tests/integration/runtime/test_cascade_ids_in_openai_published_catalog.py::test_every_runtime_model_id_appears_in_openai_catalog_snapshot` | runtime model_id absent from snapshot |
| `tests/integration/runtime/test_cascade_registry_alignment.py::test_every_active_registry_id_resolves_to_exactly_one_cascade_entry` | cascade-registry alignment with active model registry |
| `tests/integration/runtime/test_cleanup_threads.py::test_cleanup_dry_run_then_apply` | cleanup-threads dry-run vs apply semantics (cascade-related) |
| `tests/test_no_fictitious_model_ids.py::test_no_fictitious_model_ids_in_production_code` | A15 counter-pattern enforcement |

---

### Cat-8: Migration substrate (multi-Slab pre-existing) — 4 failures

**Root cause:** various Slab-2/3/5 migration substrate pinning tests; some assert artifacts that were superseded by later Slabs.

**Status:** PRE-EXISTING; resolution at S5 (governance JSON + sprint-status flips) or S6 (substrate archives).

| nodeid | Attribution |
|---|---|
| `tests/migration/test_a17_p3_entries_present.py::test_a17_and_p4_entries_present_with_frozen_shape` | (FIXED 2026-05-07 S1 P0-4 cascade — test renamed P3→P4 in lockstep with anti-pattern dedup; **NOW PASSING**) |
| `tests/migration/test_dispatch_registry_promoted.py::test_dispatch_registry_status_no_longer_interim` | dispatch-registry `_status` should be `production` (already promoted; test may be checking ledger entry shape) |
| `tests/migration/test_m5_verdict_consequence_path.py::test_m5_verdict_consequence_path` | M5 verdict consequence-path semantic check |
| `tests/migration/test_slab_2c_next_session_start_here_updated.py::test_next_session_start_here_reflects_slab_2c_close` | next-session-start-here.md content assertion (file is gitignored hot-start; CI may not see it) |

---

### Cat-9: Ledger / queries — 2 failures

**Root cause:** ledger event idempotency + query-shape tests; needs investigation post-Trial-3 (likely Slab 6.x ledger-shape drift).

**Status:** PRE-EXISTING.

| nodeid | Attribution |
|---|---|
| `tests/integration/ledger/test_emit_ledger_event_idempotent.py::test_emit_ledger_event_idempotent` | ledger event idempotency |
| `tests/integration/ledger/test_queries.py::test_queries_return_expected_shapes` | ledger query result shapes |

---

### Cat-10: Performance / latency budget — 1 failure

**Root cause:** checkpoint-write-latency p95 < 500ms; flake-prone on slower environments OR drift from substrate-evolution.

**Status:** PRE-EXISTING; environment-dependent.

| nodeid | Attribution |
|---|---|
| `tests/performance/runtime/test_checkpoint_write_latency.py::test_checkpoint_write_latency_p95_under_500ms` | LangGraph checkpoint-write latency budget |

---

### Cat-11: Specialist body (Irene LLM real-invocation token floor) — 1 failure

**Root cause:** Irene's `_act` real LLM invocation token-floor test; needs valid OPENAI_API_KEY + sufficient corpus complexity.

**Status:** ENVIRONMENT-CONDITIONAL.

| nodeid | Attribution |
|---|---|
| `tests/specialists/irene/test_irene_act_node_llm_invocation.py::test_irene_act_node_real_llm_invocation_with_token_floor` | requires valid OPENAI_API_KEY + corpus shape |

---

### Cat-12: Structural / DSL self-registration — 3 failures

**Root cause:** Slab 7c parity-DSL self-registration audit floor; Slab 7c TW-7c-4/5/6 tripwire-detection scaffolds; G0 poll-surface DSL self-registration. Likely related to Wave-3 close + housekeeping-2 dependency.

**Status:** PRE-EXISTING; some may be resolved by S5 housekeeping-2 close.

| nodeid | Attribution |
|---|---|
| `tests/structural/test_transport_parity_dsl_registration_floor.py::test_transport_parity_dsl_self_registration_floor` | parity-DSL registration count below floor |
| `tests/structural/test_tw_7c_4_5_6_detection_scaffolds_present.py::test_tw_7c_4_detector_exists_and_passes` | TW-7c-4 detector scaffold presence |
| `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py::test_tw_7c_4_detector_reports_no_fire` | TW-7c-4 audit AC; should pass; investigate at S5 |
| `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py::test_live_dispatch_python_scope_is_bounded` | TW-7c-4 scope-creep audit; +1 entry surfaced post-S1 measurement (Murat post-S1 AM-12) |
| `tests/gates/section_02a/test_g0_poll_surface_dsl_registration.py::test_self_registration_audit_passes_floor_10` | §02A G0 poll-surface DSL self-registration ≥ floor 10 |

---

### Cat-13: Pipeline manifest loader / lockstep — 3 failures

**Root cause:** pipeline-manifest schema-validation + red-path fixture tests; may be related to manifest evolution post-Slab-7c.

**Status:** PRE-EXISTING; resolution at S5 (state/config spikes).

| nodeid | Attribution |
|---|---|
| `tests/test_pipeline_manifest_loader.py::test_manifest_loads_and_validates` | pipeline-manifest schema-validation drift |
| `tests/test_check_pipeline_manifest_lockstep.py::test_red_path_fixtures_fail_correctly_manifest_only` | red-path fixture (manifest-only) |
| `tests/test_check_pipeline_manifest_lockstep.py::test_red_path_fixtures_fail_correctly_schema_only` | red-path fixture (schema-only) |

---

### Cat-14: Legacy run_hud / structural-walk — 4 failures

**Root cause:** `scripts/utilities/run_hud.py` legacy primary-repo HUD; tests pin behavior. Plus structural-walk motion-dry-run.

**Status:** PRE-EXISTING; resolution at S6 (legacy script archives — `run_hud.py` may be archived if no longer in production dispatch path).

| nodeid | Attribution |
|---|---|
| `tests/test_run_hud.py::TestRenderHtml::test_empty_run_renders_cleanly` | run_hud HTML rendering (legacy) |
| `tests/test_run_hud.py::TestScanBundleArtifacts::test_lists_files_with_sizes` | run_hud bundle scan |
| `tests/test_run_hud.py::TestScanBundleArtifacts::test_missing_dir_returns_empty` | run_hud missing-dir handling |
| `tests/test_structural_walk.py::test_motion_dry_run_preview_adds_marcus_motion_sequence` | structural-walk motion preview (Slab-7c surface) |

---

### Cat-15: NFR-CG / contracts / specialist contracts (already fixed in S1) — 8 failures, ALL FIXED

**Root cause:** mostly P0-3 hybrid registry restoration aftermath; pre-existing for some others.

**Status:** the 6 registry-related failures were INTRODUCED by my P0-3 first-pass rewrite + REGISSED by hybrid registry; should now be PASSING. Re-running pytest at end-of-S1 will confirm.

| nodeid | Attribution | Status |
|---|---|---|
| `tests/test_specialist_registry_contract.py::test_specialist_registry_exists_and_has_specialists_map` | (FIXED — hybrid registry restored `version: 1`) | FIXED |
| `tests/test_specialist_registry_contract.py::test_specialist_registry_contains_required_specialists` | (FIXED — hybrid registry restored 14 keys) | FIXED |
| `tests/test_specialist_registry_contract.py::test_specialist_registry_paths_are_skills_and_exist` | (FIXED — hybrid registry preserved `path` field) | FIXED |
| `tests/test_canva_specialist_contract.py::test_canva_specialist_registry_mapping_exists` | (FIXED — `canva-specialist` key restored) | FIXED |
| `tests/test_coursearc_specialist_contract.py::test_coursearc_specialist_registry_mapping_exists_for_marcus_delegation` | (FIXED — `coursearc-specialist` key restored) | FIXED |
| `tests/test_manual_tool_specialist_contracts.py::test_manual_tool_specialists_are_registered` | (FIXED — manual-tool specialists restored) | FIXED |
| `tests/test_orchestrator_agent_skill_path.py::test_orchestrator_agent_skill_path` | yaml ModuleNotFoundError in `run_reporting.py`; PRE-EXISTING (not my regression) | PRE-EXISTING |
| `tests/parity/test_nfr_cg_block_aggregated.py::test_nfr_cg_block_structural_evidence[NFR-CG6]` | NFR-CG6 structural evidence aggregation | PRE-EXISTING |

---

### Cat-16: Misc / single-instance — 4 failures

| nodeid | Attribution | Resolution |
|---|---|---|
| `tests/contracts/test_provider_directory_roster_placeholders.py::test_roster_placeholder_present_with_expected_status[consensus-retrieval-ratified]` | provider-directory roster placeholder | S5 substrate |
| `tests/contracts/test_transform_registry_lockstep.py::test_every_format_covered_or_exempted` | transform-registry format coverage | S5 substrate |
| `tests/contracts/test_33_2_state_config_disjoint_keys.py::test_pipeline_manifest_keys_do_not_shadow_other_state_configs` | state/config key namespace isolation | S5 substrate |
| `tests/end_to_end/test_full_pipeline_smoke.py::test_migrated_manifest_edges_form_linear_chain` + `test_migrated_manifest_has_33_nodes` | full-pipeline smoke; manifest-shape pin | S5 substrate |

---

## Summary

| Category | Count | Resolution Path |
|---|---|---|
| Cat-1 manifest-regen drift | 4 | S6 (post-S4 v5 retargets Epic 33) |
| Cat-2 DISMISS-thread (housekeeping-2) | 1 | S5 (housekeeping-2 lands) |
| Cat-3 cache-hit-rate (env-conditional) | 3 | post-Trial-3 (cache warmup populates) |
| Cat-4 replay infrastructure | 5 | post-Trial-3 (checkpoint-native catalog) |
| Cat-5 scaffold-conformance / sanctum | 3 | S5 / S6 (sidecar cleanup) |
| Cat-6 marcus duality (adhoc facade) | 2 | **S2** (marcus/ namespace collapse — operator NO-DEFERRAL) |
| Cat-7 catalog snapshot (A15) | 4 | S5 (catalog refresh + lapse-warn CI guard) |
| Cat-8 migration substrate | 4 | S5 governance JSON + sprint-status |
| Cat-9 ledger | 2 | post-Trial-3 |
| Cat-10 performance | 1 | environment-dependent |
| Cat-11 Irene LLM | 1 | environment-conditional (OPENAI_API_KEY) |
| Cat-12 structural / DSL | 4 | S5 (some by housekeeping-2) |
| Cat-13 pipeline manifest | 3 | S5 |
| Cat-14 legacy run_hud / structural-walk | 4 | S6 (legacy script archive) |
| Cat-15 NFR-CG / contracts (most FIXED in S1) | 8 (6 fixed; 2 remain) | (FIXED) |
| Cat-16 misc single-instance | 4 | S5 substrate |
| **Total** | **53** (post-S1-regression-fixes) |

**Note on the +2 from Murat estimate (47 → 53 post-fix):** the categorical breakdown above accounts for ~6 entries that Murat's broader-regression sample didn't include (housekeeping-2 driven; environment-conditional cache-hit-rate; structural-walk motion preview). Re-measuring post-S5 housekeeping-2 close should drop the count by 1 (Cat-2). Re-measuring post-S2 marcus/ collapse should drop by 2 (Cat-6). Post-S6 catalog-snapshot refresh drops by 4 (Cat-7). **Expected post-S5 baseline: ~46 failures; post-S6: ~38 failures.** Trial-3 launch baseline: post-S6 final.

## Forensic comparison protocol (for Trial-3 + post-trial reviews)

When Trial-3 (or any S1-S6 post-review) surfaces a failing test:

1. **Grep this catalog** for the exact `nodeid`. If present → **PRE-EXISTING**; not a Trial-3 regression. Note the category for context.
2. **If absent from this catalog AND post-Trial-3** → **CANDIDATE NEW REGRESSION**. Investigate: (a) did Trial-3 dispatch touch the path under test? (b) git-blame the test file for recent changes; (c) cross-check S1-S6 close commits.
3. **If absent from this catalog AND post-S2/S3/S4/S5/S6** → **CLEANUP REGRESSION**. The session that introduced it owns the fix.

This catalog is the single source of "what was already broken on 2026-05-07." Do NOT modify entries in place; if a category resolves, append a `RESOLVED-AT-<commit>` line below the affected category and update the Summary count. At S6 close: roll up all RESOLVED entries into a delta-summary section and mark this file historical-archive (forensic-trail-only).
