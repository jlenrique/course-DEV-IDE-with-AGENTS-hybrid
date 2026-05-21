"""Ledger query helpers."""

from __future__ import annotations

import os
from collections import defaultdict
from uuid import UUID

import psycopg

from app.ledger.events import LedgerEventAdapter, SanctumMutationLedgerEvent


def _resolve_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL env var not set")
    return database_url


def _open_connection(
    conn: psycopg.Connection | None,
    database_url: str | None,
) -> tuple[psycopg.Connection, bool]:
    if conn is not None:
        return conn, False
    return psycopg.connect(database_url or _resolve_database_url()), True


def _deserialize_rows(rows: list[tuple]) -> list[object]:
    events: list[object] = []
    for event_id, trial_id, gate_id, kind, payload, created_at in rows:
        raw = {
            "event_id": str(event_id),
            "trial_id": str(trial_id),
            "gate_id": gate_id,
            "kind": kind,
            "created_at": created_at.isoformat(),
            **payload,
        }
        events.append(LedgerEventAdapter.validate_python(raw))
    return events


def reject_rate_per_gate(
    trial_id: UUID | str,
    *,
    conn: psycopg.Connection | None = None,
    database_url: str | None = None,
) -> dict[str, float]:
    """Return per-gate reject rates for one trial."""
    active_conn, owns = _open_connection(conn, database_url)
    try:
        with active_conn.cursor() as cur:
            cur.execute(
                """
                SELECT gate_id, payload->>'verb'
                FROM ledger_events
                WHERE trial_id = %s AND kind = 'verdict';
                """,
                (trial_id,),
            )
            rows = cur.fetchall()
        totals: dict[str, int] = defaultdict(int)
        rejects: dict[str, int] = defaultdict(int)
        for gate_id, verb in rows:
            totals[gate_id] += 1
            if verb == "reject":
                rejects[gate_id] += 1
        return {
            gate_id: rejects[gate_id] / totals[gate_id]
            for gate_id in sorted(totals)
        }
    finally:
        if owns:
            active_conn.close()


def gate_inventory(
    trial_id: UUID | str,
    *,
    conn: psycopg.Connection | None = None,
    database_url: str | None = None,
) -> list[str]:
    """Return the distinct verdict gate ids fired in one trial."""
    active_conn, owns = _open_connection(conn, database_url)
    try:
        with active_conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT gate_id
                FROM ledger_events
                WHERE trial_id = %s AND kind = 'verdict'
                ORDER BY gate_id;
                """,
                (trial_id,),
            )
            return [row[0] for row in cur.fetchall()]
    finally:
        if owns:
            active_conn.close()


def sanctum_mutations(
    trial_id: UUID | str,
    *,
    conn: psycopg.Connection | None = None,
    database_url: str | None = None,
) -> list[SanctumMutationLedgerEvent]:
    """Return sanctum mutation events for one trial."""
    active_conn, owns = _open_connection(conn, database_url)
    try:
        with active_conn.cursor() as cur:
            cur.execute(
                """
                SELECT event_id, trial_id, gate_id, kind, payload, created_at
                FROM ledger_events
                WHERE trial_id = %s AND kind = 'sanctum_mutation'
                ORDER BY created_at;
                """,
                (trial_id,),
            )
            rows = cur.fetchall()
        return [
            event
            for event in _deserialize_rows(rows)
            if isinstance(event, SanctumMutationLedgerEvent)
        ]
    finally:
        if owns:
            active_conn.close()


__all__ = ["gate_inventory", "reject_rate_per_gate", "sanctum_mutations"]
