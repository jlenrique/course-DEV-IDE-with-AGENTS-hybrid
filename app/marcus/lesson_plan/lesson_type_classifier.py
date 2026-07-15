"""Pure, closed lesson-type classification for pre-work Scene composition."""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator

LessonType = Literal["fresh_pain", "bridge_identity", "skill_build"]
SceneArchetype = Literal["external_friction", "introspective_threshold", "difficulty_practice"]
ClassificationStatus = Literal["decisive", "insufficient", "ambiguous"]


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


class LessonTypeEvidence(_StrictModel):
    """Closed feature record; it contains evidence, never a tie-break."""

    fresh_pain: bool
    bridge_identity: bool
    skill_build: bool
    evidence_refs: tuple[NonBlankStr, ...]

    @model_validator(mode="after")
    def _traceable_unique_refs(self) -> LessonTypeEvidence:
        if not self.evidence_refs:
            raise ValueError("lesson-type evidence requires at least one evidence ref")
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError("lesson-type evidence refs must be unique")
        return self


class LessonTypeClassification(_StrictModel):
    status: ClassificationStatus
    lesson_type: LessonType | None
    archetype: SceneArchetype | None
    confidence: float | None
    evidence_refs: tuple[NonBlankStr, ...]

    @model_validator(mode="after")
    def _closed_disposition(self) -> LessonTypeClassification:
        if not self.evidence_refs:
            raise ValueError("classification requires at least one evidence ref")
        if len(set(self.evidence_refs)) != len(self.evidence_refs):
            raise ValueError("classification evidence refs must be unique")
        if self.status == "decisive":
            if self.lesson_type is None or self.archetype is None or self.confidence != 1.0:
                raise ValueError(
                    "decisive classification requires class, archetype, confidence 1.0"
                )
            expected = {
                "fresh_pain": "external_friction",
                "bridge_identity": "introspective_threshold",
                "skill_build": "difficulty_practice",
            }[self.lesson_type]
            if self.archetype != expected:
                raise ValueError("classification archetype must exactly match lesson type")
        elif any(
            value is not None for value in (self.lesson_type, self.archetype, self.confidence)
        ):
            raise ValueError("non-decisive classification cannot carry a class or confidence")
        return self


_MAPPING: dict[LessonType, SceneArchetype] = {
    "fresh_pain": "external_friction",
    "bridge_identity": "introspective_threshold",
    "skill_build": "difficulty_practice",
}


def classify_lesson_type(evidence: LessonTypeEvidence) -> LessonTypeClassification:
    """Return the complete truth-table result without priority or inference."""
    active = tuple(
        lesson_type
        for lesson_type in ("fresh_pain", "bridge_identity", "skill_build")
        if getattr(evidence, lesson_type)
    )
    if len(active) == 1:
        lesson_type = active[0]
        return LessonTypeClassification(
            status="decisive",
            lesson_type=lesson_type,
            archetype=_MAPPING[lesson_type],
            confidence=1.0,
            evidence_refs=evidence.evidence_refs,
        )
    return LessonTypeClassification(
        status="insufficient" if not active else "ambiguous",
        lesson_type=None,
        archetype=None,
        confidence=None,
        evidence_refs=evidence.evidence_refs,
    )


__all__ = [
    "ClassificationStatus",
    "LessonType",
    "LessonTypeClassification",
    "LessonTypeEvidence",
    "SceneArchetype",
    "classify_lesson_type",
]
