# Local Postgres Setup (Slab 1)

This migration uses a native local Postgres 15+ install.

No Docker or container runtime is required.

## One-Time Install

Install Postgres 15+ using your platform-native installer:

- Windows: EDB installer
- macOS: `brew install postgresql@15`
- Linux: distro package for Postgres 15+

Ensure `psql` is on `PATH`.

## Bootstrap

1. Ensure `.env` contains:
   - `DATABASE_URL=postgresql://user:pass@localhost:5432/course_dev_ide_migration`
2. Run:

```bash
psql "$DATABASE_URL" -f scripts/dev/init_postgres.sql
```

The script is idempotent and safe to run repeatedly.

## Verify

```bash
psql "$DATABASE_URL" -c "SELECT version();"
```

Expected: Postgres version is 15 or higher.
