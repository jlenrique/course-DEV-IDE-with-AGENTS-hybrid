from __future__ import annotations

import json
from pathlib import Path

from app.marcus.orchestrator.gate_runner import (
    CALIBRATION_TRIPWIRE_LOG,
    ENGAGEMENT_DECAY_REPORT,
    emit_engagement_decay_report,
)


def test_engagement_decay_report_passes_at_sm4_threshold(tmp_path: Path) -> None:
    result = emit_engagement_decay_report(
        trial_id="trial-2",
        first_quartile_events=10,
        last_quartile_events=3,
        artifact_dir=tmp_path,
    )

    report = (tmp_path / ENGAGEMENT_DECAY_REPORT).read_text(encoding="utf-8")
    assert result["passed"] is True
    assert "- status: PASS" in report
    assert "- last_to_first_ratio: 0.3000" in report
    assert not (tmp_path / CALIBRATION_TRIPWIRE_LOG).exists()


def test_engagement_decay_breach_triggers_c1_tripwire(tmp_path: Path) -> None:
    result = emit_engagement_decay_report(
        trial_id="trial-2",
        first_quartile_events=10,
        last_quartile_events=2,
        artifact_dir=tmp_path,
    )

    events = [
        json.loads(line)
        for line in (tmp_path / CALIBRATION_TRIPWIRE_LOG)
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    assert result["passed"] is False
    assert result["tripwire_event"]["gate_id"] == "C1"
    assert events[-1]["fired"] is True
