# Migration Story 1.1b: Package Layout + Postgres + Sanctum Fork Notice

Status: done

## Story

As a dev agent completing Slab 1 substrate scaffolding,
I want the Slab-1 package layout, Postgres bootstrap artifacts, harness canaries, and sanctum notices in place,
So that 1.1c+ can build on a real substrate with migration governance evidence.

## Acceptance Criteria Summary

- `scripts/dev/init_postgres.sql` exists and remains idempotent.
- `docs/dev-guide/local-postgres-setup.md` exists and documents native local Postgres setup (no Docker).
- SQL parse-only check runs via pure Python parser (`sqlparse`) and exits 0.
- `tests/integration/postgres/test_server_version.py` uses `psycopg`, asserts Postgres >= 15 when reachable, and skips when `DATABASE_URL` is unset/unreachable.
- Sanctum CLONE-FORK-NOTICE presence test passes.
- Harness canaries pass for `tests/end_to_end/test_harness_contract.py` and `tests/trial_replay/test_harness_contract.py`.
- Import smoke for `app.runtime`, `app.models`, `app.manifest`, `app.http`, and `app.mcp_server` succeeds.

## Review Findings

- [x] [Review] Clean layered review (Blind + Edge + Acceptance): 0 decision-needed, 0 patch, 0 defer, 0 dismissed requiring action.

## Dev Agent Record

### Verification Commands and Outcomes

- `python -m uv run --no-project --python .\.venv\Scripts\python.exe --with sqlparse python -c "<parse scripts/dev/init_postgres.sql>"`
  - Outcome: pass (`Parsed 7 SQL statements from scripts/dev/init_postgres.sql`).
- `python -m uv run --no-project --python .\.venv\Scripts\python.exe --with pytest --with "psycopg[binary]" pytest tests/integration/postgres/test_server_version.py -q`
  - Outcome: expected sandbox behavior (`1 skipped`).
- `python -m uv run --no-project --python .\.venv\Scripts\python.exe python -c "import app.runtime, app.models, app.manifest, app.http, app.mcp_server; print('ok')"`
  - Outcome: pass (`ok`).
- `python -m uv run --no-project --python .\.venv\Scripts\python.exe --with pytest pytest tests/integration/sanctum/test_clone_fork_notice_present.py -q`
  - Outcome: pass (`1 passed`).
- `python -m uv run --no-project --python .\.venv\Scripts\python.exe --with pytest pytest tests/end_to_end/test_harness_contract.py tests/trial_replay/test_harness_contract.py -q`
  - Outcome: pass (`2 passed`).

### Completion Notes

- `tests/integration/postgres/test_server_version.py` was added to satisfy AC-Postgres-A skip-on-unreachable behavior.
- AC-Postgres-B is operator-gated and remains pending operator evidence at story closure.

### File List

- `scripts/dev/init_postgres.sql`
- `docs/dev-guide/local-postgres-setup.md`
- `tests/integration/postgres/test_server_version.py`
- `tests/integration/sanctum/test_clone_fork_notice_present.py`
- `tests/end_to_end/test_harness_contract.py`
- `tests/trial_replay/test_harness_contract.py`
- `_bmad-output/implementation-artifacts/migration-1-1b-package-layout-postgres-sanctum-fork-notice.md`

