"""Strict, deterministic pre-work projection contracts for workbook producers.

This module is deliberately M3-safe: it owns normalized data contracts, honest
offline seams, and pure Markdown projection only. Runtime wiring belongs to a
later integration story.
"""

from __future__ import annotations

from typing import Annotated, Literal, Protocol

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator

Availability = Literal["authored", "degraded", "unavailable"]
ObjectiveStatus = Literal["ratified", "unratified", "unknown"]
BeatOrder = tuple[Literal["scene"], Literal["friction_scale"], Literal["promise"]]

PREWORK_STUB_MARKER = "prework_semantics_not_authored"
SCENE_NOT_AUTHORED = "Source-grounded Scene not yet authored."
PROMISE_NOT_AUTHORED = "Ratified-objective Promise not yet authored."


def _non_blank(value: str) -> str:
    if not value.strip():
        raise ValueError("value must contain non-whitespace text")
    return value


NonBlankStr = Annotated[str, AfterValidator(_non_blank)]


class _StrictModel(BaseModel):
    model_config = ConfigDict(
        strict=True,
        extra="forbid",
        frozen=True,
        validate_assignment=True,
        validate_default=True,
    )


class SceneBrief(_StrictModel):
    """Source-grounded Scene result; semantic adequacy is owned by Story 36.2."""

    status: Availability
    text: NonBlankStr | None
    source_refs: tuple[NonBlankStr, ...]
    known_losses: tuple[NonBlankStr, ...]
    marker: NonBlankStr | None
    lesson_type: Literal["fresh_pain", "bridge_identity", "skill_build"] | None = None
    archetype: (
        Literal["external_friction", "introspective_threshold", "difficulty_practice"] | None
    ) = None

    @model_validator(mode="after")
    def _honest_availability(self) -> SceneBrief:
        if self.status == "authored" and (not self.text or not self.text.strip()):
            raise ValueError("authored Scene requires text")
        if self.status != "authored" and self.text is not None:
            raise ValueError("unavailable/degraded Scene cannot carry authored text")
        if self.status == "authored" and (self.known_losses or self.marker is not None):
            raise ValueError("authored Scene cannot carry losses or an unavailable marker")
        if self.status != "authored" and (not self.known_losses or self.marker is None):
            raise ValueError("unavailable/degraded Scene requires losses and a marker")
        if self.text and any(
            line.strip() in {"## Scene", "## Friction Scale", "## Promise"}
            for line in self.text.splitlines()
        ):
            raise ValueError("Scene text cannot forge a pre-work beat heading")
        if (self.lesson_type is None) != (self.archetype is None):
            raise ValueError("Scene lesson type and archetype must be supplied together")
        return self


class FrictionScaleSpec(_StrictModel):
    """Immutable weekly Friction Scale copy contract."""

    duration_copy: Literal["Take about 20 seconds."]
    rating_prompt: Literal["Rate this friction from 0 to 10."]
    low_anchor: Literal["0 — present, but not getting in the way."]
    high_anchor: Literal["10 — repeatedly blocks the work."]
    locate_prompt: Literal["Locate where it shows up."]
    honest_line_prompt: Literal["Write one honest line."]
    review_hook: Literal["Keep this mark and line for review after the presentation."]


class PromiseVow(_StrictModel):
    """One ratified objective projected as an ability vow."""

    objective_id: NonBlankStr
    text: NonBlankStr

    @model_validator(mode="after")
    def _single_markdown_item(self) -> PromiseVow:
        if any(separator in self.text for separator in ("\n", "\r", "\u2028", "\u2029")):
            raise ValueError("Promise vow must render as one Markdown list item")
        return self


class PromiseProjection(_StrictModel):
    """Promise beat result; ratification authority is owned by Story 36.3."""

    status: Availability
    vows: tuple[PromiseVow, ...]
    known_losses: tuple[NonBlankStr, ...]
    marker: NonBlankStr | None

    @model_validator(mode="after")
    def _honest_availability(self) -> PromiseProjection:
        if self.status == "authored" and not self.vows:
            raise ValueError("authored Promise requires at least one vow")
        if self.status != "authored" and self.vows:
            raise ValueError("unavailable/degraded Promise cannot carry vows")
        if self.status == "authored" and (self.known_losses or self.marker is not None):
            raise ValueError("authored Promise cannot carry losses or an unavailable marker")
        if self.status != "authored" and (not self.known_losses or self.marker is None):
            raise ValueError("unavailable/degraded Promise requires losses and a marker")
        return self


class PreWorkProvenance(_StrictModel):
    source_refs: tuple[NonBlankStr, ...]
    known_losses: tuple[NonBlankStr, ...]


class ObjectiveInput(_StrictModel):
    objective_id: NonBlankStr
    text: NonBlankStr
    status: ObjectiveStatus


class SceneComposeRequest(_StrictModel):
    """Normalized extracted seed only; never reads source artifacts itself."""

    seed_text: NonBlankStr
    source_refs: tuple[NonBlankStr, ...]
    orienting_hint: NonBlankStr | None = None
    lesson_type: Literal["fresh_pain", "bridge_identity", "skill_build"] | None = None
    archetype: (
        Literal["external_friction", "introspective_threshold", "difficulty_practice"] | None
    ) = None
    payoff_slide_keys: tuple[NonBlankStr, ...] = ()

    @model_validator(mode="after")
    def _paired_lesson_shape(self) -> SceneComposeRequest:
        if (self.lesson_type is None) != (self.archetype is None):
            raise ValueError("lesson type and archetype must be supplied together")
        return self


class PromiseTransformRequest(_StrictModel):
    """Normalized objective inputs only; never loads planning artifacts itself."""

    objectives: tuple[ObjectiveInput, ...]
    scene_context: NonBlankStr | None = None
    friction_context: NonBlankStr | None = None
    transformation_posture: Literal["pertinent_ability_first_move"]


class SceneComposer(Protocol):
    def __call__(self, request: SceneComposeRequest) -> SceneBrief: ...


class PromiseTransformer(Protocol):
    def __call__(self, request: PromiseTransformRequest) -> PromiseProjection: ...


FRICTION_SCALE = FrictionScaleSpec(
    duration_copy="Take about 20 seconds.",
    rating_prompt="Rate this friction from 0 to 10.",
    low_anchor="0 — present, but not getting in the way.",
    high_anchor="10 — repeatedly blocks the work.",
    locate_prompt="Locate where it shows up.",
    honest_line_prompt="Write one honest line.",
    review_hook="Keep this mark and line for review after the presentation.",
)


class PreWorkBrief(_StrictModel):
    """Aggregate in the closed Scene -> Friction Scale -> Promise order."""

    scene: SceneBrief
    friction_scale: FrictionScaleSpec
    promise: PromiseProjection
    provenance: PreWorkProvenance
    beat_order: BeatOrder = ("scene", "friction_scale", "promise")

    @model_validator(mode="after")
    def _provenance_matches_nested_contracts(self) -> PreWorkBrief:
        expected_losses = self.scene.known_losses + self.promise.known_losses
        if self.provenance.source_refs != self.scene.source_refs:
            raise ValueError("aggregate source refs must equal Scene source refs")
        if self.provenance.known_losses != expected_losses:
            raise ValueError("aggregate known losses must equal nested known losses")
        return self


def offline_scene_composer(request: SceneComposeRequest) -> SceneBrief:
    """Accept a normalized request without pretending to author a Scene."""
    del request
    return SceneBrief(
        status="unavailable",
        text=None,
        source_refs=(),
        known_losses=("scene_writer_unavailable",),
        marker=PREWORK_STUB_MARKER,
    )


def offline_promise_transformer(request: PromiseTransformRequest) -> PromiseProjection:
    """Accept normalized objectives without pretending to ratify/transform them."""
    del request
    return PromiseProjection(
        status="unavailable",
        vows=(),
        known_losses=("promise_writer_unavailable",),
        marker=PREWORK_STUB_MARKER,
    )


def _friction_lines(spec: FrictionScaleSpec) -> list[str]:
    return [
        spec.duration_copy,
        "",
        spec.rating_prompt,
        "",
        f"- **{spec.low_anchor.split(' — ', 1)[0]}** — {spec.low_anchor.split(' — ', 1)[1]}",
        f"- **{spec.high_anchor.split(' — ', 1)[0]}** — {spec.high_anchor.split(' — ', 1)[1]}",
        "",
        f"**Locate it:** {spec.locate_prompt}",
        "",
        f"**One honest line:** {spec.honest_line_prompt}",
        "",
        spec.review_hook,
    ]


def render_deterministic_frame() -> str:
    """Render the byte-golden fixed headings, honesty shell, and Friction copy."""
    lines = [
        "## Scene",
        "",
        SCENE_NOT_AUTHORED,
        "",
        "## Friction Scale",
        "",
        *_friction_lines(FRICTION_SCALE),
        "",
        "## Promise",
        "",
        PROMISE_NOT_AUTHORED,
    ]
    return "\n".join(lines) + "\n"


def render_prework_markdown(brief: PreWorkBrief) -> str:
    """Render an already-authored brief without loading or inferring semantics."""
    scene_copy = brief.scene.text if brief.scene.status == "authored" else SCENE_NOT_AUTHORED
    if brief.promise.status == "authored":
        promise_lines = [f"- {vow.text}" for vow in brief.promise.vows]
    else:
        promise_lines = [PROMISE_NOT_AUTHORED]
    lines = [
        "## Scene",
        "",
        scene_copy or SCENE_NOT_AUTHORED,
        "",
        "## Friction Scale",
        "",
        *_friction_lines(brief.friction_scale),
        "",
        "## Promise",
        "",
        *promise_lines,
    ]
    return "\n".join(lines) + "\n"


__all__ = [
    "FRICTION_SCALE",
    "PREWORK_STUB_MARKER",
    "FrictionScaleSpec",
    "ObjectiveInput",
    "PreWorkBrief",
    "PreWorkProvenance",
    "PromiseProjection",
    "PromiseTransformRequest",
    "PromiseTransformer",
    "PromiseVow",
    "SceneBrief",
    "SceneComposeRequest",
    "SceneComposer",
    "offline_promise_transformer",
    "offline_scene_composer",
    "render_deterministic_frame",
    "render_prework_markdown",
]
