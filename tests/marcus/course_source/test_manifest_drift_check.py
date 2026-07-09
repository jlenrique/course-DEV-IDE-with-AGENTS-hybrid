from __future__ import annotations

from pathlib import Path

from app.marcus.course_source.manifest_drift import check_manifest_snapshot
from app.marcus.course_source.manifest_scan import (
    render_manifest_yaml,
    scan_course,
    write_manifest_snapshot,
)


def _course_root(tmp_path: Path) -> Path:
    root = tmp_path / "course"
    (root / "sources" / "course").mkdir(parents=True)
    (root / "course.yaml").write_text(
        "\n".join(
            [
                "schema_version: 0.1",
                "course_id: course-x",
                "sme:",
                "  name: SME",
                "course:",
                "  code: X 100",
                "  title: Course X",
                "  module_count_expected: 0",
                "runtime_contract:",
                "  runnable_input_scope: lesson_corpus_leaf",
                "  do_not_run_from:",
                "    - course_root",
                "    - module_root",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return root


def test_clean_manifest_snapshot_passes(tmp_path: Path) -> None:
    root = _course_root(tmp_path)
    snapshot = write_manifest_snapshot(scan_course(root), root / "source-manifest.yaml")

    assert check_manifest_snapshot(root, snapshot).is_stale is False


def test_disk_drift_fails_with_named_path(tmp_path: Path) -> None:
    root = _course_root(tmp_path)
    snapshot = write_manifest_snapshot(scan_course(root), root / "source-manifest.yaml")
    (root / "sources" / "course" / "new-source.md").write_text("new", encoding="utf-8")

    result = check_manifest_snapshot(root, snapshot)

    assert result.is_stale is True
    assert "sources/course/new-source.md" in result.diff


def test_manifest_snapshot_contains_summary_not_full_gap_ledger(tmp_path: Path) -> None:
    root = _course_root(tmp_path)
    text = render_manifest_yaml(scan_course(root).manifest)

    assert "gap_summary:" in text
    assert "gaps:" not in text
