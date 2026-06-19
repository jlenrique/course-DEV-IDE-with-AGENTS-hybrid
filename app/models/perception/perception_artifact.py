"""Minimal perception artifact contract consumed by Quinn-R P2-1."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

CoverageState = Literal["perceived", "low-confidence", "not-covered"]
Confidence = Literal["HIGH", "LOW"]


class PerceptionArtifact(BaseModel):
    """Legacy-compatible slide perception summary.

    Field names intentionally match the pre-existing perception artifact shape
    used by producer scripts; P2-1 only closes the model and adds coverage.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    confidence: Confidence
    visual_elements: list[dict[str, Any]] = Field(default_factory=list)
    extracted_text: str = ""
    layout_description: str = ""
    slide_title: str = ""
    text_blocks: list[dict[str, Any] | str] = Field(default_factory=list)
    artifact_path: str = ""
    slide_id: str
    card_number: int | str | None = None
    coverage: CoverageState = "perceived"

    @field_validator("slide_id")
    @classmethod
    def _slide_id_nonblank(cls, value: str) -> str:
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("slide_id must be non-empty")
        return cleaned


__all__ = ["Confidence", "CoverageState", "PerceptionArtifact"]
