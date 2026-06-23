"""Vision specialist payload and provider response contracts."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator

from app.models.perception.perception_artifact import (
    Confidence,
    CoverageState,
    ImageRoleTier,
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
    """Live gpt-5.5 perception response parsed before conversion to PerceptionArtifact.

    Bbox provenance (AC-5, vision-perceiver-real 2026-06-21): each
    ``visual_elements[].bbox`` is an APPROXIMATE normalized region estimate in
    ``[x1, y1, x2, y2]`` form (each coordinate in ``0..1``). These are
    LLM-estimated and coarse — the deterministic reading-path classifier only
    buckets element centers into thirds, so sub-third precision is neither
    produced by the perceiver nor relied upon downstream.
    """

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

    @field_validator("visual_elements")
    @classmethod
    def _role_tier_values_are_closed(
        cls, value: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        adapter = TypeAdapter(ImageRoleTier)
        for index, element in enumerate(value):
            if not isinstance(element, dict):
                raise ValueError(f"visual_elements[{index}] must be an object")
            if "role_tier" in element and element["role_tier"] is not None:
                adapter.validate_python(element["role_tier"])
        return value


__all__ = ["CONSUMED_PAYLOAD_KEYS", "VisionProviderResponse"]
