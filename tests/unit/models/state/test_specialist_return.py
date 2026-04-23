"""Shape-pin tests for `SpecialistReturn` (Story 1.2 AC-1.2-A/B/C)."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.state import SpecialistReturn
from tests.unit.models.state._helpers import (
    assert_forbids_extra_field,
    assert_round_trip,
    load_golden,
)


@pytest.fixture
def valid_kwargs() -> dict[str, object]:
    return {"specialist_id": "irene", "verb": "proceed"}


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(SpecialistReturn, load_golden("specialist_return"))


def test_forbids_extra_fields(valid_kwargs: dict[str, object]) -> None:
    assert_forbids_extra_field(SpecialistReturn, valid_kwargs)


@pytest.mark.parametrize("verb", ["proceed", "edit", "reject"])
def test_accepts_valid_verb_values(verb: str, valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["verb"] = verb
    if verb == "edit":
        valid_kwargs["edit_payload"] = {"k": "v"}
    elif verb == "reject":
        valid_kwargs["reject_reason"] = "fails contract"
    sr = SpecialistReturn(**valid_kwargs)
    assert sr.verb == verb


def test_rejects_unknown_verb(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["verb"] = "approve"  # operator-side verb, not specialist-side
    with pytest.raises(ValidationError):
        SpecialistReturn(**valid_kwargs)


def test_edit_verb_requires_edit_payload(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["verb"] = "edit"
    with pytest.raises(ValidationError):
        SpecialistReturn(**valid_kwargs)


def test_reject_verb_requires_reject_reason(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["verb"] = "reject"
    with pytest.raises(ValidationError):
        SpecialistReturn(**valid_kwargs)


def test_proceed_verb_with_edit_payload_rejected(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["edit_payload"] = {"x": 1}
    with pytest.raises(ValidationError):
        SpecialistReturn(**valid_kwargs)


def test_proceed_verb_with_reject_reason_rejected(valid_kwargs: dict[str, object]) -> None:
    """G6-EDGE inverse-coverage: proceed must NOT carry reject_reason either."""
    valid_kwargs["reject_reason"] = "should not appear on proceed"
    with pytest.raises(ValidationError):
        SpecialistReturn(**valid_kwargs)


def test_rejects_naive_timestamp(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["timestamp"] = datetime(2026, 4, 23)  # naive
    with pytest.raises(ValidationError):
        SpecialistReturn(**valid_kwargs)
