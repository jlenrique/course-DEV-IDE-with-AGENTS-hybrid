"""Shape-pin tests for `SpecialistEnvelope` (Story 1.2 AC-1.2-A/B/C)."""

from __future__ import annotations

from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models.state import SpecialistEnvelope, SpecialistReturn
from tests.unit.models.state._helpers import (
    assert_forbids_extra_field,
    assert_round_trip,
    load_golden,
)


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(SpecialistEnvelope, load_golden("specialist_envelope"))


def test_forbids_extra_fields() -> None:
    assert_forbids_extra_field(SpecialistEnvelope, {"specialist_id": "irene"})


def test_default_request_id_is_uuid4() -> None:
    se = SpecialistEnvelope(specialist_id="irene")
    assert se.request_id.version == 4


def test_default_payload_in_is_empty_dict() -> None:
    se = SpecialistEnvelope(specialist_id="irene")
    assert se.payload_in == {}
    assert se.payload_out is None


def test_payload_out_accepts_specialist_return() -> None:
    sr = SpecialistReturn(specialist_id="irene", verb="proceed")
    se = SpecialistEnvelope(specialist_id="irene", payload_out=sr)
    assert se.payload_out is not None
    assert se.payload_out.verb == "proceed"


def test_rejects_naive_created_at() -> None:
    with pytest.raises(ValidationError):
        SpecialistEnvelope(
            specialist_id="irene",
            created_at=datetime(2026, 4, 23),  # naive
        )


def test_default_created_at_is_tz_aware() -> None:
    se = SpecialistEnvelope(specialist_id="irene")
    assert se.created_at.tzinfo is not None


def test_validate_assignment_blocks_naive_post_construction() -> None:
    se = SpecialistEnvelope(specialist_id="irene")
    with pytest.raises(ValidationError):
        se.created_at = datetime(2026, 4, 23)  # naive
