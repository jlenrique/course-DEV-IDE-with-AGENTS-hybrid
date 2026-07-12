# Story 35.3 — Completion Notes (COMPLETE)

Start-path integration: pinned sequence + pre-flight/heartbeats. Fresh dev agent
(retry). No commits made (orchestrator commits post-review).

## Status checklist
- [x] app/marcus/orchestrator/preflight.py (new module)
- [x] production_runner start-region integration (launch + gate + trace helpers)
- [x] trial.py start-path integration (--hud flag, pre-envelope exit traces)
- [x] tests/unit/marcus/orchestrator/test_preflight.py (14 tests + 1 live)
- [x] tests/unit/marcus/orchestrator/test_start_path_sequence.py (8 tests)
- [x] existing suites green (tests/unit/marcus 514 passed; integration marcus 39 passed)
- [x] ruff clean; lint-imports 17 kept / 0 broken; lockstep checker exit 0
- [x] L3 live witness banked (hud-35-3-preflight-live-witness.md)

## Files touched
- NEW `app/marcus/orchestrator/preflight.py` — `run_preflight`, `PreflightDeps`,
  `PreflightResult`, `launch_hud_server`, phase-01 local checks + phase-02 live
  heartbeats (OpenAI/Gamma/LangSmith-env), healthz identity probe.
- `app/marcus/orchestrator/production_runner.py`:
  - `class PreflightGateFailed` (new exception).
  - `_append_operator_surface_trace`, `emit_registered_and_terminal_trace`,
    `_run_start_preflight_gate` (new helpers).
  - `run_production_trial(..., hud="on")` param + the pinned-sequence gate block
    inserted after the registered persist + steps emit, before the walk.
  - added `DEFAULT_HUD_CONFIG_PATH` to the assembler import; `__all__` updated.
- `app/marcus/cli/trial.py`:
  - `start_trial(..., hud="on")` param, threaded into `run_production_trial`.
  - `--hud on|off` CLI arg (default on, AD-7).
  - `cancelled-at-g0` + `saved-only` exits now call
    `emit_registered_and_terminal_trace` (amendment 12).
  - `start_trial_cli` catches `PreflightGateFailed` → exit 1 with a clear message.

## Sequence integration points (file:line, current)
- Registered projection persist: `production_runner.py` `_persist_envelope` @ ~2680
  (35.2, unchanged) — the projection the gate + trace build on.
- Steps emit @ ~2839 (35.2, unchanged).
- **NEW gate block** inserted immediately after the steps emit (~2840), BEFORE
  `compile_run_graph` / the node walk and BEFORE the in-flight transition:
  `if not allow_offline_cost_report: _run_start_preflight_gate(...)`; not-green
  → append terminal trace + `raise PreflightGateFailed` (walk never runs).
- Pre-envelope exits: `trial.py::start_trial` cancelled-at-g0 return + saved-only
  return each call `emit_registered_and_terminal_trace`.

## Design decisions of record
- Pinned AD-7 sequence maps onto the real topology: `start_trial`
  (mint/dir/G0/pre-envelope-exits) → `run_production_trial` (registered persist →
  steps → **HUD launch + pre-flight gate** → in-flight → walk).
- Pre-flight + HUD/notifier launch run ONLY on real starts
  (`not allow_offline_cost_report`); offline harness runs skip them, so the whole
  existing offline suite + cost-report path is byte-unchanged.
- `--hud on|off` (default ON) gates server + notifier LAUNCH only; pre-flight is
  runtime-owned and always runs on a real start.
- Gating rule: `all_green = all(item.state == "pass" for non-soft items)`.
  `missed` and `fail` both break green (per "any failed/missed → FAIL") but stay
  DISTINCT states (missed != fail). Soft items (coordination-db) never gate.
- Server launch failure → healthz item FAIL (injected `healthz_fn`), never a raise.
- v1 heartbeat set = OpenAI + Gamma + LangSmith-env-presence (amendment 10).

## Test results
- `test_preflight.py` + `test_start_path_sequence.py`: 21 passed, 1 deselected
  (the `live` heartbeat test) — run `-n0`.
- Wrong-server-on-port: `test_healthz_fails_wrong_server_on_port` +
  `test_healthz_nonce_mismatch_same_trial_fails` (identity guard live logic).
- FAIL-blocks-walk / green-proceeds / offline-skips / pinned-order / server-
  before-heartbeats / launch-failure-not-raise all covered.
- Regression: `tests/unit/marcus` 514 passed; `tests/integration/marcus`
  (trial CLI + confirm-or-edit + cli/) 39 passed.
- ruff: all checks passed. lint-imports: 17 kept, 0 broken (HUD1 fence intact).
  lockstep checker: exit 0.

## Deviations / notes for review
- **Full trial-start L3 to the spawn-gate deferred to 35.7** (documented in the
  live-witness file): driving the full server-child + healthz-live path end to
  end requires a paid specialist walk, which this story is explicitly told NOT
  to start. The pre-flight function itself is proven live (real OpenAI + Gamma);
  the healthz identity item is proven hermetically incl. wrong-server-on-port.
- `_run_start_preflight_gate` imports `app.notify.__main__.launch_notifier` and
  `app.marcus.orchestrator.preflight` lazily inside the function. No import-linter
  contract forbids orchestrator → app.notify or orchestrator → scripts (only the
  HUD1 fence restricts `app.hud`); lint-imports confirms 0 broken.
- No `state/config/hud-config.yaml` yet (35.6 owns it); `load_hud_config` returns
  defaults (port 8791) when absent — the gate handles this gracefully.
