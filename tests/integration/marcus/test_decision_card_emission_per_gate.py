from __future__ import annotations

import pytest

from marcus.orchestrator.m3_trial import run_local_m3_trial


@pytest.mark.parametrize("gate_id", ["G1", "G2C", "G3", "G4"])
def test_decision_card_emitted_for_each_required_gate(gate_id: str, monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    envelope = run_local_m3_trial()
    event = next(record for record in envelope.gate_events if record.gate_id == gate_id)

    assert event.card_id
    assert len(event.decision_card_digest) == 64
    assert event.resume_payload["gate_id"] == gate_id
