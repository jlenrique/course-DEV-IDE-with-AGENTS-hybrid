"""Section 02A HIL poll-surface verdict models."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.state._base import enforce_tz_aware, enforce_uuid4_version

Section02AVerdictVerb = Literal["approve", "edit", "reject"]
Section02ASurfaceId = Literal["section_02a_g0_poll"]
SECTION_02A_SURFACE_ID: Section02ASurfaceId = "section_02a_g0_poll"


class DirectiveEditPayload(BaseModel):
    """Field-level edits keyed by DirectiveSource ``ref_id``."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    edits: dict[str, dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="Mapping of source id to field-level updates.",
    )

    @field_validator("edits")
    @classmethod
    def _reject_empty_update_blocks(
        cls,
        value: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        for ref_id, updates in value.items():
            if not ref_id:
                raise ValueError("edit source id must be non-empty")
            if not updates:
                raise ValueError(f"edit block for {ref_id!r} must be non-empty")
        return value


class Section02AOperatorVerdict(BaseModel):
    """Tamper-evident verdict emitted by the Section 02A G0 poll surface."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

    run_id: UUID = Field(..., description="UUID4 identity for the directive run.")
    surface_id: Section02ASurfaceId = Field(
        default=SECTION_02A_SURFACE_ID,
        description="Closed Section 02A poll-surface identifier.",
    )
    verb: Section02AVerdictVerb = Field(..., description="approve | edit | reject")
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
        description="Lowercase sha256 digest of the reviewed directive payload.",
    )
    edit_payload: DirectiveEditPayload | None = Field(
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
    def _enforce_verb_payload_consistency(self) -> Section02AOperatorVerdict:
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
    "DirectiveEditPayload",
    "SECTION_02A_SURFACE_ID",
    "Section02AOperatorVerdict",
    "Section02ASurfaceId",
    "Section02AVerdictVerb",
]
