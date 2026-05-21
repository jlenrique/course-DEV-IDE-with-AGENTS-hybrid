from __future__ import annotations

from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models.state.operator_verdict import (
    OperatorVerdict,
    operator_verdict_schema_text,
)

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "operator_verdict"
    / "operator_verdict_with_revise_count_golden.json"
)
SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / ".."
    / "app"
    / "models"
    / "schemas"
    / "operator_verdict.schema.json"
).resolve()


def _base_payload() -> dict[str, object]:
    return {
        "trial_id": UUID("22222222-2222-4222-8222-222222222222"),
        "verb": "approve",
        "gate_id": "G2B",
        "card_id": UUID("33333333-3333-4333-8333-333333333333"),
        "operator_id": "operator_1",
        "decision_card_digest": "a" * 64,
    }


def test_revise_count_defaults_to_zero() -> None:
    verdict = OperatorVerdict(**_base_payload())

    assert verdict.revise_count == 0


def test_revise_count_valid_range_zero_to_three_and_golden_fixture() -> None:
    for count in [0, 1, 2, 3]:
        verdict = OperatorVerdict(**_base_payload(), revise_count=count)
        assert verdict.revise_count == count

    golden = OperatorVerdict.model_validate_json(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert golden.revise_count == 2


def test_revise_count_four_raises_validation_error() -> None:
    with pytest.raises(ValidationError):
        OperatorVerdict(**_base_payload(), revise_count=4)


def test_json_schema_byte_equality() -> None:
    assert operator_verdict_schema_text() == SCHEMA_PATH.read_text(encoding="utf-8")
