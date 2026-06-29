"""Pydantic source of truth for Irene Pass 2 authoring guidance.

The PerceptionArtifact below is a minimal authoring-envelope projection. It is
compatible with the rich upstream app.models.perception.PerceptionArtifact, but
it is not a runtime grounding authority. Irene Pass 2 grounds on the rich
vision-produced model and may project that evidence down only for template and
validator compatibility.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.perception import PerceptionArtifact as RichPerceptionArtifact

# Pattern is intentionally stricter than runtime Pydantic field validators:
# Rust-regex (Pydantic v2) does not support negative lookahead, so URL schemes
# are rejected via "no colons except optional Windows drive prefix" instead.
# Trade-off: rejects local paths with colons in non-drive positions (Mac classic
# paths; rare Linux filenames). Trade-off operator-ratified 2026-04-28 per
# dispatch decision_needed resolution. Defense-in-depth remains in field
# validators below.
LOCAL_PNG_PATH_PATTERN = r"^(?:[A-Za-z]:[\\/])?[^:]+[.][Pp][Nn][Gg]$"
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

    @field_validator("file_path", mode="before")
    @classmethod
    def _file_path_must_be_png(cls, value: object) -> object:
        if not isinstance(value, str):
            return value
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


def project_rich_perception_for_authoring(
    artifact: RichPerceptionArtifact | dict[str, object],
) -> PerceptionArtifact:
    """Project rich vision evidence into the minimal authoring-envelope shape."""
    rich = RichPerceptionArtifact.model_validate(artifact)
    return PerceptionArtifact(
        slide_id=rich.slide_id,
        source_image_path=_normalized_path(rich.source_png_path or rich.artifact_path),
        visual_elements=rich.visual_elements,
    )


class VisualReference(_StrictModel):
    element: str = Field(min_length=1)
    location_on_slide: str = Field(min_length=1)
    narration_cue: str = Field(min_length=1)
    perception_source: str = Field(min_length=1)


# --------------------------------------------------------------------------- #
# Directed-voice contract (P5 directed-voice arc, Step 1).
# FROZEN STEP-1 CONTRACT — schema_version "voice-direction.v1". Authority:
# `_bmad-output/planning-artifacts/p5-directed-voice-arc-strawman-2026-06-27.md`
# §G-RECONCILED (Marcus control-card override — AUTHORITATIVE over §G field
# specifics). `voice_direction` is delivery METADATA only: it never carries
# narration text and never relaxes the figure-citation gate (the gate reads
# narration_text exclusively — see app/specialists/irene/graph.py:_assert_figure_
# citations_within_perceived). `delivery_tag` is generation-text-only and is
# ISOLATED from the figure-gated displayed narration (Card 3 + ENRIQUE-A5). The
# mapper that turns this into TTS settings is the pure leaf
# app/specialists/_shared/voice_direction_map.py (consumed at Step 4).
# --------------------------------------------------------------------------- #
RenderStrategy = Literal["tts", "dialogue"]
EmotionalTone = Literal[
    "neutral", "warm", "concerned", "urgent", "reflective", "encouraging"
]
Pace = Literal["slower", "neutral", "faster"]
Energy = Literal["low", "medium", "high"]
VoiceDirectionSource = Literal["role-derived", "cd-authored", "operator-override"]
# Story enhanced-vo.2 (Slice 1): closed rhetorical-role taxonomy for the v3
# provider-text compiler. ADDITIVE optional field (NOT a schema_version bump). The
# model ACCEPTS the full taxonomy; the compiler
# (app/specialists/_shared/voice_provider_text.py) POPULATES only `warm_callback`
# (STRUCTURAL) + `contrast_emphasis` (TONAL) this slice — the rest are
# accepted-but-deferred (compiler fails loud if asked to render them). Mirrors the
# audition variant slugs (manifest variants), minus the no-role neutral baseline.
RhetoricalRole = Literal[
    "warm_callback",
    "contrast_emphasis",
    "curious_pivot",
    "clinical_seriousness",
    "breakthrough_moment",
    "confidential_aside",
    "restrained_urgency",
    "slow_reflective",
]


class ElevenLabsSettings(_StrictModel):
    """Optional explicit per-field ElevenLabs override.

    Mirrors `scripts/api_clients/elevenlabs_client.text_to_speech()` params. Any
    field set here wins over a direction-derived value at mapping time (per-field
    precedence; see voice_direction_map.map_voice_direction_to_tts).
    """

    # min_length=1: an empty-string voice_id is falsy-but-valid and would
    # short-circuit every precedence tier in the mapper, flowing "" to the TTS
    # dispatcher (Step 4). Reject it at the contract boundary.
    voice_id: str | None = Field(default=None, min_length=1)
    stability: float | None = Field(default=None, ge=0.0, le=1.0)
    similarity_boost: float | None = Field(default=None, ge=0.0, le=1.0)
    style: float | None = Field(default=None, ge=0.0, le=1.0)
    model_id: str | None = None
    speed: float | None = Field(default=None, ge=0.7, le=1.2)


class DialogueTurn(_StrictModel):
    """A single speaker turn (MODELED in v1, NOT consumed in v1)."""

    # FOLLOW-ON `dialogue-turns-grounding-validator-when-consumed`: when the
    # Text-to-Dialogue follow-on consumes dialogue_turns, enforce IR-4 with a
    # real validator (union of turn texts subset of figure-gated narration_text).
    # v1 is correctly inert/docstring-only.
    speaker: str = Field(min_length=1)
    text: str = Field(
        min_length=1,
        description=(
            "When consumed (Text-to-Dialogue follow-on, NOT v1), the "
            "concatenation of turn texts MUST be a partition/derivation of the "
            "segment's already-figure-gated narration_text; no turn may "
            "introduce speech that bypasses the figure-citation gate."
        ),
    )
    # min_length=1: reject empty-string voice_id (same rationale as
    # ElevenLabsSettings.voice_id above).
    voice_id: str | None = Field(default=None, min_length=1)


class VoiceDirection(_StrictModel):
    """Per-segment delivery direction (FROZEN STEP-1 CONTRACT, §G-RECONCILED)."""

    schema_version: Literal["voice-direction.v1"] = "voice-direction.v1"
    # FOLLOW-ON: fail-loud on unsupported render_strategy is a Step-4
    # Enrique-consumption AC (the dispatcher rejects non-`tts` at consume time);
    # at Step 1 `dialogue` is schema-tolerated + mapper-inert.
    render_strategy: RenderStrategy = "tts"
    delivery_intent: str | None = Field(default=None, max_length=500)
    emotional_tone: EmotionalTone | None = None
    pace: Pace | None = None
    energy: Energy | None = None
    # Story enhanced-vo.2 (Slice 1): per-segment rhetorical role consumed by the v3
    # provider-text compiler at synthesis (effective model == eleven_v3). Additive,
    # optional, default None -> directed-voice-OFF / non-v3 runs stay byte-identical
    # (the model is extra="forbid", so the field MUST be declared to be carried).
    rhetorical_role: RhetoricalRole | None = None
    # Generation-text-only delivery cue (e.g. "[thoughtfully]"). ISOLATED from
    # the figure-gated displayed narration (Card 3 + ENRIQUE-A5): it is NEVER
    # injected into the learner-facing/gated narration_text and never reaches
    # the figure-citation gate. Free-text by design (no substring grounding).
    delivery_tag: str | None = Field(default=None, max_length=120)
    pause_before_seconds: float | None = Field(default=None, ge=0.0, le=5.0)
    pause_after_seconds: float | None = Field(default=None, ge=0.0, le=5.0)
    elevenlabs: ElevenLabsSettings | None = None
    dialogue_turns: tuple[DialogueTurn, ...] | None = None
    source: VoiceDirectionSource | None = None

    @field_validator("dialogue_turns", mode="before")
    @classmethod
    def _coerce_sequence_to_tuple(cls, value: object) -> object:
        if isinstance(value, list):
            return tuple(value)
        return value


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
    # Story enhanced-vo.1 (Slice 0): the STABLE source-slide identity each final
    # segment descends from (the source-deck slide ordinal as a string), threaded
    # so the directed-voice role->slide linkage is a deterministic IDENTITY join
    # on this key instead of the fail-open source/final ORDINAL-SET comparison.
    # Optional (default None) so a directed-voice-OFF / non-enriched run stays
    # byte-identical (the model is ``extra="forbid"``, so the field MUST be
    # declared to be carried at all). Populated by ``_attach_voice_direction`` on
    # a directed+enriched run; NEVER the final segment ordinal.
    slide_key: str | None = None
    voice_direction: VoiceDirection | None = None

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
