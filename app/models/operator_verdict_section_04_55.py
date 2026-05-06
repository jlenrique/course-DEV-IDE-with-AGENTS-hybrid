"""Section 04.55 HIL run-constants lock verdict models."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

Section04_55VerdictVerb = Literal["lock", "edit", "reject"]
Section04_55SurfaceId = Literal["section_04_55_g1_5_run_constants"]
SECTION_04_55_SURFACE_ID: Section04_55SurfaceId = (
    "section_04_55_g1_5_run_constants"
)


class RunConstantsEditPayload(BaseModel):
    """Field-level run-constants edits keyed by constants path or field name."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    edits: dict[str, Any] = Field(
        ...,
        min_length=1,
        description="Mapping of run-constants fields or paths to replacement values.",
    )

    @field_validator("edits")
    @classmethod
    def _reject_blank_edit_paths(cls, value: dict[str, Any]) -> dict[str, Any]:
        for field_path in value:
            if not field_path.strip():
                raise ValueError("edit field path must be non-empty")
        return value


class Section04_55OperatorVerdict(BaseModel):  # noqa: N801
    """Tamper-evident verdict emitted by the Section 04.55 G1.5 surface."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

    run_id: UUID = Field(..., description="UUID4 identity for the enclosing run.")
    surface_id: Section04_55SurfaceId = Field(
        default=SECTION_04_55_SURFACE_ID,
        description="Closed Section 04.55 run-constants surface identifier.",
    )
    verb: Section04_55VerdictVerb = Field(..., description="lock | edit | reject")
    operator_id: str = Field(
        ...,
        min_length=1,
        pattern=r"^[a-zA-Z][a-zA-Z0-9_-]+$",
        description="Operator identifier.",
    )
    run_constants_id: str = Field(
        ...,
        min_length=1,
        description="Stable identity for the reviewed run-constants payload.",
    )
    submitted_at: datetime = Field(
        default_factory=lambda: datetime.now(tz=UTC),
        description="Timezone-aware verdict submission time.",
    )
    decision_card_digest: str = Field(
        ...,
        description="Lowercase sha256 digest of the reviewed run-constants payload.",
    )
    edit_payload: RunConstantsEditPayload | None = Field(
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

    @field_validator("run_constants_id")
    @classmethod
    def _strip_non_empty_run_constants_id(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("run_constants_id must be non-empty")
        return stripped

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

    @field_validator("reject_reason")
    @classmethod
    def _strip_optional_reject_reason(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("reject_reason must be non-empty when supplied")
        return stripped

    @model_validator(mode="after")
    def _enforce_verb_payload_consistency(self) -> Section04_55OperatorVerdict:
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
            raise ValueError("verb='lock' forbids edit_payload and reject_reason")
        return self


__all__ = [
    "RunConstantsEditPayload",
    "SECTION_04_55_SURFACE_ID",
    "Section04_55OperatorVerdict",
    "Section04_55SurfaceId",
    "Section04_55VerdictVerb",
]
