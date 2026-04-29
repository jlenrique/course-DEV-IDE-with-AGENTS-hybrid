from __future__ import annotations

import json
from pathlib import Path

from app.marcus.orchestrator.gate_runner import (
    CALIBRATION_TRIPWIRE_LOG,
    CalibrationTripwireConfig,
    evaluate_calibration_tripwire,
)


def _events(path: Path) -> list[dict[str, object]]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def test_synthetic_three_axis_disagreement_fires_and_locks(tmp_path: Path) -> None:
    event = evaluate_calibration_tripwire(
        gate_id="G2C",
        trial_id="trial-2",
        operator_override_history=[False, False, False],
        disagreement_axes=3,
        artifact_dir=tmp_path,
    )

    assert event["fired"] is True
    assert event["auto_lock"] == {
        "gate_id": "G2C",
        "remaining_trials": 3,
        "batch_approve_locked": True,
    }
    assert _events(tmp_path / CALIBRATION_TRIPWIRE_LOG)[0]["fired"] is True


def test_consensus_path_stays_quiet_but_is_witnessed(tmp_path: Path) -> None:
    event = evaluate_calibration_tripwire(
        gate_id="G2C",
        trial_id="trial-2",
        operator_override_history=[False, False, False, False, False],
        disagreement_axes=0,
        artifact_dir=tmp_path,
    )

    assert event["fired"] is False
    assert event["quiet_witnessed"] is True
    assert event["armed_check"] == "passed"
    assert _events(tmp_path / CALIBRATION_TRIPWIRE_LOG)[0]["quiet_witnessed"] is True


def test_rolling_override_rate_above_threshold_fires(tmp_path: Path) -> None:
    event = evaluate_calibration_tripwire(
        gate_id="G3",
        trial_id="trial-2",
        operator_override_history=[False, True, True, True],
        artifact_dir=tmp_path,
        config=CalibrationTripwireConfig(window_size=4, override_rate_threshold=0.50),
    )

    assert event["fired"] is True
    assert event["operator_override_rate"] == 0.75
