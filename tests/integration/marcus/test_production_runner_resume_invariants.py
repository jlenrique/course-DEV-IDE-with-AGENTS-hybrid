from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4

from app.marcus.orchestrator import production_runner
from tests.integration.marcus.test_production_runner_resume_continues_execution import (
    CORPUS,
    _manifest,
    _RecordingAdapter,
    _verdict,
)


def test_contributions_persist_across_pause_resume(
    tmp_path: Path,
    monkeypatch,
) -> None:
    paused_adapter = _RecordingAdapter()
    monkeypatch.setattr(
        production_runner,
        "ProductionDispatchAdapter",
        lambda: paused_adapter,
    )
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    trial_id = uuid4()
    manifest_path = _manifest(tmp_path / "manifest.yaml", gate_id="G1")
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=manifest_path,
        max_specialist_calls=1,
    )

    resumed = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=_verdict(tmp_path, trial_id=trial_id, gate_id="G1", verb="approve"),
        runs_root=tmp_path,
        max_specialist_calls=1,
    )

    direct_trial_id = uuid4()
    direct = production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=direct_trial_id,
        runs_root=tmp_path,
        manifest_path=manifest_path,
        max_specialist_calls=2,
        pause_at_gates=False,
    )

    assert [
        item.specialist_id for item in resumed.production_envelope.contributions
    ] == [item.specialist_id for item in direct.production_envelope.contributions]
    assert [item["specialist_id"] for item in paused_adapter.calls[:2]] == [
        "texas",
        "irene",
    ]


def test_trace_metadata_stays_linked_to_same_trial_id_across_resume(
    tmp_path: Path,
    monkeypatch,
) -> None:
    adapter = _RecordingAdapter()
    monkeypatch.setattr(production_runner, "ProductionDispatchAdapter", lambda: adapter)
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGSMITH_API_KEY", "ls-test")
    monkeypatch.setenv("LANGSMITH_PROJECT", "test-project")
    trial_id = uuid4()
    production_runner.run_production_trial(
        CORPUS,
        "production",
        "operator_test",
        trial_id=trial_id,
        runs_root=tmp_path,
        manifest_path=_manifest(tmp_path / "manifest-trace.yaml", gate_id="G1"),
        max_specialist_calls=1,
    )

    envelope = production_runner.resume_production_trial(
        trial_id=trial_id,
        verdict=_verdict(tmp_path, trial_id=trial_id, gate_id="G1", verb="approve"),
        runs_root=tmp_path,
        max_specialist_calls=1,
    )

    trace = json.loads((tmp_path / str(trial_id) / "trace-fixture.json").read_text())
    assert envelope.langsmith_trace_id == str(trial_id)
    assert trace["root"]["trace_id"] == str(trial_id)
    assert trace["root"]["extra"]["metadata"]["trial_id"] == str(trial_id)
    assert [
        child["extra"]["metadata"]["specialist_id"]
        for child in trace["root"]["child_runs"]
    ] == ["texas", "irene"]
