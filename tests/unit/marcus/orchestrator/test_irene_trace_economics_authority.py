"""Regression pins for Irene's single durable economics authority."""

from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

import app.runtime.economics as economics
from app.marcus.orchestrator.production_runner import _trace_run_for_contribution
from app.models.runtime.production_envelope import SpecialistContribution
from app.runtime.economics import _reconcile_pass1_provider_attempts, measure_trial_cost


def _contribution(specialist_id: str, *, node_id: str) -> SpecialistContribution:
    return SpecialistContribution.from_output(
        specialist_id=specialist_id,
        node_id=node_id,
        output={},
        model_used="gpt-5.4",
    )


def test_irene_pass1_contributions_mint_only_nonbillable_execution_markers(
    tmp_path: Path,
) -> None:
    trial_id = uuid4()
    contributions = [
        _contribution("irene_pass1", node_id="04A"),
        _contribution("irene_pass1", node_id="05"),
        _contribution("irene_pass1", node_id="05B"),
        _contribution("gary", node_id="07"),
    ]

    projected = [
        _trace_run_for_contribution(
            trial_id=trial_id,
            contribution=contribution,
        )
        for contribution in contributions
    ]

    assert [trace.total_tokens for trace in projected] == [0, 0, 0, 35]
    report = measure_trial_cost(str(trial_id), trace_runs=projected, history=[])
    assert "irene_pass1" not in report.per_agent_breakdown
    assert len(report._trace_provider_attempts) == 1
    assert report._trace_provider_attempts[0]["agent_name"] == "gary"
    assert report._irene_execution_nodes == ("04A", "05", "05B")

    with pytest.raises(RuntimeError, match="without durable journals"):
        _reconcile_pass1_provider_attempts(
            report,
            trial_id=str(trial_id),
            runs_root=tmp_path,
        )


def test_partial_irene_journal_loss_fails_closed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    trial_id = uuid4()
    projected = [
        _trace_run_for_contribution(
            trial_id=trial_id,
            contribution=_contribution("irene_pass1", node_id=node_id),
        )
        for node_id in ("04A", "05", "05B")
    ]
    projected.append(
        _trace_run_for_contribution(
            trial_id=trial_id,
            contribution=_contribution("gary", node_id="07"),
        )
    )
    report = measure_trial_cost(str(trial_id), trace_runs=projected, history=[])
    run_dir = tmp_path / str(trial_id)
    run_dir.mkdir()
    (run_dir / "irene-pass1-call-04A.v1.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(
        economics,
        "_load_pass1_provider_attempts",
        lambda **_: [{"node_id": "04A"}],
    )

    with pytest.raises(RuntimeError, match="lack durable journals for nodes: 05, 05B"):
        _reconcile_pass1_provider_attempts(
            report,
            trial_id=str(trial_id),
            runs_root=tmp_path,
        )
