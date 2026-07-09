"""Strict course-source records for source ingestion planning."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.marcus.lesson_plan.event_type_registry import OPEN_ID_REGEX_PATTERN

SCHEMA_VERSION = "0.1"

SourceScope = Literal["course", "shared", "module", "lesson"]
GitStatus = Literal["tracked", "ignored", "untracked"]
GapKind = Literal[
    "empty_source_dir",
    "empty_lesson_dir",
    "format_unsupported",
    "module_count_mismatch",
    "source_availability",
    "declared_detected_drift",
]
GapSeverity = Literal["info", "warning", "error"]
SourceRole = Literal["source", "reference", "scaffold"]
SourceAvailabilityStatus = Literal["present", "pending", "missing", "unknown"]
SourcePurpose = Literal["reference_seed", "new_build", "enhancement", "unknown"]


def _schema_version(value: object) -> str:
    normalized = str(value)
    if normalized != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION!r}")
    return normalized


class SmeRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str


class CourseDetails(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    code: str
    title: str
    module_count_expected: int = Field(ge=0)


class RuntimeContract(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    runnable_input_scope: Literal["lesson_corpus_leaf"]
    do_not_run_from: list[Literal["course_root", "module_root"]] = Field(default_factory=list)


class SourceReference(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    url: str
    description: str = ""


class ModuleRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    module_id: str = Field(pattern=OPEN_ID_REGEX_PATTERN)
    title: str


class SourceAvailabilityRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    source_kind: str
    status: SourceAvailabilityStatus = "unknown"
    description: str = ""
    access_note: str = ""


class CourseRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: str
    course_id: str = Field(pattern=OPEN_ID_REGEX_PATTERN)
    sme: SmeRecord
    course: CourseDetails
    source_references: list[SourceReference] = Field(default_factory=list)
    modules: list[ModuleRecord] = Field(default_factory=list)
    status: str | None = None
    runtime_contract: RuntimeContract
    source_purpose: SourcePurpose = "unknown"
    source_availability: list[SourceAvailabilityRecord] = Field(default_factory=list)

    @field_validator("schema_version", mode="before")
    @classmethod
    def _schema_version_pinned(cls, value: object) -> str:
        return _schema_version(value)


class SourceManifestEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    path: str
    scope: SourceScope
    content_sha256: str = Field(min_length=64, max_length=64)
    tracked: bool
    git_status: GitStatus = "untracked"
    source_role: SourceRole
    course_id: str | None = None
    module_id: str | None = None
    lesson_id: str | None = None
    declared: bool = False


class SourceManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: str = SCHEMA_VERSION
    course_id: str
    declared: dict[str, object]
    detected: dict[str, object]
    gap_summary: dict[str, int] = Field(default_factory=dict)
    entries: list[SourceManifestEntry] = Field(default_factory=list)


class GapEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    kind: GapKind
    severity: GapSeverity = "warning"
    path: str | None = None
    message: str
    access_note: str = ""
    declared: object | None = None
    detected: object | None = None


class GapLedger(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    schema_version: str = SCHEMA_VERSION
    course_id: str
    gaps: list[GapEntry] = Field(default_factory=list)


__all__ = [
    "CourseDetails",
    "CourseRecord",
    "GapEntry",
    "GitStatus",
    "GapKind",
    "GapLedger",
    "GapSeverity",
    "ModuleRecord",
    "RuntimeContract",
    "SCHEMA_VERSION",
    "SmeRecord",
    "SourceAvailabilityRecord",
    "SourceAvailabilityStatus",
    "SourceManifest",
    "SourceManifestEntry",
    "SourcePurpose",
    "SourceReference",
    "SourceRole",
    "SourceScope",
]
