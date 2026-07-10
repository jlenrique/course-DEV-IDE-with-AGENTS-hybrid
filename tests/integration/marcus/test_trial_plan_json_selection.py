"""Trial start consumes --lesson-plan-json auto-derived selection (Mine 1 seam)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.cli.trial import start_trial
from app.marcus.lesson_plan.collateral_spec import (
    CollateralSpec,
    DepthDeltaContract,
    WorkbookSection,
    WorkbookSpec,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
FIXTURE_INPUT = Path("tests/fixtures/trial_corpus/README.md")


def _workbook_plan_json(path: Path) -> Path:
    collateral = CollateralSpec(
        declaration="present",
        workbook=WorkbookSpec(
            sections=[
                WorkbookSection(
                    section_id="sec-1",
                    learning_objective_id="obj-1",
                    title="Depth",
                    depth_delta=DepthDeltaContract(
                        deferred_from_slide="slide-1",
                        deferred_depth="supporting method",
                    ),
                )
            ]
        ),
    )
    plan = {
        "lesson_summary": "seam test",
        "plan_units": [],
        "collateral": collateral.model_dump(mode="json"),
    }
    path.write_text(json.dumps(plan), encoding="utf-8")
    return path


def test_start_trial_consumes_lesson_plan_json_selection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    captured: dict[str, object] = {}

    def _spy(**kwargs: object) -> None:
        captured.update(kwargs)
        raise RuntimeError("stop-after-capture")

    monkeypatch.setattr("app.marcus.cli.trial.run_production_trial", _spy)

    plan_json = _workbook_plan_json(tmp_path / "irene-pass1.lesson-plan.json")
    with pytest.raises(RuntimeError, match="stop-after-capture"):
        start_trial(
            preset="production",
            input_path=FIXTURE_INPUT,
            operator_id="operator_plan_json_seam",
            trial_id=uuid4(),
            allow_offline_cost_report=True,
            runs_root=tmp_path / "runs",
            lesson_plan_collateral_intent_path=plan_json,
            lesson_plan_collateral_bundle_id="narrated-deck-with-workbook",
        )

    selection = captured["component_selection"]
    assert selection is not None
    assert selection.as_map() == {"deck": True, "motion": True, "workbook": True}
    receipt = (tmp_path / "runs").glob("*/trial-start.json")
    # trial-start may not write if we stop inside run_production_trial after
    # selection is already threaded — capture is the binding proof.
    assert captured.get("component_selection") is not None
    _ = list(receipt)  # silence unused
