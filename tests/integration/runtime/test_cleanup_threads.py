"""`cleanup()` integration test (AC-1.5-C).

Populates fixture threads of varying ages + statuses into a live Postgres
`checkpoints` table, runs `cleanup(dry_run=True)`, asserts the expected
would-be-deleted count, runs `cleanup(dry_run=False)`, asserts removal.
Skips when DATABASE_URL unset or Postgres unreachable.
"""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import psycopg
import pytest

from app.runtime.cleanup_threads import cleanup
from app.runtime.retention_policy import RetentionPolicy


def _is_unreachable_error(exc: psycopg.OperationalError) -> bool:
    text = str(exc).lower()
    return any(
        marker in text
        for marker in (
            "connection refused",
            "could not connect",
            "connection timed out",
            "timeout expired",
            "no route to host",
            "name or service not known",
        )
    )


def _policy() -> RetentionPolicy:
    return RetentionPolicy(
        max_thread_age_days=30,
        cleanup_cron_hint="0 3 * * *",
        retain_completed=False,
        retain_failed=True,
    )


def _insert_thread_row(
    conn: psycopg.Connection,
    thread_id: str,
    status: str,
    updated_at: datetime,
) -> None:
    """Insert a minimal row that the cleanup SQL can reason about.

    langgraph-checkpoint-postgres writes its own schema via `setup()`. This test
    reuses that table shape; we just populate the `metadata` JSONB with the
    status + updated_at tags the SQL expects.
    """
    metadata = json.dumps(
        {"status": status, "updated_at": updated_at.isoformat()}
    )
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO checkpoints (
                thread_id, checkpoint_ns, checkpoint_id,
                parent_checkpoint_id, type, checkpoint, metadata
            ) VALUES (%s, '', %s, NULL, 'test', '{}'::jsonb, %s::jsonb);
            """,
            (thread_id, f"chk-{uuid4()}", metadata),
        )
    conn.commit()


def _ensure_checkpoints_table(conn: psycopg.Connection) -> None:
    """Invoke AsyncPostgresSaver.setup() via a sync helper to ensure the table exists."""
    import asyncio

    from app.runtime.checkpointer import make_checkpointer

    async def _bootstrap() -> None:
        async with make_checkpointer():
            pass  # setup() runs inside make_checkpointer()

    asyncio.run(_bootstrap())


def test_cleanup_dry_run_then_apply() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping cleanup integration.")

    try:
        _ensure_checkpoints_table(psycopg.connect(database_url, autocommit=True))
    except psycopg.OperationalError as exc:
        if _is_unreachable_error(exc):
            pytest.skip(f"Postgres unreachable: {exc}")
        raise

    old_ts = datetime.now(UTC) - timedelta(days=60)
    recent_ts = datetime.now(UTC) - timedelta(days=5)
    test_suffix = uuid4().hex[:8]
    fixtures = [
        (f"old-completed-{test_suffix}", "completed", old_ts),   # delete
        (f"old-failed-{test_suffix}", "failed", old_ts),         # retain (retain_failed=True)
        (f"recent-{test_suffix}", "running", recent_ts),         # not old enough
        (f"old-running-{test_suffix}", "running", old_ts),       # delete
    ]

    try:
        with psycopg.connect(database_url) as conn:
            for thread_id, status, ts in fixtures:
                _insert_thread_row(conn, thread_id, status, ts)

            dry = cleanup(conn, _policy(), dry_run=True)
            assert dry.dry_run is True
            # Only our fixture threads are deletable; filter by our test_suffix to isolate.
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT thread_id FROM checkpoints WHERE thread_id LIKE %s;",
                    (f"%-{test_suffix}",),
                )
                existing = {row[0] for row in cur.fetchall()}
            # Our two "old + not retained" fixtures are in the delete set; dry count ≥ 2.
            assert dry.deleted_count >= 2

            applied = cleanup(conn, _policy(), dry_run=False)
            assert applied.dry_run is False
            assert applied.deleted_count >= 2

            with conn.cursor() as cur:
                cur.execute(
                    "SELECT thread_id FROM checkpoints WHERE thread_id LIKE %s;",
                    (f"%-{test_suffix}",),
                )
                remaining = {row[0] for row in cur.fetchall()}
            # old-completed + old-running deleted; old-failed + recent retained.
            assert f"old-completed-{test_suffix}" not in remaining
            assert f"old-running-{test_suffix}" not in remaining
            assert f"old-failed-{test_suffix}" in remaining
            assert f"recent-{test_suffix}" in remaining

            # Cleanup the test_suffix fixtures we left behind (best effort).
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM checkpoints WHERE thread_id LIKE %s;",
                    (f"%-{test_suffix}",),
                )
            conn.commit()
            _ = existing  # retained for diagnostics if the suffix isolation ever fails
    except psycopg.OperationalError as exc:
        if _is_unreachable_error(exc):
            pytest.skip(f"Postgres unreachable: {exc}")
        raise
