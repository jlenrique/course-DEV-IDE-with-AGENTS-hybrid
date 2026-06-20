from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.specialists.vision.repeatability import (
    REPEATABILITY_THRESHOLDS,
    compare_artifacts,
)

FIXTURES = Path(__file__).resolve().parents[2] / "fixtures" / "perception" / "golden"


def _load(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.mark.quarantined
def test_golden_artifact_repeatability_held_out_equivalent_fixture_is_stable() -> None:
    verdict = compare_artifacts(
        _load("slide-01-provider-response.json"),
        _load("slide-01-provider-response-equivalent.json"),
    )

    assert verdict.stable is True
    assert verdict.reasons == []
    assert verdict.thresholds == REPEATABILITY_THRESHOLDS


@pytest.mark.parametrize(
    ("fixture", "reason_prefix", "threshold_key", "relaxed_value"),
    [
        (
            "slide-01-provider-response-bbox-negative.json",
            "bbox_iou",
            "bbox_iou_min",
            0.0,
        ),
        (
            "slide-01-provider-response-element-negative.json",
            "element_jaccard",
            "element_jaccard_min",
            0.0,
        ),
        (
            "slide-01-provider-response-text-negative.json",
            "text_edit_distance",
            "text_edit_distance_max",
            10000.0,
        ),
    ],
)
@pytest.mark.quarantined
def test_each_repeatability_threshold_is_load_bearing(
    monkeypatch: pytest.MonkeyPatch,
    fixture: str,
    reason_prefix: str,
    threshold_key: str,
    relaxed_value: float,
) -> None:
    reference = _load("slide-01-provider-response.json")
    candidate = _load(fixture)

    strict_verdict = compare_artifacts(reference, candidate)

    assert strict_verdict.stable is False
    assert len(strict_verdict.reasons) == 1
    assert strict_verdict.reasons[0].startswith(reason_prefix)

    monkeypatch.setitem(REPEATABILITY_THRESHOLDS, threshold_key, relaxed_value)
    relaxed_verdict = compare_artifacts(reference, candidate)

    assert relaxed_verdict.stable is True
    assert relaxed_verdict.reasons == []


@pytest.mark.quarantined
def test_legacy_aggregate_negative_control_still_fails() -> None:
    verdict = compare_artifacts(
        _load("slide-01-provider-response.json"),
        _load("slide-01-provider-response-perturbed.json"),
    )

    assert verdict.stable is False
    assert any(reason.startswith("element_jaccard") for reason in verdict.reasons)
