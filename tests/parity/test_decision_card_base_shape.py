from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import TypeAdapter, ValidationError

from app.models.decision_cards._base import (
    CacheState,
    DecisionCardBase,
    DecisionCardMeta,
)
from app.models.decision_cards.override_event import OverrideEvent


def _override_event() -> OverrideEvent:
    return OverrideEvent(
        event_id=uuid4(),
        applied_at=datetime(2026, 5, 5, 12, 0, tzinfo=UTC),
        node_id="04",
        previous_value={"gate": "G1"},
        new_value={"gate": "G1A"},
        operator_id="operator_1",
        confirm_token="CONFIRM",
    )


def test_decision_card_base_field_set_and_config() -> None:
    assert set(DecisionCardBase.model_fields) == {"decision_card_digest", "meta"}
    assert set(DecisionCardMeta.model_fields) == {
        "affected_nodes",
        "cache_state",
        "override_trail",
    }
    assert DecisionCardBase.model_config["extra"] == "forbid"
    assert DecisionCardBase.model_config["validate_assignment"] is True
    assert DecisionCardBase.model_config["frozen"] is True


def test_decision_card_base_accepts_valid_meta() -> None:
    card = DecisionCardBase(
        decision_card_digest="a" * 64,
        meta=DecisionCardMeta(
            cache_state="healthy",
            affected_nodes=["04", "05"],
            override_trail=[_override_event()],
        ),
    )

    assert card.meta.cache_state is CacheState.HEALTHY
    assert card.meta.affected_nodes == ["04", "05"]
    assert len(card.meta.override_trail) == 1


def test_cache_state_closed_enum_rejects_red_values() -> None:
    with pytest.raises(ValidationError):
        DecisionCardMeta(cache_state="warm")

    schema = DecisionCardMeta.model_json_schema()
    assert schema["$defs"]["CacheState"]["enum"] == ["healthy", "mixed", "cold"]
    assert TypeAdapter(CacheState).validate_python("cold") is CacheState.COLD
    with pytest.raises(ValidationError):
        TypeAdapter(CacheState).validate_python("warm")


def test_decision_card_digest_requires_sha256_hex() -> None:
    with pytest.raises(ValidationError, match="lowercase sha256"):
        DecisionCardBase(
            decision_card_digest="not-a-digest",
            meta=DecisionCardMeta(cache_state="mixed"),
        )


def test_decision_card_base_is_frozen_after_construction() -> None:
    card = DecisionCardBase(
        decision_card_digest="b" * 64,
        meta=DecisionCardMeta(cache_state="cold"),
    )

    with pytest.raises(ValidationError):
        card.decision_card_digest = "c" * 64
