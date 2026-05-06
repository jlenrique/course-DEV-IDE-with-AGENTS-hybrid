"""Section 07C storyboard-build verdict models."""

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

Section07CBuildVerb = Literal["submit", "edit", "discard"]
Section07CSurfaceId = Literal["section_07c_storyboard_build"]
SECTION_07C_SURFACE_ID: Section07CSurfaceId = "section_07c_storyboard_build"


def _strip_non_empty(value: str, *, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must be non-empty")
    return stripped


class StoryboardBuildPayload(BaseModel):
    """Submitted storyboard build payload for Section 07C."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    target_section: str = Field(
        ...,
        min_length=1,
        description="Target course section for the storyboard build.",
    )
    storyboard_html_path: str = Field(
        ...,
        min_length=1,
        description="Relative path to the emitted HTML reviewer artifact.",
    )
    slide_count: int = Field(
        ...,
        ge=1,
        description="Number of slides represented in the storyboard artifact.",
    )
    storyboard_html_digest: str = Field(
        ...,
        description="Lowercase sha256 digest of the emitted HTML artifact bytes.",
    )

    @field_validator("target_section", "storyboard_html_path", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        if isinstance(value, str):
            return _strip_non_empty(value, field_name=info.field_name)
        return value

    @field_validator("storyboard_html_path")
    @classmethod
    def _require_html_suffix(cls, value: str) -> str:
        if not value.lower().endswith(".html"):
            raise ValueError("storyboard_html_path must end with .html")
        return value

    @field_validator("storyboard_html_digest", mode="before")
    @classmethod
    def _require_html_sha256(cls, value: object) -> object:
        if isinstance(value, str):
            value = value.strip()
            if not re.fullmatch(r"[0-9a-f]{64}", value):
                raise ValueError("storyboard_html_digest must be lowercase sha256 hex")
        return value


class StoryboardEditPayload(BaseModel):
    """Field-level edits for a submitted storyboard build."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    edits: dict[str, Any] = Field(
        ...,
        min_length=1,
        description="Mapping of storyboard field names or paths to replacements.",
    )

    @field_validator("edits")
    @classmethod
    def _reject_blank_edit_keys(cls, value: dict[str, Any]) -> dict[str, Any]:
        normalized: dict[str, Any] = {}
        for field_name, field_value in value.items():
            if not isinstance(field_name, str):
                raise ValueError("edit field name must be a string")
            normalized[_strip_non_empty(field_name, field_name="edit field name")] = (
                field_value
            )
        return normalized


class Section07COperatorVerdict(BaseModel):
    """Tamper-evident verdict emitted by the Section 07C build surface."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    run_id: UUID = Field(..., description="UUID4 identity for the storyboard build run.")
    surface_id: Section07CSurfaceId = Field(
        default=SECTION_07C_SURFACE_ID,
        description="Closed Section 07C build-surface identifier.",
    )
    verb: Section07CBuildVerb = Field(
        ...,
        description="Closed build verb set: submit | edit | discard.",
    )
    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Plan-unit identifier for the storyboard build.",
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
        description="Lowercase sha256 digest of the storyboard build payload.",
    )
    build_payload: StoryboardBuildPayload | None = Field(
        default=None,
        description="Required iff verb is submit.",
    )
    edit_payload: StoryboardEditPayload | None = Field(
        default=None,
        description="Required iff verb is edit.",
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
    def _enforce_verb_payload_consistency(self) -> Section07COperatorVerdict:
        if self.verb == "submit":
            if self.build_payload is None:
                raise ValueError("verb='submit' requires build_payload")
            if self.edit_payload is not None:
                raise ValueError("verb='submit' forbids edit_payload")
            return self
        if self.verb == "edit":
            if self.edit_payload is None:
                raise ValueError("verb='edit' requires edit_payload")
            if self.build_payload is not None:
                raise ValueError("verb='edit' forbids build_payload")
            return self
        if self.build_payload is not None or self.edit_payload is not None:
            raise ValueError("verb='discard' forbids build_payload and edit_payload")
        return self


__all__ = [
    "SECTION_07C_SURFACE_ID",
    "Section07CBuildVerb",
    "Section07COperatorVerdict",
    "Section07CSurfaceId",
    "StoryboardBuildPayload",
    "StoryboardEditPayload",
]
