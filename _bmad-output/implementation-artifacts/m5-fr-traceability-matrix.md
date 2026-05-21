# M5 FR Traceability Matrix

Generated: 2026-04-27

Scope: Batch 2 B-trace read-and-report pass over the M5-relevant functional requirements named in the pre-trial defensibility dispatch. This matrix extends the 15-invariant audit matrix by mapping each load-bearing FR to acceptance criteria, tests, and implementation evidence in the post-Batch-1 state.

## Summary

| Metric | Count |
|---|---:|
| FR rows reviewed | 17 |
| TRACED | 15 |
| PARTIAL | 2 |
| GAP | 0 |

No FR `GAP` was found. Two FRs are `PARTIAL` because the accepted M5 record already carries conditional or deferred live-execution work: FR51 checkpoint-native replay discovery and FR52 production clone-launch execution equivalence. Deferred-inventory entries were filed as `m5-fr-trace-partial-FR51` and `m5-fr-trace-partial-FR52`.

## Matrix

| FR | Description | Slab/Story | ACs | Tests | Implementation files | Status |
|---|---|---|---|---|---|---|
| FR51 | Trial replay byte-for-byte reproducibility | 5a.1 | AC-5a.1-A, AC-5a.1-B, AC-5a.1-C, AC-5a.1-D | `tests/integration/replay/test_replay_all_closed_trials.py`; `tests/integration/replay/test_replay_budget.py`; `tests/integration/replay/test_sanctum_variance_policy.py`; `tests/trial_replay/test_replay_all.py`; `tests/trial_replay/test_gha_workflow_present.py` | `app/replay/discovery.py`; `app/replay/regression.py`; `.github/workflows/trial-replay.yml`; `_bmad-output/implementation-artifacts/migration-5a-1-trial-replay-regression-suite.md` | PARTIAL |
| FR52 | Head-to-head parity | 5a.2 | AC-5a.2-A, AC-5a.2-B, AC-5a.2-C, AC-5a.2-D | `tests/integration/replay/test_parity_comparison.py`; `tests/migration/test_5a_2_parity_evidence_present.py`; `tests/migration/test_5a_2_party_mode_5_agent_recording.py` | `app/replay/parity_comparison.py`; `_bmad-output/implementation-artifacts/migration-5a-2-head-to-head-parity-trial.md`; `_bmad-output/implementation-artifacts/parity-window-verdict-2026-04-26.md` | PARTIAL |
| FR54 | Cache hit-rate and prefix stability substitute metric | 5a.3 | AC-5a.3-A, AC-5a.3-B, AC-5a.3-C | `tests/end_to_end/test_cache_hit_rate_baseline.py`; `tests/unit/models/test_cache_prefix_stability.py`; `tests/unit/runtime/test_compute_cache_impact.py` | `app/models/adapter.py`; `app/models/selector.py`; `app/models/state/cache_state.py`; `app/specialists/*/graph.py`; `_bmad-output/implementation-artifacts/migration-5a-3-economics-cost-reduction-bar.md` | TRACED |
| FR55 | Cost-engineering foundation: per-trial cost measurement and persisted report | 5a.3 | AC-5a.3-D, AC-5a.3-E, AC-5a.3-F | `tests/integration/runtime/test_measure_trial_cost.py`; `tests/integration/runtime/test_record_trial_cost_report.py`; `tests/unit/runtime/test_trial_economics_report_strict.py`; `tests/unit/runtime/test_check_trial_budget.py` | `app/runtime/economics.py`; `app/models/runtime/trial_economics_report.py`; `runtime/config/openai_pricing.yaml`; `scripts/utilities/migration_health_dashboard.py` | TRACED |
| FR56 | Cost-engineering foundation: cascade and pricing coverage | 5a.3 | AC-5a.3-G, AC-5a.3-H, AC-5a.3-I | `tests/integration/runtime/test_cascade_config_loading.py`; `tests/integration/runtime/test_pricing_table_covers_cascade.py`; `tests/integration/runtime/test_migration_health_dashboard_cost_rows.py` | `app/runtime/cascade_config.py`; `runtime/config/model_cascade.yaml`; `runtime/config/openai_pricing.yaml`; `scripts/setup/validate_cascade_config.py` | TRACED |
| FR60 | Backport channel closed | 5a.5 | AC-5a.5-A, AC-5a.5-B | `tests/migration/test_m5_verdict_consequence_path.py` | `_bmad-output/upstream-state.md`; `docs/dev-guide/langgraph-migration-guide.md`; `docs/operator/post-m5-runbook.md`; `_bmad-output/implementation-artifacts/m5-decision.md` | TRACED |
| FR61 | Forward-port playbook | 5a.5 | AC-5a.5-C, AC-5a.5-D | `tests/migration/test_m5_verdict_consequence_path.py` | `docs/dev-guide/m5-forward-port-readiness-checklist.md`; `docs/operator/post-m5-runbook.md`; `_bmad-output/upstream-state.md`; `_bmad-output/implementation-artifacts/m5-decision.md` | TRACED |
| FR62 | Rollback plan | 5a.5 | AC-5a.5-E, AC-5a.5-F | `tests/migration/test_m5_verdict_consequence_path.py` | `docs/operator/post-m5-runbook.md`; `docs/workflow/production-change-window.md`; `_bmad-output/upstream-state.md`; `_bmad-output/implementation-artifacts/m5-decision.md` | TRACED |
| FR63 | Invariant preservation evidence | 5a.4 | AC-5a.4-A, AC-5a.4-B, AC-5a.4-C | `tests/migration/test_15_invariant_audit_matrix_present.py`; `tests/migration/test_15_invariant_stub_absorption.py`; `tests/unit/models/state/test_reproducibility_invariants.py` | `_bmad-output/implementation-artifacts/15-invariant-audit-matrix.md`; `_bmad-output/implementation-artifacts/migration-5a-4-15-invariant-audit-matrix-and-fr64-catalog-final.md`; `app/models/state/run_state.py` | TRACED |
| FR64 | Anti-pattern catalog | 5a.4 | AC-5a.4-D, AC-5a.4-E | `tests/migration/test_anti_patterns_catalog_fr64_final.py`; `tests/migration/test_slab_4_anti_patterns_cycle_complete.py` | `docs/dev-guide/specialist-anti-patterns.md`; `_bmad-output/implementation-artifacts/migration-5a-4-15-invariant-audit-matrix-and-fr64-catalog-final.md` | TRACED |
| FR2 | FastAPI and MCP transport parity | Slab 1, Slab 3 | AC-1-1d-A, AC-1-1d-B, AC-1-1d-C | `tests/integration/transport_parity/test_fastapi_mcp_parity.py`; `tests/integration/transport_parity/test_mcp_subprocess_hygiene.py`; `tests/integration/transports/test_mcp_stdio_smoke.py`; `tests/integration/runtime/test_fastapi_server.py` | `app/runtime/server.py`; `app/http/gate_endpoint.py`; `app/mcp_server/server.py`; `app/mcp_server/tools/ping.py`; `app/runtime/minimal_node.py` | TRACED |
| FR30 | Sanctum cold-read fingerprinting | Slab 4 | AC-4.6-A, AC-4.6-B | `tests/unit/marcus/test_marcus_cold_read.py`; `tests/unit/models/state/test_sanctum_fingerprint.py`; `tests/unit/models/state/test_reproducibility_invariants.py` | `app/marcus/facade.py`; `app/models/state/run_state.py`; `app/models/state/sanctum_fingerprint.py` | TRACED |
| FR34 | HIL gate authority through operator verdict and resume API | Slab 3, Slab 4 | AC-3-GATE-A, AC-3-GATE-B, AC-3-GATE-C | `tests/integration/gates/test_resume_api_authority.py`; `tests/integration/gates/test_resume_from_verdict_digest_match.py`; `tests/integration/transports/test_gate_transport_parity.py`; `tests/integration/ledger/test_verdict_transport_emission.py` | `app/gates/resume_api.py`; `app/models/state/operator_verdict.py`; `app/http/gate_endpoint.py`; `app/mcp_server/tools/gate_decide.py`; `app/marcus/cli/gate_cli.py` | TRACED |
| FR40 | Marcus and Cora lane separation | Slab 4 | AC-4-LANE-A, AC-4-LANE-B | `tests/integration/cora/test_cora_marcus_import_linter_bidirectional.py`; `tests/integration/marcus/test_marcus_import_linter_contract.py`; import-linter contract in `pyproject.toml` | `app/marcus/`; `app/cora/`; `pyproject.toml` | TRACED |
| FR42 | LangSmith trace export | Slab 4, 5a.3 | AC-4-OBS-A, AC-5a.3-D | `tests/unit/observability/test_span_tag_contract_pin.py`; `tests/integration/observability/test_langsmith_span_tags.py`; `tests/integration/runtime/test_measure_trial_cost.py` | `app/runtime/span_tags.py`; `app/models/adapter.py`; `app/runtime/economics.py`; `app/gates/party_mode_as_interrupt.py` | TRACED |
| FR43 | Frozen-graph compiled-digest stability | Slab 4 | AC-4-FROZEN-A, AC-4-FROZEN-B | `tests/migration/test_compiled_graph_digest_stable.py`; `tests/migration/test_v42_artifacts_present.py`; `tests/migration/test_frozen_graph_ceremony_doc_present.py` | `runtime/graphs/v42/`; `app/runtime/compiled_graph_digest.py`; `docs/operator/frozen-graph-ceremony.md` | TRACED |
| FR59 | Sanctum watcher | Slab 4.6 | AC-4.6-C, AC-4.6-D | `tests/integration/runtime/test_sanctum_watcher_detects_mutation.py`; `tests/integration/runtime/test_sanctum_mutation_non_fatal.py`; `tests/integration/runtime/test_mutation_timing_semantics.py`; `tests/unit/runtime/test_sanctum_warning_strict.py` | `app/runtime/sanctum_watcher.py`; `app/runtime/sanctum_warning.py`; `app/ledger/events.py` | TRACED |

## Partial Dispositions

| FR | Reason | Deferred entry | Reactivation gate |
|---|---|---|---|
| `FR51` | The accepted 5a.1 replay surface proves deterministic replay on the migration-native Marcus baseline fixture, but checkpoint-native closed-trial catalog discovery remains deferred. | `m5-fr-trace-partial-FR51` | Test surface added that exercises FR51 end-to-end against actual LangGraph checkpoint storage. |
| `FR52` | The accepted 5a.2 evidence proves control-plane artifact parity, but a real production clone-launch execution path remains unproven. | `m5-fr-trace-partial-FR52` | Test surface added that exercises FR52 end-to-end through a real production clone trial with LangSmith trace evidence. |
