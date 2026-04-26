"""Postgres-backed ledger emitter."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from uuid import UUID

import psycopg
from pydantic import BaseModel, ConfigDict, Field

from app.ledger.events import LedgerEvent, LedgerEventAdapter

LOGGER = logging.getLogger(__name__)
_LEDGER_EMISSION_FAILURES_TOTAL = 0


class EmissionResult(BaseModel):
    """Outcome of one ledger emission attempt."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    status: str = Field(..., min_length=1)
    event_id: UUID | None
    idempotency_key: str = Field(..., min_length=1)
    reason: str | None = None


def get_ledger_emission_failures_total() -> int:
    return _LEDGER_EMISSION_FAILURES_TOTAL


def reset_ledger_counters() -> None:
    global _LEDGER_EMISSION_FAILURES_TOTAL
    _LEDGER_EMISSION_FAILURES_TOTAL = 0


def _schema_path() -> Path:
    return Path(__file__).resolve().with_name("schema.sql")


def resolve_database_url() -> str:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL env var not set")
    return database_url


def ensure_ledger_schema(conn: psycopg.Connection) -> None:
    """Create the ledger schema if it does not exist."""
    sql = _schema_path().read_text(encoding="utf-8")
    with conn.cursor() as cur:
        cur.execute(sql)
    conn.commit()


def _load_existing_event_id(
    conn: psycopg.Connection,
    idempotency_key: str,
) -> UUID | None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT event_id FROM ledger_events WHERE idempotency_key = %s;",
            (idempotency_key,),
        )
        row = cur.fetchone()
    return row[0] if row is not None else None


def emit_ledger_event(
    event: LedgerEvent,
    *,
    conn: psycopg.Connection | None = None,
    database_url: str | None = None,
) -> EmissionResult:
    """Insert one ledger event or no-op on an existing idempotency key."""
    global _LEDGER_EMISSION_FAILURES_TOTAL

    normalized = LedgerEventAdapter.validate_python(event)
    key = normalized.idempotency_key()
    owns_connection = conn is None
    active_conn = conn

    try:
        if active_conn is None:
            active_conn = psycopg.connect(database_url or resolve_database_url())
        ensure_ledger_schema(active_conn)
        existing_event_id = _load_existing_event_id(active_conn, key)
        if existing_event_id is not None:
            return EmissionResult(
                status="duplicate",
                event_id=existing_event_id,
                idempotency_key=key,
            )

        payload = json.dumps(normalized.payload(), sort_keys=True, separators=(",", ":"))
        with active_conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO ledger_events (
                    event_id, trial_id, gate_id, kind, payload, idempotency_key, created_at
                ) VALUES (%s, %s, %s, %s, %s::jsonb, %s, %s);
                """,
                (
                    normalized.event_id,
                    normalized.trial_id,
                    normalized.gate_id,
                    normalized.kind,
                    payload,
                    key,
                    normalized.created_at,
                ),
            )
        active_conn.commit()
        return EmissionResult(
            status="inserted",
            event_id=normalized.event_id,
            idempotency_key=key,
        )
    except (psycopg.OperationalError, RuntimeError) as exc:
        _LEDGER_EMISSION_FAILURES_TOTAL += 1
        LOGGER.warning("ledger emission failed: %s", exc)
        return EmissionResult(
            status="failed",
            event_id=None,
            idempotency_key=key,
            reason=str(exc),
        )
    finally:
        if owns_connection and active_conn is not None:
            active_conn.close()


__all__ = [
    "EmissionResult",
    "emit_ledger_event",
    "ensure_ledger_schema",
    "get_ledger_emission_failures_total",
    "reset_ledger_counters",
]
