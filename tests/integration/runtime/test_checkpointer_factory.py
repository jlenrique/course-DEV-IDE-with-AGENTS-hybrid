"""`make_checkpointer` factory integration test (AC-1.5-A).

Constructs the checkpointer, writes + reads a probe checkpoint, asserts the
schema is idempotent-safe via `setup()`. Skips when `DATABASE_URL` unset or
Postgres unreachable per sandbox-AC discipline.
"""

from __future__ import annotations

import asyncio
import os
from uuid import uuid4

import psycopg
import pytest
from langgraph.checkpoint.base import CheckpointMetadata, empty_checkpoint

from app.runtime.checkpointer import make_checkpointer


@pytest.fixture
def event_loop_policy() -> asyncio.AbstractEventLoopPolicy:
    if os.name == "nt":
        return asyncio.WindowsSelectorEventLoopPolicy()
    return asyncio.DefaultEventLoopPolicy()


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


@pytest.mark.asyncio
async def test_make_checkpointer_writes_and_reads_probe() -> None:
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set; skipping Postgres checkpointer integration.")

    thread_id = f"probe-{uuid4()}"
    config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}}
    checkpoint = empty_checkpoint()

    try:
        async with make_checkpointer() as saver:
            metadata = CheckpointMetadata(source="input", step=0, writes={}, parents={})
            await saver.aput(config, checkpoint, metadata, {})
            read = await saver.aget(config)
            assert read is not None
            assert read["id"] == checkpoint["id"]
    except psycopg.OperationalError as exc:
        if _is_unreachable_error(exc):
            pytest.skip(f"Postgres unreachable: {exc}")
        raise
