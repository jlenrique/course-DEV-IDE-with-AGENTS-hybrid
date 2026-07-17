"""Amendment M3b meta-pin: ``WITNESS_REPLAY_STRICT=1`` turns skip into FAILURE.

``runs/`` is gitignored, so a paid-run pre-flight that silently SKIPPED a
missing witness would read as green — this self-test proves skip ≠ green is
load-bearing, not aspirational.
"""

from __future__ import annotations

import pytest
from _pytest.outcomes import Failed, Skipped

from tests.live_witness_replay.registry import STRICT_ENV, skip_or_fail, strict_mode


def test_normal_mode_skips(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(STRICT_ENV, raising=False)
    assert not strict_mode()
    with pytest.raises(Skipped):
        skip_or_fail("witness missing")


def test_strict_mode_turns_skip_into_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(STRICT_ENV, "1")
    assert strict_mode()
    with pytest.raises(Failed) as caught:
        skip_or_fail("witness missing")
    assert "skip is not green" in str(caught.value)


@pytest.mark.parametrize("value", ["1", "true", "TRUE", " yes ", "On"])
def test_strict_mode_arms_on_recognized_truthy_values(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    """R6: {'1','true','yes','on'} arm strict mode, case-insensitive + stripped."""
    monkeypatch.setenv(STRICT_ENV, value)
    assert strict_mode()


@pytest.mark.parametrize("value", ["0", "", "false", "no", "OFF"])
def test_strict_mode_disarms_on_recognized_falsy_values(
    monkeypatch: pytest.MonkeyPatch, value: str
) -> None:
    monkeypatch.setenv(STRICT_ENV, value)
    assert not strict_mode()
    with pytest.raises(Skipped):
        skip_or_fail("witness missing")


def test_strict_mode_unrecognized_value_raises_never_silently_disarms(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """R6: a typo'd flag ('banana') is a hard error, never a silent disarm."""
    monkeypatch.setenv(STRICT_ENV, "banana")
    with pytest.raises(ValueError, match="never silently disarms"):
        strict_mode()
    with pytest.raises(ValueError, match="WITNESS_REPLAY_STRICT"):
        skip_or_fail("witness missing")
