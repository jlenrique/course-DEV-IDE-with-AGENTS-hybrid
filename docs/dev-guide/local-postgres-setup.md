# Local Postgres Setup (Slab 1)

This migration uses a native local Postgres 15+ install.

No Docker or container runtime is required.

## One-Time Install

Install Postgres 15+ using your platform-native installer:

- Windows: EDB installer (interactive) — or `winget` unattended (recommended; see below)
- macOS: `brew install postgresql@15`
- Linux: distro package for Postgres 15+

Ensure `psql` is on `PATH`.

### Windows — unattended install via winget (recommended for first-trial setup)

Verified path on a clean Windows 11 machine (2026-04-28, first tracked trial setup):

```powershell
winget install -e --id PostgreSQL.PostgreSQL.17 --silent --accept-package-agreements --accept-source-agreements --override "--mode unattended --unattendedmodeui none --superpassword postgres --servicename postgresql-x64-17 --servicepassword postgres --serverport 5432 --enable-components server,commandlinetools"
```

Notes:
- Sets the `postgres` superuser password to `postgres` for local development. Override `--superpassword` if you prefer a different value, but remember to use that password in the bootstrap step below (the `user:pass` role created by `init_postgres.sql` is unaffected).
- Installs PostgreSQL 17 (within "15+" range). For 18, swap the package id to `PostgreSQL.PostgreSQL.18`.
- After install, the Windows service `postgresql-x64-17` auto-starts and binds `0.0.0.0:5432`. Verify with:
  ```powershell
  Get-Service -Name 'postgresql*'
  netstat -an | Select-String ":5432.*LISTENING"
  ```
- `psql.exe` lands at `C:\Program Files\PostgreSQL\17\bin\psql.exe`. Add `C:\Program Files\PostgreSQL\17\bin` to PATH for shorter invocation, or call the full path inline (the bootstrap example below uses the full path so it works without a PATH change).

## Bootstrap

1. Ensure `.env` contains:
   - `DATABASE_URL=postgresql://user:pass@localhost:5432/course_dev_ide_migration`
2. Run as the `postgres` superuser (the `user` role created by the script does not exist yet):

   **Linux / macOS:**
   ```bash
   PGPASSWORD=postgres psql -U postgres -h localhost -d postgres -f scripts/dev/init_postgres.sql
   ```

   **Windows (cmd / PowerShell with `psql` not on PATH):**
   ```bash
   PGPASSWORD=postgres "/c/Program Files/PostgreSQL/17/bin/psql.exe" -U postgres -h localhost -d postgres -f scripts/dev/init_postgres.sql
   ```

The script is idempotent and safe to run repeatedly.

## Verify

```bash
psql "$DATABASE_URL" -c "SELECT version();"
```

Expected: Postgres version is 15 or higher.

For Python-side verification (matches what the production-trial-playbook §1.4 runs), see [`docs/operator/production-trial-playbook.md`](../operator/production-trial-playbook.md) §1.4 — note that the check loads `DATABASE_URL` from `.env` via `python-dotenv` because a bare `python -c` does **not** auto-load `.env`.

## Checkpoint retention + cleanup (Story 1.5)

LangGraph checkpoints are written via `langgraph-checkpoint-postgres` into the
`checkpoints` table of the bootstrap database. Without cleanup the table grows
unbounded under single-operator usage. The policy + CLI below let operators
manage retention without ad-hoc SQL.

### Policy

The retention policy is data-driven, shipped at
[`state/config/retention-policy.yaml`](../../state/config/retention-policy.yaml).
Defaults:

- `max_thread_age_days: 30` — threads older than this are eligible for cleanup
- `cleanup_cron_hint: "0 3 * * *"` — recommended cadence (daily at 03:00 local time)
- `retain_completed: false` — completed threads older than the age bar are deleted
- `retain_failed: true` — failed threads are kept indefinitely for forensic value

`cleanup_cron_hint` is **documentation-only**. `app.runtime` does NOT
self-schedule (D3 discipline — the same tamper-evidence stance that forbids
`app.gates.**` from importing schedulers). The operator implements the cadence
externally via OS-level cron or Task Scheduler.

### CLI

```bash
# Preview what would be deleted — no DB mutation.
python -m app.runtime.cleanup_threads --dry-run

# Actually delete eligible threads.
python -m app.runtime.cleanup_threads --apply
```

Both commands print the active policy summary + the deletion count. Exit 0 on
success; exit 1 on `DATABASE_URL` unset or Postgres-unreachable.

### Recommended cron pattern (operator-owned)

Example crontab entry matching the default `cleanup_cron_hint`:

```cron
0 3 * * * cd /path/to/repo && /path/to/.venv/bin/python -m app.runtime.cleanup_threads --apply
```

Windows Task Scheduler: run the same command daily at 03:00 with the working
directory set to the repo root and the Python interpreter pointing at
`.venv\Scripts\python.exe`.

### Performance

NFR-P3 requires checkpoint writes to complete within 500ms at single-operator
volume. The `tests/performance/runtime/test_checkpoint_write_latency.py` probe
writes 100 checkpoints, discards the first 10 as warmup, and asserts p95 over
samples 11-100 stays within budget. If the probe fails, see the Completion
Notes of Story 1.5 for the baseline distribution.
