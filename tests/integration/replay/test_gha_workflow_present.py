from __future__ import annotations

from pathlib import Path


def test_trial_replay_workflow_exists_and_invokes_fail_loud_mode() -> None:
    workflow_path = Path(".github/workflows/trial-replay.yml")
    assert workflow_path.is_file()

    text = workflow_path.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "schedule:" in text
    assert "app.replay.regression --mode fail-loud" in text
