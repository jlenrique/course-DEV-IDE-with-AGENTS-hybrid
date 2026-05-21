"""Shared gate-runner guardrails for Slab 7a closeout."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_ARTIFACT_DIR = Path("_artifacts") / "current-trial"

# Backward-compat alias for any external caller still referencing the
# Trial-2-bound name. Removed at S6 P3 housekeeping.
DEFAULT_TRIAL_2_ARTIFACT_DIR = DEFAULT_ARTIFACT_DIR
CALIBRATION_TRIPWIRE_LOG = "calibration_tripwire_log.jsonl"
ENGAGEMENT_DECAY_REPORT = "engagement_decay_report.md"


class MarcusDualityBoundaryError(RuntimeError):
    """Raised when Marcus orchestration and operator-handoff state are mixed."""


@dataclass(frozen=True)
class CalibrationTripwireConfig:
    """Configuration for operator-override-rate calibration checks."""

    window_size: int = 5
    override_rate_threshold: float = 0.50
    disagreement_axis_threshold: int = 3
    auto_lock_trials: int = 3


DEFAULT_CALIBRATION_TRIPWIRE_CONFIG = CalibrationTripwireConfig()


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _artifact_dir(root: Path | None) -> Path:
    return root if root is not None else DEFAULT_ARTIFACT_DIR


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(payload, sort_keys=True) + "\n")


def evaluate_calibration_tripwire(
    *,
    gate_id: str,
    trial_id: str,
    operator_override_history: list[bool],
    disagreement_axes: int = 0,
    artifact_dir: Path | None = None,
    config: CalibrationTripwireConfig | None = None,
) -> dict[str, Any]:
    """Evaluate and log a calibration-tripwire fire or witnessed quiet event."""

    config = config or DEFAULT_CALIBRATION_TRIPWIRE_CONFIG
    if config.window_size < 1:
        raise ValueError("window_size must be at least 1")
    window = operator_override_history[-config.window_size :]
    override_rate = (sum(1 for item in window if item) / len(window)) if window else 0.0
    rate_fired = override_rate > config.override_rate_threshold
    disagreement_fired = disagreement_axes >= config.disagreement_axis_threshold
    fired = rate_fired or disagreement_fired
    event = {
        "event": "calibration_tripwire",
        "trial_id": trial_id,
        "gate_id": gate_id,
        "checked_at": _now_iso(),
        "window_size": config.window_size,
        "observed_window_size": len(window),
        "operator_override_rate": round(override_rate, 4),
        "override_rate_threshold": config.override_rate_threshold,
        "disagreement_axes": disagreement_axes,
        "disagreement_axis_threshold": config.disagreement_axis_threshold,
        "fired": fired,
        "quiet_witnessed": not fired,
    }
    if fired:
        reasons: list[str] = []
        if rate_fired:
            reasons.append("operator_override_rate")
        if disagreement_fired:
            reasons.append("synthetic_disagreement_axes")
        event.update(
            {
                "reason": "+".join(reasons),
                "auto_lock": {
                    "gate_id": gate_id,
                    "remaining_trials": config.auto_lock_trials,
                    "batch_approve_locked": True,
                },
            }
        )
    else:
        event.update({"armed_check": "passed", "auto_lock": None})
    log_path = _artifact_dir(artifact_dir) / CALIBRATION_TRIPWIRE_LOG
    _append_jsonl(log_path, event)
    event["log_path"] = log_path.as_posix()
    return event


def emit_engagement_decay_report(
    *,
    trial_id: str,
    first_quartile_events: int,
    last_quartile_events: int,
    artifact_dir: Path | None = None,
    gate_id: str = "C1",
    minimum_last_to_first_ratio: float = 0.30,
) -> dict[str, Any]:
    """Write the trial engagement-decay report and fire C1 on SM-4 breach."""

    if first_quartile_events < 0 or last_quartile_events < 0:
        raise ValueError("quartile event counts must be non-negative")
    ratio = (
        last_quartile_events / first_quartile_events
        if first_quartile_events
        else 1.0
    )
    passed = ratio >= minimum_last_to_first_ratio
    root = _artifact_dir(artifact_dir)
    root.mkdir(parents=True, exist_ok=True)
    report_path = root / ENGAGEMENT_DECAY_REPORT
    status = "PASS" if passed else "FAIL"
    report_path.write_text(
        "\n".join(
            [
                f"# Engagement Decay Report - {trial_id}",
                "",
                f"- first_quartile_events: {first_quartile_events}",
                f"- last_quartile_events: {last_quartile_events}",
                f"- last_to_first_ratio: {ratio:.4f}",
                f"- minimum_ratio: {minimum_last_to_first_ratio:.4f}",
                f"- status: {status}",
                "",
            ]
        ),
        encoding="utf-8",
        newline="\n",
    )
    tripwire_event = None
    if not passed:
        tripwire_event = evaluate_calibration_tripwire(
            gate_id=gate_id,
            trial_id=trial_id,
            operator_override_history=[True],
            disagreement_axes=CalibrationTripwireConfig().disagreement_axis_threshold,
            artifact_dir=root,
        )
    return {
        "trial_id": trial_id,
        "report_path": report_path.as_posix(),
        "first_quartile_events": first_quartile_events,
        "last_quartile_events": last_quartile_events,
        "last_to_first_ratio": ratio,
        "passed": passed,
        "tripwire_event": tripwire_event,
    }


def assert_marcus_duality_boundary(
    *,
    orchestrator_mode_state: Any | None,
    operator_handoff_state: Any | None,
) -> None:
    """Fail when one transition tries to carry both Marcus state modes."""

    if orchestrator_mode_state is not None and operator_handoff_state is not None:
        raise MarcusDualityBoundaryError(
            "Marcus orchestrator-mode state must not mix with operator-handoff state"
        )


def assert_payload_duality_boundary(payload: dict[str, Any]) -> None:
    """Runtime payload assertion used by dispatch adapters."""

    assert_marcus_duality_boundary(
        orchestrator_mode_state=payload.get("orchestrator_mode_state"),
        operator_handoff_state=payload.get("operator_handoff_state"),
    )


__all__ = [
    "CALIBRATION_TRIPWIRE_LOG",
    "DEFAULT_ARTIFACT_DIR",
    "DEFAULT_TRIAL_2_ARTIFACT_DIR",  # backward-compat alias; removed at S6
    "ENGAGEMENT_DECAY_REPORT",
    "CalibrationTripwireConfig",
    "DEFAULT_CALIBRATION_TRIPWIRE_CONFIG",
    "MarcusDualityBoundaryError",
    "assert_marcus_duality_boundary",
    "assert_payload_duality_boundary",
    "emit_engagement_decay_report",
    "evaluate_calibration_tripwire",
]
