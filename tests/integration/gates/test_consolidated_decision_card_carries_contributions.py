from __future__ import annotations

from uuid import UUID

from app.gates.party_mode_as_interrupt import build_party_mode_decision_card


def test_consolidated_decision_card_carries_contributions() -> None:
    card = build_party_mode_decision_card(
        contributions=[
            {
                "contribution_id": "33333333-3333-4333-8333-333333333333",
                "persona": "winston",
                "payload": {"finding": "architecture first"},
                "submitted_at": "2026-04-26T12:00:00Z",
                "trace_link": "https://smith.langchain.com/traces/trace-123",
            }
        ],
        gate_id="G-PARTY",
        trial_id=UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
    )

    assert len(card.meta.party_mode_contributions) == 1
    assert card.meta.consolidated_at is not None
    assert card.meta.party_mode_contributions[0].persona == "winston"
