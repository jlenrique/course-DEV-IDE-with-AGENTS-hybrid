"""Drill collateral content model (Mine 5).

Distinct artifact family from ``WorkbookSpec`` (kind stays closed to workbook).
Minimal schema: LO-linked short practice items with prompt + expected_focus +
source_refs.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.marcus.lesson_plan.event_type_registry import OPEN_ID_REGEX_PATTERN

SCHEMA_VERSION = "0.1"


class DrillSourceRef(BaseModel):
    """One source anchor for a drill practice item."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    ref_id: str = Field(..., pattern=OPEN_ID_REGEX_PATTERN)
    locator: str = Field(..., min_length=1)
    excerpt: str = ""


class DrillPracticeItem(BaseModel):
    """One LO-linked short practice item."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    item_id: str = Field(..., pattern=OPEN_ID_REGEX_PATTERN)
    learning_objective_id: str = Field(..., pattern=OPEN_ID_REGEX_PATTERN)
    prompt: str = Field(..., min_length=1)
    expected_focus: str = Field(..., min_length=1)
    source_refs: tuple[DrillSourceRef, ...] = Field(default_factory=tuple)

    @field_validator("prompt", "expected_focus")
    @classmethod
    def _non_whitespace(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("prompt/expected_focus must be non-empty after strip")
        return cleaned


class DrillSpec(BaseModel):
    """Deck-companion drill artifact (distinct from workbook)."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: Literal["0.1"] = SCHEMA_VERSION
    kind: Literal["deck-companion-drill"] = "deck-companion-drill"
    title: str = "Practice drill"
    items: tuple[DrillPracticeItem, ...] = Field(default_factory=tuple)

    @field_validator("title")
    @classmethod
    def _title_nonempty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("drill title must be non-empty")
        return cleaned


__all__ = [
    "SCHEMA_VERSION",
    "DrillPracticeItem",
    "DrillSourceRef",
    "DrillSpec",
]
