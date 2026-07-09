"""RED/GREEN tests for Phase-2 source assessment (AC-P2-1)."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.marcus.course_source.input_bundle import build_lesson_planning_input_bundle
from app.marcus.lesson_plan.source_assessment import (
    SourceAssessmentError,
    assess_from_corpus_dir,
    assess_from_input_bundle,
    assessments_differ_in_kind_or_count,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = (
    REPO_ROOT
    / "_bmad-output"
    / "implementation-artifacts"
    / "evidence"
    / "s7p2-story-b-syllabus-metadata-20260708T110225"
)
HAI_ROOT = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "aziz-nazha-hai-510-generative-ai-in-healthcare"
)
PHS_ROOT = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "juan-leon-phs-620-teaching-learning-seminar"
)
TEJAL_RICH = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)


def _hai_assessment():
    bundle = build_lesson_planning_input_bundle(
        course_root=HAI_ROOT,
        proposal_path=EVIDENCE / "hai-510" / "module-metadata.yaml",
        module_id="module-01-foundations-of-ai-in-healthcare",
        operator_focus="Plan around missing lecture video and slide source.",
    )
    return assess_from_input_bundle(bundle)


def _phs_assessment():
    bundle = build_lesson_planning_input_bundle(
        course_root=PHS_ROOT,
        proposal_path=EVIDENCE / "phs-620" / "module-metadata.yaml",
        module_id="module-01",
        operator_focus="Enhance existing course content after Confluence and Canvas access.",
    )
    return assess_from_input_bundle(bundle)


def test_source_assessment_classifies_hai_as_thin_path() -> None:
    assessment = _hai_assessment()
    assert assessment.richness == "thin"
    assert assessment.gap_count >= 1
    assert assessment.gap_summaries
    assert "course-source-bundle" in assessment.tags


def test_source_assessment_classifies_phs_as_thin_path() -> None:
    assessment = _phs_assessment()
    assert assessment.richness == "thin"
    assert assessment.gap_count >= 1
    assert assessment.gap_summaries
    assert "course-source-bundle" in assessment.tags


def test_source_assessment_classifies_tejal_as_rich_path() -> None:
    assessment = assess_from_corpus_dir(TEJAL_RICH, corpus_id="tejal-c1m1-p4")
    assert assessment.richness == "rich"
    assert assessment.detected_file_count >= 3
    assert any(tag.startswith("bucket:") for tag in assessment.tags)


def test_thin_and_rich_assessments_differ_in_kind_or_count() -> None:
    hai = _hai_assessment()
    phs = _phs_assessment()
    tejal = assess_from_corpus_dir(TEJAL_RICH, corpus_id="tejal-c1m1-p4")
    assert assessments_differ_in_kind_or_count(hai, tejal)
    assert assessments_differ_in_kind_or_count(phs, tejal)


def test_course_root_refused_as_corpus_leaf() -> None:
    with pytest.raises(SourceAssessmentError, match="course/module container"):
        assess_from_corpus_dir(HAI_ROOT)
