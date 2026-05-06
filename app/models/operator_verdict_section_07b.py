"""Section 07B HIL per-slide A/B variant verdict models."""

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

Section07BVerdictVerb = Literal["select", "edit", "reject"]
Section07BSurfaceId = Literal["section_07b_g2m_per_slide_variant"]
SECTION_07B_SURFACE_ID: Section07BSurfaceId = "section_07b_g2m_per_slide_variant"


def _strip_non_empty(value: str, *, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must be non-empty")
    return stripped


class PerSlideVariantPayload(BaseModel):
    """Selected A/B variant for one Section 07B slide."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    selected_variant: Literal["A", "B"] = Field(
        ...,
        description="Selected per-slide variant.",
    )
    rationale: str | None = Field(
        default=None,
        description="Optional operator rationale for the selected variant.",
    )

    @field_validator("rationale", mode="before")
    @classmethod
    def _strip_optional_rationale(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="rationale")
        return value


class PerSlideVariantEditPayload(BaseModel):
    """Field-level edits keyed by slide id for per-slide variant metadata."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    edits: dict[str, dict[str, Any]] = Field(
        ...,
        min_length=1,
        description="Mapping of slide id to field-level variant updates.",
    )

    @field_validator("edits")
    @classmethod
    def _reject_empty_update_blocks(
        cls,
        value: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        normalized: dict[str, dict[str, Any]] = {}
        for slide_id, updates in value.items():
            if not isinstance(slide_id, str):
                raise ValueError("edit slide id must be a string")
            normalized_slide_id = _strip_non_empty(
                slide_id,
                field_name="edit slide id",
            )
            if not updates:
                raise ValueError(
                    f"edit block for slide_id={normalized_slide_id!r} must be non-empty"
                )
            normalized[normalized_slide_id] = updates
        return normalized


class Section07BOperatorVerdict(BaseModel):
    """Tamper-evident verdict emitted by the Section 07B G2M poll surface."""

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=True,
        frozen=True,
    )

    run_id: UUID = Field(
        ...,
        description="UUID4 identity for the per-slide variant run.",
    )
    surface_id: Section07BSurfaceId = Field(
        default=SECTION_07B_SURFACE_ID,
        description="Closed Section 07B per-slide variant surface identifier.",
    )
    verb: Section07BVerdictVerb = Field(
        ...,
        description="Closed verdict verb set: select | edit | reject.",
    )
    slide_id: str = Field(
        ...,
        min_length=1,
        description="Identifier of the slide under A/B variant review.",
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
    select_payload: PerSlideVariantPayload | None = Field(
        default=None,
        description="Required iff verb is select.",
    )
    edit_payload: PerSlideVariantEditPayload | None = Field(
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
    def _enforce_verb_payload_consistency(self) -> Section07BOperatorVerdict:
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
    "PerSlideVariantEditPayload",
    "PerSlideVariantPayload",
    "SECTION_07B_SURFACE_ID",
    "Section07BOperatorVerdict",
    "Section07BSurfaceId",
    "Section07BVerdictVerb",
]
