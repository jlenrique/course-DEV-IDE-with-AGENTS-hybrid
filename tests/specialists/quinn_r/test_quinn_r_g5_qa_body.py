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
        "perception_artifacts": [
            {
                "artifact_path": "fixtures/s1.png",
                "card_number": 1,
                "confidence": "HIGH",
                "coverage": "perceived",
                "extracted_text": "Fixture text one.",
                "layout_description": "Fixture slide one.",
                "slide_id": "s1",
                "slide_title": "Slide one",
                "text_blocks": [{"text": "Fixture text one"}],
                "visual_elements": [{"kind": "title", "label": "slide one"}],
            },
            {
                "artifact_path": "fixtures/s2.png",
                "card_number": 2,
                "confidence": "HIGH",
                "coverage": "perceived",
                "extracted_text": "Fixture text two.",
                "layout_description": "Fixture slide two.",
                "slide_id": "s2",
                "slide_title": "Slide two",
                "text_blocks": [{"text": "Fixture text two"}],
                "visual_elements": [{"kind": "title", "label": "slide two"}],
            },
        ],
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


def _words(count: int) -> str:
    return " ".join(f"word{i}" for i in range(count))


def _set_total_duration(payload: dict, total_seconds: float) -> None:
    per_segment = total_seconds / len(payload["narration_segments"])
    for segment in payload["narration_segments"]:
        segment["duration_seconds"] = per_segment
        segment["motion_duration_seconds"] = per_segment


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
        _set_total_duration(payload, 5)
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


def test_g5_slow_but_intelligible_voice_passes() -> None:
    payload = _payload()
    for segment in payload["narration_segments"]:
        segment["text"] = _words(16)
    _set_total_duration(payload, 15)

    verdict = run_g5_checks(payload)

    assert verdict["blocking"] == []
    assert verdict["advisory"] == []


def test_g5_runaway_fast_trips_ceiling() -> None:
    payload = _payload()
    _set_total_duration(payload, 5)

    with pytest.raises(WpmThresholdError, match="above intelligibility ceiling 200"):
        run_g5_checks(payload)


def test_g5_broken_slow_trips_floor() -> None:
    payload = _payload()
    _set_total_duration(payload, 12)

    with pytest.raises(WpmThresholdError, match="below intelligibility floor 110"):
        run_g5_checks(payload)


def test_g5_operator_break_glass_downgrades_breach() -> None:
    payload = _payload()
    payload["wpm_breach_override"] = True
    _set_total_duration(payload, 5)

    verdict = run_g5_checks(payload)

    assert verdict["blocking"] == []
    assert {
        "reason": "wpm-breach-operator-override",
        "observed_wpm": 240.0,
        "floor": 110.0,
        "ceiling": 200.0,
    } in verdict["advisory"]


# --- Boundary pins (party-mode T11, Murat+Amelia): the band is INCLUSIVE at both
# edges; just-outside raises. Together these kill the `<`/`<=` (and `>`/`>=`) mutant. ---


def test_g5_floor_edge_is_inclusive_passes() -> None:
    payload = _payload()
    for segment in payload["narration_segments"]:
        segment["text"] = _words(11)  # 22 words total
    _set_total_duration(payload, 12)  # 22/12*60 == 110.0 exactly == FLOOR

    verdict = run_g5_checks(payload)

    assert verdict["blocking"] == []
    assert verdict["advisory"] == []


def test_g5_ceiling_edge_is_inclusive_passes() -> None:
    payload = _payload()
    for segment in payload["narration_segments"]:
        segment["text"] = _words(10)  # 20 words total
    _set_total_duration(payload, 6)  # 20/6*60 == 200.0 exactly == CEILING

    verdict = run_g5_checks(payload)

    assert verdict["blocking"] == []
    assert verdict["advisory"] == []


def test_g5_just_below_floor_raises() -> None:
    payload = _payload()
    for segment in payload["narration_segments"]:
        segment["text"] = _words(9)  # 18 words total
    _set_total_duration(payload, 10)  # 18/10*60 == 108.0, just below 110

    with pytest.raises(WpmThresholdError, match="below intelligibility floor 110"):
        run_g5_checks(payload)


def test_g5_just_above_ceiling_raises() -> None:
    payload = _payload()
    for segment in payload["narration_segments"]:
        segment["text"] = _words(17)  # 34 words total
    _set_total_duration(payload, 10)  # 34/10*60 == 204.0, just above 200

    with pytest.raises(WpmThresholdError, match="above intelligibility ceiling 200"):
        run_g5_checks(payload)


def test_g5_absent_perception_is_dormant_unverified_not_a_fail() -> None:
    # P2-1 Edge-1 ratified posture: with no perception_artifacts the fidelity
    # detector is dormant (UNVERIFIED), NOT a Class-A fail — the run still passes
    # G5 mechanics-only (trials remain runnable until P2-2 wires perception).
    payload = _payload()
    payload.pop("perception_artifacts", None)

    verdict = run_g5_checks(payload)

    assert verdict["blocking"] == []
    assert verdict["fidelity"]["status"] == "unverified"
    assert verdict["fidelity"]["reason"] == "perception-not-wired"


def test_g5_estimated_durations_suppress_breach_to_advisory() -> None:
    # A real out-of-band breach WITH estimated durations must NOT raise (the
    # existing self-referential escape, preserved verbatim) — kills the
    # dropped-escape mutant.
    payload = _payload()
    payload["wpm_durations_estimated"] = True
    _set_total_duration(payload, 5)  # 240 WPM — would raise the ceiling if measured

    verdict = run_g5_checks(payload)

    assert verdict["blocking"] == []
    assert verdict["advisory"] == []
