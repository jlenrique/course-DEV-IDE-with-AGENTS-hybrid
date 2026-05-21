"""Tests for Story 30-2b ``dispatch_intake_pre_packet`` (AC-T.5)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog, PrePacketSnapshotPayload, SourceRef
from app.marcus.orchestrator import ORCHESTRATOR_MODULE_IDENTITY
from app.marcus.orchestrator import dispatch as dispatch_mod
from app.marcus.orchestrator.dispatch import dispatch_intake_pre_packet


def _sample_envelope() -> EventEnvelope:
    payload = PrePacketSnapshotPayload(
        sme_refs=[
            SourceRef(source_id="pdf-001", path=None, content_digest="a" * 64)
        ],
        ingestion_digest="b" * 64,
        pre_packet_artifact_path="course-content/staging/irene-packet.md",
        step_03_extraction_checksum="c" * 64,
    )
    return EventEnvelope(
        timestamp=datetime.now(tz=UTC),
        plan_revision=0,
        event_type="pre_packet_snapshot",
        payload=payload.model_dump(mode="json"),
    )


def test_dispatch_intake_pre_packet_happy_path(tmp_path: Path) -> None:
    """AC-T.5 (a) — happy path: one envelope → one log entry."""
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")
    envelope = _sample_envelope()

    dispatch_intake_pre_packet(envelope, log=log)

    events = list(log.read_events())
    assert len(events) == 1
    assert events[0].event_type == "pre_packet_snapshot"


def test_dispatch_intake_pre_packet_passes_orchestrator_writer_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """AC-T.5 (b) — dispatch always supplies writer=ORCHESTRATOR_MODULE_IDENTITY.

    Verifies the writer argument passed to the underlying write API surface;
    guards against a future refactor flipping the writer kwarg.
    """
    captured: dict[str, Any] = {}

    def fake_emit(envelope: EventEnvelope, *, writer: str, log: Any = None) -> None:
        captured["envelope"] = envelope
        captured["writer"] = writer
        captured["log"] = log

    monkeypatch.setattr(dispatch_mod, "emit_pre_packet_snapshot", fake_emit)

    envelope = _sample_envelope()
    log = LessonPlanLog(path=tmp_path / "lesson_plan_log.jsonl")

    dispatch_intake_pre_packet(envelope, log=log)

    assert captured["writer"] == ORCHESTRATOR_MODULE_IDENTITY
    assert captured["writer"] == "marcus-orchestrator"
    assert captured["envelope"] is envelope
    assert captured["log"] is log
