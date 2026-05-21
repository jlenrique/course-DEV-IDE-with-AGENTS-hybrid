from __future__ import annotations

import os
from uuid import UUID

import psycopg
import pytest

from app.ledger.emitter import emit_ledger_event, ensure_ledger_schema
from app.ledger.events import build_verdict_ledger_event
from app.models.state.operator_verdict import OperatorVerdict


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


def _verdict(trial_id: UUID) -> OperatorVerdict:
    return OperatorVerdict.model_validate(
        {
            "verdict_id": "22222222-2222-4222-8222-222222222222",
            "trial_id": str(trial_id),
            "verb": "approve",
            "gate_id": "G2C",
            "card_id": "11111111-1111-4111-8111-111111111111",
            "operator_id": "juanl",
            "timestamp": "2026-04-26T12:02:00Z",
            "decision_card_digest": "a" * 64,
        }
    )


def test_emit_ledger_event_idempotent() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping ledger Postgres integration.")

    trial_id = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    event = build_verdict_ledger_event(_verdict(trial_id), transport_kind="cli")
    try:
        with psycopg.connect(database_url) as conn:
            ensure_ledger_schema(conn)
            first = emit_ledger_event(event, conn=conn)
            second = emit_ledger_event(event, conn=conn)
            assert first.status == "inserted"
            assert second.status == "duplicate"
            assert second.event_id == first.event_id
            with conn.cursor() as cur:
                cur.execute("DELETE FROM ledger_events WHERE trial_id = %s;", (trial_id,))
            conn.commit()
    except psycopg.OperationalError as exc:
        if _is_unreachable_error(exc):
            pytest.skip(f"Postgres unreachable: {exc}")
        raise
