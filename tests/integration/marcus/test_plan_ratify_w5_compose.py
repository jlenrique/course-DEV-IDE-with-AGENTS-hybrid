"""W5 liveproof: plan-ratify → selection delta → compose_and_digest → trial start.

Operator-required compose liveproof for marcus-planning-ratification-surface.
No Gamma spend — local compose on the changed selection only.

Baseline default is narrated-deck-with-motion; this suite ratifies narrated-deck
so selection delta is forced.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.marcus.cli.plan_ratify_cli import main as plan_ratify_main
from app.marcus.cli.trial import start_trial
from app.marcus.lesson_plan.composition import compose_and_digest
from app.marcus.lesson_plan.planning_ratification import (
    compute_selection_delta,
    default_baseline_selection,
    resolve_intent_file,
    write_selection_delta,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
TEJAL = (
    REPO_ROOT
    / "course-content"
    / "courses"
    / "tejal-c1m1-p4-assessments-bridge"
)
FIXTURE_INPUT = Path("tests/fixtures/trial_corpus/README.md")


def _ratify_lighter_deck(output_dir: Path) -> Path:
    """Ratify narrated-deck (differs from default baseline motion-on)."""
    code = plan_ratify_main(
        [
            "--purpose",
            "Ship deck only while waiting on motion assets",
            "--audience",
            "APC C1 learners",
            "--workflow",
            "narrated-deck",
            "--gap-fill-chosen",
            "lighter_collateral",
            "--gap-fill-considered",
            "lighter_collateral,wait,synthesize",
            "--gap-fill-rationale",
            "Defer motion; ship narrated deck now",
            "--output-dir",
            str(output_dir),
            "--corpus-dir",
            str(TEJAL),
        ]
    )
    assert code == 0
    return output_dir / "ratified-collateral-intent.yaml"


def test_w5_compose_and_digest_on_ratified_selection(tmp_path: Path) -> None:
    intent = _ratify_lighter_deck(tmp_path)
    resolved = resolve_intent_file(intent)
    assert resolved.source == "ratified"
    assert resolved.bundle_id == "narrated-deck"
    digest = compose_and_digest(resolved.selection, repo_root=REPO_ROOT)
    assert digest.composed_graph_digest
    assert digest.input_closure_digest
    assert digest.composed_node_ids
    assert digest.component_selection == {
        "deck": True,
        "motion": False,
        "workbook": False,
    }


def test_w5_selection_delta_vs_baseline(tmp_path: Path) -> None:
    intent = _ratify_lighter_deck(tmp_path)
    after = resolve_intent_file(intent)
    before = default_baseline_selection()
    delta = compute_selection_delta(before=before, after=after)
    assert delta.changed
    assert before.selection != after.selection
    write_selection_delta(delta, tmp_path / "selection-delta.json")
    assert (tmp_path / "selection-delta.json").is_file()


def test_w5_trial_start_threads_selection_into_component_selection(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AC-M8: trial start consumes ratified intent (spy — no full walk)."""
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.delenv("LANGSMITH_PROJECT", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr("app.marcus.cli.trial._load_env_if_available", lambda: None)
    captured: dict[str, object] = {}

    def _spy(**kwargs: object) -> None:
        captured.update(kwargs)
        raise RuntimeError("stop-after-capture")

    monkeypatch.setattr("app.marcus.cli.trial.run_production_trial", _spy)

    intent = _ratify_lighter_deck(tmp_path / "ratify")
    resolved = resolve_intent_file(intent)
    digest = compose_and_digest(resolved.selection, repo_root=REPO_ROOT)
    assert digest.composed_graph_digest
    assert digest.component_selection == resolved.selection.as_map()

    with pytest.raises(RuntimeError, match="stop-after-capture"):
        start_trial(
            preset="production",
            input_path=FIXTURE_INPUT,
            operator_id="operator_w5_plan_ratify",
            allow_offline_cost_report=True,
            runs_root=tmp_path / "runs",
            lesson_plan_collateral_intent_path=intent,
        )

    selection = captured["component_selection"]
    assert selection is not None
    assert selection.as_map() == {"deck": True, "motion": False, "workbook": False}
