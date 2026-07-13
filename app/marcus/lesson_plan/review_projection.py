"""Strict, deterministic Review-frame contracts for workbook producers.

This M3-safe module accepts typed pre-work authority and projects an honest
five-beat shell. It neither reads runtime state nor invokes semantic writers.
"""

from __future__ import annotations

from typing import Annotated, Literal, Protocol

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator

from app.marcus.lesson_plan.check_on_learning_projection import (
    CheckAnswerClaim,
    CheckGateReceipt,
    CheckOnLearningRequest,
    CheckOnLearningResult,
    CheckOnLearningWriter,
    CheckOnLearningWriterCandidate,
    CheckSourceClaim,
    CheckSourceSpan,
    RetrievalCheckItem,
    check_authority_digest,
    check_candidate_digest,
    compose_check_on_learning,
    offline_check_on_learning_writer,
)
from app.marcus.lesson_plan.deep_dive_projection import (
    DeepDiveSkeletonRequest,
    DeepDiveSkeletonResult,
    DeepDiveSkeletonWriterResult,
    DeepDiveWriterCandidate,
    compose_deep_dive_skeleton,
    deep_dive_authority_digest,
)
from app.marcus.lesson_plan.deep_dive_projection import (
    DeepDiveWriter as DeepDiveSkeletonWriter,
)
from app.marcus.lesson_plan.deep_dive_projection import (
    offline_deep_dive_writer as offline_deep_dive_skeleton_writer,
)
from app.marcus.lesson_plan.prework_projection import PreWorkBrief

ReviewStatus = Literal["ready", "pending", "unavailable"]
Ownership = Literal["learner_written", "lesson_level"]
ReviewBeatOrder = tuple[
    Literal["bookend"],
    Literal["deep_dive"],
    Literal["check_on_learning"],
    Literal["door_left_ajar"],
    Literal["closing_reflection"],
]

REVIEW_BEAT_ORDER: ReviewBeatOrder = (
    "bookend",
    "deep_dive",
    "check_on_learning",
    "door_left_ajar",
    "closing_reflection",
)
REVIEW_HEADINGS = (
    "Bookend",
    "Deep Dive",
    "Check on Learning",
    "The Door Left Ajar",
    "Closing Reflection",
)
REVIEW_WATCHWORDS = ("engagement", "depth", "recall", "engagement", "transfer")

BOOKEND_CALLBACK = (
    "Return to the friction mark, location, and honest line you wrote before the "
    "presentation. Re-read them before continuing."
)
BOOKEND_UNAVAILABLE_COPY = (
    "Your pre-work note is not available here. Continue with the review."
)
LESSON_SLOT_PENDING_COPY = "This lesson-level section is pending."
CHECK_PENDING_COPY = "Questions and answers will appear here."
REFLECTION_SHELL_COPY = "Write your reflection in this space."
BOOKEND_UNAVAILABLE_MARKER = "review_bookend_unavailable"
WRITER_UNAVAILABLE_MARKER = "review_writer_unavailable"


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


class BookendBeat(_StrictModel):
    beat_id: Literal["bookend"] = "bookend"
    heading: Literal["Bookend"] = "Bookend"
    watchword: Literal["engagement"] = "engagement"
    ownership: Literal["learner_written"] = "learner_written"
    status: Literal["ready", "unavailable"]
    prompt: NonBlankStr
    known_losses: tuple[NonBlankStr, ...]
    marker: NonBlankStr | None

    @model_validator(mode="after")
    def _honest_status(self) -> BookendBeat:
        if self.status == "ready":
            if self.prompt != BOOKEND_CALLBACK or self.known_losses or self.marker is not None:
                raise ValueError("ready Bookend requires the canonical callback and no losses")
        elif (
            self.prompt != BOOKEND_UNAVAILABLE_COPY
            or self.known_losses != ("prework_authority_unavailable",)
            or self.marker != BOOKEND_UNAVAILABLE_MARKER
        ):
            raise ValueError("unavailable Bookend requires its canonical local-loss state")
        if any(line.strip().startswith("## ") for line in self.prompt.splitlines()):
            raise ValueError("Bookend prompt cannot forge a Review heading")
        return self


class DeepDiveBeat(_StrictModel):
    beat_id: Literal["deep_dive"] = "deep_dive"
    heading: Literal["Deep Dive"] = "Deep Dive"
    watchword: Literal["depth"] = "depth"
    ownership: Literal["lesson_level"] = "lesson_level"
    status: Literal["pending"] = "pending"
    content: None = None
    section_shell: Literal["This lesson-level section is pending."] = LESSON_SLOT_PENDING_COPY
    known_losses: tuple[Literal["deep_dive_not_authored"]] = ("deep_dive_not_authored",)


class CheckOnLearningBeat(_StrictModel):
    beat_id: Literal["check_on_learning"] = "check_on_learning"
    heading: Literal["Check on Learning"] = "Check on Learning"
    watchword: Literal["recall"] = "recall"
    ownership: Literal["lesson_level"] = "lesson_level"
    status: Literal["pending"] = "pending"
    content: None = None
    section_shell: Literal["Questions and answers will appear here."] = CHECK_PENDING_COPY
    known_losses: tuple[Literal["check_not_authored"]] = ("check_not_authored",)


class DoorLeftAjarBeat(_StrictModel):
    beat_id: Literal["door_left_ajar"] = "door_left_ajar"
    heading: Literal["The Door Left Ajar"] = "The Door Left Ajar"
    watchword: Literal["engagement"] = "engagement"
    ownership: Literal["lesson_level"] = "lesson_level"
    status: Literal["pending"] = "pending"
    content: None = None
    section_shell: Literal["This lesson-level section is pending."] = LESSON_SLOT_PENDING_COPY
    known_losses: tuple[Literal["door_left_ajar_not_authored"]] = (
        "door_left_ajar_not_authored",
    )


class ClosingReflectionBeat(_StrictModel):
    beat_id: Literal["closing_reflection"] = "closing_reflection"
    heading: Literal["Closing Reflection"] = "Closing Reflection"
    watchword: Literal["transfer"] = "transfer"
    ownership: Literal["learner_written"] = "learner_written"
    status: Literal["pending"] = "pending"
    prompt: None = None
    section_shell: Literal["Write your reflection in this space."] = REFLECTION_SHELL_COPY
    known_losses: tuple[Literal["reflection_prompt_not_authored"]] = (
        "reflection_prompt_not_authored",
    )


class ReviewBrief(_StrictModel):
    """Closed aggregate in canonical five-beat order."""

    bookend: BookendBeat
    deep_dive: DeepDiveBeat
    check_on_learning: CheckOnLearningBeat
    door_left_ajar: DoorLeftAjarBeat
    closing_reflection: ClosingReflectionBeat
    beat_order: ReviewBeatOrder = REVIEW_BEAT_ORDER


class ReviewWriterRequest(_StrictModel):
    """Minimal normalized seam; downstream stories may replace offline writers."""

    lesson_ref: NonBlankStr


class ReviewWriterResult(_StrictModel):
    """Honest placeholder result with no downstream semantic payload."""

    status: Literal["unavailable"]
    content: None
    known_losses: tuple[NonBlankStr, ...]
    marker: Literal["review_writer_unavailable"]

    @model_validator(mode="after")
    def _requires_loss(self) -> ReviewWriterResult:
        if not self.known_losses:
            raise ValueError("unavailable writer result requires a known loss")
        return self


class DeepDiveWriter(Protocol):
    def __call__(self, request: ReviewWriterRequest) -> ReviewWriterResult: ...


class CheckWriter(Protocol):
    def __call__(self, request: ReviewWriterRequest) -> ReviewWriterResult: ...


class ReflectionWriter(Protocol):
    def __call__(self, request: ReviewWriterRequest) -> ReviewWriterResult: ...


def _offline_writer(loss: str) -> ReviewWriterResult:
    return ReviewWriterResult(
        status="unavailable",
        content=None,
        known_losses=(loss,),
        marker=WRITER_UNAVAILABLE_MARKER,
    )


def offline_deep_dive_writer(request: ReviewWriterRequest) -> ReviewWriterResult:
    del request
    return _offline_writer("deep_dive_writer_unavailable")


def offline_check_writer(request: ReviewWriterRequest) -> ReviewWriterResult:
    del request
    return _offline_writer("check_writer_unavailable")


def offline_reflection_writer(request: ReviewWriterRequest) -> ReviewWriterResult:
    del request
    return _offline_writer("reflection_writer_unavailable")


def build_review_brief(prework: PreWorkBrief | None) -> ReviewBrief:
    """Build the deterministic frame from typed authority, without global reads."""
    if prework is not None and not isinstance(prework, PreWorkBrief):
        raise TypeError("prework must be a validated PreWorkBrief or None")
    if prework is None:
        bookend = BookendBeat(
            status="unavailable",
            prompt=BOOKEND_UNAVAILABLE_COPY,
            known_losses=("prework_authority_unavailable",),
            marker=BOOKEND_UNAVAILABLE_MARKER,
        )
    else:
        bookend = BookendBeat(
            status="ready",
            prompt=BOOKEND_CALLBACK,
            known_losses=(),
            marker=None,
        )
    return ReviewBrief(
        bookend=bookend,
        deep_dive=DeepDiveBeat(),
        check_on_learning=CheckOnLearningBeat(),
        door_left_ajar=DoorLeftAjarBeat(),
        closing_reflection=ClosingReflectionBeat(),
    )


def render_review_markdown(brief: ReviewBrief) -> str:
    """Render only validated deterministic shell copy with canonical LF bytes."""
    if not isinstance(brief, ReviewBrief):
        raise TypeError("brief must be a validated ReviewBrief")
    lines = [
        f"## {brief.bookend.heading}",
        "",
        brief.bookend.prompt,
        "",
        f"## {brief.deep_dive.heading}",
        "",
        brief.deep_dive.section_shell,
        "",
        f"## {brief.check_on_learning.heading}",
        "",
        brief.check_on_learning.section_shell,
        "",
        f"## {brief.door_left_ajar.heading}",
        "",
        brief.door_left_ajar.section_shell,
        "",
        f"## {brief.closing_reflection.heading}",
        "",
        brief.closing_reflection.section_shell,
    ]
    return "\n".join(lines) + "\n"


__all__ = [
    "BOOKEND_CALLBACK",
    "REVIEW_BEAT_ORDER",
    "REVIEW_HEADINGS",
    "REVIEW_WATCHWORDS",
    "BookendBeat",
    "CheckAnswerClaim",
    "CheckGateReceipt",
    "CheckOnLearningRequest",
    "CheckOnLearningResult",
    "CheckOnLearningWriter",
    "CheckOnLearningWriterCandidate",
    "CheckSourceClaim",
    "CheckSourceSpan",
    "CheckWriter",
    "DeepDiveWriter",
    "DeepDiveSkeletonRequest",
    "DeepDiveSkeletonResult",
    "DeepDiveSkeletonWriter",
    "DeepDiveSkeletonWriterResult",
    "DeepDiveWriterCandidate",
    "ReflectionWriter",
    "ReviewBrief",
    "ReviewWriterRequest",
    "ReviewWriterResult",
    "RetrievalCheckItem",
    "build_review_brief",
    "compose_deep_dive_skeleton",
    "compose_check_on_learning",
    "check_authority_digest",
    "check_candidate_digest",
    "deep_dive_authority_digest",
    "offline_check_writer",
    "offline_check_on_learning_writer",
    "offline_deep_dive_writer",
    "offline_deep_dive_skeleton_writer",
    "offline_reflection_writer",
    "render_review_markdown",
]
