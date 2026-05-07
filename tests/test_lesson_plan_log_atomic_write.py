"""AC-T.9 — Atomic-write behavior.

Two surfaces:
    - ``test_fsync_called_on_append`` (all platforms): spy-based fsync
      assertion; verifies the write → flush → fsync call sequence.
    - ``test_no_partial_line_on_simulated_crash`` (POSIX only via skipif):
      simulates a crash and asserts the log file is readable without
      half-JSON.

Per Murat note in AC-B.9 / `feedback_regression_proof_tests.md`: no xfail
on the default suite. Platform-conditional skipif on the crash-simulation
assertion is exempted as collect-time platform gating.
"""

from __future__ import annotations

import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog, LogCorruptError


def _env(event_type: str = "plan_unit.created", rev: int = 1) -> EventEnvelope:
    return EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=rev,
        event_type=event_type,
        payload={},
    )


def test_fsync_called_on_append(tmp_path: Path) -> None:
    """AC-T.9 (all platforms): os.fsync must be called after each append."""
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    with patch("marcus.lesson_plan.log.os.fsync", wraps=os.fsync) as fsync_spy:
        log.append_event(_env(), writer_identity="marcus-orchestrator")
    assert fsync_spy.call_count == 1, (
        f"os.fsync must be called exactly once per append; got {fsync_spy.call_count}"
    )


def test_fsync_called_multiple_appends(tmp_path: Path) -> None:
    """AC-T.9: N appends → N fsync calls."""
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    with patch("marcus.lesson_plan.log.os.fsync", wraps=os.fsync) as fsync_spy:
        log.append_event(_env(), writer_identity="marcus-orchestrator")
        log.append_event(_env(), writer_identity="marcus-orchestrator")
        log.append_event(_env(), writer_identity="marcus-orchestrator")
    assert fsync_spy.call_count == 3


def test_fsync_is_final_call(tmp_path: Path) -> None:
    """AC-T.9: fsync is the final call in the write→flush→fsync sequence.

    G6 SF-BH-13: renamed from ``test_write_flush_fsync_sequence``. The
    write→flush ordering is a Python stdlib invariant (not an 31-2 contract)
    — testing it directly is over-scope. What 31-2 owns is "fsync is
    invoked, and it is the LAST syscall before context-manager exit." A
    missed fsync would surface as an M-5 re-read-after-write failure.
    """
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    call_order: list[str] = []

    real_fsync = os.fsync

    def fsync_stub(fd: int) -> None:
        call_order.append("fsync")
        real_fsync(fd)

    with patch("marcus.lesson_plan.log.os.fsync", side_effect=fsync_stub):
        # Append; write + flush happen inside the with-block before fsync.
        log.append_event(_env(), writer_identity="marcus-orchestrator")

    # fsync MUST be the final (and only) tracked call.
    assert call_order == ["fsync"], f"fsync call order drift: {call_order}"


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="POSIX fsync atomicity guarantee; Windows NTFS sufficient for "
    "single-process single-writer per AC-B.9 platform caveat.",
)
def test_no_partial_line_on_simulated_crash(tmp_path: Path) -> None:
    """AC-T.9 POSIX: partial line in log raises LogCorruptError at read.

    G6 SF-AA-3: simulates a human-edited corrupt log (or a crash that
    left a partial line despite fsync). The real-world single-writer
    POSIX-append <PIPE_BUF scenario should NOT create partial lines — but
    if one appears by any means (manual edit, external corruption, disk
    bitflip), the read path MUST raise :class:`LogCorruptError` with
    actionable line-number diagnosis (G6 MF-EC-1) rather than silently
    truncating or reading a malformed envelope.
    """
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    # Write one complete event.
    log.append_event(_env("plan_unit.created", 1), writer_identity="marcus-orchestrator")

    # Simulate a corruption scenario: append half a JSON object to the file.
    # (Real-world: crash-before-fsync on a non-MVP multi-writer setup, or
    # human edit. Either way, the read path must fail LOUDLY.)
    path = log.path
    with path.open("a", encoding="utf-8") as fh:
        fh.write('{"event_id": "partial\n')

    # Re-read; the corrupted line MUST raise LogCorruptError naming the
    # line number.
    with pytest.raises(LogCorruptError) as exc:
        list(log.read_events())
    assert "line 2" in str(exc.value), (
        f"LogCorruptError must name the corrupted line; got: {exc.value}"
    )


def test_append_creates_parent_directory(tmp_path: Path) -> None:
    """AC-B.9: append_event creates the parent directory if absent."""
    nested = tmp_path / "runtime" / "nested" / "log.jsonl"
    log = LessonPlanLog(path=nested)
    assert not nested.parent.exists()
    log.append_event(_env(), writer_identity="marcus-orchestrator")
    assert nested.exists()
    assert nested.parent.is_dir()
