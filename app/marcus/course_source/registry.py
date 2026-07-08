"""Load and validate course-source container declarations."""

from __future__ import annotations

from pathlib import Path

import yaml

from app.marcus.course_source.models import CourseRecord


def load_course(course_root: Path) -> CourseRecord:
    course_yaml = course_root / "course.yaml"
    if not course_yaml.exists():
        raise FileNotFoundError(f"course.yaml not found under course root: {course_root}")
    data = yaml.safe_load(course_yaml.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"course.yaml must contain a mapping: {course_yaml}")
    return CourseRecord.model_validate(data)


__all__ = ["load_course"]
