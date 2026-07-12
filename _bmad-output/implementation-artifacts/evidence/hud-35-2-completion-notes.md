# Story 35.2 — Assembler + runner emission (both walks) — Completion Notes

**Date:** 2026-07-11 · **Branch:** dev/hud-revival-2026-07-11 · **Dev:** fresh bmad-dev-story agent
**ADs:** 2, 10 (producer), 15, 17 (+3 for the command builder). No commits (orchestrator commits post-review).

## Files

**New:**
- `app/marcus/orchestrator/operator_surface_assembler.py` — `OperatorSurfaceAssembler`, the sole writer of `operator-surface.json` (AD-15). Stateless construct-on-demand keyed `(trial_id, runs_root)` (greenlight amendment 13); read-merge-write via the contract's lenient reader + strict re-serialize.
- `app/marcus/cli/next_action.py` — `build_next_action(envelope, card_path=None) -> str`, the CLI-co-located next-action command builder (AD-3). Stdlib-only; imported lazily by the assembler to avoid the `app.marcus.cli` package-init import cycle.
- `tests/unit/marcus/orchestrator/test_operator_surface_assembler.py` — 15 assembler unit tests.
- `tests/unit/marcus/orchestrator/test_runner_projection_emission.py` — 8 runner-integration tests.
- `tests/unit/marcus/cli/test_next_action.py` — 5 command-builder round-trip tests.

**Modified:**
- `app/marcus/orchestrator/production_runner.py` — minimal emission integration (below).

## Integration diff summary (production_runner.py)

Lines touched are small and localized; all emission calls are wrapped never-to-raise.

1. **Import** (1 line): `from app.marcus.orchestrator.operator_surface_assembler import OperatorSurfaceAssembler`.
2. **Two helper functions** (~24 lines) before `_persist_envelope`: `_emit_operator_surface(envelope, runs_root)` and `_emit_operator_surface_steps(trial_id, runs_root, manifest, walk_index)` — each double-guarded (the assembler already swallows all exceptions per amendment 8).
3. **`_persist_envelope`** (+2 lines): after the unchanged `run.json` `write_text`, calls `_emit_operator_surface(...)`. run.json write semantics are byte-identical (same `model_dump_json(indent=2) + "\n"`, same plain write, no atomicity/reorder).
4. **Start walk** (`run_production_trial`): `update_steps` at `compose_manifest` (walk_index 0); loop wrapped in `_start_assembler.freshness_tick()`; per-node `_emit_operator_surface_steps(...)` at loop top.
5. **Continuation walk** (`_continue_production_walk`): `update_steps` at `compose_manifest` (walk_index `start_index`); loop wrapped in `_continue_assembler.freshness_tick()`; per-node steps update at loop top.
6. **Reconcile-on-entry (AD-17)** (+2 lines each): `resume_production_trial`, `resume_batch_production_trial`, `recover_production_trial` each call `_emit_operator_surface(envelope, runs_root)` immediately after loading the run.json envelope, before any status guard. (`run_production_trial`'s first `registered` persist is itself the entry emit.)
7. **~3501 direct run.json bypass** (recover-reenter branch): the lone `(run_dir/"run.json").write_text(...)` replaced by `_persist_envelope(envelope, runs_root)` — byte-identical envelope content, now also emits the projection.

## Design decisions / deviations

- **seq / progress_seq (AD-10):** `seq` bumps on every write. `progress_seq` starts at its 0 baseline on the first-ever write and increments only on progress events — envelope status/pause-identity transitions (`emit`), walk-index change / node lifecycle (`update_steps`), pre-flight item completion (`update_preflight_item`). Freshness ticks and `update_health` bump `seq` only. `append_trace` / `set_notifications_echo` bump `seq` only.
- **walk_generation / reentered_from inferred, not threaded:** the assembler detects a walk-index REGRESSION vs the last-seen index inside `update_steps` and marks it as a labeled re-entry (`walk_generation++`, `reentered_from=new_index`). This satisfies AD-15's "index regression renders as labeled re-entry" without threading generation markers through the continuation-walk signatures — keeping the runner diff minimal. (Deviation from a literal "runner sets walk_generation" reading; behavior-equivalent and covered by a dedicated test.)
- **Witness-mode health absence:** in 35.2 the health section is not yet populated (that is 35.3), so every `in-flight` emit / per-node steps write logs a witness-mode lifecycle warning ("status=in-flight requires the health section"). This is the contract's intended staged-rollout behavior (violations LOG, never raise, without strict context) — not a defect. Accepted cost for v1; resolves when 35.3 lands heartbeats/health.
- **Atomic write:** temp file + `os.replace` with 5×20ms bounded retry; exhaustion logs-and-skips (returns False), never raises into the walk. Fault-injected via monkeypatched `os.replace` (deterministic) for both the retries-then-succeeds and always-fail-exhaustion branches (party-downgraded deterministic smoke; the concurrency hammer is deferred).
- **In-process lock:** one module-level `threading.Lock` per `trial_id` covers all writes (emit, section APIs, freshness ticks).
- **Both-walk goldens:** per the story spec's sanctioned fallback, a full live walk is too heavy for a hermetic unit; `_persist_envelope` is driven directly for every status transition, and reconcile-on-entry ordering is exercised through the three real entry points (each raises a status guard right after the reconcile emit, so the projection write is observable without a paid walk). Assembler unit goldens additionally cover every pause class and section.

## Test results

- New suite (28 tests): **28 passed** (`test_operator_surface_assembler.py` 15, `test_runner_projection_emission.py` 8, `test_next_action.py` 5).
- 35.1 contract pins/parity (`test_operator_surface_shape_pin.py`, `test_operator_surface_parity.py`): **107 passed**.
- Orchestrator regression (`tests/unit/marcus/orchestrator` + `test_provider_batch_wait_pause.py`): **191 passed**.
- Block-mode consumers (`tests/test_run_hud.py`, `tests/test_progress_map.py`): **passed** (2 skips = 35.0 dispositions).
- `ruff check` on all new/changed files: **All checks passed**.
- `lint-imports`: **17 kept, 0 broken** (incl. HUD1 contract).
- `check_pipeline_manifest_lockstep.py`: **exit 0** (trace `reports/dev-coherence/2026-07-11-2144/...PASS.yaml`).

## Pre-existing failure (NOT introduced by 35.2)

`tests/integration/gates/test_resume_api_authority.py::test_no_unauthorized_callers` fails, flagging `app/marcus/cli/marcus_interlocutor.py` and `app/marcus/cli/marcus_spoc.py` — neither touched by this story. Confirmed it fails identically with the 35.2 runner change stashed. `next_action.py` builds command STRINGS only and never constructs `OperatorVerdict`, so it is not an offender.

## Deferred (filed to inventory follow-on)

- Concurrency-hammer test for replace-under-open-reader (party-downgraded; deterministic smoke shipped here).
- Health section population + witness-warning quieting arrives with 35.3.
