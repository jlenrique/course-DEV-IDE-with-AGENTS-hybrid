"""Strict cross-specialist accumulator for production composition."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def compute_output_digest(output: dict[str, Any]) -> str:
    """Return a stable SHA-256 digest for a specialist output payload."""
    canonical = json.dumps(
        output,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _enforce_tz_aware(value: datetime) -> datetime:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
    return value


def _enforce_uuid4(value: UUID) -> UUID:
    if value.version != 4:
        raise ValueError("trial_id must be a UUID4")
    return value


class SpecialistContribution(BaseModel):
    """One immutable specialist output appended to a production envelope."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True, frozen=True)

    specialist_id: str = Field(..., min_length=1)
    contributed_at: datetime
    output: dict[str, Any]
    cost_usd: float = Field(..., ge=0.0)
    model_used: str = Field(..., min_length=1)
    output_digest: str = Field(..., min_length=64, max_length=64, pattern=r"^[0-9a-f]{64}$")

    @classmethod
    def from_output(
        cls,
        *,
        specialist_id: str,
        output: dict[str, Any],
        model_used: str,
        cost_usd: float = 0.0,
        contributed_at: datetime | None = None,
    ) -> SpecialistContribution:
        return cls(
            specialist_id=specialist_id,
            contributed_at=contributed_at or datetime.now(UTC),
            output=output,
            cost_usd=cost_usd,
            model_used=model_used,
            output_digest=compute_output_digest(output),
        )

    @field_validator("contributed_at")
    @classmethod
    def _enforce_contributed_tz(cls, value: datetime) -> datetime:
        return _enforce_tz_aware(value)

    @model_validator(mode="after")
    def _enforce_output_digest(self) -> SpecialistContribution:
        expected = compute_output_digest(self.output)
        if self.output_digest != expected:
            raise ValueError("output_digest must equal sha256 of output")
        return self


class ProductionEnvelope(BaseModel):
    """Canonical cross-specialist accumulator for production composition.

    This is distinct from ``RunState.cache_state.cache_prefix``, which remains
    per-specialist scratch for isolated scaffold execution.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)

    schema_version: Literal["production-envelope.v1"] = "production-envelope.v1"
    trial_id: UUID
    contributions: tuple[SpecialistContribution, ...] = Field(default_factory=tuple)

    @field_validator("trial_id")
    @classmethod
    def _enforce_trial_uuid4(cls, value: UUID) -> UUID:
        return _enforce_uuid4(value)

    def get_contribution(self, specialist_id: str) -> SpecialistContribution | None:
        """Lookup an upstream specialist contribution by id."""
        for contribution in self.contributions:
            if contribution.specialist_id == specialist_id:
                return contribution
        return None

    def add_contribution(self, contribution: SpecialistContribution) -> None:
        """Append exactly one contribution per specialist per trial."""
        if self.get_contribution(contribution.specialist_id) is not None:
            raise ValueError(
                f"production envelope already has contribution for "
                f"{contribution.specialist_id!r}"
            )
        self.contributions = (*self.contributions, contribution)


__all__ = [
    "ProductionEnvelope",
    "SpecialistContribution",
    "compute_output_digest",
]
