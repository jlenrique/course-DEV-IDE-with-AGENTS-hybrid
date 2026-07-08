from __future__ import annotations

import pytest
from pydantic import TypeAdapter, ValidationError

from app.marcus.course_source.models import (
    CourseRecord,
    SourceManifestEntry,
    SourceScope,
)


def _course_payload() -> dict:
    return {
        "schema_version": "0.1",
        "course_id": "test-course",
        "sme": {"name": "Test SME"},
        "course": {
            "code": "TST 100",
            "title": "Test Course",
            "module_count_expected": 1,
        },
        "runtime_contract": {
            "runnable_input_scope": "lesson_corpus_leaf",
            "do_not_run_from": ["course_root", "module_root"],
        },
    }


def test_course_record_is_strict_and_allows_only_source_planning_fields() -> None:
    record = CourseRecord.model_validate(
        _course_payload()
        | {
            "source_purpose": "reference_seed",
            "source_availability": [
                {
                    "source_kind": "recorded_lectures",
                    "status": "pending",
                    "description": "Future capture source.",
                    "access_note": "Coordinate delivery.",
                }
            ],
        }
    )
    assert record.source_purpose == "reference_seed"
    assert record.source_availability[0].status == "pending"
    assert record.source_availability[0].access_note == "Coordinate delivery."

    with pytest.raises(ValidationError):
        CourseRecord.model_validate(_course_payload() | {"voice": "warm"})


def test_schema_version_accepts_yaml_numeric_but_pins_to_string() -> None:
    payload = _course_payload() | {"schema_version": 0.1}
    assert CourseRecord.model_validate(payload).schema_version == "0.1"

    with pytest.raises(ValidationError, match="schema_version"):
        CourseRecord.model_validate(_course_payload() | {"schema_version": "0.2"})


def test_source_scope_closed_enum_rejects_drift_at_three_surfaces() -> None:
    assert SourceManifestEntry.model_json_schema()["properties"]["scope"]["enum"] == [
        "course",
        "shared",
        "module",
        "lesson",
    ]

    with pytest.raises(ValidationError):
        SourceManifestEntry(
            path="x.md",
            scope="styleguide",  # type: ignore[arg-type]
            content_sha256="0" * 64,
            tracked=False,
            source_role="scaffold",
        )

    adapter = TypeAdapter(SourceScope)
    with pytest.raises(ValidationError):
        adapter.validate_python("styleguide")


def test_manifest_entry_assignment_validation_rejects_closed_enum_drift() -> None:
    entry = SourceManifestEntry(
        path="x.md",
        scope="course",
        content_sha256="0" * 64,
        tracked=False,
        source_role="scaffold",
    )

    with pytest.raises(ValidationError):
        entry.scope = "voice"  # type: ignore[assignment]
