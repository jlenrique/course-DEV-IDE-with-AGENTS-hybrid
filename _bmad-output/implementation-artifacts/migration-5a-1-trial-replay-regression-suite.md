# Migration Story 5a.1: Trial-Replay Regression Suite + CI Fail-Loud Mode

**Status:** ready-for-dev
**Sprint key:** `migration-5a-1-trial-replay-regression-suite`
**Epic:** Slab 5a — Acceptance (M5 go/no-go gate "Migration ships") — **OPENING story**.
**Pts:** 5 | **Gate:** dual (per governance JSON `5a-1.expected_gate_mode = "dual-gate"`, rationale: `operator_acceptance_gate`). **K-target:** ~1.5× (target 18 / floor 12).

**Predecessor:** Slab 4 done (4.4 ledger + 4.5 frozen-graph + 4.6 sanctum hook all stable). Drafted-for-queue.

---

## T1 Readiness Block

1. Governance: `5a-1.expected_gate_mode = "dual-gate"` (operator_acceptance_gate).
2. **Substrate:** `app/replay/` does NOT exist (verify); `tests/trial_replay/` does NOT exist (verify).
3. **Closed trial inventory** — Slab 2/3/4 trial runs at known checkpoint storage location (verify per Slab-1 substrate; likely `state/trials/` or LangGraph checkpointer Postgres rows).
4. **Pack-hash + sanctum-hash baselines** — frozen-graph compiled-graph-digest from 4.5; sanctum fingerprint from Slab-2c + 3.6 baseline.
5. **D1 sanctum-fingerprint variance policy** — architecture decision-of-record D1 (cold-read fingerprint + variance bands).
6. **NFR-X1/X3/X4/X5** — replay determinism + variance-band tolerance + wall-clock budgets.
7. **CI fail-loud vs warn-on-clone modes** — operator-controlled flag.
8. Severance posture.

### TEMPLATE scope decisions

**Decision #1 — Bounded scope:** (a) `app/replay/regression.py::replay_all_closed_trials()` + per-trial `replay_trial(trial_id, mode: Literal["fail-loud", "warn-on-clone"])`; (b) `tests/trial_replay/` populated with 100% coverage of closed tracked trial runs from Slab 2/3/4; (c) pack-hash drift detection + ReplayError raise; (d) sanctum-hash mismatch handling per D1 (fail-loud raises; warn-on-clone continues with snapshot fallback + provenance log); (e) GHA workflow at `.github/workflows/trial-replay.yml`; (f) per-trial wall-clock ≤15min per NFR. NOT in scope: head-to-head parity (5a.2); economics (5a.3); invariant audit (5a.4); M5 ship verdict (5a.5).

**Decision #2 — Closed-trial discovery mechanism:** `app/replay/discovery.py::list_closed_trials() -> list[TrialRef]` walks the LangGraph checkpointer storage (Postgres tables OR `state/trials/` filesystem per Slab-1 substrate; verify at T1) for trials with terminal-state checkpoint. Filter per `closed_at` field presence.

**Decision #3 — ReplayError discriminated by drift-kind:** typed errors: `PackHashDriftError`, `SanctumFingerprintDriftError`, `ManifestSnapshotDriftError`. Single `ReplayError` base class. Caller switches behavior based on (mode, drift-kind) tuple.

**Decision #4 — Per-trial wall-clock budget enforcement:** `replay_trial` wraps in `time.perf_counter()` start/stop; raises `ReplayBudgetExceeded` if elapsed > 15min per NFR-X4. Test asserts 15min budget against 3-fixture trial set (avg ≤5min/trial).

---

## Story

As a **governance system enforcing byte-for-byte reproducibility per FR51 + NFR-X1/X3/X4/X5**,
I want **`app/replay/regression.py` + `tests/trial_replay/` with 100% closed-trial coverage + CI fail-loud on pack-hash drift + D1 sanctum-fingerprint variance policy + per-trial ≤15min wall-clock budget + GHA workflow**,
So that **FR51 + NFR-X1/X3/X4/X5 are met and M5 ship verdict has byte-for-byte regression evidence**.

---

## Acceptance Criteria

### AC-5a.1-A — `app/replay/regression.py::replay_all_closed_trials()` impl

- **Given** closed trials exist (verify via `list_closed_trials()` per Decision #2 at T1)
- **When** dev authors `replay_all_closed_trials(mode: Literal["fail-loud", "warn-on-clone"]) -> ReplayBatchResult`
- **Then** every closed trial replays from final checkpoint; pack-hash compared; ReplayError discriminated per Decision #3 raised on drift in fail-loud mode.
- **Test pin:** `tests/integration/replay/test_replay_all_closed_trials.py` — 2 tests: clean batch → exit 0 + result.passed_count > 0; synthetic drift → ReplayError with discriminated kind.

### AC-5a.1-B — Sanctum-fingerprint variance policy per D1 (DUAL-GATE acceptance gate-1)

- **Given** mode="fail-loud" → drift raises; mode="warn-on-clone" → snapshot fallback + provenance log per D1
- **When** synthetic sanctum-hash mismatch fixture runs in each mode
- **Then** behavior matches D1 contract.
- **Test pin:** `tests/integration/replay/test_sanctum_variance_policy.py` — 2 tests (one per mode).

### AC-5a.1-C — `tests/trial_replay/` 100% coverage of closed trials

- **Given** closed trials enumerated at T1
- **When** dev authors per-trial replay test (parametrized over discovered trials)
- **Then** test collection includes all closed trials; pytest run replays each + verifies pack-hash + sanctum-fingerprint per D1.
- **Test pin:** `tests/trial_replay/test_replay_all.py` — N parametrize-collapsible tests (N = closed-trial count) → 1 K-floor unit per Murat M-R18.

### AC-5a.1-D — Per-trial wall-clock budget per NFR-X4

- **Given** Decision #4 wraps in `time.perf_counter()`
- **When** synthetic 3-fixture trial set runs
- **Then** each trial completes ≤15min; ReplayBudgetExceeded raised on overrun.
- **Test pin:** `tests/integration/replay/test_replay_budget.py` — 2 tests: under-budget passes; over-budget raises.

### AC-5a.1-E — GHA workflow at `.github/workflows/trial-replay.yml`

- **Given** workflow does not exist
- **When** dev authors with cron trigger (nightly) + manual `workflow_dispatch` (ad-hoc); invokes `replay_all_closed_trials(mode="fail-loud")` in CI
- **Then** workflow file exists + parses + has fail-loud invocation regex.
- **Test pin:** `tests/integration/replay/test_gha_workflow_present.py` — 1 test.

### AC-5a.1-F — Anti-pattern catalog harvest

NO new entries expected.

### AC-5a.1-G — TEMPLATE compliance

R1, R6, R8 honored.

### AC-5a.1-H — D12 close protocol (DUAL-gate; operator_acceptance_gate; FIVE-line)

1. Invariant preservation: FR51 + NFR-X1/X3/X4/X5; D1 sanctum variance policy.
2. Anti-pattern harvest: N/A.
3. Migration-guide update: §"Trial Replay" added.
4. TEMPLATE compliance: R1, R6, R8.
5. Dual-gate gate-2 (operator acceptance review): operator confirms 100% closed-trial coverage + GHA fail-loud mode + variance policy adequacy.

### AC-5a.1-I — Sprint-status state-flips at filing AND close.

---

## File Structure Requirements

### NEW files

- `app/replay/{__init__, regression, discovery}.py` + replay_error classes
- `tests/integration/replay/{test_replay_all_closed_trials, test_sanctum_variance_policy, test_replay_budget, test_gha_workflow_present}.py`
- `tests/trial_replay/{__init__, test_replay_all}.py`
- `.github/workflows/trial-replay.yml`

### MODIFIED files

- `_bmad-output/implementation-artifacts/sprint-status.yaml` — per AC-I.
- `docs/dev-guide/langgraph-migration-guide.md` — §"Trial Replay" added.

---

## Testing Requirements

**K-target ~1.5× (target 18 / floor 12).** AC-A:2 + AC-B:2 + AC-C:N→1 K-floor + AC-D:2 + AC-E:1 = **8 K-floor**. RIDER: AC-A discriminated-error per kind (3 kinds → 3 K-floor units; orthogonal properties per Decision #3) → +2; AC-B mode-orthogonal-property-pin → +1; AC-C per-trial-success-shape pin → +1 = **honest 12 K-floor (meets floor)**. Within ~1.5× band.

Sandbox-AC PASS (LangGraph checkpointer + Postgres shipped per Slab-1; pytest.skip on missing service).

---

## Dev Agent Record

_(Populated during T1–T9 execution.)_
