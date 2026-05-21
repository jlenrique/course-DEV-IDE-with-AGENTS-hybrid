from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.models.state.specialist_state import SpecialistState, specialist_state_schema_text

FIXTURE = Path("tests/fixtures/specialist_state/specialist_state_golden.json")
SCHEMA = Path("app/models/schemas/specialist_state.schema.json")


def test_specialist_state_round_trips_golden_fixture() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))

    state = SpecialistState.model_validate(payload)

    assert state.model_dump(mode="json") == payload


def test_specialist_state_schema_file_is_lockstep() -> None:
    assert SCHEMA.read_text(encoding="utf-8") == specialist_state_schema_text()


def test_specialist_state_schema_required_fields_are_pinned() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    assert set(schema["required"]) == {"trial_id", "specialist_id"}


def test_specialist_state_rejects_windows_paths() -> None:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    payload["artifact_paths"] = ["state\\config\\runs\\bad.md"]

    with pytest.raises(ValidationError, match="POSIX"):
        SpecialistState.model_validate(payload)
