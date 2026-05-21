"""Gary fidelity-slides pre-dispatch writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.parity.contracts import declare_sanctum_alignment

declare_sanctum_alignment(
    writer_id="gary-fidelity-slides",
    sanctum_path="_bmad/memory/bmad-agent-marcus/",
)

FidelitySeverity = Literal["MUST", "SHOULD", "MAY"]


def _strip_non_empty(value: object, *, field_name: str) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{field_name} must be non-empty")
        return stripped
    return value


class VeraFidelityCriterion(BaseModel):
    """Vera-authored criterion carried into Gary's slide package."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    criterion_id: str = Field(
        ...,
        min_length=1,
        description="Stable Vera fidelity criterion identifier.",
    )
    severity: FidelitySeverity = Field(
        ...,
        description="Closed Vera severity: MUST, SHOULD, or MAY.",
    )
    description: str = Field(
        ...,
        min_length=1,
        description="Operator-readable fidelity criterion text.",
    )
    vera_source_ref: str | None = Field(
        default=None,
        description="Optional provenance pointer to the Vera source contract.",
    )

    @field_validator("criterion_id", "description", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)

    @field_validator("vera_source_ref", mode="before")
    @classmethod
    def _strip_optional_source_ref(cls, value: object) -> object:
        if value is None:
            return None
        return _strip_non_empty(value, field_name="vera_source_ref")


class GaryFidelitySlides(BaseModel):
    """Per-plan-unit fidelity criteria package for Gary dispatch."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Plan-unit identifier for this fidelity payload.",
    )
    target_section: str = Field(
        ...,
        min_length=1,
        description="Target course section for the fidelity payload.",
    )
    vera_criteria: list[VeraFidelityCriterion] = Field(
        ...,
        min_length=1,
        description="Vera criteria prepopulated for Gary slide generation.",
    )
    schema_version: int = Field(
        default=1,
        description="Schema version for FR-7c-51 bump-on-change discipline.",
    )

    @field_validator("plan_unit_id", "target_section", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)


def emit_gary_fidelity_slides(
    payload: GaryFidelitySlides,
    output_path: Path,
) -> Path:
    """Write Gary fidelity-slides JSON and return the written path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return output_path


__all__ = [
    "FidelitySeverity",
    "GaryFidelitySlides",
    "VeraFidelityCriterion",
    "emit_gary_fidelity_slides",
]
