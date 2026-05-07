"""Smoke test pinning the 29-2 unblock handshake (Story 29-1, AC-B.9)."""

from __future__ import annotations


def test_29_1_unblock_handshake() -> None:
    """AC-B.9 — the six canonical names are importable and callable/raiseable.

    This is the single-line completion signal documented in the TL;DR: when
    29-1 closes, 29-2 MUST be able to import the six public names from
    ``marcus.lesson_plan.fit_report`` and use them immediately. If this test
    fails, 29-2 cannot begin.
    """
    from app.marcus.lesson_plan.fit_report import (  # noqa: PLC0415
        StaleFitReportError,
        UnknownUnitIdError,
        deserialize_fit_report,
        emit_fit_report,
        serialize_fit_report,
        validate_fit_report,
    )

    # Functions are callable.
    assert callable(validate_fit_report)
    assert callable(serialize_fit_report)
    assert callable(deserialize_fit_report)
    assert callable(emit_fit_report)

    # Exceptions are raiseable and inherit ValueError.
    assert issubclass(StaleFitReportError, ValueError)
    assert issubclass(UnknownUnitIdError, ValueError)
