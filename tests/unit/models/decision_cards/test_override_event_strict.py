from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid1, uuid4

import pytest
from pydantic import ValidationError

from app.models.decision_cards import OverrideEvent


def test_override_event_strict_validation() -> None:
    event = OverrideEvent(
        event_id=uuid4(),
        applied_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        node_id="04",
        previous_value={"model": "gpt-5"},
        new_value={"model": "gpt-5-mini"},
        operator_id="juanl",
        confirm_token="confirm-override-001",
    )
    assert event.node_id == "04"

    with pytest.raises(ValidationError, match="timezone-aware"):
        OverrideEvent(
            event_id=uuid4(),
            applied_at=datetime(2026, 4, 26, 12, 0, 0),
            node_id="04",
            previous_value={},
            new_value={},
            operator_id="juanl",
            confirm_token="confirm-override-001",
        )

    with pytest.raises(ValidationError, match="UUID4"):
        OverrideEvent(
            event_id=uuid1(),
            applied_at=datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
            node_id="04",
            previous_value={},
            new_value={},
            operator_id="juanl",
            confirm_token="confirm-override-001",
        )
