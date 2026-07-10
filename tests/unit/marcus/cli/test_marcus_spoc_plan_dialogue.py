"""Mine-next N2-lite — SPOC plan-dialogue preflight wire."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from app.marcus.cli.marcus_spoc import (
    main as spoc_main,
    narrate_plan_dialogue_preflight,
    run_plan_dialogue_preflight,
)
from app.marcus.cli.plan_dialogue_cli import PlanDialogueError
from app.marcus.lesson_plan.planning_context import load_planning_context

REPO_ROOT = Path(__file__).resolve().parents[4]
TEJAL = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)


def test_narrate_plan_dialogue_preflight_names_lo_workflow() -> None:
    text = narrate_plan_dialogue_preflight()
    assert "learning objectives" in text.lower()
    assert "workflow" in text.lower()
    assert "Marcus-SPOC" in text


def test_run_plan_dialogue_preflight_writes_companions(tmp_path: Path) -> None:
    script = tmp_path / "script.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "purpose": "SPOC-owned planning for N2",
                "audience": "APC C1 learners",
                "workflow": "narrated-deck",
                "gap_fill_considered": "synthesize,wait",
                "gap_fill_chosen": "synthesize",
                "gap_fill_rationale": "Tejal leaf",
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
    paths = run_plan_dialogue_preflight(
        corpus_dir=TEJAL,
        output_dir=out,
        script=script,
    )
    assert paths["companion"].is_file()
    assert paths["ratified_los"].is_file()
    assert (out / "ratified-collateral-intent.yaml").is_file()
    ctx = load_planning_context(out)
    assert ctx is not None
    assert ctx.has_framing()
    assert len(ctx.learning_objectives) == 2


def test_spoc_main_plan_dialogue_flag(tmp_path: Path) -> None:
    script = tmp_path / "script.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "purpose": "CLI SPOC plan-dialogue",
                "audience": "learners",
                "workflow": "narrated-deck",
                "gap_fill_considered": "synthesize,wait",
                "gap_fill_chosen": "synthesize",
                "learning_objectives": ["LO one", "LO two"],
                "confirm": "yes",
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "spoc-out"
    code = spoc_main(
        [
            "--plan-dialogue",
            "--corpus-dir",
            str(TEJAL),
            "--plan-output-dir",
            str(out),
            "--plan-script",
            str(script),
        ]
    )
    assert code == 0
    assert (out / "planning-ratification.json").is_file()
    assert (out / "ratified-los.json").is_file()
    los = json.loads((out / "ratified-los.json").read_text(encoding="utf-8"))
    assert len(los["ratified_los"]) == 2


def test_spoc_plan_dialogue_confirm_decline_fail_loud(tmp_path: Path) -> None:
    script = tmp_path / "decline.yaml"
    script.write_text(
        yaml.safe_dump(
            {
                "purpose": "p",
                "audience": "a",
                "workflow": "narrated-deck",
                "gap_fill_considered": "synthesize,wait",
                "gap_fill_chosen": "synthesize",
                "learning_objectives": ["x"],
                "confirm": "no",
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(PlanDialogueError, match="aborted"):
        run_plan_dialogue_preflight(
            corpus_dir=TEJAL,
            output_dir=tmp_path / "declined",
            script=script,
        )
