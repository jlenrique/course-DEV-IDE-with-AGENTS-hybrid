from __future__ import annotations

from pathlib import Path

import yaml

from app.marcus.course_source.manifest_scan import (
    render_gap_ledger_yaml,
    render_manifest_yaml,
    scan_course,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
HAI_ROOT = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "aziz-nazha-hai-510-generative-ai-in-healthcare"
)
PHS_ROOT = REPO_ROOT / "course-content" / "courses" / "juan-leon-phs-620-teaching-learning-seminar"


def test_seeded_course_scans_are_deterministic_and_scope_classified() -> None:
    first = scan_course(HAI_ROOT)
    second = scan_course(HAI_ROOT)

    assert render_manifest_yaml(first.manifest) == render_manifest_yaml(second.manifest)
    assert render_gap_ledger_yaml(first.gap_ledger) == render_gap_ledger_yaml(second.gap_ledger)

    by_path = {entry.path: entry for entry in first.manifest.entries}
    assert by_path["course.yaml"].scope == "course"
    assert by_path["sources/shared/README.md"].scope == "shared"
    module_yaml = "modules/module-01-foundations-of-ai-in-healthcare/module.yaml"
    lesson_readme = "modules/module-01-foundations-of-ai-in-healthcare/lessons/README.md"
    assert by_path[module_yaml].scope == "module"
    assert by_path[lesson_readme].scope == "lesson"
    assert by_path[lesson_readme].lesson_id is None


def test_scaffold_reference_files_do_not_mark_source_complete() -> None:
    scan = scan_course(PHS_ROOT)
    roles = {entry.path: entry.source_role for entry in scan.manifest.entries}
    gaps = {gap.declared["source_kind"]: gap for gap in scan.gap_ledger.gaps if gap.declared}

    assert roles["sources/course/PHS 620 Syllabus 2025.doc"] == "reference"
    assert any(gap.kind == "source_availability" for gap in scan.gap_ledger.gaps)
    assert scan.manifest.gap_summary["source_availability"] >= 1
    assert {"canvas_current_course_content", "confluence_current_course_content"} <= set(gaps)
    assert all(gap.access_note for gap in gaps.values())


def test_empty_source_and_lesson_dirs_are_gaps_not_crashes(tmp_path: Path) -> None:
    course_root = tmp_path / "course"
    (course_root / "sources" / "course").mkdir(parents=True)
    (course_root / "sources" / "shared").mkdir(parents=True)
    (course_root / "modules" / "module-01" / "sources").mkdir(parents=True)
    (course_root / "modules" / "module-01" / "lessons").mkdir(parents=True)
    (course_root / "course.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": "0.1",
                "course_id": "course-x",
                "sme": {"name": "SME"},
                "course": {
                    "code": "X 100",
                    "title": "Course X",
                    "module_count_expected": 1,
                },
                "modules": [{"module_id": "module-01", "title": "Module 1"}],
                "runtime_contract": {
                    "runnable_input_scope": "lesson_corpus_leaf",
                    "do_not_run_from": ["course_root", "module_root"],
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    scan = scan_course(course_root)

    assert {gap.kind for gap in scan.gap_ledger.gaps} >= {
        "empty_source_dir",
        "empty_lesson_dir",
    }


def test_nested_lesson_leaf_content_prevents_false_empty_gap(tmp_path: Path) -> None:
    course_root = tmp_path / "course"
    source_file = (
        course_root / "modules" / "module-01" / "lessons" / "lesson-01" / "source.md"
    )
    source_file.parent.mkdir(parents=True)
    source_file.write_text("real source", encoding="utf-8")
    (course_root / "modules" / "module-01" / "sources").mkdir(parents=True)
    (course_root / "course.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": "0.1",
                "course_id": "course-x",
                "sme": {"name": "SME"},
                "course": {
                    "code": "X 100",
                    "title": "Course X",
                    "module_count_expected": 1,
                },
                "modules": [{"module_id": "module-01", "title": "Module 1"}],
                "runtime_contract": {
                    "runnable_input_scope": "lesson_corpus_leaf",
                    "do_not_run_from": ["course_root", "module_root"],
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    scan = scan_course(course_root)

    gap_paths = {gap.path for gap in scan.gap_ledger.gaps}
    assert "modules/module-01/lessons" not in gap_paths
    by_path = {entry.path: entry for entry in scan.manifest.entries}
    assert by_path["modules/module-01/lessons/lesson-01/source.md"].lesson_id == "lesson-01"
