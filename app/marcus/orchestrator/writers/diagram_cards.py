"""Gary diagram-cards pre-dispatch writer."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, field_validator

from app.parity.contracts import declare_sanctum_alignment

declare_sanctum_alignment(
    writer_id="gary-diagram-cards",
    sanctum_path="_bmad/memory/bmad-agent-marcus/",
)

DiagramVisualKind = Literal["flowchart", "sequence", "comparison", "literal-visual"]


def _strip_non_empty(value: object, *, field_name: str) -> object:
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped:
            raise ValueError(f"{field_name} must be non-empty")
        return stripped
    return value


class DiagramCard(BaseModel):
    """Per-slide diagram requirement for Gary."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    slide_index: int = Field(..., ge=1, description="One-based slide index.")
    visual_kind: DiagramVisualKind = Field(
        ...,
        description="Closed diagram visual kind for Gary rendering.",
    )
    specification: str = Field(
        ...,
        min_length=1,
        description="Operator-authored per-slide visual specification.",
    )
    caption: str | None = Field(
        default=None,
        description="Optional rendering caption for the diagram card.",
    )

    @field_validator("specification", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)

    @field_validator("caption", mode="before")
    @classmethod
    def _strip_optional_caption(cls, value: object) -> object:
        if value is None:
            return None
        return _strip_non_empty(value, field_name="caption")


class GaryDiagramCards(BaseModel):
    """Per-plan-unit diagram card package for Gary dispatch."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    plan_unit_id: str = Field(
        ...,
        min_length=1,
        description="Plan-unit identifier for this diagram-card payload.",
    )
    target_section: str = Field(
        ...,
        min_length=1,
        description="Target course section for the diagram-card payload.",
    )
    cards: list[DiagramCard] = Field(
        ...,
        min_length=1,
        description="Diagram cards for literal visual requirements.",
    )
    schema_version: int = Field(
        default=1,
        description="Schema version for FR-7c-51 bump-on-change discipline.",
    )

    @field_validator("plan_unit_id", "target_section", mode="before")
    @classmethod
    def _strip_required_strings(cls, value: object, info: ValidationInfo) -> object:
        return _strip_non_empty(value, field_name=info.field_name)


def emit_gary_diagram_cards(payload: GaryDiagramCards, output_path: Path) -> Path:
    """Write Gary diagram-cards JSON and return the written path."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True),
        encoding="utf-8",
        newline="\n",
    )
    return output_path


__all__ = [
    "DiagramCard",
    "DiagramVisualKind",
    "GaryDiagramCards",
    "emit_gary_diagram_cards",
]
