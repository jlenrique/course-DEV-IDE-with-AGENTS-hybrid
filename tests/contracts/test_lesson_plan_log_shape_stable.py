"""AC-T.1 — Lesson Plan Log surface shape-pin.

Pins the ``log.py`` write-path surface via explicit-allowlist + SCHEMA_CHANGELOG
gate pattern (inherited from 27-0 / 31-1 AC-T.1). Any change without a
SCHEMA_CHANGELOG entry OR an allowlist update here fails the test.

Surface pinned:
    - ``LessonPlanLog`` (class; method allowlist)
    - ``WriterIdentity`` (Literal closed set)
    - ``StalePlanRefError`` / ``UnauthorizedWriterError`` (exception classes)
    - ``NAMED_MANDATORY_EVENTS`` (frozenset; parity checked separately in AC-T.7)
    - ``PrePacketSnapshotPayload`` / ``PlanLockedPayload`` / ``SourceRef`` (Pydantic)
    - ``LOG_PATH`` (module constant)
    - ``assert_plan_fresh`` (module-level function)
    - ``WRITER_EVENT_MATRIX`` (dict)
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import get_args

import app.marcus.lesson_plan.log as log_module
from app.marcus.lesson_plan.log import (
    LOG_PATH,
    NAMED_MANDATORY_EVENTS,
    WRITER_EVENT_MATRIX,
    LessonPlanLog,
    PlanLockedPayload,
    PrePacketSnapshotPayload,
    SourceRef,
    StalePlanRefError,
    UnauthorizedWriterError,
    WriterIdentity,
    assert_plan_fresh,
)

CHANGELOG = (
    Path(__file__).parents[2]
    / "_bmad-output"
    / "implementation-artifacts"
    / "SCHEMA_CHANGELOG.md"
)


# ---------------------------------------------------------------------------
# Allowlists (snapshot surface)
# ---------------------------------------------------------------------------


EXPECTED_LESSONPLANLOG_PUBLIC_METHODS = {
    "append_event",
    "read_events",
    "latest_plan_revision",
    "latest_plan_digest",
    # Properties (accessible as attrs):
    "path",
}


EXPECTED_PRE_PACKET_SNAPSHOT_FIELDS = {
    "sme_refs",
    "ingestion_digest",
    "pre_packet_artifact_path",
    "step_03_extraction_checksum",
}


EXPECTED_PLAN_LOCKED_PAYLOAD_FIELDS = {
    "lesson_plan_digest",
}


EXPECTED_SOURCE_REF_FIELDS = {
    "source_id",
    "path",
    "content_digest",
}


EXPECTED_MODULE_PUBLIC_NAMES = {
    "LOG_PATH",
    "LessonPlanLog",
    "LogCorruptError",
    "NAMED_MANDATORY_EVENTS",
    "PRE_PACKET_SNAPSHOT_EVENT_TYPE",
    "PlanLockedPayload",
    "PrePacketSnapshotPayload",
    "SourceRef",
    "StalePlanRefError",
    "UnauthorizedWriterError",
    "WRITER_EVENT_MATRIX",
    "WriterIdentity",
    "assert_plan_fresh",
}


# ---------------------------------------------------------------------------
# Module-level surface
# ---------------------------------------------------------------------------


def test_module_all_matches_expected_public_names() -> None:
    actual = set(log_module.__all__)
    assert actual == EXPECTED_MODULE_PUBLIC_NAMES, (
        f"log.py __all__ drift. Missing: {EXPECTED_MODULE_PUBLIC_NAMES - actual}. "
        f"New: {actual - EXPECTED_MODULE_PUBLIC_NAMES}. Update SCHEMA_CHANGELOG."
    )


def test_log_path_is_path_at_state_runtime() -> None:
    """LOG_PATH ends with the canonical relative segment and is absolute.

    G6 MF-BH-1: resolved to an absolute path at module import time via
    ``_find_project_root`` for cwd-independence. The contract is now
    "absolute AND ends with state/runtime/lesson_plan_log.jsonl" rather
    than literal equality to the relative form.
    """
    assert isinstance(LOG_PATH, Path)
    assert LOG_PATH.is_absolute(), f"LOG_PATH must be absolute; got {LOG_PATH}"
    canonical_tail = ("state", "runtime", "lesson_plan_log.jsonl")
    assert LOG_PATH.parts[-3:] == canonical_tail, (
        f"LOG_PATH drift: {LOG_PATH}. Canonical runtime tail per AC-B.1 is "
        f"state/runtime/lesson_plan_log.jsonl."
    )


# ---------------------------------------------------------------------------
# LessonPlanLog class surface
# ---------------------------------------------------------------------------


def _public_attrs(cls: type) -> set[str]:
    return {
        name
        for name, _ in inspect.getmembers(cls)
        if not name.startswith("_")
    }


def test_lessonplanlog_public_surface_matches_allowlist() -> None:
    actual = _public_attrs(LessonPlanLog)
    assert actual == EXPECTED_LESSONPLANLOG_PUBLIC_METHODS, (
        f"LessonPlanLog public surface drift. Missing: "
        f"{EXPECTED_LESSONPLANLOG_PUBLIC_METHODS - actual}. "
        f"New: {actual - EXPECTED_LESSONPLANLOG_PUBLIC_METHODS}."
    )


def test_append_event_signature_is_envelope_and_writer_identity() -> None:
    sig = inspect.signature(LessonPlanLog.append_event)
    params = list(sig.parameters.keys())
    assert params == ["self", "envelope", "writer_identity"], (
        f"append_event signature drift: {params}"
    )


def test_read_events_has_since_revision_and_event_types_kwargs() -> None:
    sig = inspect.signature(LessonPlanLog.read_events)
    assert "since_revision" in sig.parameters
    assert "event_types" in sig.parameters


# ---------------------------------------------------------------------------
# Payload shapes
# ---------------------------------------------------------------------------


def test_pre_packet_snapshot_payload_fields_match_allowlist() -> None:
    actual = set(PrePacketSnapshotPayload.model_fields.keys())
    assert actual == EXPECTED_PRE_PACKET_SNAPSHOT_FIELDS


def test_plan_locked_payload_fields_match_allowlist() -> None:
    actual = set(PlanLockedPayload.model_fields.keys())
    assert actual == EXPECTED_PLAN_LOCKED_PAYLOAD_FIELDS


def test_source_ref_fields_match_allowlist() -> None:
    actual = set(SourceRef.model_fields.keys())
    assert actual == EXPECTED_SOURCE_REF_FIELDS


# ---------------------------------------------------------------------------
# WriterIdentity closed set
# ---------------------------------------------------------------------------


def test_writer_identity_is_closed_literal_set() -> None:
    args = set(get_args(WriterIdentity))
    assert args == {"marcus-orchestrator", "marcus-intake"}, (
        f"WriterIdentity widened: {args}. Widening requires ruling amendment + "
        f"SCHEMA_CHANGELOG major bump per AC-C.5."
    )


# ---------------------------------------------------------------------------
# WRITER_EVENT_MATRIX shape
# ---------------------------------------------------------------------------


def test_writer_event_matrix_keys_equal_named_mandatory_events() -> None:
    assert set(WRITER_EVENT_MATRIX.keys()) == NAMED_MANDATORY_EVENTS


def test_writer_event_matrix_only_pre_packet_allows_intake() -> None:
    for event_type, permitted in WRITER_EVENT_MATRIX.items():
        if event_type == "pre_packet_snapshot":
            assert "marcus-intake" in permitted
            assert "marcus-orchestrator" in permitted
        else:
            assert "marcus-intake" not in permitted, (
                f"R1 amendment 13 violation: {event_type} permits marcus-intake"
            )
            assert "marcus-orchestrator" in permitted


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


def test_stale_plan_ref_error_is_value_error_subclass() -> None:
    assert issubclass(StalePlanRefError, ValueError)


def test_unauthorized_writer_error_is_permission_error_subclass() -> None:
    assert issubclass(UnauthorizedWriterError, PermissionError)


# ---------------------------------------------------------------------------
# assert_plan_fresh function
# ---------------------------------------------------------------------------


def test_assert_plan_fresh_is_callable_module_level() -> None:
    assert callable(assert_plan_fresh)
    sig = inspect.signature(assert_plan_fresh)
    assert "envelope" in sig.parameters
    assert "log" in sig.parameters


# ---------------------------------------------------------------------------
# SCHEMA_CHANGELOG gate
# ---------------------------------------------------------------------------


def test_schema_changelog_pins_lesson_plan_log_v1_0() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")
    assert "Lesson Plan Log v1.0" in text, (
        "SCHEMA_CHANGELOG.md does not pin `Lesson Plan Log v1.0` — per "
        "AC-C.3 the log surface requires its own changelog entry."
    )
    assert "Story 31-2" in text, "Changelog entry must attribute to Story 31-2"
