# M5 NFR Assessment

Generated: 2026-04-27

Scope: Batch 2 B-nfr read-and-report pass over the M5 NFR set named in the pre-trial defensibility dispatch. Assessment values are `MET` or `NOT MET`; confidence values are `HIGH`, `MEDIUM`, `LOW`, or `UNVERIFIABLE-IN-DEV`.

## Summary

| Metric | Count |
|---|---:|
| NFR blocks reviewed | 11 |
| MET | 11 |
| NOT MET | 0 |
| LOW confidence | 0 |
| UNVERIFIABLE-IN-DEV confidence | 0 |

No `NOT MET` NFR was found. FR51 and FR52 remain conditional/deferred at the functional traceability layer, but the NFR contracts reviewed here are implemented and covered by tests at the accepted M5 scope.

### NFR-X1 - Replay Determinism

**Source:** Slab 5a Story 5a.1; `_bmad-output/implementation-artifacts/migration-5a-1-trial-replay-regression-suite.md`.

**Implementation:** `app/replay/regression.py` compares replay output hashes against baselines and emits deterministic replay records.

**Test coverage:** `tests/integration/replay/test_replay_all_closed_trials.py`, `tests/trial_replay/test_replay_all.py`, and `tests/integration/replay/test_sanctum_variance_policy.py`.

**Assessment:** MET.

**Confidence:** MEDIUM.

**Risk:** The accepted M5 scope uses the migration-native Marcus baseline fixture. Checkpoint-native closed-trial catalog discovery remains deferred through `m5-fr-trace-partial-FR51`.

### NFR-X3 - Sanctum-Fingerprint Variance-Band Tolerance

**Source:** Slab 5a Story 5a.1 and D1 sanctum variance policy.

**Implementation:** `app/replay/regression.py` accepts sanctum variance within the declared tolerance while preserving hash comparison for non-variance fields.

**Test coverage:** `tests/integration/replay/test_sanctum_variance_policy.py` covers within-band acceptance and out-of-band rejection.

**Assessment:** MET.

**Confidence:** HIGH.

**Risk:** None surfaced.

### NFR-X4 - Per-Trial Wall-Clock Budget <= 15 Minutes

**Source:** Slab 5a Story 5a.1.

**Implementation:** `app/replay/regression.py` measures replay duration and raises the budget violation path when elapsed time exceeds the configured ceiling.

**Test coverage:** `tests/integration/replay/test_replay_budget.py` covers under-budget success and over-budget failure.

**Assessment:** MET.

**Confidence:** HIGH.

**Risk:** None surfaced.

### NFR-X5 - Replay Completeness For Closed Trials

**Source:** Slab 5a Story 5a.1.

**Implementation:** `app/replay/discovery.py` and `app/replay/regression.py` discover replayable closed trials and execute the replay sweep used by the GHA workflow.

**Test coverage:** `tests/integration/replay/test_replay_all_closed_trials.py`, `tests/trial_replay/test_replay_all.py`, and `tests/trial_replay/test_gha_workflow_present.py`.

**Assessment:** MET.

**Confidence:** MEDIUM.

**Risk:** Completeness holds for the currently discoverable replay catalog. Actual LangGraph checkpoint catalog discovery remains a deferred confidence-raising follow-on through `m5-fr-trace-partial-FR51`.

### Cost NFR - Per-Trial Cost Reports Persisted

**Source:** Slab 5a Story 5a.3 amended cost-engineering foundation.

**Implementation:** `app/runtime/economics.py` records strict `TrialEconomicsReport` payloads and writes persisted report artifacts.

**Test coverage:** `tests/integration/runtime/test_record_trial_cost_report.py`, `tests/unit/runtime/test_trial_economics_report_strict.py`, and `tests/integration/runtime/test_measure_trial_cost.py`.

**Assessment:** MET.

**Confidence:** HIGH.

**Risk:** None surfaced.

### Cost NFR - Per-Agent Attribution Computed

**Source:** Slab 5a Story 5a.3 amended cost-engineering foundation.

**Implementation:** `app/runtime/economics.py` aggregates token usage and cost attribution per agent and exposes drift computations.

**Test coverage:** `tests/integration/runtime/test_measure_trial_cost.py` and `tests/unit/runtime/test_compute_per_agent_drift.py`.

**Assessment:** MET.

**Confidence:** HIGH.

**Risk:** None surfaced.

### Cost NFR - Cascade Digest Stable

**Source:** Slab 5a Story 5a.3 amended cost-engineering foundation.

**Implementation:** `app/runtime/cascade_config.py` loads `runtime/config/model_cascade.yaml` and computes a stable cascade digest for cost-report provenance.

**Test coverage:** `tests/integration/runtime/test_cascade_config_loading.py` covers loading, validation failure, and stable digest behavior.

**Assessment:** MET.

**Confidence:** HIGH.

**Risk:** None surfaced.

### Cost NFR - Pricing Digest Stable

**Source:** Slab 5a Story 5a.3 amended cost-engineering foundation.

**Implementation:** `app/runtime/cascade_config.py` loads `runtime/config/openai_pricing.yaml`; `app/runtime/economics.py` carries pricing provenance into generated cost reports.

**Test coverage:** `tests/integration/runtime/test_pricing_table_covers_cascade.py`, `tests/integration/runtime/test_measure_trial_cost.py`, and `tests/integration/runtime/test_record_trial_cost_report.py`.

**Assessment:** MET.

**Confidence:** MEDIUM.

**Risk:** Pricing coverage is directly tested and report provenance is integration-tested, but there is no single-purpose repeated-pricing-digest stability test. No current evidence indicates instability.

### Sanctum NFR - Cold-Read Fingerprint Determinism

**Source:** Slab 4 and Slab 5a invariant preservation evidence.

**Implementation:** `app/models/state/sanctum_fingerprint.py`, `app/models/state/run_state.py`, and `app/marcus/facade.py` compute and preserve cold-read fingerprint state.

**Test coverage:** `tests/unit/marcus/test_marcus_cold_read.py`, `tests/unit/models/state/test_sanctum_fingerprint.py`, and `tests/unit/models/state/test_reproducibility_invariants.py`.

**Assessment:** MET.

**Confidence:** HIGH.

**Risk:** None surfaced.

### Sanctum NFR - Watcher Debounce And Non-Fatal Mutation Warning

**Source:** Slab 4.6 sanctum watcher requirements.

**Implementation:** `app/runtime/sanctum_watcher.py`, `app/runtime/sanctum_warning.py`, and `app/ledger/events.py` detect mutation and preserve non-fatal warning semantics.

**Test coverage:** `tests/integration/runtime/test_sanctum_watcher_detects_mutation.py`, `tests/integration/runtime/test_sanctum_mutation_non_fatal.py`, `tests/integration/runtime/test_mutation_timing_semantics.py`, and `tests/unit/runtime/test_sanctum_warning_strict.py`.

**Assessment:** MET.

**Confidence:** MEDIUM.

**Risk:** The implementation has polling fallback behavior for environments without watchdog support. Tests cover detection and non-fatal semantics; they do not prove every host-specific filesystem event ordering.

### Transport NFR - FastAPI And MCP Byte-Equivalent Parity

**Source:** Story 1-1d and transport parity evidence.

**Implementation:** `app/runtime/server.py`, `app/http/gate_endpoint.py`, `app/mcp_server/server.py`, and `app/mcp_server/tools/ping.py` expose the same minimal runtime and gate semantics across HTTP and MCP transports.

**Test coverage:** `tests/integration/transport_parity/test_fastapi_mcp_parity.py`, `tests/integration/transport_parity/test_mcp_subprocess_hygiene.py`, `tests/integration/transports/test_mcp_stdio_smoke.py`, and `tests/integration/runtime/test_fastapi_server.py`.

**Assessment:** MET.

**Confidence:** HIGH.

**Risk:** None surfaced.
