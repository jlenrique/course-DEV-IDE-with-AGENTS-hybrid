"""Gary slide-content pre-dispatch writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.parity.contracts import declare_sanctum_alignment

declare_sanctum_alignment(
    writer_id="gary-slide-content",
    sanctum_path="_bmad/memory/bmad-agent-marcus/",
)

SlideContentKind = Literal["narrative", "exposition", "summary"]


def _strip_non_empty(value: object, *, field_name: str) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{field_name} must be non-empty")
        return stripped
    return value


class SlideContentEntry(BaseModel):
    """Per-slide text payload prepared for Gary."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    slide_index: int = Field(..., ge=1, description="One-based slide index.")
    title: str = Field(..., min_length=1, description="Slide title text.")
    body: str = Field(..., min_length=1, description="Slide body text.")
    content_kind: SlideContentKind = Field(
        ...,
        description="Closed slide content kind for Gary payload shaping.",
    )

    @field_validator("title", "body", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)


class GarySlideContent(BaseModel):
    """Per-plan-unit slide content package for Gary dispatch."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Plan-unit identifier for this Gary pre-dispatch payload.",
    )
    target_section: str = Field(
        ...,
        min_length=1,
        description="Target course section for the slide content payload.",
    )
    slides: list[SlideContentEntry] = Field(
        ...,
        min_length=1,
        description="Slide content entries for the plan unit.",
    )
    schema_version: int = Field(
        default=1,
        description="Schema version for FR-7c-51 bump-on-change discipline.",
    )

    @field_validator("plan_unit_id", "target_section", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)


def emit_gary_slide_content(payload: GarySlideContent, output_path: Path) -> Path:
    """Write Gary slide-content JSON and return the written path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return output_path


__all__ = [
    "GarySlideContent",
    "SlideContentEntry",
    "SlideContentKind",
    "emit_gary_slide_content",
]
