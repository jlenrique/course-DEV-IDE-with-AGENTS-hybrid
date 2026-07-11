"""Trial start consumes --lesson-plan-json auto-derived selection (Mine 1 seam)."""

from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

import pytest

import app.marcus.cli.trial as trial_mod
from app.marcus.cli.trial import start_trial
from app.marcus.lesson_plan.collateral_selection import CollateralSelectionError
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


def _install_loader_spies(
    monkeypatch: pytest.MonkeyPatch,
) -> tuple[list[Path], list[Path]]:
    """Spy on BOTH loaders in the trial-module namespace, delegating to the real
    functions, so the tests observe WHICH loader the programmatic sniff routes
    to — not merely the downstream selection value (loop-1 hollow-pin fix)."""
    intent_calls: list[Path] = []
    plan_calls: list[Path] = []
    real_intent = trial_mod.load_lesson_plan_collateral_selection
    real_plan = trial_mod.load_selection_from_lesson_plan_json
    monkeypatch.setattr(
        "app.marcus.cli.trial.load_lesson_plan_collateral_selection",
        lambda p: (intent_calls.append(p), real_intent(p))[1],
    )
    monkeypatch.setattr(
        "app.marcus.cli.trial.load_selection_from_lesson_plan_json",
        lambda p: (plan_calls.append(p), real_plan(p))[1],
    )
    return intent_calls, plan_calls


def test_start_trial_sniff_fall_through_routes_to_intent_loader(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sniff fall-through pin: a dict with no ratification_status and no plan
    keys routes to the intent loader and binds nothing (component_selection
    stays None; the source value itself is not observed here). Current
    behavior, pinned as-is — its design disposition is a filed defer."""
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_calls, plan_calls = _install_loader_spies(monkeypatch)
    captured: dict[str, object] = {}

    def _spy(**kwargs: object) -> None:
        captured.update(kwargs)
        raise RuntimeError("stop-after-capture")

    monkeypatch.setattr("app.marcus.cli.trial.run_production_trial", _spy)

    note_path = tmp_path / "note.json"
    note_path.write_text(json.dumps({"note": "not a plan"}), encoding="utf-8")
    with pytest.raises(RuntimeError, match="stop-after-capture"):
        start_trial(
            preset="production",
            input_path=FIXTURE_INPUT,
            operator_id="operator_sniff_fall_through",
            trial_id=uuid4(),
            allow_offline_cost_report=True,
            runs_root=tmp_path / "runs",
            lesson_plan_collateral_intent_path=note_path,
        )

    # Routing observation: intent loader fired with the passed path; the plan
    # loader never fired — distinguishes routed-and-bound-nothing from
    # silently-ignored (the loop-1 known-bad state).
    assert intent_calls == [note_path]
    assert plan_calls == []
    assert captured["component_selection"] is None


def test_start_trial_sniff_routes_unratified_plan_shape_to_plan_loader(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sniff boundary pin: a plan-shaped dict carrying ratification_status !=
    "ratified" still routes to the PLAN loader (the `!= "ratified"` predicate
    arm), which fails loud on missing collateral before any walk."""
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_calls, plan_calls = _install_loader_spies(monkeypatch)

    def _never_walk(**kwargs: object) -> None:
        raise AssertionError("run_production_trial must not be reached")

    monkeypatch.setattr("app.marcus.cli.trial.run_production_trial", _never_walk)

    draft_path = tmp_path / "draft.lesson-plan.json"
    draft_path.write_text(
        json.dumps({"plan_units": [], "ratification_status": "draft"}),
        encoding="utf-8",
    )
    with pytest.raises(
        CollateralSelectionError, match="lesson_plan.collateral is required"
    ):
        start_trial(
            preset="production",
            input_path=FIXTURE_INPUT,
            operator_id="operator_sniff_boundary",
            trial_id=uuid4(),
            allow_offline_cost_report=True,
            runs_root=tmp_path / "runs",
            lesson_plan_collateral_intent_path=draft_path,
        )

    assert plan_calls == [draft_path]
    assert intent_calls == []


def test_start_trial_ratified_stamped_plan_shape_routes_to_intent_loader(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sniff boundary pin: a plan-shaped dict stamped ratification_status ==
    "ratified" routes to the INTENT loader (pins the `!= "ratified"` FALSE arm
    of the sniff), where the closed ratified-intent shape rejects the extra
    plan keys and fails loud before any walk. The routing assertions are the
    point; the raise is the intent loader's own validation behavior."""
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_calls, plan_calls = _install_loader_spies(monkeypatch)

    def _never_walk(**kwargs: object) -> None:
        raise AssertionError("run_production_trial must not be reached")

    monkeypatch.setattr("app.marcus.cli.trial.run_production_trial", _never_walk)

    stamped_path = tmp_path / "stamped.lesson-plan.json"
    stamped_path.write_text(
        json.dumps({"plan_units": [], "ratification_status": "ratified"}),
        encoding="utf-8",
    )
    with pytest.raises(
        CollateralSelectionError, match="closed ratified intent validation failed"
    ):
        start_trial(
            preset="production",
            input_path=FIXTURE_INPUT,
            operator_id="operator_sniff_ratified_stamped",
            trial_id=uuid4(),
            allow_offline_cost_report=True,
            runs_root=tmp_path / "runs",
            lesson_plan_collateral_intent_path=stamped_path,
        )

    assert intent_calls == [stamped_path]
    assert plan_calls == []


def test_start_trial_wrapper_shape_routes_to_plan_loader(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sniff disjunct pin: a {"lesson_plan": {...}} contribution wrapper (no
    top-level collateral/plan_units, no ratification_status) routes to the
    PLAN loader via the third sniff disjunct (`isinstance(raw.get(
    "lesson_plan"), dict)`), which unwraps the plan and fails loud on missing
    collateral before any walk."""
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    intent_calls, plan_calls = _install_loader_spies(monkeypatch)

    def _never_walk(**kwargs: object) -> None:
        raise AssertionError("run_production_trial must not be reached")

    monkeypatch.setattr("app.marcus.cli.trial.run_production_trial", _never_walk)

    wrapper_path = tmp_path / "wrapper.lesson-plan.json"
    wrapper_path.write_text(
        json.dumps({"lesson_plan": {"plan_units": []}}),
        encoding="utf-8",
    )
    with pytest.raises(
        CollateralSelectionError, match="lesson_plan.collateral is required"
    ):
        start_trial(
            preset="production",
            input_path=FIXTURE_INPUT,
            operator_id="operator_sniff_wrapper",
            trial_id=uuid4(),
            allow_offline_cost_report=True,
            runs_root=tmp_path / "runs",
            lesson_plan_collateral_intent_path=wrapper_path,
        )

    assert plan_calls == [wrapper_path]
    assert intent_calls == []
