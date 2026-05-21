"""Event-type registry + open-string validator (Story 31-1 AC-B.8).

Two registered sets:

- :data:`KNOWN_PLAN_UNIT_EVENT_TYPES` — the nine Gagne-9 event labels. These
  are the valid ``event_type`` values on ``PlanUnit``.
- :data:`RESERVED_LOG_EVENT_TYPES` — the mandatory log event-types pre-registered
  for 31-2 emission. Reserved, not emitted by 31-1 (single-writer rule per
  R1 ruling amendment 13).

:func:`validate_event_type` WARNS (does not reject) on event_types outside
either set so that future learning-model / event-stream extensions emerge
visibly in observability, not silently. Invalid-regex strings are REJECTED.
"""

from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Known plan_unit event_type labels (Gagne-9)
# ---------------------------------------------------------------------------

KNOWN_PLAN_UNIT_EVENT_TYPES: frozenset[str] = frozenset(
    {f"gagne-event-{n}" for n in range(1, 10)}
)
"""The nine Gagne Events of Instruction as open-string labels."""


# ---------------------------------------------------------------------------
# Reserved log event_types (R1 ruling amendment 8 / R2 rider W-1)
# ---------------------------------------------------------------------------

# Named single-source-of-truth constants. Downstream emitters (30-2b dispatch,
# 31-2 log writer, 29-1 fit-report emitter) MUST import these rather than
# hard-code the string literal — closes 30-1 G6-D2 cross-story slip.
EVENT_PRE_PACKET_SNAPSHOT: str = "pre_packet_snapshot"
EVENT_PLAN_UNIT_CREATED: str = "plan_unit.created"
EVENT_SCOPE_DECISION_SET: str = "scope_decision.set"
EVENT_SCOPE_DECISION_TRANSITION: str = "scope_decision_transition"
EVENT_PLAN_LOCKED: str = "plan.locked"
EVENT_FANOUT_ENVELOPE_EMITTED: str = "fanout.envelope.emitted"
EVENT_FIT_REPORT_EMITTED: str = "fit_report.emitted"
# G6-Opus 30-3b sweep (party-mode 2026-04-19 follow-on): dedicated event-type
# for dial-tuning operations. Was previously emitted as EVENT_SCOPE_DECISION_SET
# in tune_unit_dials, conflating semantic categories — downstream readers
# (32-3 smoke harness, audit consumers, 31-2 log readers) interpreting
# scope_decision.set events would mistake a dial change for a scope change.
EVENT_DIALS_TUNED: str = "dials.tuned"

RESERVED_LOG_EVENT_TYPES: frozenset[str] = frozenset(
    {
        # Event-type naming grammar: <domain_noun>.<past_tense_verb>.
        # Reserved for 31-2 pre_packet_snapshot emission per R1 ruling amendment 13
        # (single-writer rule).
        EVENT_PRE_PACKET_SNAPSHOT,
        EVENT_PLAN_UNIT_CREATED,
        EVENT_SCOPE_DECISION_SET,
        EVENT_SCOPE_DECISION_TRANSITION,
        EVENT_PLAN_LOCKED,
        EVENT_FANOUT_ENVELOPE_EMITTED,
        # Registered by Story 29-1 — Marcus-Orchestrator emits when a
        # validated FitReport is appended to the log.
        EVENT_FIT_REPORT_EMITTED,
        # Registered by 30-3b retroactively (party-mode 2026-04-19 follow-on):
        # dial-tuning is a distinct semantic category from scope-decision-set.
        EVENT_DIALS_TUNED,
    }
)


REGISTERED_EVENT_TYPES: frozenset[str] = (
    KNOWN_PLAN_UNIT_EVENT_TYPES | RESERVED_LOG_EVENT_TYPES
)
"""Union of known + reserved event_types; the "registered" set."""


# Single-source-of-truth open-id regex. Downstream modules (schema.py,
# events.py) import OPEN_ID_REGEX_PATTERN for Pydantic Field(pattern=...)
# usage; the compiled form is for in-module .match() checks.
OPEN_ID_REGEX_PATTERN: str = r"^[a-z0-9._-]+$"
_OPEN_ID_REGEX = re.compile(OPEN_ID_REGEX_PATTERN)

# SF-4: dedup warnings — warn only on FIRST encounter of an unknown event_type
# per process lifetime. Without this, a hot path emitting the same unknown
# event_type on every call floods the logs (Edge Case Hunter #8 / Blind #7).
_WARNED_UNKNOWN_TYPES: set[str] = set()


def _reset_warning_state() -> None:
    """Clear the warn-once memo. For test isolation only."""
    _WARNED_UNKNOWN_TYPES.clear()


def validate_event_type(value: str) -> str:
    """Validate an event_type string; WARN once per unknown value (AC-B.8 / AC-T.6).

    Rules:
        - Must be a non-empty string matching ``^[a-z0-9._-]+$``.
        - If the value is in :data:`REGISTERED_EVENT_TYPES`, return silently.
        - Otherwise log a warning at WARNING level **only on first encounter
          per process lifetime** and return the value unchanged. Unknown
          values are PERMITTED for Gagne-seam extensibility (future learning
          models ship a second-tier story). Dedup implemented via
          ``_WARNED_UNKNOWN_TYPES`` module-level set (SF-4).
    """
    if not isinstance(value, str) or not value:
        raise ValueError("event_type must be a non-empty string")
    if not _OPEN_ID_REGEX.match(value):
        raise ValueError(
            f"event_type {value!r} fails open-id regex ^[a-z0-9._-]+$"
        )
    if value not in REGISTERED_EVENT_TYPES and value not in _WARNED_UNKNOWN_TYPES:
        logger.warning(
            "event_type %r not in known registry; "
            "permitted for Gagné-seam extensibility",
            value,
        )
        _WARNED_UNKNOWN_TYPES.add(value)
    return value


__all__ = [
    "EVENT_DIALS_TUNED",
    "EVENT_FANOUT_ENVELOPE_EMITTED",
    "EVENT_FIT_REPORT_EMITTED",
    "EVENT_PLAN_LOCKED",
    "EVENT_PLAN_UNIT_CREATED",
    "EVENT_PRE_PACKET_SNAPSHOT",
    "EVENT_SCOPE_DECISION_SET",
    "EVENT_SCOPE_DECISION_TRANSITION",
    "KNOWN_PLAN_UNIT_EVENT_TYPES",
    "OPEN_ID_REGEX_PATTERN",
    "REGISTERED_EVENT_TYPES",
    "RESERVED_LOG_EVENT_TYPES",
    "validate_event_type",
]
