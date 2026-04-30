from __future__ import annotations

import pytest

from app.specialists.quinn_r.graph import (
    CoverageGapError,
    VttMonotonicityError,
    WpmThresholdError,
    run_g5_checks,
)


def _payload() -> dict:
    return {
        "slides": [{"slide_id": "s1"}, {"slide_id": "s2"}],
        "narration_profile_controls": {"target_wpm": 120},
        "vtt_text": (
            "WEBVTT\n\n00:00:00.000 --> 00:00:05.000\none\n\n"
            "00:00:05.100 --> 00:00:10.000\ntwo\n"
        ),
        "narration_segments": [
            {
                "slide_id": "s1",
                "text": "one two three four five six seven eight nine ten",
                "duration_seconds": 5,
                "motion_duration_seconds": 5,
            },
            {
                "slide_id": "s2",
                "text": "one two three four five six seven eight nine ten",
                "duration_seconds": 5,
                "motion_duration_seconds": 5.4,
            },
        ],
    }


def test_g5_happy_path_returns_advisory_blocking_partition() -> None:
    verdict = run_g5_checks(_payload())
    assert verdict["blocking"] == []
    assert verdict["advisory"] == []


@pytest.mark.parametrize(
    ("mutation", "error"),
    [
        ("wpm", WpmThresholdError),
        ("vtt", VttMonotonicityError),
        ("coverage", CoverageGapError),
    ],
)
def test_g5_blocking_failures_raise(mutation: str, error: type[Exception]) -> None:
    payload = _payload()
    if mutation == "wpm":
        payload["narration_profile_controls"]["target_wpm"] = 60
    elif mutation == "vtt":
        payload["vtt_text"] = (
            "WEBVTT\n\n00:00:02.000 --> 00:00:03.000\none\n\n"
            "00:00:01.000 --> 00:00:04.000\ntwo\n"
        )
    else:
        payload["narration_segments"] = payload["narration_segments"][:1]
    with pytest.raises(error):
        run_g5_checks(payload)


def test_g5_duration_mismatch_is_advisory() -> None:
    payload = _payload()
    payload["narration_segments"][1]["motion_duration_seconds"] = 8
    verdict = run_g5_checks(payload)
    assert verdict["advisory"] == [{"slide_id": "s2", "reason": "duration-coherence"}]
