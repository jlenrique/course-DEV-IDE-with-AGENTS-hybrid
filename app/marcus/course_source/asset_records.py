"""Canonical records for course-provided and missing source assets."""

from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from app.marcus.lesson_plan.event_type_registry import OPEN_ID_REGEX_PATTERN

SCHEMA_VERSION = "0.1"


class AssetKind(StrEnum):
    reading = "reading"
    lecture = "lecture"
    lab = "lab"
    assignment = "assignment"
    assessment = "assessment"
    discussion_prompt = "discussion_prompt"
    syllabus = "syllabus"
    project_artifact = "project_artifact"


class AssetRecordStatus(StrEnum):
    source_grounded = "source_grounded"
    partial = "partial"
    inferred = "inferred"
    missing = "missing"
    required_gap = "required_gap"
    draft_gap_fill = "draft_gap_fill"
    needs_sme_review = "needs_sme_review"


class SourceRefRole(StrEnum):
    requirement = "requirement"
    content = "content"


ASSET_KIND_RECONCILIATION: dict[str, str] = {
    "assignment_instructions": "assignment",
    "discussion_forum": "discussion_prompt",
    "exercise_lab": "lab",
    "reference_citation": "reading",
}
"""Mapping from existing source-type vocabulary to the asset-kind vocabulary."""


class AssetSourceRef(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        use_enum_values=True,
        validate_assignment=True,
    )

    ref_id: str = Field(..., pattern=OPEN_ID_REGEX_PATTERN)
    path: str = Field(..., description="Source path carrying this evidence.")
    locator: str = Field(..., description="Section, row, page, or slide locator.")
    role: SourceRefRole = Field(
        ...,
        description="Whether the ref names a requirement or content evidence.",
    )


class AssetReview(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    sme_required: bool = Field(
        default=False,
        description="True when the record needs subject-matter review.",
    )


class CanonicalAssetRecord(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        use_enum_values=True,
        validate_assignment=True,
    )

    schema_version: Literal["0.1"] = Field(default=SCHEMA_VERSION)
    asset_id: str = Field(..., pattern=OPEN_ID_REGEX_PATTERN)
    asset_kind: AssetKind
    course_id: str = Field(..., pattern=OPEN_ID_REGEX_PATTERN)
    module_id: str | None = Field(default=None, pattern=OPEN_ID_REGEX_PATTERN)
    lesson_id: str | None = Field(default=None, pattern=OPEN_ID_REGEX_PATTERN)
    source_refs: tuple[AssetSourceRef, ...] = Field(default_factory=tuple)
    learning_objective_refs: tuple[
        Annotated[str, Field(pattern=OPEN_ID_REGEX_PATTERN)], ...
    ] = Field(default_factory=tuple)
    derivation: Literal["source_evidence", "syllabus_requirement", "lesson_lo"] = (
        "source_evidence"
    )
    status: AssetRecordStatus
    content: dict[str, JsonValue] = Field(default_factory=dict)
    gaps: tuple[str, ...] = Field(default_factory=tuple)
    review: AssetReview = Field(default_factory=AssetReview)

    def model_copy(
        self,
        *,
        update: dict[str, Any] | None = None,
        deep: bool = False,
    ) -> Self:
        data = self.model_dump(mode="python")
        if update:
            data.update(update)
        return type(self).model_validate(data)

    @model_validator(mode="after")
    def _source_grounded_requires_content_ref(self) -> CanonicalAssetRecord:
        valid_source_ref_roles = {
            SourceRefRole.requirement.value,
            SourceRefRole.content.value,
        }
        if any(ref.role not in valid_source_ref_roles for ref in self.source_refs):
            raise ValueError("source_refs require a known role")
        if self.derivation == "syllabus_requirement":
            if not self.source_refs:
                raise ValueError(
                    "syllabus_requirement records require requirement source_refs"
                )
            if any(
                ref.role != SourceRefRole.requirement.value for ref in self.source_refs
            ):
                raise ValueError(
                    "syllabus_requirement records require requirement source_refs"
                )
        if self.derivation in {"syllabus_requirement", "lesson_lo"} and (
            self.status == AssetRecordStatus.source_grounded.value
        ):
            raise ValueError(f"{self.derivation} records cannot claim source_grounded")
        if self.status != AssetRecordStatus.source_grounded.value:
            return self
        if not self.source_refs:
            raise ValueError("status source_grounded requires source_refs")
        if not any(ref.role == SourceRefRole.content.value for ref in self.source_refs):
            raise ValueError("status source_grounded requires a content source_ref")
        return self


def make_syllabus_requirement_record(
    *,
    asset_id: str,
    asset_kind: AssetKind,
    course_id: str,
    source_ref: AssetSourceRef | dict[str, object],
    status: Literal["missing", "required_gap", "inferred"],
    module_id: str | None = None,
    lesson_id: str | None = None,
    learning_objective_refs: list[str] | None = None,
) -> CanonicalAssetRecord:
    if status not in {"missing", "required_gap", "inferred"}:
        raise ValueError("syllabus requirement records cannot claim source_grounded")
    return CanonicalAssetRecord(
        asset_id=asset_id,
        asset_kind=asset_kind,
        course_id=course_id,
        module_id=module_id,
        lesson_id=lesson_id,
        source_refs=[source_ref],
        learning_objective_refs=learning_objective_refs or [],
        derivation="syllabus_requirement",
        status=status,
    )


def make_lesson_lo_record(
    *,
    asset_id: str,
    asset_kind: AssetKind,
    course_id: str,
    learning_objective_refs: list[str],
    status: Literal["inferred", "needs_sme_review"],
    module_id: str | None = None,
    lesson_id: str | None = None,
    source_refs: list[AssetSourceRef | dict[str, object]] | None = None,
) -> CanonicalAssetRecord:
    return CanonicalAssetRecord(
        asset_id=asset_id,
        asset_kind=asset_kind,
        course_id=course_id,
        module_id=module_id,
        lesson_id=lesson_id,
        source_refs=source_refs or [],
        learning_objective_refs=learning_objective_refs,
        derivation="lesson_lo",
        status=status,
    )


def emit_requirement_gap_records(
    *,
    course_id: str,
    asset_kind: AssetKind,
    source_refs: list[AssetSourceRef | dict[str, object]],
    module_id: str | None = None,
) -> tuple[CanonicalAssetRecord, ...]:
    resolved_kind = AssetKind(asset_kind)
    id_scope = module_id or course_id
    records: list[CanonicalAssetRecord] = []
    for index, source_ref in enumerate(source_refs, start=1):
        records.append(
            make_syllabus_requirement_record(
                asset_id=f"{id_scope}-{resolved_kind.value}-{index:03d}",
                asset_kind=resolved_kind,
                course_id=course_id,
                module_id=module_id,
                source_ref=source_ref,
                status="required_gap",
            )
        )
    return tuple(records)


def canonical_asset_record_json_schema() -> dict[str, object]:
    return CanonicalAssetRecord.model_json_schema()


__all__ = [
    "ASSET_KIND_RECONCILIATION",
    "SCHEMA_VERSION",
    "AssetKind",
    "AssetRecordStatus",
    "AssetReview",
    "AssetSourceRef",
    "CanonicalAssetRecord",
    "SourceRefRole",
    "canonical_asset_record_json_schema",
    "emit_requirement_gap_records",
    "make_lesson_lo_record",
    "make_syllabus_requirement_record",
]
