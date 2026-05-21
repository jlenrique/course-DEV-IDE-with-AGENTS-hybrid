from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid1, uuid4

import pytest
from pydantic import ValidationError

from app.models.decision_cards import DecisionCard, DecisionCardMeta, OverrideEvent


def _meta() -> DecisionCardMeta:
    return DecisionCardMeta(
        cache_state="healthy",
        affected_nodes=["04", "05"],
        override_trail=[
            OverrideEvent(
                event_id=uuid4(),
                applied_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
                node_id="04",
                previous_value={"model": "gpt-5"},
                new_value={"model": "gpt-5-mini"},
                operator_id="juanl",
                confirm_token="confirm-001",
            )
        ],
        reject_rate=0.25,
    )


def _valid_kwargs() -> dict[str, object]:
    return {
        "card_id": uuid4(),
        "trial_id": uuid4(),
        "gate_id": "G1",
        "created_at": datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        "drafted_proposal": {"action": "open-trial"},
        "evidence": [{"kind": "manifest", "node": "04"}],
        "risks": ["cache cold-start"],
        "verb": "approve",
        "meta": _meta(),
    }


def test_decision_card_model_config_and_extra_field_rejection() -> None:
    assert DecisionCard.model_config["extra"] == "forbid"
    assert DecisionCard.model_config["validate_assignment"] is True

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        DecisionCard.model_validate({**_valid_kwargs(), "bogus": True})


def test_decision_card_rejects_naive_datetime() -> None:
    payload = _valid_kwargs()
    payload["created_at"] = datetime(2026, 4, 26, 12, 0, 0)
    with pytest.raises(ValidationError, match="timezone-aware"):
        DecisionCard.model_validate(payload)


def test_decision_card_verb_closed_enum_rejected_at_construction_assignment_and_json() -> None:
    payload = _valid_kwargs()
    payload["verb"] = "timeout"
    with pytest.raises(ValidationError):
        DecisionCard.model_validate(payload)

    card = DecisionCard.model_validate(_valid_kwargs())
    with pytest.raises(ValidationError):
        card.verb = "timeout"

    with pytest.raises(ValidationError):
        DecisionCard.model_validate_json(
            """{
                "card_id": "11111111-1111-4111-8111-111111111111",
                "trial_id": "22222222-2222-4222-8222-222222222222",
                "gate_id": "G1",
                "created_at": "2026-04-26T12:00:00+00:00",
                "drafted_proposal": {"action": "open-trial"},
                "evidence": [{"kind": "manifest", "node": "04"}],
                "risks": ["cache cold-start"],
                "verb": "timeout",
                "meta": {
                    "cache_state": "healthy",
                    "affected_nodes": ["04", "05"],
                    "override_trail": [],
                    "reject_rate": 0.25
                }
            }"""
        )


def test_decision_card_meta_rejects_empty_affected_node_and_non_uuid4_ids() -> None:
    with pytest.raises(ValidationError, match="affected_nodes entries"):
        DecisionCardMeta(
            cache_state="mixed",
            affected_nodes=[""],
            override_trail=[],
            reject_rate=0.5,
        )

    payload = _valid_kwargs()
    payload["card_id"] = uuid1()
    with pytest.raises(ValidationError, match="UUID4"):
        DecisionCard.model_validate(payload)
