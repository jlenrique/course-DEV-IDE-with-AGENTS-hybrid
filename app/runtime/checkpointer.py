"""`app.runtime.checkpointer` — `AsyncPostgresSaver` factory (AC-1.5-A).

Single entrypoint `make_checkpointer()` that reads `DATABASE_URL` from env,
constructs an `AsyncPostgresSaver` per the LangGraph SDK pattern, and ensures
the `checkpoints` table schema is present via `setup()` (idempotent).

The factory returns an async context manager so callers use it with
`async with make_checkpointer() as cp:` — this matches `AsyncPostgresSaver`'s
native `from_conn_string` API shape.
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover — type-checker only
    from collections.abc import AsyncIterator

    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver


class CheckpointerConfigError(RuntimeError):
    """Raised when `DATABASE_URL` is missing or the schema bootstrap fails."""


def resolve_database_url() -> str:
    """Return the `DATABASE_URL` env var or raise with a diagnostic message."""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise CheckpointerConfigError(
            "DATABASE_URL env var not set. See docs/dev-guide/local-postgres-setup.md "
            "for the bootstrap flow."
        )
    return url


def resolve_checkpointer_conninfo() -> str:
    """Return Postgres conninfo with a bounded connection timeout."""
    from psycopg.conninfo import make_conninfo

    return make_conninfo(resolve_database_url(), connect_timeout="2")


@asynccontextmanager
async def make_checkpointer() -> AsyncIterator[AsyncPostgresSaver]:
    """Async context manager yielding a ready-to-use `AsyncPostgresSaver`.

    Reads `DATABASE_URL`, opens the connection per LangGraph's
    `from_conn_string`, and calls `setup()` to ensure the `checkpoints` schema
    exists (idempotent — `setup()` is safe to call against a populated DB).

    Raises:
        CheckpointerConfigError: If `DATABASE_URL` is unset.
    """
    from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

    conn_string = resolve_checkpointer_conninfo()
    async with AsyncPostgresSaver.from_conn_string(conn_string) as saver:
        await saver.setup()
        yield saver


__all__ = [
    "CheckpointerConfigError",
    "make_checkpointer",
    "resolve_checkpointer_conninfo",
    "resolve_database_url",
]
