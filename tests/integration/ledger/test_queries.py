from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import UUID

import psycopg
import pytest

from app.ledger.emitter import emit_ledger_event, ensure_ledger_schema
from app.ledger.events import (
    build_override_ledger_event,
    build_sanctum_mutation_ledger_event,
    build_verdict_ledger_event,
)
from app.ledger.queries import gate_inventory, reject_rate_per_gate, sanctum_mutations
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


def _verdict(verb: str, gate_id: str, trial_id: UUID, verdict_id: str) -> OperatorVerdict:
    return OperatorVerdict.model_validate(
        {
            "verdict_id": verdict_id,
            "trial_id": str(trial_id),
            "verb": verb,
            "gate_id": gate_id,
            "card_id": "11111111-1111-4111-8111-111111111111",
            "operator_id": "juanl",
            "timestamp": "2026-04-26T12:02:00Z",
            "decision_card_digest": "a" * 64,
            "reject_reason": "fail" if verb == "reject" else None,
        }
    )


def test_queries_return_expected_shapes() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        pytest.skip("DATABASE_URL not set; skipping ledger Postgres integration.")

    trial_id = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    try:
        with psycopg.connect(database_url) as conn:
            ensure_ledger_schema(conn)
            emit_ledger_event(
                build_verdict_ledger_event(
                    _verdict("approve", "G2C", trial_id, "22222222-2222-4222-8222-222222222222"),
                    transport_kind="cli",
                ),
                conn=conn,
            )
            emit_ledger_event(
                build_verdict_ledger_event(
                    _verdict("reject", "G2C", trial_id, "33333333-3333-4333-8333-333333333333"),
                    transport_kind="cli",
                ),
                conn=conn,
            )
            emit_ledger_event(
                build_verdict_ledger_event(
                    _verdict("approve", "G3", trial_id, "44444444-4444-4444-8444-444444444444"),
                    transport_kind="http",
                ),
                conn=conn,
            )
            emit_ledger_event(
                build_override_ledger_event(
                    trial_id=trial_id,
                    node_id="04",
                    operator_id="juanl",
                    previous_model="gpt-5",
                    new_model="gpt-5-mini",
                    confirm_token="confirm-001",
                    phase="applied",
                ),
                conn=conn,
            )
            emit_ledger_event(
                build_sanctum_mutation_ledger_event(
                    trial_id=trial_id,
                    file_path="_bmad/memory/bmad-agent-cora/CAPABILITIES.md",
                    hash_before="aaaa",
                    hash_after="bbbb",
                    mutated_at=datetime(2026, 4, 26, 12, 3, tzinfo=UTC),
                ),
                conn=conn,
            )

            assert reject_rate_per_gate(trial_id, conn=conn) == {"G2C": 0.5, "G3": 0.0}
            assert gate_inventory(trial_id, conn=conn) == ["G2C", "G3"]
            mutations = sanctum_mutations(trial_id, conn=conn)
            assert len(mutations) == 1
            assert mutations[0].file_path.endswith("CAPABILITIES.md")

            with conn.cursor() as cur:
                cur.execute("DELETE FROM ledger_events WHERE trial_id = %s;", (trial_id,))
            conn.commit()
    except psycopg.OperationalError as exc:
        if _is_unreachable_error(exc):
            pytest.skip(f"Postgres unreachable: {exc}")
        raise
