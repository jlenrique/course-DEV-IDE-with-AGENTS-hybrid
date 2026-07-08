from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from app.marcus.course_source.asset_records import (
    ASSET_KIND_RECONCILIATION,
    AssetKind,
    AssetRecordStatus,
    AssetSourceRef,
    CanonicalAssetRecord,
    SourceRefRole,
    emit_requirement_gap_records,
    make_lesson_lo_record,
    make_syllabus_requirement_record,
)


def _content_ref() -> dict[str, str]:
    return {
        "ref_id": "src-001",
        "path": "sources/course/source.md",
        "locator": "Module 1 > Slide 2",
        "role": "content",
    }


def _requirement_ref() -> dict[str, str]:
    return {
        "ref_id": "syllabus-001",
        "path": "sources/course/syllabus.doc",
        "locator": "Week 1 row",
        "role": "requirement",
    }


def test_source_grounded_requires_content_source_ref() -> None:
    with pytest.raises(ValidationError, match="source_grounded"):
        CanonicalAssetRecord(
            asset_id="asset-001",
            asset_kind="lecture",
            course_id="course-001",
            source_refs=[],
            status="source_grounded",
        )

    with pytest.raises(ValidationError, match="content"):
        CanonicalAssetRecord(
            asset_id="asset-001",
            asset_kind="lecture",
            course_id="course-001",
            source_refs=[_requirement_ref()],
            status="source_grounded",
        )

    record = CanonicalAssetRecord(
        asset_id="asset-001",
        asset_kind="lecture",
        course_id="course-001",
        source_refs=[_content_ref()],
        status="source_grounded",
    )
    assert record.status == "source_grounded"

    with pytest.raises(ValidationError):
        record.source_refs[0].role = "requirement"  # type: ignore[misc]

    with pytest.raises(ValidationError):
        record.source_refs = ()  # type: ignore[assignment]


def test_syllabus_row_record_cannot_claim_source_grounded() -> None:
    record = make_syllabus_requirement_record(
        asset_id="asset-002",
        asset_kind="lecture",
        course_id="course-001",
        module_id="module-01",
        source_ref=_requirement_ref(),
        status="required_gap",
    )
    assert record.status == "required_gap"
    assert record.source_refs[0].role == "requirement"

    with pytest.raises(ValidationError, match="requirement source_refs"):
        make_syllabus_requirement_record(
            asset_id="asset-002",
            asset_kind="lecture",
            course_id="course-001",
            module_id="module-01",
            source_ref=_content_ref(),
            status="required_gap",
        )

    with pytest.raises(ValidationError, match="requirement source_refs"):
        CanonicalAssetRecord(
            asset_id="asset-002",
            asset_kind="lecture",
            course_id="course-001",
            source_refs=[],
            derivation="syllabus_requirement",
            status="required_gap",
        )

    with pytest.raises(ValueError, match="source_grounded"):
        make_syllabus_requirement_record(
            asset_id="asset-002",
            asset_kind="lecture",
            course_id="course-001",
            module_id="module-01",
            source_ref=_requirement_ref(),
            status="source_grounded",  # type: ignore[arg-type]
        )


def test_lesson_lo_derived_record_stays_review_status() -> None:
    record = make_lesson_lo_record(
        asset_id="asset-003",
        asset_kind="project_artifact",
        course_id="course-001",
        module_id="module-01",
        lesson_id="lesson-01",
        source_refs=[_requirement_ref()],
        learning_objective_refs=["lo-001"],
        status="needs_sme_review",
    )

    assert record.status == "needs_sme_review"
    assert record.derivation == "lesson_lo"
    with pytest.raises(ValidationError):
        record.status = "source_grounded"  # type: ignore[assignment]

    with pytest.raises(ValidationError):
        CanonicalAssetRecord(
            asset_id="asset-003",
            asset_kind="project_artifact",
            course_id="course-001",
            source_refs=[_content_ref()],
            learning_objective_refs=["lo-001"],
            derivation="lesson_lo",
            status="source_grounded",
        )

    with pytest.raises(ValidationError):
        make_lesson_lo_record(
            asset_id="asset-003",
            asset_kind="project_artifact",
            course_id="course-001",
            learning_objective_refs=["not a valid objective id"],
            status="needs_sme_review",
        )


def test_closed_enums_reject_drift_at_three_surfaces() -> None:
    schema = CanonicalAssetRecord.model_json_schema()
    assert schema["$defs"]["AssetKind"]["enum"] == [
        "reading",
        "lecture",
        "lab",
        "assignment",
        "assessment",
        "discussion_prompt",
        "syllabus",
        "project_artifact",
    ]
    assert "source_grounded" in schema["$defs"]["AssetRecordStatus"]["enum"]

    with pytest.raises(ValidationError):
        CanonicalAssetRecord(
            asset_id="asset-004",
            asset_kind="video",  # type: ignore[arg-type]
            course_id="course-001",
            status="missing",
        )

    with pytest.raises(ValidationError):
        TypeAdapter(AssetKind).validate_python("video")
    with pytest.raises(ValidationError):
        TypeAdapter(AssetRecordStatus).validate_python("complete")
    with pytest.raises(ValidationError):
        TypeAdapter(SourceRefRole).validate_python("citation")

    with pytest.raises(ValidationError):
        CanonicalAssetRecord(
            schema_version="999",  # type: ignore[arg-type]
            asset_id="asset-004",
            asset_kind="lecture",
            course_id="course-001",
            status="missing",
        )


def test_unknown_fields_and_assignment_are_rejected() -> None:
    with pytest.raises(ValidationError):
        CanonicalAssetRecord(
            asset_id="asset-005",
            asset_kind="reading",
            course_id="course-001",
            status="missing",
            routing_hint="tejal",  # type: ignore[call-arg]
        )

    record = CanonicalAssetRecord(
        asset_id="asset-005",
        asset_kind="reading",
        course_id="course-001",
        status="missing",
    )
    with pytest.raises(ValidationError):
        record.asset_kind = "video"  # type: ignore[assignment]


def test_copy_content_and_gap_surfaces_revalidate() -> None:
    record = CanonicalAssetRecord(
        asset_id="asset-006",
        asset_kind="reading",
        course_id="course-001",
        status="missing",
        gaps=["missing source text"],
        content={"title": "Reading 1"},
    )
    assert record.gaps == ("missing source text",)

    with pytest.raises(AttributeError):
        record.gaps.append("silently mutated")  # type: ignore[attr-defined]

    with pytest.raises(ValidationError):
        record.content = {"not_json": object()}  # type: ignore[dict-item]

    invalid_ref = AssetSourceRef.model_construct(
        ref_id="src-001",
        path="sources/course/source.md",
        locator="Module 1 > Slide 2",
        role="citation",
    )
    with pytest.raises(ValidationError, match="known role"):
        record.model_copy(update={"source_refs": (invalid_ref,)})


def test_asset_kind_reconciliation_maps_existing_vocabularies() -> None:
    assert ASSET_KIND_RECONCILIATION["assignment_instructions"] == "assignment"
    assert ASSET_KIND_RECONCILIATION["discussion_forum"] == "discussion_prompt"
    assert ASSET_KIND_RECONCILIATION["exercise_lab"] == "lab"
    assert ASSET_KIND_RECONCILIATION["reference_citation"] == "reading"


def test_requirement_gap_emission_never_claims_source_grounded() -> None:
    records = emit_requirement_gap_records(
        course_id="course-001",
        asset_kind="lecture",
        source_refs=[
            _requirement_ref() | {"ref_id": "syllabus-001"},
            _requirement_ref() | {"ref_id": "syllabus-002", "locator": "Week 2 row"},
        ],
    )

    assert len(records) == 2
    assert [record.asset_id for record in records] == [
        "course-001-lecture-001",
        "course-001-lecture-002",
    ]
    assert {record.status for record in records} == {"required_gap"}
    assert {record.derivation for record in records} == {"syllabus_requirement"}
    assert not any(record.status == "source_grounded" for record in records)

    module_records = emit_requirement_gap_records(
        course_id="course-001",
        module_id="module-01",
        asset_kind="lecture",
        source_refs=[_requirement_ref()],
    )
    assert module_records[0].asset_id == "module-01-lecture-001"
