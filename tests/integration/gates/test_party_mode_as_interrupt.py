from __future__ import annotations

import importlib
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.gates.resume_api import clear_resume_registry

party_mode_module = importlib.import_module("app.gates.party_mode_as_interrupt")


@pytest.fixture(autouse=True)
def _clear_registry() -> None:
    clear_resume_registry()


def test_party_mode_as_interrupt_full_flow(monkeypatch: pytest.MonkeyPatch) -> None:
    trial_id = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")

    def _resume_payload(payload: dict[str, object]) -> dict[str, object]:
        card = payload["decision_card"]
        return {
            "verdict_id": "22222222-2222-4222-8222-222222222222",
            "trial_id": str(trial_id),
            "verb": "approve",
            "gate_id": "G-PARTY",
            "card_id": card["card_id"],
            "operator_id": "juanl",
            "timestamp": "2026-04-26T12:02:00Z",
            "decision_card_digest": payload["decision_card_digest"],
        }

    monkeypatch.setattr(
        party_mode_module,
        "interrupt",
        _resume_payload,
    )

    card = party_mode_module.party_mode_as_interrupt(
        [
            {
                "contribution_id": "33333333-3333-4333-8333-333333333333",
                "persona": "winston",
                "payload": {"finding": "keep architecture explicit"},
                "submitted_at": "2026-04-26T12:00:00Z",
                "trace_link": "https://smith.langchain.com/traces/trace-123",
            },
            {
                "contribution_id": "44444444-4444-4444-8444-444444444444",
                "persona": "murat",
                "payload": {"finding": "test the interrupt resume path"},
                "submitted_at": "2026-04-26T12:01:00Z",
                "trace_link": "reports/langsmith/trace-456.json",
            },
        ],
        "G-PARTY",
        trial_id=trial_id,
    )

    assert card.gate_id == "G-PARTY"
    assert len(card.meta.party_mode_contributions) == 2


def test_party_mode_as_interrupt_rejects_invalid_contribution() -> None:
    trial_id = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")

    with pytest.raises(ValidationError):
        party_mode_module.party_mode_as_interrupt(
            [
                {
                    "contribution_id": "33333333-3333-4333-8333-333333333333",
                    "persona": "",
                    "payload": {},
                    "submitted_at": "2026-04-26T12:00:00Z",
                    "trace_link": None,
                }
            ],
            "G-PARTY",
            trial_id=trial_id,
        )
