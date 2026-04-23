"""Shape-pin tests for `OperatorVerdict` (Story 1.2 AC-1.2-A/B/C).

Includes the FR34 tamper-evidence triple-layer red-rejection test:
``verb="timeout"`` and ``verb="auto_approve"`` MUST be rejected at field
+ model_validator + schema-pin layers.
"""

from __future__ import annotations

from datetime import datetime
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
        "verb": "approve",
        "gate_id": "G2C",
        "decision_card_id": uuid4(),
        "operator_id": "juanl",
    }


def test_round_trip_against_golden_fixture() -> None:
    assert_round_trip(OperatorVerdict, load_golden("operator_verdict"))


def test_forbids_extra_fields(valid_kwargs: dict[str, object]) -> None:
    assert_forbids_extra_field(OperatorVerdict, {**valid_kwargs})


def test_is_frozen(valid_kwargs: dict[str, object]) -> None:
    ov = OperatorVerdict(**valid_kwargs)
    with pytest.raises(ValidationError):
        ov.verb = "edit"  # frozen=True forbids


@pytest.mark.parametrize("tamper_verb", ["timeout", "auto_approve"])
def test_fr34_tamper_verbs_rejected_at_construction(
    tamper_verb: str,
    valid_kwargs: dict[str, object],
) -> None:
    """FR34: 'timeout' and 'auto_approve' MUST never reach the verdict surface."""
    valid_kwargs["verb"] = tamper_verb
    with pytest.raises(ValidationError):
        OperatorVerdict(**valid_kwargs)


@pytest.mark.parametrize("tamper_verb", ["timeout", "auto_approve"])
def test_fr34_tamper_verbs_rejected_via_json_validation(tamper_verb: str) -> None:
    """JSON-input path also red-rejects tamper verbs (defense-in-depth for raw ingest)."""
    payload = {
        "verb": tamper_verb,
        "gate_id": "G2C",
        "decision_card_id": "22222222-2222-4222-8222-222222222222",
        "operator_id": "juanl",
        "timestamp": "2026-04-23T12:00:00+00:00",
    }
    with pytest.raises(ValidationError):
        OperatorVerdict.model_validate(payload)


def test_edit_verb_requires_edit_payload(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["verb"] = "edit"
    with pytest.raises(ValidationError):
        OperatorVerdict(**valid_kwargs)


def test_edit_verb_with_edit_payload_accepted(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["verb"] = "edit"
    valid_kwargs["edit_payload"] = {"replacement": "new content"}
    ov = OperatorVerdict(**valid_kwargs)
    assert ov.verb == "edit"
    assert ov.edit_payload == {"replacement": "new content"}


def test_reject_verb_requires_reject_reason(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["verb"] = "reject"
    with pytest.raises(ValidationError):
        OperatorVerdict(**valid_kwargs)


def test_reject_verb_with_reject_reason_accepted(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["verb"] = "reject"
    valid_kwargs["reject_reason"] = "fails fidelity contract"
    ov = OperatorVerdict(**valid_kwargs)
    assert ov.verb == "reject"


def test_approve_verb_with_edit_payload_rejected(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["edit_payload"] = {"x": 1}
    with pytest.raises(ValidationError):
        OperatorVerdict(**valid_kwargs)


def test_approve_verb_with_reject_reason_rejected(valid_kwargs: dict[str, object]) -> None:
    """G6-EDGE inverse-coverage: approve must NOT carry reject_reason either."""
    valid_kwargs["reject_reason"] = "should not appear on approve"
    with pytest.raises(ValidationError):
        OperatorVerdict(**valid_kwargs)


def test_rejects_naive_datetime(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["timestamp"] = datetime(2026, 4, 23, 12, 0, 0)  # naive
    with pytest.raises(ValidationError):
        OperatorVerdict(**valid_kwargs)


def test_rejects_non_uuid4_decision_card_id(valid_kwargs: dict[str, object]) -> None:
    import uuid

    valid_kwargs["decision_card_id"] = uuid.uuid1()  # uuid1, not uuid4
    with pytest.raises(ValidationError):
        OperatorVerdict(**valid_kwargs)


def test_rejects_empty_gate_id(valid_kwargs: dict[str, object]) -> None:
    valid_kwargs["gate_id"] = ""
    with pytest.raises(ValidationError):
        OperatorVerdict(**valid_kwargs)
