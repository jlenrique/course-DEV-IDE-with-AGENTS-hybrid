"""Section 06B literal-visual operator-build verdict models."""

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

Section06BBuildVerb = Literal["submit", "edit", "discard"]
Section06BSurfaceId = Literal["section_06b_literal_visual_build"]
VisualSpecKind = Literal["flowchart", "sequence", "comparison", "literal-visual"]
SECTION_06B_SURFACE_ID: Section06BSurfaceId = "section_06b_literal_visual_build"


def _strip_non_empty(value: str, *, field_name: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{field_name} must be non-empty")
    return stripped


class SlideVisualSpecification(BaseModel):
    """Operator-authored visual specification for one slide."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    slide_index: int = Field(..., ge=1, description="One-based slide index.")
    visual_kind: VisualSpecKind = Field(
        ...,
        description="Closed visual specification kind.",
    )
    specification: str = Field(
        ...,
        min_length=1,
        description="Operator-authored per-slide visual specification.",
    )
    caption: str | None = Field(
        default=None,
        description="Optional rendering caption.",
    )

    @field_validator("specification", mode="before")
    @classmethod
    def _strip_specification(cls, value: object, info: ValidationInfo) -> object:
        if isinstance(value, str):
            return _strip_non_empty(value, field_name=info.field_name)
        return value

    @field_validator("caption", mode="before")
    @classmethod
    def _strip_caption(cls, value: object) -> object:
        if value is None:
            return None
        if isinstance(value, str):
            return _strip_non_empty(value, field_name="caption")
        return value


class LiteralVisualBuildPayload(BaseModel):
    """Submitted literal-visual build payload for Section 06B."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    target_section: str = Field(
        ...,
        min_length=1,
        description="Target course section for the literal-visual build.",
    )
    slide_specifications: list[SlideVisualSpecification] = Field(
        ...,
        min_length=1,
        description="Operator-authored slide visual specifications.",
    )

    @field_validator("target_section", mode="before")
    @classmethod
    def _strip_target_section(cls, value: object, info: ValidationInfo) -> object:
        if isinstance(value, str):
            return _strip_non_empty(value, field_name=info.field_name)
        return value


class LiteralVisualEditPayload(BaseModel):
    """Field-level edits for a literal-visual build payload."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    edits: dict[str, Any] = Field(
        ...,
        min_length=1,
        description="Mapping of literal-visual field names or paths to replacements.",
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


class Section06BOperatorVerdict(BaseModel):
    """Tamper-evident verdict emitted by the Section 06B build surface."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True, frozen=True)

    run_id: UUID = Field(..., description="UUID4 identity for the build run.")
    surface_id: Section06BSurfaceId = Field(
        default=SECTION_06B_SURFACE_ID,
        description="Closed Section 06B build-surface identifier.",
    )
    verb: Section06BBuildVerb = Field(
        ...,
        description="Closed build verb set: submit | edit | discard.",
    )
    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Plan-unit identifier for the literal-visual build.",
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
        description="Lowercase sha256 digest of the build payload or upstream source.",
    )
    build_payload: LiteralVisualBuildPayload | None = Field(
        default=None,
        description="Required iff verb is submit.",
    )
    edit_payload: LiteralVisualEditPayload | None = Field(
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
    def _enforce_verb_payload_consistency(self) -> Section06BOperatorVerdict:
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
    "LiteralVisualBuildPayload",
    "LiteralVisualEditPayload",
    "SECTION_06B_SURFACE_ID",
    "Section06BBuildVerb",
    "Section06BOperatorVerdict",
    "Section06BSurfaceId",
    "SlideVisualSpecification",
    "VisualSpecKind",
]
