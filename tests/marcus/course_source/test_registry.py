from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from app.marcus.course_source.registry import load_course

REPO_ROOT = Path(__file__).resolve().parents[3]
HAI_ROOT = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "aziz-nazha-hai-510-generative-ai-in-healthcare"
)
PHS_ROOT = REPO_ROOT / "course-content" / "courses" / "juan-leon-phs-620-teaching-learning-seminar"


def test_seeded_hai_course_root_loads_declared_four_modules() -> None:
    record = load_course(HAI_ROOT)
    assert record.course.module_count_expected == 4
    assert len(record.modules) == 4
    assert record.source_purpose == "new_build"
    assert {item.source_kind for item in record.source_availability} == {
        "companion_reading_list",
        "lecture_slides",
        "recorded_lecture_videos",
    }


def test_seeded_phs_course_root_loads_as_valid_with_gap_potential() -> None:
    record = load_course(PHS_ROOT)
    assert record.course.module_count_expected == 15
    assert record.modules == []
    assert record.source_purpose == "enhancement"
    assert {item.source_kind for item in record.source_availability} == {
        "canvas_current_course_content",
        "confluence_current_course_content",
    }


def test_missing_course_yaml_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="course.yaml"):
        load_course(tmp_path)


def test_malformed_course_yaml_fails_loud(tmp_path: Path) -> None:
    (tmp_path / "course.yaml").write_text("schema_version: 0.1\n", encoding="utf-8")

    with pytest.raises(ValidationError):
        load_course(tmp_path)
