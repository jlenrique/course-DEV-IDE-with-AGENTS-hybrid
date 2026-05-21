"""Lesson Plan Log — append-only JSONL write-path + single-writer enforcement (Story 31-2).

Ships the `LessonPlanLog` class, `append_event` / `read_events` /
`latest_plan_revision` / `latest_plan_digest` API surface, the
module-level `assert_plan_fresh` staleness detector, the `WriterIdentity`
Literal closed set, the single-writer matrix (`WRITER_EVENT_MATRIX`), the
`NAMED_MANDATORY_EVENTS` frozenset alias, and the `PrePacketSnapshotPayload`
/ `PlanLockedPayload` / `SourceRef` Pydantic payload shapes.

Amendments surfaced here:

* **R1 ruling amendment 8** — six named mandatory events (aliased from
  :data:`marcus.lesson_plan.event_type_registry.RESERVED_LOG_EVENT_TYPES`).
* **R1 ruling amendment 13** — Marcus-Orchestrator is the SOLE writer for
  five of six event_types; `pre_packet_snapshot` is the single Intake-
  permitted row (enforced by `WRITER_EVENT_MATRIX` + runtime matrix check
  in `append_event`). Triple-surfaced: schema (Literal) + runtime (matrix)
  + tests (12-case parametrized, ``tests/test_lesson_plan_log_single_writer.py``).
* **Winston R1 amendment on 30-4** — `pre_packet_snapshot.payload` carries
  ENOUGH state for 30-4 fanout to reconstruct Intake-era context from the
  log alone (no in-memory Marcus-Intake dependency). Shape pinned on
  :class:`PrePacketSnapshotPayload`.
* **R2 M-2 — monotonic revision scope.** Monotonic-revision gate applies
  ONLY to `plan.locked` events. Non-`plan.locked` events at stale revision
  are LEGAL (interleaved writes ordering). See :meth:`LessonPlanLog.append_event`.

Atomic-write discipline (AC-B.9 / R2 W-R1):

    Single-process single-writer MVP. ``append_event`` writes one canonical-JSON
    line per event via ``open("a") + write + flush + fsync``. POSIX-side the
    write of a line < ``PIPE_BUF`` offers useful atomicity guarantees for the
    single-writer case; Windows NTFS does not guarantee OS-level atomicity but
    is adequate for the declared single-process single-writer assumption
    (AC-C.7).

Platform caveat (Winston W-R1, R2 party-mode 2026-04-18):

    Current append uses append-then-fsync on POSIX. On Windows NTFS, future
    hardening via ``os.replace()`` temp-file-rename is atomic; the current
    implementation is adequate for single-process single-writer MVP but may be
    upgraded for multi-writer scenarios. See ruling amendment R-W1
    (2026-04-18 R2 party-mode).

Writer discipline (Quinn Q-R2-R1, R2 party-mode 2026-04-18):

    Do NOT pass a ``writer_identity`` other than the one your module owns.
    Intake modules pass only ``"marcus-intake"``; Orchestrator modules pass only
    ``"marcus-orchestrator"``. ``bmad-code-review`` Blind Hunter SHOULD grep for
    ``writer_identity=`` assignments and verify caller-module alignment.
    Trust-the-caller is the single-process single-writer assumption;
    grep-detectable discipline converts it from convention to CI-verifiable.

Log lifecycle contract (G6 MF-EC-2):

    The log at :data:`LOG_PATH` is an **append-across-runs governance
    artifact**. It persists between process invocations and MUST NOT be
    assumed empty at caller init. Callers writing ``plan.locked`` events
    MUST consult :meth:`LessonPlanLog.latest_plan_revision` to compute the
    next revision (``latest + 1``). Re-using a prior revision number
    (including ``plan_revision=1`` against a non-empty log) raises
    :class:`marcus.lesson_plan.schema.StaleRevisionError`. This is the
    strict-monotonic pin per §6-B2; idempotent-relock is out-of-scope.

Out-of-scope (AC-C.7):

* No compaction, no rotation, no external observers.
* No multi-process coordination (explicit single-process single-writer).
* No event dedup (two identical envelopes produce two log lines).
* No idempotent-relock (§6-B2 strict-monotonic pin).
* No v0 backward-compatibility (this is v1.0 first log).
"""

from __future__ import annotations

import json
import os
import typing
from collections.abc import Iterator
from pathlib import Path
from types import MappingProxyType
from typing import Any, Final, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.marcus.lesson_plan.event_type_registry import (
    EVENT_PRE_PACKET_SNAPSHOT,
    RESERVED_LOG_EVENT_TYPES,
)
from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.schema import StaleRevisionError

# ---------------------------------------------------------------------------
# Project-root resolution — cwd-independent LOG_PATH (G6 MF-BH-1)
# ---------------------------------------------------------------------------


def _find_project_root() -> Path:
    """Walk up from this file looking for a project-root marker.

    Returns the first ancestor containing either ``pyproject.toml`` or a
    ``.git/`` directory. Falls back to the module's grandparent directory
    (``marcus/lesson_plan/`` → repo root) if no marker is found.

    Pinned at module import time to keep :data:`LOG_PATH` cwd-independent
    across interpreters launched from arbitrary working directories.
    """
    here = Path(__file__).resolve().parent
    for candidate in [here, *here.parents]:
        if (candidate / "pyproject.toml").exists() or (candidate / ".git").exists():
            return candidate
    # Fallback: marcus/lesson_plan/log.py → marcus/lesson_plan/ → marcus/ → repo
    return Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Constants — single source of truth for named mandatory events + writer set
# ---------------------------------------------------------------------------


LOG_PATH: Path = _find_project_root() / "state" / "runtime" / "lesson_plan_log.jsonl"
"""Canonical runtime path for the append-only lesson-plan log (AC-B.1 / AC-C.4).

Resolved to an absolute path at module import time via
:func:`_find_project_root` (walks up from ``__file__`` for a ``pyproject.toml``
or ``.git/`` marker) — cwd-independent per G6 MF-BH-1.

Tests MUST override via :class:`LessonPlanLog` constructor ``path=`` parameter
(e.g. ``LessonPlanLog(path=tmp_path / "log.jsonl")``). Module-level
monkeypatching of ``LOG_PATH`` has no effect on instances already constructed
(see :meth:`LessonPlanLog.__init__`) per G6 SF-EC-4.
"""


WriterIdentity = Literal["marcus-orchestrator", "marcus-intake"]
"""Closed set of permitted writer identities (AC-B.3 / AC-C.5).

Widening requires (a) R1/R2-equivalent ruling amendment, (b)
SCHEMA_CHANGELOG major-version bump, (c) explicit migration-path AC on
whatever story proposes the widening. No backdoor.
"""


NAMED_MANDATORY_EVENTS: frozenset[str] = RESERVED_LOG_EVENT_TYPES
"""Alias of :data:`RESERVED_LOG_EVENT_TYPES` — write-time gate on
``append_event`` (AC-B.8).

Single source of truth, two naming surfaces: 31-1 registered the six named
mandatory event_types in
:data:`marcus.lesson_plan.event_type_registry.RESERVED_LOG_EVENT_TYPES`; 31-2
aliases them here to keep the write-path readable. AC-T.7 asserts set
equality; M-3 asserts immutability via the underlying frozenset type.
"""


_WRITER_EVENT_MATRIX_UNDERLYING: dict[str, frozenset[WriterIdentity]] = {
    "plan_unit.created": frozenset({"marcus-orchestrator"}),
    "scope_decision.set": frozenset({"marcus-orchestrator"}),
    "scope_decision_transition": frozenset({"marcus-orchestrator"}),
    "plan.locked": frozenset({"marcus-orchestrator"}),
    "fanout.envelope.emitted": frozenset({"marcus-orchestrator"}),
    "pre_packet_snapshot": frozenset({"marcus-orchestrator", "marcus-intake"}),
    # Story 29-1 — fit-report emissions are Marcus-Orchestrator-only.
    # Irene (29-2) produces FitReport instances and hands them to Marcus via
    # the orchestration seam; Irene MUST NOT emit directly. See
    # marcus/lesson_plan/fit_report.py docstring for the canonical-caller
    # invariant (AC-B.5.1).
    "fit_report.emitted": frozenset({"marcus-orchestrator"}),
    # Registered by 30-3b retroactively (G6-Opus party-mode 2026-04-19 follow-on):
    # dial tuning is Orchestrator-only, just like scope_decision.set, but is
    # a distinct semantic event so log readers can disambiguate.
    "dials.tuned": frozenset({"marcus-orchestrator"}),
}

WRITER_EVENT_MATRIX: typing.Mapping[str, frozenset[WriterIdentity]] = MappingProxyType(
    _WRITER_EVENT_MATRIX_UNDERLYING
)
"""AC-B.3 single-writer enforcement matrix.

The ``pre_packet_snapshot`` row is the SOLE case where ``marcus-intake`` may
successfully invoke ``append_event`` — all other five events are Marcus-
Orchestrator-only. AC-T.3 parametrizes the full (2 × 6 = 12) Cartesian
product and asserts accept-or-reject per row.

**Tamper-resistance (party-mode 2026-04-19 follow-on, Blind#15):** wrapped
in :class:`types.MappingProxyType` so callers cannot widen writer permissions
at runtime via direct dict mutation. The inner ``frozenset`` values were
already immutable; this wrap closes the outer-dict bypass. The single-writer
rule (R1 ruling amendment 13) is foundational — the matrix that enforces
it must be tamper-resistant.
"""


# ---------------------------------------------------------------------------
# Module-level import-time safety net (G6 SF-BH-7)
# ---------------------------------------------------------------------------
#
# If a future dev-agent adds a new event_type to NAMED_MANDATORY_EVENTS but
# forgets to update WRITER_EVENT_MATRIX (or vice versa), importing this module
# raises AssertionError immediately rather than surfacing as a KeyError at
# runtime. The sibling test
# ``tests/test_lesson_plan_log_named_events.py``
# covers the same invariant via parametrized check; this module-level
# assertion is belt-and-suspenders for early detection at import time.

assert frozenset(WRITER_EVENT_MATRIX.keys()) == NAMED_MANDATORY_EVENTS, (
    "WRITER_EVENT_MATRIX keys must equal NAMED_MANDATORY_EVENTS; "
    "if you added a new event, update BOTH."
)


# ---------------------------------------------------------------------------
# Named event-type constants (single-source-of-truth; 30-1 G6-D2 closure)
# ---------------------------------------------------------------------------
#
# Per 30-1 G6-D2 deferral ("apply W-3-style single-source-of-truth pattern
# as a future hardening"), named constants are exported for callers that
# would otherwise hard-code the raw string literals. The constants are the
# ONE canonical source for each event-type name; WRITER_EVENT_MATRIX and
# NAMED_MANDATORY_EVENTS use the same literals by construction, pinned by
# the import-time assertion above.

PRE_PACKET_SNAPSHOT_EVENT_TYPE: Final[str] = EVENT_PRE_PACKET_SNAPSHOT
"""Event-type string for pre-packet snapshot emissions (30-2b, R1 amendment 13).

Callers constructing a :class:`EventEnvelope` or gating an event_type in
:mod:`marcus.orchestrator.write_api` MUST reference this constant rather
than hard-coding the literal. Pattern precedent: 29-1's
:data:`marcus.lesson_plan.fit_report.FIT_REPORT_EMITTED_EVENT_TYPE`.

**Single source of truth:** value is re-exported from
:data:`marcus.lesson_plan.event_type_registry.EVENT_PRE_PACKET_SNAPSHOT`
(party-mode 2026-04-19 consolidation closing 30-1 G6-D2 cross-story slip).
The registry is the canonical home for log event-type literals; this module
binds the same value for callers already importing from ``log``.
"""

assert PRE_PACKET_SNAPSHOT_EVENT_TYPE in NAMED_MANDATORY_EVENTS, (
    "PRE_PACKET_SNAPSHOT_EVENT_TYPE must be in NAMED_MANDATORY_EVENTS."
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class UnauthorizedWriterError(PermissionError):
    """Raised by :meth:`LessonPlanLog.append_event` when a writer identity is
    not permitted to write the presented ``event_type`` per
    :data:`WRITER_EVENT_MATRIX` (AC-B.3 / R1 ruling amendment 13)."""


class StalePlanRefError(ValueError):
    """Raised by :func:`assert_plan_fresh` when the envelope's plan-ref
    (revision and/or digest) does not match the latest values on the log
    (AC-B.5, R2 M-1 axis-named matrix)."""


class LogCorruptError(Exception):
    """Raised by :meth:`LessonPlanLog.read_events` when the underlying
    JSONL file contains a line that cannot be parsed (malformed JSON) or
    fails :class:`EventEnvelope` validation (G6 MF-EC-1).

    Message includes the line-number and file path for actionable diagnosis.
    Wraps the original ``json.JSONDecodeError`` or ``pydantic.ValidationError``
    via ``__cause__``.
    """


# ---------------------------------------------------------------------------
# Path-safety helper (G6 SF-EC-9)
# ---------------------------------------------------------------------------


def _validate_repo_relative_path(value: str, *, field_name: str) -> str:
    """Reject absolute paths + parent-directory traversal segments.

    Enforces that artifact paths are repo-relative (G6 SF-EC-9). Rejects
    - values starting with ``/`` or ``\\`` (POSIX absolute or UNC prefix)
    - values containing a ``:`` followed by a slash (Windows drive root)
    - values containing ``..`` path segments (traversal)

    Used by :class:`SourceRef.path` and
    :class:`PrePacketSnapshotPayload.pre_packet_artifact_path`.
    """
    if value.startswith(("/", "\\")):
        raise ValueError(
            f"{field_name} must be repo-relative; absolute paths forbidden. Got {value!r}"
        )
    # Windows drive-letter check: 'C:/...', 'C:\\...'
    if len(value) >= 3 and value[1] == ":" and value[2] in ("/", "\\"):
        raise ValueError(
            f"{field_name} must be repo-relative; Windows absolute paths forbidden. "
            f"Got {value!r}"
        )
    # Parent-traversal check — any path segment equal to ".." is a traversal attempt.
    parts = value.replace("\\", "/").split("/")
    if ".." in parts:
        raise ValueError(
            f"{field_name} must be repo-relative; '..' traversal segments forbidden. "
            f"Got {value!r}"
        )
    return value


# ---------------------------------------------------------------------------
# Payload shapes (AC-B.7 / AC-B.11)
# ---------------------------------------------------------------------------


class SourceRef(BaseModel):
    """SME-input source reference (AC-B.7).

    Shipped at first-use site in ``log.py``. If 30-4 or a downstream story
    needs to reuse ``SourceRef``, the model migrates to ``schema.py`` via a
    minor SCHEMA_CHANGELOG bump. First-use-site placement avoids premature
    abstraction.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    source_id: str = Field(..., min_length=1)
    path: str | None = Field(
        None,
        description="Filesystem path to source (repo-relative); None when source has no file.",
    )
    content_digest: str = Field(..., min_length=1)

    @field_validator("path")
    @classmethod
    def _validate_path_repo_relative(cls, value: str | None) -> str | None:
        """G6 SF-EC-9: reject absolute paths + ``..`` traversal segments."""
        if value is None:
            return value
        return _validate_repo_relative_path(value, field_name="SourceRef.path")


class PrePacketSnapshotPayload(BaseModel):
    """Payload shape for ``pre_packet_snapshot`` events (AC-B.7 / Winston R1).

    Carries enough state for 30-4 fanout to reconstruct Intake-era context
    from the log alone. No ``read_from_marcus_intake_state()`` path exists.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    sme_refs: list[SourceRef] = Field(
        ...,
        min_length=1,
        description=(
            "SME input pointers captured at pre-packet snapshot time. "
            "MUST be non-empty — a pre-packet without any SME input is a "
            "contract violation (G6 SF-EC-8)."
        ),
    )
    ingestion_digest: str = Field(
        ...,
        min_length=1,
        description="sha256 of the raw ingestion bundle.",
    )
    pre_packet_artifact_path: str = Field(
        ...,
        min_length=1,
        description="Filesystem path to pre-packet artifact (repo-relative).",
    )
    step_03_extraction_checksum: str = Field(
        ...,
        min_length=1,
        description="Checksum of step-03 extraction output.",
    )

    @field_validator("pre_packet_artifact_path")
    @classmethod
    def _validate_artifact_path_repo_relative(cls, value: str) -> str:
        """G6 SF-EC-9: reject absolute paths + ``..`` traversal segments."""
        return _validate_repo_relative_path(
            value, field_name="PrePacketSnapshotPayload.pre_packet_artifact_path"
        )


class PlanLockedPayload(BaseModel):
    """Payload shape for ``plan.locked`` events (AC-B.11).

    ``lesson_plan_revision`` lives on the envelope itself (per 31-1
    ``EventEnvelope.plan_revision``); the digest lives in the payload
    because it is event-specific, not envelope-generic.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    lesson_plan_digest: str = Field(
        ...,
        min_length=1,
        description="sha256 from compute_digest(LessonPlan).",
    )


# ---------------------------------------------------------------------------
# Canonical JSON helpers
# ---------------------------------------------------------------------------


def _json_default(value: Any) -> Any:
    """JSON encoder fallback for non-native types.

    Envelopes are serialized via ``model_dump(mode="json")`` upstream, which
    already converts :class:`datetime`/:class:`date` to ISO strings. Any
    value reaching this fallback is therefore an unsupported type — raise
    :class:`TypeError` with an explanatory message (G6 SF-BH-6).
    """
    raise TypeError(f"Cannot serialize {type(value).__name__} for log append")


def _serialize_envelope(envelope: EventEnvelope) -> str:
    """Serialize an envelope to a single canonical-JSON line (no trailing newline)."""
    payload = envelope.model_dump(mode="json")
    return json.dumps(
        payload,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
        default=_json_default,
    )


# ---------------------------------------------------------------------------
# LessonPlanLog
# ---------------------------------------------------------------------------


class LessonPlanLog:
    """Append-only JSONL log for Lesson Plan events (AC-B.1 / AC-B.2 / AC-B.4).

    Single-process single-writer. The ``append_event`` method is the ONLY
    write path for the log file; downstream consumers MUST read via
    ``read_events`` (AC-C.8). No in-place edits, no delete, no compaction.
    """

    def __init__(self, path: Path | None = None) -> None:
        """Construct a log against ``path`` (default: :data:`LOG_PATH`).

        The default :data:`LOG_PATH` is captured at ``__init__`` time. Module-
        level mutation of :data:`LOG_PATH` after construction does NOT affect
        existing instances; pass a per-instance ``path=`` to override (G6
        SF-EC-4). Tests MUST pass a per-test ``tmp_path`` to avoid polluting
        the runtime log; production code calls ``LessonPlanLog()`` with no
        arguments.
        """
        self._path: Path = path if path is not None else LOG_PATH

    @property
    def path(self) -> Path:
        """Return the filesystem path backing this log instance."""
        return self._path

    # --- Write path ---------------------------------------------------

    def append_event(
        self,
        envelope: EventEnvelope,
        writer_identity: WriterIdentity,
    ) -> None:
        """Append a single event envelope to the log (AC-B.2 / AC-B.9).

        Validation order:
            1. ``envelope`` is a valid :class:`EventEnvelope`
               (Pydantic already validated at construction; defensive
               isinstance check here).
            2. ``envelope.event_type`` is in
               :data:`NAMED_MANDATORY_EVENTS`. Unknown event_types are
               REJECTED (governance artifact, not extensibility surface).
            3. ``writer_identity`` is a recognized :data:`WriterIdentity`
               value; unrecognized values raise :class:`ValueError` to
               distinguish typos from permission denials (G6 SF-EC-3).
            4. ``writer_identity`` is permitted to write
               ``envelope.event_type`` per :data:`WRITER_EVENT_MATRIX`.
            5. For ``event_type == "plan.locked"`` ONLY: revision is
               strictly greater than ``self.latest_plan_revision()``.
               Non-``plan.locked`` events bypass this check per R2 M-2.

        Atomic write: one canonical-JSON line + ``\\n`` + fsync. Parent
        directory is created if absent.
        """
        # --- Validation step 1: envelope type guard -----------------
        if not isinstance(envelope, EventEnvelope):
            raise TypeError(
                f"append_event expects EventEnvelope; got {type(envelope).__name__}"
            )

        # --- Validation step 2: event_type in NAMED_MANDATORY_EVENTS -
        if envelope.event_type not in NAMED_MANDATORY_EVENTS:
            raise ValueError(
                f"event_type {envelope.event_type!r} not in "
                f"NAMED_MANDATORY_EVENTS; log is a governance artifact — "
                f"extend RESERVED_LOG_EVENT_TYPES via schema version bump"
            )

        # --- Validation step 3: writer_identity is a recognized value -
        # G6 SF-EC-3: Literal is static-only at runtime; a typo like
        # "marcus_orchestrator" (underscore) would otherwise slip through to
        # the matrix lookup and raise UnauthorizedWriterError, conflating
        # "typo" with "auth-fail". Raise ValueError explicitly to separate.
        recognized_identities = typing.get_args(WriterIdentity)
        if writer_identity not in recognized_identities:
            raise ValueError(
                f"writer_identity {writer_identity!r} is not a recognized "
                f"WriterIdentity; must be one of {sorted(recognized_identities)}"
            )

        # --- Validation step 4: writer_identity permitted? ----------
        permitted = WRITER_EVENT_MATRIX[envelope.event_type]
        if writer_identity not in permitted:
            raise UnauthorizedWriterError(
                f"writer_identity={writer_identity!r} is not permitted to "
                f"write event_type={envelope.event_type!r}; permitted: "
                f"{sorted(permitted)}"
            )

        # --- Validation step 5: monotonic-revision on plan.locked ---
        # R2 M-2 — scope is PLAN.LOCKED ONLY. Non-plan.locked events at
        # stale revision are LEGAL (interleaved writes ordering).
        if envelope.event_type == "plan.locked":
            current = self.latest_plan_revision()
            if envelope.plan_revision <= current:
                raise StaleRevisionError(
                    f"plan.locked revision {envelope.plan_revision} is not "
                    f"greater than current latest_plan_revision()={current} "
                    f"(strict-monotonic pin per §6-B2; idempotent-relock "
                    f"is out-of-scope for 31-2)"
                )

        # --- Atomic append: open(a) + write + flush + fsync ---------
        line = _serialize_envelope(envelope) + "\n"
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a", encoding="utf-8") as fh:
            fh.write(line)
            fh.flush()
            os.fsync(fh.fileno())

    # --- Read path ----------------------------------------------------

    def read_events(
        self,
        since_revision: int | None = None,
        event_types: set[str] | None = None,
    ) -> Iterator[EventEnvelope]:
        """Yield envelopes from the log (AC-B.4).

        * ``since_revision=None`` yields ALL events; otherwise yields events
          where ``envelope.plan_revision >= since_revision``.
        * ``event_types=None`` yields ALL event_types; otherwise yields
          events whose ``event_type`` is in the requested set.
        * Ordering: insertion order (file-offset order), stable across reads.
        * Each yielded envelope is a freshly-constructed Pydantic instance;
          mutating a yielded envelope does not affect subsequent reads.

        Raises :class:`LogCorruptError` (G6 MF-EC-1) when a line cannot be
        parsed as JSON or fails :class:`EventEnvelope` validation. The error
        message names the line-number and file path for actionable diagnosis.

        **Snapshot semantics (party-mode 2026-04-19, Edge#7):** the iterator
        opens the file once at first ``next(...)`` and reads line-by-line.
        Any ``append_event`` call by another writer (or this writer) after the
        iterator opens is NOT guaranteed visible — re-call :meth:`read_events`
        to see appended events. This snapshot contract keeps the read API
        deterministic for any single drain.

        **Iterator-drain contract (party-mode 2026-04-19, Blind#8):** to
        guarantee prompt file-handle release, callers should fully drain the
        iterator (``for env in log.read_events(...): ...``) or wrap it in
        :class:`contextlib.closing` for partial consumption. CPython's
        refcount GC closes the underlying file when the generator falls out
        of scope, but PyPy / freethreading runtimes may delay closure under
        GC pressure — explicit draining or ``closing(...)`` is the portable
        guarantee.
        """
        if not self._path.exists():
            return
        with self._path.open("r", encoding="utf-8") as fh:
            for line_num, raw_line in enumerate(fh, start=1):
                stripped = raw_line.strip()
                if not stripped:
                    continue
                try:
                    payload = json.loads(stripped)
                except json.JSONDecodeError as exc:
                    raise LogCorruptError(
                        f"Log corrupted at line {line_num}: {exc}. "
                        f"Path: {self._path}"
                    ) from exc
                try:
                    envelope = EventEnvelope.model_validate(payload)
                except ValidationError as exc:
                    raise LogCorruptError(
                        f"Log corrupted at line {line_num}: envelope "
                        f"validation failed: {exc}. Path: {self._path}"
                    ) from exc
                if since_revision is not None and envelope.plan_revision < since_revision:
                    continue
                if event_types is not None and envelope.event_type not in event_types:
                    continue
                yield envelope

    # --- Helpers ------------------------------------------------------

    def _iter_all_lines(self) -> list[str]:
        """Read all non-empty lines from the log file into memory.

        Used by reverse-scanning helpers :meth:`latest_plan_revision` and
        :meth:`latest_plan_digest` (G6 MF-BH-2). Returns an empty list if
        the log file does not yet exist.
        """
        if not self._path.exists():
            return []
        with self._path.open("r", encoding="utf-8") as fh:
            return [line for line in fh if line.strip()]

    def latest_plan_revision(self) -> int:
        """Return the most-recent ``plan.locked`` event's ``plan_revision``.

        Returns ``0`` if no ``plan.locked`` event exists yet (bootstrap
        case — revision numbering starts at 1 for the first lock).

        Reverse-scans the log file from end to start (G6 MF-BH-2): the
        LATEST ``plan.locked`` line is authoritative by strict-monotonic
        invariant (AC-B.6), so the first match from the tail wins.
        """
        lines = self._iter_all_lines()
        for line_num, raw_line in enumerate(reversed(lines), start=1):
            stripped = raw_line.strip()
            actual_line_num = len(lines) - line_num + 1
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise LogCorruptError(
                    f"Log corrupted at line {actual_line_num}: {exc}. "
                    f"Path: {self._path}"
                ) from exc
            try:
                envelope = EventEnvelope.model_validate(payload)
            except ValidationError as exc:
                raise LogCorruptError(
                    f"Log corrupted at line {actual_line_num}: envelope "
                    f"validation failed: {exc}. Path: {self._path}"
                ) from exc
            if envelope.event_type == "plan.locked":
                return envelope.plan_revision
        return 0

    def latest_plan_digest(self) -> str | None:
        """Return the digest from the most-recent ``plan.locked`` event's payload.

        Returns ``None`` if no ``plan.locked`` event exists yet (bootstrap
        case). Reads the ``lesson_plan_digest`` field from the event payload
        (shape-pinned on :class:`PlanLockedPayload` per AC-B.11).

        Reverse-scans the log file (G6 MF-BH-2). Per G6 MF-BH-3, a
        ``plan.locked`` event whose payload fails :class:`PlanLockedPayload`
        validation raises :class:`LogCorruptError` at read time — silently
        returning a stale digest (earlier revision's) would be drift. Since
        :class:`PlanLockedPayload` is enforced on the WRITE-side (AC-B.11)
        and the payload-validation gate here is on the READ-side, only a
        corrupted file can trigger this branch.
        """
        lines = self._iter_all_lines()
        for line_num, raw_line in enumerate(reversed(lines), start=1):
            stripped = raw_line.strip()
            actual_line_num = len(lines) - line_num + 1
            try:
                payload = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise LogCorruptError(
                    f"Log corrupted at line {actual_line_num}: {exc}. "
                    f"Path: {self._path}"
                ) from exc
            try:
                envelope = EventEnvelope.model_validate(payload)
            except ValidationError as exc:
                raise LogCorruptError(
                    f"Log corrupted at line {actual_line_num}: envelope "
                    f"validation failed: {exc}. Path: {self._path}"
                ) from exc
            if envelope.event_type != "plan.locked":
                continue
            # G6 MF-BH-3: strict — plan.locked payload MUST validate as
            # PlanLockedPayload. A silently-missing `lesson_plan_digest`
            # would return a stale digest from an older revision.
            try:
                validated = PlanLockedPayload.model_validate(envelope.payload)
            except ValidationError as exc:
                raise LogCorruptError(
                    f"Log corrupted at line {actual_line_num}: plan.locked "
                    f"payload failed PlanLockedPayload validation: {exc}. "
                    f"Path: {self._path}"
                ) from exc
            return validated.lesson_plan_digest
        return None


# ---------------------------------------------------------------------------
# Staleness detector (AC-B.5; R2 M-1 axis-named matrix)
# ---------------------------------------------------------------------------


def assert_plan_fresh(
    envelope: Any,
    *,
    log: LessonPlanLog | None = None,
) -> None:
    """Raise :class:`StalePlanRefError` when envelope plan-ref is stale (AC-B.5).

    The envelope is "fresh" when BOTH:

    * ``envelope.lesson_plan_revision == log.latest_plan_revision()``
    * ``envelope.lesson_plan_digest == log.latest_plan_digest()``

    Semantics:

    * Bootstrap case: empty log returns ``latest_plan_revision()=0`` and
      ``latest_plan_digest()=None``. An envelope claiming ``revision=0`` and
      ``digest=""`` (or ``digest=None``) passes (documented empty-log
      bootstrap — G6 MF-BH-4). Any other combination against an empty log
      raises :class:`StalePlanRefError`.
    * R2 M-1 axis-named error message: the message names EXPLICITLY whether
      ``revision``, ``digest``, or ``both`` axes triggered the raise. This
      gives operators + downstream audit code an unambiguous signal.

    Duck-typed input: the envelope need only expose ``lesson_plan_revision:
    int`` and ``lesson_plan_digest: str`` attributes. 32-2 coverage manifest
    pins the field shape across all envelope types 05→13.

    The ``log`` keyword argument is provided for test isolation (pass a
    ``LessonPlanLog(path=tmp_path / "log.jsonl")``); production call-sites
    pass no argument and accept the default ``LessonPlanLog()``.
    """
    resolved_log = log if log is not None else LessonPlanLog()
    log_rev = resolved_log.latest_plan_revision()
    log_digest = resolved_log.latest_plan_digest()

    # Duck-typed field access.
    try:
        env_rev = envelope.lesson_plan_revision
        env_digest = envelope.lesson_plan_digest
    except AttributeError as exc:
        raise AttributeError(
            "assert_plan_fresh expects envelope to expose "
            "'lesson_plan_revision' and 'lesson_plan_digest' attributes"
        ) from exc

    # Bootstrap empty-log case (G6 MF-BH-4): revision=0 AND digest in
    # {"", None} permitted. The envelope may carry either sentinel to
    # signal "no prior lock yet" since PlanLockedPayload requires
    # min_length=1 at write time and latest_plan_digest() returns None for
    # an empty log at read time.
    if log_rev == 0 and log_digest is None:
        if env_rev == 0 and env_digest in ("", None):
            return
        # Fall through to axis-named raise below.
        effective_log_digest: str | None = None
    else:
        effective_log_digest = log_digest

    rev_match = env_rev == log_rev
    digest_match = env_digest == effective_log_digest

    if rev_match and digest_match:
        return

    # R2 M-1 — axis-named message.
    mismatches: list[str] = []
    if not rev_match:
        mismatches.append(
            f"revision mismatch (envelope={env_rev}, log={log_rev})"
        )
    if not digest_match:
        mismatches.append(
            f"digest mismatch (envelope={env_digest!r}, log={effective_log_digest!r})"
        )
    raise StalePlanRefError(
        "StalePlanRefError: " + "; ".join(mismatches)
    )


__all__ = [
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
]
