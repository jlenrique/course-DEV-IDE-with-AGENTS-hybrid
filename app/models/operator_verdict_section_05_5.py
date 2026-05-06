"""Section 05.5 HIL per-slide mode verdict models."""

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

Section05_5VerdictVerb = Literal["select", "edit", "reject"]
Section05_5SurfaceId = Literal["section_05_5_g2b_per_slide_mode"]
SECTION_05_5_SURFACE_ID: Section05_5SurfaceId = (
    "section_05_5_g2b_per_slide_mode"
)
PerSlideMode = Literal["narrated-deck", "motion-enabled-narrated-lesson"]


def _strip_non_empty(value: str, *, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must be non-empty")
    return stripped


class PerSlideModePayload(BaseModel):
    """Selected presentation mode for one slide."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    selected_mode: PerSlideMode = Field(
        ...,
        description="Selected per-slide presentation mode.",
    )
    rationale: str | None = Field(
        default=None,
        description="Optional operator rationale for the selected mode.",
    )

    @field_validator("rationale", mode="before")
    @classmethod
    def _strip_optional_rationale(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="rationale")
        return value


class PerSlideModeEditPayload(BaseModel):
    """Field-level edits for per-slide mode candidates or metadata."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    updates: dict[str, Any] = Field(
        ...,
        min_length=1,
        description="Mapping of per-slide mode field names or paths to replacement values.",
    )

    @field_validator("updates")
    @classmethod
    def _reject_blank_update_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for field_name, field_value in value.items():
            if not isinstance(field_name, str):
                raise ValueError("edit field name must be a string")
            normalized[_strip_non_empty(field_name, field_name="edit field name")] = (
                field_value
            )
        return normalized


class Section05_5OperatorVerdict(BaseModel):  # noqa: N801
    """Tamper-evident verdict emitted by the Section 05.5 G2B poll surface."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

    run_id: UUID = Field(
        ...,
        description="UUID4 identity for the per-slide mode run.",
    )
    surface_id: Section05_5SurfaceId = Field(
        default=SECTION_05_5_SURFACE_ID,
        description="Closed Section 05.5 per-slide mode surface identifier.",
    )
    verb: Section05_5VerdictVerb = Field(
        ...,
        description="Closed verdict verb set: select | edit | reject.",
    )
    slide_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the slide whose presentation mode is under review.",
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
        description="Lowercase sha256 digest of the reviewed G2C card.",
    )
    select_payload: PerSlideModePayload | None = Field(
        default=None,
        description="Required iff verb is select.",
    )
    edit_payload: PerSlideModeEditPayload | None = Field(
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

    @field_validator("slide_id", "operator_id", mode="before")
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
    def _enforce_verb_payload_consistency(self) -> Section05_5OperatorVerdict:
        if self.verb == "select":
            if self.select_payload is None:
                raise ValueError("verb='select' requires select_payload")
            if self.edit_payload is not None or self.reject_reason is not None:
                raise ValueError(
                    "verb='select' forbids edit_payload and reject_reason"
                )
            return self
        if self.verb == "edit":
            if self.edit_payload is None:
                raise ValueError("verb='edit' requires edit_payload")
            if self.select_payload is not None or self.reject_reason is not None:
                raise ValueError(
                    "verb='edit' forbids select_payload and reject_reason"
                )
            return self
        if self.reject_reason is None:
            raise ValueError("verb='reject' requires reject_reason")
        if self.select_payload is not None or self.edit_payload is not None:
            raise ValueError("verb='reject' forbids select_payload and edit_payload")
        return self


__all__ = [
    "SECTION_05_5_SURFACE_ID",
    "PerSlideMode",
    "PerSlideModeEditPayload",
    "PerSlideModePayload",
    "Section05_5OperatorVerdict",
    "Section05_5SurfaceId",
    "Section05_5VerdictVerb",
]
