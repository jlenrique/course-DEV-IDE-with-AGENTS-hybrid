"""`app.runtime.cleanup_threads` — operator-invoked checkpoint cleanup (AC-1.5-C/D).

Queries the `checkpoints` table (populated by `langgraph-checkpoint-postgres`)
for threads older than `RetentionPolicy.max_thread_age_days`, honors the
`retain_completed` / `retain_failed` flags, and deletes matching threads in a
single transaction.

Operator-invoked only — `app.runtime` does NOT self-schedule (D3 discipline).
The CLI (`python -m app.runtime.cleanup_threads --dry-run` or `--apply`)
prints the policy summary + deletion count and exits 0 on success, 1 on
Postgres-unreachable or other named error surface.

## Metadata contract (consumed by the cleanup SQL)

The cleanup SELECT expects two tags on the most recent checkpoint row per
thread's `metadata` JSONB column:

- `metadata->>'status'` — one of `"completed"`, `"failed"`, `"running"`, or any
  other string. The retain_completed / retain_failed flags filter on the first
  two; every other status is treated as eligible-for-deletion when old enough.
- `metadata->>'updated_at'` (or `metadata->>'created_at'` as fallback) — an
  ISO-8601 timestamp string parseable by Postgres `timestamptz` cast.

Graphs that persist checkpoints are expected to write these tags via
`CheckpointMetadata` / `metadata.writes` when the graph transitions to a
terminal node. Slab 2 specialist scaffolds + Slab 3 Marcus orchestration will
each own their own `status` writes; Slab 1 ships the consumer contract only.
Checkpoints without these tags are retained (SQL filters `ts IS NOT NULL`).
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import psycopg

from app.runtime.retention_policy import DEFAULT_POLICY_PATH, RetentionPolicy, load_policy


@dataclass(frozen=True)
class CleanupResult:
    """Outcome of a single `cleanup()` invocation."""

    deleted_count: int
    dry_run: bool
    policy_version: str


# The `langgraph-checkpoint-postgres` `checkpoints` table shape is:
#   thread_id text, checkpoint_ns text, checkpoint_id text, parent_checkpoint_id text,
#   type text, checkpoint jsonb, metadata jsonb, ...
# `metadata->>'status'` is the status tag updated by the graph at terminal nodes.
# Latest checkpoint per thread determines the thread's "age."
_SELECT_CANDIDATES_SQL = """
WITH latest_per_thread AS (
    SELECT DISTINCT ON (thread_id)
        thread_id,
        metadata,
        COALESCE(
            (metadata->>'updated_at')::timestamptz,
            (metadata->>'created_at')::timestamptz
        ) AS ts
    FROM checkpoints
    ORDER BY thread_id, checkpoint_id DESC
)
SELECT thread_id, COALESCE(metadata->>'status', 'unknown') AS status
FROM latest_per_thread
WHERE ts IS NOT NULL
  AND ts < NOW() - (%s || ' days')::interval;
"""

_DELETE_THREADS_SQL = "DELETE FROM checkpoints WHERE thread_id = ANY(%s);"


def _threads_to_delete(
    candidates: list[tuple[str, str]],
    policy: RetentionPolicy,
) -> list[str]:
    """Apply retain_completed / retain_failed flags to candidate threads."""
    to_delete: list[str] = []
    for thread_id, status in candidates:
        if status == "completed" and policy.retain_completed:
            continue
        if status == "failed" and policy.retain_failed:
            continue
        to_delete.append(thread_id)
    return to_delete


def cleanup(
    conn: psycopg.Connection,
    policy: RetentionPolicy,
    *,
    dry_run: bool = False,
    policy_version: str = "1.0",
) -> CleanupResult:
    """Execute the cleanup query against the open Postgres connection.

    Args:
        conn: Open `psycopg.Connection`. Caller owns the connection lifecycle.
        policy: Loaded `RetentionPolicy`.
        dry_run: When True, identifies but does NOT delete threads.
        policy_version: String stamped into `CleanupResult` for logging.

    Returns:
        `CleanupResult` with `deleted_count` (0 on dry_run with no candidates).
    """
    with conn.cursor() as cur:
        cur.execute(_SELECT_CANDIDATES_SQL, (str(policy.max_thread_age_days),))
        candidates = [(row[0], row[1]) for row in cur.fetchall()]

    to_delete = _threads_to_delete(candidates, policy)

    if not to_delete or dry_run:
        return CleanupResult(
            deleted_count=len(to_delete),
            dry_run=dry_run,
            policy_version=policy_version,
        )

    with conn.cursor() as cur:
        cur.execute(_DELETE_THREADS_SQL, (to_delete,))
    conn.commit()
    return CleanupResult(
        deleted_count=len(to_delete),
        dry_run=False,
        policy_version=policy_version,
    )


# ------------------------------------------------------------------ CLI


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m app.runtime.cleanup_threads",
        description="Operator-invoked checkpoint cleanup (FR5).",
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Report what would be deleted.")
    mode.add_argument("--apply", action="store_true", help="Actually delete eligible threads.")
    parser.add_argument(
        "--policy-path",
        type=Path,
        default=None,
        help=f"Override retention policy YAML (default: {DEFAULT_POLICY_PATH}).",
    )
    return parser


def _print_policy_summary(policy: RetentionPolicy) -> None:
    print("Retention policy:")
    print(f"  max_thread_age_days: {policy.max_thread_age_days}")
    print(f"  cleanup_cron_hint:   {policy.cleanup_cron_hint!r}")
    print(f"  retain_completed:    {policy.retain_completed}")
    print(f"  retain_failed:       {policy.retain_failed}")


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    policy = load_policy(args.policy_path)
    _print_policy_summary(policy)

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL env var not set.", file=sys.stderr)
        return 1

    try:
        with psycopg.connect(database_url, connect_timeout=2) as conn:
            result = cleanup(conn, policy, dry_run=args.dry_run)
    except psycopg.OperationalError as exc:
        print(f"ERROR: Postgres connection failed: {exc}", file=sys.stderr)
        return 1

    mode_label = "dry-run" if result.dry_run else "apply"
    print(f"cleanup {mode_label}: {result.deleted_count} thread(s) eligible.")
    return 0


if __name__ == "__main__":  # pragma: no cover — exercised via CLI integration test
    sys.exit(main())


__all__ = ["CleanupResult", "cleanup", "main"]
