from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.specialists.vision.repeatability import compare_artifacts

REFERENCE = (
    Path(__file__).resolve().parents[2]
    / "fixtures"
    / "perception"
    / "golden"
    / "slide-01-provider-response.json"
)
CANDIDATE = REFERENCE.with_name("slide-01-provider-response-equivalent.json")


@pytest.mark.live
def test_silent_drift_canary_fixture_pair_is_clean() -> None:
    reference = json.loads(REFERENCE.read_text(encoding="utf-8"))
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))

    verdict = compare_artifacts(reference, candidate)

    assert verdict.stable is True
    assert verdict.reasons == []
