"""Assess available source material for lesson-planning ratification.

Thin adapter over course-source input bundles and curated corpus leaves.
Does not perform remote ingestion or fill missing media.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.marcus.course_source.input_bundle import LessonPlanningInputBundle

SourceRichness = Literal["thin", "rich"]


class SourceAssessmentError(ValueError):
    """Raised when source assessment cannot be produced honestly."""


class GapSummary(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    kind: str
    count: int = Field(ge=1)
    sample_message: str = ""


class SourceAssessment(BaseModel):
    """Machine-checkable assessment of available source for a planning run."""

    model_config = ConfigDict(extra="forbid", frozen=True, validate_assignment=True)

    course_or_corpus_id: str
    richness: SourceRichness
    tags: tuple[str, ...] = Field(default_factory=tuple)
    gap_summaries: tuple[GapSummary, ...] = Field(default_factory=tuple)
    gap_count: int = Field(ge=0)
    asset_record_count: int = Field(ge=0)
    detected_file_count: int = Field(ge=0)
    notes: str = ""

    @field_validator("tags")
    @classmethod
    def _tags_nonempty_strings(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        cleaned = tuple(tag.strip() for tag in value if tag and tag.strip())
        if not cleaned:
            raise ValueError("source assessment requires at least one tag")
        return cleaned


def assess_from_input_bundle(bundle: LessonPlanningInputBundle) -> SourceAssessment:
    """Assess a course-source lesson-planning input bundle (typical thin path)."""
    kind_counts: dict[str, list[str]] = {}
    for gap in bundle.gap_ledger:
        kind_counts.setdefault(gap.kind, []).append(gap.message)
    gap_summaries = tuple(
        GapSummary(
            kind=kind,
            count=len(messages),
            sample_message=messages[0] if messages else "",
        )
        for kind, messages in sorted(kind_counts.items())
    )
    tags = [
        "course-source-bundle",
        f"source_purpose:{bundle.course.source_purpose}",
        f"module:{bundle.module.module_id}",
    ]
    if any(record.status == "required_gap" for record in bundle.asset_records):
        tags.append("required_gaps_present")
    if bundle.scoped_source_manifest.entries:
        tags.append("scoped_manifest_present")
    detected = int(
        bundle.scoped_source_manifest.detected.get("scaffold_file_count", 0)
        or 0
    )
    # Syllabus-only / gap-heavy bundles are thin; curated content would show
    # grounded assets and fewer required gaps.
    grounded = sum(
        1 for record in bundle.asset_records if record.status == "source_grounded"
    )
    richness: SourceRichness = "rich" if grounded > 0 and not gap_summaries else "thin"
    return SourceAssessment(
        course_or_corpus_id=bundle.course.course_id,
        richness=richness,
        tags=tuple(tags),
        gap_summaries=gap_summaries,
        gap_count=len(bundle.gap_ledger),
        asset_record_count=len(bundle.asset_records),
        detected_file_count=detected,
        notes=(
            "Assessed from LessonPlanningInputBundle gap_ledger and asset_records; "
            "does not claim full lecture ingestion."
        ),
    )


_CURATED_BUCKETS = ("slides", "references", "assessments", "sources")


def assess_from_corpus_dir(corpus_dir: Path, *, corpus_id: str | None = None) -> SourceAssessment:
    """Assess a curated lesson corpus leaf (typical rich Tejal-style path)."""
    root = corpus_dir.resolve()
    if not root.is_dir():
        raise SourceAssessmentError(f"corpus_dir is not a directory: {root}")
    # Refuse course/module containers — lesson-leaf contract.
    for sentinel in ("course.yaml", "module.yaml"):
        if (root / sentinel).is_file() or (root.parent / sentinel).is_file():
            raise SourceAssessmentError(
                f"corpus_dir looks like a course/module container ({sentinel}); "
                "use a lesson-level corpus leaf"
            )
    tags: list[str] = ["curated-corpus-leaf"]
    file_count = 0
    bucket_hits: list[str] = []
    for bucket in _CURATED_BUCKETS:
        bucket_path = root / bucket
        if bucket_path.is_dir():
            files = [p for p in bucket_path.rglob("*") if p.is_file()]
            if files:
                bucket_hits.append(bucket)
                file_count += len(files)
                tags.append(f"bucket:{bucket}")
    # Also count top-level markdown/text teaching files.
    top_files = [
        p
        for p in root.iterdir()
        if p.is_file() and p.suffix.lower() in {".md", ".txt", ".docx", ".pdf"}
    ]
    file_count += len(top_files)
    if top_files:
        tags.append("top_level_source_files")
    if not bucket_hits and not top_files:
        raise SourceAssessmentError(
            f"corpus_dir has no curated teaching material: {root}"
        )
    richness: SourceRichness = "rich" if file_count >= 3 and bucket_hits else "thin"
    gap_summaries: tuple[GapSummary, ...] = ()
    if "slides" not in bucket_hits:
        gap_summaries = (
            GapSummary(
                kind="missing_slides_bucket",
                count=1,
                sample_message="No slides/ bucket with files in curated corpus",
            ),
        )
    return SourceAssessment(
        course_or_corpus_id=corpus_id or root.name,
        richness=richness,
        tags=tuple(tags),
        gap_summaries=gap_summaries,
        gap_count=len(gap_summaries),
        asset_record_count=file_count,
        detected_file_count=file_count,
        notes=(
            "Assessed from curated corpus leaf layout; does not claim full "
            "lecture ingestion or remote LMS sync."
        ),
    )


def assessments_differ_in_kind_or_count(
    left: SourceAssessment,
    right: SourceAssessment,
) -> bool:
    """True when two assessments differ beyond cosmetic id/filename."""
    if left.richness != right.richness:
        return True
    if left.gap_count != right.gap_count:
        return True
    left_kinds = {item.kind for item in left.gap_summaries}
    right_kinds = {item.kind for item in right.gap_summaries}
    if left_kinds != right_kinds:
        return True
    left_tag_kinds = {tag.split(":", 1)[0] for tag in left.tags}
    right_tag_kinds = {tag.split(":", 1)[0] for tag in right.tags}
    return left_tag_kinds != right_tag_kinds


__all__ = [
    "GapSummary",
    "SourceAssessment",
    "SourceAssessmentError",
    "SourceRichness",
    "assess_from_corpus_dir",
    "assess_from_input_bundle",
    "assessments_differ_in_kind_or_count",
]
