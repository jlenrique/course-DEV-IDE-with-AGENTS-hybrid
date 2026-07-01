"""Pins for the Descript publication-receipt fail-loud verify gate.

THE GAP (scout-verified): the old verify step in
``scripts/operator/build_descript_narrated_lesson.py`` only PRINTED
``c.get('duration')`` for each composition — no assertion. Server-side
Underlord assembly DETACHES, so a premature ``get_project`` read returns a
composition with duration 0 (or None). A run could therefore look "done"
while the composition was not durably assembled, and the published-receipt
was hand-authored rather than asserted by code.

These pins lock the pure helper ``build_publication_receipt``:

- duration 0 (the detachment case) MUST raise — this is the kill shot.
- duration None (read before assembly populated it) MUST raise.
- a duration far from the expected audio total MUST raise, and the message
  MUST name actual vs expected so the operator can see the mismatch.
- a duration within tolerance of the expected audio total returns the
  receipt with ``published=True`` and ``duration_within_1s=True``.

NO live Descript: the helper is pure and unit-testable in isolation.
"""

from __future__ import annotations

import pytest

from scripts.operator.descript_publication_receipt import (
    DescriptPublicationError,
    build_publication_receipt,
)

PROJECT_ID = "d4c69938-751c-458f-be93-036874eaa81b"
COMPOSITION_ID = "e4a0d038-f16a-424b-a39c-51ea62b1ba75"
EXPECTED_AUDIO_TOTAL_S = 486.034


def test_duration_zero_raises_detachment_case() -> None:
    """duration 0 = Underlord assembly detached mid-flight -> fail loud."""
    with pytest.raises(DescriptPublicationError):
        build_publication_receipt(
            project_id=PROJECT_ID,
            composition_id=COMPOSITION_ID,
            composition_duration_s=0,
            expected_audio_total_s=EXPECTED_AUDIO_TOTAL_S,
        )


def test_duration_none_raises() -> None:
    """duration None = read before assembly populated it -> fail loud."""
    with pytest.raises(DescriptPublicationError):
        build_publication_receipt(
            project_id=PROJECT_ID,
            composition_id=COMPOSITION_ID,
            composition_duration_s=None,
            expected_audio_total_s=EXPECTED_AUDIO_TOTAL_S,
        )


def test_duration_far_from_expected_raises_with_named_values() -> None:
    """A composition 100s long vs 486s expected is not the lesson -> fail loud.

    The error message must name the actual vs expected so the mismatch is
    diagnosable from the log alone.
    """
    with pytest.raises(DescriptPublicationError) as exc_info:
        build_publication_receipt(
            project_id=PROJECT_ID,
            composition_id=COMPOSITION_ID,
            composition_duration_s=100.0,
            expected_audio_total_s=EXPECTED_AUDIO_TOTAL_S,
        )
    msg = str(exc_info.value)
    assert "100" in msg
    assert "486" in msg


def test_duration_within_tolerance_returns_receipt() -> None:
    """486.0247 vs 486.034 (delta ~0.009s) passes and returns the receipt."""
    receipt = build_publication_receipt(
        project_id=PROJECT_ID,
        composition_id=COMPOSITION_ID,
        composition_duration_s=486.024693,
        expected_audio_total_s=EXPECTED_AUDIO_TOTAL_S,
    )
    assert receipt["published"] is True
    assert receipt["published_attestation"] is True
    assert receipt["duration_within_1s"] is True
    assert receipt["project_id"] == PROJECT_ID
    assert receipt["composition_id"] == COMPOSITION_ID
    assert receipt["composition_duration_s"] == pytest.approx(486.024693)
    assert receipt["expected_audio_total_s"] == pytest.approx(486.034)
    assert receipt["duration_delta_s"] == pytest.approx(-0.009307, abs=1e-4)


def test_attested_at_utc_passthrough_is_deterministic() -> None:
    """The pure helper does not read a wall clock; the caller supplies the stamp."""
    receipt = build_publication_receipt(
        project_id=PROJECT_ID,
        composition_id=COMPOSITION_ID,
        composition_duration_s=486.024693,
        expected_audio_total_s=EXPECTED_AUDIO_TOTAL_S,
        attested_at_utc="2026-06-30T00:00:00Z",
    )
    assert receipt["attested_at_utc"] == "2026-06-30T00:00:00Z"

    # Omitted -> field absent (no nondeterministic wall-clock leak).
    receipt2 = build_publication_receipt(
        project_id=PROJECT_ID,
        composition_id=COMPOSITION_ID,
        composition_duration_s=486.024693,
        expected_audio_total_s=EXPECTED_AUDIO_TOTAL_S,
    )
    assert "attested_at_utc" not in receipt2


def test_tolerance_boundary_just_outside_raises() -> None:
    """A delta strictly greater than tolerance_s raises (boundary is exclusive)."""
    with pytest.raises(DescriptPublicationError):
        build_publication_receipt(
            project_id=PROJECT_ID,
            composition_id=COMPOSITION_ID,
            composition_duration_s=EXPECTED_AUDIO_TOTAL_S + 1.5,
            expected_audio_total_s=EXPECTED_AUDIO_TOTAL_S,
            tolerance_s=1.0,
        )
