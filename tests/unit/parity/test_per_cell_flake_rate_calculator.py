from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.parity.contracts._flake_rate import (
    CellFlakeInput,
    budget_for_cell_class,
    evaluate_cell_flake_budget,
)


def test_7c_added_cell_uses_tightened_budget():
    assert budget_for_cell_class("7c-added") == 0.0005


def test_pre_7c_cell_uses_grandfathered_budget():
    assert budget_for_cell_class("pre-7c") == 0.001


def test_zero_failures_are_within_budget_for_7c_added_cell():
    verdict = evaluate_cell_flake_budget(
        CellFlakeInput(
            cell_id="section_02a_g0",
            cell_class="7c-added",
            total_runs=2000,
            failed_runs=0,
        )
    )

    assert verdict.within_budget is True
    assert verdict.flake_rate == 0


def test_equal_to_budget_is_not_within_strict_budget():
    verdict = evaluate_cell_flake_budget(
        CellFlakeInput(
            cell_id="section_02a_g0",
            cell_class="7c-added",
            total_runs=2000,
            failed_runs=1,
        )
    )

    assert verdict.flake_rate == 0.0005
    assert verdict.within_budget is False


def test_failed_runs_cannot_exceed_total_runs():
    with pytest.raises(ValidationError):
        CellFlakeInput(
            cell_id="bad-cell",
            cell_class="pre-7c",
            total_runs=10,
            failed_runs=11,
        )
