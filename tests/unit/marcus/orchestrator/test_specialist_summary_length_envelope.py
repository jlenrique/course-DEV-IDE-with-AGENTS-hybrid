from __future__ import annotations

import pytest

from app.marcus.orchestrator.specialist_summary_writer import (
    SummaryLengthError,
    _validate_length,
)


def _lines(count: int) -> str:
    return "\n".join(f"line {index}" for index in range(count))


def test_15_line_summary_is_accepted() -> None:
    _validate_length(_lines(15))


def test_25_line_summary_is_accepted() -> None:
    _validate_length(_lines(25))


def test_14_line_summary_raises() -> None:
    with pytest.raises(SummaryLengthError):
        _validate_length(_lines(14))


def test_26_line_summary_raises() -> None:
    with pytest.raises(SummaryLengthError):
        _validate_length(_lines(26))
