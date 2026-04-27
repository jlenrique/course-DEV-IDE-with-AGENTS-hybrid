from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

import pytest

from app.marcus.orchestrator.production_runner import run_production_trial


@pytest.mark.live
def test_production_trial_smoke_live(tmp_path: Path) -> None:
    if not os.getenv("OPENAI_API_KEY") or not os.getenv("LANGSMITH_API_KEY"):
        pytest.skip("OPENAI_API_KEY and LANGSMITH_API_KEY required for live production smoke")

    envelope = run_production_trial(
        Path("tests/fixtures/trial_corpus/README.md"),
        "production",
        "operator_live",
        trial_id=uuid4(),
        runs_root=tmp_path,
        max_specialist_calls=2,
        pause_at_gates=False,
    )

    assert envelope.status in {"paused-at-gate", "completed"}
    assert envelope.production_clone_launch_evidence is True
    assert envelope.production_envelope is not None
    assert envelope.production_envelope.get_contribution("texas") is not None
    assert envelope.production_envelope.get_contribution("irene") is not None
    assert envelope.cost_report_path is not None
    assert envelope.cost_report_path.exists()
    trace_path = tmp_path / str(envelope.trial_id) / "trace-fixture.json"
    assert trace_path.exists()
    assert "texas" in trace_path.read_text(encoding="utf-8")
