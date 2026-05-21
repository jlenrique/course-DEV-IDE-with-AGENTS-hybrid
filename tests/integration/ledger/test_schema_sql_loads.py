from __future__ import annotations

import os

import psycopg
import pytest

from app.ledger.emitter import ensure_ledger_schema


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
            "temporary failure in name resolution",
        )
    )


def test_schema_sql_loads() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping ledger schema integration.")

    try:
        with psycopg.connect(database_url) as conn:
            ensure_ledger_schema(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = 'ledger_events';
                    """
                )
                assert cur.fetchone() == (1,)
    except psycopg.OperationalError as exc:
        if _is_unreachable_error(exc):
            pytest.skip(f"Postgres unreachable: {exc}")
        raise
