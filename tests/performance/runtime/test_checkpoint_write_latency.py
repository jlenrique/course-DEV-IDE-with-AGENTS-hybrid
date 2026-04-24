"""NFR-P3 checkpoint-write latency probe (AC-1.5-E).

Writes 100 checkpoints in sequence via a single shared AsyncPostgresSaver
connection, discards the first 10 samples as warmup, computes the p50/p95/p99/max
percentile distribution over samples 11-100, and asserts p95 ≤ 500ms.

Per Murat's amendment 2026-04-22:
1. Single shared connection across all 100 writes (pytest fixture; fresh
   connection per write measures connect-time, not write-time).
2. Warmup discard: samples 1-10 excluded from p95 aggregation (connection
   pool + JIT + Postgres autovacuum warm up during the first few writes).
3. Full distribution reported in pytest output for diagnostic completeness.

Skips when DATABASE_URL unset or Postgres unreachable.
"""

from __future__ import annotations

import os
import statistics
import time
from uuid import uuid4

import psycopg
import pytest
from langgraph.checkpoint.base import CheckpointMetadata, empty_checkpoint

from app.runtime.checkpointer import make_checkpointer

N_WRITES = 100
WARMUP_DISCARD = 10
P95_BUDGET_MS = 500.0


def _is_unreachable_error(exc: psycopg.OperationalError) -> bool:
    text = str(exc).lower()
    return any(
        marker in text
        for marker in (
            "connection refused",
            "could not connect",
            "connection timed out",
            "timeout expired",
        )
    )


@pytest.mark.asyncio
async def test_checkpoint_write_latency_p95_under_500ms() -> None:
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("DATABASE_URL not set; skipping NFR-P3 latency probe.")

    thread_id = f"latency-probe-{uuid4()}"
    samples_ms: list[float] = []

    try:
        async with make_checkpointer() as saver:
            for i in range(N_WRITES):
                checkpoint = empty_checkpoint()
                metadata = CheckpointMetadata(source="input", step=i, writes={}, parents={})
                config = {"configurable": {"thread_id": thread_id, "checkpoint_ns": ""}}
                start = time.perf_counter()
                await saver.aput(config, checkpoint, metadata, {})
                elapsed_ms = (time.perf_counter() - start) * 1000.0
                samples_ms.append(elapsed_ms)
    except psycopg.OperationalError as exc:
        if _is_unreachable_error(exc):
            pytest.skip(f"Postgres unreachable: {exc}")
        raise

    steady = samples_ms[WARMUP_DISCARD:]
    assert len(steady) == N_WRITES - WARMUP_DISCARD

    p50 = statistics.median(steady)
    p95 = statistics.quantiles(steady, n=20)[18]  # 95th percentile over 20 quantiles
    p99 = statistics.quantiles(steady, n=100)[98]
    max_ms = max(steady)

    distribution = (
        f"NFR-P3 checkpoint-write latency (samples {WARMUP_DISCARD + 1}-{N_WRITES}):\n"
        f"  p50: {p50:.2f}ms\n"
        f"  p95: {p95:.2f}ms\n"
        f"  p99: {p99:.2f}ms\n"
        f"  max: {max_ms:.2f}ms"
    )
    print(distribution)

    assert p95 <= P95_BUDGET_MS, (
        f"NFR-P3 VIOLATION: p95 exceeded {P95_BUDGET_MS}ms budget.\n{distribution}\n"
        f"Full samples (steady-state): {[round(s, 2) for s in steady]}"
    )
