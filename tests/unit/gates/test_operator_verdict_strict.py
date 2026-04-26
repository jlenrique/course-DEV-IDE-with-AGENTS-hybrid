from __future__ import annotations

import uuid
from datetime import datetime
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.gates.verdict import OperatorVerdict
from tests.unit.gates._helpers import sample_verdict


@pytest.fixture
def valid_kwargs() -> dict[str, object]:
    trial_id = UUID("aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa")
    return sample_verdict(trial_id=trial_id).model_dump(mode="python")


def test_strict_config(valid_kwargs: dict[str, object]) -> None:
    assert OperatorVerdict.model_config["extra"] == "forbid"
    assert OperatorVerdict.model_config["validate_assignment"] is True
    assert OperatorVerdict.model_config["frozen"] is True

    verdict = OperatorVerdict.model_validate(valid_kwargs)
    with pytest.raises(ValidationError):
        verdict.verb = "edit"

    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        OperatorVerdict.model_validate({**valid_kwargs, "bogus": True})


@pytest.mark.parametrize("tamper_verb", ["timeout", "auto_approve"])
def test_verb_closed_enum_triple_layer(
    tamper_verb: str,
    valid_kwargs: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict.model_validate({**valid_kwargs, "verb": tamper_verb})

    with pytest.raises(ValidationError):
        OperatorVerdict.model_validate_json(
            OperatorVerdict.model_validate(valid_kwargs)
            .model_copy(update={"verb": tamper_verb})
            .model_dump_json()
        )

    verdict = OperatorVerdict.model_validate(valid_kwargs)
    with pytest.raises(ValidationError):
        verdict.verb = tamper_verb


def test_edit_payload_required_iff_edit_verb(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict.model_validate(
            {**valid_kwargs, "verb": "edit", "edit_payload": None}
        )

    with pytest.raises(ValidationError):
        OperatorVerdict.model_validate({**valid_kwargs, "edit_payload": {"x": 1}})


def test_tz_aware_datetime_required(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="timezone-aware"):
        OperatorVerdict.model_validate(
            {**valid_kwargs, "timestamp": datetime(2026, 4, 26, 12, 0, 0)}
        )


@pytest.mark.parametrize("operator_id", ["", "9juanl", "juanl!", "_juanl"])
def test_operator_id_non_empty_regex(
    operator_id: str,
    valid_kwargs: dict[str, object],
) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict.model_validate({**valid_kwargs, "operator_id": operator_id})


def test_accepts_legacy_decision_card_id_alias(valid_kwargs: dict[str, object]) -> None:
    payload = dict(valid_kwargs)
    card_id = payload.pop("card_id")
    payload["decision_card_id"] = card_id
    verdict = OperatorVerdict.model_validate(payload)
    assert verdict.card_id == card_id


def test_rejects_non_uuid4_ids(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict.model_validate({**valid_kwargs, "card_id": uuid.uuid1()})


def test_rejects_non_sha256_digest(valid_kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict.model_validate({**valid_kwargs, "decision_card_digest": "xyz"})
