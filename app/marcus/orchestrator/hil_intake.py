"""Marcus HIL intake callable — production bridge for Step 04A.

Bridges the conversational scope-ratification phase (Step 04A pack prompt)
with the programmatic ``FourALoop.run_4a()`` call that emits
``scope_decision.set`` / ``plan.locked`` / ``fanout.envelope.emitted``
events to the lesson plan log.

Operator-facing audience only: no "intake", "orchestrator", or "dispatch"
tokens in any Maya-visible string (R1 amendment 17 / Voice Register).

Story: 32-5
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

from app.marcus.lesson_plan.schema import ScopeDecision
from app.marcus.orchestrator.loop import FourAState, IntakeCallable

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

_FORBIDDEN_TOKENS = frozenset({"intake", "orchestrator", "dispatch"})


class MissingIntakeDecisionError(Exception):
    """Raised when the callable is asked for a unit_id not in the decisions dict.

    Maya-facing: message must pass Voice Register (no forbidden tokens,
    natural language, ends with invitation).
    """

    def __init__(self, unit_id: str) -> None:
        self.unit_id = unit_id
        super().__init__(
            "It looks like we haven't made a call on this unit yet — "
            "want to mark it in-scope or out-of-scope?"
        )


class LogResetNotConfirmedError(Exception):
    """Raised when reset_lesson_plan_log is called without confirm=True."""

    def __init__(self) -> None:
        super().__init__(
            "Log reset requires explicit confirmation. Pass confirm=True to proceed."
        )


# ---------------------------------------------------------------------------
# Pre-collected intake callable
# ---------------------------------------------------------------------------

_VALID_SCOPES = frozenset({"in-scope", "out-of-scope", "delegated", "blueprint"})


class MarcusPreCollectedIntakeCallable:
    """Production IntakeCallable that serves pre-collected operator decisions.

    Phase 2 of the Step 04A two-phase pattern:
    1. Marcus collects decisions conversationally (Phase 1 — already works).
    2. This callable serves those decisions to FourALoop.run_4a() (Phase 2).

    Rationale is stored verbatim — no ``.strip()``, no coercion, no parsing.
    Every invocation returns a fresh ``ScopeDecision`` instance (no aliasing).
    """

    def __init__(self, decisions: dict[str, tuple[str, str]]) -> None:
        self._decisions = dict(decisions)

    def __call__(self, state: FourAState, unit_id: str) -> tuple[ScopeDecision, str]:
        if unit_id not in self._decisions:
            raise MissingIntakeDecisionError(unit_id)
        scope_value, rationale = self._decisions[unit_id]
        decision = ScopeDecision(
            state="ratified",
            scope=scope_value,
            proposed_by="operator",
            ratified_by="maya",
        )
        return decision, rationale


def build_hil_intake_callable(
    decisions: dict[str, tuple[str, str]],
) -> IntakeCallable:
    """Factory: build a production IntakeCallable from pre-collected decisions.

    Args:
        decisions: Mapping of ``{unit_id: (scope_value, rationale)}``.
            ``scope_value`` must be one of ``{"in-scope", "out-of-scope",
            "delegated", "blueprint"}``.  ``rationale`` is any string
            (including empty) stored verbatim.

    Returns:
        An :data:`IntakeCallable` suitable for passing to
        ``Facade.run_4a()``.

    Raises:
        ValueError: If any ``scope_value`` is not in the allowed set, or if
            duplicate ``unit_id`` keys appear in a list-derived source.
    """
    for unit_id, (scope_value, _rationale) in decisions.items():
        if scope_value not in _VALID_SCOPES:
            raise ValueError(
                f"unit_id {unit_id!r}: scope_value {scope_value!r} is not valid; "
                f"must be one of {sorted(_VALID_SCOPES)}"
            )
    return MarcusPreCollectedIntakeCallable(decisions)


# ---------------------------------------------------------------------------
# Log reset utility
# ---------------------------------------------------------------------------

_LOG_FILENAME = "lesson-plan-log.jsonl"


def reset_lesson_plan_log(
    bundle_dir: Path,
    *,
    confirm: bool = False,
) -> Path | None:
    """Archive the stale lesson plan log before a fresh 04A run.

    Non-destructive: renames the log to a timestamped ``.STALE-*`` file
    within the same directory. Never deletes.

    Args:
        bundle_dir: Path to the source bundle directory containing the log.
        confirm: Must be ``True`` to proceed. Default ``False`` prevents
            accidental resets.

    Returns:
        Path to the archived stale file, or ``None`` if no log existed.

    Raises:
        LogResetNotConfirmedError: If ``confirm=False`` (the default).
    """
    if not confirm:
        raise LogResetNotConfirmedError()

    log_path = bundle_dir / _LOG_FILENAME
    if not log_path.exists():
        return None

    ts = datetime.now(tz=UTC).strftime("%Y%m%dT%H%M%S_%f")
    archive_path = bundle_dir / f"lesson-plan-log.STALE-{ts}.jsonl"
    log_path.rename(archive_path)
    return archive_path
