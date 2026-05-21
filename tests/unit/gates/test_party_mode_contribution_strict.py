from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.gates.party_mode_contribution import PartyModeContribution

FIXTURE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "gates"
    / "party_mode_contribution_golden.json"
)


@pytest.fixture
def valid_kwargs() -> dict[str, object]:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_strict_config(valid_kwargs: dict[str, object]) -> None:
    assert PartyModeContribution.model_config["extra"] == "forbid"
    assert PartyModeContribution.model_config["validate_assignment"] is True
    assert PartyModeContribution.model_config["frozen"] is True

    with pytest.raises(ValidationError):
        PartyModeContribution.model_validate({**valid_kwargs, "bogus": True})


def test_tz_aware_datetime_required(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        PartyModeContribution.model_validate(
            {**valid_kwargs, "submitted_at": datetime(2026, 4, 26, 12, 0, 0)}
        )


@pytest.mark.parametrize("persona", ["", "   "])
def test_persona_non_empty(persona: str, valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="at least 1 character|persona must be non-empty"):
        PartyModeContribution.model_validate({**valid_kwargs, "persona": persona})


def test_schema_roundtrip_golden(valid_kwargs: dict[str, object]) -> None:
    contribution = PartyModeContribution.model_validate(valid_kwargs)

    assert contribution.model_dump(mode="json") == valid_kwargs
