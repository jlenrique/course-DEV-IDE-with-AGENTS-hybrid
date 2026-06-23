"""Minimal perception artifact contract consumed by Quinn-R P2-1."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from pydantic.json_schema import SkipJsonSchema

CoverageState = Literal["perceived", "low-confidence", "not-covered"]
Confidence = Literal["HIGH", "LOW"]
PerceptionProvenance = Literal["png-grounded", "brief-expectation", "not-covered"]
ReadingPath = Literal[
    "z_pattern",
    "f_pattern",
    "center_out",
    "top_down",
    "multi_column",
    "grid_quadrant",
    "sequence_numbered",
    "split_image_text",
    "two_up_comparison",
    "text_hero_divider",
    "enumerated_process",
    "diagram_driven",
]
MacroLayout = Literal[
    "split_image_text",
    "text_hero_divider",
    "multi_column",
    "two_pane",
    "card_grid",
    "center_out",
    "diagram_driven",
    "single_text_block",
]
ImageRoleTier = Literal["1", "2", "2_5", "3", "4"]
RoleTier = ImageRoleTier
ImageRoleFlag = Literal["dropped_invalid_tier", "tier_2_5_candidate", "tier_3_quarantined"]
TextSubstructure = Literal[
    "enumerated_process",
    "peer_boxes",
    "comparison_pair",
    "dense_exposition",
    "hero_message",
]
NarrationCadence = Literal["sparse_slow", "moderate", "dense"]
CalloutIntent = Literal["invite_response", "challenge_quiz", "directive_cta"]
ReadingPathFlag = Literal["oppositional_cue"]


class PerceptionArtifact(BaseModel):
    """Legacy-compatible slide perception summary.

    Field names intentionally match the pre-existing perception artifact shape
    used by producer scripts; P2-1 only closes the model and adds coverage.

    Bbox provenance (AC-5, vision-perceiver-real 2026-06-21): each
    ``visual_elements[].bbox`` is an APPROXIMATE normalized ``[x1,y1,x2,y2]``
    region estimate (0..1). These are LLM-estimated and coarse — the
    deterministic reading-path classifier only buckets element centers into
    thirds, so sub-third bbox precision is neither produced by the live gpt-5.5
    perceiver nor relied upon downstream.
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
    reading_path: ReadingPath | None = Field(
        default=None,
        description="Deterministic reading-path classification derived from perceived geometry.",
    )
    macro_layout: MacroLayout | None = Field(
        default=None,
        description="Geometry-derived macro-layout axis for the reading-path tuple.",
    )
    image_roles: list[ImageRoleTier | None] | None = Field(
        default=None,
        description="Per-element image role tiers emitted or deterministically backfilled in S2.",
    )
    image_role_flags: list[ImageRoleFlag] | None = Field(
        default=None,
        description=(
            "S2 side-channel for provisional 2.5 candidates and tier-3 quarantine harvest."
        ),
    )
    text_substructure: TextSubstructure | None = Field(
        default=None,
        description="Geometry-derived text-substructure axis for the reading-path tuple.",
    )
    narration_cadence: NarrationCadence | None = Field(
        default=None,
        description="Density-derived narration cadence axis for the reading-path tuple.",
    )
    callout_intent: CalloutIntent | None = Field(
        default=None,
        description="Optional callout speech-act axis; S1 leaves this unpopulated for S3.",
    )
    reading_path_flags: list[ReadingPathFlag] | None = Field(
        default=None,
        description="Deterministic S1 side-channel flags for later reading-path escalation.",
    )
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


__all__ = [
    "CalloutIntent",
    "Confidence",
    "CoverageState",
    "ImageRoleFlag",
    "ImageRoleTier",
    "MacroLayout",
    "NarrationCadence",
    "PerceptionArtifact",
    "PerceptionProvenance",
    "ReadingPathFlag",
    "ReadingPath",
    "RoleTier",
    "TextSubstructure",
]
