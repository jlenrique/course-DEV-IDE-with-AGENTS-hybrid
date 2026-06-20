"""Vision specialist payload and provider response contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.perception.perception_artifact import (
    Confidence,
    CoverageState,
    PerceptionProvenance,
)

CONSUMED_PAYLOAD_KEYS: frozenset[str] = frozenset(
    {
        "gary_slide_output",
        "slides",
        "run_id",
        "runs_root",
    }
)


class VisionProviderResponse(BaseModel):
    """Pinned provider response parsed before conversion to PerceptionArtifact."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    slide_id: str = Field(..., min_length=1)
    confidence: Confidence
    coverage: CoverageState = "perceived"
    provenance: PerceptionProvenance = "png-grounded"
    visual_elements: list[dict[str, Any]] = Field(default_factory=list)
    extracted_text: str = ""
    layout_description: str = ""
    slide_title: str = ""
    text_blocks: list[dict[str, Any] | str] = Field(default_factory=list)
    artifact_path: str = ""
    card_number: int | str | None = None
    confidence_score: float | None = Field(default=None, ge=0.0, le=1.0)
    provider_model_id: str = ""
    source_png_path: str = ""


__all__ = ["CONSUMED_PAYLOAD_KEYS", "VisionProviderResponse"]
