"""Pydantic source of truth for Irene Pass 2 authoring guidance."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

LOCAL_PNG_PATH_PATTERN = r"^.+[.][Pp][Nn][Gg]$"
VisualDetailLoad = Literal["light", "medium", "heavy"]
ContentDensity = Literal["light", "medium", "heavy"]
BridgeType = Literal["none", "intro", "outro", "pivot", "both", "cluster_boundary"]
CompositionMode = Literal["isolated", "composed"]
ClusterPosition = Literal["establish", "tension", "develop", "resolve"]
ClusterRole = Literal["head", "interstitial"]
ProceduralRule = Literal[
    "behavioral_intent_parity",
    "bridge_cadence",
    "cluster_arc_continuity",
    "motion_perception_confirmation",
    "narration_cue_presence",
    "traceable_visual_references",
]
REQUIRED_PROCEDURAL_RULES: tuple[ProceduralRule, ...] = (
    "behavioral_intent_parity",
    "bridge_cadence",
    "cluster_arc_continuity",
    "motion_perception_confirmation",
    "narration_cue_presence",
    "traceable_visual_references",
)


def _ensure_utc_aware(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("datetime field must be timezone-aware")
    if value.utcoffset() != UTC.utcoffset(value):
        raise ValueError("datetime field must be UTC")
    return value


def _normalized_path(value: str) -> str:
    return value.replace("\\", "/").strip()


class _StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True, strict=True)


class GarySlideOutput(_StrictModel):
    slide_id: str = Field(min_length=1, description="Gary slide identifier.")
    card_number: int = Field(ge=1, description="One-based slide/card order.")
    file_path: str = Field(
        min_length=1,
        pattern=LOCAL_PNG_PATH_PATTERN,
        description="Local downloaded PNG path.",
    )
    source_ref: str = Field(min_length=1, description="Traceable source reference.")

    @field_validator("file_path")
    @classmethod
    def _file_path_must_be_png(cls, value: str) -> str:
        normalized = _normalized_path(value)
        if not normalized.lower().endswith(".png"):
            raise ValueError("file_path must reference a local PNG")
        if normalized.startswith(("http://", "https://")):
            raise ValueError("file_path must not be remote")
        return normalized


class PerceptionArtifact(_StrictModel):
    slide_id: str = Field(min_length=1)
    source_image_path: str = Field(min_length=1, pattern=LOCAL_PNG_PATH_PATTERN)
    visual_elements: list[dict[str, object]] = Field(default_factory=list)

    @field_validator("source_image_path")
    @classmethod
    def _normalize_source_image_path(cls, value: str) -> str:
        return _normalized_path(value)


class VisualReference(_StrictModel):
    element: str = Field(min_length=1)
    location_on_slide: str = Field(min_length=1)
    narration_cue: str = Field(min_length=1)
    perception_source: str = Field(min_length=1)


class SegmentManifestSegment(_StrictModel):
    id: str = Field(min_length=1)
    slide_id: str = Field(min_length=1)
    card_number: int = Field(ge=1)
    narration_text: str = Field(min_length=1)
    behavioral_intent: str = Field(min_length=1)
    visual_file: str = Field(min_length=1, pattern=LOCAL_PNG_PATH_PATTERN)
    visual_detail_load: VisualDetailLoad
    timing_role: str = Field(min_length=1)
    content_density: ContentDensity
    duration_rationale: str = Field(min_length=1)
    bridge_type: BridgeType
    visual_references: list[VisualReference] = Field(min_length=1)
    cluster_id: str | None = None
    cluster_role: ClusterRole | None = None
    cluster_position: ClusterPosition | None = None

    @field_validator("visual_file")
    @classmethod
    def _normalize_visual_file(cls, value: str) -> str:
        return _normalized_path(value)


class SegmentManifest(_StrictModel):
    segments: list[SegmentManifestSegment] = Field(min_length=1)


class IrenePass2AuthoringEnvelope(_StrictModel):
    """Authoring-time contract consumed by Irene prompt guidance."""

    schema_version: Literal["irene-pass-2-authoring.v1"] = "irene-pass-2-authoring.v1"
    run_id: str = Field(min_length=1)
    generated_at_utc: datetime
    composition_mode: CompositionMode
    gary_slide_output: list[GarySlideOutput] = Field(min_length=1)
    perception_artifacts: list[PerceptionArtifact] = Field(min_length=1)
    segment_manifest: SegmentManifest
    narration_script_markers: list[str] = Field(min_length=1)
    procedural_rules: tuple[ProceduralRule, ...] = Field(
        min_length=len(REQUIRED_PROCEDURAL_RULES),
        max_length=len(REQUIRED_PROCEDURAL_RULES),
    )

    @field_validator("generated_at_utc", mode="before")
    @classmethod
    def _parse_generated_at_iso8601(cls, value: object) -> object:
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    @field_validator("procedural_rules", mode="before")
    @classmethod
    def _parse_procedural_rules_sequence(cls, value: object) -> object:
        if isinstance(value, list):
            return tuple(value)
        return value

    @field_validator("generated_at_utc")
    @classmethod
    def _generated_at_must_be_utc_aware(cls, value: datetime) -> datetime:
        return _ensure_utc_aware(value)

    @field_validator("procedural_rules")
    @classmethod
    def _procedural_rules_must_be_complete(
        cls, value: tuple[ProceduralRule, ...]
    ) -> tuple[ProceduralRule, ...]:
        if value != REQUIRED_PROCEDURAL_RULES:
            raise ValueError(
                "procedural_rules must exactly match the validator-enforced rule set"
            )
        return value

    @model_validator(mode="after")
    def _cross_artifact_shape(self) -> IrenePass2AuthoringEnvelope:
        gary_path_by_slide = {
            item.slide_id: _normalized_path(item.file_path)
            for item in self.gary_slide_output
        }
        gary_card_by_slide = {
            item.slide_id: item.card_number
            for item in self.gary_slide_output
        }
        missing_perception = sorted(
            set(gary_path_by_slide)
            - {item.slide_id for item in self.perception_artifacts}
        )
        if missing_perception:
            raise ValueError(
                "perception_artifacts missing slide_id(s): " + ", ".join(missing_perception)
            )
        for artifact in self.perception_artifacts:
            expected = gary_path_by_slide.get(artifact.slide_id)
            if expected is not None and _normalized_path(artifact.source_image_path) != expected:
                raise ValueError(
                    "perception_artifacts source_image_path must match "
                    f"gary_slide_output.file_path for {artifact.slide_id}"
                )

        marker_set = set(self.narration_script_markers)
        unknown_segment_ids = sorted(
            segment.id
            for segment in self.segment_manifest.segments
            if segment.id not in marker_set
        )
        if unknown_segment_ids:
            raise ValueError(
                "segment_manifest segment id(s) absent from narration_script_markers: "
                + ", ".join(unknown_segment_ids)
            )

        gary_slide_ids = set(gary_path_by_slide)
        unknown_segment_slides = sorted(
            segment.slide_id
            for segment in self.segment_manifest.segments
            if segment.slide_id not in gary_slide_ids
        )
        if unknown_segment_slides:
            raise ValueError(
                "segment_manifest references unknown slide_id(s): "
                + ", ".join(unknown_segment_slides)
            )
        segment_visual_mismatches = sorted(
            segment.id
            for segment in self.segment_manifest.segments
            if _normalized_path(segment.visual_file) != gary_path_by_slide.get(segment.slide_id)
        )
        if segment_visual_mismatches:
            raise ValueError(
                "segment_manifest visual_file must match gary_slide_output.file_path for "
                "segment id(s): " + ", ".join(segment_visual_mismatches)
            )

        segment_card_mismatches = sorted(
            segment.id
            for segment in self.segment_manifest.segments
            if segment.card_number != gary_card_by_slide.get(segment.slide_id)
        )
        if segment_card_mismatches:
            raise ValueError(
                "segment_manifest card_number must match gary_slide_output.card_number for "
                "segment id(s): " + ", ".join(segment_card_mismatches)
            )

        missing_cluster_roles = sorted(
            segment.id
            for segment in self.segment_manifest.segments
            if segment.cluster_id is not None and segment.cluster_role is None
        )
        if missing_cluster_roles:
            raise ValueError(
                "cluster_role is required when cluster_id is present for segment id(s): "
                + ", ".join(missing_cluster_roles)
            )
        return self
