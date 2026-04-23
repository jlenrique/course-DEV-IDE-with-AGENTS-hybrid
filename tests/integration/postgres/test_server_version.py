import os

import psycopg
import pytest


def _is_unreachable_error(exc: psycopg.OperationalError) -> bool:
    text = str(exc).lower()
    markers = (
        "connection refused",
        "could not connect",
        "connection timed out",
        "timeout expired",
        "no route to host",
        "name or service not known",
        "temporary failure in name resolution",
    )
    return any(marker in text for marker in markers)


def test_postgres_server_version_is_15_or_newer() -> None:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL is not set; skipping Postgres version smoke test.")

    try:
        with psycopg.connect(database_url) as conn:
            assert conn.info.server_version >= 150000
    except psycopg.OperationalError as exc:
        if _is_unreachable_error(exc):
            pytest.skip(f"Postgres is unreachable at DATABASE_URL: {exc}")
        raise
