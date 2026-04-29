"""Specialist persistence state shape for Slab 7a conversation artifacts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.decision_cards import SpecialistId
from app.models.state._base import enforce_tz_aware
from app.models.state.model_resolution_entry import ModelResolutionEntry

SpecialistStateStatus = Literal["pending", "running", "completed", "deferred", "failed"]


class SpecialistState(BaseModel):
    """Persisted per-specialist state snapshot for adjacent gate pickup."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: Literal["specialist-state.v1"] = "specialist-state.v1"
    trial_id: UUID
    specialist_id: SpecialistId
    gate_id: str | None = Field(default=None, min_length=1)
    status: SpecialistStateStatus = "pending"
    cache_prefix: str | None = None
    cache_prefix_hash: str | None = Field(
        default=None,
        min_length=64,
        max_length=64,
        pattern=r"^[0-9a-f]{64}$",
    )
    summary_path: str | None = None
    artifact_paths: tuple[str, ...] = Field(default_factory=tuple)
    model_resolution_trail: tuple[ModelResolutionEntry, ...] = Field(default_factory=tuple)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("updated_at")
    @classmethod
    def _enforce_updated_at_tz(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("summary_path")
    @classmethod
    def _summary_path_posix(cls, value: str | None) -> str | None:
        if value is not None and "\\" in value:
            raise ValueError("summary_path must use POSIX separators")
        return value

    @field_validator("artifact_paths")
    @classmethod
    def _artifact_paths_posix(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if any("\\" in path for path in value):
            raise ValueError("artifact_paths must use POSIX separators")
        return value


def specialist_state_schema_text() -> str:
    """Return the canonical emitted SpecialistState JSON Schema text."""
    import json

    return json.dumps(SpecialistState.model_json_schema(), indent=2, sort_keys=True) + "\n"


__all__ = [
    "SpecialistState",
    "SpecialistStateStatus",
    "specialist_state_schema_text",
]
