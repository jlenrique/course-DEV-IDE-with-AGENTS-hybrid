"""Minimal perception artifact contract consumed by Quinn-R P2-1."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.json_schema import SkipJsonSchema

CoverageState = Literal["perceived", "low-confidence", "not-covered"]
Confidence = Literal["HIGH", "LOW"]
PerceptionProvenance = Literal["png-grounded", "brief-expectation", "not-covered"]


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
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    provider_model_id: str = ""
    source_png_path: str = ""
    provenance: SkipJsonSchema[PerceptionProvenance] = Field(
        default="png-grounded",
        exclude=True,
        description="Internal audit provenance; excluded from public schema/dumps.",
    )

    @field_validator("slide_id")
    @classmethod
    def _slide_id_nonblank(cls, value: str) -> str:
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("slide_id must be non-empty")
        return cleaned


__all__ = ["Confidence", "CoverageState", "PerceptionArtifact", "PerceptionProvenance"]
