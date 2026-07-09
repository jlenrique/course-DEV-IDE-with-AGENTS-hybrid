"""RED/GREEN live tests for Marcus plan-ratify CLI (AC-M1/M2/M3/M7)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.marcus.cli import __main__ as marcus_main
from app.marcus.cli.plan_ratify_cli import main as plan_ratify_main
from app.marcus.lesson_plan.planning_ratification import PlanningRatificationRecord

REPO_ROOT = Path(__file__).resolve().parents[3]
TEJAL = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)


def _base_argv(output_dir: Path, **overrides: str) -> list[str]:
    args = {
        "--purpose": "Bridge assessments to Module 2",
        "--audience": "APC C1 learners",
        "--workflow": "narrated-deck",
        "--gap-fill-chosen": "synthesize",
        "--gap-fill-considered": "synthesize,wait",
        "--gap-fill-rationale": "Rich curated source; synthesize framing",
        "--output-dir": str(output_dir),
        "--corpus-dir": str(TEJAL),
    }
    args.update({f"--{k.replace('_', '-')}": v for k, v in overrides.items()})
    flat: list[str] = []
    for key, value in args.items():
        flat.extend([key, value])
    return flat


def test_plan_ratify_writes_companion_and_intent(tmp_path: Path) -> None:
    code = plan_ratify_main(_base_argv(tmp_path))
    assert code == 0
    companion = tmp_path / "planning-ratification.json"
    intent = tmp_path / "ratified-collateral-intent.yaml"
    assert companion.is_file()
    assert intent.is_file()
    record = PlanningRatificationRecord.model_validate_json(
        companion.read_text(encoding="utf-8")
    )
    assert "Module 2" in record.purpose
    assert record.workflow == "narrated-deck"


def test_plan_ratify_via_marcus_cli_entrypoint(tmp_path: Path) -> None:
    argv = ["plan-ratify", *_base_argv(tmp_path)]
    code = marcus_main.main(argv)
    assert code == 0
    assert (tmp_path / "planning-ratification.json").is_file()


def test_plan_ratify_requires_assessment_source(tmp_path: Path) -> None:
    # argparse mutually_exclusive_group required=True → SystemExit
    with pytest.raises(SystemExit) as excinfo:
        plan_ratify_main(
            [
                "--purpose",
                "p",
                "--audience",
                "a",
                "--workflow",
                "narrated-deck",
                "--gap-fill-chosen",
                "synthesize",
                "--gap-fill-considered",
                "synthesize,wait",
                "--output-dir",
                str(tmp_path),
            ]
        )
    assert excinfo.value.code != 0
    assert not (tmp_path / "planning-ratification.json").exists()


def test_plan_ratify_fail_loud_invalid_gap_fill(tmp_path: Path) -> None:
    code = plan_ratify_main(
        _base_argv(
            tmp_path,
            gap_fill_chosen="synthesize",
            gap_fill_considered="wait,lighter_collateral",
        )
    )
    assert code == 2
    assert not (tmp_path / "planning-ratification.json").exists()


def test_plan_ratify_fail_loud_overclaim_purpose(tmp_path: Path) -> None:
    code = plan_ratify_main(
        _base_argv(
            tmp_path,
            purpose="We achieved full lecture ingestion for this module",
        )
    )
    assert code == 2


def test_plan_ratify_workbook_without_collateral_fails(tmp_path: Path) -> None:
    code = plan_ratify_main(
        _base_argv(
            tmp_path,
            workflow="narrated-deck-with-workbook",
            gap_fill_chosen="synthesize",
            gap_fill_considered="synthesize,wait",
        )
    )
    assert code == 2
