"""Section 04.5 HIL run-budget estimator verdict models."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

Section04_5VerdictVerb = Literal["acknowledged", "edit", "reject"]
Section04_5SurfaceId = Literal["section_04_5_g1_5_estimator"]
SECTION_04_5_SURFACE_ID: Section04_5SurfaceId = "section_04_5_g1_5_estimator"


class EstimatorEditPayload(BaseModel):
    """Field-level edits for the run-budget estimator operator inputs."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    updates: dict[str, Any] = Field(
        ...,
        min_length=1,
        description="Mapping of estimator field names to operator-confirmed updates.",
    )

    @field_validator("updates")
    @classmethod
    def _reject_blank_update_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        for field_name in value:
            if not field_name.strip():
                raise ValueError("estimator edit field name must be non-empty")
        return value


class Section04_5OperatorVerdict(BaseModel):  # noqa: N801
    """Tamper-evident verdict emitted by the Section 04.5 G1.5 estimator surface."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

    run_id: UUID = Field(..., description="UUID4 identity for the estimator run.")
    surface_id: Section04_5SurfaceId = Field(
        default=SECTION_04_5_SURFACE_ID,
        description="Closed Section 04.5 estimator surface identifier.",
    )
    verb: Section04_5VerdictVerb = Field(
        ...,
        description="acknowledged | edit | reject",
    )
    estimator_id: str = Field(
        ...,
        min_length=1,
        description="Run-budget estimator identifier.",
    )
    operator_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]+$",
        description="Operator identifier.",
    )
    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Timezone-aware verdict submission time.",
    )
    decision_card_digest: str = Field(
        ...,
        description="Lowercase sha256 digest of the reviewed estimator payload.",
    )
    edit_payload: EstimatorEditPayload | None = Field(
        default=None,
        description="Required iff verb is edit.",
    )
    reject_reason: str | None = Field(
        default=None,
        description="Required iff verb is reject.",
    )

    @field_validator("run_id")
    @classmethod
    def _require_uuid4(cls, value: UUID) -> UUID:
        return enforce_uuid4_version(value)

    @field_validator("estimator_id", "operator_id", mode="before")
    @classmethod
    def _strip_string_identifier(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("submitted_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("decision_card_digest")
    @classmethod
    def _require_sha256(cls, value: str) -> str:
        if not re.fullmatch(r"[0-9a-f]{64}", value):
            raise ValueError("decision_card_digest must be lowercase sha256 hex")
        return value

    @model_validator(mode="after")
    def _enforce_verb_payload_consistency(self) -> Section04_5OperatorVerdict:
        if self.verb == "edit":
            if self.edit_payload is None:
                raise ValueError("verb='edit' requires edit_payload")
            if self.reject_reason is not None:
                raise ValueError("verb='edit' forbids reject_reason")
            return self
        if self.verb == "reject":
            if self.reject_reason is None:
                raise ValueError("verb='reject' requires reject_reason")
            if self.edit_payload is not None:
                raise ValueError("verb='reject' forbids edit_payload")
            return self
        if self.edit_payload is not None or self.reject_reason is not None:
            raise ValueError("verb='acknowledged' forbids edit_payload and reject_reason")
        return self


__all__ = [
    "EstimatorEditPayload",
    "SECTION_04_5_SURFACE_ID",
    "Section04_5OperatorVerdict",
    "Section04_5SurfaceId",
    "Section04_5VerdictVerb",
]
