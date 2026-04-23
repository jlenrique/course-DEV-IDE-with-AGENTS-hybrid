# Migration Story 1.5: Checkpoint Retention + Cleanup Policy

**Status:** ready-for-dev
**Sprint key:** 1-5-checkpoint-retention-cleanup
**Epic:** Slab 1 Substrate (migration Epic 1)
**Milestone anchored:** M1 — checkpoints survive ≥48hr operator-pause per FR4.
**Pts:** 2 | **Gate:** single | **K-target:** ~1.3×
**Parallel-eligible:** after 1.1b (depends on Postgres bootstrap only; no upstream code dep on 1.1c/1.2/1.3/1.4).

## Story

As a **dev agent landing checkpoint operational policy**,
I want **`langgraph-checkpoint-postgres` configured with a retention + cleanup policy (FR5: thread-old-than-N-days cleaned automatically; FR4: ≥48hr survival on active threads)**,
So that **Postgres doesn't grow unbounded under single-operator usage, NFR-P3 ≤500ms checkpoint write time is preserved, and operators have a documented policy for thread retention without ad-hoc cleanup**.

## Acceptance Criteria

All ACs dev-agent-executable. No operator-gated AC. Postgres-touching ACs follow sandbox-AC discipline (skip-on-unreachable via `psycopg`).

### AC-1.5-A — `app.runtime.checkpointer` factory

- **Given** 1.1a installed `langgraph-checkpoint-postgres` and 1.1b authored the `init_postgres.sql` bootstrap
- **When** the dev agent authors `app/runtime/checkpointer.py` exporting `make_checkpointer() -> AsyncPostgresSaver` that:
  - Reads `DATABASE_URL` from env
  - Instantiates `AsyncPostgresSaver(...)` per the LangGraph SDK pattern
  - Verifies the `checkpoints` table is present (via `psycopg`); creates it via `setup()` if absent (idempotent)
- **Then** `tests/integration/runtime/test_checkpointer_factory.py` constructs the checkpointer + writes a probe checkpoint + reads it back; skips with documented reason when `DATABASE_URL` unreachable.

### AC-1.5-B — Retention policy schema + YAML

- **Given** retention rules need to be data-driven
- **When** the dev agent authors:
  - `app/runtime/retention_policy.py` with `RetentionPolicy` Pydantic v2 model: `{max_thread_age_days: int, cleanup_cron_hint: str, retain_completed: bool, retain_failed: bool}` (`cron_hint` is documentation-only; actual scheduling is operator-side per D3 — `app.gates` may not import schedulers)
  - `state/config/retention-policy.yaml` with default values: `max_thread_age_days: 30`, `cleanup_cron_hint: "0 3 * * *"`, `retain_completed: false`, `retain_failed: true` (failed threads kept for forensic value)
- **Then** four-file-lockstep complete; YAML round-trips through the model; closed-enum-style cron-hint validation (regex check, not full cron parser).

### AC-1.5-C — `app.runtime.cleanup_threads` callable

- **Given** the retention policy is loaded
- **When** the dev agent authors `app/runtime/cleanup_threads.py` exporting `cleanup(checkpointer, policy: RetentionPolicy, dry_run: bool = False) -> CleanupResult` that:
  - Queries the `checkpoints` table for threads older than `max_thread_age_days` (filtered per `retain_completed` / `retain_failed` flags)
  - Deletes them in a single transaction (or returns the deletion count on `dry_run=True`)
  - Returns `CleanupResult(deleted_count, dry_run, policy_version)`
- **Then** `tests/integration/runtime/test_cleanup_threads.py` populates fixture threads of varying ages + statuses, runs `cleanup(dry_run=True)`, asserts the correct count would-be-deleted; runs `cleanup(dry_run=False)`, asserts they're gone; skips on unreachable Postgres.

### AC-1.5-D — Operator-facing CLI entry

- **Given** operators need to manually invoke cleanup (no auto-scheduling per D3)
- **When** the dev agent authors `python -m app.runtime.cleanup_threads --dry-run` and `python -m app.runtime.cleanup_threads --apply` CLI entry points
- **Then** the CLI prints the policy summary + the deletion count + dry-run-vs-apply mode; exit 0 on success, exit 1 on Postgres-unreachable (CLI's own behavior — operator-facing failure surface). **Test discipline (per Murat amendment 2026-04-22):** the pytest that exercises this CLI MUST `pytest.skip(...)` when `DATABASE_URL` is unreachable (sandbox-AC discipline applies to the test); the CLI's exit-1-on-unreachable behavior is only assertable when Postgres IS reachable but the connection fails for another reason (e.g., bad credentials in `DATABASE_URL`). Author both: (a) `tests/integration/runtime/test_cleanup_cli_smoke.py` that runs the CLI against a reachable Postgres + asserts exit 0 + parses the deletion count line; (b) `tests/integration/runtime/test_cleanup_cli_bad_url.py` that runs the CLI with a deliberately-bad `DATABASE_URL` env override + asserts exit 1 + asserts a named-error stderr line (skip both when `DATABASE_URL` unset).

### AC-1.5-E — NFR-P3 checkpoint-write latency probe

- **Given** NFR-P3 says checkpoint writes must complete within 500ms at single-operator volume
- **When** the dev agent authors `tests/performance/runtime/test_checkpoint_write_latency.py` that writes 100 checkpoints in sequence + computes the percentile distribution per Murat amendment 2026-04-22:
  1. **Single shared connection** across all 100 writes (use a pytest fixture; do NOT open a fresh connection per write — that measures connect-time, not write-time)
  2. **Discard the first 10 samples as warmup;** p95 is computed over samples 11–100 only (warmup effects: connection pool + JIT + Postgres autovacuum state; on a cold dev box the first 1–5 writes can be substantially slower than steady-state and skew p95 with only 100 samples)
  3. **Report the full percentile distribution** (p50 / p95 / p99 / max) in pytest output AND in the dev's Completion Notes — pass/fail alone is insufficient diagnostic data for NFR-P3 calibration if the bar is breached
- **Then** the test passes when Postgres is reachable AND p95 (over samples 11–100) ≤ 500ms; skips with documented reason when Postgres unreachable. If p95 > 500ms, the test fails AND the Completion Notes carry the full distribution for retro investigation (NFR-P3 violation requires root-cause analysis, not a budget bump).

### AC-1.5-F — Retention policy doc

- **Given** operators need to understand the policy
- **When** the dev agent extends `docs/dev-guide/local-postgres-setup.md` (from 1.1b) with a new section "Checkpoint retention + cleanup" describing the policy + CLI commands + recommended cron pattern (operator implements scheduling externally via OS-level cron / Task Scheduler)
- **Then** the doc section exists; commands are grep-able; cron pattern is operator-cookbook quality.

## Tasks / Subtasks

- [ ] **T1 — Read T1 Bundle** §1 (D3 HIL tamper-evidence — relevant because retention shouldn't auto-schedule), §2 (FR3, FR4, FR5, NFR-P3), §4 (sandbox-AC for psycopg/skip).
- [ ] **T2 — Use schema-story scaffold** for `RetentionPolicy`.
- [ ] **T3 — Author checkpointer factory** per AC-1.5-A.
- [ ] **T4 — Author retention schema + YAML** per AC-1.5-B.
- [ ] **T5 — Author cleanup callable + CLI** per AC-1.5-C and AC-1.5-D.
- [ ] **T6 — Author latency probe** per AC-1.5-E.
- [ ] **T7 — Author retention doc section** per AC-1.5-F.
- [ ] **T8 — Run validators + tests.**
- [ ] **T9 — Commit.** `feat(migration): Slab 1 Story 1.5 — checkpoint retention + cleanup policy`

## Dev Notes

### Why no auto-scheduling

D3 forbids `threading.Timer`, `apscheduler`, `schedule`, and `asyncio.sleep` (callable-level) in `app.gates.**` to prevent silent auto-approve paths. The same discipline is extended to `app.runtime.cleanup_threads` by convention: the cleanup CLI is operator-invoked (via OS-level cron or Task Scheduler), not auto-scheduled inside the Python process. This is a deliberate FR-discipline choice — single-operator self-hosted, operator owns the cadence.

### Postgres connection reuse

`psycopg.connect(DATABASE_URL)` per call is fine for the cleanup CLI (single-shot). For the integration test, share a connection across the populate + cleanup phases via a pytest fixture to avoid connection-overhead skew on the latency probe.

### Project Structure Notes

**New files:**
- `app/runtime/checkpointer.py`
- `app/runtime/retention_policy.py` — **Pydantic v2 model lives HERE per Winston amendment 2026-04-22** (operational-policy config, NOT graph state; does NOT live under `app/models/state/` alongside `RunState`/`OperatorVerdict`/etc., which is reserved for LangGraph state schema models)
- `app/runtime/cleanup_threads.py` (+ `__main__.py`)
- `state/config/retention-policy.yaml`
- Four-file-lockstep tests + fixtures for `RetentionPolicy` (model + validator + tests + golden fixture, all under `app/runtime/` and `tests/unit/runtime/` — NOT under `app/models/state/`)
- `tests/integration/runtime/test_checkpointer_factory.py`
- `tests/integration/runtime/test_cleanup_threads.py`
- `tests/integration/runtime/test_cleanup_cli_smoke.py` (per AC-1.5-D — reachable-Postgres + exit-0 assertion)
- `tests/integration/runtime/test_cleanup_cli_bad_url.py` (per AC-1.5-D — bad-URL + exit-1 + named-error assertion)
- `tests/performance/runtime/test_checkpoint_write_latency.py`

**Modified:**
- `docs/dev-guide/local-postgres-setup.md` (append retention section)

## References

- Bundle: [Set-A T1 Context Bundle](../planning-artifacts/slab1-story-set-A-t1-bundle.md)
- Architecture D3 (HIL tamper-evidence — informs no-auto-scheduling rule)
- PRD FR3, FR4, FR5, NFR-P3

## Dev Agent Record

_(placeholder)_
