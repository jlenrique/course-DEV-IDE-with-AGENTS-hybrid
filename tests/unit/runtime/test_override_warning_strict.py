from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.runtime.override_warning import ModelOverrideWarning


def _valid_kwargs() -> dict[str, object]:
    return {
        "warning_id": UUID("11111111-1111-4111-8111-111111111111"),
        "trial_id": UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"),
        "node_id": "texas_retrieval",
        "requested_model": "gpt-5.5",
        "current_model": "gpt-5.4",
        "estimated_cost_delta_usd": 1.5,
        "affected_nodes": ["texas_retrieval", "writer"],
        "cache_state_delta": {"before": "healthy", "after": "mixed"},
        "confirm_token": "a" * 64,
        "issued_at": datetime(2026, 4, 26, 12, 0, tzinfo=UTC),
        "expires_at": datetime(2026, 4, 26, 12, 5, tzinfo=UTC),
    }


def test_model_override_warning_strict_config() -> None:
    warning = ModelOverrideWarning(**_valid_kwargs())
    assert warning.model_config["extra"] == "forbid"
    assert warning.model_config["frozen"] is True


def test_model_override_warning_rejects_tz_naive_datetimes() -> None:
    kwargs = _valid_kwargs()
    kwargs["issued_at"] = datetime(2026, 4, 26, 12, 0)
    with pytest.raises(ValidationError):
        ModelOverrideWarning(**kwargs)


def test_model_override_warning_rejects_negative_cost_delta() -> None:
    kwargs = _valid_kwargs()
    kwargs["estimated_cost_delta_usd"] = -0.1
    with pytest.raises(ValidationError):
        ModelOverrideWarning(**kwargs)
