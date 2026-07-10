"""RED/GREEN live tests for PlanningContext loader (AC-H1).

Live-tested as the first major component of the Irene Pass-1 handoff.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.marcus.lesson_plan.planning_context import (
    PlanningContextError,
    load_planning_context,
)
from app.marcus.lesson_plan.source_assessment import GapSummary, SourceAssessment


def _minimal_assessment() -> dict:
    return SourceAssessment(
        course_or_corpus_id="hai-510",
        richness="thin",
        tags=("course-source-bundle", "module:module-01"),
        gap_summaries=(
            GapSummary(kind="missing_lecture_video", count=1, sample_message="no video"),
        ),
        gap_count=1,
        asset_record_count=2,
        detected_file_count=3,
        notes="thin syllabus path",
    ).model_dump(mode="json")


def _write_ratification(
    run_dir: Path,
    *,
    purpose: str = "Teach clinicians when generative AI is appropriate",
    audience: str = "Practicing clinicians new to generative AI",
) -> None:
    payload = {
        "schema_version": "0.1",
        "purpose": purpose,
        "audience": audience,
        "source_assessment": _minimal_assessment(),
        "assets_to_create": [],
        "workflow": "narrated-deck",
        "gap_fill": {
            "chosen": "synthesize",
            "considered": ["synthesize", "wait"],
            "rationale": "Thin syllabus; synthesize framing",
        },
        "claim_fence": (
            "Does not claim full lecture ingestion or lecture-complete selection."
        ),
        "s8_intent": {
            "ratification_status": "ratified",
            "bundle_id": "narrated-deck",
        },
    }
    (run_dir / "planning-ratification.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def _write_ratified_los(run_dir: Path, statements: list[str]) -> None:
    payload = {
        "ratified_los": [
            {
                "objective_id": f"lo-{i:03d}",
                "statement": statement,
                "bloom_level": "understand",
                "status": "ratified",
            }
            for i, statement in enumerate(statements, start=1)
        ]
    }
    (run_dir / "ratified-los.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def test_absent_artifacts_returns_none(tmp_path: Path) -> None:
    assert load_planning_context(tmp_path) is None


def test_ratification_only_loads_purpose_audience_assessment(tmp_path: Path) -> None:
    _write_ratification(tmp_path)
    ctx = load_planning_context(tmp_path)
    assert ctx is not None
    assert "clinicians" in ctx.purpose.lower()
    assert "clinicians" in ctx.audience.lower()
    assert ctx.source_assessment is not None
    assert ctx.source_assessment.richness == "thin"
    assert ctx.learning_objectives == ()
    assert "planning-ratification.json" in ctx.sources_present


def test_ratified_los_only_loads_objectives(tmp_path: Path) -> None:
    _write_ratified_los(
        tmp_path,
        ["Identify appropriate generative-AI use cases in clinic"],
    )
    ctx = load_planning_context(tmp_path)
    assert ctx is not None
    assert ctx.purpose == ""
    assert ctx.audience == ""
    assert len(ctx.learning_objectives) == 1
    assert "generative-AI" in ctx.learning_objectives[0].statement
    assert "ratified-los.json" in ctx.sources_present


def test_merge_prefers_ratified_los_for_objectives(tmp_path: Path) -> None:
    _write_ratification(tmp_path)
    _write_ratified_los(
        tmp_path,
        [
            "List risks of generative AI in clinical documentation",
            "Apply a simple triage rule for AI-assisted drafting",
        ],
    )
    ctx = load_planning_context(tmp_path)
    assert ctx is not None
    assert "clinicians" in ctx.purpose.lower()
    assert len(ctx.learning_objectives) == 2
    assert set(ctx.sources_present) == {
        "planning-ratification.json",
        "ratified-los.json",
    }


def test_empty_ratified_los_does_not_block_ratification(tmp_path: Path) -> None:
    _write_ratification(tmp_path)
    (tmp_path / "ratified-los.json").write_text(
        json.dumps({"ratified_los": []}),
        encoding="utf-8",
    )
    ctx = load_planning_context(tmp_path)
    assert ctx is not None
    assert ctx.learning_objectives == ()
    assert ctx.purpose


def test_malformed_ratification_fails_loud(tmp_path: Path) -> None:
    (tmp_path / "planning-ratification.json").write_text("{not-json", encoding="utf-8")
    with pytest.raises(PlanningContextError, match="planning-ratification"):
        load_planning_context(tmp_path)


def test_malformed_ratified_los_fails_loud(tmp_path: Path) -> None:
    (tmp_path / "ratified-los.json").write_text("{not-json", encoding="utf-8")
    with pytest.raises(PlanningContextError, match="ratified-los"):
        load_planning_context(tmp_path)


def test_conflicting_purpose_across_files_fails_loud(tmp_path: Path) -> None:
    _write_ratification(tmp_path, purpose="Purpose A")
    payload = {
        "purpose": "Purpose B",
        "ratified_los": [
            {
                "objective_id": "lo-001",
                "statement": "Identify appropriate generative-AI use cases",
                "status": "ratified",
            }
        ],
    }
    (tmp_path / "ratified-los.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    with pytest.raises(PlanningContextError, match="conflicting non-empty purpose"):
        load_planning_context(tmp_path)


def test_tokenless_lo_is_not_auto_supported() -> None:
    from app.marcus.lesson_plan.planning_context import (
        LearningObjectiveBrief,
        PlanningContext,
        assess_lo_coverage,
    )

    ctx = PlanningContext(
        learning_objectives=(
            LearningObjectiveBrief(objective_id="lo-short", statement="Use AI"),
        ),
        sources_present=("ratified-los.json",),
    )
    receipt = assess_lo_coverage(
        ctx,
        {
            "plan_units": [
                {
                    "title": "Use AI",
                    "learning_objective": "Use AI",
                    "rationale": "x",
                }
            ]
        },
    )
    assert "lo-short" in receipt.weak_or_missing_objective_ids
    assert receipt.lo_coverage == "absent"
