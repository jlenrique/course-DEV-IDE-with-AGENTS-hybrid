from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.specialists.quinn_r.fidelity_detector import detect_fidelity
from app.specialists.quinn_r.quality_control_dispatch import FidelityError

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "perception" / "golden"


def _load(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_ac12_detector_red_on_real_produced_artifact_and_green_on_faithful() -> None:
    produced = _load("slide-01-produced-artifact.json")
    bad_segments = [
        {
            "slide_id": "slide-01",
            "text": "This slide shows a $5.2T line chart with paired bars.",
        }
    ]
    faithful_segments = [
        {
            "slide_id": "slide-01",
            "text": "The building photo sits beside callouts for $4.5T spend, 74%, and 3x growth.",
        }
    ]

    with pytest.raises(FidelityError):
        detect_fidelity(bad_segments, [produced])

    verdict = detect_fidelity(faithful_segments, [produced])
    assert verdict["blocking"] == []
