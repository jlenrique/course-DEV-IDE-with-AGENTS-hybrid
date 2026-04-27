from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import UUID, uuid4

import pytest

from app.marcus.orchestrator.production_runner import (
    resume_production_trial,
    run_production_trial,
)
from app.models.state.operator_verdict import OperatorVerdict


@pytest.mark.live
def test_production_trial_smoke_live_with_gate_resume(tmp_path: Path) -> None:
    if (
        not os.getenv("OPENAI_API_KEY")
        or not os.getenv("LANGSMITH_API_KEY")
        or not os.getenv("LANGSMITH_PROJECT")
    ):
        pytest.skip(
            "OPENAI_API_KEY, LANGSMITH_API_KEY, and LANGSMITH_PROJECT required "
            "for live production smoke"
        )

    trial_id = uuid4()
    paused = run_production_trial(
        Path("tests/fixtures/trial_corpus/README.md"),
        "production",
        "operator_live",
        trial_id=trial_id,
        runs_root=tmp_path,
        max_specialist_calls=1,
        pause_at_gates=True,
    )
    assert paused.status == "paused-at-gate"
    assert paused.paused_gate == "G1"

    decision = json.loads(
        (tmp_path / str(trial_id) / "decision-card-G1.json").read_text(
            encoding="utf-8"
        )
    )
    verdict = OperatorVerdict(
        trial_id=trial_id,
        verb="approve",
        gate_id="G1",
        card_id=UUID(decision["card"]["card_id"]),
        operator_id="operator_live",
        decision_card_digest=decision["digest"],
    )

    envelope = resume_production_trial(
        trial_id=trial_id,
        verdict=verdict,
        runs_root=tmp_path,
        max_specialist_calls=1,
    )

    assert envelope.status == "completed"
    assert envelope.production_clone_launch_evidence is True
    assert envelope.production_envelope.get_contribution("texas") is not None
    assert envelope.production_envelope.get_contribution("irene") is not None
    assert envelope.cost_report_path is not None
    assert envelope.cost_report_path.exists()
