"""Strict envelope for production-graph trial lifecycle state."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.runtime.production_envelope import ProductionEnvelope
from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

ProductionTrialStatus = Literal[
    "registered",
    "in-flight",
    "paused-at-gate",
    "paused-at-error",
    "completed",
    "failed",
]
ProductionPreset = Literal["production", "explore"]
ProductionGateId = Literal["G1", "G2C", "G3", "G4"]


class ProductionTrialEnvelope(BaseModel):
    """Production trial registry record.

    `production_clone_launch_evidence` is deliberately required by callers. The
    runner can only set it true after a real graph step and at least one live
    specialist call have both happened.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    schema_version: Literal["production-trial-envelope.v1"] = (
        "production-trial-envelope.v1"
    )
    trial_id: UUID
    preset: ProductionPreset
    corpus_path: str
    operator_id: str
    started_at: datetime
    completed_at: datetime | None = None
    status: ProductionTrialStatus
    paused_gate: ProductionGateId | None = None
    # S4 part 2 (SCP 2026-06-11): set with status "paused-at-error" — the
    # stable machine tag of the SpecialistDispatchError that paused the run
    # (recoverable via `trial recover`, no operator verdict required).
    paused_error_tag: str | None = None
    langsmith_trace_id: str | None = None
    production_clone_launch_evidence: bool
    production_clone_launch_evidence_reason: str | None = None
    production_envelope: ProductionEnvelope
    cost_report_path: Path | None = None
    artifact_paths: list[Path] = Field(default_factory=list)

    @field_validator("trial_id")
    @classmethod
    def _enforce_trial_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("started_at")
    @classmethod
    def _enforce_started_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("completed_at")
    @classmethod
    def _enforce_completed_tz(cls, value: datetime | None) -> datetime | None:
        return enforce_tz_aware(value) if value is not None else None


__all__ = [
    "ProductionGateId",
    "ProductionPreset",
    "ProductionTrialEnvelope",
    "ProductionTrialStatus",
]
