# Story 35.6 — Completion Notes (Notifier + watchdog + push)

**Dev agent:** fresh bmad-dev-story cycle · **Branch:** dev/hud-revival-2026-07-11
**ADs:** 9 (shared notifier / restart / channel split), 10 (stall + producer-dead
watchdog), 18 (contract-owned derivation), 19 (single HudConfig owner).
**Do-not-commit honored** (orchestrator commits post-review). No production
runner / trial.py / app.hud / contract-module files touched.

## Files (all new except the two shared-surface edits)

| Path | Kind | Notes |
|---|---|---|
| `app/notify/__init__.py` | new | Package surface + layer-rule docstring; re-exports service API. |
| `app/notify/service.py` | new | `NotifierService` — mtime-gated watcher, contract derivation, watchdog, push, restart state, scheme allowlist. |
| `app/notify/__main__.py` | new | `python -m app.notify` entry + `run_forever` loop + `launch_notifier` (detached Popen) + `_detached_popen_kwargs`. |
| `state/config/hud-config.yaml` | new | Real v1 config (HudConfig schema); parses `status="ok"`. |
| `tests/notify/_helpers.py` | new | `FakeApprise` spy + `make_projection` + `ProjectionWriter` (mtime-stepping). |
| `tests/notify/conftest.py` | new | Fixtures (run_dir/state_dir/writer/fake_apprise/clock). |
| `tests/notify/test_notifier_service.py` | new | Event goldens, watchdog, producer-dead, restart, fault-injection, scheme allowlist. |
| `tests/notify/test_config_gating.py` | new | Config opt-in gating + shipped-file parse + defaults fallback. |
| `tests/notify/test_main.py` | new | Run-loop exit-on-terminal, detached flags, arg parser, launch argv. |
| `tests/notify/test_live_ntfy_witness.py` | new | `live`+`serial` real ntfy push witness (excluded by default). |
| `pyproject.toml` | edit (1 range) | `apprise>=1.9.8,<2` added to `[project].dependencies`. |

## Design decisions (traceable to ADs / story guidance)

- **Derivation is never re-implemented (AD-18).** The service calls the
  contract's `derive_event_transitions` and `stall_condition` only; it adds no
  local transition logic. Config gating (`enabled`) + channel routing
  (`push`) + ack-dedup are the only service-side policy.
- **Channel split (AD-9).** The notifier owns PUSH only. On-HUD toast/sound are
  the HUD page's. Push-enabled classes (`paused_at_gate`, `paused_at_error`,
  `run_stalled`) reach Apprise; `batch_pause_resumed` and `health_threshold`
  fire on-HUD only (never push) — verified in the goldens via the spy.
- **Watchdog (AD-10).** Every poll evaluates: (a) producer-dead — status
  `in-flight` + frozen mtime + producer PID not alive → `run_stalled` ("producer
  dead"); (b) `stall_condition(cur, now, stall_budget)` for frozen progress.
  `waiting_for_provider_batch` is exempt (the contract predicate only fires for
  `in-flight`). Cross-platform PID liveness: Windows `OpenProcess`/
  `GetExitCodeProcess` via ctypes; POSIX `kill(pid,0)`. Unknown PID → assume
  alive (never false-alarm).
- **Restart semantics (AD-9).** State file `state/runtime/notify/<trial_id>.json`
  `{last_processed_progress_seq, last_status, acked}` in the notifier's OWN dir
  (never the run dir — single-writer rule; asserted). `acked` (keyed by pause/
  stall identity) is the durable dedup: an active-unacked pause fires exactly
  once on restart; an already-acked pause stays silent. `batch_pause_resumed` is
  transition-only — a fresh process starts `prev=None`, so a restart observing
  `in-flight` can never synthesize it (asserted).
- **Push safety (AD-9).** URLs come from `HUD_PUSH_URLS` env (comma-sep); creds
  never in config/repo. Scheme allowlist `{ntfy, ntfys, pover}` validated BEFORE
  any target is added; `mailto`/`json`/`slack`/webhook rejected (asserted). URLs
  are redacted (scheme+host only) in logs.
- **Fault tolerance.** `poll_once` wraps its body in a catch-all: unreadable/
  garbage projection, corrupt state file, transport raising, bad on_event sink —
  all logged and swallowed, never raised. The transport-raising golden asserts
  `poll_once` still returns the derived event with `pushed=False`.
- **Windows survives-session (Amelia trap 3).** `launch_notifier` uses
  `DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP` (POSIX: `start_new_session=True`)
  with stdout/stderr to a per-trial logfile under the notifier's own state dir.
  The loop exits on terminal status (`completed`/`failed`) + 60s grace.
- **Single config owner (AD-19).** `hud-config.yaml` is parsed only by the
  contract's `load_hud_config`; the service holds the parsed `HudConfig` +
  parse-status string. Partial overrides merge over defaults (verified: disabling
  one class leaves the rest enabled).

## Verification (DoD witness set)

| Gate | Command | Result |
|---|---|---|
| Hermetic suite | `.venv/Scripts/python.exe -m pytest tests/notify -q` | **26 passed** (live/serial excluded) |
| Serial detail | `pytest tests/notify -n0 -q` | 26 passed in 0.54s |
| Ruff | `ruff check app/notify tests/notify` | **All checks passed** |
| Import-linter | `lint-imports` | **17 kept, 0 broken** (incl. new app.notify tree; no threading import; HUD1 intact) |
| Lockstep | `check_pipeline_manifest_lockstep.py` | **exit 0** — trace `reports/dev-coherence/2026-07-11-2154/…PASS.yaml` |
| L3 live push | `test_live_ntfy_witness.py` / banked script | **delivered + receipted**, msg id `wmUW9CnmLm6S` (see `hud-35-6-ntfy-witness.md`) |

Test coverage maps to the DoD: event goldens (5 classes, config-gated via spy),
new-gate-identity refire, watchdog fire-once + refire-after-progress, batch
exempt, producer-dead, producer-alive no-false-alarm, restart-mid-pause
(unacked fires once / acked silent), batch transition-only across restart,
state-file-in-own-dir, transport-raising fault injection, garbage/missing
projection no-op, scheme allowlist (mailto rejected) + `validate_push_urls` unit,
config disable + shipped-file parse + defaults fallback, run-loop exit + detached
flags + launch argv.

## Deviations / notes for review

1. **`uv lock` not run — project is `managed = false`.** `uv lock` refuses on
   this repo (`error: The project is marked as unmanaged`), consistent with the
   `[tool.uv] managed = false` policy (active `.venv` is authoritative; MEMORY
   `.venv/Scripts/python.exe allowed`). apprise `1.12.0` (satisfies `>=1.9.8,<2`)
   is installed in the live `.venv` and imports cleanly; `python -m app.notify
   --help` works. `uv.lock` was left untouched (hand-editing a lockfile is
   riskier than the documented unmanaged-env convention). Flag if the operator
   wants the lockfile regenerated via a managed path.
2. **Config schema carries ONE staleness budget.** EXPERIENCE.md lists 5s (run
   state) / 60s (health tiles), but `HudConfig` (extra="forbid") has a single
   `staleness_budget_seconds`. Set to 5; the 60s health budget is documented in
   the YAML as a render-side default (HUD render owns it), not a v1 config field.
   No schema change made (contract module is out of scope for 35.6).
3. **`health_threshold` default = on-HUD only.** Matches the contract's
   `_default_notifications` and EXPERIENCE.md table (enabled, no sound, no push).
4. **Pushover deferred to config-swap** per greenlight amendment 10 — the live
   witness is accountless ntfy; `pover://` is an env/config change only.
5. **Two lint noqas** on over-long test *function signatures* (5-fixture params);
   all other E501s were wrapped. No `pyproject` per-file-ignore added (kept the
   pyproject touch to the single apprise line as scoped).
