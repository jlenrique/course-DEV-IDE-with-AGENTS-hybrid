"""G6 code-review hardening tests for Story 31-2 Lesson Plan Log.

Covers the MUST-FIX + SHOULD-FIX patches applied after the layered
bmad-code-review:

* **MF-BH-1** — ``LOG_PATH`` resolved to absolute path at module import time
  (cwd-independent).
* **MF-BH-2** — ``latest_plan_revision`` / ``latest_plan_digest`` use
  reverse-scan (O(file-tail) steady-state rather than O(N) per call).
* **MF-BH-3** — ``latest_plan_digest`` raises :class:`LogCorruptError` on a
  ``plan.locked`` event with a malformed payload (strict, not tolerant).
* **MF-BH-4** — bootstrap sentinel aligned: ``latest_plan_digest()`` returns
  ``None`` on empty log; :func:`assert_plan_fresh` accepts env_digest in
  ``{"", None}`` at bootstrap.
* **MF-EC-1** — :meth:`LessonPlanLog.read_events` raises
  :class:`LogCorruptError` on corrupted JSON (named line + path).
* **MF-EC-2** — pre-existing log contract: callers MUST consult
  ``latest_plan_revision()`` — re-using revision against a non-empty log
  raises :class:`StaleRevisionError`.
* **SF-EC-3** — invalid ``writer_identity`` (not in the Literal) → dedicated
  :class:`ValueError` (separates typos from permission failures).
* **SF-EC-8** — ``PrePacketSnapshotPayload.sme_refs`` requires min_length=1.
* **SF-EC-9** — ``SourceRef.path`` / ``pre_packet_artifact_path`` reject
  absolute + ``..``-traversal paths.
* **SF-BH-6** — ``_json_default`` raises :class:`TypeError` on unsupported types.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import (
    LOG_PATH,
    NAMED_MANDATORY_EVENTS,
    WRITER_EVENT_MATRIX,
    LessonPlanLog,
    LogCorruptError,
    PrePacketSnapshotPayload,
    SourceRef,
    UnauthorizedWriterError,
    _json_default,
)
from app.marcus.lesson_plan.schema import StaleRevisionError

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_log(tmp_path: Path) -> LessonPlanLog:
    return LessonPlanLog(path=tmp_path / "log.jsonl")


def _env(event_type: str, rev: int, payload: dict | None = None) -> EventEnvelope:
    return EventEnvelope(
        event_id=str(uuid4()),
        timestamp=datetime.now(tz=UTC),
        plan_revision=rev,
        event_type=event_type,
        payload=payload or {},
    )


def _plan_locked(rev: int, digest: str = "d") -> EventEnvelope:
    return _env("plan.locked", rev, payload={"lesson_plan_digest": digest})


# ---------------------------------------------------------------------------
# MF-BH-1 — LOG_PATH cwd-independent (absolute at import time)
# ---------------------------------------------------------------------------


def test_log_path_is_absolute_at_import_time() -> None:
    """MF-BH-1: LOG_PATH resolved via project-root walk; must be absolute."""
    assert LOG_PATH.is_absolute(), (
        f"LOG_PATH must be absolute (cwd-independent); got {LOG_PATH}"
    )


def test_log_path_ends_with_canonical_relative_segment() -> None:
    """MF-BH-1: absolute LOG_PATH still honors the state/runtime/ canonical form."""
    parts = LOG_PATH.parts[-3:]
    assert parts == ("state", "runtime", "lesson_plan_log.jsonl"), (
        f"LOG_PATH must end with state/runtime/lesson_plan_log.jsonl; got {LOG_PATH}"
    )


# ---------------------------------------------------------------------------
# MF-BH-2 — reverse-scan semantics (correctness)
# ---------------------------------------------------------------------------


def test_latest_plan_revision_reverse_scan_correctness(tmp_log: LessonPlanLog) -> None:
    """MF-BH-2: latest_plan_revision returns the LAST plan.locked in file order."""
    # Seed three plan.locked events at 1 → 2 → 3.
    for rev in (1, 2, 3):
        tmp_log.append_event(
            _plan_locked(rev, digest=f"d{rev}"),
            writer_identity="marcus-orchestrator",
        )
    # Reverse-scan must return the final lock revision (3), not iterate all.
    assert tmp_log.latest_plan_revision() == 3
    assert tmp_log.latest_plan_digest() == "d3"


def test_latest_plan_revision_reverse_scan_ignores_non_plan_locked(tmp_log: LessonPlanLog) -> None:
    """MF-BH-2: reverse-scan skips non-plan.locked events and finds latest lock."""
    tmp_log.append_event(_plan_locked(1, digest="d1"), writer_identity="marcus-orchestrator")
    # Pile on non-plan.locked events at mixed revisions.
    for et, rev in [
        ("plan_unit.created", 1),
        ("scope_decision.set", 1),
        ("scope_decision_transition", 2),
        ("fanout.envelope.emitted", 3),
    ]:
        tmp_log.append_event(_env(et, rev), writer_identity="marcus-orchestrator")
    # Latest plan.locked is still rev=1.
    assert tmp_log.latest_plan_revision() == 1
    assert tmp_log.latest_plan_digest() == "d1"


def test_latest_plan_revision_efficient_on_larger_log(tmp_log: LessonPlanLog) -> None:
    """MF-BH-2 (correctness shield): 30+ events do not confuse reverse-scan."""
    for rev in range(1, 11):
        tmp_log.append_event(
            _plan_locked(rev, digest=f"d{rev}"), writer_identity="marcus-orchestrator"
        )
        tmp_log.append_event(
            _env("plan_unit.created", rev), writer_identity="marcus-orchestrator"
        )
        tmp_log.append_event(
            _env("scope_decision.set", rev), writer_identity="marcus-orchestrator"
        )
    # 30 events total; latest plan.locked at rev=10.
    assert tmp_log.latest_plan_revision() == 10
    assert tmp_log.latest_plan_digest() == "d10"


# ---------------------------------------------------------------------------
# MF-BH-3 — malformed plan.locked payload is STRICT, not tolerant
# ---------------------------------------------------------------------------


def test_latest_plan_digest_raises_on_malformed_plan_locked_payload(
    tmp_path: Path,
) -> None:
    """MF-BH-3: plan.locked with missing lesson_plan_digest → LogCorruptError.

    Silently returning a stale digest from an earlier revision would be
    contract drift; strict-raise gives operators an unambiguous signal.
    """
    log_path = tmp_path / "log.jsonl"
    # Manually write a plan.locked line whose payload is missing the required
    # lesson_plan_digest. We bypass append_event (which would reject via
    # PlanLockedPayload validation at WRITE time) because MF-BH-3 is about
    # READ-time robustness on a corrupted log.
    import json

    envelope = {
        "event_id": str(uuid4()),
        "timestamp": datetime.now(tz=UTC).isoformat(),
        "plan_revision": 1,
        "event_type": "plan.locked",
        "payload": {},  # malformed — missing lesson_plan_digest
    }
    log_path.write_text(json.dumps(envelope) + "\n", encoding="utf-8")
    log = LessonPlanLog(path=log_path)
    with pytest.raises(LogCorruptError) as exc:
        log.latest_plan_digest()
    assert "plan.locked" in str(exc.value)
    assert "PlanLockedPayload" in str(exc.value)


# ---------------------------------------------------------------------------
# MF-EC-1 — read_events raises LogCorruptError on partial/malformed JSON
# ---------------------------------------------------------------------------


def test_read_events_raises_log_corrupt_error_on_malformed_json(
    tmp_log: LessonPlanLog,
) -> None:
    """MF-EC-1: malformed JSON line → LogCorruptError naming the line + path."""
    tmp_log.append_event(_env("plan_unit.created", 1), writer_identity="marcus-orchestrator")
    # Append a corrupt line (not valid JSON).
    with tmp_log.path.open("a", encoding="utf-8") as fh:
        fh.write("{not valid json\n")
    with pytest.raises(LogCorruptError) as exc:
        list(tmp_log.read_events())
    assert "line 2" in str(exc.value)
    assert str(tmp_log.path) in str(exc.value) or "log.jsonl" in str(exc.value)


def test_read_events_raises_log_corrupt_error_on_partial_line(
    tmp_log: LessonPlanLog,
) -> None:
    """MF-EC-1: partial JSON line → LogCorruptError."""
    tmp_log.append_event(_env("plan_unit.created", 1), writer_identity="marcus-orchestrator")
    with tmp_log.path.open("a", encoding="utf-8") as fh:
        fh.write('{"event_id": "partial\n')
    with pytest.raises(LogCorruptError):
        list(tmp_log.read_events())


def test_latest_plan_revision_raises_log_corrupt_error_on_corruption(
    tmp_log: LessonPlanLog,
) -> None:
    """MF-EC-1 propagation: latest_plan_revision also surfaces corruption."""
    tmp_log.append_event(_plan_locked(1), writer_identity="marcus-orchestrator")
    with tmp_log.path.open("a", encoding="utf-8") as fh:
        fh.write("{garbled\n")
    with pytest.raises(LogCorruptError):
        tmp_log.latest_plan_revision()


def test_read_events_raises_on_envelope_validation_failure(
    tmp_log: LessonPlanLog,
) -> None:
    """MF-EC-1: a valid-JSON line that fails EventEnvelope validation → LogCorruptError."""
    import json

    # Write a JSON line missing a required envelope field.
    with tmp_log.path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"event_id": "bogus"}) + "\n")
    with pytest.raises(LogCorruptError) as exc:
        list(tmp_log.read_events())
    assert "envelope validation failed" in str(exc.value)


# ---------------------------------------------------------------------------
# MF-EC-2 — pre-existing log contract (caller revision discipline)
# ---------------------------------------------------------------------------


def test_plan_locked_rev_must_exceed_pre_existing_log(tmp_log: LessonPlanLog) -> None:
    """MF-EC-2: a caller attempting plan_revision=1 against a log with rev=100 is stale.

    The log is append-across-runs; callers MUST consult
    ``latest_plan_revision()`` and compute the next revision as
    ``latest + 1``. Reusing a revision number is a ``StaleRevisionError``
    regardless of run boundaries.
    """
    # Seed the log with a high revision (simulates a prior run's output).
    tmp_log.append_event(_plan_locked(100), writer_identity="marcus-orchestrator")
    # A naive "second run" assumes empty log and tries revision=1.
    with pytest.raises(StaleRevisionError):
        tmp_log.append_event(
            _plan_locked(1, digest="naive"), writer_identity="marcus-orchestrator"
        )


# ---------------------------------------------------------------------------
# SF-EC-3 — invalid writer_identity (typo) raises ValueError, not PermissionError
# ---------------------------------------------------------------------------


def test_invalid_writer_identity_raises_value_error(tmp_log: LessonPlanLog) -> None:
    """SF-EC-3: a writer_identity typo (not in WriterIdentity Literal) → ValueError.

    Separates "typo" from "auth-fail" — previously both surfaced as
    ``UnauthorizedWriterError`` (subclass of PermissionError).
    """
    with pytest.raises(ValueError) as exc:
        tmp_log.append_event(
            _env("plan_unit.created", 0),
            writer_identity="marcus_orchestrator",  # underscore typo  # type: ignore[arg-type]
        )
    msg = str(exc.value)
    assert "marcus_orchestrator" in msg
    assert "recognized WriterIdentity" in msg


def test_invalid_writer_identity_is_not_unauthorized_writer_error(
    tmp_log: LessonPlanLog,
) -> None:
    """SF-EC-3: typo must NOT surface as UnauthorizedWriterError."""
    with pytest.raises(ValueError) as exc:
        tmp_log.append_event(
            _env("plan_unit.created", 0),
            writer_identity="nonsense-writer",  # type: ignore[arg-type]
        )
    assert not isinstance(exc.value, UnauthorizedWriterError)


# ---------------------------------------------------------------------------
# SF-EC-8 — PrePacketSnapshotPayload.sme_refs requires at least one entry
# ---------------------------------------------------------------------------


def test_pre_packet_snapshot_rejects_empty_sme_refs() -> None:
    """SF-EC-8: sme_refs MUST be non-empty."""
    with pytest.raises(ValidationError):
        PrePacketSnapshotPayload(
            sme_refs=[],
            ingestion_digest="dead",
            pre_packet_artifact_path="artifacts/pp.json",
            step_03_extraction_checksum="beef",
        )


def test_pre_packet_snapshot_accepts_one_sme_ref() -> None:
    """SF-EC-8: exactly one sme_ref satisfies the min_length=1 gate."""
    payload = PrePacketSnapshotPayload(
        sme_refs=[SourceRef(source_id="s1", path="sources/a.docx", content_digest="xyz")],
        ingestion_digest="dead",
        pre_packet_artifact_path="artifacts/pp.json",
        step_03_extraction_checksum="beef",
    )
    assert len(payload.sme_refs) == 1


# ---------------------------------------------------------------------------
# SF-EC-9 — repo-relative path validator (SourceRef.path + pre_packet_artifact_path)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "bad_path",
    [
        "../etc/passwd",
        "/etc/passwd",
        "/absolute/path/to/source.docx",
        "C:/Windows/System32/cmd.exe",
        "C:\\Windows\\System32\\cmd.exe",
        "sources/../../../escape.txt",
        "a/b/../../../c",
    ],
)
def test_source_ref_path_rejects_traversal_and_absolute(bad_path: str) -> None:
    """SF-EC-9: SourceRef.path rejects traversal + absolute paths."""
    with pytest.raises(ValidationError):
        SourceRef(source_id="s1", path=bad_path, content_digest="xyz")


@pytest.mark.parametrize(
    "bad_path",
    [
        "../etc/passwd",
        "/var/run/artifact.json",
        "C:/ProgramFiles/artifact.json",
        "artifacts/../../../escape.json",
    ],
)
def test_pre_packet_artifact_path_rejects_traversal_and_absolute(bad_path: str) -> None:
    """SF-EC-9: pre_packet_artifact_path rejects traversal + absolute paths."""
    with pytest.raises(ValidationError):
        PrePacketSnapshotPayload(
            sme_refs=[SourceRef(source_id="s1", path="sources/a.docx", content_digest="xyz")],
            ingestion_digest="dead",
            pre_packet_artifact_path=bad_path,
            step_03_extraction_checksum="beef",
        )


def test_source_ref_path_allows_repo_relative() -> None:
    """SF-EC-9: ordinary repo-relative paths are accepted."""
    ref = SourceRef(source_id="s1", path="tests/fixtures/sample.docx", content_digest="xyz")
    assert ref.path == "tests/fixtures/sample.docx"


def test_source_ref_path_allows_none() -> None:
    """SF-EC-9: SourceRef.path remains Optional — None is still allowed."""
    ref = SourceRef(source_id="s1", path=None, content_digest="xyz")
    assert ref.path is None


# ---------------------------------------------------------------------------
# SF-BH-6 — _json_default raises TypeError on unsupported types
# ---------------------------------------------------------------------------


def test_json_default_raises_on_unsupported_type() -> None:
    """SF-BH-6: _json_default rejects anything reaching the fallback.

    ``model_dump(mode="json")`` stringifies datetimes upstream; any value
    reaching ``_json_default`` is, by definition, an unsupported type.
    Raise :class:`TypeError` with a clear message.
    """
    with pytest.raises(TypeError) as exc:
        _json_default(Decimal("1.5"))
    assert "Decimal" in str(exc.value)


def test_json_default_rejects_sets() -> None:
    """SF-BH-6: sets are not JSON-serializable; _json_default rejects."""
    with pytest.raises(TypeError):
        _json_default({1, 2, 3})


# ---------------------------------------------------------------------------
# SF-BH-7 — module-level import-time safety net
# ---------------------------------------------------------------------------


def test_writer_event_matrix_keys_match_named_mandatory_events() -> None:
    """SF-BH-7: WRITER_EVENT_MATRIX keys == NAMED_MANDATORY_EVENTS.

    The module-level ``assert`` in ``log.py`` enforces this at import
    time; this test is the belt-and-suspenders surface.
    """
    assert frozenset(WRITER_EVENT_MATRIX.keys()) == NAMED_MANDATORY_EVENTS
