"""Section 04A HIL poll-surface verdict models."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationInfo,
    field_validator,
    model_validator,
)

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

Section04AVerdictVerb = Literal["approve", "edit", "reject"]
Section04ASurfaceId = Literal["section_04a_g1a_poll"]
SECTION_04A_SURFACE_ID: Section04ASurfaceId = "section_04a_g1a_poll"


def _strip_non_empty(value: str, *, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must be non-empty")
    return stripped


class PlanUnitEditPayload(BaseModel):
    """Field-level edits for one ratified PlanUnit."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    updates: dict[str, Any] = Field(
        ...,
        min_length=1,
        description="Field-level updates to apply to the reviewed plan unit.",
    )

    @field_validator("updates")
    @classmethod
    def _reject_empty_update_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for field_name, field_value in value.items():
            if not isinstance(field_name, str):
                raise ValueError("edit field name must be a string")
            normalized[_strip_non_empty(field_name, field_name="edit field name")] = (
                field_value
            )
        return normalized


class Section04AOperatorVerdict(BaseModel):
    """Tamper-evident verdict emitted by the Section 04A G1A poll surface."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

    run_id: UUID = Field(
        ...,
        description="UUID4 identity for the G1A ratification run.",
    )
    surface_id: Section04ASurfaceId = Field(
        default=SECTION_04A_SURFACE_ID,
        description="Closed Section 04A poll-surface identifier.",
    )
    verb: Section04AVerdictVerb = Field(
        ...,
        description="Closed verdict verb set: approve | edit | reject.",
    )
    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the plan unit being ratified.",
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
        description="Lowercase sha256 digest of the reviewed G1 decision card.",
    )
    edit_payload: PlanUnitEditPayload | None = Field(
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

    @field_validator("plan_unit_id", "operator_id", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        if isinstance(value, str):
            return _strip_non_empty(value, field_name=info.field_name)
        return value

    @field_validator("reject_reason", mode="before")
    @classmethod
    def _strip_optional_reject_reason(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="reject_reason")
        return value

    @field_validator("submitted_at")
    @classmethod
    def _require_tz_aware(cls, value: datetime) -> datetime:
        return enforce_tz_aware(value)

    @field_validator("decision_card_digest", mode="before")
    @classmethod
    def _require_sha256(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("decision_card_digest must be lowercase sha256 hex")
        return value

    @model_validator(mode="after")
    def _enforce_verb_payload_consistency(self) -> Section04AOperatorVerdict:
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
            raise ValueError("verb='approve' forbids edit_payload and reject_reason")
        return self


__all__ = [
    "PlanUnitEditPayload",
    "SECTION_04A_SURFACE_ID",
    "Section04AOperatorVerdict",
    "Section04ASurfaceId",
    "Section04AVerdictVerb",
]
