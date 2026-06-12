"""Deterministic node markers are non-billable (audio-arc, 2026-06-12).

Cycle-5's full composition walk (through §15) completed in memory and was
LOST at the completion-path cost recording: the compositor's
``deterministic-compositor-v0`` marker reached ``compute_cost`` and
KeyError'd because pricing has no row for non-LLM nodes — by design.
"""

from __future__ import annotations

from types import SimpleNamespace

from app.runtime.economics import measure_trial_cost


def _run(model: str, agent: str) -> SimpleNamespace:
    return SimpleNamespace(
        name=agent,
        run_type="llm",
        extra={"metadata": {"model_id": model, "agent_name": agent}},
        inputs={},
        outputs={},
        input_tokens=10,
        output_tokens=5,
        total_tokens=15,
        child_runs=[],
        trace_id="t-1",
        id="r-1",
        app_path=None,
    )


def test_deterministic_markers_are_skipped_not_priced() -> None:
    report = measure_trial_cost(
        "trial-deterministic-test",
        trace_runs=[
            _run("gpt-5-nano", "texas"),
            _run("deterministic-compositor-v0", "compositor"),
            _run("deterministic-package-builder", "package_builder"),
        ],
        history=[],
    )
    assert set(report.per_model_breakdown) == {"gpt-5-nano"}
    assert all("compositor" not in name for name in report.per_agent_breakdown)
