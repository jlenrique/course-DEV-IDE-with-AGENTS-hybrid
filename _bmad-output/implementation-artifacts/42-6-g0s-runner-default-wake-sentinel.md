---
id: 42-6
epic: 42
status: ready-for-dev   # rider R1 from the Epic-42 party sign-off (party-named + HIGH-prioritized = green-lit)
depends_on: 42-5
gate_mode: dual-gate   # LOCKSTEP (production_runner.py) + a behavior-default change on the operator start path
baseline_commit: 516ca453
lockstep: true
---

# Story 42.6: G0S default-ON for operator-steered runs (per-run wake sentinel) — rider R1

Status: done  # 2026-07-17 dev complete + dual-gate review PASS; rider R1 RESOLVED — G0S shows by default on operator runs

## Dev Agent Record

**Dev complete 2026-07-17 (fresh Claude dev agent). Baseline `516ca453`. Status → review → done.**

### File List
- `app/marcus/orchestrator/production_runner.py` (M) — `PREWALK_SETTINGS_CONFIRM_SENTINEL_NAME=".prewalk-settings-confirm"`, `_prewalk_settings_sentinel_path`, `write_prewalk_settings_confirm_sentinel(run_dir)` (AC-2), `_prewalk_settings_confirm_active(run_dir=None)` now returns True on env flag OR sentinel presence (OR semantics); the disposition calls it with `_run_dir(trial_id, runs_root)` (both walks route through the shared disposition).
- `app/marcus/cli/trial.py` (M) — `start_trial(..., prewalk_settings_confirm: bool = False)` (function default OFF → test determinism) writes the sentinel iff True; `start_trial_cli` passes `getattr(args, "prewalk_settings_confirm", True)`; new `--prewalk-settings-confirm` / `--no-prewalk-settings-confirm` flag (default ON).
- `docs/operator/hud-guide.md` (M) — the `--no-prewalk-settings-confirm` escape documented.
- `tests/marcus/orchestrator/test_prewalk_settings_wake_sentinel.py` (A) + TW-7c-4 allowlist.

### Completion Notes
- G0S now shows by DEFAULT on operator-steered CLI runs (sentinel written by `start_trial` on the CLI path), while tests calling `start_trial(...)` directly get the OFF default → the ~13 start_trial tests + all start-path consumers stay deterministic. Env flag `MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE` retained as an override (OR). Offline/non-interactive opt-out (42-5 AC-6) preserved — the sentinel wakes the gate but the offline/non-interactive disposition still skips it explicitly+traced. `--no-prewalk-settings-confirm` = operator opt-out for a fast run.

### Change Log
- 2026-07-17: per-run G0S wake sentinel; CLI default-ON; rider R1 resolved; done.

## Senior Developer Review (AI) — 2026-07-17 — DUAL-GATE

**Reviewer:** orchestrator, inline (hermetic; no windows). **Outcome: APPROVE.** (Dev agent's own report was incomplete — it backgrounded a consumer-suite pytest and terminated; orchestrator completed the verification.)

**Correctness:** wake check now honors env OR per-run sentinel; `run_dir` threaded into the check via the shared disposition (both walks). `start_trial` function default OFF is the key to test determinism; CLI passes True. No `os.environ.setdefault` (the leak anti-pattern avoided). Env flag kept as override. Opt-out preserved.

**Consumer-wide verification (the start-path-ripples check):** 42-6 unit + 42-5 gate + 13 start_trial picker tests = 64 passed; full `tests/unit/marcus/cli/` = 116 passed; integration `test_trial_cli.py` = 12 passed + 1 pre-existing (`test_start_trial_ratified_collateral_intent_runs_local_runtime` fails IDENTICALLY at 07W.1 FileNotFound — walk reached PAST G0S, so G0S did NOT newly pause it); `test_trial_475` 2 fails = **stash-witnessed pre-existing** PreflightGateFailed (before G0S). Lockstep exit 0; ruff clean; import-linter 18/0. **Net-new attributable to 42-6 = 0.** No start-path consumer newly pauses at G0S in the test suite (they call start_trial directly / run offline / fail at preflight before G0S).

**Findings:** none blocking. **Owed (R2, operator-gated):** a real operator `trial start` now writes the sentinel → G0S pauses pre-G0 on the terminal — witnessed on the operator's next steered run.

## Story

As the operator starting a real steered trial,
I want the pre-walk settings confirm gate (G0S) to appear by DEFAULT — without exporting an env flag —
so that I actually see and can confirm/change my ~16 run settings before the walk spends, which is what I asked for (42-5, RED priority).

## Why (rider R1 from `epic-42-signoff-party-record-2026-07-17.md`)

42-5 shipped G0S woken only by `MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE` (default OFF → traversed byte-identically, mirroring G0E/G0R). The party signed Epic 42 with R1 as the immediate follow-up: the gate is dark by default, so the operator's requirement is met by the MECHANISM but not by DEFAULT. The 42-5 dev deliberately did NOT `os.environ.setdefault` in `start_trial` because that leaks the pause into the ~13 `start_trial` test files and makes the suite non-deterministic. R1 is the clean fix: a per-run persisted wake sentinel set by the CLI operator path.

## T1 Readiness (BINDING)

1. **Lockstep FIRST:** `docs/dev-guide/pipeline-manifest-regime.md` — touches `production_runner.py` (trigger row) + `trial.py`.
2. `app/marcus/orchestrator/production_runner.py`: `PREWALK_SETTINGS_CONFIRM_ACTIVE_ENV` (L161), `_prewalk_settings_confirm_active()` (L165, env-only today), `_prewalk_settings_gate_disposition` (L2681; wake check at L2704). Both walks call the disposition with the run context (runs_root + trial_id → run_dir).
3. `app/marcus/cli/trial.py`: `start_trial` (L476), `start_trial_cli` (L935), the `start` subparser (~L1370). Determine HOW the ~13 start_trial tests invoke it (direct `start_trial(...)` call vs `start_trial_cli(Namespace)`), so the default-split doesn't break them.

## Acceptance Criteria

1. **Per-run wake sentinel honored.** `_prewalk_settings_confirm_active` (or the disposition) additionally returns True when a per-run sentinel exists in the run dir (e.g. `<run_dir>/.prewalk-settings-confirm`). The env flag `MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE` STILL works (OR semantics — either wakes G0S). Read by BOTH walks (start + continuation) from the run dir.
2. **CLI operator path writes the sentinel by DEFAULT.** A real `trial start` (operator CLI) writes the sentinel so G0S wakes and pauses pre-G0. Implement via an explicit param `start_trial(..., prewalk_settings_confirm: bool = False)` (function default OFF) + `start_trial_cli` passing `True` (from a `--prewalk-settings-confirm` / `--no-prewalk-settings-confirm` flag defaulting ON, so the operator can opt OUT). `start_trial` writes the sentinel iff the param is True.
3. **Tests stay deterministic (the whole reason for the sentinel).** The ~13 tests that invoke `start_trial` directly get the function default (OFF → no sentinel → G0S dormant → byte-identical traversal). Any test invoking `start_trial_cli` that would now newly pause is updated to `--no-prewalk-settings-confirm` OR the offline/non-interactive opt-out (AC-6 of 42-5) — consumer-wide baseline-diff to catch every one (LESSON from the 42-1 escape).
4. **Opt-out preserved (42-5 AC-6).** Offline (`--allow-offline-cost-report`) / non-interactive / delegated-HIL runs still skip the pause explicitly + traced, even with the sentinel — the sentinel wakes the gate, but the offline/non-interactive disposition still skips it honestly (don't regress 42-5's opt-out).
5. **`--no-prewalk-settings-confirm` escape.** The operator can turn it off for a given run (a fast keyless run) via the CLI flag; documented in the operator/admin guide.

## Scope Fences (hard NO)

- NO removal of the `MARCUS_PREWALK_SETTINGS_CONFIRM_ACTIVE` env flag (OR semantics — keep it as an override).
- NO global `os.environ.setdefault` in start_trial (the exact anti-pattern that leaks into the test suite — use the per-run sentinel).
- NO change to G0S gate mechanics / the DecisionCard / the readout (42-5/42-3 substrate) — only the WAKE condition + the CLI default.
- NO regression of 42-5's opt-out honesty (offline/non-interactive still skip).
- Only `production_runner.py` + `trial.py` (+ the sentinel read/write helper) + docs + tests.

## Dev Notes

- Sentinel = a tiny run-dir marker file (e.g. `.prewalk-settings-confirm`), written at `start_trial` when `prewalk_settings_confirm=True`, read by the disposition via the run_dir the walks already have. Content can be a short JSON `{written_by, at}` or empty — presence is the signal.
- Thread run_dir into `_prewalk_settings_confirm_active` (or add a run_dir-aware variant the disposition calls); keep the env-only overload for callers without a run dir.
- Consumer-wide baseline-diff over `tests/marcus/`, `tests/integration/marcus/`, `tests/unit/marcus/cli/` — a start-path default change ripples.
- Lockstep checker exit 0; ruff; import-linter; TW-7c-4 for any new test file.

## References
- `_bmad-output/planning-artifacts/epic-42-signoff-party-record-2026-07-17.md` (rider R1)
- `_bmad-output/implementation-artifacts/42-5-pre-walk-settings-confirm-gate.md` (the gate this defaults-ON)
- `deferred-inventory.md` §Named-But-Not-Filed `g0s-runner-default-wake-policy`

## Green-Light
Rider R1 was named + HIGH-prioritized by the Epic-42 party sign-off (5/5) — that is the green-light. Dual-gate, lockstep; fresh-Claude-dev-agent.
