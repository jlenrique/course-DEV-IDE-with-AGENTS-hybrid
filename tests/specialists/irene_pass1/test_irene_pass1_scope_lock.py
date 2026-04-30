from __future__ import annotations

from app.specialists.irene_pass1._act import confirm_plan_units
from tests.specialists.irene_pass1.test_irene_pass1_per_plan_unit_ratification import (
    _plan,
    _verdict,
)


def test_scope_lock_carries_ratified_plan_units() -> None:
    verdicts = {f"unit-{index}": _verdict(f"unit-{index}") for index in range(1, 6)}
    locked = confirm_plan_units(_plan(), verdicts)

    assert locked["locked"] is True
    assert [unit["unit_id"] for unit in locked["plan_units"]] == [
        "unit-1",
        "unit-2",
        "unit-3",
        "unit-4",
        "unit-5",
    ]
