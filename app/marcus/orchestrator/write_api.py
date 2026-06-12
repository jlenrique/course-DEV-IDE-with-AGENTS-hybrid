"""Single-writer entry point for Marcus-Orchestrator writes to the Lesson Plan log.

This module is the ONE sanctioned caller-facing surface for appending
``pre_packet_snapshot`` events to the 31-2 Lesson Plan log. It enforces
the single-writer invariant (R1 amendment 13, Quinn) at entry-point time
with a caller-scoped error message, giving callers a cleaner error
surface than the 31-2 last-mile ``append_event`` check.

Dev-facing contract
-------------------

Callers pass a pre-validated :class:`EventEnvelope` instance + the
orchestrator writer identity. The function:

1. **Type-gates** the envelope (``isinstance`` check; raises
   :class:`TypeError` on dict-sneaks-past-type-hint).
2. **Writer-gates** the caller (``writer == ORCHESTRATOR_MODULE_IDENTITY``;
   raises :class:`UnauthorizedFacadeCallerError` on mismatch). **Fires
   BEFORE** the event-type check so unauthorized callers learn nothing
   about envelope-shape validity (Q-1 precedence rider).
3. **Event-gates** the envelope type (``event_type == "pre_packet_snapshot"``;
   raises :class:`ValueError` on mismatch).
4. Delegates to :meth:`app.marcus.lesson_plan.log.LessonPlanLog.append_event`.

Idempotency (AC-B.3.1)
----------------------

This function does NOT re-trigger :meth:`EventEnvelope.model_validate` on
an already-validated instance. Two back-to-back calls with identical
envelopes produce TWO distinct log entries (no silent dedup).

Maya-facing note
----------------

Maya never calls this function directly. She interacts with the Marcus
facade; the facade routes artifacts to this function internally.

Even in error paths, the exception ``__str__()`` returns a Maya-safe
generic message. Hyphenated internal-routing tokens live on
attribute-scoped fields (``.offending_writer``, ``.debug_detail``) so
they do not leak via ``logger.error(str(e))``. See
:class:`UnauthorizedFacadeCallerError`.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import PRE_PACKET_SNAPSHOT_EVENT_TYPE, LessonPlanLog
from app.marcus.orchestrator import ORCHESTRATOR_MODULE_IDENTITY

if TYPE_CHECKING:
    from app.marcus.lesson_plan.log import WriterIdentity


logger = logging.getLogger(__name__)

# Maya-safe generic message honoring the facade Voice Register (first person
# singular, present tense, invitation to proceed). Callers observe ONLY this
# string via ``str(err)`` / ``err.args[0]``. Offending-writer detail lives on
# ``err.offending_writer`` and ``err.debug_detail`` attributes.
_MAYA_SAFE_UNAUTHORIZED_MESSAGE: str = (
    "Sorry — I hit an internal hiccup. Give me a moment and try again?"
)
# 30-1 G6-D2 closure: single-source-of-truth — reference the named constant
# exported from app.marcus.lesson_plan.log rather than hard-coding the literal.
_PRE_PACKET_SNAPSHOT_EVENT_TYPE: str = PRE_PACKET_SNAPSHOT_EVENT_TYPE


class UnauthorizedFacadeCallerError(PermissionError):
    """Raised when a non-Orchestrator caller invokes the write API.

    The exception's ``str()`` form is Maya-safe (generic message with no
    sub-identity tokens). Offending writer + dev-readable detail are
    attribute-scoped so that a stray ``logger.error(str(e))`` upstream
    cannot leak "marcus-intake" or similar into a Maya-visible channel.

    Attributes:
        offending_writer: The writer identity string the caller passed.
        debug_detail: Dev-facing string naming both offending and
            expected writer identities. Consumed by tests + structured
            debug logging; never auto-stringified.
    """

    __slots__ = ("offending_writer", "debug_detail")

    def __init__(self, offending_writer: str) -> None:
        super().__init__(_MAYA_SAFE_UNAUTHORIZED_MESSAGE)
        self.offending_writer: str = offending_writer
        self.debug_detail: str = (
            f"Unauthorized write_api caller: {offending_writer!r} "
            f"(expected {ORCHESTRATOR_MODULE_IDENTITY!r})"
        )


def emit_pre_packet_snapshot(
    envelope: EventEnvelope,
    *,
    writer: WriterIdentity,
    log: LessonPlanLog | None = None,
) -> None:
    """Append a ``pre_packet_snapshot`` envelope to the Lesson Plan log.

    Args:
        envelope: Pre-validated :class:`EventEnvelope` with
            ``event_type == "pre_packet_snapshot"``.
        writer: MUST be ``ORCHESTRATOR_MODULE_IDENTITY``
            (``"marcus-orchestrator"``). Non-Orchestrator callers raise
            :class:`UnauthorizedFacadeCallerError` with a Maya-safe
            message.
        log: Optional :class:`LessonPlanLog` instance for test isolation
            (per-test ``tmp_path``). Production code passes ``None`` and
            the default-path log is constructed.

    Raises:
        TypeError: If ``envelope`` is not an :class:`EventEnvelope`
            instance (Q-3 type-gate rider — prevents dict-sneaks-past).
        UnauthorizedFacadeCallerError: If ``writer`` is not
            ``ORCHESTRATOR_MODULE_IDENTITY``. Fires BEFORE event-type
            check (Q-1 precedence rider — security-forward default).
        ValueError: If ``envelope.event_type`` is not
            ``"pre_packet_snapshot"``.
    """
    # Step 1 (Q-3 rider): type-gate before any further inspection.
    if not isinstance(envelope, EventEnvelope):
        raise TypeError(
            f"emit_pre_packet_snapshot expects an EventEnvelope instance; "
            f"got {type(envelope).__name__}"
        )

    # Step 2 (Q-1 rider): writer-check fires BEFORE event-type check.
    # Security-forward default — unauthorized callers learn nothing about
    # envelope-shape validity.
    if writer != ORCHESTRATOR_MODULE_IDENTITY:
        raise UnauthorizedFacadeCallerError(offending_writer=writer)

    # Step 3: event-type check.
    if envelope.event_type != _PRE_PACKET_SNAPSHOT_EVENT_TYPE:
        raise ValueError(
            f"emit_pre_packet_snapshot expects event_type="
            f"{_PRE_PACKET_SNAPSHOT_EVENT_TYPE!r}; "
            f"got {envelope.event_type!r}"
        )

    # Step 4: delegate to 31-2 log. No re-validation (AC-B.3.1 idempotency).
    # The ``log`` kwarg is a test-isolation convenience — production callers
    # pass a shared ``LessonPlanLog`` instance configured for the run. When
    # ``log=None`` we fall back to a fresh default-path instance and emit a
    # warning; this follows the 29-1 precedent (see emit_fit_report).
    if log is None:
        logger.warning(
            "emit_pre_packet_snapshot called with log=None; falling back to "
            "default LessonPlanLog(). Production callers should pass a "
            "shared log instance."
        )
        target_log = LessonPlanLog()
    else:
        target_log = log
    target_log.append_event(envelope, writer)


# ---- merged from app-side write_api.py test-state-machine helper (S2 merge 2026-05-07) ----
# This is a SEPARATE concern from the production single-writer rule above (R1 amendment 13;
# Quinn). The helper exercises a state-machine append surface used by app-namespace tests
# (`app.marcus.intake.extract_pre_packet`); it does NOT bypass the single-writer rule for
# Lesson Plan log events — those go exclusively through `emit_pre_packet_snapshot` above.

def append_event(state, event):  # type: ignore[no-untyped-def]
    """Append a generic event dict to a state-machine `events` attribute (test helper).

    NOT a production write surface for Lesson Plan log events.
    Production callers use `emit_pre_packet_snapshot` above (single-writer-gated).
    """
    events = getattr(state, "events", None)
    if events is None:
        events = []
        state.events = events
    events.append(event)
    return event


__all__ = ["UnauthorizedFacadeCallerError", "emit_pre_packet_snapshot", "append_event"]
