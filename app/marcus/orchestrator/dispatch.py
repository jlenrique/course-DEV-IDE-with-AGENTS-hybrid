"""Orchestrator-side dispatch seam for Intake-originated pre-packet emissions.

Maya-facing note
----------------

Maya never calls this module directly. It is an internal routing seam on
the Marcus-Orchestrator half of the duality. Intake builds a
``pre_packet_snapshot`` envelope but does NOT emit it; the envelope lands
in the Lesson Plan log via this module's
:func:`dispatch_intake_pre_packet`, which is the SOLE caller of
:func:`marcus.orchestrator.write_api.emit_pre_packet_snapshot` for
Intake-originated flows (Story 30-2b).

Dev-facing discipline note
--------------------------

* **Single-writer rule (R1 amendment 13, Quinn).** The write API enforces
  that every call uses ``writer=ORCHESTRATOR_MODULE_IDENTITY``; this
  module is the ONLY place in :mod:`marcus.orchestrator` (outside
  :mod:`marcus.orchestrator.write_api`) that invokes that API. The AST
  contract at ``tests/contracts/test_30_2b_dispatch_monopoly.py`` asserts
  the invariant at test time.
* **No envelope construction here.** This dispatcher receives a
  pre-built, pre-validated :class:`EventEnvelope` from Intake and
  forwards it verbatim. It does not read bundle state, does not choose
  the event_type, does not mutate the envelope. Keeping the dispatch
  body to a single delegation preserves the Intake/Orchestrator seam.
* **No redundant checks.** Writer-identity, event-type, and
  envelope-instance checks all live in
  :mod:`marcus.orchestrator.write_api`. Duplicating them here would
  create a second failure surface with subtly different error messages.

Why a dispatch seam (vs Intake importing ``emit_pre_packet_snapshot`` directly)
-------------------------------------------------------------------------------

Intake MUST NOT import from :mod:`marcus.orchestrator.write_api` —
that would reverse the Marcus-duality import-order rule and couple the
Intake package to the write-API's exception surface. The dispatch
callable is passed INTO Intake via dependency injection (see the
``dispatch`` kwarg on
:func:`marcus.intake.pre_packet.prepare_and_emit_irene_packet`), which
keeps the two packages independently importable and gives tests a single
injection point for fakes.
"""

from __future__ import annotations

import logging
from typing import Final

from app.marcus.lesson_plan.events import EventEnvelope
from app.marcus.lesson_plan.log import LessonPlanLog
from app.marcus.orchestrator import ORCHESTRATOR_MODULE_IDENTITY
from app.marcus.orchestrator.write_api import emit_pre_packet_snapshot

logger = logging.getLogger(__name__)


def dispatch_intake_pre_packet(
    envelope: EventEnvelope,
    *,
    log: LessonPlanLog | None = None,
) -> None:
    """Append an Intake-originated ``pre_packet_snapshot`` envelope to the log.

    Sole Marcus-Orchestrator-side caller of
    :func:`marcus.orchestrator.write_api.emit_pre_packet_snapshot` for
    Intake-originated flows. Passes ``writer=ORCHESTRATOR_MODULE_IDENTITY``
    per the single-writer rule (R1 amendment 13).

    Args:
        envelope: Pre-validated :class:`EventEnvelope` with
            ``event_type == "pre_packet_snapshot"``. Intake constructs it.
        log: Optional :class:`LessonPlanLog` for test isolation. Production
            callers pass ``None`` and the write API's default-path log is
            constructed; the write API emits a :mod:`logging.WARNING` in
            that case so test leakage into the runtime log is visible in
            CI output (29-1 precedent).

    Raises:
        TypeError: If ``envelope`` is not an :class:`EventEnvelope`
            instance (surfaced by the write API).
        ValueError: If ``envelope.event_type`` is not
            ``"pre_packet_snapshot"`` (surfaced by the write API).
        UnauthorizedFacadeCallerError: Never raised in practice because
            this function always passes
            ``writer=ORCHESTRATOR_MODULE_IDENTITY``; documented here so
            callers know the exception lives on the write-API surface.
    """
    emit_pre_packet_snapshot(
        envelope,
        writer=ORCHESTRATOR_MODULE_IDENTITY,
        log=log,
    )


def dispatch_orchestrator_event(
    envelope: EventEnvelope,
    *,
    log: LessonPlanLog | None = None,
) -> None:
    """Append an Orchestrator-originated event envelope to the log.

    Sole non-write_api caller of :meth:`LessonPlanLog.append_event` for
    the orchestrator-originated event types landed by Story 30-3a
    (``plan_unit.created`` / ``scope_decision.set`` / ``plan.locked``)
    and by downstream stories (30-4's ``fanout.envelope.emitted``,
    29-1's ``fit_report.emitted``). Writer identity is always
    ``ORCHESTRATOR_MODULE_IDENTITY`` (single-writer rule, R1 amendment
    13).

    Args:
        envelope: Pre-validated :class:`EventEnvelope` for any
            Orchestrator-permitted event type (enforced by 31-2's
            ``WRITER_EVENT_MATRIX`` at :meth:`LessonPlanLog.append_event`).
        log: Optional :class:`LessonPlanLog` for test isolation.
            Production callers pass ``None`` and the default-path log is
            constructed; a :mod:`logging.WARNING` is emitted so test
            leakage into the runtime log is visible in CI output (29-1
            + 30-2b precedent).

    Raises:
        TypeError: Propagated from :meth:`LessonPlanLog.append_event` if
            ``envelope`` is not an :class:`EventEnvelope`.
        ValueError: Propagated on unknown-writer-identity (typo guard)
            or on ``plan.locked`` monotonicity violation.
        UnauthorizedWriterError: Propagated if the envelope's event_type
            is not permitted for ``marcus-orchestrator`` per 31-2's
            ``WRITER_EVENT_MATRIX`` — should not occur for the event
            types 30-3a and downstream consumers emit, but surfaces
            explicitly if a future refactor passes the wrong envelope.
    """
    if log is None:
        logger.warning(
            "dispatch_orchestrator_event called with log=None; falling back to "
            "default LessonPlanLog(). Production callers should pass a "
            "shared log instance; tests MUST pass log=LessonPlanLog(path=tmp_path/...)."
        )
        target_log = LessonPlanLog()
    else:
        target_log = log
    target_log.append_event(envelope, ORCHESTRATOR_MODULE_IDENTITY)


__all__: Final[tuple[str, ...]] = (
    "dispatch_intake_pre_packet",
    "dispatch_orchestrator_event",
)
