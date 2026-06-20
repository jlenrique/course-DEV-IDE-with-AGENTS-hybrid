from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.marcus.orchestrator.production_runner import _RETRYABLE_DISPATCH_TAGS
from app.specialists.quinn_r._act import run_g5_checks
from app.specialists.quinn_r.quality_control_dispatch import FidelityError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "perception" / "golden"


def _artifact() -> dict[str, object]:
    return json.loads((FIXTURES / "slide-01-produced-artifact.json").read_text(encoding="utf-8"))


def _payload(text: str) -> dict[str, object]:
    return {
        "slides": [{"slide_id": "slide-01"}],
        "narration_segments": [
            {
                "slide_id": "slide-01",
                "text": text,
                "duration_seconds": 2.5,
            }
        ],
        "perception_artifacts": [_artifact()],
        "vtt_text": "00:00:00.000 --> 00:00:10.000\ntext",
    }


def test_g5_enforces_perception_by_default() -> None:
    with pytest.raises(FidelityError):
        run_g5_checks(_payload("This slide shows a $5.2T line chart."))


def test_g5_warn_override_records_unclean_annotation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FIDELITY_GATE", "warn")

    verdict = run_g5_checks(_payload("This slide shows a $5.2T line chart."))

    assert verdict["blocking"] == []
    assert verdict["fidelity"]["status"] == "warn"
    assert "OVERRIDDEN by operator" in verdict["fidelity"]["annotation"]
    assert "narration unverified" in verdict["fidelity"]["annotation"]
    assert any(row["reason"] == "fidelity-gate-operator-override" for row in verdict["advisory"])


@pytest.mark.parametrize(
    "perception_artifacts",
    [
        [{"slide_id": "slide-01", "confidence": "HIGH", "coverage": "perceived", "extra": True}],
        [
            {
                "slide_id": "slide-01",
                "confidence": "HIGH",
                "coverage": "perceived",
                "extracted_text": "$5.2T line chart",
            },
            {
                "slide_id": "slide-01",
                "confidence": "HIGH",
                "coverage": "perceived",
                "extracted_text": "$5.2T line chart",
            },
        ],
    ],
)
def test_g5_warn_override_does_not_swallow_structural_artifact_errors(
    monkeypatch: pytest.MonkeyPatch,
    perception_artifacts: list[dict[str, object]],
) -> None:
    monkeypatch.setenv("FIDELITY_GATE", "warn")
    payload = _payload("This slide shows a $5.2T line chart.")
    payload["perception_artifacts"] = perception_artifacts

    with pytest.raises(FidelityError) as exc:
        run_g5_checks(payload)

    assert getattr(exc.value, "scope", None) == "structural"


def test_fidelity_detector_tag_is_not_retryable() -> None:
    assert "quinn_r.g5.fidelity-orphan-reference" not in _RETRYABLE_DISPATCH_TAGS
    assert "quinn_r.g5.fidelity-figure-contradiction" not in _RETRYABLE_DISPATCH_TAGS
