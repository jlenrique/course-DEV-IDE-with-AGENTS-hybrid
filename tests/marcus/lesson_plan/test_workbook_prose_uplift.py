"""Mine 6 — workbook learner-ready prose uplift tests."""

from __future__ import annotations

from app.marcus.lesson_plan.prose_uplift import (
    count_deixis_hits,
    count_revoice_markers,
    measure_prose_delta,
    prose_revoicer_for_sme,
    sme_aware_prose_revoicer,
)
from app.marcus.lesson_plan.workbook_producer import (
    REVOICE_REQUIRED_MARKER,
    default_prose_revoicer,
)

_SAMPLE = (
    "Here you see the 70% clinician burnout figure on the slide. "
    "As you can see, this chart frames the leadership decision."
)


def test_default_vs_sme_revoicer_measurable_delta() -> None:
    before = default_prose_revoicer("seg-1", _SAMPLE)
    revoicer = sme_aware_prose_revoicer("tejal")
    after = revoicer("seg-1", _SAMPLE)
    delta = measure_prose_delta(before, after)
    assert delta.revoice_marker_before >= 1
    assert delta.revoice_marker_after == 0
    assert delta.markers_cleared
    assert delta.deixis_hits_after < delta.deixis_hits_before
    assert "Tejal" in after or "tejal" in after.lower()
    assert REVOICE_REQUIRED_MARKER not in after


def test_sme_voice_honored_diverges_from_hai_gap_profile() -> None:
    tejal = sme_aware_prose_revoicer("tejal")("s1", _SAMPLE)
    hai = sme_aware_prose_revoicer("hai-510")("s1", _SAMPLE)
    assert tejal != hai
    assert "Tejal" in tejal or "tejal-apc" in tejal
    assert "HAI 510" in hai or "hai-510" in hai


def test_uplift_idempotent_second_pass() -> None:
    revoicer = sme_aware_prose_revoicer("tejal")
    first = revoicer("seg-1", _SAMPLE)
    second = revoicer("seg-1", first)
    assert count_revoice_markers(second) == 0
    assert count_deixis_hits(second) <= count_deixis_hits(first)
    assert "Voice profile:" in second
    third = revoicer("seg-1", second)
    assert count_revoice_markers(third) == 0
    assert third.count("Voice profile:") == 1


def test_factory_none_uses_default() -> None:
    revoicer = prose_revoicer_for_sme(None)
    out = revoicer("x", "plain")
    assert REVOICE_REQUIRED_MARKER in out
