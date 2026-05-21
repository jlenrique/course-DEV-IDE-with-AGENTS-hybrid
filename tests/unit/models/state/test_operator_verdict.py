"""Shape-pin tests for `OperatorVerdict`."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.state import OperatorVerdict
from tests.unit.models.state._helpers import (
    assert_forbids_extra_field,
    assert_round_trip,
    load_golden,
)


@pytest.fixture
def valid_kwargs() -> dict[str, object]:
    return {
        "verdict_id": uuid4(),
        "trial_id": uuid4(),
        "verb": "approve",
        "gate_id": "G2C",
        "card_id": uuid4(),
        "operator_id": "juanl",
        "timestamp": datetime.now(UTC),
        "decision_card_digest": "a" * 64,
    }


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(OperatorVerdict, load_golden("operator_verdict"))


def test_forbids_extra_fields(valid_kwargs: dict[str, object]) -> None:
    assert_forbids_extra_field(OperatorVerdict, {**valid_kwargs})


def test_is_frozen(valid_kwargs: dict[str, object]) -> None:
    ov = OperatorVerdict(**valid_kwargs)
    with pytest.raises(ValidationError):
        ov.verb = "edit"


@pytest.mark.parametrize("tamper_verb", ["timeout", "auto_approve"])
def test_fr34_tamper_verbs_rejected_at_construction(
    tamper_verb: str,
    valid_kwargs: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict(**{**valid_kwargs, "verb": tamper_verb})


@pytest.mark.parametrize("tamper_verb", ["timeout", "auto_approve"])
def test_fr34_tamper_verbs_rejected_via_json_validation(tamper_verb: str) -> None:
    payload = {
        "verdict_id": "11111111-1111-4111-8111-111111111111",
        "trial_id": "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa",
        "verb": tamper_verb,
        "gate_id": "G2C",
        "card_id": "22222222-2222-4222-8222-222222222222",
        "operator_id": "juanl",
        "timestamp": "2026-04-23T12:00:00+00:00",
        "decision_card_digest": "a" * 64,
    }
    with pytest.raises(ValidationError):
        OperatorVerdict.model_validate(payload)


def test_edit_verb_requires_edit_payload(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict(**{**valid_kwargs, "verb": "edit", "edit_payload": None})


def test_edit_verb_with_edit_payload_accepted(valid_kwargs: dict[str, object]) -> None:
    ov = OperatorVerdict(
        **{**valid_kwargs, "verb": "edit", "edit_payload": {"replacement": "new"}}
    )
    assert ov.verb == "edit"


def test_reject_verb_requires_reject_reason(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict(**{**valid_kwargs, "verb": "reject"})


def test_reject_verb_with_reject_reason_accepted(valid_kwargs: dict[str, object]) -> None:
    ov = OperatorVerdict(**{**valid_kwargs, "verb": "reject", "reject_reason": "fails fidelity"})
    assert ov.verb == "reject"


def test_approve_verb_with_edit_payload_rejected(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict(**{**valid_kwargs, "edit_payload": {"x": 1}})


def test_rejects_naive_datetime(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict(**{**valid_kwargs, "timestamp": datetime(2026, 4, 23, 12, 0, 0)})


def test_rejects_non_uuid4_card_id(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict(**{**valid_kwargs, "card_id": uuid.uuid1()})


def test_rejects_empty_gate_id(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict(**{**valid_kwargs, "gate_id": ""})
