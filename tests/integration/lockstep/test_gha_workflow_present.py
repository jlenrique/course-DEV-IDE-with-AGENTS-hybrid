from __future__ import annotations

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
WORKFLOW = ROOT / ".github" / "workflows" / "manifest-lockstep.yml"


def test_gha_workflow_present() -> None:
    assert WORKFLOW.exists()
    data = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    trigger = data.get("on", data.get(True, {}))
    assert "pull_request" in trigger
    run_steps = [
        step.get("run", "")
        for step in data["jobs"]["check"]["steps"]
        if isinstance(step, dict)
    ]
    assert any("python -c" in step for step in run_steps)
    assert any("check_manifest_lockstep" in step for step in run_steps)
