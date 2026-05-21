from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.models.state.operator_verdict import OperatorVerdict
from app.specialists.irene_pass1._act import (
    BulkRatificationError,
    PlanUnitRatificationError,
    confirm_plan_units,
)


def _verdict(unit_id: str, *, verb: str = "approve") -> OperatorVerdict:
    return OperatorVerdict(
        trial_id=uuid4(),
        verb=verb,
        gate_id="G1A",
        card_id=uuid4(),
        operator_id="Juanl",
        timestamp=datetime.now(UTC),
        decision_card_digest="a" * 64,
        edit_payload={"title": f"{unit_id} revised"} if verb == "edit" else None,
        reject_reason="not acceptable" if verb == "reject" else None,
    )


def _plan() -> dict[str, object]:
    return {
        "plan_units": [
            {"unit_id": f"unit-{index}", "title": f"Unit {index}"}
            for index in range(1, 6)
        ]
    }


def test_each_plan_unit_requires_own_operator_verdict() -> None:
    verdicts = {f"unit-{index}": _verdict(f"unit-{index}") for index in range(1, 6)}
    locked = confirm_plan_units(_plan(), verdicts)
    assert locked["locked"] is True
    assert len(locked["plan_units"]) == 5
    assert {unit["ratified_by"] for unit in locked["plan_units"]} == {"Juanl"}


def test_bulk_confirm_is_rejected() -> None:
    with pytest.raises(BulkRatificationError):
        confirm_plan_units(_plan(), _verdict("bulk"))


def test_missing_per_unit_verdict_is_rejected() -> None:
    with pytest.raises(PlanUnitRatificationError, match="unit-5"):
        confirm_plan_units(
            _plan(),
            {f"unit-{index}": _verdict(f"unit-{index}") for index in range(1, 5)},
        )
