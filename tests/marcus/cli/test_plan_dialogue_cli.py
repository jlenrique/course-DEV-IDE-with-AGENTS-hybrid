"""Tests for interactive plan-dialogue CLI (Mine 2A)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from app.marcus.cli import __main__ as marcus_main
from app.marcus.cli.plan_dialogue_cli import (
    PlanDialogueError,
    PlanDialogueSession,
    main as plan_dialogue_main,
)
from app.marcus.lesson_plan.planning_context import load_planning_context
from app.marcus.lesson_plan.planning_ratification import PlanningRatificationRecord

REPO_ROOT = Path(__file__).resolve().parents[3]
TEJAL = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)


def _script_answers(
    *,
    confirm: str = "yes",
    workflow: str = "narrated-deck",
    gap_chosen: str = "synthesize",
    gap_considered: str = "synthesize,wait",
    los: str = "Map radar to leadership; Apply bridge framing",
) -> list[str]:
    return [
        "Bridge assessments to Module 2",
        "APC C1 learners",
        workflow,
        gap_considered,
        gap_chosen,
        "Rich curated source",
        los,
        confirm,
    ]


def test_plan_dialogue_scripted_writes_companions_and_los(tmp_path: Path) -> None:
    script = tmp_path / "answers.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "purpose": "Bridge assessments to Module 2",
                "audience": "APC C1 learners",
                "workflow": "narrated-deck",
                "gap_fill_considered": "synthesize,wait",
                "gap_fill_chosen": "synthesize",
                "gap_fill_rationale": "Rich curated source",
                "learning_objectives": [
                    "Map radar to leadership",
                    "Apply bridge framing",
                ],
                "confirm": "yes",
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "run"
    code = plan_dialogue_main(
        [
            "--corpus-dir",
            str(TEJAL),
            "--output-dir",
            str(out),
            "--script",
            str(script),
        ]
    )
    assert code == 0
    assert (out / "planning-ratification.json").is_file()
    assert (out / "ratified-collateral-intent.yaml").is_file()
    assert (out / "ratified-los.json").is_file()
    assert (out / "marcus-planning-dialogue.md").is_file()
    record = PlanningRatificationRecord.model_validate_json(
        (out / "planning-ratification.json").read_text(encoding="utf-8")
    )
    assert record.workflow == "narrated-deck"
    los = json.loads((out / "ratified-los.json").read_text(encoding="utf-8"))
    assert len(los["ratified_los"]) == 2
    ctx = load_planning_context(out)
    assert ctx is not None
    assert ctx.has_framing()
    assert len(ctx.learning_objectives) == 2
    transcript = (out / "marcus-planning-dialogue.md").read_text(encoding="utf-8")
    assert "Turn 1" in transcript
    assert "Turn 2" in transcript


def test_plan_dialogue_via_marcus_cli_entrypoint(tmp_path: Path) -> None:
    script = tmp_path / "answers.json"
    script.write_text(
        json.dumps(
            {
                "purpose": "p",
                "audience": "a",
                "workflow": "narrated-deck",
                "gap_fill_considered": "synthesize,wait",
                "gap_fill_chosen": "synthesize",
                "gap_fill_rationale": "r",
                "learning_objectives": ["Learn X"],
                "confirm": "y",
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out"
    code = marcus_main.main(
        [
            "plan-dialogue",
            "--corpus-dir",
            str(TEJAL),
            "--output-dir",
            str(out),
            "--script",
            str(script),
        ]
    )
    assert code == 0
    assert (out / "planning-ratification.json").is_file()


def test_plan_dialogue_confirm_decline_aborts(tmp_path: Path) -> None:
    import argparse

    answers = iter(_script_answers(confirm="no"))
    session = PlanDialogueSession(
        output_dir=tmp_path / "abort",
        assess_args=argparse.Namespace(
            corpus_dir=TEJAL,
            course_root=None,
            proposal_path=None,
            module_id=None,
            operator_focus="focus",
            corpus_id="",
        ),
        input_source=lambda _p: next(answers),
        output_sink=lambda _t: None,
    )
    with pytest.raises(PlanDialogueError, match="aborted"):
        session.run()
    assert not (tmp_path / "abort" / "planning-ratification.json").exists()


def test_plan_dialogue_malformed_workflow_fail_loud(tmp_path: Path) -> None:
    script = tmp_path / "bad.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "purpose": "p",
                "audience": "a",
                "workflow": "not-a-real-workflow",
                "gap_fill_considered": "synthesize,wait",
                "gap_fill_chosen": "synthesize",
                "learning_objectives": ["x"],
                "confirm": "yes",
            }
        ),
        encoding="utf-8",
    )
    code = plan_dialogue_main(
        [
            "--corpus-dir",
            str(TEJAL),
            "--output-dir",
            str(tmp_path / "out"),
            "--script",
            str(script),
        ]
    )
    assert code == 2


def test_plan_dialogue_missing_source_fail_loud(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        plan_dialogue_main(
            [
                "--output-dir",
                str(tmp_path),
                "--script",
                str(tmp_path / "missing.yaml"),
            ]
        )
