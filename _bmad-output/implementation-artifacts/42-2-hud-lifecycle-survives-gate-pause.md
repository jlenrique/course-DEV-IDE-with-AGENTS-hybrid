---
id: 42-2
epic: 42
status: ready-for-dev
depends_on: null   # independent; can open first in Epic 42
gate_mode: single-gate
anchor_provenance: HEAD 23480353
baseline_commit: d8fb959b  # dev-open baseline 2026-07-16 (post-Epic-41)
lockstep: true   # touches app/hud/** and/or app/notify/** (block_mode_trigger_paths globs)
---

# Story 42.2: HUD lifecycle survives gate pause

Status: done  # 2026-07-16 dev complete (fresh Claude dev agent) + review PASS; single-gate; LOCKSTEP; carries the CREATE_NO_WINDOW fix

## Dev Agent Record

**Dev complete 2026-07-16 (fresh Claude dev agent). Baseline `d8fb959b`. Status → review → done.**

### File List
- `app/marcus/orchestrator/preflight.py` (M) — AC-7 `_no_window_creationflags()` (win32-guarded `CREATE_NO_WINDOW`, POSIX→0/unchanged) applied to the HUD-server Popen (L668-670 — the culprit had NO creationflags); status-aware teardown (`_status_aware_teardown`/`_read_run_status`/`_terminate_with_grace`, `TERMINAL_RUN_STATUSES={completed,failed}`, `.hud-stop` sentinel via `request_hud_stop`) replaces the blanket `atexit` terminate; `reattach_or_launch_hud_server` + `probe_hud_identity` for resume reuse (no double-launch).
- `app/notify/__main__.py` (M) — AC-7 rationale comment only (already `DETACHED_PROCESS` = no console).
- `tests/hud/test_hud_lifecycle_survives_pause.py` (A) — 25 hermetic tests (fake popen/TestClient — no real subprocess, no windows).
- `tests/notify/test_main.py` (M) — 1 AC-7 notifier pin.
- `tests/audit/test_audit_tw_7c_4_no_live_dispatch_scope_creep.py` (M) — allowlisted the 4 touched `.py`.

### Completion Notes
- **AC-7 (the operator's window fix):** the HUD server child now spawns with `CREATE_NO_WINDOW` on Windows — no more empty console windows from HUD launches during runs/dev. POSIX byte-unchanged.
- **Lifecycle (Option b, status-aware teardown):** chosen because the launcher lives in fenced `production_runner.py`; the fix lives entirely in `preflight.py`. On CLI-process exit, teardown reads run status: terminal (`completed`/`failed`) or explicit stop → terminate+grace(5s)+kill; `paused-at-gate`/`paused-at-error`/unknown → NO-OP (child stays alive — the pause-survives fix; unknown = safe default). NEVER-raises preserved throughout. Resume never double-launches (`resume_production_trial` never calls `launch_hud_server`; `reattach_or_launch_hud_server` is the robust reuse contract).

### Change Log
- 2026-07-16: CREATE_NO_WINDOW on HUD spawn (AC-7) + status-aware HUD teardown (pause≠teardown) + resume reuse; done.

## Senior Developer Review (AI) — 2026-07-16

**Reviewer:** orchestrator, inline adversarial review (no parallel test-agents, per the operator's window constraint). **Outcome: APPROVE.**

**Correctness:** `CREATE_NO_WINDOW` verified applied to the real Popen (L668-670 via the win32-guarded helper) — not merely defined. Status-aware teardown verified: `else` branch is a clean no-op (`# parked at a pause → leave the child ALIVE`), wrapped in a fault-swallowing try/except (never-raises). `TERMINAL_RUN_STATUSES={completed,failed}` mirrors the notifier. "status unknown → alive" is the correct safe direction (a transient run.json read glitch must not kill a live surface). Resume-reuse sound (launch is start-path-only by construction; reattach handshakes the nonce/port).

**Full spawn audit (orchestrator):** confirmed `production_clone_launch` is an evidence field, NOT a subprocess — `production_runner.py` spawns no window-popping child. Notifier already `DETACHED_PROCESS` (no console). The HUD popen was the sole confirmed culprit; fixed.

**Verification:** 32 hermetic tests pass (lifecycle 25 + notifier); `tests/hud`+`tests/notify` 125 passed; lockstep exit 0; ruff clean; import-linter 18/0; TW-7c-4 pass. Baseline-diff net-new=0 (the 1 failure `test_health_tiles_prefer_persisted_cost_report` is the known pre-existing inherited baseline failure, stash-witnessed).

**Findings:** none blocking. **Residual (filed, not blocking):** three *blocking* `subprocess.run` git/texas spawns (`manifest_scan.py`, `gh_pages_publish.py`, `retrieval_dispatch.py`) inherit the parent console (low window risk) but aren't `CREATE_NO_WINDOW`-guarded — filed as `repo-wide-no-window-spawn-sweep` in case any window persists. **Live proof owed:** the "no window on a real HUD spawn" is empirically confirmed only by the flag-pin (both dev and review used mocked popen); the operator's next real run is the live witness.

## Story

As the operator watching a live run,
I want the HUD (and notifier) to stay alive across start-walk → gate pause → resume,
so that when `trial start` returns at a gate (e.g. G0E) I can keep browsing the run surface and decide — instead of the HUD dying (port 8791 no longer LISTENING) the moment the walk pauses.

## Provenance & Dependencies (BINDING)

- **Epic authority:** `epics-operator-surface-next-pass-2026-07-16.md` §42-2 (E42-AC2 availability).
- **Green-light:** party record P-6 (D is a hermetic app-code lifecycle fix, split from E/42-4; must not be held hostage to tunnel plumbing).
- **Requirement + root cause:** `evidence/operator-hil-display-requirements-2026-07-16.md` §2. Diagnosis: `launch_hud_server` (`app/marcus/orchestrator/preflight.py:509`) "registers an `atexit` terminate" on the `trial start` process. When `trial start` RETURNS at the gate pause (the process exits back to the shell), `atexit` fires and terminates the HUD child. The HUD's lifecycle is coupled to the CLI process, not to the run status.
- **Inventory row filed as this story:** `hud-lifecycle-survives-gate-pause`.

## T1 Readiness (BINDING readings before any code)

1. **Lockstep gate FIRST:** `docs/dev-guide/pipeline-manifest-regime.md` — `app/hud/**` and `app/notify/**` are trigger globs. Cora block-mode hook gates.
2. `app/marcus/orchestrator/preflight.py` — `launch_hud_server` (L509-556: env wiring `HUD_TRIAL_ID`/`HUD_RUN_DIR`/`HUD_LAUNCH_NONCE`/`HUD_PORT`/`HUD_MODE`, `atexit` terminate registration L533+, NEVER raises), the notifier launch path, `notifier_alive_fn`/`hud` preflight items (L247-269, L473-477).
3. `app/hud/server.py` — the GET-only localhost server; how it binds a trial_id at launch and its own shutdown path.
4. `app/notify/service.py` — notifier child lifecycle (parallel concern; same teardown coupling).
5. Where `trial start` returns at a `paused-at-gate` (the boundary that triggers the process exit → `atexit`).
6. Epic-35 lifecycle language in the HUD arc + the `hud-stable-public-live-url` deferred entry: "run start launches/health-checks the HUD; pauses keep it alive; terminal status stops it after a short grace." That IS the target lifecycle contract.

## Acceptance Criteria

1. **Pause ≠ teardown.** When `trial start` (start walk) returns at `paused-at-gate`, the HUD server child and notifier child **remain alive and LISTENING** on their port. The `atexit`-terminate coupling that kills them on CLI-process exit is removed/decoupled for the pause case.
2. **Teardown couples to terminal status + explicit stop.** HUD/notifier children are torn down only on: terminal run status (`completed` / `cancelled` / `abandoned` / `paused-at-error` after operator ack), OR an explicit operator stop command, each with a short grace period. A gate pause is NOT terminal.
3. **Resume re-attaches, does not double-launch.** When the operator resumes (`trial resume`), the run does not spawn a second HUD on the same trial/port; it health-checks the existing child and reuses it (or cleanly replaces a dead one). No orphaned/duplicate HUD processes across a pause→resume cycle.
4. **Idle honesty.** Between a pause and resume the HUD serves the live run surface (it already reads the live file — AD-2/6, zero-lie). When no run is active it may honestly show `HUD offline / no active run`.
5. **`--hud off` unchanged.** With `--hud off`, nothing launches and nothing changes (the preflight items stay omitted per L103-104).
6. **Never-raises preserved.** The lifecycle change keeps `launch_hud_server`'s NEVER-raises contract — a HUD/notifier lifecycle failure degrades the surface, never the run.
7. **No stray console windows on Windows (operator requirement 2026-07-16).** HUD-server + notifier child processes (and any other spawned children in this path — e.g. clone launches) MUST spawn with `creationflags=subprocess.CREATE_NO_WINDOW` (or an equivalent no-window `STARTUPINFO`) on Windows so a run/dev session does not litter the desktop with empty terminal windows. Pin: on `win32`, the spawn call passes the no-window flag; cross-platform code paths are unaffected. This bit the operator repeatedly during dev sessions (integration suites spawn these children); it is a real ergonomics defect, not cosmetic.

## Scope Fences (hard NO)

- **NO public URL / tunnel work** — that's 42-4. This story is localhost lifecycle only (P-6: don't make the hermetic fix hostage to tunnel plumbing).
- **NO change to what the HUD SERVES** (GET-only, raw live file, zero-lie) — only WHEN the process lives/dies.
- **NO change to run/gate semantics** — the walk still pauses and resumes exactly as today.
- **NO new always-on daemon** beyond the run's lifecycle — the HUD's life is bounded by the run (launch at start, alive across pauses, stop at terminal + grace), not a persistent service.
- Mid-dev drift into other trigger rows (`operator_surface_assembler.py`, `production_runner.py`) is a STOP.

## Lockstep declaration

| Scoped file | Trigger-path entry? | Touched? |
|---|---|---|
| `app/marcus/orchestrator/preflight.py` | not listed (HUD launch plumbing) | yes (lifecycle decoupling) |
| `app/hud/server.py` / `app/hud/**` | **trigger glob** | likely (shutdown path) |
| `app/notify/service.py` / `app/notify/**` | **trigger glob** | likely (notifier lifecycle) |

**Verdict: lockstep regime TRIGGERED** (`app/hud/**` / `app/notify/**`). Read `pipeline-manifest-regime.md` at T1; Cora block-mode hook; lockstep checker + `tests/hud/**` + `tests/notify/**` green before review.

## Dev Notes

- The core fix is decoupling the child processes from the CLI process's `atexit`. Options for dev to choose (document the choice): (a) launch the HUD/notifier in a detached process group so a CLI exit at pause does not signal them, with an explicit lifecycle owner that ties teardown to run status; (b) keep them owned but replace the blanket `atexit` terminate with a status-aware teardown that no-ops on `paused-at-gate`. Prefer the approach that keeps the NEVER-raises + no-orphan guarantees.
- Health-check on resume: reuse the existing `HUD_LAUNCH_NONCE`/`HUD_PORT` handshake to detect a live child before launching a new one (AC-3).
- Tests: `tests/hud/test_hud_lifecycle_survives_pause.py` — pause returns with HUD still alive (mock/child-proc harness); terminal status tears down after grace; resume reuses not re-launches; `--hud off` no-op; never-raises on launch failure. Keep hermetic (no real long-lived sockets in CI where avoidable; use the existing 35.x HUD test harness patterns).

## References

- `evidence/operator-hil-display-requirements-2026-07-16.md` §2
- `epics-operator-surface-next-pass-2026-07-16.md` (P-6 split)
- `epics-operator-hud-2026-07-11.md` (Epic 35 lifecycle contract)
- `deferred-inventory.md` §HUD Next-Pass (`hud-stable-public-live-url` lifecycle language)
- `docs/dev-guide/pipeline-manifest-regime.md`

## Green-Light Round Record (2026-07-16)

**Verdict: 5/5 GREEN** — Winston insisted on the D/E split (P-6: hermetic vs infra failure domains); Sally held the operator's "watch my run across the pause" promise; Murat required the no-orphan / resume-reuse pins. Folded: P-6, the terminal-status+grace teardown contract, the never-raises preservation. Single-gate (hermetic app-code) despite the lockstep glob. Status → ready-for-dev.
