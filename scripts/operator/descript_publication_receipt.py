"""Fail-loud Descript publication-receipt helper.

Why this exists: server-side Underlord assembly DETACHES. A premature
``get_project`` read returns a composition whose ``duration`` is 0 (or None,
before the field is populated). The old verify step only PRINTED the duration
and never asserted it, so a run could look "done" while the composition was
not durably assembled — and the published-receipt was hand-authored rather
than attested by code.

``build_publication_receipt`` is a pure, unit-testable gate: it FAILS LOUD
(raises ``DescriptPublicationError``) on the detachment case (duration None or
``<= 0``) or when the assembled composition duration drifts from the expected
audio total beyond ``tolerance_s``. Only on pass does it return the receipt
dict that the build script writes to disk and treats as the authoritative
"published" attestation.

The helper reads no wall clock — pass ``attested_at_utc`` if you want the
field stamped; omit it to keep the receipt deterministic (e.g. in tests).
"""

from __future__ import annotations

from typing import Any


class DescriptPublicationError(RuntimeError):
    """Raised when a Descript composition is not durably assembled.

    Either the composition detached (duration None / <= 0) or its assembled
    duration drifts from the expected audio total beyond tolerance. Carrying a
    distinct type lets the build script exit non-zero without writing a
    published-receipt, instead of silently declaring "done".
    """


def build_publication_receipt(
    *,
    project_id: str,
    composition_id: str | None,
    composition_duration_s: float | int | None,
    expected_audio_total_s: float | int,
    tolerance_s: float = 1.0,
    attested_at_utc: str | None = None,
) -> dict[str, Any]:
    """Assert the composition is durably assembled, then return its receipt.

    FAILS LOUD (raises ``DescriptPublicationError``) when:
      - ``composition_duration_s`` is None or ``<= 0`` (the detachment case:
        Underlord had not finished assembling when the project was read), or
      - ``abs(composition_duration_s - expected_audio_total_s) > tolerance_s``
        (the assembled timeline does not match the narration we synthesized).

    The error message always names the actual vs expected duration so the
    mismatch is diagnosable from the log alone.

    On pass, returns the receipt dict (mirrors the hand-authored shape):
    ``{project_id, composition_id, composition_duration_s,
    expected_audio_total_s, duration_delta_s, duration_within_1s,
    published, published_attestation[, attested_at_utc]}``.
    """
    if composition_duration_s is None or composition_duration_s <= 0:
        raise DescriptPublicationError(
            "Descript composition is not durably assembled: "
            f"actual duration={composition_duration_s!r} "
            f"(expected ~{expected_audio_total_s}s). This is the "
            "duration-0-mid-assembly detachment case — the Underlord agent "
            "job had not finished assembling when get_project was read. "
            "NOT declaring published."
        )

    duration_delta_s = composition_duration_s - expected_audio_total_s
    if abs(duration_delta_s) > tolerance_s:
        raise DescriptPublicationError(
            "Descript composition duration drifted beyond tolerance: "
            f"actual={composition_duration_s}s vs "
            f"expected={expected_audio_total_s}s "
            f"(delta={duration_delta_s:+.3f}s, tolerance={tolerance_s}s). "
            "The assembled timeline does not match the synthesized narration. "
            "NOT declaring published."
        )

    receipt: dict[str, Any] = {
        "project_id": project_id,
        "composition_id": composition_id,
        "composition_duration_s": composition_duration_s,
        "expected_audio_total_s": expected_audio_total_s,
        "duration_delta_s": duration_delta_s,
        "duration_within_1s": True,
        "published": True,
        "published_attestation": True,
    }
    if attested_at_utc is not None:
        receipt["attested_at_utc"] = attested_at_utc
    return receipt
