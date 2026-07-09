"""Integration: plan-ratify writes are loadable by planning_context + intent path."""

from __future__ import annotations

from pathlib import Path

from app.marcus.cli.plan_ratify_cli import main as plan_ratify_main
from app.marcus.cli.trial import _resolve_start_component_selection
from app.marcus.lesson_plan.planning_context import load_planning_context
from app.marcus.lesson_plan.planning_ratification import resolve_intent_file

REPO_ROOT = Path(__file__).resolve().parents[3]
TEJAL = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)


def _ratify(output_dir: Path) -> int:
    return plan_ratify_main(
        [
            "--purpose",
            "Bridge assessments to Module 2",
            "--audience",
            "APC C1 learners",
            "--workflow",
            "narrated-deck",
            "--gap-fill-chosen",
            "synthesize",
            "--gap-fill-considered",
            "synthesize,wait",
            "--gap-fill-rationale",
            "Rich curated source",
            "--output-dir",
            str(output_dir),
            "--corpus-dir",
            str(TEJAL),
        ]
    )


def test_written_artifacts_load_via_planning_context(tmp_path: Path) -> None:
    assert _ratify(tmp_path) == 0
    ctx = load_planning_context(tmp_path)
    assert ctx is not None
    assert "Module 2" in ctx.purpose
    assert ctx.source_assessment is not None
    assert ctx.source_assessment.richness == "rich"


def test_written_intent_resolves_as_ratified(tmp_path: Path) -> None:
    assert _ratify(tmp_path) == 0
    resolved = resolve_intent_file(tmp_path / "ratified-collateral-intent.yaml")
    assert resolved.source == "ratified"
    assert resolved.bundle_id == "narrated-deck"


def test_intent_path_usable_like_trial_flag(tmp_path: Path) -> None:
    """AC-M4: same resolution path trial start uses for collateral intent."""
    assert _ratify(tmp_path) == 0
    intent = tmp_path / "ratified-collateral-intent.yaml"

    class _Args:
        lesson_plan_collateral_intent = intent
        bundle = None
        deck = None
        motion = None
        workbook = None

    start = _resolve_start_component_selection(_Args())
    assert start.lesson_plan_collateral_intent_path == intent
    assert start.selection.deck is True


def test_absent_path_load_planning_context_none(tmp_path: Path) -> None:
    assert load_planning_context(tmp_path) is None
