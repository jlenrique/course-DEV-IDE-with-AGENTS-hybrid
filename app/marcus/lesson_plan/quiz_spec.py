"""Quiz collateral content model (Mine-next N3).

Distinct artifact family from workbook and drill. LO-linked short quiz items
with prompt + choices + expected_answer_focus + source_refs.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.marcus.lesson_plan.event_type_registry import OPEN_ID_REGEX_PATTERN

SCHEMA_VERSION = "0.1"


class QuizSourceRef(BaseModel):
    """One source anchor for a quiz item."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    ref_id: str = Field(..., pattern=OPEN_ID_REGEX_PATTERN)
    locator: str = Field(..., min_length=1)
    excerpt: str = ""


class QuizItem(BaseModel):
    """One LO-linked short quiz practice item."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    item_id: str = Field(..., pattern=OPEN_ID_REGEX_PATTERN)
    learning_objective_id: str = Field(..., pattern=OPEN_ID_REGEX_PATTERN)
    prompt: str = Field(..., min_length=1)
    choices: tuple[str, ...] = Field(default_factory=tuple)
    expected_answer_focus: str = Field(..., min_length=1)
    source_refs: tuple[QuizSourceRef, ...] = Field(default_factory=tuple)

    @field_validator("prompt", "expected_answer_focus")
    @classmethod
    def _non_whitespace(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("prompt/expected_answer_focus must be non-empty")
        return cleaned


class QuizSpec(BaseModel):
    """Deck-companion quiz artifact (distinct from workbook and drill)."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    schema_version: Literal["0.1"] = SCHEMA_VERSION
    kind: Literal["deck-companion-quiz"] = "deck-companion-quiz"
    title: str = "Practice quiz"
    items: tuple[QuizItem, ...] = Field(default_factory=tuple)

    @field_validator("title")
    @classmethod
    def _title_nonempty(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("quiz title must be non-empty")
        return cleaned


__all__ = [
    "SCHEMA_VERSION",
    "QuizItem",
    "QuizSourceRef",
    "QuizSpec",
]
