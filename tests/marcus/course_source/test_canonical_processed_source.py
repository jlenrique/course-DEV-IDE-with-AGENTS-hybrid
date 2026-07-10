"""Tests for canonical processed-source contract (Mine 4A)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.marcus.course_source.canonical_processed_source import (
    CanonicalProcessedSourceError,
    annotate_typed_components_with_kind,
    resolve_asset_kind,
    validate_canonical_tree,
    write_canonical_contract_doc,
)
from app.marcus.lesson_plan.source_type import TypedComponent

REPO_ROOT = Path(__file__).resolve().parents[3]
TEJAL = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)
SAMPLE_ENRICHMENT = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "coverage-reprove-covered-faithful-20260630T193322Z"
    / "g0-enrichment.json"
)


def test_tejal_lesson_leaf_passes() -> None:
    result = validate_canonical_tree(TEJAL, scope="lesson_leaf")
    assert result.ok
    assert not result.errors
    assert len(result.digests) == 3


def test_incomplete_lesson_leaf_fail_loud(tmp_path: Path) -> None:
    (tmp_path / "slides").mkdir()
    # missing references/ and assessments/
    result = validate_canonical_tree(tmp_path, scope="lesson_leaf")
    assert not result.ok
    assert any("references" in e for e in result.errors)
    assert any("assessments" in e for e in result.errors)
    with pytest.raises(CanonicalProcessedSourceError):
        result.raise_if_failed()


def test_resolve_asset_kind_mapping() -> None:
    assert resolve_asset_kind("slide").value == "lecture"
    assert resolve_asset_kind("quiz").value == "assessment"
    assert resolve_asset_kind("exercise_lab").value == "lab"


def test_run_dir_requires_kind_shape_pin(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text("# extracted\n", encoding="utf-8")
    raw = json.loads(SAMPLE_ENRICHMENT.read_text(encoding="utf-8"))
    # Legacy card: no kind → fail
    (tmp_path / "g0-enrichment.json").write_text(
        json.dumps(raw), encoding="utf-8"
    )
    result = validate_canonical_tree(tmp_path, scope="run_dir")
    assert not result.ok
    assert any("missing required kind" in e for e in result.errors)

    annotated = annotate_typed_components_with_kind(raw)
    (tmp_path / "g0-enrichment.json").write_text(
        json.dumps(annotated), encoding="utf-8"
    )
    result2 = validate_canonical_tree(tmp_path, scope="run_dir")
    assert result2.ok, result2.errors
    assert result2.kind_counts
    # TypedComponent accepts kind
    first = TypedComponent.model_validate(annotated["typed_components"][0])
    assert first.kind == "lecture"


def test_incomplete_run_dir_fail_loud(tmp_path: Path) -> None:
    result = validate_canonical_tree(tmp_path, scope="run_dir")
    assert not result.ok
    assert any("bundle/extracted.md" in e for e in result.errors)
    assert any("g0-enrichment.json" in e for e in result.errors)


def test_kind_disagreement_fail_loud(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    (bundle / "extracted.md").write_text("# x\n", encoding="utf-8")
    raw = json.loads(SAMPLE_ENRICHMENT.read_text(encoding="utf-8"))
    annotated = annotate_typed_components_with_kind(raw)
    annotated["typed_components"][0]["kind"] = "reading"  # slide → should be lecture
    (tmp_path / "g0-enrichment.json").write_text(
        json.dumps(annotated), encoding="utf-8"
    )
    result = validate_canonical_tree(tmp_path, scope="run_dir")
    assert not result.ok
    assert any("disagrees" in e for e in result.errors)


def test_write_canonical_contract_doc(tmp_path: Path) -> None:
    path = write_canonical_contract_doc(tmp_path / "canonical.md")
    text = path.read_text(encoding="utf-8")
    assert "slides/" in text
    assert "kind" in text
    assert "AssetKind" in text
