"""Orchestrator write_api tests: AC-T.3, AC-T.4, AC-T.5, AC-T.12, AC-T.13, AC-T.14, AC-T.18.

Covers the single-writer entry point's:
* delegation to 31-2 log (AC-T.3)
* wrong-writer rejection + Maya-safe error message (AC-T.4)
* wrong-event-type rejection (AC-T.5)
* idempotency behavioral pin + import-site model_validate pin (AC-T.12)
* precedence ordering — writer check before event-type check (AC-T.13)
* type-gate on envelope (AC-T.14)
* UnauthorizedFacadeCallerError attribute discipline (AC-T.18)
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.orchestrator import ORCHESTRATOR_MODULE_IDENTITY
from app.marcus.orchestrator.write_api import (
    UnauthorizedFacadeCallerError,
    emit_pre_packet_snapshot,
)

_VALID_PAYLOAD: dict = {
    "source_ref": {
        "path": "tests/fixtures/trial_corpus/placeholder.md",
        "sha256": "a" * 64,
    },
    "pre_packet_artifact_path": "tests/fixtures/trial_corpus/placeholder.md",
    "audience_profile_version": 1,
    "sme_refs": ["placeholder"],
}


def _make_envelope(event_type: str = "pre_packet_snapshot") -> EventEnvelope:
    return EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=0,
        event_type=event_type,
        payload=_VALID_PAYLOAD if event_type == "pre_packet_snapshot" else {},
    )


# ---------------------------------------------------------------------------
# AC-T.3 — delegation smoke
# ---------------------------------------------------------------------------


def test_emit_delegates_to_append_event_with_correct_writer(tmp_path: Path) -> None:
    """AC-T.3 — happy path: envelope reaches the log via append_event."""
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    envelope = _make_envelope()

    emit_pre_packet_snapshot(envelope, writer=ORCHESTRATOR_MODULE_IDENTITY, log=log)

    events = list(log.read_events())
    assert len(events) == 1
    assert events[0].event_id == envelope.event_id
    assert events[0].event_type == "pre_packet_snapshot"


# ---------------------------------------------------------------------------
# AC-T.4 — wrong-writer rejection + Maya-safe error message
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_writer",
    ["marcus-intake", "marcus", "irene", "maya", ""],
)
def test_wrong_writer_raises_unauthorized_and_maya_safe(
    bad_writer: str,
    tmp_path: Path,
) -> None:
    """AC-T.4 + AC-B.11 — non-Orchestrator callers raise; str(err) is Maya-safe."""
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    envelope = _make_envelope()

    with pytest.raises(UnauthorizedFacadeCallerError) as exc_info:
        emit_pre_packet_snapshot(envelope, writer=bad_writer, log=log)  # type: ignore[arg-type]

    err_str = str(exc_info.value)
    err_args0 = exc_info.value.args[0]

    # Maya-safe message: no hyphenated sub-identity tokens, no offending writer.
    for forbidden in ("intake", "orchestrator", "negotiator"):
        assert forbidden not in err_str.lower(), (
            f"{forbidden!r} leaked into str(err): {err_str!r}"
        )
        assert forbidden not in err_args0.lower(), (
            f"{forbidden!r} leaked into err.args[0]: {err_args0!r}"
        )
    if bad_writer:
        assert bad_writer not in err_str, (
            f"offending writer {bad_writer!r} leaked into str(err): {err_str!r}"
        )

    # Attribute discipline: offending writer + debug_detail carry the detail.
    assert exc_info.value.offending_writer == bad_writer
    assert bad_writer in exc_info.value.debug_detail if bad_writer else True
    assert "marcus-orchestrator" in exc_info.value.debug_detail


# ---------------------------------------------------------------------------
# AC-T.5 — wrong-event-type rejection
# ---------------------------------------------------------------------------


def test_wrong_event_type_raises_value_error(tmp_path: Path) -> None:
    """AC-T.5 — non-``pre_packet_snapshot`` envelope rejected with ValueError."""
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    envelope = _make_envelope(event_type="plan.locked")

    with pytest.raises(ValueError) as exc_info:
        emit_pre_packet_snapshot(
            envelope, writer=ORCHESTRATOR_MODULE_IDENTITY, log=log
        )

    msg = str(exc_info.value)
    assert "pre_packet_snapshot" in msg
    assert "plan.locked" in msg


# ---------------------------------------------------------------------------
# AC-T.12 — idempotency: behavioral pin + import-site validate-never-called
# ---------------------------------------------------------------------------


def test_two_emits_produce_two_log_entries_no_silent_dedup(tmp_path: Path) -> None:
    """AC-T.12 (behavioral primary) — no dedup; each call is a distinct append."""
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    envelope = _make_envelope()

    emit_pre_packet_snapshot(envelope, writer=ORCHESTRATOR_MODULE_IDENTITY, log=log)
    emit_pre_packet_snapshot(envelope, writer=ORCHESTRATOR_MODULE_IDENTITY, log=log)

    events = list(log.read_events())
    assert len(events) == 2


def test_emit_does_not_re_trigger_model_validate_at_import_site(
    tmp_path: Path,
) -> None:
    """AC-T.12 (import-site pin, M-3 rider) — no re-validation at write_api."""
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    envelope = _make_envelope()

    with (
        patch("marcus.orchestrator.write_api.EventEnvelope.model_validate") as mv,
        patch(
            "marcus.orchestrator.write_api.EventEnvelope.model_validate_json"
        ) as mvj,
    ):
        emit_pre_packet_snapshot(
            envelope, writer=ORCHESTRATOR_MODULE_IDENTITY, log=log
        )

    assert mv.call_count == 0
    assert mvj.call_count == 0


# ---------------------------------------------------------------------------
# AC-T.13 — precedence ordering (Q-1 rider)
# ---------------------------------------------------------------------------


def test_writer_check_fires_before_event_type_check(tmp_path: Path) -> None:
    """AC-T.13 — both conditions violated → writer error wins.

    Security-forward default: unauthorized callers learn nothing about
    envelope-shape validity.
    """
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    envelope = _make_envelope(event_type="plan.locked")  # wrong event_type

    with pytest.raises(UnauthorizedFacadeCallerError):
        emit_pre_packet_snapshot(envelope, writer="marcus-intake", log=log)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# AC-T.14 — type-gate on envelope (Q-3 rider)
# ---------------------------------------------------------------------------


def test_dict_envelope_raises_type_error(tmp_path: Path) -> None:
    """AC-T.14 — dict-shaped envelope rejected; idempotency-trust is type-gated."""
    log = LessonPlanLog(path=tmp_path / "log.jsonl")
    bad_envelope: dict = {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "plan_revision": 0,
        "event_type": "pre_packet_snapshot",
        "payload": _VALID_PAYLOAD,
    }

    with pytest.raises(TypeError) as exc_info:
        emit_pre_packet_snapshot(
            bad_envelope,  # type: ignore[arg-type]
            writer=ORCHESTRATOR_MODULE_IDENTITY,
            log=log,
        )

    assert "EventEnvelope" in str(exc_info.value)


# ---------------------------------------------------------------------------
# AC-T.18 — UnauthorizedFacadeCallerError attribute discipline
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "offending",
    ["marcus-intake", "marcus-negotiator", "irene", "maya", "random-attacker"],
)
def test_unauthorized_error_shape_is_maya_safe(offending: str) -> None:
    """AC-T.18 — ``str(err)`` Maya-safe; offending writer on attribute only."""
    err = UnauthorizedFacadeCallerError(offending)

    # Maya-safe message — equal to the pinned generic across all inputs.
    expected_maya_safe = (
        "Sorry — I hit an internal hiccup. Give me a moment and try again?"
    )
    assert str(err) == expected_maya_safe
    assert err.args == (expected_maya_safe,)

    # Offending writer preserved verbatim on attribute.
    assert err.offending_writer == offending

    # Debug detail names both offending and expected.
    assert offending in err.debug_detail
    assert ORCHESTRATOR_MODULE_IDENTITY in err.debug_detail

    # str(err) does NOT contain the offending writer.
    assert offending not in str(err)
