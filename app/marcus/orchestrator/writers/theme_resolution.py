"""Gary theme-resolution pre-dispatch writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.parity.contracts import declare_sanctum_alignment

declare_sanctum_alignment(
    writer_id="gary-theme-resolution",
    sanctum_path="_bmad/memory/bmad-agent-marcus/",
)

ThemePaletteHint = Literal["light", "dark", "high-contrast", "brand-default"]


def _strip_non_empty(value: object, *, field_name: str) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{field_name} must be non-empty")
        return stripped
    return value


class ResolvedTheme(BaseModel):
    """Resolved Gary theme metadata."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    theme_name: str = Field(
        ...,
        min_length=1,
        description="Resolved Gary theme name.",
    )
    palette: ThemePaletteHint = Field(
        ...,
        description="Closed palette hint for Gary theme selection.",
    )
    template_intent: str | None = Field(
        default=None,
        description="Optional Gary template intent hint.",
    )

    @field_validator("theme_name", mode="before")
    @classmethod
    def _strip_theme_name(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)

    @field_validator("template_intent", mode="before")
    @classmethod
    def _strip_template_intent(cls, value: object) -> object:
        if value is None:
            return None
        return _strip_non_empty(value, field_name="template_intent")


class GaryThemeResolution(BaseModel):
    """Resolved theme payload for Gary dispatch."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Plan-unit identifier for this theme payload.",
    )
    target_section: str = Field(
        ...,
        min_length=1,
        description="Target course section for the theme payload.",
    )
    experience_profile_id: str = Field(
        ...,
        min_length=1,
        description="Experience profile used to resolve the theme.",
    )
    creative_directive_id: str | None = Field(
        default=None,
        description="Optional creative directive provenance identifier.",
    )
    resolved_theme: ResolvedTheme = Field(
        ...,
        description="Resolved Gary theme details.",
    )
    schema_version: int = Field(
        default=1,
        description="Schema version for FR-7c-51 bump-on-change discipline.",
    )

    @field_validator(
        "plan_unit_id",
        "target_section",
        "experience_profile_id",
        mode="before",
    )
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)

    @field_validator("creative_directive_id", mode="before")
    @classmethod
    def _strip_optional_creative_directive_id(cls, value: object) -> object:
        if value is None:
            return None
        return _strip_non_empty(value, field_name="creative_directive_id")


def emit_gary_theme_resolution(
    payload: GaryThemeResolution,
    output_path: Path,
) -> Path:
    """Write Gary theme-resolution JSON and return the written path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return output_path


__all__ = [
    "GaryThemeResolution",
    "ResolvedTheme",
    "ThemePaletteHint",
    "emit_gary_theme_resolution",
]
