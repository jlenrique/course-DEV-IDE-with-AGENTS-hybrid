from __future__ import annotations

from marcus.orchestrator.m3_trial import run_local_m3_trial


def test_edit_verb_propagates_to_downstream_payload(monkeypatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    envelope = run_local_m3_trial()
    gate_event = next(event for event in envelope.gate_events if event.gate_id == "G2C")

    assert gate_event.verdict_verb == "edit"
    assert envelope.downstream_payloads["09"]["operator_edits"][0]["change_summary"].startswith(
        "Tighten evidence chain"
    )
    verdict_events = [event for event in envelope.ledger_events if event["kind"] == "verdict"]
    assert any(event["verb"] == "edit" for event in verdict_events)
