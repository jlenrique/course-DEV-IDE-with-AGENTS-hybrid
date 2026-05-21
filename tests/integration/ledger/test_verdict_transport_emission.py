from __future__ import annotations

from uuid import UUID

from app.gates.resume_api import build_transport_response
from app.ledger.emitter import EmissionResult
from app.ledger.events import VerdictLedgerEvent
from tests.unit.gates._helpers import sample_verdict


def test_build_transport_response_emits_typed_verdict_event(
    monkeypatch,
) -> None:
    captured: list[VerdictLedgerEvent] = []

    def _record(event):
        captured.append(event)
        return EmissionResult(
            status="inserted",
            event_id=event.event_id,
            idempotency_key=event.idempotency_key(),
        )

    monkeypatch.setattr("app.ledger.emitter.emit_ledger_event", _record)

    verdict = sample_verdict(trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"))
    response = build_transport_response(
        command=type("CommandStub", (), {"resume": {"verb": "approve"}})(),
        verdict=verdict,
        transport_kind="cli",
    )

    assert response["ledger_event"]["kind"] == "verdict"
    assert len(captured) == 1
    assert captured[0].gate_id == "G1"
    assert captured[0].verb == "approve"
    assert captured[0].transport_kind == "cli"
