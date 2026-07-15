"""Strict per-trial economics report models."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.state._base import enforce_tz_aware


class AgentCostEntry(BaseModel):
    """Per-agent aggregate cost attribution for one trial."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    agent_name: str = Field(..., min_length=1)
    model_assigned: str = Field(..., min_length=1)
    call_count: int = Field(..., ge=0)
    input_tokens: int = Field(..., ge=0)
    output_tokens: int = Field(..., ge=0)
    cost_usd: float = Field(..., ge=0.0)


class DriftAlert(BaseModel):
    """Informational per-agent drift alert against rolling historical median."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    agent_name: str = Field(..., min_length=1)
    rolling_median_usd_per_call: float = Field(..., ge=0.0)
    observed_usd_per_call: float = Field(..., ge=0.0)
    deviation_pct: float


DriftStatus = DriftAlert


class BudgetStatus(BaseModel):
    """Soft-cap budget posture for the measured trial."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    state: Literal["no-cap", "under-budget", "over-budget-warning", "unknown-cost"]
    over_by_usd: float = Field(..., ge=0.0)


class TrialEconomicsReport(BaseModel):
    """Strict cost-engineering report captured for one trial."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    trial_id: str = Field(..., min_length=1)
    measured_at: datetime
    total_cost_usd: float = Field(..., ge=0.0)
    per_agent_breakdown: dict[str, AgentCostEntry]
    per_model_breakdown: dict[str, float]
    cascade_config_digest: str = Field(
        ...,
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
    )
    pricing_table_digest: str = Field(
        ...,
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
    )
    langsmith_trace_url: str | None = None
    drift_alerts: list[DriftAlert] = Field(default_factory=list)
    budget_status: BudgetStatus
    cost_posture: Literal[
        "exact",
        "known-lower-bound-with-explicit-unavailable-attempts",
    ] = "exact"
    unavailable_attempt_count: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def _cost_posture_matches_unavailable_count(self) -> TrialEconomicsReport:
        exact = self.cost_posture == "exact"
        if exact != (self.unavailable_attempt_count == 0):
            raise ValueError("cost posture contradicts unavailable-attempt count")
        return self

    @field_validator("measured_at")
    @classmethod
    def _tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("per_model_breakdown")
    @classmethod
    def _non_negative_model_costs(cls, value: dict[str, float]) -> dict[str, float]:
        for model_id, cost in value.items():
            if not isinstance(model_id, str) or not model_id:
                raise ValueError("per_model_breakdown keys must be non-empty strings")
            if cost < 0.0:
                raise ValueError("per_model_breakdown values must be non-negative")
        return value


__all__ = [
    "AgentCostEntry",
    "BudgetStatus",
    "DriftAlert",
    "DriftStatus",
    "TrialEconomicsReport",
]
