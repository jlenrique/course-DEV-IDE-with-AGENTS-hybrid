"""Marcus-Orchestrator: 4A conversation loop + plan-lock commit + downstream fan-out (05+).

This sub-package is part of the Marcus duality split landed in Story 30-1 and
relocated to ``app.marcus.*`` at pre-Trial-3 cleanup S2 (2026-05-07; Marcus
namespace collapse — `migration-tech-debt-app-marcus-stub-disposition` closure
with reality-corrected direction).

Maya-facing note
----------------

Maya never imports from this package. She interacts with a single Marcus
facade (``app.marcus.facade.get_facade()``). The sub-package exists internally
to isolate the conversation-orchestration + log-write side of Marcus from
the ingestion side.

Developer discipline note
-------------------------

* 30-1 (structural foundation): module shell + identity constant + negotiator
  seam + :mod:`app.marcus.orchestrator.write_api` single-writer entry point.
* 30-3a (4A skeleton + lock): lifts the 4A conversation loop into this
  package; promotes :data:`NEGOTIATOR_SEAM` from a string sentinel to a
  structural marker with handoff state.
* 30-4 (plan-lock fanout): fan-out dispatch on plan-lock commit.
* S2 (2026-05-07): identities and seams preserved verbatim under the
  new ``app.marcus.*`` home.

Single-writer contract
----------------------

Marcus-Orchestrator is the SOLE caller of
:func:`app.marcus.orchestrator.write_api.emit_pre_packet_snapshot`. The facade
routes Intake-side artifacts through the Orchestrator; Intake never calls
the write API directly. R1 amendment 13 (Quinn single-writer rule); see
``tests/contracts/test_marcus_single_writer_routing.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Literal

from app.marcus.orchestrator.routing import RoutingDecision, route_step
from app.marcus.orchestrator.supervisor import Supervisor, SupervisorPreset, mode_for_preset

# NOTE: `append_event` is NOT eagerly imported here — write_api.py imports
# `ORCHESTRATOR_MODULE_IDENTITY` from this module, which would create a circular
# import. Callers wanting `append_event` import it directly:
#   from app.marcus.orchestrator.write_api import append_event
# The legacy `marcus.orchestrator.__init__` never re-exported it either.

ORCHESTRATOR_MODULE_IDENTITY: Literal["marcus-orchestrator"] = "marcus-orchestrator"
"""Programming-token identity for the Orchestrator half of the Marcus duality.

String-equal to the 31-2 ``WriterIdentity`` Literal value. Imported by
:mod:`app.marcus.orchestrator.write_api` as the single source of truth for
the writer-check string (avoids the three-place string-drift hazard).
See :data:`app.marcus.lesson_plan.log.WriterIdentity`.

Note: token value is ``"marcus-orchestrator"`` — preserved from 30-1 for
WriterIdentity Literal compatibility. The package now lives at ``app.marcus.*``
but the token itself stays ``marcus-orchestrator`` (changing it would break
the 31-2 single-writer log contract + the Golden-Trace fixture).
"""


_NEGOTIATOR_SEAM_BACKCOMPAT_TOKEN: Final[str] = "marcus-negotiator"
"""Grep-discoverable 30-1 sentinel token. :class:`NegotiatorSeam.__str__`
returns this value to preserve backward-compat with 30-1's grep-based
tests (:mod:`tests.test_marcus_negotiator_seam_named`)."""


@dataclass(frozen=True)
class NegotiatorSeam:
    """Structural marker for the 4A conversation-loop negotiator (30-3a upgrade).

    At 30-1 this seam was a string sentinel. 30-3a upgraded it to a
    typed structural marker carrying the handoff state the 4A loop
    needs: the pending-intake queue, the per-turn dialogue history,
    and the active-loop flag.

    Backward-compat with 30-1's grep-based sentinel contract is
    preserved via :meth:`__str__`, which returns the literal string
    ``"marcus-negotiator"``.

    Fields:
        pending_queue: Tuple of ``unit_id`` strings awaiting scope-
            decision intake. Empty when the loop is idle or post-lock.
        dialogue_history: Tuple of ``(turn_kind, content)`` pairs
            recording the Maya<->Marcus exchange.
        active_loop: True iff the loop is currently running
            (:meth:`FourALoop.run_4a` is on the stack).
    """

    pending_queue: tuple[str, ...] = field(default_factory=tuple)
    dialogue_history: tuple[tuple[str, str], ...] = field(default_factory=tuple)
    active_loop: bool = False

    def __str__(self) -> str:
        return _NEGOTIATOR_SEAM_BACKCOMPAT_TOKEN


NEGOTIATOR_SEAM: Final[NegotiatorSeam] = NegotiatorSeam()
"""Singleton :class:`NegotiatorSeam` instance - grep-discoverable sentinel.

``str(NEGOTIATOR_SEAM) == "marcus-negotiator"`` preserves 30-1's
grep-based sentinel contract while exposing the structural fields
the 4A loop needs.
"""

__all__: Final[tuple[str, ...]] = (
    "NEGOTIATOR_SEAM",
    "NegotiatorSeam",
    "ORCHESTRATOR_MODULE_IDENTITY",
    "RoutingDecision",
    "Supervisor",
    "SupervisorPreset",
    "mode_for_preset",
    "route_step",
)
