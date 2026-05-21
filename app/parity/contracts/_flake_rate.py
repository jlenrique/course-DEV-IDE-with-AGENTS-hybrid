"""Per-cell flake-rate calculator for TW-7c-6 scaffold checks."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

CellClass = Literal["pre-7c", "7c-added"]

PRE_7C_BUDGET = 0.001
SLAB_7C_ADDED_BUDGET = 0.0005


class CellFlakeInput(BaseModel):
    """Synthetic or observed per-cell run result input."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    cell_id: str = Field(..., min_length=1)
    cell_class: CellClass
    total_runs: int = Field(..., ge=1)
    failed_runs: int = Field(..., ge=0)

    @model_validator(mode="after")
    def _failed_runs_not_above_total(self) -> CellFlakeInput:
        if self.failed_runs > self.total_runs:
            raise ValueError("failed_runs cannot exceed total_runs")
        return self


class CellFlakeVerdict(BaseModel):
    """Budget result for one parity cell."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    cell_id: str
    cell_class: CellClass
    total_runs: int
    failed_runs: int
    flake_rate: float
    budget: float
    within_budget: bool


def budget_for_cell_class(cell_class: CellClass) -> float:
    return SLAB_7C_ADDED_BUDGET if cell_class == "7c-added" else PRE_7C_BUDGET


def evaluate_cell_flake_budget(cell: CellFlakeInput) -> CellFlakeVerdict:
    """Evaluate one cell against the strict AMEND-7a rate budget."""
    flake_rate = cell.failed_runs / cell.total_runs
    budget = budget_for_cell_class(cell.cell_class)
    return CellFlakeVerdict(
        cell_id=cell.cell_id,
        cell_class=cell.cell_class,
        total_runs=cell.total_runs,
        failed_runs=cell.failed_runs,
        flake_rate=flake_rate,
        budget=budget,
        within_budget=flake_rate < budget,
    )


__all__ = [
    "CellFlakeInput",
    "CellFlakeVerdict",
    "budget_for_cell_class",
    "evaluate_cell_flake_budget",
]
